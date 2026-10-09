"""Design pairing, compact persistence and resume safeguards for the follow-up."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from turtlefarm.config import ConfigError
from turtlefarm.followup import FollowupDesign, _execute, run_followup
from turtlefarm.runner import BatchHalted, configuration_hash, iter_raw

ROOT = Path(__file__).resolve().parents[1]


def small_design(**overrides):
    design = FollowupDesign(
        name="followup-test", protocol_version=1, base_commit="76fa981", transfer_rate=0.025,
        network_seeds=(200, 201), epidemic_seed_start=20000, epidemic_replicates=2,
        policy_seed_start=50000, policy_replicates=2, response_delays=(1, 3), durations=(2, 4),
        fixed=dict(beta=0.2, gamma=1.0, capacity=12, k=2, max_days=20),
    )
    return replace(design, **overrides)


def test_committed_design_has_19000_unique_configs_and_nested_shared_policies():
    design = FollowupDesign.from_json(ROOT / "experiments/config/followup-duration-policy.json")
    configs = design.configs()
    assert len(configs) == len(set(configs)) == 19000
    assert sum(c.strategy == "none" for c in configs) == 100
    assert sum(c.strategy == "betweenness" for c in configs) == 900
    assert sum(c.strategy == "random" for c in configs) == 18000
    for index, network in enumerate(design.network_seeds):
        rows = [c for c in configs if c.network_seed == network]
        assert {c.epidemic_seed for c in rows} == set(range(20000 + 5 * index, 20005 + 5 * index))
        assert {c.policy_seed for c in rows if c.strategy == "random"} == set(range(50000 + 20 * index, 50020 + 20 * index))
    assert {c.k * c.quarantine_duration for c in configs if c.strategy != "none"} == {14, 28, 56}


@pytest.mark.parametrize("overrides", [
    dict(name="../escape"), dict(network_seeds=(200, 200)), dict(durations=()),
    dict(epidemic_replicates=0), dict(policy_replicates=True), dict(policy_seed_start=-1),
    dict(response_delays=(-1,)), dict(fixed={"strategy": "random"}),
])
def test_invalid_design(overrides):
    with pytest.raises(ConfigError):
        small_design(**overrides)


def test_compact_record_keeps_configuration_and_observations_without_daily_trajectories():
    design = small_design()
    cfg = design.configs()[0]
    record = _execute((cfg, design.protocol_hash))
    assert record["config"] == cfg.to_dict()
    assert "daily" not in record
    assert record["summary"]["configuration_hash"] == configuration_hash(cfg.to_dict())
    assert record["summary"]["status"] == "completed"
    assert record["summary"]["regions_visited_by_I"] >= 1
    assert record["initial_infected_agents"]


def test_resume_skips_without_writing_and_refuses_existing_file(tmp_path):
    design = small_design()
    output = tmp_path / "runs.jsonl"
    counts = run_followup(design, output)
    before = output.read_bytes()
    assert counts == dict(planned=52, written=52, skipped=0, failed=0)
    assert run_followup(design, output, resume=True) == dict(planned=52, written=0, skipped=52, failed=0)
    assert output.read_bytes() == before
    with pytest.raises(FileExistsError):
        run_followup(design, output)


@pytest.mark.parametrize("change,match", [
    ("protocol", "protocol/schema"), ("duplicate", "duplicate"), ("config", "altered"),
    ("commit", "implementation commit changed"), ("failure", "failed runs exceed"),
    ("invariant", "invariant failure"),
])
def test_resume_refuses_bad_prior_records_before_appending(tmp_path, change, match):
    design = small_design()
    record = _execute((design.configs()[0], design.protocol_hash))
    if change == "protocol":
        record["summary"]["protocol_hash"] = "wrong"
    elif change == "config":
        record["config"]["beta"] = 0.9
    elif change == "commit":
        record["summary"]["code_commit"] = "other"
    elif change in {"failure", "invariant"}:
        record["summary"]["status"] = "failed"
        record["summary"]["stop_reason"] = "invariant failure" if change == "invariant" else "runtime error"
        record["error"] = "fixture failure"
    output = tmp_path / "runs.jsonl"
    output.write_text((json.dumps(record) + "\n") * (2 if change == "duplicate" else 1))
    before = output.read_bytes()
    with pytest.raises((ValueError, BatchHalted), match=match):
        run_followup(design, output, resume=True)
    assert output.read_bytes() == before


def test_parallel_execution_matches_serial_scientific_rows(tmp_path):
    design = small_design(network_seeds=(200,), epidemic_replicates=1, durations=(2,), response_delays=(1,))
    serial, parallel = tmp_path / "serial.jsonl", tmp_path / "parallel.jsonl"
    run_followup(design, serial)
    run_followup(design, parallel, workers=2)
    def science(path):
        return [{k: v for k, v in r["summary"].items() if k != "run_id"} for r in iter_raw(path)]
    assert science(serial) == science(parallel)


def test_new_failure_is_saved_before_batch_halts(tmp_path, monkeypatch):
    import turtlefarm.followup as module
    original = module._execute
    def fail(task):
        row = original(task)
        row["summary"].update(status="failed", stop_reason="runtime error")
        row["error"] = "fixture failure"
        return row
    monkeypatch.setattr(module, "_execute", fail)
    output = tmp_path / "runs.jsonl"
    with pytest.raises(BatchHalted):
        run_followup(small_design(), output)
    assert len(list(iter_raw(output))) == 1
