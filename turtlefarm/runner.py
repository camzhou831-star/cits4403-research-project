"""Batch experiment runner (experiment-plan sections 3, 6, 10, 11, 16; docs/run-result-schema.md).

The runner owns only the execution envelope and persistence: ``schema_version``, ``run_id``,
``timestamp_utc``, ``configuration_hash`` and append-only JSONL. Every scientific quantity comes from the
model's ``RunRecord``; nothing is recomputed here.

A design expands into paired comparison blocks keyed by (network_seed, epidemic_seed, transfer_rate).
Inside one block every strategy shares the network instance and the event-keyed epidemic draws:

    1 shared no-intervention baseline                       (D007: not repeated per delay)
    + per response delay: 1 betweenness run + 1 random run per policy seed

A pilot design may additionally ``sweep`` otherwise-fixed fields (beta, gamma, D, ...) and may leave
``response_delays`` and ``policy_seeds`` empty to run the no-intervention baseline only. A formal design
has no sweep: those values are frozen before it runs (experiment-plan section 9).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from turtlefarm.config import ConfigError, SimulationConfig
from turtlefarm.model import STATUS_FAILED, RunRecord, run_baseline

SCHEMA_VERSION = "turtlefarm.run.v1"

# Working trigger of experiment-plan section 16: pause the whole batch above this share of failed runs.
DEFAULT_MAX_FAILURE_RATE = 0.01

# Config fields a design may fix for every run. Structure (n_agents, n_tanks, ...) is locked by
# design="main"; design, label, the three seeds and the three independent variables are set by the runner.
_FIXED_FIELDS = frozenset(
    {"beta", "gamma", "p_in", "p_out", "network_max_attempts", "capacity", "quarantine_duration", "k", "max_days"}
)


class BatchHalted(RuntimeError):
    """The batch stopped early (invariant failure or failure rate above the trigger). Records written so
    far are kept; investigate and document before any rerun (experiment-plan sections 11 and 16)."""


@dataclass(frozen=True)
class ExperimentDesign:
    """Machine-readable description of one pilot or formal batch (``experiments/config/*.json``)."""

    name: str
    transfer_rates: tuple[float, ...]
    response_delays: tuple[int, ...]
    network_seeds: tuple[int, ...]
    epidemic_seeds: tuple[int, ...]
    policy_seeds: tuple[int, ...]
    fixed: dict[str, Any] = field(default_factory=dict)
    sweep: dict[str, tuple[Any, ...]] = field(default_factory=dict)  # pilot only

    def __post_init__(self) -> None:
        errs: list[str] = []
        if not self.name:
            errs.append("name must be non-empty")
        for level_name in ("transfer_rates", "network_seeds", "epidemic_seeds"):
            if not getattr(self, level_name):
                errs.append(f"{level_name} must be non-empty")
        if bool(self.response_delays) != bool(self.policy_seeds):
            errs.append("response_delays and policy_seeds must both be given, or both be empty (baseline only)")
        levels_by_name = {
            name: getattr(self, name)
            for name in ("transfer_rates", "response_delays", "network_seeds", "epidemic_seeds", "policy_seeds")
        }
        levels_by_name.update({f"sweep[{name!r}]": levels for name, levels in self.sweep.items()})
        for level_name, levels in levels_by_name.items():
            if len(set(levels)) != len(levels):
                errs.append(f"{level_name} contains duplicates: {levels!r}")
        for group_name, group in (("fixed", self.fixed), ("sweep", self.sweep)):
            unknown = sorted(set(group) - _FIXED_FIELDS)
            if unknown:
                errs.append(f"{group_name} may only set {sorted(_FIXED_FIELDS)}, got {unknown}")
        if set(self.fixed) & set(self.sweep):
            errs.append(f"fields cannot be both fixed and swept: {sorted(set(self.fixed) & set(self.sweep))}")
        if any(not levels for levels in self.sweep.values()):
            errs.append("every swept field needs at least one level")
        if errs:
            raise ConfigError("; ".join(errs))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentDesign":
        known = {
            "name", "transfer_rates", "response_delays", "network_seeds", "epidemic_seeds", "policy_seeds",
            "fixed", "sweep",
        }
        unknown = sorted(set(data) - known)
        if unknown:
            raise ConfigError(f"unknown design keys: {unknown}")
        missing = sorted(known - {"fixed", "sweep"} - set(data))
        if missing:
            raise ConfigError(f"missing design keys: {missing}")
        return cls(
            name=data["name"],
            transfer_rates=tuple(data["transfer_rates"]),
            response_delays=tuple(data["response_delays"]),
            network_seeds=tuple(data["network_seeds"]),
            epidemic_seeds=tuple(data["epidemic_seeds"]),
            policy_seeds=tuple(data["policy_seeds"]),
            fixed=dict(data.get("fixed", {})),
            sweep={name: tuple(levels) for name, levels in data.get("sweep", {}).items()},
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "ExperimentDesign":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def configs(self) -> list[SimulationConfig]:
        """Every run of the design, block by block. Building the full list first means an invalid
        parameter raises ``ConfigError`` before any run starts, never halfway through a batch."""
        swept = [dict(zip(self.sweep, values)) for values in itertools.product(*self.sweep.values())]
        configs: list[SimulationConfig] = []
        for candidate, network_seed, epidemic_seed, transfer_rate in itertools.product(
            swept, self.network_seeds, self.epidemic_seeds, self.transfer_rates
        ):
            common = dict(
                self.fixed,
                **candidate,
                design="main",
                label=self.name,
                network_seed=network_seed,
                epidemic_seed=epidemic_seed,
                transfer_rate=transfer_rate,
            )
            # response_delay and quarantine_duration have no effect under "none"; they are pinned to 0 so
            # that the shared baseline has exactly one configuration per block.
            configs.append(SimulationConfig(**{**common, "strategy": "none", "quarantine_duration": 0}))
            for delay in self.response_delays:
                configs.append(SimulationConfig(**common, strategy="betweenness", response_delay=delay))
                for policy_seed in self.policy_seeds:
                    configs.append(
                        SimulationConfig(**common, strategy="random", response_delay=delay, policy_seed=policy_seed)
                    )
        # A pilot sweep over quarantine_duration yields the same baseline once per candidate; run it once.
        return list(dict.fromkeys(configs))


def configuration_hash(config: dict[str, Any]) -> str:
    """Lowercase hex SHA-256 over canonical JSON of ``config`` (run-result-schema section 8)."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def to_raw_record(record: RunRecord, *, run_id: str, timestamp_utc: str) -> dict[str, Any]:
    """Wrap a model ``RunRecord`` in the runner envelope. Dataclasses and tuples become plain JSON."""
    body = asdict(record)
    config = body["config"]
    has_intervention = config["strategy"] != "none"
    raw = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp_utc": timestamp_utc,
        "code_commit": body.pop("code_commit"),
        "configuration_hash": configuration_hash(config),
        "intervention_duration_days": config["quarantine_duration"] if has_intervention else None,
    }
    raw.update(body)
    raw["transitions"] = [list(t) for t in body["transitions"]]
    return raw


def recorded_hashes(path: Path) -> set[str]:
    """Configuration hashes already present in a raw file, whatever their status. A failed run is not
    silently retried on resume (experiment-plan section 11)."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as fh:
        return {json.loads(line)["configuration_hash"] for line in fh if line.strip()}


def run_design(
    design: ExperimentDesign,
    out_path: str | Path,
    *,
    resume: bool = False,
    max_failure_rate: float = DEFAULT_MAX_FAILURE_RATE,
    progress: Callable[[int, int, dict[str, Any]], None] | None = None,
) -> dict[str, int]:
    """Run every configuration of ``design`` and append one JSON line per attempted run.

    An existing ``out_path`` is refused unless ``resume`` is set, in which case configurations whose hash
    is already recorded are skipped. Raises ``BatchHalted`` after writing the offending record.
    """
    out = Path(out_path)
    if out.exists() and not resume:
        raise FileExistsError(f"{out} exists; raw results are append-only. Pass resume=True to continue it.")
    configs = design.configs()
    done = recorded_hashes(out) if resume else set()
    out.parent.mkdir(parents=True, exist_ok=True)

    counts = {"planned": len(configs), "skipped": 0, "written": 0, "failed": 0}
    with out.open("a", encoding="utf-8") as fh:
        for index, cfg in enumerate(configs):
            if configuration_hash(cfg.to_dict()) in done:
                counts["skipped"] += 1
                continue
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            raw = to_raw_record(run_baseline(cfg), run_id=uuid.uuid4().hex, timestamp_utc=timestamp)
            fh.write(json.dumps(raw, separators=(",", ":")) + "\n")
            fh.flush()
            counts["written"] += 1
            if progress is not None:
                progress(index + 1, len(configs), raw)
            if raw["status"] == STATUS_FAILED:
                counts["failed"] += 1
                if raw["stop_reason"] == "invariant failure":
                    raise BatchHalted(f"invariant failure in run {raw['run_id']}: {raw['error']}")
                if counts["failed"] > max_failure_rate * len(configs):
                    raise BatchHalted(
                        f"{counts['failed']} failed runs exceed {max_failure_rate:.0%} of {len(configs)} planned"
                    )
    return counts


def iter_raw(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def flatten(raw: dict[str, Any]) -> dict[str, Any]:
    """One summary-table row per run: block key, condition, provenance and the model's own metrics.
    Relative reductions are paired-analysis outputs and are deliberately not computed here."""
    config = raw["config"]
    network = raw["network"] or {}
    row = {
        "run_id": raw["run_id"],
        "configuration_hash": raw["configuration_hash"],
        "code_commit": raw["code_commit"],
        "label": config["label"],
        "network_seed": config["network_seed"],
        "epidemic_seed": config["epidemic_seed"],
        "policy_seed": config["policy_seed"],
        "network_hash": network.get("network_hash"),
        "transfer_rate": config["transfer_rate"],
        "response_delay": config["response_delay"],
        "strategy": config["strategy"],
        "beta": config["beta"],
        "gamma": config["gamma"],
        "quarantine_duration": config["quarantine_duration"],
        "k": config["k"],
        "selected_tanks": ",".join(str(t) for t in raw["selected_tanks"]),
        "intervention_start_day": raw["intervention_start_day"],
        "status": raw["status"],
        "stop_reason": raw["stop_reason"],
        "attempted_transfers": sum(d["attempted_transfers"] for d in raw["daily"]),
        "accepted_transfers": sum(d["accepted_transfers"] for d in raw["daily"]),
        "blocked_transfers": sum(d["blocked_transfers"] for d in raw["daily"]),
    }
    row.update(raw["metrics"])
    return row
