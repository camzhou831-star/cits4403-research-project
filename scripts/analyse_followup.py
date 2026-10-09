"""Analyse existing formal/follow-up CSVs; does not execute simulations or change source datasets.

Usage: python scripts/analyse_followup.py --boot-seed 20261009
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from turtlefarm.followup_analysis import PRIMARY, analyse_followup, formal_delay_effects, verify_formal_replay
from turtlefarm.runner import configuration_hash


def plot_strategy_effects(effects: pd.DataFrame, path: Path) -> None:
    """One compact figure: within-duration targeted-minus-random effects, pointwise intervals."""
    fig, axes = plt.subplots(2, 3, figsize=(10.8, 6.6), sharex=True, sharey="row", squeeze=False,
                             layout="constrained")
    for row, metric in enumerate(PRIMARY):
        for col, duration in enumerate((7, 14, 28)):
            ax = axes[row, col]
            values = effects[(effects["metric"] == metric) & (effects["quarantine_duration"] == duration)]
            values = values.sort_values("response_delay")
            scale = 100 if metric == "final_attack_rate" else 1
            mean = values["mean_diff"].to_numpy() * scale
            errors = np.maximum(0, np.array([mean - values["ci95_low"] * scale,
                                            values["ci95_high"] * scale - mean]))
            ax.errorbar(values["response_delay"], mean, yerr=errors, marker="o", capsize=4, color="#23628c")
            ax.axhline(0, color="0.5", linewidth=0.8)
            ax.set_xticks((1, 12, 33))
            if row == 0:
                ax.set_title(f"Duration {duration} days\n{2 * duration} tank-days if activated", fontsize=10)
            else:
                ax.set_xlabel("Response delay (days)")
        axes[row, 0].set_ylabel(("Attack-rate difference (percentage points)" if metric == "final_attack_rate" else "Affected-tank difference")
                               + "\n(targeted − random)")
    fig.suptitle("Follow-up at transfer rate 0.025: negative favours targeting\n"
                 "Pointwise 95% network-cluster intervals; no multiplicity adjustment", fontsize=11)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def source_receipt(path: Path) -> dict:
    """Portable repository paths and exact bytes, including not-yet-committed analysis files."""
    path = path.resolve()
    try:
        display = path.relative_to(ROOT).as_posix()
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def analysis_code_receipt() -> dict:
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                  capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        revision = None
    return {
        "repository_head": revision,
        "revision_scope": "HEAD context only; file SHA256 values identify the analysed working-tree code",
        "files": [source_receipt(Path(__file__)), source_receipt(ROOT / "src/turtlefarm/followup_analysis.py")],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal", type=Path, default=ROOT / "results/summary/formal-nested.csv")
    parser.add_argument("--followup", type=Path, default=ROOT / "results/summary/followup-duration-policy.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results/analysis/followup-duration-policy")
    parser.add_argument("--design", type=Path, default=ROOT / "experiments/config/followup-duration-policy.json")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--boot-seed", type=int, default=20261009)
    args = parser.parse_args(argv)
    inputs = {"formal": args.formal.resolve(), "followup": args.followup.resolve()}
    output = args.output.resolve()
    if any(path.parent == output or path == output for path in inputs.values()):
        parser.error("analysis output must be separate from source summary files")
    formal, followup = (pd.read_csv(inputs[name]) for name in ("formal", "followup"))
    # Validate and compute everything before creating outputs: invalid input cannot leave partial tables.
    design = json.loads(args.design.read_text(encoding="utf-8"))
    protocol_hash = configuration_hash(design)
    tables = analyse_followup(followup, n_boot=args.n_boot, seed=args.boot_seed, expected_protocol_hash=protocol_hash)
    tables["formal-delay-effects"] = formal_delay_effects(formal, n_boot=args.n_boot, seed=args.boot_seed)
    replay = verify_formal_replay(formal, followup)
    metadata = {
        "analysis": "duration-policy follow-up; separate from the original formal experiment",
        "sources": {name: source_receipt(path) for name, path in inputs.items()},
        "analysis_code": analysis_code_receipt(),
        "source_code_commits": {name: sorted(frame["code_commit"].dropna().astype(str).unique().tolist())
                                for name, frame in (("formal", formal), ("followup", followup))
                                if "code_commit" in frame},
        "bootstrap": {"unit": "network_seed", "resamples": args.n_boot, "seed": args.boot_seed,
                      "interval": "pointwise percentile 95%", "multiplicity_adjustment": "none"},
        "validation": {"passed": True, "checks": ["exact planned run keys", "unique complete runs",
                        "fixed disease/capacity/k", "matched network hashes", "nested epidemic seeds",
                        "policy seed schedules and consistent selected pairs", "valid outcome domains"]},
        "formal_capacity": "12: fixed historical design; original CSV omits this column",
        "protocol": {**source_receipt(args.design), "configuration_hash": protocol_hash},
        "formal_replay": replay,
        "selection": "all matched blocks; no intervention-started or observed-event selection for contrasts",
        "event_times": "conditional on an event; non-events remain missing, with separate incidence indicators",
        "policy_mcse": "conditional on recorded networks and epidemics; computed from policy-level epidemic means",
        "duration_caveat": "k=2; increasing duration increases committed tank-day budget; no pure timing attribution",
        "tests": {"command": "python -m pytest tests/test_followup_analysis.py",
                  "execution": "not run by this analysis script; record test execution separately"},
        "tables": {name: {"rows": len(table), "columns": list(table.columns)} for name, table in tables.items()},
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
    plot_strategy_effects(tables["strategy-effects"], output / "fig-strategy-effects.png")
    (output / "analysis-summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(formal)} formal and {len(followup)} follow-up runs; analysis -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
