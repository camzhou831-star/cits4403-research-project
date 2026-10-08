"""Exploratory (post-hoc) analysis of why a 2-tank, D-day quarantine has a small effect.

Reads the recorded formal runs (results/raw/<design>.jsonl and results/summary/<design>.csv), computes the
position and timing measures of turtlefarm.mechanism and writes them to
results/analysis/<design>/mechanism.json, from which scripts/build_report.py fills the report.

Usage:
    python scripts/mechanism_analysis.py              # design formal-nested
    python scripts/mechanism_analysis.py --design formal-nested
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]  # src/: the turtlefarm package; root: utils/

import pandas as pd

from turtlefarm.mechanism import (
    between_region_edges,
    bridge_coverage,
    first_cross_region_day,
    removal_disconnects,
    tanks_ever_infected_by,
)
from turtlefarm.runner import iter_raw

FOCUS_RATE = 0.025  # the intermediate transfer rate, where quarantine effects are largest


def selected(text: str) -> list[int]:
    return [int(t) for t in str(text).split(",")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--design", default="formal-nested")
    args = parser.parse_args()
    design = json.loads((ROOT / "experiments" / "config" / f"{args.design}.json").read_text(encoding="utf-8"))
    summary = pd.read_csv(ROOT / "results" / "summary" / f"{args.design}.csv")
    duration = int(design["fixed"]["quarantine_duration"])

    # One pass over the baseline runs: networks, first crossing day, infected tanks by day.
    networks, crossing, baselines = {}, {}, {}
    for raw in iter_raw(ROOT / "results" / "raw" / f"{args.design}.jsonl"):
        cfg = raw["config"]
        if cfg["strategy"] != "none" or cfg["transfer_rate"] == 0:
            continue
        networks.setdefault(cfg["network_seed"], raw["network"])
        key = (cfg["network_seed"], cfg["epidemic_seed"], cfg["transfer_rate"])
        baselines[key] = raw
        if cfg["transfer_rate"] == FOCUS_RATE:
            crossing[key] = first_cross_region_day(raw)

    # Position: targeted tanks vs the random tanks actually drawn, per network.
    interventions = summary[summary["strategy"] != "none"]
    targeted_cov, random_cov, targeted_cut, random_cut, n_bridges = [], [], [], [], []
    for seed, net in sorted(networks.items()):
        edges, regions = net["edges"], net["regions"]
        n_bridges.append(len(between_region_edges(edges, regions)))
        arms = interventions[interventions["network_seed"] == seed]
        top = selected(arms.loc[arms["strategy"] == "betweenness", "selected_tanks"].iloc[0])
        draws = [selected(t) for t in arms.loc[arms["strategy"] == "random", "selected_tanks"].unique()]
        targeted_cov.append(bridge_coverage(edges, regions, top))
        random_cov.append(statistics.mean(bridge_coverage(edges, regions, d) for d in draws))
        targeted_cut.append(removal_disconnects(edges, len(regions), top))
        random_cut.append(statistics.mean(removal_disconnects(edges, len(regions), d) for d in draws))

    # Timing at the focus rate: first crossing relative to the quarantine window [delay, delay + D).
    days = [d for d in crossing.values() if d is not None]
    timing = {}
    for delay in design["response_delays"]:
        start = max(1, delay)
        timing[str(delay)] = {
            "crossed_before_start": sum(d < start for d in days) / len(days),
            "crossed_during_window": sum(start <= d < start + duration for d in days) / len(days),
            "crossed_after_window": sum(d >= start + duration for d in days) / len(days),
        }

    # Were the selected tanks already infected when quarantine started? (state from the shared baseline)
    started = interventions[interventions["intervention_start_day"].notna() & (interventions["transfer_rate"] > 0)]
    already = {}
    for (rate, delay, strategy), runs in started.groupby(["transfer_rate", "response_delay", "strategy"]):
        shares = []
        for row in runs.itertuples():
            raw = baselines[(row.network_seed, row.epidemic_seed, row.transfer_rate)]
            infected = tanks_ever_infected_by(raw, int(row.intervention_start_day) - 1)
            tanks = selected(row.selected_tanks)
            shares.append(sum(t in infected for t in tanks) / len(tanks))
        already.setdefault(f"{rate:g}", {}).setdefault(str(delay), {})[strategy] = statistics.mean(shares)

    result = {
        "design": args.design,
        "quarantine_duration": duration,
        "networks": len(networks),
        "between_region_edges_mean": statistics.mean(n_bridges),
        "bridge_coverage_targeted_mean": statistics.mean(targeted_cov),
        "bridge_coverage_random_mean": statistics.mean(random_cov),
        "disconnects_targeted_share": statistics.mean(targeted_cut),
        "disconnects_random_share": statistics.mean(random_cut),
        "focus_rate": FOCUS_RATE,
        "focus_baselines": len(crossing),
        "never_crossed_share": sum(d is None for d in crossing.values()) / len(crossing),
        "first_cross_day_median": statistics.median(days),
        "first_cross_day_q1": statistics.quantiles(days, n=4)[0],
        "first_cross_day_q3": statistics.quantiles(days, n=4)[2],
        "timing_by_delay": timing,
        "selected_already_infected": already,
    }
    out = ROOT / "results" / "analysis" / args.design / "mechanism.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
