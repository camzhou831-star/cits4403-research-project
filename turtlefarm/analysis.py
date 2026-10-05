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
    """Criteria Q1-Q3 per D candidate. Uses pooled intervention runs and the shared baselines only."""
    gamma = summary["gamma"].unique()
    if len(gamma) != 1:
        raise ValueError("Stage 2 must use a single frozen gamma")
    baseline = summary[(summary["strategy"] == "none") & (summary["status"] == STATUS_COMPLETED)]
    extinction_median = float(baseline["time_to_extinction"].median())
    rows = []
    interventions = summary[(summary["strategy"] != "none") & (summary["status"] != STATUS_FAILED)]
    for d, df in interventions.groupby("quarantine_duration", sort=True):
        share_blocking = float((df["blocked_transfers"] >= 1).mean())
        rows.append(
            {
                "quarantine_duration": int(d),
                "runs": len(df),
                "share_blocked_ge_1": share_blocking,
                "baseline_extinction_median": extinction_median,
                "Q1_quarantine_not_noop": share_blocking >= 0.90,
                "Q2_D_le_25pct_extinction": d <= 0.25 * extinction_median,
                "Q3_D_ge_infectious_period": d >= 1 / gamma[0],
            }
        )
    table = pd.DataFrame(rows)
    table["passed"] = table[["Q1_quarantine_not_noop", "Q2_D_le_25pct_extinction", "Q3_D_ge_infectious_period"]].all(axis=1)
    return table


def select_duration(table: pd.DataFrame) -> int | None:
    passing = table.loc[table["passed"], "quarantine_duration"]
    return int(passing.min()) if len(passing) else None


# --------------------------------------------------------------------------------------------------
# Formal analysis (experiment-plan sections 6 and 12)
# --------------------------------------------------------------------------------------------------


def condition_summary(summary: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS + SECONDARY_METRICS) -> pd.DataFrame:
    """Count, mean, median, SD, IQR and a normal-approximation 95% CI per condition and metric.
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
            half = 1.96 * values.std(ddof=1) / math.sqrt(n) if n > 1 else np.nan
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
                    "ci95_low": mean - half,
                    "ci95_high": mean + half,
                }
            )
    out = pd.DataFrame(rows)
    out["response_delay"] = out["response_delay"].replace(-1, pd.NA)
    return out


def paired_differences(summary: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS) -> pd.DataFrame:
    """Targeted-minus-random difference per paired block (experiment-plan section 6).

    The block key is (network_seed, epidemic_seed, transfer_rate, response_delay, quarantine_duration).
    The random arm of a block is the mean over its policy seeds, so each block contributes one difference.
    A block is dropped if either arm failed; the count of dropped blocks is kept in ``attrs``.
    """
    keys = list(BLOCK_KEYS) + ["response_delay", "quarantine_duration"]
    arms = summary[summary["strategy"].isin(["betweenness", "random"])]
    failed_blocks = arms.loc[arms["status"] == STATUS_FAILED, keys].drop_duplicates()
    ok = arms.merge(failed_blocks, on=keys, how="left", indicator=True)
    ok = ok[ok["_merge"] == "left_only"]
    metrics = list(metrics)
    targeted = ok[ok["strategy"] == "betweenness"].set_index(keys)[metrics]
    random_mean = ok[ok["strategy"] == "random"].groupby(keys)[metrics].mean()
    joined = targeted.join(random_mean, lsuffix="_targeted", rsuffix="_random", how="inner")
    for m in metrics:
        joined[f"diff_{m}"] = joined[f"{m}_targeted"] - joined[f"{m}_random"]
        joined[f"rel_reduction_{m}"] = np.where(
            joined[f"{m}_random"] > 0, -joined[f"diff_{m}"] / joined[f"{m}_random"], np.nan
        )
    out = joined.reset_index()
    out.attrs["dropped_blocks"] = len(failed_blocks)
    return out


def cluster_bootstrap_ci(
    df: pd.DataFrame,
    value: str,
    cluster: str = "network_seed",
    n_boot: int = 2000,
    seed: int = 0,
    stat=np.mean,
) -> tuple[float, float, float]:
    """Point estimate and percentile 95% CI, resampling whole network instances (experiment-plan section 12)."""
    groups = [g[value].dropna().to_numpy() for _, g in df.groupby(cluster)]
    point = float(stat(np.concatenate(groups)))
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        picked = rng.integers(0, len(groups), size=len(groups))
        boots[i] = stat(np.concatenate([groups[j] for j in picked]))
    low, high = np.percentile(boots, [2.5, 97.5])
    return point, float(low), float(high)


def paired_effect_table(diffs: pd.DataFrame, metrics: Iterable[str] = PRIMARY_METRICS, **boot_kwargs) -> pd.DataFrame:
    """Mean and median paired difference with cluster-bootstrap CIs per (transfer_rate, response_delay, D)."""
    rows = []
    cell_keys = ["transfer_rate", "response_delay", "quarantine_duration"]
    for cell, group in diffs.groupby(cell_keys, sort=True):
        for m in metrics:
            mean, lo, hi = cluster_bootstrap_ci(group, f"diff_{m}", **boot_kwargs)
            rows.append(
                {
                    **dict(zip(cell_keys, cell)),
                    "metric": m,
                    "blocks": len(group),
                    "networks": group["network_seed"].nunique(),
                    "mean_diff": mean,
                    "mean_diff_ci95_low": lo,
                    "mean_diff_ci95_high": hi,
                    "median_diff": float(group[f"diff_{m}"].median()),
                    "mean_rel_reduction": float(group[f"rel_reduction_{m}"].mean()),
                    "share_targeted_better": float((group[f"diff_{m}"] < 0).mean()),
                }
            )
    return pd.DataFrame(rows)
