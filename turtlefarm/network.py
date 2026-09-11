"""Modular tank-transfer network (model-specification sections 3 and 4).

20 tanks in 4 regions of 5. Edges are drawn independently: probability ``p_in`` inside a region, ``p_out``
between regions, in a fixed pair order from a generator derived from ``(network_seed, attempt)``. An
attempt is rejected (and the next attempt index tried, deterministically) when it fails a structural
check. The accepted network is immutable (all fields are tuples or read-only mappings), hashed, and
carries its pre-outbreak betweenness ranking so that targeted selection can never use run-time
information (section 17, V010).

Determinism contract (frozen 2026-09-11, spec 3.2):
  * node pairs are visited in lexicographic ``itertools.combinations(range(n), 2)`` order;
  * attempt ``a`` draws ``n(n-1)/2`` uniforms from ``PCG64(SeedSequence(network_seed, spawn_key=(a,)))``;
  * betweenness is exact (non-sampled) normalised node betweenness; ranking ties are *exact* float
    equality of the computed values, broken by ascending tank_id.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import combinations
from types import MappingProxyType
from typing import Any

import networkx as nx
import numpy as np


class NetworkGenerationError(RuntimeError):
    """No attempt within ``max_attempts`` passed the structural checks. Carries the full rejection record."""

    def __init__(self, *, network_seed: int, p_in: float, p_out: float, rejected: tuple[str, ...]) -> None:
        self.network_seed = network_seed
        self.p_in = p_in
        self.p_out = p_out
        self.rejected = rejected
        counts = dict(Counter(rejected))
        super().__init__(
            f"network_seed={network_seed}: no attempt in {len(rejected)} passed the structural checks "
            f"(p_in={p_in}, p_out={p_out}); rejection counts: {counts}"
        )


def region_of(tank_id: int, tanks_per_region: int) -> int:
    return tank_id // tanks_per_region


def structural_rejection_reason(graph: nx.Graph, regions: tuple[int, ...]) -> str | None:
    """Pre-defined structural checks (spec 3.1 prohibitions and 3.2 step 4). None means accepted.

    1. connected;
    2. at least one inter-region edge (implied by 1 with >1 region, kept explicit for the record);
    3. not a complete graph;
    4. betweenness not identical for every node (risk R002: fully symmetric structure has no bridges).
    """
    n = graph.number_of_nodes()
    if n == 0 or not nx.is_connected(graph):
        return "not connected"
    if not any(regions[u] != regions[v] for u, v in graph.edges):
        return "no inter-region edge"
    if graph.number_of_edges() == n * (n - 1) // 2:
        return "complete graph"
    bc = nx.betweenness_centrality(graph, normalized=True)
    if len(set(bc.values())) == 1:
        return "all nodes have identical betweenness"
    return None


def rank_by_betweenness(betweenness: Sequence[float] | Mapping[int, float]) -> list[int]:
    """Descending betweenness; exact-equality ties broken by ascending tank_id (spec section 4, V110, A018).

    Accepts a sequence indexed by tank_id or a mapping tank_id -> value."""
    ids = list(betweenness.keys()) if isinstance(betweenness, Mapping) else list(range(len(betweenness)))
    return sorted(ids, key=lambda t: (-betweenness[t], t))


def tie_groups(betweenness: Sequence[float]) -> list[list[int]]:
    """Groups of tank_ids sharing exactly equal betweenness (size >= 2), ordered by descending value."""
    by_value: dict[float, list[int]] = {}
    for t, v in enumerate(betweenness):
        by_value.setdefault(v, []).append(t)
    return [ids for v, ids in sorted(by_value.items(), key=lambda kv: -kv[0]) if len(ids) > 1]


@dataclass(frozen=True)
class TransferNetwork:
    """Immutable accepted network. ``betweenness`` is a tuple indexed by tank_id; ``metrics`` is read-only."""

    n_tanks: int
    regions: tuple[int, ...]  # regions[tank_id]
    edges: tuple[tuple[int, int], ...]  # sorted (u, v) with u < v
    network_seed: int
    attempt: int  # index of the accepted attempt (0-based)
    rejected: tuple[str, ...]  # rejection reason of each earlier attempt, in order
    p_in: float
    p_out: float
    betweenness: tuple[float, ...]  # betweenness[tank_id]
    metrics: Mapping[str, float | int]
    network_hash: str
    adjacency: Mapping[int, tuple[int, ...]] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if len(self.betweenness) != self.n_tanks or len(self.regions) != self.n_tanks:
            raise ValueError("betweenness and regions must have one entry per tank")
        adj: dict[int, list[int]] = {t: [] for t in range(self.n_tanks)}
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        object.__setattr__(self, "adjacency", MappingProxyType({t: tuple(sorted(n)) for t, n in adj.items()}))
        if not isinstance(self.metrics, MappingProxyType):
            object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))

    # ------------------------------------------------------------------ derived views
    def graph(self) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(range(self.n_tanks))
        g.add_edges_from(self.edges)
        return g

    def neighbours(self, tank_id: int) -> tuple[int, ...]:
        return self.adjacency[tank_id]

    @property
    def ranking(self) -> list[int]:
        return rank_by_betweenness(self.betweenness)

    def top_k(self, k: int) -> list[int]:
        """Highest-betweenness tanks with deterministic tie-break. Uses only the pre-outbreak network."""
        return self.ranking[:k]

    def tie_ids_at_rank(self, k: int) -> list[int]:
        """Tanks whose betweenness exactly equals that of the k-th ranked tank (same rule as ranking)."""
        if k <= 0 or k > self.n_tanks:
            return []
        boundary = self.betweenness[self.ranking[k - 1]]
        return [t for t, v in enumerate(self.betweenness) if v == boundary]

    def ties_at_rank(self, k: int) -> int:
        """How many tanks share the k-th ranked betweenness value (1 = no tie at that boundary)."""
        return len(self.tie_ids_at_rank(k))

    @property
    def tie_groups(self) -> list[list[int]]:
        return tie_groups(self.betweenness)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable record for run metadata (spec 15.2): adjacency, centralities, attempt, hash."""
        return {
            "n_tanks": self.n_tanks,
            "regions": list(self.regions),
            "edges": [list(e) for e in self.edges],
            "adjacency": {str(t): list(n) for t, n in self.adjacency.items()},
            "network_seed": self.network_seed,
            "attempt": self.attempt,
            "rejected": list(self.rejected),
            "p_in": self.p_in,
            "p_out": self.p_out,
            "betweenness": list(self.betweenness),
            "ranking": self.ranking,
            "tie_groups": self.tie_groups,
            "metrics": dict(self.metrics),
            "network_hash": self.network_hash,
        }


def _network_hash(regions: tuple[int, ...], edges: tuple[tuple[int, int], ...]) -> str:
    payload = json.dumps({"regions": regions, "edges": edges}, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _attempt_edges(
    n_tanks: int, regions: tuple[int, ...], p_in: float, p_out: float, network_seed: int, attempt: int
) -> tuple[tuple[int, int], ...]:
    """One attempt: an independent draw per node pair in fixed (u, v) order (spec 3.2 steps 2-3)."""
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(network_seed, spawn_key=(attempt,))))
    pairs = list(combinations(range(n_tanks), 2))
    draws = rng.random(len(pairs))
    edges = []
    for (u, v), d in zip(pairs, draws):
        p = p_in if regions[u] == regions[v] else p_out
        if d < p:
            edges.append((u, v))
    return tuple(edges)


def network_metrics(graph: nx.Graph, regions: tuple[int, ...]) -> dict[str, float | int]:
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    inter = sum(1 for u, v in graph.edges if regions[u] != regions[v])
    communities = [{t for t in range(n) if regions[t] == r} for r in sorted(set(regions))]
    degrees = [d for _, d in graph.degree]
    return {
        "n_edges": m,
        "n_intra_edges": m - inter,
        "n_inter_edges": inter,
        "mean_degree": 2 * m / n,
        "min_degree": min(degrees),
        "max_degree": max(degrees),
        "density": nx.density(graph),
        "clustering": nx.average_clustering(graph),
        "modularity": nx.community.modularity(graph, communities),
        "diameter": nx.diameter(graph),
    }


def generate_network(
    *,
    network_seed: int,
    p_in: float,
    p_out: float,
    n_tanks: int = 20,
    n_regions: int = 4,
    max_attempts: int = 100,
) -> TransferNetwork:
    """Deterministic modular network for ``network_seed``; retries attempts until the structural checks
    pass (spec 3.2 step 4). Same inputs always give the same network and the same attempt index."""
    for name, v in (("network_seed", network_seed), ("n_tanks", n_tanks), ("n_regions", n_regions), ("max_attempts", max_attempts)):
        if not isinstance(v, int) or isinstance(v, bool):
            raise ValueError(f"{name} must be an integer, got {v!r}")
    if network_seed < 0 or n_tanks <= 0 or n_regions <= 0 or max_attempts <= 0:
        raise ValueError("network_seed must be >= 0; n_tanks, n_regions and max_attempts must be positive")
    if n_tanks % n_regions != 0:
        raise ValueError("n_tanks must divide evenly into n_regions")
    for name, v in (("p_in", p_in), ("p_out", p_out)):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(f"{name} must be a number, got {v!r}")
    if not (0.0 < p_out < p_in <= 1.0):
        raise ValueError(f"require 0 < p_out < p_in <= 1, got p_in={p_in}, p_out={p_out}")
    per_region = n_tanks // n_regions
    regions = tuple(region_of(t, per_region) for t in range(n_tanks))

    rejected: list[str] = []
    for attempt in range(max_attempts):
        edges = _attempt_edges(n_tanks, regions, p_in, p_out, network_seed, attempt)
        g = nx.Graph()
        g.add_nodes_from(range(n_tanks))
        g.add_edges_from(edges)
        reason = structural_rejection_reason(g, regions)
        if reason is not None:
            rejected.append(reason)
            continue
        bc_map = nx.betweenness_centrality(g, normalized=True)
        bc = tuple(float(bc_map[t]) for t in range(n_tanks))
        return TransferNetwork(
            n_tanks=n_tanks,
            regions=regions,
            edges=edges,
            network_seed=network_seed,
            attempt=attempt,
            rejected=tuple(rejected),
            p_in=p_in,
            p_out=p_out,
            betweenness=bc,
            metrics=MappingProxyType(network_metrics(g, regions)),
            network_hash=_network_hash(regions, edges),
        )
    raise NetworkGenerationError(network_seed=network_seed, p_in=p_in, p_out=p_out, rejected=tuple(rejected))
