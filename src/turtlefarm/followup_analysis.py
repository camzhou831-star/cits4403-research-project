"""Analysis of the separately labelled duration/policy follow-up; never runs simulations.

All contrasts use every complete matched block, including outbreaks ending before intervention.
Intervals are pointwise network-cluster percentile bootstrap intervals, not multiplicity-adjusted.
Policy Monte Carlo errors condition on the recorded networks and epidemic draws.
"""

from __future__ import annotations

import itertools
import json
import re

import numpy as np
import pandas as pd

from turtlefarm.analysis import cluster_bootstrap_ratio

PRIMARY = ("final_attack_rate", "affected_tanks")
EVENT_TIMES = ("first_infectious_arrival", "first_local_secondary_infection")
OBSERVATION_COUNTS = (
    "infectious_cross_region_transfers", "regions_visited_by_I",
    "regions_with_local_transmission", "local_infections_outside_initial_region",
)
EVENT_INDICATORS = ("infectious_arrival_observed", "local_secondary_infection_observed")
FACTORS = ("beta", "gamma", "capacity", "k", "transfer_rate")
BLOCK = ("network_seed", "epidemic_seed", *FACTORS)
CELL = (*FACTORS, "quarantine_duration", "response_delay")
DELAY_CONTRASTS = ((12, 1), (33, 1), (33, 12))
DURATION_CONTRASTS = ((14, 7), (28, 7), (28, 14))


def _pair(value: object) -> tuple[int, int]:
    try:
        pair = tuple(sorted(int(t) for t in str(value).split(",")))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid selected_tanks: {value!r}") from exc
    if len(pair) != 2 or len(set(pair)) != 2 or not all(0 <= t < 20 for t in pair):
        raise ValueError(f"invalid selected_tanks: {value!r}")
    return pair


def validate_runs(
    summary: pd.DataFrame, *, followup: bool,
    network_seeds: tuple[int, ...] = tuple(range(200, 220)),
    epidemics_per_network: int = 5, policy_count: int = 20,
    expected_protocol_hash: str | None = None,
) -> pd.DataFrame:
    """Return a checked copy, rejecting missing/extra/duplicate runs rather than dropping them.

    The historical formal CSV omits capacity: its documented fixed value 12 is supplied explicitly.
    Follow-up CSVs must contain it. Smaller network/replicate sets are for deterministic unit fixtures;
    epidemic numbering retains the study's five-seed stride and policy numbering its twenty-seed stride.
    Censored/failed runs require a separate analysis decision; this function never silently excludes them.
    """
    required = set(BLOCK) | {"strategy", "response_delay", "quarantine_duration", "policy_seed",
                             "status", "network_hash", "selected_tanks", *PRIMARY}
    if not followup:
        required.remove("capacity")
    else:
        required.update((*EVENT_TIMES, *OBSERVATION_COUNTS, "p_in", "p_out", "max_days",
                         "protocol_hash", "observation_schema_version", "code_commit"))
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    df = summary.copy()
    if "capacity" not in df:
        df["capacity"] = 12
    for col, value in {"beta": 0.2, "gamma": 0.1, "capacity": 12, "k": 2}.items():
        if not df[col].eq(value).all():
            raise ValueError(f"expected fixed {col}={value}")
    if followup:
        for col, value in {"p_in": 0.6, "p_out": 0.05, "max_days": 365}.items():
            if not df[col].eq(value).all():
                raise ValueError(f"expected fixed {col}={value}")
        hashes = df["protocol_hash"].drop_duplicates().tolist()
        if len(hashes) != 1 or not isinstance(hashes[0], str) or not re.fullmatch(r"[0-9a-f]{64}", hashes[0]):
            raise ValueError("missing/mixed/invalid protocol_hash")
        if expected_protocol_hash is not None and hashes[0] != expected_protocol_hash:
            raise ValueError("protocol_hash does not match the supplied design")
        if not df["observation_schema_version"].eq("turtlefarm.observation.v1").all():
            raise ValueError("unsupported observation_schema_version")
        if df["code_commit"].isna().any() or df["code_commit"].nunique() != 1 or not df["code_commit"].astype(str).str.len().gt(0).all():
            raise ValueError("follow-up must record one nonempty implementation commit")
    if not len(df) or not df["status"].eq("completed").all():
        raise ValueError("all planned runs must be completed; failed/censored/empty input requires review: "
                         f"{df['status'].value_counts(dropna=False).to_dict()}")
    if not 1 <= epidemics_per_network <= 5 or not 1 <= policy_count <= 20:
        raise ValueError("invalid expected epidemic or policy count")
    rates = (0.025,) if followup else (0.0, 0.01, 0.025, 0.1)
    durations = (7, 14, 28) if followup else (14,)
    run_key = ["network_seed", "epidemic_seed", "transfer_rate", "strategy",
               "response_delay", "quarantine_duration", "policy_seed"]
    numeric = ["network_seed", "epidemic_seed", "response_delay", "quarantine_duration"]
    for col in numeric:
        if df[col].isna().any() or not (df[col] == df[col].astype(int)).all():
            raise ValueError(f"invalid integer key: {col}")
    random = df["strategy"].eq("random")
    if df.loc[random, "policy_seed"].isna().any() or df.loc[~random, "policy_seed"].notna().any():
        raise ValueError("policy_seed is required exactly for random runs")
    if not (df.loc[random, "policy_seed"] == df.loc[random, "policy_seed"].astype(int)).all():
        raise ValueError("policy_seed must be integral")
    keys = df[run_key].copy()
    keys["policy_seed"] = keys["policy_seed"].fillna(-1).astype(int)
    if keys.duplicated().any():
        raise ValueError("duplicate run keys")
    expected = set()
    for network, offset, rate in itertools.product(network_seeds, range(epidemics_per_network), rates):
        epidemic = 20000 + 5 * (network - 200) + offset
        expected.add((network, epidemic, rate, "none", 0, 0, -1))
        seeds = (range(50000 + 20 * (network - 200), 50000 + 20 * (network - 200) + policy_count)
                 if followup else (1000, 1001, 1002))
        for duration, delay in itertools.product(durations, (1, 12, 33)):
            expected.add((network, epidemic, rate, "betweenness", delay, duration, -1))
            expected.update((network, epidemic, rate, "random", delay, duration, seed) for seed in seeds)
    actual = set(keys.itertuples(index=False, name=None))
    if actual != expected:
        raise ValueError(f"incomplete/unexpected design: {len(expected - actual)} missing, "
                         f"{len(actual - expected)} unexpected run keys")
    if df["network_hash"].isna().any() or not df.groupby("network_seed")["network_hash"].nunique().eq(1).all():
        raise ValueError("matched runs must share one network_hash per network_seed")
    intervention = df["strategy"].ne("none")
    df.loc[intervention, "selected_tanks"] = df.loc[intervention, "selected_tanks"].map(
        lambda value: ",".join(map(str, _pair(value))))
    policy_keys = ["network_seed", "strategy", "policy_seed"]
    if not df.loc[intervention].groupby(policy_keys, dropna=False)["selected_tanks"].nunique().eq(1).all():
        raise ValueError("selected pairs must be reused across epidemics, durations and delays")
    for metric in PRIMARY + (OBSERVATION_COUNTS if followup else ()):
        values = pd.to_numeric(df[metric], errors="coerce")
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"missing/nonfinite/negative outcome: {metric}")
    if not df["final_attack_rate"].between(0, 1).all():
        raise ValueError("final_attack_rate outside [0, 1]")
    if not df["affected_tanks"].between(1, 20).all():
        raise ValueError("affected_tanks outside [1, 20]")
    if followup:
        for metric in OBSERVATION_COUNTS:
            if not df[metric].eq(df[metric].astype(int)).all():
                raise ValueError(f"nonintegral count: {metric}")
        for metric in ("regions_visited_by_I", "regions_with_local_transmission"):
            if not df[metric].between(0, 4).all():
                raise ValueError(f"region count outside [0, 4]: {metric}")
        for metric, indicator in zip(EVENT_TIMES, EVENT_INDICATORS):
            values = pd.to_numeric(df[metric], errors="coerce")
            if (df[metric].notna() & values.isna()).any():
                raise ValueError(f"invalid event time: {metric}")
            finite = values.dropna()
            if not np.isfinite(finite).all() or (finite < 1).any() or not finite.eq(finite.astype(int)).all():
                raise ValueError(f"invalid event time: {metric}")
            if "days_simulated" in df and (values > df["days_simulated"]).any():
                raise ValueError(f"event after simulation end: {metric}")
            df[metric] = values
            df[indicator] = values.notna().astype(int)
        if not df["first_infectious_arrival"].notna().eq(df["infectious_cross_region_transfers"] > 0).all():
            raise ValueError("arrival event and crossing count disagree")
        if not df["first_local_secondary_infection"].notna().eq(df["local_infections_outside_initial_region"] > 0).all():
            raise ValueError("local infection event and outside infection count disagree")
        if (df["first_local_secondary_infection"].notna() & df["first_infectious_arrival"].isna()).any():
            raise ValueError("outside local infection without infectious arrival")
        if (df["first_local_secondary_infection"] < df["first_infectious_arrival"]).any():
            raise ValueError("outside local infection precedes infectious arrival")
        if not (df["regions_visited_by_I"] > 1).eq(df["first_infectious_arrival"].notna()).all():
            raise ValueError("infectious-visit regions disagree with arrival event")
        if (df["regions_with_local_transmission"] > df["regions_visited_by_I"]).any():
            raise ValueError("local-transmission regions exceed infectious-visit regions")
    return df


def _interval(df: pd.DataFrame, value: str, *, n_boot: int, seed: int) -> tuple[float, float, float]:
    # Retain even all-non-event networks in conditional event-time resampling.
    work = df.assign(_numerator=df[value].fillna(0), _observed=df[value].notna().astype(int))
    return cluster_bootstrap_ratio(work, "_numerator", "_observed", n_boot=n_boot, seed=seed)


def _arm_means(df: pd.DataFrame, metrics: tuple[str, ...]) -> pd.DataFrame:
    keys = [*BLOCK, "quarantine_duration", "response_delay", "strategy"]
    return df.groupby(keys, as_index=False)[list(metrics)].mean()


def _effects(left: pd.DataFrame, right: pd.DataFrame, keys: list[str], groups: list[str],
             metrics: tuple[str, ...], *, n_boot: int, seed: int, **labels: object) -> list[dict]:
    paired = left.merge(right, on=keys, suffixes=("_left", "_right"), validate="one_to_one", how="outer",
                        indicator=True)
    if not paired["_merge"].eq("both").all():
        raise ValueError("unmatched contrast blocks")
    rows = []
    for cell, group in paired.groupby(groups, sort=True):
        cell = cell if isinstance(cell, tuple) else (cell,)
        for metric in metrics:
            diff = group.assign(_difference=group[f"{metric}_left"] - group[f"{metric}_right"])
            mean, lo, hi = _interval(diff, "_difference", n_boot=n_boot, seed=seed)
            rows.append({**dict(zip(groups, cell)), **labels, "metric": metric, "blocks": len(group),
                         "networks": group["network_seed"].nunique(),
                         "mean_left": group[f"{metric}_left"].mean(),
                         "mean_right": group[f"{metric}_right"].mean(),
                         "mean_diff": mean, "ci95_low": lo, "ci95_high": hi})
    return rows


def paired_contrasts(df: pd.DataFrame, *, axis: str, metrics: tuple[str, ...] = PRIMARY,
                     n_boot: int = 2000, seed: int = 0) -> pd.DataFrame:
    """Contrasts after validation: strategy=targeted-random, delay=late-early, duration=long-short."""
    if n_boot < 1 or not isinstance(seed, int) or seed < 0:
        raise ValueError("n_boot must be positive and seed a nonnegative integer")
    arms = _arm_means(df[df["strategy"].ne("none")], metrics)
    keys = [*BLOCK, "quarantine_duration", "response_delay"]
    if axis == "strategy":
        return pd.DataFrame(_effects(
            arms[arms["strategy"].eq("betweenness")], arms[arms["strategy"].eq("random")],
            keys, list(CELL), metrics, n_boot=n_boot, seed=seed, contrast="betweenness-random"))
    if axis not in ("response_delay", "quarantine_duration"):
        raise ValueError("unknown contrast axis")
    contrasts = DELAY_CONTRASTS if axis == "response_delay" else DURATION_CONTRASTS
    keys.remove(axis)
    keys.append("strategy")
    groups = [x for x in CELL if x != axis] + ["strategy"]
    rows = []
    for high, low in contrasts:
        rows.extend(_effects(
            arms[arms[axis].eq(high)], arms[arms[axis].eq(low)], keys, groups, metrics,
            n_boot=n_boot, seed=seed, contrast=f"{high}-{low}", **{f"{axis}_left": high,
                                                                     f"{axis}_right": low}))
    return pd.DataFrame(rows)


def formal_delay_effects(summary: pd.DataFrame, *, n_boot: int = 2000, seed: int = 0,
                         **validation_kwargs) -> pd.DataFrame:
    """Three matched delay contrasts at each nonzero formal transfer rate, with no started-only filter."""
    df = validate_runs(summary, followup=False, **validation_kwargs)
    return paired_contrasts(df[df["transfer_rate"] > 0], axis="response_delay", n_boot=n_boot, seed=seed)


def condition_summary(df: pd.DataFrame, *, n_boot: int = 2000, seed: int = 0) -> pd.DataFrame:
    """Event-time means condition on observed events; missing is a non-event, never day zero.

    Counts include random policy replicates; network resampling preserves their dependence. Unconditional
    event-incidence indicator rows accompany the conditional time rows.
    """
    metrics = PRIMARY + OBSERVATION_COUNTS + EVENT_TIMES + EVENT_INDICATORS
    groups = [*CELL, "strategy"]
    rows = []
    for cell, group in df.groupby(groups, sort=True):
        for metric in metrics:
            mean, lo, hi = _interval(group, metric, n_boot=n_boot, seed=seed)
            observed = int(group[metric].notna().sum())
            rows.append({**dict(zip(groups, cell)), "metric": metric, "runs": len(group),
                         "networks": group["network_seed"].nunique(), "observed": observed,
                         "non_events": len(group) - observed if metric in EVENT_TIMES else 0,
                         "estimand": "mean_given_event" if metric in EVENT_TIMES else "unconditional_mean",
                         "mean": mean, "ci95_low": lo, "ci95_high": hi})
    return pd.DataFrame(rows)


def policy_diagnostics(df: pd.DataFrame, *, prefixes: tuple[int, ...] = (5, 10, 20)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Coverage and conditional MC error for fixed seed-order prefixes; no outcome-based seed selection.

    A policy draw is reused across epidemics. MC variance is therefore computed from policy-level epidemic
    means within each network, not by treating policy×epidemic rows as independent. The global conditional
    variance is sum(s_n**2 / m) / N**2, since policy schedules are independent between networks.
    """
    random = df[df["strategy"].eq("random")].copy()
    random["policy_slot"] = random["policy_seed"] - (50000 + 20 * (random["network_seed"] - 200))
    coverage, stability = [], []
    for prefix in prefixes:
        part = random[random["policy_slot"] < prefix]
        for network, group in part.groupby("network_seed", sort=True):
            draws = group[["policy_seed", "selected_tanks"]].drop_duplicates().sort_values("policy_seed")
            if len(draws) != prefix:
                raise ValueError(f"policy prefix {prefix} incomplete in network {network}")
            pairs = [_pair(value) for value in draws["selected_tanks"]]
            same = sum(a // 5 == b // 5 for a, b in pairs)
            coverage.append({"network_seed": network, "policy_prefix": prefix, "draws": len(pairs),
                             "unique_pairs": len(set(pairs)), "duplicate_pair_draws": len(pairs) - len(set(pairs)),
                             "same_region_draws": same, "same_region_share": same / len(pairs),
                             **{f"draws_covering_region_{region}": sum(any(t // 5 == region for t in pair) for pair in pairs)
                                for region in range(4)},
                             "pairs": json.dumps(pairs)})
        policy_means = part.groupby([*CELL, "network_seed", "policy_seed"], as_index=False)[list(PRIMARY)].mean()
        target = df[df["strategy"].eq("betweenness")].groupby(list(CELL))[list(PRIMARY)].mean()
        for cell, group in policy_means.groupby(list(CELL), sort=True):
            for metric in PRIMARY:
                by_network = group.groupby("network_seed")[metric]
                count = by_network.size()
                n = len(count)
                mcse = float(np.sqrt((by_network.var(ddof=1) / count).sum()) / n)
                random_mean = float(group[metric].mean())
                targeted_mean = float(target.loc[cell, metric])
                stability.append({**dict(zip(CELL, cell)), "metric": metric, "policy_prefix": prefix,
                                  "networks": n, "mean_random": random_mean, "mean_targeted": targeted_mean,
                                  "mean_diff": targeted_mean - random_mean, "conditional_policy_mcse": mcse,
                                  "conditional_mcse_scope": "recorded networks and epidemic draws fixed"})
    return pd.DataFrame(coverage), pd.DataFrame(stability)


def verify_formal_replay(formal: pd.DataFrame, followup: pd.DataFrame) -> dict:
    """Check repeated historical conditions after design validation; never edits either dataset."""
    keys = ["network_seed", "epidemic_seed", "transfer_rate", "strategy", "response_delay", "quarantine_duration"]
    def repeated(frame):
        return frame[frame["transfer_rate"].eq(0.025) & (
            frame["strategy"].eq("none") | (frame["strategy"].eq("betweenness") & frame["quarantine_duration"].eq(14)))]
    left, right = repeated(formal), repeated(followup)
    columns = sorted((set(left) & set(right)) - set(keys) - {"run_id", "configuration_hash", "code_commit", "label"})
    joined = left.merge(right, on=keys, how="outer", suffixes=("_formal", "_followup"),
                        validate="one_to_one", indicator=True)
    if not len(joined) or not joined["_merge"].eq("both").all():
        raise ValueError("formal replay has missing/unmatched conditions")
    mismatches = []
    for column in columns:
        a, b = joined[f"{column}_formal"], joined[f"{column}_followup"]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            equal = np.isclose(a, b, rtol=0, atol=1e-12, equal_nan=True)
        else:
            equal = a.eq(b) | (a.isna() & b.isna())
        if not np.all(equal):
            mismatches.append(column)
    if mismatches:
        raise ValueError(f"formal replay differs in columns: {mismatches}")
    return {"passed": True, "matched_runs": len(joined), "compared_columns": columns,
            "numeric_absolute_tolerance": 1e-12, "excluded_metadata": ["run_id", "configuration_hash", "code_commit", "label"]}


def analyse_followup(summary: pd.DataFrame, *, n_boot: int = 2000, seed: int = 0,
                     **validation_kwargs) -> dict[str, pd.DataFrame]:
    """Validate the specified study and return analysis tables, with no I/O or model execution."""
    df = validate_runs(summary, followup=True, **validation_kwargs)
    metrics = PRIMARY + OBSERVATION_COUNTS + EVENT_INDICATORS
    coverage, stability = policy_diagnostics(df)
    return {
        "strategy-effects": paired_contrasts(df, axis="strategy", metrics=metrics, n_boot=n_boot, seed=seed),
        "delay-effects": paired_contrasts(df, axis="response_delay", metrics=metrics, n_boot=n_boot, seed=seed),
        "duration-effects": paired_contrasts(df, axis="quarantine_duration", metrics=metrics, n_boot=n_boot, seed=seed),
        "condition-summary": condition_summary(df, n_boot=n_boot, seed=seed),
        "policy-coverage": coverage,
        "policy-stability": stability,
    }
