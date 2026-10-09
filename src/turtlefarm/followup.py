"""Compact, append-only execution of the protocol in docs/followup-protocol.md.

This runner retains configurations, outcomes and event observations, not full daily
trajectories. It is separate from the original formal experiment runner.
"""

from __future__ import annotations

import json
import math
import uuid
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from turtlefarm.config import ConfigError, SimulationConfig
from turtlefarm.model import STATUS_FAILED
from turtlefarm.observation import ObservedSimulation
from turtlefarm.runner import BatchHalted, configuration_hash, flatten, iter_raw, to_raw_record

OBSERVATION_SCHEMA_VERSION = "turtlefarm.observation.v1"
COMPACT_SCHEMA_VERSION = "turtlefarm.followup.v1"


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
    simulation = ObservedSimulation(cfg)
    record = simulation.run()
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    raw = to_raw_record(record, run_id=uuid.uuid4().hex, timestamp_utc=timestamp)
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
    single implementation commit. Existing failures count toward the batch limit.
    """
    if type(workers) is not int or workers < 1:
        raise ValueError("workers must be a positive integer")
    if not math.isfinite(max_failure_rate) or not 0 <= max_failure_rate <= 1:
        raise ValueError("max_failure_rate must lie in [0, 1]")
    configs = design.configs()
    expected = {configuration_hash(cfg.to_dict()) for cfg in configs}
    out = Path(out_path)
    if out.exists() and not resume:
        raise FileExistsError(f"{out} exists; use --resume or a different output directory")
    done: set[str] = set()
    commits: set[str] = set()
    counts = dict(planned=len(configs), written=0, skipped=0, failed=0)

    def check(record: dict[str, Any]) -> None:
        row = record["summary"]
        key = row["configuration_hash"]
        if (record["schema_version"] != COMPACT_SCHEMA_VERSION
                or row["observation_schema_version"] != OBSERVATION_SCHEMA_VERSION
                or row["protocol_hash"] != design.protocol_hash):
            raise ValueError("raw records do not match the current protocol/schema")
        if key != configuration_hash(record["config"]) or key not in expected or key in done:
            raise ValueError("raw records have an unknown, altered or duplicate configuration")
        commits.add(row["code_commit"])
        if len(commits) != 1:
            raise ValueError("raw records mix implementation commits; use a separate output directory")
        done.add(key)
        if row["status"] == STATUS_FAILED:
            counts["failed"] += 1
            if row["stop_reason"] == "invariant failure":
                raise BatchHalted(f"invariant failure: {record['error']}")
            if counts["failed"] > max_failure_rate * len(configs):
                raise BatchHalted(f"{counts['failed']} failed runs exceed {max_failure_rate:.0%} of the design")

    if resume and out.exists():
        for record in iter_raw(out):
            check(record)
    counts["skipped"] = len(done)
    pending = [(cfg, design.protocol_hash) for cfg in configs if configuration_hash(cfg.to_dict()) not in done]
    if not pending:
        return counts
    # Reject stale resumes before appending (the model records this same commit).
    from turtlefarm.model import _git_commit
    if commits and _git_commit() not in commits:
        raise ValueError("implementation commit changed; use a separate output directory")
    out.parent.mkdir(parents=True, exist_ok=True)
    pool = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    try:
        records = pool.map(_execute, pending, chunksize=4) if pool else map(_execute, pending)
        with out.open("a", encoding="utf-8") as handle:
            for record in records:
                # Store a failed simulation before enforcing its stop rule.
                handle.write(json.dumps(record, separators=(",", ":")) + "\n")
                handle.flush()
                counts["written"] += 1
                check(record)
                if progress:
                    progress(len(done), len(configs), record["summary"])
    finally:
        if pool:
            pool.shutdown(wait=True, cancel_futures=True)
    return counts
