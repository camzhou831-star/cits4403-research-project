"""Live demonstration for Checkpoint 3 and the Week 12 demo: rerun one paired block of the formal experiment.

Runs every arm of one block of `formal-nested` (no intervention, highest-betweenness, and random quarantine
for each policy seed) with the frozen parameters, prints the outcomes and the paired difference, and checks
each run against the stored record in results/summary/formal-nested.csv.

The default block is the representative cross-region outbreak of figure 7 (results/analysis/formal-nested/
fig7-selection.json). That run was picked by a rule on the no-intervention baseline only, so it is not chosen
for how well any strategy did. One block illustrates the mechanism; it is not evidence for the hypotheses.

Usage:
    python scripts/demo_final.py
    python scripts/demo_final.py --delay 1
    python scripts/demo_final.py --network 200 --epidemic 20000 --rate 0.1 --delay 12
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from turtlefarm import SimulationConfig
from turtlefarm.model import run_baseline
from turtlefarm.runner import configuration_hash

DESIGN = ROOT / "experiments" / "config" / "formal-nested.json"
SUMMARY = ROOT / "results" / "summary" / "formal-nested.csv"
SELECTION = ROOT / "results" / "analysis" / "formal-nested" / "fig7-selection.json"


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    default = json.loads(SELECTION.read_text(encoding="utf-8"))["cross_region"]
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--network", type=int, default=default["network_seed"])
    parser.add_argument("--epidemic", type=int, default=default["epidemic_seed"])
    parser.add_argument("--rate", type=float, default=default["config"]["transfer_rate"])
    parser.add_argument("--delay", type=int, default=max(design["response_delays"]), choices=design["response_delays"])
    args = parser.parse_args()

    fixed = design["fixed"]
    common = dict(fixed, design="main", label=design["name"], network_seed=args.network,
                  epidemic_seed=args.epidemic, transfer_rate=args.rate)
    arms = [("none", None)] + [("betweenness", None)] + [("random", s) for s in design["policy_seeds"]]
    stored = pd.read_csv(SUMMARY)

    print(f"Frozen parameters: beta={fixed['beta']}, gamma={fixed['gamma']}, p_in={fixed['p_in']}, "
          f"p_out={fixed['p_out']}, k=2, D={fixed['quarantine_duration']} days (budget {2 * fixed['quarantine_duration']} tank-days)")
    print(f"Block: network {args.network}, epidemic seed {args.epidemic}, transfer rate {args.rate}, "
          f"response delay {args.delay} days\n")

    rows, all_match = [], True
    for strategy, policy_seed in arms:
        if strategy == "none":
            cfg = SimulationConfig(**{**common, "strategy": "none", "quarantine_duration": 0})
        else:
            cfg = SimulationConfig(**common, strategy=strategy, response_delay=args.delay, policy_seed=policy_seed)
        record = run_baseline(cfg)
        m = record.metrics
        blocked = sum(d.blocked_transfers for d in record.daily)
        match = stored[stored["configuration_hash"] == configuration_hash(cfg.to_dict())]
        same = len(match) == 1 and all(
            match.iloc[0][key] == m[key] for key in ("final_attack_rate", "affected_tanks", "peak_infected")
        )
        all_match &= same
        rows.append({
            "strategy": strategy, "policy seed": "-" if policy_seed is None else policy_seed,
            "quarantined tanks": ",".join(map(str, record.selected_tanks)) or "-",
            "start day": "-" if record.intervention_start_day is None else record.intervention_start_day,
            "attack rate": f"{m['final_attack_rate']:.3f}", "affected tanks": m["affected_tanks"],
            "blocked transfers": blocked, "days": m["days_simulated"],
            "= stored record": "yes" if same else "NO",
        })
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))

    ar = {r["strategy"] + str(r["policy seed"]): float(r["attack rate"]) for r in rows}
    random_mean = sum(ar[f"random{s}"] for s in design["policy_seeds"]) / len(design["policy_seeds"])
    print(f"\nPaired difference in this block (targeted - mean of random): "
          f"{ar['betweenness-'] - random_mean:+.3f} attack rate")
    print("Every arm saw the same random draws until the quarantine started (event-keyed draws),")
    print("so the difference comes from which tanks were closed. One block is an illustration, not a result.")
    print(f"\nAll runs identical to results/summary/{SUMMARY.stem}.csv: {'yes' if all_match else 'NO'}")
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
