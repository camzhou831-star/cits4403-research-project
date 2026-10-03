"""Batch-runner tests (experiment-plan sections 3, 6, 10, 11, 16; docs/run-result-schema.md)."""

import json
from dataclasses import replace

import pytest

from turtlefarm import SimulationConfig, run_baseline
from turtlefarm.config import ConfigError
from turtlefarm.model import InvariantError, Simulation
from turtlefarm.runner import (
    SCHEMA_VERSION,
    BatchHalted,
    ExperimentDesign,
    configuration_hash,
    flatten,
    iter_raw,
    run_design,
    to_raw_record,
)

TOP_LEVEL_FIELDS = {
    "schema_version", "run_id", "timestamp_utc", "code_commit", "configuration_hash", "config", "seeds",
    "network", "initial_infected_agents", "initial_infected_tanks", "selected_tanks",
    "intervention_start_day", "intervention_duration_days", "intervention_cost", "status", "stop_reason",
    "error", "daily", "metrics", "transitions",
}


def _design(**overrides) -> ExperimentDesign:
    values = dict(
        name="unit-test",
        transfer_rates=(0.0, 0.05),
        response_delays=(1, 5),
        network_seeds=(0,),
        epidemic_seeds=(7, 8),
        policy_seeds=(3,),
        fixed=dict(beta=0.2, gamma=0.2, quarantine_duration=4, max_days=60),
    )
    values.update(overrides)
    return ExperimentDesign(**values)


def test_design_expands_to_shared_baseline_plus_delay_by_strategy_cells():
    design = _design(policy_seeds=(3, 4))
    configs = design.configs()

    # per block: 1 baseline + 2 delays x (1 betweenness + 2 random policy seeds)
    assert len(configs) == 1 * 2 * 2 * (1 + 2 * (1 + 2))
    block = [c for c in configs if (c.epidemic_seed, c.transfer_rate) == (7, 0.05)]
    assert [c.strategy for c in block].count("none") == 1
    assert {(c.strategy, c.response_delay, c.policy_seed) for c in block if c.strategy != "none"} == {
        ("betweenness", 1, None), ("betweenness", 5, None),
        ("random", 1, 3), ("random", 1, 4), ("random", 5, 3), ("random", 5, 4),
    }
    assert len({configuration_hash(c.to_dict()) for c in configs}) == len(configs)


def test_random_and_targeted_share_budget_and_block_key():
    for delay in (1, 5):
        cell = [c for c in _design().configs() if c.strategy != "none" and c.response_delay == delay]
        assert len({(c.k, c.quarantine_duration) for c in cell}) == 1
    assert all(c.design == "main" and c.label == "unit-test" for c in _design().configs())


@pytest.mark.parametrize(
    "overrides,match",
    [
        (dict(name=""), "name"),
        (dict(transfer_rates=()), "transfer_rates must be non-empty"),
        (dict(epidemic_seeds=(1, 1)), "duplicates"),
        (dict(fixed=dict(design="scenario")), "fixed may only set"),
        (dict(fixed=dict(n_tanks=5)), "fixed may only set"),
        (dict(fixed=dict(strategy="none")), "fixed may only set"),
        (dict(sweep=dict(transfer_rate=(0.1,))), "sweep may only set"),
        (dict(sweep=dict(beta=(0.1, 0.1))), "duplicates"),
        (dict(sweep=dict(beta=())), "at least one level"),
        (dict(sweep=dict(beta=(0.1, 0.3))), "both fixed and swept"),
        (dict(policy_seeds=()), "both be given, or both be empty"),
    ],
)
def test_invalid_designs_are_refused(overrides, match):
    with pytest.raises(ConfigError, match=match):
        _design(**overrides)


def test_pilot_sweep_multiplies_blocks_and_shares_the_duration_free_baseline():
    fixed = dict(gamma=0.2, max_days=60)
    design = _design(fixed=fixed, sweep=dict(beta=(0.1, 0.2), quarantine_duration=(3, 6)))
    configs = design.configs()
    blocks = 1 * 2 * 2  # network seeds x epidemic seeds x transfer rates

    # The baseline ignores D, so it runs once per (beta, block), not once per (beta, D, block).
    assert sum(c.strategy == "none" for c in configs) == 2 * blocks
    assert sum(c.strategy != "none" for c in configs) == 2 * 2 * blocks * 2 * (1 + 1)
    assert {(c.beta, c.quarantine_duration) for c in configs if c.strategy != "none"} == {
        (0.1, 3), (0.1, 6), (0.2, 3), (0.2, 6),
    }
    assert len(set(configs)) == len(configs)


def test_baseline_only_design_runs_no_intervention():
    design = _design(response_delays=(), policy_seeds=(), fixed=dict(gamma=0.2), sweep=dict(beta=(0.1, 0.2)))
    configs = design.configs()
    assert len(configs) == 2 * 1 * 2 * 2 and {c.strategy for c in configs} == {"none"}


def test_invalid_parameter_fails_before_any_run(tmp_path):
    out = tmp_path / "raw.jsonl"
    with pytest.raises(ConfigError, match="transfer_rate"):
        run_design(_design(transfer_rates=(0.0, 1.5)), out)
    assert not out.exists()


def test_design_json_round_trip_and_unknown_keys(tmp_path):
    design = _design()
    path = tmp_path / "design.json"
    path.write_text(json.dumps(design.to_dict()), encoding="utf-8")
    assert ExperimentDesign.from_json(path) == design

    with pytest.raises(ConfigError, match="unknown design keys"):
        ExperimentDesign.from_dict({**design.to_dict(), "betta": 0.1})
    with pytest.raises(ConfigError, match="missing design keys"):
        ExperimentDesign.from_dict({"name": "x"})


def test_configuration_hash_is_canonical_and_sensitive():
    cfg = SimulationConfig(beta=0.2, epidemic_seed=7)
    as_dict = cfg.to_dict()
    assert configuration_hash(as_dict) == configuration_hash(dict(reversed(list(as_dict.items()))))
    assert configuration_hash(as_dict) != configuration_hash(replace(cfg, epidemic_seed=8).to_dict())
    assert len(configuration_hash(as_dict)) == 64


def test_raw_record_has_every_schema_field_and_is_json_serialisable():
    cfg = SimulationConfig(
        beta=0.2, gamma=0.2, transfer_rate=0.05, strategy="random", policy_seed=3, quarantine_duration=4,
        response_delay=1, epidemic_seed=7,
    )
    record = run_baseline(cfg, record_transitions=True)
    raw = to_raw_record(record, run_id="abc", timestamp_utc="2026-09-20T00:00:00Z")

    assert set(raw) == TOP_LEVEL_FIELDS
    assert raw["schema_version"] == SCHEMA_VERSION
    assert raw["intervention_duration_days"] == 4
    assert raw["intervention_cost"] == raw["metrics"]["intervention_cost"] == 2 * 4
    assert raw["metrics"] == record.metrics  # the runner never recomputes outcomes
    assert json.loads(json.dumps(raw)) == raw

    baseline = to_raw_record(run_baseline(SimulationConfig(epidemic_seed=7)), run_id="x", timestamp_utc="t")
    assert baseline["intervention_duration_days"] is None and baseline["selected_tanks"] == []


def test_run_design_writes_one_line_per_run_with_unique_ids(tmp_path):
    design = _design()
    out = tmp_path / "nested" / "raw.jsonl"
    counts = run_design(design, out)

    records = list(iter_raw(out))
    assert counts == {"planned": len(design.configs()), "skipped": 0, "written": len(records), "failed": 0}
    assert len(records) == len(design.configs())
    assert len({r["run_id"] for r in records}) == len(records)
    assert all(r["timestamp_utc"].endswith("Z") and set(r) == TOP_LEVEL_FIELDS for r in records)


def test_paired_strategies_share_network_and_initial_case(tmp_path):
    out = tmp_path / "raw.jsonl"
    run_design(_design(), out)
    blocks: dict[tuple, list[dict]] = {}
    for r in iter_raw(out):
        key = (r["seeds"]["network_seed"], r["seeds"]["epidemic_seed"], r["config"]["transfer_rate"])
        blocks.setdefault(key, []).append(r)

    for records in blocks.values():
        assert {r["config"]["strategy"] for r in records} == {"none", "random", "betweenness"}
        assert len({r["network"]["network_hash"] for r in records}) == 1
        assert len({tuple(r["initial_infected_agents"]) for r in records}) == 1


def test_existing_raw_file_is_refused_and_resume_skips_recorded_runs(tmp_path):
    design = _design()
    out = tmp_path / "raw.jsonl"
    run_design(design, out)
    before = out.read_text(encoding="utf-8")

    with pytest.raises(FileExistsError, match="append-only"):
        run_design(design, out)
    assert out.read_text(encoding="utf-8") == before

    counts = run_design(design, out, resume=True)
    assert counts["skipped"] == counts["planned"] and counts["written"] == 0
    assert out.read_text(encoding="utf-8") == before

    # A larger design resumed into the same file only adds the new block.
    grown = run_design(_design(epidemic_seeds=(7, 8, 9)), out, resume=True)
    assert grown["skipped"] == counts["planned"] and grown["written"] == grown["planned"] - counts["planned"]
    assert out.read_text(encoding="utf-8").startswith(before)


def test_invariant_failure_is_recorded_then_halts_the_batch(tmp_path, monkeypatch):
    def broken(self):
        if self.day == 2:
            raise InvariantError("forced for test")

    monkeypatch.setattr(Simulation, "_check_invariants", broken)
    out = tmp_path / "raw.jsonl"
    with pytest.raises(BatchHalted, match="invariant failure"):
        run_design(_design(), out)

    records = list(iter_raw(out))
    assert len(records) == 1  # the failed run is kept, nothing after it is attempted
    assert records[0]["status"] == "failed" and "forced for test" in records[0]["error"]
    assert records[0]["config"]["epidemic_seed"] == 7 and records[0]["daily"]


def test_runtime_failures_halt_only_above_the_failure_rate(tmp_path, monkeypatch):
    def broken(self):
        if self.cfg.epidemic_seed == 8 and self.cfg.strategy == "none" and self.cfg.transfer_rate == 0.0:
            raise ValueError("boom")
        return 0, 0, 0

    monkeypatch.setattr(Simulation, "_movement_stage", broken)
    tolerant = run_design(_design(), tmp_path / "tolerant.jsonl", max_failure_rate=0.5)
    assert tolerant["failed"] == 1 and tolerant["written"] == tolerant["planned"]

    with pytest.raises(BatchHalted, match="exceed"):
        run_design(_design(), tmp_path / "strict.jsonl", max_failure_rate=0.01)


def test_flatten_gives_one_row_with_block_key_and_model_metrics(tmp_path):
    out = tmp_path / "raw.jsonl"
    run_design(_design(), out)
    rows = [flatten(r) for r in iter_raw(out)]

    assert len({tuple(sorted(row)) for row in rows}) == 1
    for row, raw in zip(rows, iter_raw(out)):
        assert row["final_attack_rate"] == raw["metrics"]["final_attack_rate"]
        assert row["attempted_transfers"] == row["accepted_transfers"] + row["blocked_transfers"]
        assert row["network_hash"] == raw["network"]["network_hash"]
