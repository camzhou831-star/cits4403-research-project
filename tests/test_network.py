"""Transfer network tests (spec sections 3-4; validation-plan V010, V110; risk R002)."""

import networkx as nx
import pytest

from turtlefarm import SimulationConfig, generate_network, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.network import (
    NetworkGenerationError,
    rank_by_betweenness,
    structural_rejection_reason,
)

P = dict(p_in=0.6, p_out=0.05)


def test_fixed_region_assignment_four_by_five():
    net = generate_network(network_seed=0, **P)
    assert net.n_tanks == 20
    assert net.regions == tuple(t // 5 for t in range(20))
    assert net.edges == tuple(sorted(net.edges)) and all(u < v for u, v in net.edges)


def test_same_seed_same_network_and_attempt():
    a = generate_network(network_seed=3, **P)
    b = generate_network(network_seed=3, **P)
    assert a == b
    assert a.network_hash == b.network_hash and a.attempt == b.attempt


def test_different_seeds_differ():
    hashes = {generate_network(network_seed=s, **P).network_hash for s in range(8)}
    assert len(hashes) == 8


def test_accepted_network_passes_structural_checks():
    for seed in range(10):
        net = generate_network(network_seed=seed, **P)
        g = net.graph()
        assert nx.is_connected(g)
        assert net.metrics["n_inter_edges"] >= 1
        assert net.metrics["n_edges"] < 190
        assert len(set(round(v, 12) for v in net.betweenness.values())) > 1
        assert structural_rejection_reason(g, net.regions) is None


def test_rejected_attempts_are_recorded_and_deterministic():
    # tiny p_out makes disconnected first attempts likely; the record must show them
    net = generate_network(network_seed=0, p_in=0.6, p_out=0.01)
    assert net.attempt == len(net.rejected)
    assert all(r in ("not connected", "no inter-region edge") for r in net.rejected)
    assert generate_network(network_seed=0, p_in=0.6, p_out=0.01) == net


def test_max_attempts_exceeded_raises():
    with pytest.raises(NetworkGenerationError):
        generate_network(network_seed=0, p_in=0.2, p_out=0.001, max_attempts=3)


@pytest.mark.parametrize("p_in,p_out", [(0.5, 0.5), (0.3, 0.6), (0.6, 0.0), (1.1, 0.1)])
def test_invalid_probabilities_rejected(p_in, p_out):
    with pytest.raises(ValueError):
        generate_network(network_seed=0, p_in=p_in, p_out=p_out)
    with pytest.raises(ConfigError):
        SimulationConfig(p_in=p_in, p_out=p_out)


# ---------------------------------------------------------------- structural checks on hand-built graphs
def _regions():
    return tuple(t // 5 for t in range(20))


def test_structural_check_rejects_complete_graph():
    assert structural_rejection_reason(nx.complete_graph(20), _regions()) == "complete graph"


def test_structural_check_rejects_disconnected():
    g = nx.Graph()
    g.add_nodes_from(range(20))
    g.add_edges_from([(t, t + 1) for t in range(19) if t != 9])
    assert structural_rejection_reason(g, _regions()) == "not connected"


def test_structural_check_rejects_symmetric_ring():
    """A 20-cycle is connected, has inter-region edges and is not complete, but every node has the same
    betweenness, so there is no bridge tank to target (R002)."""
    assert structural_rejection_reason(nx.cycle_graph(20), _regions()) == "all nodes have identical betweenness"


# ---------------------------------------------------------------- betweenness ranking and ties (V110)
def test_V110_ties_break_by_ascending_tank_id():
    bc = {0: 0.1, 1: 0.5, 2: 0.5, 3: 0.9, 4: 0.1}
    assert rank_by_betweenness(bc) == [3, 1, 2, 0, 4]
    bc_reordered = {4: 0.1, 2: 0.5, 3: 0.9, 0: 0.1, 1: 0.5}
    assert rank_by_betweenness(bc_reordered) == [3, 1, 2, 0, 4]


def test_top_k_and_tie_count():
    net = generate_network(network_seed=0, **P)
    assert net.top_k(2) == net.ranking[:2]
    assert net.ties_at_rank(1) >= 1
    assert net.betweenness[net.top_k(1)[0]] == max(net.betweenness.values())


# ---------------------------------------------------------------- V010: pre-outbreak only, in run metadata
def test_V010_network_independent_of_epidemic_seed_and_recorded_in_run():
    a = run_baseline(SimulationConfig(network_seed=5, epidemic_seed=1))
    b = run_baseline(SimulationConfig(network_seed=5, epidemic_seed=2))
    assert a.network == b.network
    assert a.network["network_hash"] == generate_network(network_seed=5, **P).network_hash
    for key in ("attempt", "edges", "regions", "betweenness", "ranking", "metrics", "rejected"):
        assert key in a.network


def test_scenario_runs_carry_no_network():
    from tests.test_hand_trace import CONFIG, DRAWS, LAYOUT
    from turtlefarm import TableDraws

    rec = run_baseline(CONFIG, layout=LAYOUT, draws=TableDraws(DRAWS))
    assert rec.network is None
