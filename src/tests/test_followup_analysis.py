"""Deterministic synthetic-table tests: no model execution and no dependence on study outcomes."""

import itertools
import json

import numpy as np
import pandas as pd
import pytest

from turtlefarm.followup_analysis import (
    analyse_followup, condition_summary, formal_delay_effects, paired_contrasts,
    policy_diagnostics, validate_runs, verify_formal_replay,
)

SMALL = dict(network_seeds=(200, 201), epidemics_per_network=2)


def fixture_rows(followup=True):
    rows = []
    rates = (0.025,) if followup else (0.0, 0.01, 0.025, 0.1)
    for network, offset, rate in itertools.product((200, 201), range(2), rates):
        base = dict(network_seed=network, epidemic_seed=20000 + 5 * (network - 200) + offset,
                    transfer_rate=rate, beta=0.2, gamma=0.1, capacity=12, k=2,
                    network_hash=f"hash-{network}", status="completed", days_simulated=100,
                    p_in=0.6, p_out=0.05, max_days=365, protocol_hash="a" * 64,
                    observation_schema_version="turtlefarm.observation.v1", code_commit="fixture-commit",
                    final_attack_rate=0.3 + offset * 0.02 + (network - 200) * 0.01,
                    affected_tanks=6, first_infectious_arrival=np.nan,
                    first_local_secondary_infection=np.nan, infectious_cross_region_transfers=0,
                    regions_visited_by_I=1, regions_with_local_transmission=1,
                    local_infections_outside_initial_region=0)
        rows.append(dict(base, strategy="none", response_delay=0, quarantine_duration=0,
                         policy_seed=np.nan, selected_tanks=np.nan))
        for duration, delay in itertools.product((7, 14, 28) if followup else (14,), (1, 12, 33)):
            common = dict(base, quarantine_duration=duration, response_delay=delay)
            common["final_attack_rate"] += 0.001 * delay - 0.001 * duration
            rows.append(dict(common, strategy="betweenness", policy_seed=np.nan, selected_tanks="0,5",
                             final_attack_rate=common["final_attack_rate"] - 0.03))
            for slot in range(20 if followup else 3):
                seed = 50000 + 20 * (network - 200) + slot if followup else 1000 + slot
                # Repeated pairs are intentional: different seed draws need not yield different pairs.
                rows.append(dict(common, strategy="random", policy_seed=seed,
                                 selected_tanks=f"{slot % 4},{5 + slot % 4}",
                                 final_attack_rate=common["final_attack_rate"] + 0.001 * slot))
    return pd.DataFrame(rows)


@pytest.fixture
def checked():
    return validate_runs(fixture_rows(), followup=True, **SMALL)


def test_complete_grid_and_original_input_unchanged():
    source = fixture_rows()
    before = source.copy(deep=True)
    result = validate_runs(source, followup=True, **SMALL)
    assert len(result) == 4 * (1 + 9 * 21)
    assert result["infectious_arrival_observed"].sum() == 0
    pd.testing.assert_frame_equal(source, before)


@pytest.mark.parametrize("change,match", [
    (lambda df: df.iloc[:-1], "missing"),
    (lambda df: pd.concat([df, df.iloc[[0]]]), "duplicate"),
    (lambda df: df.assign(capacity=16), "fixed capacity"),
    (lambda df: df.assign(gamma=0.2), "fixed gamma"),
    (lambda df: df.assign(status="censored"), "completed"),
    (lambda df: df.drop(columns="capacity"), "missing columns"),
    (lambda df: df.assign(final_attack_rate=np.nan), "outcome"),
    (lambda df: df.assign(first_infectious_arrival=0), "event time"),
    (lambda df: df.assign(first_infectious_arrival=101), "event after"),
    (lambda df: df.assign(first_infectious_arrival="not a day"), "event time"),
    (lambda df: df.assign(regions_visited_by_I=5), "region count"),
    (lambda df: df.assign(p_out=0.1), "fixed p_out"),
    (lambda df: df.assign(protocol_hash="bad"), "protocol_hash"),
    (lambda df: df.assign(observation_schema_version="unknown"), "observation_schema"),
    (lambda df: df.assign(first_infectious_arrival=1), "arrival event"),
])
def test_rejects_incomplete_mixed_or_invalid_data(change, match):
    with pytest.raises(ValueError, match=match):
        validate_runs(change(fixture_rows()), followup=True, **SMALL)


def test_wrong_policy_schedule_and_changed_pair_rejected():
    df = fixture_rows()
    random = df["strategy"].eq("random")
    df.loc[random, "policy_seed"] += 1000
    with pytest.raises(ValueError, match="unexpected"):
        validate_runs(df, followup=True, **SMALL)
    df = fixture_rows()
    df.loc[df.index[df["strategy"].eq("random")][0], "selected_tanks"] = "1,2"
    with pytest.raises(ValueError, match="reused"):
        validate_runs(df, followup=True, **SMALL)


def test_mismatched_network_hash_rejected():
    df = fixture_rows()
    df.loc[0, "network_hash"] = "other"
    with pytest.raises(ValueError, match="network_hash"):
        validate_runs(df, followup=True, **SMALL)


def test_strategy_difference_is_random_policy_mean_per_block(checked):
    effects = paired_contrasts(checked, axis="strategy", n_boot=50, seed=13)
    ar = effects[effects.metric.eq("final_attack_rate")]
    assert len(ar) == 9
    assert set(ar["quarantine_duration"]) == {7, 14, 28}
    assert ar["blocks"].eq(4).all()  # not 80 independent policy×epidemic rows
    assert np.allclose(ar["mean_diff"], -0.0395)
    assert np.allclose(ar["ci95_low"], -0.0395)
    assert np.allclose(ar["ci95_high"], -0.0395)


def test_delay_and_duration_signs_and_matching(checked):
    delay = paired_contrasts(checked, axis="response_delay", n_boot=30, seed=2)
    duration = paired_contrasts(checked, axis="quarantine_duration", n_boot=30, seed=2)
    for table, axis, sign in ((delay, "response_delay", 1), (duration, "quarantine_duration", -1)):
        ar = table[table.metric.eq("final_attack_rate")]
        want = sign * 0.001 * (ar[f"{axis}_left"] - ar[f"{axis}_right"])
        assert np.allclose(ar["mean_diff"], want)
        assert ar["blocks"].eq(4).all()
    # A contrast API cannot quietly inner-join away a missing block.
    incomplete = checked.drop(checked.index[checked.strategy.eq("betweenness")][0])
    with pytest.raises(ValueError, match="unmatched"):
        paired_contrasts(incomplete, axis="response_delay", n_boot=10, seed=2)


def test_formal_delays_include_nonstarted_blocks_and_all_nonzero_rates():
    df = fixture_rows(followup=False).drop(columns="capacity")
    df["intervention_start_day"] = np.nan
    result = formal_delay_effects(df, n_boot=20, seed=2, **SMALL)
    assert len(result) == 3 * 3 * 2 * 2
    assert set(result.transfer_rate) == {0.01, 0.025, 0.1}
    assert result.blocks.eq(4).all()
    assert set(result.contrast) == {"12-1", "33-1", "33-12"}


def test_non_events_not_zero_and_event_incidence_reported(checked):
    checked.loc[checked.index[0], "first_infectious_arrival"] = 10
    checked.loc[checked.index[0], "infectious_arrival_observed"] = 1
    table = condition_summary(checked, n_boot=40, seed=3)
    none = table[table.strategy.eq("none")].set_index("metric")
    assert none.loc["first_infectious_arrival", "mean"] == 10
    assert none.loc["first_infectious_arrival", "non_events"] == 3
    assert none.loc["first_infectious_arrival", "estimand"] == "mean_given_event"
    assert none.loc["infectious_arrival_observed", "mean"] == 0.25
    assert np.isnan(none.loc["first_local_secondary_infection", "mean"])
    assert np.isnan(none.loc["first_local_secondary_infection", "ci95_low"])


def test_policy_prefix_coverage_duplicates_and_conditional_mcse(checked):
    coverage, stability = policy_diagnostics(checked)
    assert len(coverage) == 6
    assert coverage[coverage.policy_prefix.eq(20)].unique_pairs.eq(4).all()
    assert coverage[coverage.policy_prefix.eq(20)].duplicate_pair_draws.eq(16).all()
    assert coverage.same_region_draws.eq(0).all()
    assert coverage.draws_covering_region_0.eq(coverage.draws).all()
    assert coverage.draws_covering_region_3.eq(0).all()
    assert set(stability.policy_prefix) == {5, 10, 20}
    for prefix in (5, 10, 20):
        ar = stability[stability.metric.eq("final_attack_rate") & stability.policy_prefix.eq(prefix)]
        expected_mcse = np.std(np.arange(prefix) * 0.001, ddof=1) / np.sqrt(prefix * 2)
        assert np.allclose(ar.conditional_policy_mcse, expected_mcse)
        assert np.allclose(ar.mean_diff, -0.03 - 0.001 * (prefix - 1) / 2)


def test_bootstrap_reproducible_and_analysis_tables_keep_factors():
    first = analyse_followup(fixture_rows(), n_boot=25, seed=91, **SMALL)
    second = analyse_followup(fixture_rows(), n_boot=25, seed=91, **SMALL)
    assert set(first) == {"strategy-effects", "delay-effects", "duration-effects", "condition-summary",
                          "policy-coverage", "policy-stability"}
    for key in first:
        pd.testing.assert_frame_equal(first[key], second[key])
    for key in ("strategy-effects", "delay-effects", "duration-effects", "condition-summary"):
        assert {"beta", "gamma", "capacity", "k", "transfer_rate"} <= set(first[key])


def test_seed_and_bootstrap_count_validation(checked):
    for kwargs in ({"n_boot": 0}, {"seed": -1}):
        with pytest.raises(ValueError, match="n_boot"):
            paired_contrasts(checked, axis="strategy", **kwargs)


def test_expected_protocol_hash_and_replay_guard():
    with pytest.raises(ValueError, match="supplied design"):
        validate_runs(fixture_rows(), followup=True, expected_protocol_hash="b" * 64, **SMALL)
    formal, followup = fixture_rows(False), fixture_rows()
    result = verify_formal_replay(formal, followup)
    assert result["matched_runs"] == 16
    followup.loc[0, "final_attack_rate"] += 0.01
    with pytest.raises(ValueError, match="final_attack_rate"):
        verify_formal_replay(formal, followup)


def test_network_bootstrap_resamples_clusters_not_individual_epidemics(checked):
    targeted = checked.strategy.eq("betweenness") & checked.network_seed.eq(201)
    checked.loc[targeted, "final_attack_rate"] += 0.04
    result = paired_contrasts(checked, axis="strategy", n_boot=200, seed=83)
    row = result[result.metric.eq("final_attack_rate")].iloc[0]
    picked = np.random.default_rng(83).integers(0, 2, size=(200, 2))
    draws = np.array([-0.0395, 0.0005])[picked].mean(axis=1)
    assert row.mean_diff == pytest.approx(-0.0195)
    assert row.ci95_low == pytest.approx(np.percentile(draws, 2.5))
    assert row.ci95_high == pytest.approx(np.percentile(draws, 97.5))


def test_cli_writes_tables_figure_provenance_without_changing_inputs(tmp_path, monkeypatch):
    from utils import analyse_followup as cli
    from turtlefarm.runner import configuration_hash
    design = {"fixture": "analysis only"}
    formal = fixture_rows(False).drop(columns=["protocol_hash", "observation_schema_version"])
    followup = fixture_rows().assign(protocol_hash=configuration_hash(design))
    formal_path, followup_path = tmp_path / "formal.csv", tmp_path / "followup.csv"
    design_path, output = tmp_path / "design.json", tmp_path / "analysis"
    formal.to_csv(formal_path, index=False)
    followup.to_csv(followup_path, index=False)
    design_path.write_text(json.dumps(design))
    before = [path.read_bytes() for path in (formal_path, followup_path, design_path)]
    original_analysis, original_formal = cli.analyse_followup, cli.formal_delay_effects
    monkeypatch.setattr(cli, "analyse_followup", lambda frame, **kwargs: original_analysis(frame, **SMALL, **kwargs))
    monkeypatch.setattr(cli, "formal_delay_effects", lambda frame, **kwargs: original_formal(frame, **SMALL, **kwargs))
    assert cli.main(["--formal", str(formal_path), "--followup", str(followup_path), "--design", str(design_path),
                     "--output", str(output), "--n-boot", "20", "--boot-seed", "11"]) == 0
    assert len(list(output.glob("*.csv"))) == 7
    assert (output / "fig-strategy-effects.png").stat().st_size > 1000
    metadata = json.loads((output / "analysis-summary.json").read_text())
    assert metadata["bootstrap"]["seed"] == 11
    assert metadata["formal_replay"]["matched_runs"] == 16
    assert metadata["validation"]["passed"]
    assert metadata["protocol"]["configuration_hash"] == configuration_hash(design)
    receipts = metadata["analysis_code"]["files"]
    assert {receipt["path"] for receipt in receipts} == {
        "utils/analyse_followup.py", "src/turtlefarm/followup_analysis.py"}
    assert all(len(receipt["sha256"]) == 64 for receipt in receipts)
    assert "HEAD context only" in metadata["analysis_code"]["revision_scope"]
    assert before == [path.read_bytes() for path in (formal_path, followup_path, design_path)]
