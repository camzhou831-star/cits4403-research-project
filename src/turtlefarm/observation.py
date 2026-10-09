"""Event-level observations without changing the simulation or its run-record schema.

An infectious arrival is a successful move by an already-infectious agent into a region not
initially seeded. A local infection is an S -> I transition in its post-movement tank; it does
not identify the infector or establish a transmission generation. Counts include events that
are invisible in end-of-day infectious snapshots, such as arrival followed by same-day recovery.
"""

from __future__ import annotations

from turtlefarm.config import SimulationConfig
from turtlefarm.entities import I
from turtlefarm.model import Simulation
from turtlefarm.rng import DrawSource
from turtlefarm.scenario import Layout


class ObservedSimulation(Simulation):
    """Run the original model and retain observations separately from its unchanged RunRecord.

    ``infectious_transfers`` contains successful inter-region moves only; ``local_infections``
    contains all committed S -> I events. Both lists are ordered by day and then agent ID, not
    by within-day movement priority. Neither list is persisted by the ordinary batch runner.
    The observer consults no random draws and calls each observed parent stage exactly once.
    Its movement snapshots rely on the model's one-move-per-agent-per-day rule.

    Main runs have one initially seeded region. Validation scenarios may have several or none;
    "outside initial region" then means outside the set of regions containing initial I agents.
    Region IDs are read from tanks, never inferred from agent or tank numbering.
    "Visited by I" includes initial presence and local infection, not just imported infection.
    "Regions with local transmission" counts every region with an S -> I event, including
    initially seeded regions, but the initial I agents themselves are not local infections.
    Check the returned run status: observations from failed runs are not complete outcomes.
    """

    def __init__(
        self,
        config: SimulationConfig,
        record_transitions: bool = False,
        *,
        layout: Layout | None = None,
        draws: DrawSource | None = None,
    ) -> None:
        super().__init__(config, record_transitions=record_transitions, layout=layout, draws=draws)
        self.infectious_transfers: list[dict[str, int]] = []
        self.local_infections: list[dict[str, int]] = []
        self._initial_regions: set[int] = set()
        self._regions_visited_by_I: set[int] = set()
        self._regions_with_local_transmission: set[int] = set()

    def _initialise(self) -> None:
        super()._initialise()
        self._initial_regions = {self.tanks[t].region_id for t in self.initial_infected_tanks}
        self._regions_visited_by_I.update(self._initial_regions)

    def _movement_stage(self) -> tuple[int, int, int]:
        origins = {agent.agent_id: agent.tank_id for agent in self.agents if agent.disease_state == I}
        counts = super()._movement_stage()
        for agent_id, origin_id in origins.items():
            destination_id = self.agents[agent_id].tank_id
            if origin_id == destination_id:
                continue
            origin_region = self.tanks[origin_id].region_id
            destination_region = self.tanks[destination_id].region_id
            self._regions_visited_by_I.add(destination_region)
            if origin_region != destination_region:
                self.infectious_transfers.append(
                    {
                        "day": self.day,
                        "agent_id": agent_id,
                        "origin_tank": origin_id,
                        "destination_tank": destination_id,
                        "origin_region": origin_region,
                        "destination_region": destination_region,
                    }
                )
        return counts

    def _commit(self, infections: list[int], recoveries: list[int]) -> None:
        # Read the pending infections' locations before the original synchronous commit. Only
        # publish these observations after that commit succeeds; do not turn an uncommitted draw
        # into a local infection if the parent rejects the update.
        events = [
            {
                "day": self.day,
                "agent_id": agent_id,
                "tank_id": self.agents[agent_id].tank_id,
                "region_id": self.tanks[self.agents[agent_id].tank_id].region_id,
            }
            for agent_id in infections
        ]
        super()._commit(infections, recoveries)
        self.local_infections.extend(events)
        self._regions_with_local_transmission.update(event["region_id"] for event in events)
        self._regions_visited_by_I.update(event["region_id"] for event in events)

    def observation_metrics(self) -> dict[str, int | None]:
        """Compact counts and first days; None means no qualifying event was observed.

        Repeated crossings count separately, including returns to an initially seeded region.
        First arrival and first local secondary infection exclude all initially seeded regions.
        Local-transmission region counts, in contrast, include initially seeded regions.
        """
        arrivals = [
            event["day"]
            for event in self.infectious_transfers
            if event["destination_region"] not in self._initial_regions
        ]
        outside_infections = [
            event for event in self.local_infections if event["region_id"] not in self._initial_regions
        ]
        return {
            "first_infectious_arrival": min(arrivals, default=None),
            "first_local_secondary_infection": min((event["day"] for event in outside_infections), default=None),
            "infectious_cross_region_transfers": len(self.infectious_transfers),
            "regions_visited_by_I": len(self._regions_visited_by_I),
            "regions_with_local_transmission": len(self._regions_with_local_transmission),
            "local_infections_outside_initial_region": len(outside_infections),
        }
