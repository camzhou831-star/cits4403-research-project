"""Simulation configuration and validation (model-specification section 18; validation-plan section 4).

Values marked PROVISIONAL are working proposals awaiting facilitator confirmation (D001-D008 in
docs/decision-log.md). They are plain configuration numbers; changing them does not change model logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

STRATEGIES = ("none", "random", "betweenness")

# Provisional working proposals (docs/research-plan.md, D002 / D003 / D006).
PROVISIONAL_CAPACITY = 12
PROVISIONAL_K = 2
PROVISIONAL_MAX_DAYS = 365


class ConfigError(ValueError):
    """Raised before a run starts when the configuration is invalid. Never clamp silently."""


@dataclass(frozen=True)
class SimulationConfig:
    # Structure (fixed decisions)
    n_agents: int = 200
    n_tanks: int = 20
    n_regions: int = 4
    initial_per_tank: int = 10
    initial_infected: int = 1

    # Disease (fixed in the main experiment; values chosen by pilot, not yet frozen)
    beta: float = 0.1
    gamma: float = 0.1

    # Movement (M2). The baseline only accepts transfer_rate == 0.
    transfer_rate: float = 0.0
    capacity: int = PROVISIONAL_CAPACITY  # PROVISIONAL D002

    # Intervention (M2). The baseline only accepts strategy == "none".
    strategy: str = "none"
    response_delay: int = 0  # PROVISIONAL D001: measured from introduction at t = 0
    quarantine_duration: int = 0  # D004: select after pilot
    k: int = PROVISIONAL_K  # PROVISIONAL D003

    # Horizon
    max_days: int = PROVISIONAL_MAX_DAYS  # PROVISIONAL D006

    # Seeds (model-specification section 16)
    network_seed: int = 0
    epidemic_seed: int = 0
    policy_seed: int | None = None

    # Free-text provenance, copied into run metadata
    label: str = ""
    provisional_fields: tuple[str, ...] = field(
        default=("capacity", "k", "max_days", "response_delay"), repr=False
    )

    def __post_init__(self) -> None:
        self.validate()

    # ------------------------------------------------------------------ validation
    def validate(self) -> None:
        errs: list[str] = []

        def prob(name: str) -> None:
            v = getattr(self, name)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 <= v <= 1.0):
                errs.append(f"{name} must be a probability in [0, 1], got {v!r}")

        def nonneg_int(name: str) -> None:
            v = getattr(self, name)
            if not isinstance(v, int) or isinstance(v, bool) or v < 0:
                errs.append(f"{name} must be a non-negative integer, got {v!r}")

        def pos_int(name: str) -> None:
            v = getattr(self, name)
            if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                errs.append(f"{name} must be a positive integer, got {v!r}")

        for p in ("beta", "gamma", "transfer_rate"):
            prob(p)
        for p in ("n_agents", "n_tanks", "n_regions", "initial_per_tank", "capacity", "max_days"):
            pos_int(p)
        for p in ("initial_infected", "response_delay", "quarantine_duration", "k"):
            nonneg_int(p)
        for p in ("network_seed", "epidemic_seed"):
            nonneg_int(p)
        if self.policy_seed is not None and (
            not isinstance(self.policy_seed, int) or isinstance(self.policy_seed, bool) or self.policy_seed < 0
        ):
            errs.append(f"policy_seed must be None or a non-negative integer, got {self.policy_seed!r}")

        if self.strategy not in STRATEGIES:
            errs.append(f"strategy must be one of {STRATEGIES}, got {self.strategy!r}")

        # Structural facts fixed by the research design (validation-plan section 4).
        if self.n_tanks != 20 or self.n_regions != 4:
            errs.append("design fixes exactly 20 tanks in 4 regions")
        elif self.n_tanks % self.n_regions != 0:
            errs.append("n_tanks must divide evenly into n_regions")
        if self.n_agents != self.n_tanks * self.initial_per_tank:
            errs.append(
                f"n_agents ({self.n_agents}) must equal n_tanks * initial_per_tank "
                f"({self.n_tanks} * {self.initial_per_tank})"
            )
        if self.initial_per_tank > self.capacity:
            errs.append(f"initial occupancy {self.initial_per_tank} exceeds capacity {self.capacity}")
        if self.initial_infected > self.n_agents:
            errs.append("initial_infected exceeds n_agents")
        if self.k > self.n_tanks:
            errs.append(f"k ({self.k}) exceeds n_tanks ({self.n_tanks})")

        # Baseline scope guard (M1). Movement and quarantine arrive in M2; refuse rather than silently ignore.
        if self.transfer_rate != 0.0:
            errs.append("transfer_rate > 0 requires cross-tank movement, which is not implemented in the M1 baseline")
        if self.strategy != "none":
            errs.append(f"strategy {self.strategy!r} requires quarantine logic, which is not implemented in the M1 baseline")
        if self.strategy == "random" and self.policy_seed is None:
            errs.append("random strategy requires policy_seed")

        if errs:
            raise ConfigError("; ".join(errs))

    # ------------------------------------------------------------------ helpers
    @property
    def tanks_per_region(self) -> int:
        return self.n_tanks // self.n_regions

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["provisional_fields"] = list(self.provisional_fields)
        return d
