"""Transfer network tests (spec sections 3-4; validation-plan V010, V110; risk R002)."""

import json
import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

from turtlefarm import SimulationConfig, generate_network, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.network import (
    NetworkGenerationError,
    rank_by_betweenness,
    structural_rejection_reason,
    tie_groups,
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
        assert len(set(net.betweenness)) > 1
        assert structural_rejection_reason(g, net.regions) is None


def test_rejected_attempts_are_recorded_and_deterministic():
    # tiny p_out makes disconnected first attempts likely; the record must show them
    net = generate_network(network_seed=0, p_in=0.6, p_out=0.01)
    assert net.attempt == len(net.rejected)
    assert all(r in ("not connected", "no inter-region edge") for r in net.rejected)
    assert generate_network(network_seed=0, p_in=0.6, p_out=0.01) == net


def test_max_attempts_exceeded_raises_with_full_rejection_record():
    with pytest.raises(NetworkGenerationError) as info:
        generate_network(network_seed=0, p_in=0.2, p_out=0.001, max_attempts=3)
    err = info.value
    assert err.network_seed == 0 and err.p_in == 0.2 and err.p_out == 0.001
    assert len(err.rejected) == 3 and all(isinstance(r, str) for r in err.rejected)
    assert "rejection counts" in str(err)


@pytest.mark.parametrize("kwargs", [dict(network_seed=-1), dict(network_seed=1.5), dict(n_regions=0), dict(n_tanks=7, n_regions=4), dict(max_attempts=0), dict(p_in="x")])
def test_generate_network_validates_arguments(kwargs):
    args = dict(network_seed=0, **P)
    args.update(kwargs)
    with pytest.raises(ValueError):
        generate_network(**args)


# ---------------------------------------------------------------- immutability (spec 17, V010)
def test_network_is_deeply_immutable():
    net = generate_network(network_seed=0, **P)
    with pytest.raises(TypeError):
        net.betweenness[0] = 1.0
    with pytest.raises(TypeError):
        net.metrics["n_edges"] = 0
    with pytest.raises(TypeError):
        net.adjacency[0] = ()
    with pytest.raises((AttributeError, TypeError)):
        net.attempt = 5


def test_V010_ranking_and_hash_unchanged_by_running_the_epidemic():
    from turtlefarm import Simulation

    sim = Simulation(SimulationConfig(network_seed=4, epidemic_seed=9, beta=0.4, gamma=0.2))
    sim._initialise()
    before = (sim.network.network_hash, tuple(sim.network.ranking), sim.network.betweenness)
    rec = sim.run()
    assert rec.status == "completed"
    assert (sim.network.network_hash, tuple(sim.network.ranking), sim.network.betweenness) == before
    assert rec.network["ranking"] == list(before[1])


# ---------------------------------------------------------------- adjacency in metadata (spec 3.2 / 15.2)
def test_adjacency_matches_edges_and_is_json_serialisable():
    net = generate_network(network_seed=2, **P)
    d = net.to_dict()
    json.dumps(d)  # must not raise
    assert set(d["adjacency"]) == {str(t) for t in range(20)}
    rebuilt = set()
    for t, nbrs in d["adjacency"].items():
        for v in nbrs:
            rebuilt.add((min(int(t), v), max(int(t), v)))
            assert int(t) in d["adjacency"][str(v)]  # symmetric
    assert rebuilt == {tuple(e) for e in d["edges"]}
    assert d["betweenness"] == list(net.betweenness) and len(d["betweenness"]) == 20
    assert d["tie_groups"] == net.tie_groups


# ---------------------------------------------------------------- golden fixture and cross-process replay
def test_golden_seed0():
    """Locks the determinism contract (pair order, PCG64 seeding, structural checks). If this changes,
    the generator's behaviour changed and every recorded network hash becomes stale: update deliberately
    and record the change in docs/decision-log.md."""
    net = generate_network(network_seed=0, **P)
    assert net.attempt == 1 and net.rejected == ("not connected",)
    assert net.metrics["n_edges"] == 34 and net.metrics["n_inter_edges"] == 11
    assert net.ranking[:3] == [16, 9, 7]
    assert net.network_hash == GOLDEN_HASH_SEED0


GOLDEN_HASH_SEED0 = generate_network(network_seed=0, **P).network_hash  # pinned in test_golden_hash_literal


def test_golden_hash_literal():
    assert GOLDEN_HASH_SEED0 == "2f20c54948e6831e"


def test_replay_in_fresh_process_gives_same_hash():
    code = (
        "from turtlefarm import generate_network;"
        "n = generate_network(network_seed=0, p_in=0.6, p_out=0.05);"
        "print(n.network_hash, n.attempt)"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                         cwd=Path(__file__).resolve().parent.parent / "src")
    assert out.stdout.split() == [GOLDEN_HASH_SEED0, "1"]


# ---------------------------------------------------------------- hand-checked centralities
def test_normalised_betweenness_on_hand_computed_graphs():
    star = nx.star_graph(4)  # centre 0, leaves 1-4
    bc = nx.betweenness_centrality(star, normalized=True)
    assert bc[0] == 1.0 and all(bc[l] == 0.0 for l in range(1, 5))
    path = nx.path_graph(5)  # 0-1-2-3-4: node 2 carries 4 of 6 pairs, node 1 carries 3
    bc = nx.betweenness_centrality(path, normalized=True)
    assert abs(bc[2] - 4 / 6) < 1e-12 and abs(bc[1] - 3 / 6) < 1e-12 and bc[0] == 0.0
    assert rank_by_betweenness([bc[t] for t in range(5)]) == [2, 1, 3, 0, 4]
    assert tie_groups([bc[t] for t in range(5)]) == [[1, 3], [0, 4]]


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
    assert rank_by_betweenness([0.1, 0.5, 0.5, 0.9, 0.1]) == [3, 1, 2, 0, 4]


def test_tie_rule_is_exact_equality_everywhere():
    """Ranking, tie_ids_at_rank and tie_groups must agree: values differing by 5e-13 are NOT a tie."""
    from turtlefarm.network import TransferNetwork
    from types import MappingProxyType

    bc = [0.0] * 20
    bc[3], bc[7] = 0.5, 0.5 - 5e-13
    net = TransferNetwork(n_tanks=20, regions=_regions(), edges=((3, 7),), network_seed=0, attempt=0, rejected=(),
                          p_in=0.6, p_out=0.05, betweenness=tuple(bc), metrics=MappingProxyType({}), network_hash="x")
    assert net.ranking[:2] == [3, 7]
    assert net.tie_ids_at_rank(1) == [3] and net.ties_at_rank(2) == 1
    assert net.tie_groups == [list(range(0, 3)) + list(range(4, 7)) + list(range(8, 20))]


def test_top_k_and_tie_count():
    net = generate_network(network_seed=0, **P)
    assert net.top_k(2) == net.ranking[:2]
    assert net.ties_at_rank(1) >= 1
    assert net.betweenness[net.top_k(1)[0]] == max(net.betweenness)


# ---------------------------------------------------------------- V010: pre-outbreak only, in run metadata
def test_V010_network_independent_of_epidemic_seed_and_recorded_in_run():
    a = run_baseline(SimulationConfig(network_seed=5, epidemic_seed=1))
    b = run_baseline(SimulationConfig(network_seed=5, epidemic_seed=2))
    assert a.network == b.network
    assert a.network["network_hash"] == generate_network(network_seed=5, **P).network_hash
    for key in ("attempt", "edges", "adjacency", "regions", "betweenness", "ranking", "tie_groups", "metrics", "rejected", "network_hash"):
        assert key in a.network


def test_scenario_runs_carry_no_network():
    from tests.test_hand_trace import CONFIG, DRAWS, LAYOUT
    from turtlefarm import TableDraws

    rec = run_baseline(CONFIG, layout=LAYOUT, draws=TableDraws(DRAWS))
    assert rec.network is None
