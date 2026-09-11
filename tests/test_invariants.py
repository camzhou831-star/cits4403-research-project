"""Formal invariant tests V001-V005, V011, V012 (docs/validation-plan.md section 2, section 7).

One test function per V id; the id is in the function name so PR descriptions can cite them.
"""

import pytest

from turtlefarm import SimulationConfig, Simulation, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.entities import I, R, S
from turtlefarm.model import InvariantError, STATUS_CENSORED, STATUS_COMPLETED, STATUS_FAILED


def _sim(**kw) -> Simulation:
    sim = Simulation(SimulationConfig(**kw))
    sim._initialise()
    return sim


# ---------------------------------------------------------------- V001 agent total is always 200
@pytest.mark.parametrize(
    "kwargs",
    [dict(n_agents=400, initial_per_tank=20), dict(n_agents=190), dict(initial_infected=0),
     dict(initial_infected=2), dict(n_tanks=10, n_agents=100), dict(n_regions=5)],
)
def test_V001_main_design_rejects_non_canonical_population(kwargs):
    with pytest.raises(ConfigError):
        SimulationConfig(**kwargs)


def test_V001_daily_summary_matches_agent_table():
    rec = run_baseline(SimulationConfig(epidemic_seed=11, beta=0.3, gamma=0.2))
    assert rec.status == STATUS_COMPLETED
    for d in rec.daily:
        assert d.S + d.I + d.R == 200
        assert sum(t["occupancy"] for t in d.tanks) == 200
        assert sum(t["S"] for t in d.tanks) == d.S
        assert sum(t["I"] for t in d.tanks) == d.I
        assert sum(t["R"] for t in d.tanks) == d.R


# ---------------------------------------------------------------- V002 each agent in exactly one tank
def test_V002_every_agent_in_exactly_one_tank():
    sim = _sim(epidemic_seed=2)
    membership = [a for t in sim.tanks for a in t.members]
    assert sorted(membership) == list(range(200))
    for ag in sim.agents:
        assert ag.agent_id in sim.tanks[ag.tank_id].members


def test_V002_duplicate_membership_is_detected():
    sim = _sim(epidemic_seed=2)
    sim.tanks[1].members.add(0)  # agent 0 lives in tank 0
    with pytest.raises(InvariantError, match="more than one tank"):
        sim._check_invariants()


def test_V002_missing_membership_is_detected():
    sim = _sim(epidemic_seed=2)
    sim.tanks[0].members.discard(0)
    with pytest.raises(InvariantError, match="not in any tank"):
        sim._check_invariants()


# ---------------------------------------------------------------- V003 state domain is exactly S/I/R
def test_V003_unknown_state_is_rejected_not_counted_as_R():
    sim = _sim(epidemic_seed=3)
    sim.agents[5].disease_state = "X"
    with pytest.raises(InvariantError, match="disease_state"):
        sim._counts()
    with pytest.raises(InvariantError, match="disease_state"):
        sim._check_invariants()


def test_V003_unknown_state_mid_run_yields_failed_record(monkeypatch):
    cfg = SimulationConfig(epidemic_seed=3, beta=0.5, gamma=0.1)
    sim = Simulation(cfg)
    original = sim._movement_stage

    def corrupt():
        if sim.day == 2:
            sim.agents[0].disease_state = "zombie"
        return original()

    monkeypatch.setattr(sim, "_movement_stage", corrupt)
    rec = sim.run()
    assert rec.status == STATUS_FAILED
    assert rec.stop_reason == "invariant failure"
    assert "zombie" in rec.error
    assert rec.config["epidemic_seed"] == 3  # provenance kept on failure


# ---------------------------------------------------------------- V005 recovered agents never re-infect
def test_V005_no_R_to_I_in_transition_log():
    for seed in range(5):
        rec = run_baseline(SimulationConfig(epidemic_seed=seed, beta=0.4, gamma=0.3), record_transitions=True)
        assert rec.status == STATUS_COMPLETED
        pairs = {(frm, to) for _day, _agent, frm, to in rec.transitions}
        assert pairs <= {(S, I), (I, R)}
        # every agent that leaves I goes to R exactly once and never appears again
        recovered = [a for _d, a, frm, to in rec.transitions if frm == I]
        assert len(recovered) == len(set(recovered))
        later = {}
        for day, a, frm, _to in rec.transitions:
            if frm == R:
                pytest.fail(f"agent {a} left R on day {day}")


@pytest.mark.parametrize("frm,to", [(R, I), (R, S), (I, S), (S, R), (S, S)])
def test_V005_illegal_transition_rejected(frm, to):
    sim = _sim(epidemic_seed=5)
    ag = sim.agents[0]
    ag.disease_state = frm
    ag.ever_infected = frm != S
    with pytest.raises(InvariantError, match="illegal transition"):
        sim._transition(ag, to)


# ---------------------------------------------------------------- V011 same config + seeds -> same outputs
def test_V011_same_seed_replay_is_identical_in_every_recorded_field():
    cfg = SimulationConfig(epidemic_seed=7, beta=0.2, gamma=0.1)
    a = run_baseline(cfg, record_transitions=True)
    b = run_baseline(cfg, record_transitions=True)
    assert a.initial_infected_agents == b.initial_infected_agents
    assert a.initial_infected_tanks == b.initial_infected_tanks
    assert a.status == b.status and a.stop_reason == b.stop_reason and a.error == b.error
    assert a.daily == b.daily
    assert a.metrics == b.metrics
    assert a.transitions == b.transitions
    assert a.seeds == b.seeds and a.config == b.config


def test_V011_different_epidemic_seed_changes_trajectory():
    trajectories = {
        tuple((d.S, d.I, d.R) for d in run_baseline(SimulationConfig(epidemic_seed=s, beta=0.2, gamma=0.1)).daily)
        for s in range(6)
    }
    assert len(trajectories) > 1


# ---------------------------------------------------------------- V012 every run ends with explicit status
def test_V012_every_run_has_status_and_stop_reason():
    for seed in range(4):
        rec = run_baseline(SimulationConfig(epidemic_seed=seed))
        assert rec.status in (STATUS_COMPLETED, STATUS_CENSORED)
        assert rec.stop_reason


def test_V012_horizon_reached_is_censored_not_completed():
    rec = run_baseline(SimulationConfig(epidemic_seed=1, beta=0.0, gamma=0.0, max_days=5))
    assert rec.status == STATUS_CENSORED
    assert rec.daily[-1].day == 5
    assert rec.metrics["time_to_extinction"] is None
    assert rec.stop_reason == "infection present at max_days=5"


def test_V012_runtime_error_becomes_failed_record_with_traceback(monkeypatch):
    sim = Simulation(SimulationConfig(epidemic_seed=1))

    def boom():
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(sim, "_movement_stage", boom)
    rec = sim.run()
    assert rec.status == STATUS_FAILED
    assert rec.stop_reason == "runtime error"
    assert rec.error.startswith("RuntimeError: disk on fire")
    assert "Traceback" in rec.error
    assert rec.seeds["epidemic_seed"] == 1


def test_V012_keyboard_interrupt_is_not_swallowed(monkeypatch):
    sim = Simulation(SimulationConfig(epidemic_seed=1))

    def interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(sim, "_movement_stage", interrupt)
    with pytest.raises(KeyboardInterrupt):
        sim.run()
