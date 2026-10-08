"""Explicit small-scenario layouts for validation only (validation-plan section 9).

The main research design fixes 200 agents in 20 tanks (config ``design="main"``). Hand-traceable
scenarios need a handful of tanks and agents, so they are built from an explicit ``Layout`` under
``design="scenario"``. A scenario run records ``design="scenario"`` in its metadata; the experiment
runner must refuse anything but ``design="main"``.
"""

from __future__ import annotations

from dataclasses import dataclass

from turtlefarm.entities import DISEASE_STATES, S


class LayoutError(ValueError):
    """The layout is internally inconsistent."""


@dataclass(frozen=True)
class TankSpec:
    tank_id: int
    region_id: int
    capacity: int


@dataclass(frozen=True)
class AgentSpec:
    agent_id: int
    tank_id: int
    disease_state: str = S


@dataclass(frozen=True)
class Layout:
    tanks: tuple[TankSpec, ...]
    agents: tuple[AgentSpec, ...]

    def __post_init__(self) -> None:
        self.validate()

    @property
    def n_tanks(self) -> int:
        return len(self.tanks)

    @property
    def n_agents(self) -> int:
        return len(self.agents)

    @property
    def n_regions(self) -> int:
        return len({t.region_id for t in self.tanks})

    def validate(self) -> None:
        errs: list[str] = []
        if [t.tank_id for t in self.tanks] != list(range(len(self.tanks))):
            errs.append("tank_ids must be contiguous 0..n_tanks-1 in order")
        if [a.agent_id for a in self.agents] != list(range(len(self.agents))):
            errs.append("agent_ids must be contiguous 0..n_agents-1 in order")
        if not self.tanks or not self.agents:
            errs.append("layout needs at least one tank and one agent")
        occupancy = [0] * len(self.tanks)
        for a in self.agents:
            if a.disease_state not in DISEASE_STATES:
                errs.append(f"agent {a.agent_id} has state {a.disease_state!r}, expected one of {DISEASE_STATES}")
            if not 0 <= a.tank_id < len(self.tanks):
                errs.append(f"agent {a.agent_id} placed in unknown tank {a.tank_id}")
            else:
                occupancy[a.tank_id] += 1
        for t in self.tanks:
            if t.capacity <= 0:
                errs.append(f"tank {t.tank_id} capacity must be positive")
            elif t.tank_id < len(occupancy) and occupancy[t.tank_id] > t.capacity:
                errs.append(f"tank {t.tank_id} occupancy {occupancy[t.tank_id]} exceeds capacity {t.capacity}")
        if errs:
            raise LayoutError("; ".join(errs))
