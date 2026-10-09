"""Exact event observations remain separate from the original model and its random draws."""

from dataclasses import asdict

import pytest

from turtlefarm.config import SimulationConfig
from turtlefarm.entities import I, R
from turtlefarm.mechanism import first_cross_region_day
from turtlefarm.model import STATUS_CENSORED, STATUS_COMPLETED, Simulation
from turtlefarm.network import generate_network
from turtlefarm.observation import ObservedSimulation
from turtlefarm.rng import EventKeyedDraws, TableDraws, initialisation_stream
from turtlefarm.scenario import AgentSpec, Layout, TankSpec


@pytest.mark.parametrize("network_seed,epidemic_seed", [(0, 7), (3, 9)])
@pytest.mark.parametrize(
    "overrides",
    [
        {"transfer_rate": 0.0, "beta": 0.0, "gamma": 1.0},
        {"transfer_rate": 0.3, "beta": 1.0, "gamma": 0.0},
        {"transfer_rate": 1.0, "capacity": 10},
        {"strategy": "random", "policy_seed": 1000, "response_delay": 1, "quarantine_duration": 2},
        {"strategy": "betweenness", "response_delay": 0, "quarantine_duration": 2},
        {"strategy": "betweenness", "response_delay": 30, "quarantine_duration": 2, "beta": 0.0, "gamma": 1.0},
    ],
)
def test_observer_preserves_complete_run_record(network_seed, epidemic_seed, overrides):
    values = dict(network_seed=network_seed, epidemic_seed=epidemic_seed, transfer_rate=0.2, max_days=6)
    values.update(overrides)
    config = SimulationConfig(**values)
    plain = Simulation(config, record_transitions=True).run()
    observed = ObservedSimulation(config, record_transitions=True)
    record = observed.run()

    assert record.status in (STATUS_COMPLETED, STATUS_CENSORED), record.error
    assert asdict(record) == asdict(plain)
    assert len(observed.local_infections) == sum(day.new_infections for day in record.daily)
    assert observed.observation_metrics()["infectious_cross_region_transfers"] <= sum(
        day.accepted_transfers for day in record.daily
    )


class _RecordingDraws(EventKeyedDraws):
    def __init__(self, seed, n_agents):
        super().__init__(seed, n_agents)
        self.consulted = []

    def uniform(self, process, day, agent_id):
        self.consulted.append((process, day, agent_id))
        return super().uniform(process, day, agent_id)


def test_observer_consults_exactly_the_same_draws_in_the_same_order():
    config = SimulationConfig(transfer_rate=0.4, beta=0.3, gamma=0.2, max_days=8, epidemic_seed=7)
    plain_draws = _RecordingDraws(config.epidemic_seed, config.n_agents)
    observed_draws = _RecordingDraws(config.epidemic_seed, config.n_agents)
    plain = Simulation(config, draws=plain_draws).run()
    observed = ObservedSimulation(config, draws=observed_draws).run()
    assert asdict(observed) == asdict(plain)
    assert observed_draws.consulted == plain_draws.consulted


def _forced_move_case(*, beta=0.0, gamma=1.0, days=1, cross_region=True):
    """Force exactly one agent's path on a real generated main-design graph, with explicit draws."""
    network = generate_network(network_seed=0, p_in=0.6, p_out=0.05)
    origin, destination = next(
        (u, v) for u, v in network.edges if (network.regions[u] != network.regions[v]) == cross_region
    )
    for seed in range(1000):
        initial_agent = int(initialisation_stream(seed).choice(200, size=1, replace=False)[0])
        if initial_agent // 10 == origin:
            break
    else:
        raise AssertionError("no initialisation seed found for the chosen edge endpoint")
    config = SimulationConfig(
        network_seed=0, epidemic_seed=seed, transfer_rate=0.5, beta=beta, gamma=gamma, max_days=days
    )
    table = {}
    for day in range(1, days + 1):
        start, end = (origin, destination) if day % 2 else (destination, origin)
        neighbours = network.neighbours(start)
        for agent_id in range(config.n_agents):
            table["movement", day, agent_id] = 0.1 if agent_id == initial_agent else 0.9
            table["transmission", day, agent_id] = 0.5
            table["recovery", day, agent_id] = 0.5
        table["movement_destination", day, initial_agent] = (neighbours.index(end) + 0.5) / len(neighbours)
    return config, table, initial_agent, origin, destination, network


def test_infectious_arrival_is_seen_even_when_agent_recovers_the_same_day():
    config, table, initial_agent, origin, destination, network = _forced_move_case()
    observed = ObservedSimulation(config, draws=TableDraws(table))
    record = observed.run()
    plain = Simulation(config, draws=TableDraws(table)).run()

    assert asdict(record) == asdict(plain)
    assert record.status == STATUS_COMPLETED, record.error
    assert record.daily[-1].I == 0
    assert record.metrics["affected_tanks"] == 2  # the existing primary outcome already sees the visit
    assert first_cross_region_day(asdict(record)) is None  # end-of-day I snapshots miss it
    assert observed.infectious_transfers == [
        {
            "day": 1,
            "agent_id": initial_agent,
            "origin_tank": origin,
            "destination_tank": destination,
            "origin_region": network.regions[origin],
            "destination_region": network.regions[destination],
        }
    ]
    assert observed.observation_metrics() == {
        "first_infectious_arrival": 1,
        "first_local_secondary_infection": None,
        "infectious_cross_region_transfers": 1,
        "regions_visited_by_I": 2,
        "regions_with_local_transmission": 0,
        "local_infections_outside_initial_region": 0,
    }


def test_local_infection_is_distinct_from_arrival_and_uses_post_movement_location():
    config, table, _initial_agent, _origin, destination, network = _forced_move_case(beta=1.0)
    observed = ObservedSimulation(config, draws=TableDraws(table))
    record = observed.run()
    assert record.status == STATUS_CENSORED, record.error
    assert observed.observation_metrics() == {
        "first_infectious_arrival": 1,
        "first_local_secondary_infection": 1,
        "infectious_cross_region_transfers": 1,
        "regions_visited_by_I": 2,
        "regions_with_local_transmission": 1,
        "local_infections_outside_initial_region": 10,
    }
    assert observed.local_infections == [
        {"day": 1, "agent_id": agent_id, "tank_id": destination, "region_id": network.regions[destination]}
        for agent_id in range(destination * 10, destination * 10 + 10)
    ]


def test_repeated_crossings_include_a_return_but_regions_are_distinct():
    config, table, _initial_agent, _origin, _destination, _network = _forced_move_case(gamma=0.0, days=2)
    observed = ObservedSimulation(config, draws=TableDraws(table))
    record = observed.run()
    assert record.status == STATUS_CENSORED, record.error
    metrics = observed.observation_metrics()
    assert [event["day"] for event in observed.infectious_transfers] == [1, 2]
    assert metrics["infectious_cross_region_transfers"] == 2
    assert metrics["regions_visited_by_I"] == 2
    assert metrics["first_infectious_arrival"] == 1
    assert metrics["first_local_secondary_infection"] is None


def test_susceptible_crossing_is_not_an_infectious_transfer():
    config, table, initial_agent, origin, destination, network = _forced_move_case()
    susceptible_agent = next(agent_id for agent_id in range(origin * 10, origin * 10 + 10) if agent_id != initial_agent)
    table["movement", 1, susceptible_agent] = 0.2
    neighbours = network.neighbours(origin)
    table["movement_destination", 1, susceptible_agent] = (neighbours.index(destination) + 0.5) / len(neighbours)
    observed = ObservedSimulation(config, draws=TableDraws(table))
    record = observed.run()
    assert record.status == STATUS_COMPLETED, record.error
    assert record.daily[-1].accepted_transfers == 2
    assert observed.observation_metrics()["infectious_cross_region_transfers"] == 1
    assert observed.infectious_transfers[0]["agent_id"] == initial_agent


def test_within_region_infectious_move_does_not_count_as_a_crossing():
    config, table, _initial_agent, _origin, _destination, _network = _forced_move_case(cross_region=False)
    observed = ObservedSimulation(config, draws=TableDraws(table))
    record = observed.run()
    assert record.status == STATUS_COMPLETED, record.error
    assert record.daily[-1].accepted_transfers == 1
    assert record.metrics["affected_tanks"] == 2
    assert observed.observation_metrics()["infectious_cross_region_transfers"] == 0
    assert observed.observation_metrics()["regions_visited_by_I"] == 1
    assert observed.observation_metrics()["first_infectious_arrival"] is None


def test_zero_movement_local_transmission_includes_initial_region_but_not_initial_case():
    observed = ObservedSimulation(SimulationConfig(transfer_rate=0.0, beta=1.0, gamma=0.0, max_days=1))
    record = observed.run()
    assert record.status == STATUS_CENSORED, record.error
    assert len(observed.local_infections) == 9
    assert observed.observation_metrics() == {
        "first_infectious_arrival": None,
        "first_local_secondary_infection": None,
        "infectious_cross_region_transfers": 0,
        "regions_visited_by_I": 1,
        "regions_with_local_transmission": 1,
        "local_infections_outside_initial_region": 0,
    }


def test_scenario_uses_actual_region_ids_and_excludes_all_initial_regions_from_outside_counts():
    layout = Layout(
        tanks=(TankSpec(0, 42, 3), TankSpec(1, 7, 3), TankSpec(2, 99, 3)),
        agents=(
            AgentSpec(0, 0, I), AgentSpec(1, 0), AgentSpec(2, 1, I), AgentSpec(3, 1),
            AgentSpec(4, 2, R), AgentSpec(5, 2),
        ),
    )
    config = SimulationConfig(
        design="scenario", n_agents=6, n_tanks=3, n_regions=1, initial_per_tank=2,
        initial_infected=2, beta=1.0, gamma=1.0, max_days=1,
    )
    observed = ObservedSimulation(config, layout=layout)
    record = observed.run()
    assert asdict(record) == asdict(Simulation(config, layout=layout).run())
    assert {event["region_id"] for event in observed.local_infections} == {42, 7}
    assert observed.observation_metrics() == {
        "first_infectious_arrival": None,
        "first_local_secondary_infection": None,
        "infectious_cross_region_transfers": 0,
        "regions_visited_by_I": 2,
        "regions_with_local_transmission": 2,
        "local_infections_outside_initial_region": 0,
    }


def test_no_initial_infection_has_no_visits_or_local_transmission():
    layout = Layout(tanks=(TankSpec(0, 42, 2),), agents=(AgentSpec(0, 0), AgentSpec(1, 0, R)))
    config = SimulationConfig(
        design="scenario", n_agents=2, n_tanks=1, n_regions=1, initial_per_tank=2, initial_infected=0, k=0
    )
    observed = ObservedSimulation(config, layout=layout)
    record = observed.run()
    assert record.status == STATUS_COMPLETED and record.daily[-1].day == 0
    assert observed.observation_metrics() == {
        "first_infectious_arrival": None,
        "first_local_secondary_infection": None,
        "infectious_cross_region_transfers": 0,
        "regions_visited_by_I": 0,
        "regions_with_local_transmission": 0,
        "local_infections_outside_initial_region": 0,
    }
