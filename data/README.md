# Synthetic data and provenance

No external dataset is used. Networks, initial infections and subsequent random events are generated from the recorded seeds. The epidemic draws are keyed by event, day and agent; random-policy draws select the quarantined tank pair.

## Inputs and outputs

| Location | Contents |
|---|---|
| `config/` | Seven JSON designs, including both pilot rounds, Stage 2, smoke, original crossed, final nested and follow-up designs |
| `results/summary/` | One row per recorded run |
| `results/pilot/` | Parameter-selection criteria and the disclosed historical Q1 proxy |
| `results/analysis/formal-nested/` | Final original-study tables and figures |
| `results/analysis/followup-duration-policy/` | Separate sensitivity analysis and its provenance receipt |
| `results/analysis/formal/` | Superseded crossed-seed analysis, retained for audit |
| `results/demo/` | Example animation, timing figure and historical original-study video |
| `results/raw/` | Regenerable raw JSONL records; ignored by Git |
| `results/tmp/` | Temporary verification outputs; ignored by Git |
| `methods/` | Rules, protocols, schemas, validation evidence and limitations |
| `figures/` | Conceptual model diagram |

## Recorded studies

| Summary | Rows | Role |
|---|---:|---|
| `pilot-stage1-disease.csv` | 2,000 | Initial disease/transfer pilot |
| `pilot-stage1-disease-r2.csv` | 2,400 | Expanded transfer-grid pilot |
| `pilot-stage2-intervention.csv` | 5,550 | Quarantine-duration selection |
| `formal.csv` | 5,200 | Historical crossed-seed experiment; not the final formal result |
| `formal-nested.csv` | 5,200 | Final original experiment: 20 networks, 100 nested epidemic seeds |
| `followup-duration-policy.csv` | 19,000 | Paired duration/policy sensitivity study on the same networks and epidemic blocks |

The follow-up is separate from `formal-nested`, not an independent confirmation dataset. All 19,000 runs completed without failure or censoring; 400 replays of original conditions match their recorded scientific fields. Pointwise intervals and policy-sampling limits are described in [the follow-up methods and results](methods/followup.md).

The historical `formal` dataset crossed the same five epidemic seeds with 20 networks. The final nested design instead uses five independent epidemic seeds within each network. They are different experimental designs, not duplicate copies. The historical files document the correction and must not be pooled with the final results.

The old mixed-blocking Q1 table is retained as `results/pilot/stage2-criteria-legacy-proxy.csv`. Current criteria use complete, cause-specific counters. Neither table establishes the counterfactual number of successful transfers prevented by quarantine.

## Reproduction

Run from the repository root with the dependencies in `requirements.txt`:

```bash
python utils/run_experiment.py data/config/formal-nested.json
python utils/analyse_results.py formal-nested
python utils/mechanism_analysis.py

python utils/run_followup.py data/config/followup-duration-policy.json --dry-run
python utils/run_followup.py data/config/followup-duration-policy.json --workers 4
python utils/analyse_followup.py
```

Existing raw files are append-only. Use `--resume` only for a compatible unfinished batch; it does not retry failures. For a fresh reproduction after a code revision, use a separate output directory. The README provides the full commands, failure-handling rules and notebook instructions.

The original run contract and follow-up missing-value/event definitions are in [the result schema](methods/result-schema.md).

## Directory migration and historical receipts

The submission cleanup changed locations, not the configuration values, seeds or committed result bytes:

| Historical location | Current location |
|---|---|
| `experiments/config/` | `data/config/` |
| `results/` | `data/results/` |
| `scripts/` | `utils/` |
| `tests/` | `src/tests/` |
| `docs/figures/` | `data/figures/` |
| Scientific `docs/*.md` | Consolidated under `data/methods/` |

The report is submitted separately through the university website. Old checkpoint notes, rehearsal scripts and report files were removed from the code submission; their earlier versions remain in Git history.

Historical JSON receipts intentionally retain the paths, implementation commits and SHA256 hashes that were recorded when their analyses ran. In particular, `results/analysis/followup-duration-policy/analysis-summary.json` was moved under `data/` without rewriting its internal source paths. Resolve its historical `results/...` input paths as `data/results/...` when checking the current files. Historical code hashes identify that earlier analysis code, not the relocated working tree.

Rerunning analysis creates a new receipt with current paths and code hashes; it does not retrospectively change the provenance of the recorded simulations. To keep the historical receipt intact, use the analysis command's `--output` option with a directory under `data/results/tmp/`.
