"""Design pairing, compact persistence and resume safeguards for the follow-up."""

import json
import multiprocessing
from dataclasses import replace
from pathlib import Path

import pytest

from turtlefarm.config import ConfigError
from turtlefarm.followup import FollowupDesign, _execute, run_followup
from turtlefarm.runner import BatchHalted, configuration_hash, iter_raw

ROOT = Path(__file__).resolve().parents[2]


def small_design(**overrides):
    design = FollowupDesign(
        name="followup-test", protocol_version=1, base_commit="76fa981", transfer_rate=0.025,
        network_seeds=(200, 201), epidemic_seed_start=20000, epidemic_replicates=2,
        policy_seed_start=50000, policy_replicates=2, response_delays=(1, 3), durations=(2, 4),
        fixed=dict(beta=0.2, gamma=1.0, capacity=12, k=2, max_days=20),
    )
    return replace(design, **overrides)


def test_committed_design_has_19000_unique_configs_and_nested_shared_policies():
    design = FollowupDesign.from_json(ROOT / "data/config/followup-duration-policy.json")
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


def test_completed_historical_batch_is_not_relabelled_after_implementation_changes(tmp_path, monkeypatch):
    import turtlefarm.followup as module
    design = small_design(network_seeds=(200,), epidemic_replicates=1, durations=(2,), response_delays=(1,))
    output = tmp_path / "runs.jsonl"
    run_followup(design, output)
    before = output.read_bytes()
    monkeypatch.setattr(module, "_repository_commit", lambda: "later-guard-implementation")
    counts = run_followup(design, output, resume=True)
    assert counts["written"] == 0 and counts["skipped"] == len(design.configs())
    assert output.read_bytes() == before


@pytest.mark.parametrize("change,match", [
    ("protocol", "protocol/schema"), ("duplicate", "duplicate"), ("config", "altered"),
    ("commit", "implementation commit changed"), ("missing_commit", "missing implementation commit"),
    ("failure", "failed runs exceed"),
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
    elif change == "missing_commit":
        record["summary"]["code_commit"] = None
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


@pytest.mark.parametrize("reason", ["runtime error", "invariant failure"])
def test_new_failure_is_saved_before_batch_halts(tmp_path, monkeypatch, reason):
    import turtlefarm.followup as module
    original = module._execute
    def fail(task):
        row = original(task)
        row["summary"].update(status="failed", stop_reason=reason)
        row["error"] = "fixture failure"
        return row
    monkeypatch.setattr(module, "_execute", fail)
    output = tmp_path / "runs.jsonl"
    with pytest.raises(BatchHalted):
        run_followup(small_design(), output)
    assert len(list(iter_raw(output))) == 1
    assert not output.with_name(output.name + ".lock").exists()


def _hold_first_run(design, output, entered, release):
    """A real second process holds the coordinator lock while its first record is persisted."""
    def progress(done, _total, _row):
        if done == 1:
            entered.set()
            if not release.wait(timeout=20):
                raise RuntimeError("test coordinator was not released")
    run_followup(design, output, progress=progress)


@pytest.mark.parametrize("resume", [False, True])
def test_concurrent_coordinator_is_rejected_without_touching_raw_file(tmp_path, resume):
    design = small_design(network_seeds=(200,), epidemic_replicates=1, durations=(2,), response_delays=(1,))
    output = tmp_path / "runs.jsonl"
    context = multiprocessing.get_context("spawn")
    entered, release = context.Event(), context.Event()
    process = context.Process(target=_hold_first_run, args=(design, output, entered, release))
    process.start()
    try:
        assert entered.wait(timeout=15), "first coordinator never reached its locked checkpoint"
        before = output.read_bytes()
        with pytest.raises(FileExistsError, match="coordinator lock exists"):
            run_followup(design, output, resume=resume)
        assert output.read_bytes() == before
    finally:
        release.set()
        process.join(timeout=15)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
    assert process.exitcode == 0
    assert len(list(iter_raw(output))) == len(design.configs())
    assert not output.with_name(output.name + ".lock").exists()


def test_stale_lock_is_not_deleted_automatically_and_manual_recovery_preserves_raw(tmp_path):
    design = small_design(network_seeds=(200,), epidemic_replicates=1, durations=(2,), response_delays=(1,))
    output = tmp_path / "runs.jsonl"
    first = _execute((design.configs()[0], design.protocol_hash))
    output.write_text(json.dumps(first) + "\n")
    before = output.read_bytes()
    lock = output.with_name(output.name + ".lock")
    marker = json.dumps({"pid": 99999999, "hostname": "inactive-test-host"})
    lock.write_text(marker)
    with pytest.raises(FileExistsError, match="crash recovery"):
        run_followup(design, output, resume=True)
    assert lock.read_text() == marker and output.read_bytes() == before
    lock.unlink()  # Emulate manual removal of this test-owned inactive marker, not any raw record.
    counts = run_followup(design, output, resume=True)
    assert counts["skipped"] == 1
    assert output.read_bytes().startswith(before)
    assert not lock.exists()


@pytest.mark.parametrize("workers", [1, 2])
def test_repository_provenance_is_independent_of_cwd(tmp_path, monkeypatch, workers):
    import turtlefarm.followup as module
    import turtlefarm.model as model
    expected_commit = module._repository_commit()
    monkeypatch.chdir(tmp_path)
    # The inherited model may return None or another repository's SHA. Compact provenance must
    # be independently resolved from the implementation path, not copied from that value.
    monkeypatch.setattr(model, "_git_commit", lambda: "unrelated-cwd-commit")
    design = small_design(network_seeds=(200,), epidemic_replicates=1, durations=(2,), response_delays=(1,))
    output = tmp_path / "runs.jsonl"
    run_followup(design, output, workers=workers)
    assert {record["summary"]["code_commit"] for record in iter_raw(output)} == {expected_commit}


def test_missing_repository_provenance_refuses_new_work_before_opening_raw(tmp_path, monkeypatch):
    import turtlefarm.followup as module
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    output = tmp_path / "runs.jsonl"
    with pytest.raises(ValueError, match="cannot determine implementation commit"):
        run_followup(small_design(), output)
    assert not output.exists()
    assert not output.with_name(output.name + ".lock").exists()


def test_midbatch_commit_change_does_not_append_a_mixed_commit_record(tmp_path, monkeypatch):
    import turtlefarm.followup as module
    head = ["original-commit"]
    monkeypatch.setattr(module, "_repository_commit", lambda: head[0])
    output = tmp_path / "runs.jsonl"
    saved = []
    def change_head(done, _total, _row):
        assert done == 1
        saved.append(output.read_bytes())
        head[0] = "changed-commit"
    with pytest.raises(ValueError, match="implementation commit changed during batch"):
        run_followup(small_design(), output, progress=change_head)
    assert output.read_bytes() == saved[0]
    assert len(list(iter_raw(output))) == 1
    assert not output.with_name(output.name + ".lock").exists()


def test_commit_change_during_one_simulation_discards_that_result(tmp_path, monkeypatch):
    import turtlefarm.followup as module
    head = ["original-commit"]
    monkeypatch.setattr(module, "_repository_commit", lambda: head[0])
    original = module.ObservedSimulation.run
    def change_head(simulation):
        record = original(simulation)
        head[0] = "changed-commit"
        return record
    monkeypatch.setattr(module.ObservedSimulation, "run", change_head)
    output = tmp_path / "runs.jsonl"
    with pytest.raises(ValueError, match="implementation commit changed during simulation"):
        run_followup(small_design(), output)
    assert output.read_bytes() == b""
    assert not output.with_name(output.name + ".lock").exists()


@pytest.mark.parametrize("change", ["protocol", "schema", "observation_schema", "config", "commit"])
def test_new_record_metadata_is_validated_before_append(tmp_path, monkeypatch, change):
    import turtlefarm.followup as module
    original = module._execute
    def corrupt_metadata(task):
        record = original(task)
        if change == "protocol":
            record["summary"]["protocol_hash"] = "wrong"
        elif change == "schema":
            record["schema_version"] = "wrong"
        elif change == "observation_schema":
            record["summary"]["observation_schema_version"] = "wrong"
        elif change == "config":
            record["config"]["beta"] = 0.9
        else:
            record["summary"]["code_commit"] = "wrong"
        return record
    monkeypatch.setattr(module, "_execute", corrupt_metadata)
    output = tmp_path / "runs.jsonl"
    with pytest.raises(ValueError):
        run_followup(small_design(), output)
    assert output.read_bytes() == b""
    assert not output.with_name(output.name + ".lock").exists()
