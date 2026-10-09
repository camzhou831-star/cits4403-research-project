"""Run the separate duration/policy sensitivity design without rewriting formal data."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from turtlefarm.followup import FollowupDesign, run_followup
from turtlefarm.runner import BatchHalted, iter_raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "results",
                        help="use a separate directory to reproduce without replacing committed results")
    args = parser.parse_args()
    design = FollowupDesign.from_json(args.design)
    print(f"{design.name}: {len(design.configs()):,} planned runs; protocol {design.protocol_hash}")
    if args.dry_run:
        return 0
    raw_path = args.output_dir / "raw" / f"{design.name}.jsonl"
    summary_path = args.output_dir / "summary" / f"{design.name}.csv"

    def progress(done: int, total: int, row: dict) -> None:
        if done % 250 == 0 or done == total:
            print(f"{done}/{total}; status={row['status']}; elapsed={time.perf_counter() - started:.1f}s", flush=True)

    started = time.perf_counter()
    halted = False
    try:
        counts = run_followup(design, raw_path, resume=args.resume, workers=args.workers, progress=progress)
        print(counts)
    except BatchHalted as exc:
        print(f"Batch halted: {exc}", file=sys.stderr)
        halted = True
    except (FileExistsError, ValueError) as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        return 2
    if raw_path.exists():
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([record["summary"] for record in iter_raw(raw_path)]).to_csv(summary_path, index=False)
        print(f"Summary: {summary_path}")
    return 1 if halted else 0


if __name__ == "__main__":
    raise SystemExit(main())
