"""Extreme-case tests V101, V103, V104 (data/methods/validation.md#extreme-and-boundary-cases)."""

from turtlefarm import SimulationConfig, run_baseline
from turtlefarm.entities import I, R, S
from turtlefarm.model import STATUS_COMPLETED


# ---------------------------------------------------------------- V101 beta = 0: no transmission at all
def test_V101_beta_zero_never_infects_anyone_else():
    for seed in range(5):
        rec = run_baseline(SimulationConfig(epidemic_seed=seed, beta=0.0, gamma=0.3), record_transitions=True)
        assert rec.status == STATUS_COMPLETED
        assert rec.metrics["ever_infected"] == 1
        assert rec.metrics["final_attack_rate"] == 1 / 200
        assert rec.metrics["affected_tanks"] == 1
        assert all(d.new_infections == 0 for d in rec.daily)
        assert [(frm, to) for _d, _a, frm, to in rec.transitions] == [(I, R)]


# ---------------------------------------------------------------- V103 gamma = 1: recover exactly one day later
def test_V103_gamma_one_every_infection_lasts_exactly_one_day():
    for seed in range(5):
        rec = run_baseline(SimulationConfig(epidemic_seed=seed, beta=0.6, gamma=1.0), record_transitions=True)
        assert rec.status == STATUS_COMPLETED
        infected_on = {a: d for d, a, frm, to in rec.transitions if to == I}
        recovered_on = {a: d for d, a, frm, to in rec.transitions if to == R}
        # the initial case is infectious on day 0 and recovers on day 1
        initial = rec.initial_infected_agents[0]
        assert recovered_on[initial] == 1
        for a, d in infected_on.items():
            assert recovered_on[a] == d + 1, f"agent {a} infected day {d} recovered day {recovered_on.get(a)}"


def test_V103_transmit_then_recover_within_a_day():
    """An agent infectious at the start of a day both transmits and (with gamma = 1) recovers that day."""
    rec = run_baseline(SimulationConfig(epidemic_seed=0, beta=1.0, gamma=1.0))
    d1 = rec.daily[1]
    assert d1.new_infections == 9 and d1.recoveries == 1


# ---------------------------------------------------------------- V104 beta = 1: whole tank infected next day
def test_V104_beta_one_infects_every_susceptible_tankmate_next_day():
    for seed in range(5):
        rec = run_baseline(SimulationConfig(epidemic_seed=seed, beta=1.0, gamma=0.5))
        d1 = rec.daily[1]
        assert d1.S == 190 and d1.I + d1.R == 10, d1
        assert d1.new_infections == 9
        assert d1.affected_tanks_ever == 1
        tank = rec.initial_infected_tanks[0]
        assert rec.daily[1].tanks[tank]["S"] == 0
        assert rec.metrics["ever_infected"] == 10  # no movement, so no other tank is ever reached


def test_V104_newly_infected_do_not_transmit_or_recover_on_their_infection_day():
    """Reference sequence for beta = 1, gamma = 1 (reviewed 2026-09-11):
    day 0: 199/1/0  day 1: 190/9/1  day 2: 190/0/10.
    Day 1: the initial case infects its 9 tankmates and recovers. The 9 newly infected neither recover
    on day 1 (I = 9, not 0) nor transmit on day 1 (nothing else to infect anyway). Day 2: all 9 recover."""
    rec = run_baseline(SimulationConfig(epidemic_seed=0, beta=1.0, gamma=1.0))
    got = [(d.S, d.I, d.R) for d in rec.daily]
    assert got == [(199, 1, 0), (190, 9, 1), (190, 0, 10)]
    assert rec.status == STATUS_COMPLETED and rec.stop_reason == "extinction on day 2"
    assert rec.metrics == {
        "final_attack_rate": 10 / 200,
        "ever_infected": 10,
        "affected_tanks": 1,
        "peak_infected": 9,
        "time_to_peak": 1,
        "time_to_extinction": 2,
        "days_simulated": 2,
        "intervention_cost": 0,
    }
