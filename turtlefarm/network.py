"""Modular tank-transfer network (model-specification sections 3 and 4).

20 tanks in 4 regions of 5. Edges are drawn independently: probability ``p_in`` inside a region, ``p_out``
between regions, in a fixed pair order from a generator derived from ``(network_seed, attempt)``. An
attempt is rejected (and the next attempt index tried, deterministically) when it fails a structural
check. The accepted network is immutable, hashed, and carries its pre-outbreak betweenness ranking so
that targeted selection can never use run-time information (section 17, V010).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from typing import Any

import networkx as nx
import numpy as np


class NetworkGenerationError(RuntimeError):
    """No attempt within ``max_attempts`` passed the structural checks."""


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
    if max(bc.values()) - min(bc.values()) < 1e-12:
        return "all nodes have identical betweenness"
    return None


def rank_by_betweenness(betweenness: dict[int, float]) -> list[int]:
    """Descending betweenness; ties broken by ascending tank_id (spec section 4, V110, A018)."""
    return sorted(betweenness, key=lambda t: (-betweenness[t], t))


@dataclass(frozen=True)
class TransferNetwork:
    n_tanks: int
    regions: tuple[int, ...]  # regions[tank_id]
    edges: tuple[tuple[int, int], ...]  # sorted (u, v) with u < v
    network_seed: int
    attempt: int  # index of the accepted attempt (0-based)
    rejected: tuple[str, ...]  # rejection reason of each earlier attempt, in order
    p_in: float
    p_out: float
    betweenness: dict[int, float]
    metrics: dict[str, float | int]
    network_hash: str

    # ------------------------------------------------------------------ derived views
    def graph(self) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(range(self.n_tanks))
        g.add_edges_from(self.edges)
        return g

    @property
    def adjacency(self) -> dict[int, tuple[int, ...]]:
        adj: dict[int, list[int]] = {t: [] for t in range(self.n_tanks)}
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        return {t: tuple(sorted(n)) for t, n in adj.items()}

    def neighbours(self, tank_id: int) -> tuple[int, ...]:
        return self.adjacency[tank_id]

    @property
    def ranking(self) -> list[int]:
        return rank_by_betweenness(self.betweenness)

    def top_k(self, k: int) -> list[int]:
        """Highest-betweenness tanks with deterministic tie-break. Uses only the pre-outbreak network."""
        return self.ranking[:k]

    def ties_at_rank(self, k: int) -> int:
        """How many tanks share the betweenness value of the k-th ranked tank (1 = no tie)."""
        if k <= 0 or k > self.n_tanks:
            return 0
        boundary = self.betweenness[self.ranking[k - 1]]
        return sum(1 for v in self.betweenness.values() if abs(v - boundary) < 1e-12)

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_tanks": self.n_tanks,
            "regions": list(self.regions),
            "edges": [list(e) for e in self.edges],
            "network_seed": self.network_seed,
            "attempt": self.attempt,
            "rejected": list(self.rejected),
            "p_in": self.p_in,
            "p_out": self.p_out,
            "betweenness": {str(t): v for t, v in self.betweenness.items()},
            "ranking": self.ranking,
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
    if n_tanks % n_regions != 0:
        raise ValueError("n_tanks must divide evenly into n_regions")
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
        bc = {int(t): float(v) for t, v in nx.betweenness_centrality(g, normalized=True).items()}
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
            metrics=network_metrics(g, regions),
            network_hash=_network_hash(regions, edges),
        )
    raise NetworkGenerationError(
        f"network_seed={network_seed}: no attempt in {max_attempts} passed the structural checks "
        f"(p_in={p_in}, p_out={p_out}); last reasons: {rejected[-5:]}"
    )
