"""Blocked transfers attributed to quarantine or capacity (pilot-protocol section 4, quarantine-specific Q1)."""

from pathlib import Path

import pandas as pd
import pytest

from turtlefarm import Simulation, SimulationConfig, run_baseline
from turtlefarm.entities import OPEN, QUARANTINED
from turtlefarm.runner import ExperimentDesign, flatten, to_raw_record

ROOT = Path(__file__).resolve().parent.parent
CAUSES = ("blocked_quarantine_out", "blocked_quarantine_in", "blocked_capacity")


def _config(strategy: str, **overrides) -> SimulationConfig:
    values = dict(strategy=strategy, transfer_rate=1.0, beta=0.0, gamma=1.0, network_seed=0, epidemic_seed=7)
    if strategy != "none":
        values.update(response_delay=0, quarantine_duration=3, k=2)
    if strategy == "random":
        values["policy_seed"] = 3
    values.update(overrides)
    return SimulationConfig(**values)


@pytest.mark.parametrize("strategy", ["none", "random", "betweenness"])
def test_causes_partition_blocked_transfers_every_day(strategy):
    record = run_baseline(_config(strategy, transfer_rate=0.3, beta=0.3, gamma=0.1))
    for day in record.daily:
        assert sum(getattr(day, cause) for cause in CAUSES) == day.blocked_transfers


def test_capacity_only_blocking_without_quarantine():
    sim = Simulation(_config("none"))
    sim._initialise()
    for tank in sim.tanks:
        tank.capacity = tank.occupancy

    attempted, accepted, blocked = sim._movement_stage()

    assert (attempted, accepted, blocked) == (sim.n_agents, 0, sim.n_agents)
    assert sim._blocked_by_cause == {"quarantine_out": 0, "quarantine_in": 0, "capacity": sim.n_agents}


def test_quarantined_origin_counts_as_quarantine_out():
    sim = Simulation(_config("betweenness"))
    sim._initialise()
    sim.step()  # response_delay 0: quarantine is active on the first movement stage

    inside = sum(sim.tanks[t].occupancy for t in sim.selected_tanks)
    day = sim.daily[-1]
    assert inside > 0
    assert day.blocked_quarantine_out == inside


def test_quarantine_out_is_rule_attribution_not_additional_prevented_movement():
    """Origin quarantine wins the rule order even when full neighbours would also block movement."""
    summaries = []
    for quarantined in (False, True):
        sim = Simulation(_config("none"))
        sim._initialise()
        for tank in sim.tanks:
            tank.capacity = tank.occupancy
        if quarantined:
            sim.tanks[0].management_state = QUARANTINED
        counts = sim._movement_stage()
        assert counts == (sim.n_agents, 0, sim.n_agents)
        assert sum(sim._blocked_by_cause.values()) == counts[2]
        summaries.append(dict(sim._blocked_by_cause))
        if quarantined:
            assert sim._blocked_by_cause["quarantine_out"] == sim.tanks[0].occupancy > 0
    assert summaries[0]["quarantine_out"] == 0
    assert summaries[1]["capacity"] < summaries[0]["capacity"]


def _origin_with_neighbours(sim: Simulation) -> tuple[int, list[int]]:
    for tank in sim.tanks:
        neighbours = list(sim.network.neighbours(tank.tank_id))
        if neighbours and tank.occupancy > 0:
            return tank.tank_id, neighbours
    raise AssertionError("network has no occupied tank with neighbours")


def _isolate_agents_in(sim: Simulation, origin: int) -> None:
    """Make only agents in ``origin`` attempt to move; everyone else stays put via a closed origin."""
    for tank in sim.tanks:
        if tank.tank_id != origin:
            tank.management_state = QUARANTINED
            tank.quarantine_start_day = sim.day
            tank.quarantine_end_day = sim.day + 1


def test_quarantined_neighbour_with_space_counts_as_quarantine_in():
    sim = Simulation(_config("none"))
    sim._initialise()
    origin, neighbours = _origin_with_neighbours(sim)
    _isolate_agents_in(sim, origin)  # every neighbour is now quarantined; some have space

    sim._movement_stage()

    assert sim._blocked_by_cause["quarantine_in"] == sim.tanks[origin].occupancy
    assert sim._blocked_by_cause["capacity"] == 0


def test_quarantined_but_full_neighbours_count_as_capacity():
    sim = Simulation(_config("none"))
    sim._initialise()
    origin, neighbours = _origin_with_neighbours(sim)
    _isolate_agents_in(sim, origin)
    for t in neighbours:
        sim.tanks[t].capacity = sim.tanks[t].occupancy  # would be ineligible even if open

    sim._movement_stage()

    assert sim._blocked_by_cause["quarantine_in"] == 0
    assert sim._blocked_by_cause["capacity"] == sim.tanks[origin].occupancy
    assert all(sim.tanks[t].management_state == QUARANTINED for t in neighbours)
    assert sim.tanks[origin].management_state == OPEN


def test_flatten_sums_causes_and_leaves_old_raw_records_empty():
    raw = to_raw_record(run_baseline(_config("random", transfer_rate=0.3)), run_id="x", timestamp_utc="t")
    row = flatten(raw)
    assert sum(row[cause] for cause in CAUSES) == row["blocked_transfers"]

    for day in raw["daily"]:
        for cause in CAUSES:
            del day[cause]
    assert all(flatten(raw)[cause] is None for cause in CAUSES)


KEY = ["network_seed", "epidemic_seed", "policy_seed", "transfer_rate", "response_delay", "strategy", "quarantine_duration"]


def test_counters_do_not_change_committed_stage2_pilot_runs():
    """Rerunning a sample of committed Stage 2 pilot configurations reproduces every recorded outcome.

    Matched on the condition key: configuration_hash differs because provisional_fields was emptied by the
    parameter freeze after the pilot ran (pilot-protocol section 4)."""
    design = ExperimentDesign.from_json(ROOT / "experiments" / "config" / "pilot-stage2-intervention.json")
    committed = pd.read_csv(ROOT / "results" / "summary" / "pilot-stage2-intervention.csv")
    committed["policy_seed"] = committed["policy_seed"].astype("Int64")
    committed = committed.set_index(KEY)
    columns = ["selected_tanks", "intervention_start_day", "status", "attempted_transfers", "accepted_transfers",
               "blocked_transfers", "final_attack_rate", "affected_tanks", "peak_infected", "days_simulated"]
    for cfg in design.configs()[::400]:
        row = flatten(to_raw_record(run_baseline(cfg), run_id="x", timestamp_utc="t"))
        expected = committed.loc[tuple(pd.NA if row[k] is None else row[k] for k in KEY)]
        for column in columns:
            got, want = row[column], expected[column]
            if pd.isna(want):
                assert got is None or pd.isna(got) or got == "", column
            elif isinstance(want, str):
                assert str(got) == want, column
            else:
                assert got == pytest.approx(want), column
