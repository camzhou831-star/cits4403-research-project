"""Exploratory (post-hoc) measures of why a short quarantine has a small effect.

Added after the formal results, to test the mechanism the report had only proposed. Two questions:

* **Position.** How much of the between-region structure do the selected tanks cover? Measured on the
  pre-outbreak network: the share of between-region edges with an endpoint in a selected tank, and whether
  removing the selected tanks disconnects the network.
* **Timing.** When does an outbreak first reach a second region, relative to the quarantine window, and
  had the selected tanks already held infection when quarantine started?

Everything is read from recorded runs (raw JSONL records and the summary table); nothing re-runs the model.
Because draws are event-keyed, a baseline run and the intervention runs of its block are identical until the
quarantine starts, so the baseline trajectory gives the state at the response day for every arm.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import networkx as nx


def between_region_edges(edges: Iterable[Iterable[int]], regions: list[int]) -> list[tuple[int, int]]:
    return [(a, b) for a, b in edges if regions[a] != regions[b]]


def bridge_coverage(edges: Iterable[Iterable[int]], regions: list[int], selected: Iterable[int]) -> float:
    """Share of between-region edges with at least one endpoint in ``selected``."""
    bridges = between_region_edges(edges, regions)
    chosen = set(selected)
    return sum(1 for a, b in bridges if a in chosen or b in chosen) / len(bridges)


def removal_disconnects(edges: Iterable[Iterable[int]], n_tanks: int, selected: Iterable[int]) -> bool:
    """True if deleting the selected tanks leaves the remaining tanks in more than one component."""
    graph = nx.Graph()
    graph.add_nodes_from(range(n_tanks))
    graph.add_edges_from(map(tuple, edges))
    graph.remove_nodes_from(set(selected))
    return nx.number_connected_components(graph) > 1


def first_cross_region_day(raw: Mapping[str, Any]) -> int | None:
    """First day on which a tank outside the initial region holds an infectious agent (None if never)."""
    regions = raw["network"]["regions"]
    home = regions[raw["initial_infected_tanks"][0]]
    for day in raw["daily"]:
        if any(t["I"] > 0 and regions[t["tank_id"]] != home for t in day["tanks"]):
            return day["day"]
    return None


def tanks_ever_infected_by(raw: Mapping[str, Any], day: int) -> set[int]:
    """Tanks that held an infectious agent at the end of any day up to and including ``day``."""
    seen: set[int] = set()
    for record in raw["daily"]:
        if record["day"] > day:
            break
        seen |= {t["tank_id"] for t in record["tanks"] if t["I"] > 0}
    return seen
