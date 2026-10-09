"""Tables and figures for a recorded formal design (data/methods/experiments.md#outcomes-and-analysis).

Usage:
    python utils/analyse_results.py formal-nested
    python utils/analyse_results.py formal-nested --n-boot 5000

Reads data/results/summary/<design>.csv only and writes everything to data/results/analysis/<design>/, so every number
in the original-study analysis can be regenerated from raw records with two commands. Pilot designs are refused: pilot
data are never used as evidence for the hypothesis (data/methods/experiments.md#pilot-protocol).

Figures 1 and 7 also read data/results/raw/<design>.jsonl: figure 1 draws the network instance stored in the
run records, and figure 7 picks representative runs by the rule in ``pick_representative_runs``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]  # src/: the turtlefarm package; root: utils/

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from utils.network_layout import edges_crossing_nodes, network_layout
from turtlefarm.analysis import (
    PRIMARY_METRICS,
    REPRESENTATIVE_TRANSFER_RATE,
    baseline_differences,
    baseline_effect_table,
    outbreak_class,
    condition_summary,
    paired_differences,
    paired_effect_table,
    pick_representative_runs,
)
from turtlefarm.runner import iter_raw
from turtlefarm.model import STATUS_CENSORED, STATUS_FAILED

STRATEGY_ORDER = ("none", "random", "betweenness")
# Fixed categorical order, validated for CVD separation on a light surface (dataviz reference palette).
CATEGORICAL = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
STRATEGY_COLORS = dict(zip(STRATEGY_ORDER, CATEGORICAL))
SIR_COLORS = {"S": CATEGORICAL[0], "I": CATEGORICAL[1], "R": CATEGORICAL[2]}
INK, MUTED = "#0b0b0b", "#8a8984"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "lines.linewidth": 2})
METRIC_LABELS = {
    "final_attack_rate": "Final attack rate",
    "affected_tanks": "Affected tanks",
    "peak_infected": "Peak infected",
    "time_to_extinction": "Time to extinction (days)",
}


def _error_lengths(mean: pd.Series, low: pd.Series, high: pd.Series) -> list:
    """Error-bar lengths for matplotlib. When every value in a cell is identical, the bootstrap bounds can
    differ from the mean by ~1e-16 in either direction, which matplotlib rejects as a negative length."""
    return [(mean - low).clip(lower=0), (high - mean).clip(lower=0)]


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
                yerr=_error_lengths(sel["mean"], sel["ci95_low"], sel["ci95_high"]),
                marker="o", capsize=3, label=strategy, color=STRATEGY_COLORS[strategy],
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
        for i, (delay, sel) in enumerate(df.groupby("response_delay")):
            sel = sel.sort_values("transfer_rate")
            ax.errorbar(
                sel["transfer_rate"], sel["mean_diff"],
                yerr=_error_lengths(sel["mean_diff"], sel["mean_diff_ci95_low"], sel["mean_diff_ci95_high"]),
                marker="o", capsize=3, label=f"delay {int(delay)} d", color=CATEGORICAL[i],
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


def _raw_baselines(raw_path: Path):
    """No-intervention raw records only; skipping other lines before parsing keeps a large file fast."""
    with raw_path.open(encoding="utf-8") as fh:
        for line in fh:
            if '"strategy":"none"' in line:
                yield json.loads(line)


def plot_network(raw: dict, k: int, path: Path) -> None:
    """Figure 1: one network instance. Colour = region, area = betweenness, black ring = the k tanks the
    highest-betweenness strategy quarantines (pre-outbreak ranking, ties broken by tank id)."""
    net = raw["network"]
    regions, betweenness = net["regions"], net["betweenness"]
    pos = network_layout(net["edges"], regions)
    span = max(max(abs(x), abs(y)) for x, y in pos.values())
    for a, b, tank in edges_crossing_nodes(net["edges"], pos, clearance=0.06 * span):
        print(f"figure 1 warning: edge {a}-{b} passes close to tank {tank}; check the drawing")
    for a in pos:
        for b in pos:
            if a < b and math.dist(pos[a], pos[b]) < 0.12 * span:
                print(f"figure 1 warning: tanks {a} and {b} overlap; check the drawing")
    selected = set(net["ranking"][:k])
    fig, ax = plt.subplots(figsize=(7, 6))
    for a, b in net["edges"]:
        cross = regions[a] != regions[b]
        ax.plot(*zip(pos[a], pos[b]), color=INK if cross else MUTED, lw=1.8 if cross else 0.9,
                alpha=0.9 if cross else 0.6, zorder=1)
    top = max(betweenness) or 1.0
    for tank, (x, y) in pos.items():
        ax.scatter(x, y, s=120 + 900 * betweenness[tank] / top, color=CATEGORICAL[regions[tank] % 4],
                   edgecolors=INK if tank in selected else "#fcfcfb", linewidths=3 if tank in selected else 2, zorder=2)
        ax.annotate(str(tank), (x, y), ha="center", va="center", fontsize=8, color=INK, zorder=3)
    handles = [
        plt.Line2D([], [], marker="o", ls="", markersize=9, color=CATEGORICAL[r % 4], label=f"region {r}")
        for r in sorted(set(regions))
    ]
    ax.legend(handles=handles, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=9)
    ax.set_title(
        f"Network seed {net['network_seed']} (p_in={net['p_in']}, p_out={net['p_out']})\n"
        f"node area = betweenness; black ring = top-{k} tanks {sorted(selected)}; dark edges cross regions",
        fontsize=9,
    )
    ax.margins(0.12)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_representative_runs(picked: dict, path: Path) -> None:
    """Figure 7: S/I/R totals (top) and infected agents per region (bottom) for the representative local and
    cross-region outbreaks. Region lines are labelled directly at their peak."""
    classes = [c for c in ("local", "cross_region") if c in picked]
    fig, axes = plt.subplots(2, len(classes), figsize=(5.5 * len(classes), 6), sharex="col", squeeze=False)
    for col, name in enumerate(classes):
        raw = picked[name]["raw"]
        cfg = raw["config"]
        days = [d["day"] for d in raw["daily"]]
        top, bottom = axes[0][col], axes[1][col]
        for state in ("S", "I", "R"):
            top.plot(days, [d[state] for d in raw["daily"]], color=SIR_COLORS[state], label=state)
        top.set_title(
            f"{name.replace('_', '-')} outbreak (class n={picked[name]['class_size']}, "
            f"median AR={picked[name]['class_median']:.3f})\n"
            f"network {cfg['network_seed']}, epidemic {cfg['epidemic_seed']}, transfer {cfg['transfer_rate']}, "
            f"AR={raw['metrics']['final_attack_rate']:.3f}",
            fontsize=9,
        )
        top.set_ylabel("agents")
        top.legend(frameon=False, fontsize=8)
        regions = sorted({t["region_id"] for t in raw["daily"][0]["tanks"]})
        for region in regions:
            series = [sum(t["I"] for t in d["tanks"] if t["region_id"] == region) for d in raw["daily"]]
            bottom.plot(days, series, color=CATEGORICAL[region % 4])
            peak = max(series)
            if peak > 0:
                bottom.annotate(f"region {region}", (days[series.index(peak)], peak), xytext=(3, 3),
                                textcoords="offset points", fontsize=8, color=INK)
        bottom.set_ylabel("infected agents by region")
        bottom.set_xlabel("day")
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
        raise SystemExit("pilot results are not analysed as evidence (data/methods/experiments.md#pilot-protocol)")

    summary = pd.read_csv(ROOT / "data" / "results" / "summary" / f"{args.design}.csv")
    out = ROOT / "data" / "results" / "analysis" / args.design
    out.mkdir(parents=True, exist_ok=True)

    run_status_table(summary).to_csv(out / "run-status.csv", index=False)
    cond = condition_summary(summary, n_boot=args.n_boot, seed=args.boot_seed)
    cond.to_csv(out / "condition-summary.csv", index=False)
    design_path = ROOT / "data" / "config" / f"{args.design}.json"
    expected_seeds = len(json.loads(design_path.read_text(encoding="utf-8"))["policy_seeds"]) if design_path.exists() else None
    diffs = paired_differences(summary, expected_policy_seeds=expected_seeds)
    diffs.to_csv(out / "paired-differences.csv", index=False)
    effects = paired_effect_table(diffs, n_boot=args.n_boot, seed=args.boot_seed)
    effects.to_csv(out / "paired-effects.csv", index=False)
    base_diffs = baseline_differences(summary, expected_policy_seeds=expected_seeds)
    if base_diffs.attrs["incomplete_blocks"]:
        print(f"WARNING: {base_diffs.attrs['incomplete_blocks']} cells excluded from baseline comparisons as incomplete")
    baseline_effect_table(base_diffs, n_boot=args.n_boot, seed=args.boot_seed).to_csv(
        out / "baseline-effects.csv", index=False
    )
    print(
        f"{len(summary)} runs; {len(diffs)} paired blocks ({diffs.attrs['dropped_blocks']} dropped for failed runs, "
        f"{int(diffs['quarantine_started'].sum())} with quarantine started, "
        f"{diffs.attrs['incomplete_blocks']} incomplete)"
    )
    if diffs.attrs["incomplete_blocks"]:
        print("WARNING: some blocks are missing a targeted run or random policy seeds; check the raw file")

    plot_metric_vs_transfer(cond, "final_attack_rate", out / "fig2-attack-rate.png")
    plot_metric_vs_transfer(cond, "affected_tanks", out / "fig3-affected-tanks.png")
    plot_paired_effects(effects, out / "fig4-paired-effects.png")
    plot_paired_effects(effects, out / "fig4b-paired-effects-quarantine-started.png", subset="quarantine_started")
    plot_distribution(summary, "peak_infected", out / "fig5-peak-infected.png")
    plot_distribution(summary, "time_to_extinction", out / "fig6-time-to-extinction.png")
    raw_path = ROOT / "data" / "results" / "raw" / f"{args.design}.jsonl"
    if raw_path.exists():
        baselines = list(_raw_baselines(raw_path))
        first_network = min(r["config"]["network_seed"] for r in baselines)
        network_raw = next(r for r in baselines if r["config"]["network_seed"] == first_network)
        plot_network(network_raw, network_raw["config"]["k"], out / "fig1-network.png")
        networks = {}
        for r in baselines:
            net = r["network"]
            networks.setdefault(net["network_seed"], {
                "network_seed": net["network_seed"], "attempt": net["attempt"], "network_hash": net["network_hash"],
                "top_k": ",".join(map(str, net["ranking"][: r["config"]["k"]])),
                "top_k_regions": ",".join(str(net["regions"][t]) for t in net["ranking"][: r["config"]["k"]]),
                "tie_groups": len(net["tie_groups"]), **net["metrics"],
            })
        pd.DataFrame(sorted(networks.values(), key=lambda n: n["network_seed"])).to_csv(out / "networks.csv", index=False)
        hidden = [
            (r["config"]["network_seed"], r["config"]["epidemic_seed"], r["config"]["transfer_rate"], outbreak_class(r))
            for r in baselines
            if r["metrics"].get("affected_tanks", 0)
            > len({t["tank_id"] for d in r["daily"] for t in d["tanks"] if t["I"] > 0})
        ]
        (out / "outbreak-class-check.json").write_text(json.dumps({
            "baseline_runs": len(baselines),
            "runs_with_hidden_affected_tanks": len(hidden),
            "of_which_classed_local": [list(h[:3]) for h in hidden if h[3] == "local"],
        }, indent=2), encoding="utf-8")
        if hidden:
            local = [h for h in hidden if h[3] == "local"]
            print(
                f"outbreak_class check: {len(hidden)} baseline runs have affected tanks not visible in daily "
                f"snapshots; {len(local)} of them are classed local and need a manual check: {local}"
            )
        classes = pd.DataFrame(
            [{"transfer_rate": r["config"]["transfer_rate"], "cross_region": outbreak_class(r) == "cross_region"}
             for r in baselines if r["status"] == "completed"]
        )
        classes.groupby("transfer_rate")["cross_region"].agg(["mean", "size"]).rename(
            columns={"mean": "share_cross_region", "size": "runs"}
        ).reset_index().to_csv(out / "outbreak-classes.csv", index=False)
        picked = pick_representative_runs(baselines)
        selection = {
            name: {"network_seed": p["raw"]["config"]["network_seed"], "epidemic_seed": p["raw"]["config"]["epidemic_seed"],
                   "run_id": p["raw"]["run_id"], "final_attack_rate": p["raw"]["metrics"]["final_attack_rate"],
                   "class_size": p["class_size"], "class_median": p["class_median"], "config": p["raw"]["config"]}
            for name, p in picked.items()
        }
        selection["rule"] = (f"no-intervention runs at transfer_rate={REPRESENTATIVE_TRANSFER_RATE}; per outbreak class, "
                             "final attack rate closest to the class median; ties -> smallest (network_seed, epidemic_seed)")
        (out / "fig7-selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
        plot_representative_runs(picked, out / "fig7-representative-runs.png")
    else:
        print(f"no {raw_path.relative_to(ROOT)}: figures 1 and 7 skipped (regenerate the raw file first)")
    print(f"tables and figures -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
