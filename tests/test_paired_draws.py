"""Event-keyed draws (model-specification section 16): the draw for (process, day, agent) depends only on
the epidemic seed, never on which other draws were consulted. This is the property that keeps random and
targeted strategies paired under one epidemic seed."""

import pytest

from turtlefarm import EventKeyedDraws, TableDraws
from turtlefarm.rng import MissingDrawError, PROCESSES


def test_draw_is_a_pure_function_of_seed_process_day_agent():
    a = EventKeyedDraws(42, 200)
    b = EventKeyedDraws(42, 200)
    # consult b in a completely different order / subset first
    b.uniform("recovery", 9, 199)
    b.uniform("transmission", 3, 0)
    for day in (1, 2, 3, 50):
        for agent in (0, 17, 199):
            for process in PROCESSES:
                assert a.uniform(process, day, agent) == b.uniform(process, day, agent)


def test_skipping_draws_does_not_shift_later_draws():
    """Strategy A consults agents 0..9 on day 1; strategy B only agent 9. Both see the same value."""
    a = EventKeyedDraws(7, 200)
    b = EventKeyedDraws(7, 200)
    for agent in range(10):
        a.uniform("transmission", 1, agent)
    assert a.uniform("transmission", 1, 9) == b.uniform("transmission", 1, 9)
    assert a.uniform("transmission", 2, 0) == b.uniform("transmission", 2, 0)


def test_processes_days_agents_and_seeds_are_independent():
    d = EventKeyedDraws(1, 200)
    assert d.uniform("transmission", 1, 0) != d.uniform("recovery", 1, 0)
    assert d.uniform("transmission", 1, 0) != d.uniform("transmission", 2, 0)
    assert d.uniform("transmission", 1, 0) != d.uniform("transmission", 1, 1)
    assert d.uniform("transmission", 1, 0) != EventKeyedDraws(2, 200).uniform("transmission", 1, 0)


def test_draws_are_uniform_in_unit_interval():
    d = EventKeyedDraws(3, 200)
    vals = [d.uniform("recovery", day, a) for day in range(1, 30) for a in range(200)]
    assert all(0.0 <= v < 1.0 for v in vals)
    assert 0.45 < sum(vals) / len(vals) < 0.55


def test_agent_out_of_range_rejected():
    with pytest.raises(IndexError):
        EventKeyedDraws(3, 200).uniform("recovery", 1, 200)


def test_table_draws_record_and_refuse_missing_keys():
    t = TableDraws({("transmission", 1, 1): 0.3})
    assert t.uniform("transmission", 1, 1) == 0.3
    with pytest.raises(MissingDrawError):
        t.uniform("recovery", 1, 0)
    assert t.consulted == [("transmission", 1, 1)]


@pytest.mark.parametrize("bad", [{("nope", 1, 1): 0.1}, {("recovery", 1, 1): 1.0}, {("recovery", 1, 1): -0.1}])
def test_table_draws_validate_input(bad):
    with pytest.raises(ValueError):
        TableDraws(bad)
