"""Author's smoke tests for the M1 baseline. The formal V-numbered suite (issue #13) is owned by Member B."""

import pytest

from turtlefarm import SimulationConfig
from turtlefarm.config import ConfigError
from turtlefarm.model import run_baseline, STATUS_COMPLETED, STATUS_CENSORED


def test_default_config_runs_and_stops():
    rec = run_baseline(SimulationConfig(epidemic_seed=1))
    assert rec.status in (STATUS_COMPLETED, STATUS_CENSORED)
    assert rec.stop_reason
    assert rec.daily[0].day == 0 and rec.daily[0].I == 1 and rec.daily[0].S == 199
    for d in rec.daily:
        assert d.S + d.I + d.R == 200


def test_same_seed_same_output():
    a = run_baseline(SimulationConfig(epidemic_seed=7, beta=0.2, gamma=0.1), record_transitions=True)
    b = run_baseline(SimulationConfig(epidemic_seed=7, beta=0.2, gamma=0.1), record_transitions=True)
    assert a.transitions == b.transitions
    assert a.metrics == b.metrics


def test_movement_free_baseline_never_leaves_initial_tank():
    rec = run_baseline(SimulationConfig(epidemic_seed=3, beta=0.5, gamma=0.05))
    assert rec.metrics["affected_tanks"] == 1
    assert rec.metrics["ever_infected"] <= 10


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(beta=1.5),
        dict(gamma=-0.1),
        dict(capacity=9),
        dict(n_agents=150),
        dict(k=21),
        dict(transfer_rate=0.1),
        dict(strategy="random", policy_seed=1),
        dict(max_days=0),
    ],
)
def test_invalid_config_rejected(kwargs):
    with pytest.raises(ConfigError):
        SimulationConfig(**kwargs)
