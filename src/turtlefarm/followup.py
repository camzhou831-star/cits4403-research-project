"""Compact, append-only execution of the protocol in docs/followup-protocol.md.

This runner retains configurations, outcomes and event observations, not full daily
trajectories. It is separate from the original formal experiment runner.
"""

from __future__ import annotations

import json
import math
import os
import socket
import subprocess
import uuid
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from turtlefarm.config import ConfigError, SimulationConfig
from turtlefarm.model import STATUS_FAILED
from turtlefarm.observation import ObservedSimulation
from turtlefarm.runner import BatchHalted, configuration_hash, flatten, iter_raw, to_raw_record

OBSERVATION_SCHEMA_VERSION = "turtlefarm.observation.v1"
COMPACT_SCHEMA_VERSION = "turtlefarm.followup.v1"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _repository_commit() -> str:
    """Resolve this implementation's repository, never the caller's working directory.

    Keep the existing short-SHA representation so historical compact records remain readable.
    Missing provenance is an execution error, not a permissible None commit.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--verify", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"cannot determine implementation commit for {REPO_ROOT}") from exc
    commit = result.stdout.strip()
    if not commit:
        raise ValueError(f"cannot determine implementation commit for {REPO_ROOT}")
    return commit


@contextmanager
def _coordinator_lock(out: Path) -> Iterator[None]:
    """One coordinator per canonical raw path, using portable exclusive file creation.

    The lock covers both resume inspection and writing; workers never acquire or remove it.
    Normal returns and exceptions remove the marker. A hard crash can leave <raw>.lock:
    inspect its PID and hostname, confirm that coordinator has stopped, then remove ONLY
    that marker and use --resume. Never remove a live coordinator's lock or the raw data.
    PID reuse and remote hosts make automatic stale-lock deletion unsafe.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    lock_path = out.with_name(out.name + ".lock")
    try:
        handle = lock_path.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise FileExistsError(
            f"coordinator lock exists: {lock_path}; another run may be active. "
            "For crash recovery, verify its PID/hostname is inactive before removing only the lock."
        ) from exc
    try:
        json.dump({"pid": os.getpid(), "hostname": socket.gethostname(),
                   "created_utc": datetime.now(timezone.utc).isoformat(), "raw_path": str(out)}, handle)
        handle.flush()
        yield
    finally:
        handle.close()
        lock_path.unlink()


@dataclass(frozen=True)
class FollowupDesign:
    name: str
    protocol_version: int
    base_commit: str
    transfer_rate: float
    network_seeds: tuple[int, ...]
    epidemic_seed_start: int
    epidemic_replicates: int
    policy_seed_start: int
    policy_replicates: int
    response_delays: tuple[int, ...]
    durations: tuple[int, ...]
    fixed: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.name or Path(self.name).name != self.name or self.name in {".", ".."}:
            raise ConfigError("name must be a non-empty filename component")
        for field in ("protocol_version", "epidemic_replicates", "policy_replicates"):
            value = getattr(self, field)
            if type(value) is not int or value < 1:
                raise ConfigError(f"{field} must be a positive integer")
        for field in ("epidemic_seed_start", "policy_seed_start"):
            value = getattr(self, field)
            if type(value) is not int or value < 0:
                raise ConfigError(f"{field} must be a non-negative integer")
        for field in ("network_seeds", "response_delays", "durations"):
            values = getattr(self, field)
            if not values or len(values) != len(set(values)):
                raise ConfigError(f"{field} must be non-empty and unique")
            if any(type(v) is not int or v < (1 if field == "durations" else 0) for v in values):
                raise ConfigError(f"invalid {field}")
        permitted = {"beta", "gamma", "capacity", "p_in", "p_out", "k", "max_days", "network_max_attempts"}
        if set(self.fixed) - permitted:
            raise ConfigError(f"unknown fixed fields: {sorted(set(self.fixed) - permitted)}")
        if not isinstance(self.base_commit, str) or not self.base_commit:
            raise ConfigError("base_commit must identify the original experiment version")

    @classmethod
    def from_json(cls, path: str | Path) -> "FollowupDesign":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in ("network_seeds", "response_delays", "durations"):
            if key in data:
                data[key] = tuple(data[key])
        try:
            design = cls(**data)
        except TypeError as exc:
            raise ConfigError(str(exc)) from exc
        design.configs()  # Validate all model parameters before any output is opened.
        return design

    @property
    def protocol_hash(self) -> str:
        return configuration_hash(asdict(self))

    def configs(self) -> list[SimulationConfig]:
        configs = []
        for i, network_seed in enumerate(self.network_seeds):
            policies = range(self.policy_seed_start + i * self.policy_replicates,
                             self.policy_seed_start + (i + 1) * self.policy_replicates)
            for j in range(self.epidemic_replicates):
                common = dict(self.fixed, label=self.name, network_seed=network_seed,
                              epidemic_seed=self.epidemic_seed_start + i * self.epidemic_replicates + j,
                              transfer_rate=self.transfer_rate)
                configs.append(SimulationConfig(**common, strategy="none"))
                for duration in self.durations:
                    for delay in self.response_delays:
                        condition = dict(common, quarantine_duration=duration, response_delay=delay)
                        configs.append(SimulationConfig(**condition, strategy="betweenness"))
                        configs.extend(SimulationConfig(**condition, strategy="random", policy_seed=seed)
                                       for seed in policies)
        return configs


def _execute(task: tuple[SimulationConfig, str]) -> dict[str, Any]:
    cfg, protocol_hash = task
    implementation_commit = _repository_commit()
    simulation = ObservedSimulation(cfg)
    record = simulation.run()
    if _repository_commit() != implementation_commit:
        raise ValueError("implementation commit changed during simulation; no record was appended")
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    raw = to_raw_record(record, run_id=uuid.uuid4().hex, timestamp_utc=timestamp)
    # The original model resolves Git relative to cwd. Only this compact execution envelope
    # overrides that provenance; no model rule, scientific quantity or historical record changes.
    raw["code_commit"] = implementation_commit
    row = flatten(raw)
    row.update({field: getattr(cfg, field) for field in ("capacity", "p_in", "p_out", "max_days")})
    row.update(simulation.observation_metrics())
    row.update(protocol_hash=protocol_hash, observation_schema_version=OBSERVATION_SCHEMA_VERSION)
    return {
        "schema_version": COMPACT_SCHEMA_VERSION,
        "timestamp_utc": timestamp,
        "config": raw["config"],
        "error": raw["error"],
        "initial_infected_agents": raw["initial_infected_agents"],
        "initial_infected_tanks": raw["initial_infected_tanks"],
        "summary": row,
    }


def run_followup(
    design: FollowupDesign,
    out_path: str | Path,
    *,
    resume: bool = False,
    workers: int = 1,
    max_failure_rate: float = 0.01,
    progress: Callable[[int, int, dict[str, Any]], None] | None = None,
) -> dict[str, int]:
    """Persist in configuration order, including failures; never silently replace a run.

    Resume requires matching protocol and schema, unique configuration hashes and a
    single implementation commit. Existing failures count toward the batch limit. An exclusive
    <raw>.lock marker prevents overlapping coordinators; see _coordinator_lock for crash recovery.
    """
    if type(workers) is not int or workers < 1:
        raise ValueError("workers must be a positive integer")
    if not math.isfinite(max_failure_rate) or not 0 <= max_failure_rate <= 1:
        raise ValueError("max_failure_rate must lie in [0, 1]")
    configs = design.configs()
    out = Path(out_path).resolve()
    with _coordinator_lock(out):
        return _run_locked(design, configs, out, resume=resume, workers=workers,
                           max_failure_rate=max_failure_rate, progress=progress)


def _run_locked(
    design: FollowupDesign,
    configs: list[SimulationConfig],
    out: Path,
    *,
    resume: bool,
    workers: int,
    max_failure_rate: float,
    progress: Callable[[int, int, dict[str, Any]], None] | None,
) -> dict[str, int]:
    """The caller holds the coordinator lock until all worker processes have stopped."""
    expected = {configuration_hash(cfg.to_dict()) for cfg in configs}
    if out.exists() and not resume:
        raise FileExistsError(f"{out} exists; use --resume or a different output directory")
    done: set[str] = set()
    commits: set[str] = set()
    counts = dict(planned=len(configs), written=0, skipped=0, failed=0)

    def validate_metadata(record: dict[str, Any]) -> None:
        row = record["summary"]
        key = row["configuration_hash"]
        if (record["schema_version"] != COMPACT_SCHEMA_VERSION
                or row["observation_schema_version"] != OBSERVATION_SCHEMA_VERSION
                or row["protocol_hash"] != design.protocol_hash):
            raise ValueError("raw records do not match the current protocol/schema")
        if key != configuration_hash(record["config"]) or key not in expected or key in done:
            raise ValueError("raw records have an unknown, altered or duplicate configuration")
        commit = row["code_commit"]
        if not isinstance(commit, str) or not commit:
            raise ValueError("raw records have missing implementation commit provenance")
        if commits and commit not in commits:
            raise ValueError("raw records mix implementation commits; use a separate output directory")

    def accept_record(record: dict[str, Any]) -> None:
        """Account for a validated, already-persisted record before enforcing stop rules."""
        row = record["summary"]
        commits.add(row["code_commit"])
        done.add(row["configuration_hash"])
        if row["status"] == STATUS_FAILED:
            counts["failed"] += 1
            if row["stop_reason"] == "invariant failure":
                raise BatchHalted(f"invariant failure: {record['error']}")
            if counts["failed"] > max_failure_rate * len(configs):
                raise BatchHalted(f"{counts['failed']} failed runs exceed {max_failure_rate:.0%} of the design")

    if resume and out.exists():
        for record in iter_raw(out):
            validate_metadata(record)
            accept_record(record)
    counts["skipped"] = len(done)
    pending = [(cfg, design.protocol_hash) for cfg in configs if configuration_hash(cfg.to_dict()) not in done]
    if not pending:
        return counts
    # Completed historical files need no new execution. For pending work, pin the repository
    # commit before starting workers and refuse a changed implementation before every append.
    implementation_commit = _repository_commit()
    if commits and implementation_commit not in commits:
        raise ValueError("implementation commit changed; use a separate output directory")
    pool = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    try:
        records = pool.map(_execute, pending, chunksize=4) if pool else map(_execute, pending)
        with out.open("a", encoding="utf-8") as handle:
            for record in records:
                if (_repository_commit() != implementation_commit
                        or record["summary"]["code_commit"] != implementation_commit):
                    raise ValueError("implementation commit changed during batch; no new record was appended")
                validate_metadata(record)
                # Store a failed simulation before enforcing its stop rule.
                handle.write(json.dumps(record, separators=(",", ":")) + "\n")
                handle.flush()
                counts["written"] += 1
                accept_record(record)
                if progress:
                    progress(len(done), len(configs), record["summary"])
    finally:
        if pool:
            pool.shutdown(wait=True, cancel_futures=True)
    return counts
