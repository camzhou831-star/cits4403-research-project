"""Tank-quarantine tests (model specification sections 11-12; V107-V110)."""

import pytest

from turtlefarm import Simulation, SimulationConfig, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.entities import OPEN, QUARANTINED


def _config(strategy: str, **overrides) -> SimulationConfig:
    values = dict(
        strategy=strategy,
        transfer_rate=1.0,
        response_delay=0,
        quarantine_duration=2,
        k=2,
        beta=0.0,
        gamma=1.0,
        network_seed=0,
        epidemic_seed=7,
    )
    if strategy == "random":
        values["policy_seed"] = 3
    values.update(overrides)
    return SimulationConfig(**values)


@pytest.mark.parametrize(
    "kwargs,match",
    [
        (dict(strategy="random", quarantine_duration=2), "policy_seed"),
        (dict(strategy="random", policy_seed=1), "quarantine_duration"),
        (dict(strategy="betweenness", quarantine_duration=2, k=0), "k must be positive"),
        (dict(strategy="betweenness", quarantine_duration=2, policy_seed=1), "only valid"),
        (dict(strategy="none", policy_seed=1), "only valid"),
    ],
)
def test_intervention_configuration_is_validated(kwargs, match):
    with pytest.raises(ConfigError, match=match):
        SimulationConfig(**kwargs)


def test_random_selection_is_reproducible_and_independent_of_epidemic_seed():
    selected = []
    for epidemic_seed in (1, 2, 99):
        sim = Simulation(_config("random", epidemic_seed=epidemic_seed, policy_seed=17))
        sim._initialise()
        selected.append(sim.selected_tanks)

    assert selected[0] == selected[1] == selected[2]
    assert len(selected[0]) == 2 and len(set(selected[0])) == 2


def test_betweenness_selection_uses_pre_outbreak_network_ranking():
    sim = Simulation(_config("betweenness"))
    sim._initialise()

    assert sim.selected_tanks == sim.network.top_k(sim.cfg.k)


def test_V108_zero_delay_activates_before_first_movement_stage_and_blocks_both_directions():
    sim = Simulation(_config("betweenness", quarantine_duration=3))
    sim._initialise()
    members_before = {tank_id: set(sim.tanks[tank_id].members) for tank_id in sim.selected_tanks}

    sim.step()

    assert sim.day == 1 and sim.intervention_start_day == 1
    assert all(sim.tanks[tank_id].management_state == QUARANTINED for tank_id in sim.selected_tanks)
    assert {tank_id: set(sim.tanks[tank_id].members) for tank_id in sim.selected_tanks} == members_before
    assert sim.daily[-1].blocked_transfers >= sum(len(members) for members in members_before.values())


def test_response_delay_activates_on_the_scheduled_stage_day():
    sim = Simulation(_config("betweenness", response_delay=3))
    sim._initialise()

    for day in (1, 2):
        sim.day = day
        sim._management_update()
        assert sim.intervention_start_day is None
        assert all(tank.management_state == OPEN for tank in sim.tanks)

    sim.day = 3
    sim._management_update()
    assert sim.intervention_start_day == 3


def test_V107_quarantine_interval_is_half_open_and_releases_before_end_day_movement():
    sim = Simulation(_config("betweenness", quarantine_duration=2))
    sim._initialise()

    sim.day = 1
    sim._management_update()
    assert all(sim.tanks[t].is_quarantined_on(1) for t in sim.selected_tanks)
    assert all(sim.tanks[t].quarantine_end_day == 3 for t in sim.selected_tanks)

    sim.day = 2
    sim._management_update()
    assert all(sim.tanks[t].management_state == QUARANTINED for t in sim.selected_tanks)

    sim.day = 3
    sim._management_update()
    assert all(sim.tanks[t].management_state == OPEN for t in sim.selected_tanks)
    assert all(sim.tanks[t].quarantine_start_day is None for t in sim.selected_tanks)
    assert all(sim.tanks[t].quarantine_end_day is None for t in sim.selected_tanks)


def test_V109_no_intervention_ignores_response_delay_and_has_zero_cost():
    common = dict(transfer_rate=0.2, epidemic_seed=11, beta=0.2, gamma=0.1, max_days=60)
    first = run_baseline(SimulationConfig(response_delay=0, **common))
    second = run_baseline(SimulationConfig(response_delay=20, **common))

    assert first.daily == second.daily
    assert first.metrics == second.metrics
    assert first.selected_tanks == second.selected_tanks == []
    assert first.intervention_start_day is second.intervention_start_day is None
    assert first.intervention_cost == second.intervention_cost == 0


def test_random_and_betweenness_strategies_use_the_same_intervention_budget():
    random_record = run_baseline(_config("random"))
    targeted_record = run_baseline(_config("betweenness"))

    expected_cost = 2 * 2
    assert random_record.intervention_cost == targeted_record.intervention_cost == expected_cost
    assert random_record.metrics["intervention_cost"] == expected_cost
    assert targeted_record.metrics["intervention_cost"] == expected_cost
    assert len(random_record.selected_tanks) == len(targeted_record.selected_tanks) == 2


def test_quarantine_run_is_reproducible_with_the_same_seeds():
    cfg = _config("random", transfer_rate=0.2, beta=0.2, gamma=0.1, max_days=60)
    first = run_baseline(cfg)
    second = run_baseline(cfg)

    assert first.selected_tanks == second.selected_tanks
    assert first.intervention_start_day == second.intervention_start_day
    assert first.daily == second.daily
    assert first.metrics == second.metrics
