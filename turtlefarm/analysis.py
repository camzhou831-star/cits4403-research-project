"""Pilot selection rules and formal paired analysis (docs/pilot-protocol.md; experiment-plan sections 6, 12).

Every function here reads the per-run summary table written by ``scripts/run_experiment.py`` (one row per
run, ``turtlefarm.runner.flatten``) and, where a criterion needs a daily trajectory, the raw JSONL. Nothing
re-runs the model.

The pilot functions only encode the criteria written in ``pilot-protocol.md`` before any pilot data was
seen. Where the protocol leaves a choice open, the function reports the ambiguity instead of resolving it
silently (pilot-protocol section 1, rule 5).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np
import pandas as pd

from turtlefarm.model import STATUS_CENSORED, STATUS_COMPLETED, STATUS_FAILED

MINOR_OUTBREAK_MAX_ATTACK_RATE = 0.06  # pilot-protocol section 3: infection never really left the first tank
CANDIDATE_KEYS = ("beta", "gamma")
BLOCK_KEYS = ("network_seed", "epidemic_seed", "transfer_rate")
PRIMARY_METRICS = ("final_attack_rate", "affected_tanks")
# Paired differences are means of up to three runs, so identical outcomes can differ by ~1e-17 in floating
# point. Anything within this tolerance counts as a tie.
DIFF_TOLERANCE = 1e-9
SECONDARY_METRICS = ("peak_infected", "time_to_extinction")


# --------------------------------------------------------------------------------------------------
# Stage 1: disease regime and transfer-rate levels (pilot-protocol section 3)
# --------------------------------------------------------------------------------------------------


@dataclass
class CandidateResult:
    beta: float
    gamma: float
    checks: dict[str, bool]
    notes: dict[str, Any]
    triples: list[tuple[float, float, float]] = field(default_factory=list)  # S5-qualifying level triples

    @property
    def passed(self) -> bool:
        return all(self.checks.values())


def _nonzero_levels(df: pd.DataFrame) -> list[float]:
    return sorted(level for level in df["transfer_rate"].unique() if level > 0)


def _s5_triples(df: pd.DataFrame) -> list[tuple[float, float, float]]:
    """Ordered non-zero level triples whose median affected tanks strictly increase and whose adjacent mean
    accepted-transfers-per-day differ by at least a factor of 2 (criterion S5)."""
    by_level = df[df["transfer_rate"] > 0].groupby("transfer_rate")
    median_tanks = by_level["affected_tanks"].median()
    per_day = (df["accepted_transfers"] / df["days_simulated"].clip(lower=1)).groupby(df["transfer_rate"]).mean()
    triples = []
    for a, b, c in itertools.combinations(_nonzero_levels(df), 3):
        if not median_tanks[a] < median_tanks[b] < median_tanks[c]:
            continue
        if per_day[a] > 0 and per_day[b] >= 2 * per_day[a] and per_day[c] >= 2 * per_day[b]:
            triples.append((a, b, c))
    return triples


def pick_triple(triples: Iterable[tuple[float, float, float]]) -> tuple[float, float, float] | None:
    """Selection rule 3: the largest span (highest - lowest level); if spans tie, the smaller middle level."""
    triples = list(triples)
    if not triples:
        return None
    widest = max(c - a for a, _, c in triples)
    return min((t for t in triples if math.isclose(t[2] - t[0], widest)), key=lambda t: t[1])


def evaluate_stage1(summary: pd.DataFrame) -> list[CandidateResult]:
    """Criteria S1-S6 for every (beta, gamma) candidate of a no-intervention Stage 1 summary table."""
    if set(summary["strategy"]) != {"none"}:
        raise ValueError("Stage 1 must contain no-intervention runs only (pilot-protocol section 3)")
    results = []
    for (beta, gamma), df in summary.groupby(list(CANDIDATE_KEYS), sort=True):
        levels = _nonzero_levels(df)
        completed = df[df["status"] != STATUS_FAILED]
        minor = completed["final_attack_rate"] <= MINOR_OUTBREAK_MAX_ATTACK_RATE
        zero = completed[completed["transfer_rate"] == 0]
        top_two = levels[-2:]
        minor_share_top = {lvl: float(minor[completed["transfer_rate"] == lvl].mean()) for lvl in top_two}
        lowest_median = float(completed.loc[completed["transfer_rate"] == levels[0], "final_attack_rate"].median())
        block_share = {
            lvl: float(
                completed.loc[completed["transfer_rate"] == lvl, "blocked_transfers"].sum()
                / max(1, completed.loc[completed["transfer_rate"] == lvl, "attempted_transfers"].sum())
            )
            for lvl in levels
        }
        censored_share = float((df["status"] == STATUS_CENSORED).mean())
        triples = _s5_triples(completed)
        checks = {
            "S1_zero_transfer_one_tank": bool(len(zero) > 0 and (zero["affected_tanks"] == 1).all()),
            "S2_no_failed_censored_le_1pct": bool((df["status"] == STATUS_FAILED).sum() == 0 and censored_share <= 0.01),
            "S3_top_two_minor_le_70pct": bool(len(top_two) == 2 and all(s <= 0.70 for s in minor_share_top.values())),
            "S4_lowest_level_median_ar_le_0_90": bool(lowest_median <= 0.90),
            "S5_three_distinguishable_levels": bool(triples),
            "S6_blocked_share_le_20pct": bool(all(s <= 0.20 for s in block_share.values())),
        }
        notes = {
            "runs": len(df),
            STATUS_FAILED: int((df["status"] == STATUS_FAILED).sum()),
            "censored_share": censored_share,
            "minor_share_top_two": minor_share_top,
            "lowest_level_median_attack_rate": lowest_median,
            "blocked_share_by_level": block_share,
        }
        results.append(CandidateResult(float(beta), float(gamma), checks, notes, triples))
    return results


@dataclass
class Stage1Selection:
    beta: float | None
    gamma: float | None
    transfer_rates: tuple[float, ...] | None  # 0 + the three S5 levels
    ambiguities: list[str]


def select_stage1(summary: pd.DataFrame, results: list[CandidateResult]) -> Stage1Selection:
    """Selection rules 1-3. Returns ``ambiguities`` instead of guessing when the protocol does not decide."""
    passing = [r for r in results if r.passed]
    if not passing:
        return Stage1Selection(None, None, None, ["no candidate meets S1-S6: record and extend the grid (rule 5)"])

    def rank(r: CandidateResult) -> tuple[float, float]:
        df = summary[(summary["beta"] == r.beta) & (summary["gamma"] == r.gamma) & (summary["status"] != STATUS_FAILED)]
        middle = pick_triple(r.triples)[1]
        return abs(df.loc[df["transfer_rate"] == middle, "final_attack_rate"].median() - 0.5), r.beta

    passing.sort(key=rank)
    ambiguities = []
    if len(passing) > 1 and rank(passing[0]) == rank(passing[1]):
        ambiguities.append(f"rule 2 ties between {[(r.beta, r.gamma) for r in passing[:2]]}")
    chosen = passing[0]
    return Stage1Selection(chosen.beta, chosen.gamma, (0.0, *pick_triple(chosen.triples)), ambiguities)


def round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


def first_day_affected_at_least(raw: dict[str, Any], tanks: int = 2) -> int | None:
    return next((d["day"] for d in raw["daily"] if d["affected_tanks_ever"] >= tanks), None)


def delay_levels(raw_records: Iterable[dict[str, Any]], beta: float, gamma: float, middle_rate: float) -> dict[str, Any]:
    """Response-delay levels D1-D3 from Stage 1 no-intervention runs (pilot-protocol section 4)."""
    second_tank_days, peak_days = [], []
    for raw in raw_records:
        cfg = raw["config"]
        if (cfg["beta"], cfg["gamma"], cfg["transfer_rate"]) != (beta, gamma, middle_rate) or raw["status"] == STATUS_FAILED:
            continue
        if raw["metrics"]["final_attack_rate"] <= MINOR_OUTBREAK_MAX_ATTACK_RATE:
            continue
        day = first_day_affected_at_least(raw)
        if day is not None:
            second_tank_days.append(day)
        peak_days.append(raw["metrics"]["time_to_peak"])
    if not peak_days:
        return {"levels": None, "valid": False, "reason": "no non-minor outbreaks at the middle level"}
    d2 = round_half_up(float(np.median(second_tank_days))) if second_tank_days else None
    d3 = round_half_up(float(np.median(peak_days)))
    valid = d2 is not None and 1 < d2 < d3
    return {
        "levels": (1, d2, d3) if valid else None,
        "valid": valid,
        "d2_median_raw": float(np.median(second_tank_days)) if second_tank_days else None,
        "d3_median_raw": float(np.median(peak_days)),
        "non_minor_runs": len(peak_days),
        "reason": None if valid else "D2 >= D3 or D2 <= 1: fall back to the next Stage 1 candidate",
    }


def stage2_design(selection: Stage1Selection, delays: tuple[int, int, int], stage1_design: dict[str, Any]) -> dict[str, Any]:
    """The Stage 2 design JSON (pilot-protocol section 4). Transfer rates are the three non-zero levels:
    at rate 0 a quarantine can never block a transfer, so it would only dilute criterion Q1."""
    return {
        "name": "pilot-stage2-intervention",
        "transfer_rates": [r for r in selection.transfer_rates if r > 0],
        "response_delays": list(delays),
        "network_seeds": stage1_design["network_seeds"],
        "epidemic_seeds": stage1_design["epidemic_seeds"],
        "policy_seeds": [900, 901, 902],
        "fixed": {**stage1_design.get("fixed", {}), "beta": selection.beta, "gamma": selection.gamma},
        "sweep": {"quarantine_duration": [7, 14, 21]},
    }


# --------------------------------------------------------------------------------------------------
# Stage 2: quarantine duration D (pilot-protocol section 4; strategies pooled, never compared)
# --------------------------------------------------------------------------------------------------


def evaluate_stage2(summary: pd.DataFrame) -> pd.DataFrame:
    """Criteria Q1-Q3 per D candidate. Uses pooled intervention runs and the shared baselines only.

    The legacy whole-run blocked counter mixes capacity and quarantine blocking, including days outside
    quarantine. Both historical proxy denominators are kept for audit, but neither verifies Q1.

    Q1 is evaluated only from the blocked-by-cause counters (pilot-protocol section 4, pre-registered
    2026-10-06): share of started runs with ``blocked_quarantine_out + blocked_quarantine_in >= 1``. Raw
    records written before those counters existed leave Q1 and overall acceptance nullable (unverified).
    """
    gamma = summary["gamma"].unique()
    if len(gamma) != 1:
        raise ValueError("Stage 2 must use a single frozen gamma")
    baseline = summary[(summary["strategy"] == "none") & (summary["status"] == STATUS_COMPLETED)]
    extinction_median = float(baseline["time_to_extinction"].median())
    rows = []
    interventions = summary[(summary["strategy"] != "none") & (summary["status"] != STATUS_FAILED)]
    has_causes = "blocked_quarantine_out" in summary and summary["blocked_quarantine_out"].notna().all()
    for d, df in interventions.groupby("quarantine_duration", sort=True):
        blocking = df["blocked_transfers"] >= 1
        started = df["intervention_start_day"].notna()
        share_all = float(blocking.mean())
        share_started = float(blocking[started].mean()) if started.any() else 0.0
        q1: dict[str, object] = {"Q1_status": "unverified_mixed_blocking_counter"}
        if has_causes:
            quarantine_block = (df["blocked_quarantine_out"] + df["blocked_quarantine_in"]) >= 1
            share_q = float(quarantine_block[started].mean()) if started.any() else 0.0
            q1 = {
                "Q1_status": "verified",
                "share_quarantine_block_ge_1_started": share_q,
                "share_quarantine_block_ge_1_all_runs": float(quarantine_block.mean()),
                "share_capacity_block_ge_1_started": float((df["blocked_capacity"][started] >= 1).mean())
                if started.any() else 0.0,
                "Q1_quarantine_not_noop": share_q >= 0.90,
            }
        rows.append(
            {
                "quarantine_duration": int(d),
                "runs": len(df),
                "runs_quarantine_started": int(started.sum()),
                "share_blocked_ge_1_all_runs": share_all,
                "share_blocked_ge_1_started": share_started,
                "baseline_extinction_median": extinction_median,
                "Q1_proxy_all_runs": share_all >= 0.90,
                "Q1_proxy_started_runs": share_started >= 0.90,
                **q1,
                "Q2_D_le_25pct_extinction": d <= 0.25 * extinction_median,
                "Q3_D_ge_infectious_period": d >= 1 / gamma[0],
            }
        )
    table = pd.DataFrame(rows)
    q2_q3 = table["Q2_D_le_25pct_extinction"] & table["Q3_D_ge_infectious_period"]
    table["passed_proxy_started"] = table["Q1_proxy_started_runs"] & q2_q3
    table["passed_proxy_all_runs"] = table["Q1_proxy_all_runs"] & q2_q3
    if has_causes:
        table["Q1_quarantine_not_noop"] = table["Q1_quarantine_not_noop"].astype("boolean")
    else:
        table["Q1_quarantine_not_noop"] = pd.Series(pd.NA, index=table.index, dtype="boolean")
    # Do not use DataFrame.all(): its skipna default would turn an unknown Q1 into a pass.
    table["passed"] = table["Q1_quarantine_not_noop"] & q2_q3
    return table


def select_duration(table: pd.DataFrame) -> int | None:
    """Select only fully verified candidates; a proxy pass or unknown Q1 is insufficient."""
    # Historical tables used passed=True for the mixed-counter proxy. Reject that schema too.
    if "Q1_status" not in table:
        return None
    verified = table["Q1_status"].eq("verified") & table["passed"].fillna(False)
    passing = table.loc[verified, "quarantine_duration"]
    return int(passing.min()) if len(passing) else None


# --------------------------------------------------------------------------------------------------
# Formal analysis (experiment-plan sections 6 and 12)
# --------------------------------------------------------------------------------------------------


def condition_summary(
    summary: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS + SECONDARY_METRICS, **boot_kwargs
) -> pd.DataFrame:
    """Count, mean, median, SD, IQR and a 95% CI per condition and metric. The CI is a network-cluster
    bootstrap (runs sharing a network are not independent), which also keeps it inside the outcome's range.
    The shared no-intervention baseline is reported once per transfer rate (D007)."""
    keys = ["transfer_rate", "response_delay", "strategy"]
    df = summary[summary["status"] != STATUS_FAILED].copy()
    df.loc[df["strategy"] == "none", "response_delay"] = -1  # baseline is delay-independent
    rows = []
    for cond, group in df.groupby(keys, sort=True):
        for metric in metrics:
            values = group[metric].dropna().astype(float)
            n = len(values)
            mean = values.mean() if n else np.nan
            if n > 1:
                _, ci_low, ci_high = cluster_bootstrap_ci(group.dropna(subset=[metric]), metric, **boot_kwargs)
            else:
                ci_low = ci_high = np.nan
            rows.append(
                {
                    **dict(zip(keys, cond)),
                    "metric": metric,
                    "n": n,
                    "n_missing": len(group) - n,  # e.g. censored runs for time_to_extinction
                    "mean": mean,
                    "median": values.median() if n else np.nan,
                    "sd": values.std(ddof=1) if n > 1 else np.nan,
                    "iqr": values.quantile(0.75) - values.quantile(0.25) if n else np.nan,
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                }
            )
    out = pd.DataFrame(rows)
    out["response_delay"] = out["response_delay"].replace(-1, pd.NA)
    return out


def _complete_arm_cells(arms: pd.DataFrame, keys: list[str], expected_policy_seeds: int | None) -> pd.Series:
    """Boolean per cell (``keys``): exactly one targeted run and exactly ``expected_policy_seeds`` random runs
    with distinct policy seeds. ``None`` infers the expected count as the largest seen, which cannot detect a
    seed missing from every cell, so callers that know the design should pass it."""
    targeted_n = arms[arms["strategy"] == "betweenness"].groupby(keys).size()
    random = arms[arms["strategy"] == "random"].groupby(keys)["policy_seed"].agg(["size", "nunique"])
    cells = targeted_n.index.union(random.index)
    targeted_n = targeted_n.reindex(cells, fill_value=0)
    random = random.reindex(cells, fill_value=0)
    expected = expected_policy_seeds if expected_policy_seeds is not None else int(random["nunique"].max() or 0)
    return (targeted_n == 1) & (random["size"] == expected) & (random["nunique"] == expected)


def paired_differences(
    summary: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS, expected_policy_seeds: int | None = None
) -> pd.DataFrame:
    """Targeted-minus-random difference per paired block (experiment-plan section 6).

    The block key is (network_seed, epidemic_seed, transfer_rate, response_delay, quarantine_duration).
    The random arm of a block is the mean over its policy seeds, so each block contributes one difference.
    A block is dropped if either arm failed (``attrs["dropped_blocks"]``) or if it does not have exactly one
    targeted run and ``expected_policy_seeds`` distinct random runs (``attrs["incomplete_blocks"]``).
    """
    keys = list(BLOCK_KEYS) + ["response_delay", "quarantine_duration"]
    arms = summary[summary["strategy"].isin(["betweenness", "random"])]
    failed_blocks = arms.loc[arms["status"] == STATUS_FAILED, keys].drop_duplicates()
    ok = arms.merge(failed_blocks, on=keys, how="left", indicator=True)
    ok = ok[ok["_merge"] == "left_only"]
    complete = _complete_arm_cells(ok, keys, expected_policy_seeds)
    ok = ok.join(complete.rename("_complete"), on=keys)
    ok = ok[ok["_complete"]]
    metrics = list(metrics)
    targeted = ok[ok["strategy"] == "betweenness"].set_index(keys)
    random_mean = ok[ok["strategy"] == "random"].groupby(keys)[metrics].mean()
    joined = targeted[metrics].join(random_mean, lsuffix="_targeted", rsuffix="_random", how="inner")
    # Before the response day every arm of a block shares the same draws, so a quarantine that never
    # started (extinction first) is a property of the block, not of the strategy (pilot report section 5).
    joined["quarantine_started"] = targeted["intervention_start_day"].notna().reindex(joined.index)
    for m in metrics:
        joined[f"diff_{m}"] = joined[f"{m}_targeted"] - joined[f"{m}_random"]
    out = joined.reset_index()
    out.attrs["dropped_blocks"] = len(failed_blocks)
    out.attrs["incomplete_blocks"] = int((~complete).sum())
    return out


def _cluster_resample_counts(n_clusters: int, n_boot: int, seed: int) -> np.ndarray:
    """(n_boot, n_clusters) times each network instance is drawn when resampling whole clusters."""
    rng = np.random.default_rng(seed)
    picked = rng.integers(0, n_clusters, size=(n_boot, n_clusters))
    return np.stack([np.bincount(row, minlength=n_clusters) for row in picked])


def cluster_bootstrap_ratio(
    df: pd.DataFrame,
    numerator: str,
    denominator: str | None = None,
    cluster: str = "network_seed",
    n_boot: int = 2000,
    seed: int = 0,
) -> tuple[float, float, float]:
    """sum(numerator) / sum(denominator) (or / row count) with a percentile 95% CI from resampling whole
    network instances (experiment-plan section 12). Covers both a mean and a ratio of means. The same
    ``seed`` draws the same resamples for every statistic."""
    df = df.dropna(subset=[numerator] + ([denominator] if denominator else []))
    by = df.groupby(cluster)
    num = by[numerator].sum().to_numpy(dtype=float)
    den = by[denominator].sum().to_numpy(dtype=float) if denominator else by.size().to_numpy(dtype=float)
    point = num.sum() / den.sum() if den.sum() > 0 else float("nan")
    counts = _cluster_resample_counts(len(num), n_boot, seed)
    with np.errstate(divide="ignore", invalid="ignore"):
        boots = (counts @ num) / (counts @ den)
    low, high = np.nanpercentile(boots, [2.5, 97.5]) if np.isfinite(boots).any() else (np.nan, np.nan)
    return float(point), float(low), float(high)


def cluster_bootstrap_ci(df: pd.DataFrame, value: str, **kwargs) -> tuple[float, float, float]:
    """Mean of ``value`` with a network-cluster bootstrap CI."""
    return cluster_bootstrap_ratio(df, value, **kwargs)


def relative_reduction(df: pd.DataFrame, metric: str) -> float:
    """Ratio of means: 1 - mean(targeted) / mean(random) = -mean(diff) / mean(random). Positive means the
    targeted arm is lower. Unlike a mean of per-block ratios it is not dominated by blocks whose random-arm
    value is close to zero."""
    denominator = df[f"{metric}_random"].mean()
    return float(-df[f"diff_{metric}"].mean() / denominator) if denominator > 0 else float("nan")


def paired_effect_table(diffs: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS, **boot_kwargs) -> pd.DataFrame:
    """Mean and median paired difference with cluster-bootstrap CIs per (transfer_rate, response_delay, D),
    for all blocks and for the blocks whose quarantine started (``subset`` column)."""
    rows = []
    cell_keys = ["transfer_rate", "response_delay", "quarantine_duration"]
    subsets = {"all_blocks": diffs, "quarantine_started": diffs[diffs["quarantine_started"]]}
    for (subset, sub), (cell, group) in (
        ((name, sub), item) for name, sub in subsets.items() for item in sub.groupby(cell_keys, sort=True)
    ):
        for m in metrics:
            mean, lo, hi = cluster_bootstrap_ci(group, f"diff_{m}", **boot_kwargs)
            # relative reduction = -sum(diff) / sum(random), bootstrapped on the same resamples
            neg = group.assign(_neg_diff=-group[f"diff_{m}"])
            rel, rel_lo, rel_hi = cluster_bootstrap_ratio(neg, "_neg_diff", f"{m}_random", **boot_kwargs)
            rows.append(
                {
                    "subset": subset,
                    **dict(zip(cell_keys, cell)),
                    "metric": m,
                    "blocks": len(group),
                    "networks": group["network_seed"].nunique(),
                    "mean_diff": mean,
                    "mean_diff_ci95_low": lo,
                    "mean_diff_ci95_high": hi,
                    "median_diff": float(group[f"diff_{m}"].median()),
                    "mean_targeted": float(group[f"{m}_targeted"].mean()),
                    "mean_random": float(group[f"{m}_random"].mean()),
                    "rel_reduction": rel,
                    "rel_reduction_ci95_low": rel_lo,
                    "rel_reduction_ci95_high": rel_hi,
                    "share_targeted_better": float((group[f"diff_{m}"] < -DIFF_TOLERANCE).mean()),
                    "share_tied": float((group[f"diff_{m}"].abs() <= DIFF_TOLERANCE).mean()),
                }
            )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------
# Representative runs (experiment-plan section 13: chosen by an objective rule, not by appearance)
# --------------------------------------------------------------------------------------------------

REPRESENTATIVE_TRANSFER_RATE = 0.025  # the middle formal level


def regions_ever_infected(raw: dict[str, Any]) -> set[int]:
    return {t["region_id"] for day in raw["daily"] for t in day["tanks"] if t["I"] > 0}


def outbreak_class(raw: dict[str, Any]) -> str:
    """``local`` if infection never reached a tank outside the region(s) of the initially infected tank(s),
    otherwise ``cross_region``.

    Limitation: the daily records are end-of-day snapshots, so an infectious agent that enters a tank and
    recovers on the same day is not visible. ``scripts/analyse_results.py`` counts runs where the model's
    ``affected_tanks`` exceeds the tanks seen here, and those runs should be checked by hand."""
    regions = raw["network"]["regions"]
    initial = {regions[t] for t in raw["initial_infected_tanks"]}
    return "local" if regions_ever_infected(raw) <= initial else "cross_region"


def pick_representative_runs(
    raw_records: Iterable[dict[str, Any]], transfer_rate: float = REPRESENTATIVE_TRANSFER_RATE
) -> dict[str, dict[str, Any]]:
    """Rule fixed on 2026-10-06 after viewing only aggregate formal results, before viewing any single run:
    among completed no-intervention runs at ``transfer_rate``, split by ``outbreak_class`` and pick, per class,
    the run whose final attack rate is closest to that class's median; ties go to the smallest
    (network_seed, epidemic_seed). Returns ``{class: {"raw": ..., "class_size": ..., "class_median": ...}}``."""
    by_class: dict[str, list[dict[str, Any]]] = {}
    for raw in raw_records:
        cfg = raw["config"]
        if cfg["strategy"] != "none" or cfg["transfer_rate"] != transfer_rate or raw["status"] != STATUS_COMPLETED:
            continue
        by_class.setdefault(outbreak_class(raw), []).append(raw)
    picked = {}
    for name, runs in sorted(by_class.items()):
        median = float(np.median([r["metrics"]["final_attack_rate"] for r in runs]))
        best = min(
            runs,
            key=lambda r: (
                abs(r["metrics"]["final_attack_rate"] - median),
                r["config"]["network_seed"],
                r["config"]["epidemic_seed"],
            ),
        )
        picked[name] = {"raw": best, "class_size": len(runs), "class_median": median}
    return picked


def baseline_differences(
    summary: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS, expected_policy_seeds: int | None = None
) -> pd.DataFrame:
    """Strategy-minus-no-intervention difference per paired block (descriptive; added 2026-10-06 after the
    formal results, to show how much each quarantine changes the shared baseline at each response delay).

    One row per (block, strategy) with strategy in {betweenness, random}; the random arm is the mean over its
    policy seeds. A block with any failed run is dropped. A block without exactly one baseline, or a cell
    without one targeted run and ``expected_policy_seeds`` distinct random runs, is excluded and counted in
    ``attrs["incomplete_blocks"]``.
    """
    metrics = list(metrics)
    keys = list(BLOCK_KEYS)
    cell_keys = keys + ["response_delay", "quarantine_duration"]
    failed = summary.loc[summary["status"] == STATUS_FAILED, keys].drop_duplicates()
    ok = summary.merge(failed, on=keys, how="left", indicator=True)
    ok = ok[ok["_merge"] == "left_only"].drop(columns="_merge")
    base_rows = ok[ok["strategy"] == "none"]
    base_n = base_rows.groupby(keys).size()
    arms = ok[ok["strategy"] != "none"]
    complete = _complete_arm_cells(arms, cell_keys, expected_policy_seeds)
    complete_cells = complete[complete].index.to_frame(index=False)
    complete_cells = complete_cells[
        complete_cells.set_index(keys).index.isin(base_n[base_n == 1].index)
    ]
    arms = arms.merge(complete_cells, on=cell_keys)
    base = base_rows.set_index(keys)[metrics]
    base = base[base.index.isin(base_n[base_n == 1].index)]
    out = arms.groupby(cell_keys + ["strategy"])[metrics].mean().reset_index()
    out = out.join(base, on=keys, rsuffix="_none")
    for m in metrics:
        out[f"{m}_arm"] = out[m]
        out[f"diff_{m}"] = out[m] - out[f"{m}_none"]
    out = out.drop(columns=metrics)
    all_cells = len(complete)
    out.attrs["incomplete_blocks"] = int(all_cells - len(complete_cells))
    return out


def baseline_effect_table(diffs: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS, **boot_kwargs) -> pd.DataFrame:
    """Mean strategy-minus-baseline difference and relative reduction with network-cluster bootstrap CIs."""
    rows = []
    cell_keys = ["strategy", "transfer_rate", "response_delay", "quarantine_duration"]
    for cell, group in diffs.groupby(cell_keys, sort=True):
        for m in metrics:
            mean, lo, hi = cluster_bootstrap_ci(group, f"diff_{m}", **boot_kwargs)
            neg = group.assign(_neg_diff=-group[f"diff_{m}"])
            rel, rel_lo, rel_hi = cluster_bootstrap_ratio(neg, "_neg_diff", f"{m}_none", **boot_kwargs)
            rows.append(
                {
                    **dict(zip(cell_keys, cell)),
                    "metric": m,
                    "blocks": len(group),
                    "mean_none": float(group[f"{m}_none"].mean()),
                    "mean_arm": float(group[f"{m}_arm"].mean()),
                    "mean_diff": mean,
                    "mean_diff_ci95_low": lo,
                    "mean_diff_ci95_high": hi,
                    "rel_reduction": rel,
                    "rel_reduction_ci95_low": rel_lo,
                    "rel_reduction_ci95_high": rel_hi,
                }
            )
    return pd.DataFrame(rows)
