"""Pilot selection rules and paired analysis (docs/pilot-protocol.md; experiment-plan sections 6, 12).

The pilot tests use hand-built summary rows, never real pilot output, so no pilot outcome is seen here.
"""

import itertools

import numpy as np
import pandas as pd
import pytest

from turtlefarm.analysis import (
    baseline_differences,
    baseline_effect_table,
    condition_summary,
    cluster_bootstrap_ci,
    delay_levels,
    evaluate_stage1,
    evaluate_stage2,
    paired_differences,
    paired_effect_table,
    outbreak_class,
    pick_representative_runs,
    pick_triple,
    relative_reduction,
    round_half_up,
    select_duration,
    select_stage1,
    stage2_design,
)
from turtlefarm.runner import ExperimentDesign, flatten, iter_raw, run_design

LEVELS = (0.0, 0.01, 0.02, 0.05, 0.1)
# per level: (median-ish attack rate, affected tanks, accepted transfers per day)
GOOD_REGIME = {0.0: (0.05, 1, 0), 0.01: (0.3, 3, 2), 0.02: (0.5, 6, 4), 0.05: (0.7, 10, 9), 0.1: (0.8, 14, 20)}


def _stage1_rows(beta=0.1, gamma=0.1, regime=GOOD_REGIME, n=10, **override):
    rows = []
    for rate, seed in itertools.product(LEVELS, range(n)):
        ar, tanks, per_day = regime[rate]
        row = dict(
            beta=beta, gamma=gamma, strategy="none", transfer_rate=rate, network_seed=seed % 2, epidemic_seed=seed,
            status="completed", final_attack_rate=ar, affected_tanks=tanks, days_simulated=100,
            accepted_transfers=per_day * 100, attempted_transfers=per_day * 100 + 1, blocked_transfers=1,
        )
        row.update(override)
        rows.append(row)
    return rows


def test_good_candidate_passes_all_stage1_criteria():
    (result,) = evaluate_stage1(pd.DataFrame(_stage1_rows()))
    assert result.passed, result.checks
    assert (0.01, 0.02, 0.05) in result.triples


def test_s1_violation_fails_candidate():
    rows = _stage1_rows()
    rows[0]["affected_tanks"] = 2  # transfer_rate 0 but infection reached a second tank: a bug
    (result,) = evaluate_stage1(pd.DataFrame(rows))
    assert not result.checks["S1_zero_transfer_one_tank"]


def test_saturated_regime_fails_s4():
    saturated = {rate: (0.95, t, d) for rate, (_, t, d) in GOOD_REGIME.items()}
    (result,) = evaluate_stage1(pd.DataFrame(_stage1_rows(regime=saturated)))
    assert not result.checks["S4_lowest_level_median_ar_le_0_90"]


def test_any_failed_run_fails_s2():
    rows = _stage1_rows()
    rows[3]["status"] = "failed"
    (result,) = evaluate_stage1(pd.DataFrame(rows))
    assert not result.checks["S2_no_failed_censored_le_1pct"]


def test_stage1_refuses_intervention_runs():
    rows = _stage1_rows()
    rows[0]["strategy"] = "random"
    with pytest.raises(ValueError, match="no-intervention"):
        evaluate_stage1(pd.DataFrame(rows))


def test_rule3_picks_widest_span_then_smaller_middle_level():
    assert pick_triple([(0.01, 0.02, 0.1), (0.01, 0.05, 0.1), (0.02, 0.05, 0.1)]) == (0.01, 0.02, 0.1)
    assert pick_triple([(0.01, 0.02, 0.05), (0.02, 0.05, 0.1)]) == (0.02, 0.05, 0.1)
    assert pick_triple([]) is None
    summary = pd.DataFrame(_stage1_rows())
    selection = select_stage1(summary, evaluate_stage1(summary))
    assert selection.ambiguities == [] and selection.transfer_rates == (0.0, 0.01, 0.02, 0.1)


def test_rule2_prefers_middle_attack_rate_near_half():
    far = {rate: (min(ar + 0.15, 0.85), t, d) for rate, (ar, t, d) in GOOD_REGIME.items()}
    summary = pd.DataFrame(_stage1_rows(beta=0.2, regime=far) + _stage1_rows(beta=0.1))
    selection = select_stage1(summary, evaluate_stage1(summary))
    assert (selection.beta, selection.ambiguities) == (0.1, [])


def test_no_passing_candidate_stops():
    summary = pd.DataFrame(_stage1_rows(status="failed"))
    selection = select_stage1(summary, evaluate_stage1(summary))
    assert selection.beta is None and selection.ambiguities


def _raw(rate, attack_rate, second_tank_day, peak_day, beta=0.1, gamma=0.1):
    daily = [{"day": d, "affected_tanks_ever": 1 if second_tank_day is None or d < second_tank_day else 2} for d in range(40)]
    return {
        "config": {"beta": beta, "gamma": gamma, "transfer_rate": rate}, "status": "completed", "daily": daily,
        "metrics": {"final_attack_rate": attack_rate, "time_to_peak": peak_day},
    }


def test_delay_levels_use_non_minor_runs_at_middle_level_only():
    raws = [
        _raw(0.02, 0.5, 4, 20), _raw(0.02, 0.4, 6, 30), _raw(0.02, 0.6, 5, 25),
        _raw(0.02, 0.05, None, 2),  # minor outbreak: excluded
        _raw(0.05, 0.9, 1, 3),  # other level: excluded
    ]
    out = delay_levels(raws, 0.1, 0.1, 0.02)
    assert out["levels"] == (1, 5, 25) and out["non_minor_runs"] == 3


def test_indistinguishable_delays_are_invalid():
    out = delay_levels([_raw(0.02, 0.5, 9, 8)], 0.1, 0.1, 0.02)
    assert not out["valid"] and out["levels"] is None


def test_round_half_up():
    assert [round_half_up(x) for x in (2.5, 3.5, 4.49)] == [3, 4, 4]


def test_stage2_design_is_a_valid_runner_design():
    summary = pd.DataFrame(_stage1_rows())
    selection = select_stage1(summary, evaluate_stage1(summary))
    stage1 = {"network_seeds": [100, 101], "epidemic_seeds": [9000], "fixed": {"p_in": 0.6, "p_out": 0.05}}
    design = ExperimentDesign.from_dict(stage2_design(selection, (1, 5, 25), stage1))
    assert design.transfer_rates == (0.01, 0.02, 0.1)
    assert design.fixed == {"p_in": 0.6, "p_out": 0.05, "beta": 0.1, "gamma": 0.1}
    assert design.sweep == {"quarantine_duration": (7, 14, 21)}
    # per block: 1 baseline + 3 D x 3 delays x (1 betweenness + 3 random)
    assert len(design.configs()) == 2 * 1 * 3 * (1 + 3 * 3 * 4)


def test_stage2_selects_smallest_passing_duration():
    rows = [dict(strategy="none", status="completed", gamma=0.1, quarantine_duration=0, blocked_transfers=0,
                 time_to_extinction=100, intervention_start_day=np.nan)]
    for d, blocked in ((7, 5), (14, 5), (21, 5), (28, 5)):
        rows += [dict(strategy=s, status="completed", gamma=0.1, quarantine_duration=d, blocked_transfers=blocked,
                      time_to_extinction=np.nan, intervention_start_day=1) for s in ("random", "betweenness")]
    table = evaluate_stage2(pd.DataFrame(rows))
    # Q3 needs D >= 1/gamma = 10, Q2 needs D <= 25
    assert table.set_index("quarantine_duration")["passed"].to_dict() == {7: False, 14: True, 21: True, 28: False}
    assert select_duration(table) == 14


def _formal_rows():
    rows = []
    for net, epi in itertools.product(range(3), range(4)):
        common = dict(network_seed=net, epidemic_seed=epi, transfer_rate=0.05, quarantine_duration=14, status="completed")
        rows.append(dict(common, strategy="none", response_delay=0, final_attack_rate=0.6, affected_tanks=10))
        start = np.nan if epi == 3 else 5.0  # epidemic seed 3 dies out before the response day
        rows.append(dict(common, strategy="betweenness", response_delay=5, final_attack_rate=0.3, affected_tanks=4,
                         intervention_start_day=start))
        for policy_seed, ar in ((1, 0.4), (2, 0.6)):
            rows.append(dict(common, strategy="random", response_delay=5, policy_seed=policy_seed,
                             final_attack_rate=ar, affected_tanks=6, intervention_start_day=start))
    return pd.DataFrame(rows)


def test_paired_difference_averages_random_policy_seeds_per_block():
    diffs = paired_differences(_formal_rows())
    assert len(diffs) == 12
    assert np.allclose(diffs["diff_final_attack_rate"], 0.3 - 0.5)
    assert "rel_reduction_affected_tanks" not in diffs  # per-block ratios are not reported


def test_failed_arm_drops_whole_block():
    df = _formal_rows()
    df.loc[(df["strategy"] == "random") & (df["epidemic_seed"] == 0) & (df["network_seed"] == 0), "status"] = "failed"
    diffs = paired_differences(df)
    assert len(diffs) == 11 and diffs.attrs["dropped_blocks"] == 1


def test_cluster_bootstrap_resamples_networks():
    df = pd.DataFrame({"network_seed": [0, 0, 1, 1, 2, 2], "x": [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]})
    point, low, high = cluster_bootstrap_ci(df, "x", n_boot=500)
    assert point == 2.0 and 1.0 <= low <= point <= high <= 3.0
    constant = cluster_bootstrap_ci(df.assign(x=1.0), "x", n_boot=50)
    assert constant == (1.0, 1.0, 1.0)


def test_effect_table_and_condition_summary_shapes():
    effects = paired_effect_table(paired_differences(_formal_rows()), n_boot=100)
    assert set(effects["metric"]) == {"final_attack_rate", "affected_tanks"}
    blocks = effects.groupby("subset")["blocks"].first().to_dict()
    assert blocks == {"all_blocks": 12, "quarantine_started": 9}
    assert (effects["share_targeted_better"] == 1.0).all()
    cond = condition_summary(_formal_rows(), metrics=("final_attack_rate",))
    baseline = cond[cond["strategy"] == "none"]
    assert len(baseline) == 1 and pd.isna(baseline["response_delay"].iloc[0])


def test_analysis_runs_on_real_runner_output(tmp_path):
    design = ExperimentDesign(
        name="analysis-e2e", transfer_rates=(0.0, 0.05), response_delays=(1, 5), network_seeds=(0, 1),
        epidemic_seeds=(7,), policy_seeds=(3, 4), fixed=dict(beta=0.2, gamma=0.2, quarantine_duration=4, max_days=60),
    )
    raw_path = tmp_path / "raw.jsonl"
    run_design(design, raw_path)
    summary = pd.DataFrame([flatten(r) for r in iter_raw(raw_path)])
    diffs = paired_differences(summary)
    assert len(diffs) == 2 * 2 * 2  # networks x transfer rates x delays
    assert not paired_effect_table(diffs, n_boot=50).empty
    assert not condition_summary(summary).empty


def test_q1_counts_only_runs_whose_quarantine_started():
    rows = [dict(strategy="none", status="completed", gamma=0.1, quarantine_duration=0, blocked_transfers=0,
                 time_to_extinction=100, intervention_start_day=np.nan)]
    # 8 started runs that all block, 2 runs that went extinct before the response day
    rows += [dict(strategy="random", status="completed", gamma=0.1, quarantine_duration=14, blocked_transfers=3,
                  time_to_extinction=np.nan, intervention_start_day=12)] * 8
    rows += [dict(strategy="betweenness", status="completed", gamma=0.1, quarantine_duration=14, blocked_transfers=0,
                  time_to_extinction=5, intervention_start_day=np.nan)] * 2
    (row,) = evaluate_stage2(pd.DataFrame(rows)).to_dict("records")
    assert row["share_blocked_ge_1_all_runs"] == 0.8 and not row["Q1_original_all_runs"]
    assert row["share_blocked_ge_1_started"] == 1.0 and row["Q1_quarantine_not_noop"]
    assert row["passed"] and not row["passed_original_q1"]


def test_relative_reduction_is_a_ratio_of_means_not_a_mean_of_ratios():
    # block 0: random 0.01 -> 0.03 (per-block ratio -200%); block 1: random 0.5 -> 0.3 (+40%)
    diffs = pd.DataFrame({
        "network_seed": [0, 1], "x_targeted": [0.03, 0.3], "x_random": [0.01, 0.5],
    }).assign(diff_x=lambda d: d.x_targeted - d.x_random)
    assert np.isclose(relative_reduction(diffs, "x"), 1 - 0.33 / 0.51)
    assert np.isnan(relative_reduction(diffs.assign(x_random=0.0), "x"))


def test_effect_table_relative_reduction_agrees_with_mean_diff():
    effects = paired_effect_table(paired_differences(_formal_rows()), n_boot=100)
    row = effects[(effects.subset == "all_blocks") & (effects.metric == "affected_tanks")].iloc[0]
    assert np.isclose(row.rel_reduction, -row.mean_diff / row.mean_random)
    assert np.isclose(row.rel_reduction, 1 - 4 / 6)
    assert row.rel_reduction_ci95_low <= row.rel_reduction <= row.rel_reduction_ci95_high


def _run_record(network_seed, epidemic_seed, attack_rate, infected_regions, rate=0.025, strategy="none"):
    regions = [t // 5 for t in range(20)]
    tanks = [{"tank_id": t, "region_id": regions[t], "I": int(regions[t] in infected_regions and t % 5 == 0)} for t in range(20)]
    return {
        "config": {"strategy": strategy, "transfer_rate": rate, "network_seed": network_seed, "epidemic_seed": epidemic_seed},
        "status": "completed", "network": {"regions": regions}, "initial_infected_tanks": [0],
        "daily": [{"tanks": tanks}], "metrics": {"final_attack_rate": attack_rate},
    }


def test_outbreak_class_uses_initial_region():
    assert outbreak_class(_run_record(0, 0, 0.05, {0})) == "local"
    assert outbreak_class(_run_record(0, 0, 0.5, {0, 2})) == "cross_region"


def test_representative_run_is_closest_to_class_median_with_seed_tie_break():
    raws = [
        _run_record(1, 1, 0.04, {0}), _run_record(0, 2, 0.06, {0}), _run_record(0, 1, 0.06, {0}),
        _run_record(2, 1, 0.30, {0, 1}), _run_record(2, 2, 0.50, {0, 1}), _run_record(2, 3, 0.90, {0, 3}),
        _run_record(9, 9, 0.50, {0, 1}, rate=0.1), _run_record(9, 8, 0.50, {0, 1}, strategy="random"),
    ]
    picked = pick_representative_runs(raws)
    assert picked["local"]["class_size"] == 3 and picked["local"]["class_median"] == 0.06
    assert (picked["local"]["raw"]["config"]["network_seed"], picked["local"]["raw"]["config"]["epidemic_seed"]) == (0, 1)
    assert picked["cross_region"]["raw"]["config"]["epidemic_seed"] == 2


def test_baseline_differences_pair_each_arm_with_its_block_baseline():
    diffs = baseline_differences(_formal_rows())
    assert set(diffs["strategy"]) == {"betweenness", "random"} and len(diffs) == 24
    targeted = diffs[diffs["strategy"] == "betweenness"]
    assert np.allclose(targeted["diff_final_attack_rate"], 0.3 - 0.6)
    random = diffs[diffs["strategy"] == "random"]
    assert np.allclose(random["diff_affected_tanks"], 6 - 10)
    table = baseline_effect_table(diffs, n_boot=50)
    row = table[(table.strategy == "betweenness") & (table.metric == "final_attack_rate")].iloc[0]
    assert np.isclose(row.rel_reduction, 0.5) and row.blocks == 12


def test_float_noise_counts_as_a_tie_not_a_win():
    df = _formal_rows()
    # make every arm identical, then perturb the random mean by floating-point noise only
    df["final_attack_rate"] = 0.1
    df.loc[df["strategy"] == "random", "final_attack_rate"] = [0.1 + 1e-17, 0.1 - 1e-17] * (len(df[df.strategy == "random"]) // 2)
    effects = paired_effect_table(paired_differences(df), metrics=("final_attack_rate",), n_boot=20)
    assert (effects["share_targeted_better"] == 0).all() and (effects["share_tied"] == 1).all()


def test_missing_random_seed_or_targeted_arm_is_reported():
    df = _formal_rows()
    assert paired_differences(df).attrs["incomplete_blocks"] == 0
    drop_seed = df.index[(df.strategy == "random") & (df.policy_seed == 2) & (df.epidemic_seed == 0) & (df.network_seed == 0)]
    assert paired_differences(df.drop(drop_seed)).attrs["incomplete_blocks"] == 1
    drop_arm = df.index[(df.strategy == "betweenness") & (df.epidemic_seed == 1) & (df.network_seed == 1)]
    assert paired_differences(df.drop(drop_arm)).attrs["incomplete_blocks"] == 1


def test_condition_summary_ci_resamples_networks_and_stays_in_range():
    df = _formal_rows()
    # networks 0, 1, 2 have different mean attack rates, all close to the upper bound of 1
    df.loc[df["strategy"] == "none", "final_attack_rate"] = [1.0] * 4 + [1.0, 0.9, 1.0, 1.0] + [0.9] * 4
    cond = condition_summary(df, metrics=("final_attack_rate",), n_boot=200)
    base = cond[cond["strategy"] == "none"].iloc[0]
    assert base["ci95_high"] <= 1.0 + 1e-12
    assert base["ci95_low"] - 1e-12 <= base["mean"] <= base["ci95_high"] + 1e-12
    assert base["ci95_low"] < base["ci95_high"]  # networks differ, so the interval is not degenerate
