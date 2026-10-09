"""Turtle agents and tanks (data/methods/model.md#2-entities)."""

from __future__ import annotations

from dataclasses import dataclass, field

S, I, R = "S", "I", "R"
DISEASE_STATES = (S, I, R)

OPEN, QUARANTINED = "open", "quarantined"
MANAGEMENT_STATES = (OPEN, QUARANTINED)


@dataclass
class Agent:
    agent_id: int
    tank_id: int
    disease_state: str = S
    state_entered_day: int = 0
    ever_infected: bool = False


@dataclass
class Tank:
    tank_id: int
    region_id: int
    capacity: int
    management_state: str = OPEN
    quarantine_start_day: int | None = None
    quarantine_end_day: int | None = None  # half-open interval [start, end)
    members: set[int] = field(default_factory=set)

    @property
    def occupancy(self) -> int:
        return len(self.members)

    def is_quarantined_on(self, day: int) -> bool:
        return (
            self.quarantine_start_day is not None
            and self.quarantine_end_day is not None
            and self.quarantine_start_day <= day < self.quarantine_end_day
        )
