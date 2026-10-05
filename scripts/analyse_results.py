"""Tables and figures for a recorded formal design (experiment-plan sections 12 and 14).

Usage:
    python scripts/analyse_results.py formal
    python scripts/analyse_results.py formal --n-boot 5000

Reads results/summary/<design>.csv only and writes everything to results/analysis/<design>/, so every number
in the report can be regenerated from the raw records with two commands. Pilot designs are refused: pilot
data are never used as evidence for the hypothesis (pilot-protocol section 1).

Status: skeleton. Figures 2-6 are drafted; figure 1 (network diagram) and figure 7 (representative runs,
chosen by an objective rule) are still TODO.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from turtlefarm.analysis import PRIMARY_METRICS, condition_summary, paired_differences, paired_effect_table
from turtlefarm.model import STATUS_CENSORED, STATUS_FAILED

STRATEGY_ORDER = ("none", "random", "betweenness")
METRIC_LABELS = {
    "final_attack_rate": "Final attack rate",
    "affected_tanks": "Affected tanks",
    "peak_infected": "Peak infected",
    "time_to_extinction": "Time to extinction (days)",
}


def run_status_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Completed / censored / failed counts per condition; reported, never filtered silently (section 11)."""
    return (
        summary.groupby(["transfer_rate", "response_delay", "strategy", "status"], dropna=False)
        .size()
        .unstack("status", fill_value=0)
        .reset_index()
    )


def plot_metric_vs_transfer(cond: pd.DataFrame, metric: str, path: Path) -> None:
    """Figures 2 and 3: metric vs transfer rate by strategy, one panel per response delay, mean with 95% CI.
    The shared baseline is drawn identically in every panel (D007)."""
    df = cond[cond["metric"] == metric]
    delays = sorted(df["response_delay"].dropna().unique())
    fig, axes = plt.subplots(1, len(delays), figsize=(4 * len(delays), 3.4), sharey=True, squeeze=False)
    for ax, delay in zip(axes[0], delays):
        for strategy in STRATEGY_ORDER:
            sel = df[df["strategy"] == strategy]
            if strategy != "none":
                sel = sel[sel["response_delay"] == delay]
            sel = sel.sort_values("transfer_rate")
            ax.errorbar(
                sel["transfer_rate"], sel["mean"],
                yerr=[sel["mean"] - sel["ci95_low"], sel["ci95_high"] - sel["mean"]],
                marker="o", capsize=3, label=strategy,
            )
        ax.set_title(f"response delay = {int(delay)} d")
        ax.set_xlabel("transfer rate")
    axes[0][0].set_ylabel(METRIC_LABELS[metric])
    axes[0][-1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_paired_effects(effects: pd.DataFrame, path: Path, subset: str = "all_blocks") -> None:
    """Figure 4: mean targeted-minus-random difference with network-cluster bootstrap CI.
    Negative = highest-betweenness quarantine did better in that cell."""
    fig, axes = plt.subplots(1, len(PRIMARY_METRICS), figsize=(5 * len(PRIMARY_METRICS), 3.4), squeeze=False)
    for ax, metric in zip(axes[0], PRIMARY_METRICS):
        df = effects[(effects["metric"] == metric) & (effects["subset"] == subset)]
        for delay, sel in df.groupby("response_delay"):
            sel = sel.sort_values("transfer_rate")
            ax.errorbar(
                sel["transfer_rate"], sel["mean_diff"],
                yerr=[sel["mean_diff"] - sel["mean_diff_ci95_low"], sel["mean_diff_ci95_high"] - sel["mean_diff"]],
                marker="o", capsize=3, label=f"delay {int(delay)} d",
            )
        ax.axhline(0, color="grey", lw=0.8)
        ax.set_title(f"{METRIC_LABELS[metric]}: targeted - random")
        ax.set_xlabel("transfer rate")
    axes[0][-1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_distribution(summary: pd.DataFrame, metric: str, path: Path) -> None:
    """Figures 5 and 6: per-strategy distribution, pooled over delays, one box per transfer rate."""
    df = summary[summary["status"] != STATUS_FAILED]
    rates = sorted(df["transfer_rate"].unique())
    fig, axes = plt.subplots(1, len(rates), figsize=(3.2 * len(rates), 3.4), sharey=True, squeeze=False)
    for ax, rate in zip(axes[0], rates):
        sel = df[df["transfer_rate"] == rate]
        data = [sel.loc[sel["strategy"] == s, metric].dropna() for s in STRATEGY_ORDER]
        ax.boxplot(data, tick_labels=STRATEGY_ORDER)
        ax.set_title(f"transfer rate = {rate}")
    axes[0][0].set_ylabel(METRIC_LABELS[metric])
    if metric == "time_to_extinction":
        censored = int((df["status"] == STATUS_CENSORED).sum())
        fig.suptitle(f"completed runs only; {censored} censored runs reported separately", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("design", help="design name, e.g. formal")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--boot-seed", type=int, default=0)
    args = parser.parse_args()
    if args.design.startswith("pilot"):
        raise SystemExit("pilot results are not analysed as evidence (pilot-protocol section 1)")

    summary = pd.read_csv(ROOT / "results" / "summary" / f"{args.design}.csv")
    out = ROOT / "results" / "analysis" / args.design
    out.mkdir(parents=True, exist_ok=True)

    run_status_table(summary).to_csv(out / "run-status.csv", index=False)
    cond = condition_summary(summary)
    cond.to_csv(out / "condition-summary.csv", index=False)
    diffs = paired_differences(summary)
    diffs.to_csv(out / "paired-differences.csv", index=False)
    effects = paired_effect_table(diffs, n_boot=args.n_boot, seed=args.boot_seed)
    effects.to_csv(out / "paired-effects.csv", index=False)
    print(
        f"{len(summary)} runs; {len(diffs)} paired blocks ({diffs.attrs['dropped_blocks']} dropped for failed runs, "
        f"{int(diffs['quarantine_started'].sum())} with quarantine started)"
    )

    plot_metric_vs_transfer(cond, "final_attack_rate", out / "fig2-attack-rate.png")
    plot_metric_vs_transfer(cond, "affected_tanks", out / "fig3-affected-tanks.png")
    plot_paired_effects(effects, out / "fig4-paired-effects.png")
    plot_paired_effects(effects, out / "fig4b-paired-effects-quarantine-started.png", subset="quarantine_started")
    plot_distribution(summary, "peak_infected", out / "fig5-peak-infected.png")
    plot_distribution(summary, "time_to_extinction", out / "fig6-time-to-extinction.png")
    # TODO fig1: modular network, colour = region, size = betweenness (turtlefarm.network)
    # TODO fig7: S/I/R time series of one local and one cross-group outbreak, picked by a rule fixed in advance
    print(f"tables and figures -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
