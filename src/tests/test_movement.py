"""Network-constrained movement tests (data/methods/model.md#9-cross-tank-movement; V102, V105, V106)."""

import pytest

from turtlefarm import Simulation, SimulationConfig, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.model import STATUS_COMPLETED


def _initialised_sim(*, transfer_rate: float, epidemic_seed: int = 0) -> Simulation:
    sim = Simulation(
        SimulationConfig(
            transfer_rate=transfer_rate,
            epidemic_seed=epidemic_seed,
            beta=0.0,
            gamma=1.0,
        )
    )
    sim._initialise()
    return sim


def test_V102_zero_transfer_rate_changes_no_locations_and_consults_no_draws():
    sim = _initialised_sim(transfer_rate=0.0)
    before = [agent.tank_id for agent in sim.agents]

    assert sim._movement_stage() == (0, 0, 0)
    assert [agent.tank_id for agent in sim.agents] == before


def test_scenario_without_a_transfer_network_rejects_nonzero_movement():
    with pytest.raises(ConfigError, match="Layout has no transfer network"):
        SimulationConfig(
            design="scenario",
            n_agents=6,
            n_tanks=3,
            n_regions=1,
            initial_per_tank=3,
            transfer_rate=0.1,
        )


def test_V105_transfer_rate_one_attempts_every_agent_and_uses_only_network_edges():
    sim = _initialised_sim(transfer_rate=1.0, epidemic_seed=7)
    before = [agent.tank_id for agent in sim.agents]

    attempted, accepted, blocked = sim._movement_stage()

    assert attempted == sim.n_agents
    assert accepted + blocked == attempted
    assert accepted > 0
    assert sum(before[a] != sim.agents[a].tank_id for a in range(sim.n_agents)) == accepted
    for agent_id, old_tank in enumerate(before):
        new_tank = sim.agents[agent_id].tank_id
        if new_tank != old_tank:
            assert new_tank in sim.network.neighbours(old_tank)


def test_V106_full_destinations_block_every_attempt_without_exceeding_capacity():
    sim = _initialised_sim(transfer_rate=1.0, epidemic_seed=8)
    before = [agent.tank_id for agent in sim.agents]
    for tank in sim.tanks:
        tank.capacity = tank.occupancy

    attempted, accepted, blocked = sim._movement_stage()

    assert (attempted, accepted, blocked) == (sim.n_agents, 0, sim.n_agents)
    assert [agent.tank_id for agent in sim.agents] == before
    assert all(tank.occupancy <= tank.capacity for tank in sim.tanks)


def test_movement_is_reproducible_and_daily_counts_are_recorded():
    cfg = SimulationConfig(transfer_rate=0.2, epidemic_seed=11, beta=0.0, gamma=1.0)
    first = run_baseline(cfg)
    second = run_baseline(cfg)

    assert first.status == second.status == STATUS_COMPLETED
    assert first.daily == second.daily
    day_one = first.daily[1]
    assert day_one.attempted_transfers > 0
    assert day_one.accepted_transfers + day_one.blocked_transfers == day_one.attempted_transfers
    assert all(tank["occupancy"] <= cfg.capacity for tank in day_one.tanks)


def test_moving_infected_agent_updates_affected_tanks_but_not_initial_provenance():
    sim = _initialised_sim(transfer_rate=1.0, epidemic_seed=7)
    initial_tanks = list(sim.initial_infected_tanks)
    infected_agent = sim.initial_infected_agents[0]
    origin = sim.agents[infected_agent].tank_id

    sim.day = 1
    sim._movement_stage()
    destination = sim.agents[infected_agent].tank_id

    assert destination != origin
    assert destination in sim.ever_affected
    record = sim.run()
    assert record.initial_infected_tanks == initial_tanks == [origin]
