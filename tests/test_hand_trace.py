"""Hand-traced 3-tank / 6-agent scenario (issue #14, docs/hand-trace-3tank.md).

The expected values below were computed by hand in the document and must not be regenerated from the
model. The draw table contains *only* the draws the specification says are consulted; if the model ever
consults another (e.g. a recovery draw for an agent infected the same day) TableDraws raises and the
run fails, which the assertions catch."""

import pytest

from turtlefarm import AgentSpec, Layout, SimulationConfig, TableDraws, TankSpec, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.entities import I, R, S
from turtlefarm.model import STATUS_COMPLETED

LAYOUT = Layout(
    tanks=(TankSpec(0, region_id=0, capacity=12), TankSpec(1, region_id=0, capacity=12), TankSpec(2, region_id=1, capacity=12)),
    agents=(
        AgentSpec(0, tank_id=0, disease_state=I),
        AgentSpec(1, tank_id=0),
        AgentSpec(2, tank_id=0),
        AgentSpec(3, tank_id=1),
        AgentSpec(4, tank_id=1),
        AgentSpec(5, tank_id=2),
    ),
)

CONFIG = SimulationConfig(design="scenario", n_agents=6, n_tanks=3, n_regions=1, initial_per_tank=3, beta=0.5, gamma=0.5, max_days=10, label="hand-trace-3tank")

# (process, day, agent_id) -> uniform draw. See docs/hand-trace-3tank.md table 2.
DRAWS = {
    ("transmission", 1, 1): 0.30,  # p = 0.5  -> infected
    ("transmission", 1, 2): 0.60,  # p = 0.5  -> stays S
    ("recovery", 1, 0): 0.70,      # gamma = 0.5 -> stays I
    ("transmission", 2, 2): 0.70,  # p = 1 - 0.5^2 = 0.75 -> infected (would NOT be with p = 0.5)
    ("recovery", 2, 0): 0.20,      # recovers
    ("recovery", 2, 1): 0.90,      # stays I
    ("recovery", 3, 1): 0.40,      # recovers
    ("recovery", 3, 2): 0.10,      # recovers
}

EXPECTED_DAILY = [  # (day, S, I, R, new_infections, recoveries, affected_now, affected_ever)
    (0, 5, 1, 0, 0, 0, 1, 1),
    (1, 4, 2, 0, 1, 0, 1, 1),
    (2, 3, 2, 1, 1, 1, 1, 1),
    (3, 3, 0, 3, 0, 2, 0, 1),
]

EXPECTED_TRANSITIONS = [  # commit order within a day: recoveries first, then infections
    (1, 1, S, I),
    (2, 0, I, R),
    (2, 2, S, I),
    (3, 1, I, R),
    (3, 2, I, R),
]

EXPECTED_CONSULTED = [
    ("transmission", 1, 1), ("transmission", 1, 2), ("recovery", 1, 0),
    ("transmission", 2, 2), ("recovery", 2, 0), ("recovery", 2, 1),
    ("recovery", 3, 1), ("recovery", 3, 2),
]


def test_hand_trace_matches_event_log():
    draws = TableDraws(DRAWS)
    rec = run_baseline(CONFIG, record_transitions=True, layout=LAYOUT, draws=draws)
    assert rec.status == STATUS_COMPLETED, rec.error
    assert rec.stop_reason == "extinction on day 3"
    got = [(d.day, d.S, d.I, d.R, d.new_infections, d.recoveries, d.affected_tanks_now, d.affected_tanks_ever) for d in rec.daily]
    assert got == EXPECTED_DAILY
    assert rec.transitions == EXPECTED_TRANSITIONS
    assert draws.consulted == EXPECTED_CONSULTED
    assert rec.initial_infected_agents == [0] and rec.initial_infected_tanks == [0]
    assert rec.metrics == {
        "final_attack_rate": 0.5,
        "ever_infected": 3,
        "affected_tanks": 1,
        "peak_infected": 2,
        "time_to_peak": 1,
        "time_to_extinction": 3,
        "days_simulated": 3,
        "intervention_cost": 0,
    }
    assert rec.config["design"] == "scenario"


def test_hand_trace_per_tank_rows():
    rec = run_baseline(CONFIG, layout=LAYOUT, draws=TableDraws(DRAWS))
    day2 = {t["tank_id"]: (t["S"], t["I"], t["R"]) for t in rec.daily[2].tanks}
    assert day2 == {0: (0, 2, 1), 1: (2, 0, 0), 2: (1, 0, 0)}


def test_hand_trace_fails_loudly_if_an_unlisted_draw_is_consulted():
    """Dropping the day-2 draw for agent 2 must break the run: the model really consults it."""
    table = dict(DRAWS)
    del table[("transmission", 2, 2)]
    rec = run_baseline(CONFIG, layout=LAYOUT, draws=TableDraws(table))
    assert rec.status == "failed"
    assert "MissingDrawError" in rec.error and "('transmission', 2, 2)" in rec.error


def test_scenario_design_requires_layout_and_vice_versa():
    with pytest.raises(ConfigError):
        run_baseline(CONFIG)  # scenario without layout
    with pytest.raises(ConfigError):
        run_baseline(SimulationConfig(epidemic_seed=1), layout=LAYOUT)  # main design with layout
    with pytest.raises(ConfigError):
        run_baseline(SimulationConfig(design="scenario", n_agents=5, n_tanks=3, n_regions=1, initial_per_tank=3), layout=LAYOUT)
