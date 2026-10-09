"""Exploratory mechanism measures (turtlefarm.mechanism) on hand-checkable inputs."""

from turtlefarm.mechanism import (
    between_region_edges,
    bridge_coverage,
    first_cross_region_day,
    removal_disconnects,
    tanks_ever_infected_by,
)

# Two regions of two tanks: 0-1 in region 0, 2-3 in region 1, bridges 1-2 and 0-3.
EDGES = [(0, 1), (2, 3), (1, 2), (0, 3)]
REGIONS = [0, 0, 1, 1]


def test_between_region_edges_and_coverage():
    assert between_region_edges(EDGES, REGIONS) == [(1, 2), (0, 3)]
    assert bridge_coverage(EDGES, REGIONS, [1]) == 0.5
    assert bridge_coverage(EDGES, REGIONS, [1, 3]) == 1.0
    assert bridge_coverage(EDGES, REGIONS, []) == 0.0


def test_removal_disconnects():
    assert not removal_disconnects(EDGES, 4, [0])  # a 4-cycle stays connected without one node
    assert removal_disconnects(EDGES, 4, [0, 2])  # tanks 1 and 3 are left without an edge


def _raw(daily_infectious):
    """daily_infectious: list of {tank_id: I} for days 0, 1, ..."""
    return {
        "network": {"regions": REGIONS},
        "initial_infected_tanks": [0],
        "daily": [
            {"day": d, "tanks": [{"tank_id": t, "I": infected.get(t, 0)} for t in range(4)]}
            for d, infected in enumerate(daily_infectious)
        ],
    }


def test_first_cross_region_day():
    assert first_cross_region_day(_raw([{0: 1}, {0: 1, 1: 1}, {1: 1, 2: 1}])) == 2
    assert first_cross_region_day(_raw([{0: 1}, {1: 1}, {}])) is None


def test_tanks_ever_infected_by_includes_recovered_tanks():
    raw = _raw([{0: 1}, {1: 1}, {2: 1}])  # tank 0 recovered by day 1 but still counts
    assert tanks_ever_infected_by(raw, 1) == {0, 1}
    assert tanks_ever_infected_by(raw, 0) == {0}
