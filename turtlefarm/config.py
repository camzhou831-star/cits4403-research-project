"""Simulation configuration and validation (model-specification section 18; validation-plan section 4).

D001-D003 and D006 were frozen on 2026-09-11 after Checkpoint 1 (docs/decision-log.md). Numeric values
listed in ``PROVISIONAL_FIELDS`` (beta, gamma, quarantine_duration; network p_in/p_out arrive in M2) are
candidates until the pilot (model-specification section 18, layer 2) and are recorded in run metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, ClassVar

STRATEGIES = ("none", "random", "betweenness")

# Frozen decisions D002 / D003 / D006 (docs/decision-log.md, 2026-09-11).
DEFAULT_CAPACITY = 12
DEFAULT_K = 2
DEFAULT_MAX_DAYS = 365


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
    beta: float = 0.1  # PROVISIONAL: frozen after pilot
    gamma: float = 0.1  # PROVISIONAL: frozen after pilot

    # Movement (M2). The baseline only accepts transfer_rate == 0.
    transfer_rate: float = 0.0
    capacity: int = DEFAULT_CAPACITY  # D002 frozen

    # Intervention (M2). The baseline only accepts strategy == "none".
    strategy: str = "none"
    response_delay: int = 0  # D001 frozen: measured from introduction at t = 0
    quarantine_duration: int = 0  # PROVISIONAL D004: select after pilot
    k: int = DEFAULT_K  # D003 frozen

    # Horizon
    max_days: int = DEFAULT_MAX_DAYS  # D006 frozen

    # Seeds (model-specification section 16)
    network_seed: int = 0
    epidemic_seed: int = 0
    policy_seed: int | None = None

    # Free-text provenance, copied into run metadata
    label: str = ""

    # Fields whose numeric value is still a candidate (model-specification section 18, layer 2).
    # Derived from the decision log, not settable by callers; copied into run metadata.
    PROVISIONAL_FIELDS: ClassVar[tuple[str, ...]] = ("beta", "gamma", "quarantine_duration")

    @property
    def provisional_fields(self) -> tuple[str, ...]:
        return self.PROVISIONAL_FIELDS

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
