"""Submission entry points and report-independent original-study video numbers."""

from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from utils.make_demo_video import headline_numbers


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("script,design,expected", [
    ("run_experiment.py", "formal-nested.json", "5200 runs"),
    ("run_followup.py", "followup-duration-policy.json", "19,000 planned runs"),
])
def test_relocated_entry_points_resolve_package_outside_repository(tmp_path, script, design, expected):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "utils" / script), str(ROOT / "data" / "config" / design), "--dry-run"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    assert expected in completed.stdout
    assert not list(tmp_path.iterdir())


def test_original_study_headlines_retain_the_recorded_values():
    assert headline_numbers() == {
        "mult": "3.3", "tanks": "3.4", "max_reduction": "10.6%", "ci": "2", "intervals": "18",
    }


def test_video_headlines_read_tables_and_exclude_other_outcomes_and_subsets(tmp_path):
    pd.DataFrame([
        {"strategy": "none", "metric": metric, "transfer_rate": rate, "mean": mean}
        for metric, rate, mean in [
            ("final_attack_rate", 0.01, 0.2), ("final_attack_rate", 0.025, 0.3),
            ("affected_tanks", 0.01, 2), ("affected_tanks", 0.025, 5),
        ]
    ]).to_csv(tmp_path / "condition-summary.csv", index=False)
    pd.DataFrame([
        {"metric": "final_attack_rate", "rel_reduction": 0.1},
        {"metric": "final_attack_rate", "rel_reduction": 0.15},
        {"metric": "affected_tanks", "rel_reduction": 0.95},
    ]).to_csv(tmp_path / "baseline-effects.csv", index=False)
    pd.DataFrame([
        {"subset": subset, "transfer_rate": rate, "metric": metric,
         "mean_diff_ci95_low": low, "mean_diff_ci95_high": high}
        for subset, rate, metric, low, high in [
            ("all_blocks", 0.025, "final_attack_rate", -0.2, -0.1),
            ("all_blocks", 0.025, "affected_tanks", 0, 1),
            ("all_blocks", 0, "final_attack_rate", 0.1, 0.2),
            ("quarantine_started", 0.025, "final_attack_rate", 0.1, 0.2),
            ("all_blocks", 0.025, "peak_infected", 1, 2),
        ]
    ]).to_csv(tmp_path / "paired-effects.csv", index=False)
    assert headline_numbers(tmp_path) == {
        "mult": "1.5", "tanks": "2.5", "max_reduction": "15.0%", "ci": "1", "intervals": "2",
    }
