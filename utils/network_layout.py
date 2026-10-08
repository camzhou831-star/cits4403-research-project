"""Deterministic layout of a tank transfer network for figures and animations.

Used by scripts/analyse_results.py (Figure 1) and scripts/demo_animation.py (demo video), so both draw the
same network in the same positions.
"""

from __future__ import annotations

import math

import networkx as nx


def network_layout(edges: list, regions: list[int]) -> dict[int, tuple[float, float]]:
    """Deterministic spring layout (numpy only), started from one quadrant per region so regions stay grouped
    while connected tanks are pulled together."""
    graph = nx.Graph()
    graph.add_nodes_from(range(len(regions)))
    graph.add_edges_from(map(tuple, edges))
    corners = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
    start = {
        t: (corners[r % 4][0] + 0.3 * math.cos(t), corners[r % 4][1] + 0.3 * math.sin(t)) for t, r in enumerate(regions)
    }
    layout = nx.spring_layout(graph, pos=start, seed=0, iterations=500)
    pos = {t: [float(x), float(y)] for t, (x, y) in layout.items()}
    # collision relaxation: push apart tanks closer than min_dist (dense regions otherwise collapse)
    span = max(max(abs(x), abs(y)) for x, y in pos.values())
    min_dist = 0.16 * span
    for _ in range(300):
        moved = False
        for a in pos:
            for b in pos:
                if a >= b:
                    continue
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    if dist == 0:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (min_dist - dist) / 2
                    pos[a][0] -= push * dx / dist
                    pos[a][1] -= push * dy / dist
                    pos[b][0] += push * dx / dist
                    pos[b][1] += push * dy / dist
                    moved = True
        if not moved:
            break
    return {t: (x, y) for t, (x, y) in pos.items()}


def edges_crossing_nodes(edges: list, pos: dict, clearance: float) -> list[tuple[int, int, int]]:
    """(a, b, tank) where edge a-b passes within ``clearance`` of a tank that is not one of its ends."""
    hits = []
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        length2 = (x2 - x1) ** 2 + (y2 - y1) ** 2 or 1e-12
        for tank, (x, y) in pos.items():
            if tank in (a, b):
                continue
            t = max(0.0, min(1.0, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / length2))
            if math.hypot(x - (x1 + t * (x2 - x1)), y - (y1 + t * (y2 - y1))) < clearance:
                hits.append((a, b, tank))
    return hits
