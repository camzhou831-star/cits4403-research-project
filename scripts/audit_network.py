"""Structural audit of the modular network generator (issue #16, risk R002, D005 candidates).

Runs generate_network over a grid of (p_in, p_out) candidates and a list of network seeds and prints a
Markdown table. No epidemic is simulated; this is a structural pilot only, not hypothesis evidence.

Usage: python scripts/audit_network.py [--seeds 10] [--k 2]
"""

from __future__ import annotations

import argparse
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import networkx as nx

from turtlefarm.network import NetworkGenerationError, generate_network


def cross_region_path_share(net, tank: int) -> float:
    """Mean over cross-region node pairs (s, t) of the fraction of shortest s-t paths passing through
    ``tank`` as an interior node. 1.0 would mean every cross-region shortest path uses it."""
    g = net.graph()
    shares = []
    for s in range(net.n_tanks):
        for t in range(s + 1, net.n_tanks):
            if net.regions[s] == net.regions[t] or tank in (s, t):
                continue
            paths = list(nx.all_shortest_paths(g, s, t))
            shares.append(sum(1 for p in paths if tank in p[1:-1]) / len(paths))
    return sum(shares) / len(shares)

GRID = [(p_in, p_out) for p_in in (0.5, 0.6, 0.7, 0.8) for p_out in (0.03, 0.05, 0.08, 0.10)]


def audit(p_in: float, p_out: float, seeds: range, k: int) -> dict[str, float | int | str]:
    nets = []
    failed = 0
    for s in seeds:
        try:
            nets.append(generate_network(network_seed=s, p_in=p_in, p_out=p_out))
        except NetworkGenerationError:
            failed += 1
    if not nets:
        return {"p_in": p_in, "p_out": p_out, "failed": failed}
    top_bridge = 0
    for n in nets:
        top = n.top_k(1)[0]
        if any(n.regions[v] != n.regions[top] for v in n.neighbours(top)):
            top_bridge += 1
    return {
        "p_in": p_in,
        "p_out": p_out,
        "failed": failed,
                "mean_attempt": st.mean(n.attempt for n in nets),
        "max_attempt": max(n.attempt for n in nets),
        "mean_deg": st.mean(n.metrics["mean_degree"] for n in nets),
        "inter_edges": st.mean(n.metrics["n_inter_edges"] for n in nets),
        "density": st.mean(n.metrics["density"] for n in nets),
        "clustering": st.mean(n.metrics["clustering"] for n in nets),
        "modularity": st.mean(n.metrics["modularity"] for n in nets),
        "diameter": st.mean(n.metrics["diameter"] for n in nets),
        "bc_top1": st.mean(n.betweenness[n.top_k(1)[0]] for n in nets),
        "bc_top2": st.mean(n.betweenness[n.top_k(2)[1]] for n in nets),
        "bc_median": st.mean(st.median(n.betweenness) for n in nets),
        "distinct_bc": st.mean(len(set(n.betweenness)) for n in nets),
        "tie_at_k": sum(1 for n in nets if n.ties_at_rank(k) > 1),
        "top1_is_bridge": top_bridge,
        "top1_xpath": st.mean(cross_region_path_share(n, n.top_k(1)[0]) for n in nets),
        "top2_xpath": st.mean(cross_region_path_share(n, n.top_k(2)[1]) for n in nets),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--k", type=int, default=2)
    args = ap.parse_args()
    seeds = range(args.seeds)
    cols = ["p_in", "p_out", "failed", "mean_attempt", "max_attempt", "mean_deg", "inter_edges", "density",
            "clustering", "modularity", "diameter", "bc_top1", "bc_top2", "bc_median", "distinct_bc", "tie_at_k",
            "top1_is_bridge", "top1_xpath", "top2_xpath"]
    print(f"Seeds 0..{args.seeds - 1}, k = {args.k}. tie_at_k / top1_is_bridge are counts out of {args.seeds} seeds; "
          "top1_xpath / top2_xpath = mean share of cross-region shortest paths passing through the rank-1 / rank-2 tank.\n")
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for p_in, p_out in GRID:
        row = audit(p_in, p_out, seeds, args.k)
        cells = []
        for c in cols:
            v = row.get(c, "")
            cells.append(f"{v:.3f}" if isinstance(v, float) else str(v))
        print("| " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
