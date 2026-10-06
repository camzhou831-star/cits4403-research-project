"""Apply the pre-registered pilot selection rules (docs/pilot-protocol.md) to recorded pilot results.

Usage:
    python scripts/pilot_select.py stage1    # S1-S6, rules 1-3, D1-D3 -> experiments/config/pilot-stage2-intervention.json
    python scripts/pilot_select.py stage1 --design pilot-stage1-disease-r2   # a rerun on an extended grid (rule 5)
    python scripts/pilot_select.py stage2    # Q1-Q3 -> D; exits 3 if Q1 is unverified (old raw) or no D passes

Reads results/summary/<design>.csv and results/raw/<design>.jsonl, prints every criterion for every
candidate (passing or not) and writes the full tables to results/pilot/ for the pilot report. The script
never compares strategies: Stage 2 criteria pool the intervention runs (pilot-protocol section 1, rule 2).
If the protocol does not decide (no passing candidate, or a rule-2 tie) it stops with exit code 3 instead of
choosing; resolve the gap in decision-log.md, then rerun.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from turtlefarm.analysis import (
    delay_levels,
    evaluate_stage1,
    evaluate_stage2,
    select_duration,
    select_stage1,
    stage2_design,
)
from turtlefarm.runner import ExperimentDesign, iter_raw

STAGE1 = "pilot-stage1-disease"
STAGE2 = "pilot-stage2-intervention"
OUT_DIR = ROOT / "results" / "pilot"


def _summary(name: str) -> pd.DataFrame:
    path = ROOT / "results" / "summary" / f"{name}.csv"
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}: run scripts/run_experiment.py first")
    return pd.read_csv(path)


def stage1(args: argparse.Namespace) -> int:
    summary = _summary(args.design)
    results = evaluate_stage1(summary)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(
        [{"beta": r.beta, "gamma": r.gamma, **r.checks, "passed": r.passed, "s5_triples": r.triples, **r.notes} for r in results]
    )
    table.to_csv(OUT_DIR / f"{args.design}-criteria.csv", index=False)
    print(table[["beta", "gamma", *results[0].checks, "passed"]].to_string(index=False))

    selection = select_stage1(summary, results)
    for note in selection.ambiguities:
        print(f"AMBIGUOUS: {note}", file=sys.stderr)
    if selection.beta is None or selection.ambiguities:
        return 3
    print(f"\nselected beta={selection.beta} gamma={selection.gamma} transfer_rates={selection.transfer_rates}")

    middle = selection.transfer_rates[2]
    delays = delay_levels(iter_raw(ROOT / "results" / "raw" / f"{args.design}.jsonl"), selection.beta, selection.gamma, middle)
    (OUT_DIR / f"{args.design}-delays.json").write_text(json.dumps(delays, indent=2), encoding="utf-8")
    print(f"delay levels: {delays}")
    if not delays["valid"]:
        print(f"STOP: {delays['reason']}", file=sys.stderr)
        return 3

    stage1_design = json.loads((ROOT / "experiments" / "config" / f"{args.design}.json").read_text(encoding="utf-8"))
    design = stage2_design(selection, delays["levels"], stage1_design)
    ExperimentDesign.from_dict(design).configs()  # validate before writing
    out = ROOT / "experiments" / "config" / f"{STAGE2}.json"
    if out.exists() and not args.force:
        raise SystemExit(f"{out.relative_to(ROOT)} exists; pass --force to overwrite")
    out.write_text(json.dumps(design, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}; record the Stage 1 conclusion in decision-log.md before running it")
    return 0


def stage2(args: argparse.Namespace) -> int:
    table = evaluate_stage2(_summary(STAGE2))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_DIR / "stage2-criteria.csv", index=False)
    print(table.to_string(index=False))
    d = select_duration(table)
    if d is None and table["Q1_status"].eq("verified").all():
        print(
            "STOP: no D candidate meets Q1-Q3 with the quarantine-specific counters. Per pilot-protocol "
            "section 4, D=14 remains the completed formal experiment's setting and Q1 is reported as failed.",
            file=sys.stderr,
        )
        return 3
    if d is None:
        print(
            "STOP: no fully verified duration. Q1 is unverified: blocked_transfers mixes capacity and "
            "quarantine blocking over the whole run. Historical proxy results are retained; the existing "
            "formal design (D=14) is unchanged, not revalidated by this command.", file=sys.stderr,
        )
        return 3
    print(f"\nselected quarantine_duration D={d} (budget k x D tank-days)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="stage", required=True)
    p1 = sub.add_parser("stage1")
    p1.add_argument("--design", default=STAGE1, help="Stage 1 design name (default: %(default)s)")
    p1.add_argument("--force", action="store_true", help="overwrite an existing Stage 2 design")
    sub.add_parser("stage2")
    args = parser.parse_args()
    return stage1(args) if args.stage == "stage1" else stage2(args)


if __name__ == "__main__":
    raise SystemExit(main())
