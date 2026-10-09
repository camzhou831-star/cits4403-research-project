"""Run one experiment design and append raw run records (data/methods/result-schema.md).

Usage:
    python utils/run_experiment.py data/config/<design>.json
    python utils/run_experiment.py data/config/<design>.json --resume
    python utils/run_experiment.py data/config/<design>.json --dry-run

Raw records go to data/results/raw/<design name>.jsonl (git-ignored, append-only, never edited by hand) and a
flat per-run table to data/results/summary/<design name>.csv. The table is regenerated from the raw file on
every invocation, so it is always reproducible from the raw records.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]  # src/: the turtlefarm package; root: utils/

import pandas as pd

from turtlefarm.runner import BatchHalted, ExperimentDesign, flatten, iter_raw, run_design


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("design", type=Path, help="design JSON under data/config/")
    parser.add_argument("--resume", action="store_true", help="continue an existing raw file, skipping recorded runs")
    parser.add_argument("--dry-run", action="store_true", help="validate the design and print the run count only")
    args = parser.parse_args()

    design = ExperimentDesign.from_json(args.design)
    configs = design.configs()
    blocks = len(design.seed_pairs()) * len(design.transfer_rates)
    print(f"design {design.name!r}: {len(configs)} runs in {blocks} paired blocks")
    if args.dry_run:
        return 0

    raw_path = ROOT / "data" / "results" / "raw" / f"{design.name}.jsonl"
    summary_path = ROOT / "data" / "results" / "summary" / f"{design.name}.csv"

    def progress(done: int, total: int, raw: dict) -> None:
        if done % 50 == 0 or done == total:
            print(f"  {done}/{total}  last status={raw['status']}", flush=True)

    started = time.perf_counter()
    halted = None
    try:
        counts = run_design(design, raw_path, resume=args.resume, progress=progress)
        print(f"written={counts['written']} skipped={counts['skipped']} failed={counts['failed']}")
    except FileExistsError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    except BatchHalted as exc:
        halted = exc
        print(f"BATCH HALTED: {exc}", file=sys.stderr)
    print(f"elapsed {time.perf_counter() - started:.1f} s -> {raw_path.relative_to(ROOT)}")

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([flatten(raw) for raw in iter_raw(raw_path)]).to_csv(summary_path, index=False)
    print(f"summary -> {summary_path.relative_to(ROOT)}")
    return 1 if halted else 0


if __name__ == "__main__":
    raise SystemExit(main())
