"""Render report/report.md from report/report.template.md and the committed result files.

Usage:
    python scripts/build_report.py            # writes report/report.md
    python scripts/build_report.py --keys     # lists every available placeholder with its value

Every number in the report comes from results/ through a named placeholder ``{{name}}``; tables are
``{{table:name}}``. An unknown placeholder is an error, so a typo can never leave a hand-typed number behind.
The raw JSONL files are not needed: everything is read from results/summary, results/pilot and
results/analysis, which are committed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

FORMAL = "formal-nested"
CROSSED = "formal"
PILOTS = ("pilot-stage1-disease", "pilot-stage1-disease-r2", "pilot-stage2-intervention")
ANALYSIS = ROOT / "results" / "analysis"
METRIC_NAMES = {"final_attack_rate": "Final attack rate", "affected_tanks": "Affected tanks"}


def f2(x: float) -> str:
    return f"{x:.2f}"


def f3(x: float) -> str:
    return f"{x:.3f}"


def pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def ci(lo: float, hi: float, fmt=f3) -> str:
    return f"[{fmt(lo)}, {fmt(hi)}]"


def rate_key(rate: float) -> str:
    return f"{rate:g}".replace(".", "p")


def excludes_zero(lo: float, hi: float) -> bool:
    return lo > 0 or hi < 0


def collect() -> tuple[dict[str, str], dict[str, str]]:
    v: dict[str, str] = {}
    tables: dict[str, str] = {}

    # ---- design and frozen parameters
    design = json.loads((ROOT / "experiments" / "config" / f"{FORMAL}.json").read_text(encoding="utf-8"))
    fixed = design["fixed"]
    v.update(
        beta=f"{fixed['beta']:g}", gamma=f"{fixed['gamma']:g}", p_in=f"{fixed['p_in']:g}", p_out=f"{fixed['p_out']:g}",
        D=str(fixed["quarantine_duration"]),
        transfer_levels=", ".join(f"{r:g}" for r in design["transfer_rates"]),
        delay_levels=", ".join(str(d) for d in design["response_delays"]),
        n_networks=str(len(design["network_seeds"])),
        n_epidemic=str(len(design["epidemic_seeds"])),
        epi_per_network=str(len(design["epidemic_seeds"]) // len(design["network_seeds"])),
        n_policy=str(len(design["policy_seeds"])),
        network_seed_range=f"{min(design['network_seeds'])}-{max(design['network_seeds'])}",
        epidemic_seed_range=f"{min(design['epidemic_seeds'])}-{max(design['epidemic_seeds'])}",
        policy_seed_range=f"{min(design['policy_seeds'])}-{max(design['policy_seeds'])}",
        runs_per_block=str(1 + len(design["response_delays"]) * (1 + len(design["policy_seeds"]))),
    )
    v["mean_infectious_days"] = f"{1 / fixed['gamma']:g}"
    v["budget"] = str(2 * fixed["quarantine_duration"])

    # ---- pilot
    for name in PILOTS:
        s = pd.read_csv(ROOT / "results" / "summary" / f"{name}.csv")
        key = {"pilot-stage1-disease": "pilot1", "pilot-stage1-disease-r2": "pilot2", "pilot-stage2-intervention": "pilot3"}[name]
        v[f"{key}_runs"] = f"{len(s):,}"
        v[f"{key}_failed"] = str(int((s["status"] == "failed").sum()))
        v[f"{key}_censored"] = str(int((s["status"] == "censored_max_days").sum()))
    c1 = pd.read_csv(ROOT / "results" / "pilot" / "pilot-stage1-disease-criteria.csv")
    c2 = pd.read_csv(ROOT / "results" / "pilot" / "pilot-stage1-disease-r2-criteria.csv")
    v["pilot1_candidates"] = str(len(c1))
    v["pilot1_passed"] = str(int(c1["passed"].sum()))
    v["pilot2_passed"] = str(int(c2["passed"].sum()))
    st2 = pd.read_csv(ROOT / "results" / "pilot" / "stage2-criteria.csv").set_index("quarantine_duration")
    d = int(fixed["quarantine_duration"])
    v["pilot_q1_all"] = pct(st2.loc[d, "share_blocked_ge_1_all_runs"])
    v["pilot_q1_started"] = pct(st2.loc[d, "share_blocked_ge_1_started"])
    v["pilot_extinction_median"] = f"{st2.loc[d, 'baseline_extinction_median']:g}"
    v["pilot_q2_limit"] = f"{0.25 * st2.loc[d, 'baseline_extinction_median']:g}"
    delays = json.loads((ROOT / "results" / "pilot" / "pilot-stage1-disease-r2-delays.json").read_text(encoding="utf-8"))
    v["pilot_nonminor_runs"] = str(delays["non_minor_runs"])

    # ---- networks of the formal design
    nets = pd.read_csv(ANALYSIS / FORMAL / "networks.csv")
    for col in ("modularity", "n_inter_edges", "mean_degree", "diameter", "clustering"):
        v[f"net_{col}_median"] = f"{nets[col].median():g}" if col in ("n_inter_edges", "diameter") else f2(nets[col].median())
        v[f"net_{col}_min"] = f"{nets[col].min():g}" if col in ("n_inter_edges", "diameter") else f2(nets[col].min())
        v[f"net_{col}_max"] = f"{nets[col].max():g}" if col in ("n_inter_edges", "diameter") else f2(nets[col].max())
    v["net_resampled"] = str(int((nets["attempt"] > 0).sum()))
    same_region = nets["top_k_regions"].astype(str).str.split(",").map(lambda r: len(set(r)) == 1)
    v["net_topk_same_region"] = str(int(same_region.sum()))
    v["fig1_network_seed"] = str(int(nets["network_seed"].min()))
    v["fig1_top_k"] = nets.loc[nets["network_seed"].idxmin(), "top_k"].replace(",", " and ")

    # ---- tests
    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True
    ).stdout
    match = re.search(r"(\d+) tests? collected", collected)
    v["n_tests"] = match.group(1) if match else "?"

    # ---- formal run status
    s = pd.read_csv(ROOT / "results" / "summary" / f"{FORMAL}.csv")
    v["formal_runs"] = f"{len(s):,}"
    v["formal_completed"] = f"{int((s['status'] == 'completed').sum()):,}"
    v["formal_failed"] = str(int((s["status"] == "failed").sum()))
    v["formal_censored"] = str(int((s["status"] == "censored_max_days").sum()))
    v["formal_blocks"] = str(len(s[s["strategy"] == "none"]))
    v["formal_blocks_per_rate"] = str(len(s[(s["strategy"] == "none") & (s["transfer_rate"] == 0)]))

    # ---- baseline (no intervention) by transfer rate
    cond = pd.read_csv(ANALYSIS / FORMAL / "condition-summary.csv")
    base = cond[cond["strategy"] == "none"]
    rows = []
    for rate in sorted(base["transfer_rate"].unique()):
        r = base[base["transfer_rate"] == rate].set_index("metric")
        k = rate_key(rate)
        for m in ("final_attack_rate", "affected_tanks", "peak_infected", "time_to_extinction"):
            v[f"base_{m}_{k}"] = f3(r.loc[m, "mean"]) if m == "final_attack_rate" else f2(r.loc[m, "mean"])
            v[f"base_{m}_{k}_median"] = f"{r.loc[m, 'median']:g}"
        rows.append(
            f"| {rate:g} | {f3(r.loc['final_attack_rate', 'mean'])} {ci(r.loc['final_attack_rate', 'ci95_low'], r.loc['final_attack_rate', 'ci95_high'])} "
            f"| {f2(r.loc['affected_tanks', 'mean'])} {ci(r.loc['affected_tanks', 'ci95_low'], r.loc['affected_tanks', 'ci95_high'], f2)} "
            f"| {f2(r.loc['peak_infected', 'mean'])} | {r.loc['time_to_extinction', 'median']:g} |"
        )
    tables["baseline"] = "\n".join(
        [
            "| Transfer rate | Final attack rate, mean [95% CI] | Affected tanks, mean [95% CI] | Peak infected, mean | Time to extinction, median (days) |",
            "|---|---|---|---|---|",
            *rows,
        ]
    )

    # ---- strategy vs baseline
    be = pd.read_csv(ANALYSIS / FORMAL / "baseline-effects.csv")
    rows = []
    for (rate, delay), g in be[be["transfer_rate"] > 0].groupby(["transfer_rate", "response_delay"], sort=True):
        cells = []
        for strategy in ("random", "betweenness"):
            for m in ("final_attack_rate", "affected_tanks"):
                r = g[(g["strategy"] == strategy) & (g["metric"] == m)].iloc[0]
                key = f"vsbase_{strategy}_{m}_{rate_key(rate)}_d{int(delay)}"
                v[key] = pct(r["rel_reduction"])
                v[key + "_ci"] = ci(r["rel_reduction_ci95_low"], r["rel_reduction_ci95_high"], pct)
                v[key + "_diff"] = f3(r["mean_diff"]) if m == "final_attack_rate" else f2(r["mean_diff"])
                if m == "final_attack_rate":
                    mark = "" if excludes_zero(r["mean_diff_ci95_low"], r["mean_diff_ci95_high"]) else "†"
                    cells.append(f"{pct(r['rel_reduction'])} {ci(r['rel_reduction_ci95_low'], r['rel_reduction_ci95_high'], pct)}{mark}")
        rows.append(f"| {rate:g} | {int(delay)} | " + " | ".join(cells) + " |")
    tables["vs_baseline"] = "\n".join(
        [
            "| Transfer rate | Delay (days) | Random: reduction in attack rate [95% CI] | Betweenness: reduction in attack rate [95% CI] |",
            "|---|---|---|---|",
            *rows,
        ]
    )

    # ---- targeted vs random (all blocks and quarantine-started blocks)
    pe = pd.read_csv(ANALYSIS / FORMAL / "paired-effects.csv")
    rows = []
    n_cells = n_excl = 0
    for (rate, delay), g in pe[(pe["subset"] == "all_blocks") & (pe["transfer_rate"] > 0)].groupby(
        ["transfer_rate", "response_delay"], sort=True
    ):
        cells = []
        for m in ("final_attack_rate", "affected_tanks"):
            r = g[g["metric"] == m].iloc[0]
            key = f"tvr_{m}_{rate_key(rate)}_d{int(delay)}"
            fmt = f3 if m == "final_attack_rate" else f2
            v[key] = fmt(r["mean_diff"])
            v[key + "_ci"] = ci(r["mean_diff_ci95_low"], r["mean_diff_ci95_high"], fmt)
            v[key + "_rel"] = pct(r["rel_reduction"])
            v[key + "_rel_ci"] = ci(r["rel_reduction_ci95_low"], r["rel_reduction_ci95_high"], pct)
            v[key + "_share"] = pct(r["share_targeted_better"], 0)
            excl = excludes_zero(r["mean_diff_ci95_low"], r["mean_diff_ci95_high"])
            n_cells += 1
            n_excl += excl
            cells.append(f"{fmt(r['mean_diff'])} {ci(r['mean_diff_ci95_low'], r['mean_diff_ci95_high'], fmt)}{'' if excl else '†'}")
            cells.append(f"{pct(r['rel_reduction'])}")
        rows.append(f"| {rate:g} | {int(delay)} | " + " | ".join(cells) + " |")
    tables["targeted_vs_random"] = "\n".join(
        [
            "| Transfer rate | Delay (days) | Attack rate: targeted − random [95% CI] | Relative reduction | Affected tanks: targeted − random [95% CI] | Relative reduction |",
            "|---|---|---|---|---|---|",
            *rows,
        ]
    )
    v["tvr_cells"] = str(n_cells)
    v["tvr_cells_excluding_zero"] = str(n_excl)

    pdiff = pd.read_csv(ANALYSIS / FORMAL / "paired-differences.csv")
    for (rate, delay), g in pdiff[pdiff["transfer_rate"] > 0].groupby(["transfer_rate", "response_delay"]):
        key = f"tvr_final_attack_rate_{rate_key(rate)}_d{int(delay)}"
        v[key + "_equal"] = pct((g["diff_final_attack_rate"] == 0).mean(), 0)
        v[key + "_worse"] = pct((g["diff_final_attack_rate"] > 0).mean(), 0)
    started = pdiff.copy()
    started = started[started["transfer_rate"] > 0]
    for delay, g in started.groupby("response_delay"):
        v[f"not_started_d{int(delay)}"] = pct(1 - g["quarantine_started"].mean())
    ps = pe[(pe["subset"] == "quarantine_started")]
    r = ps[(ps["transfer_rate"] == 0.025) & (ps["response_delay"] == 33) & (ps["metric"] == "final_attack_rate")].iloc[0]
    v["tvr_started_ar_0p025_d33"] = f3(r["mean_diff"])
    v["tvr_started_ar_0p025_d33_ci"] = ci(r["mean_diff_ci95_low"], r["mean_diff_ci95_high"])
    v["tvr_started_ar_0p025_d33_blocks"] = str(int(r["blocks"]))

    # ---- crossed-seed run (disclosure)
    pc = pd.read_csv(ANALYSIS / CROSSED / "paired-effects.csv")
    pc = pc[(pc["subset"] == "all_blocks") & (pc["transfer_rate"] > 0)]
    v["crossed_cells_excluding_zero"] = str(int(sum(excludes_zero(a, b) for a, b in zip(pc["mean_diff_ci95_low"], pc["mean_diff_ci95_high"]))))
    v["crossed_epidemic_seeds"] = str(pd.read_csv(ROOT / "results" / "summary" / f"{CROSSED}.csv")["epidemic_seed"].nunique())

    # ---- representative runs
    sel = json.loads((ANALYSIS / FORMAL / "fig7-selection.json").read_text(encoding="utf-8"))
    for name in ("local", "cross_region"):
        p = sel[name]
        v[f"fig7_{name}_network"] = str(p["network_seed"])
        v[f"fig7_{name}_epidemic"] = str(p["epidemic_seed"])
        v[f"fig7_{name}_ar"] = f2(p["final_attack_rate"])
        v[f"fig7_{name}_n"] = str(p["class_size"])
    v["fig7_rate"] = f"{sel['local']['config']['transfer_rate']:g}"
    v["local_share_0p025"] = pct(sel["local"]["class_size"] / (sel["local"]["class_size"] + sel["cross_region"]["class_size"]), 0)

    v["figdir"] = f"../results/analysis/{FORMAL}"
    return v, tables


def render(template: str, values: dict[str, str], tables: dict[str, str]) -> str:
    unknown = []

    def sub(match: re.Match) -> str:
        key = match.group(1).strip()
        if key.startswith("table:"):
            name = key[len("table:"):]
            if name in tables:
                return tables[name]
        elif key in values:
            return values[key]
        unknown.append(key)
        return match.group(0)

    out = re.sub(r"\{\{([^}]+)\}\}", sub, template)
    if unknown:
        raise SystemExit(f"unknown placeholders: {sorted(set(unknown))}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keys", action="store_true", help="list placeholders and values")
    args = parser.parse_args()
    values, tables = collect()
    if args.keys:
        for k in sorted(values):
            print(f"{k} = {values[k]}")
        print("tables:", ", ".join(sorted(tables)))
        return 0
    template = (ROOT / "report" / "report.template.md").read_text(encoding="utf-8")
    header = "<!-- GENERATED by scripts/build_report.py from report/report.template.md; edit the template, not this file. -->\n\n"
    (ROOT / "report" / "report.md").write_text(header + render(template, values, tables), encoding="utf-8")
    print("wrote report/report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
