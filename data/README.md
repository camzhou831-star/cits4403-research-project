# Data

This project uses no external dataset. Every input is synthetic and is generated from seeds when a run starts:
the transfer network from the network seed, the initial infection and every movement, transmission and recovery
draw from the epidemic seed, and the random-quarantine choice from the policy seed.

| What | Where |
|---|---|
| Inputs: experiment designs (parameter levels and seed lists) | `experiments/config/*.json` |
| Raw run records, one JSON line per run (git-ignored, regenerable) | `results/raw/*.jsonl` |
| Per-run summary tables (committed) | `results/summary/*.csv` |
| Pilot criterion tables | `results/pilot/` |
| Analysis tables and figures | `results/analysis/<design>/` |

To regenerate the formal data from scratch, run from the repository root:

```bash
python scripts/run_experiment.py experiments/config/formal-nested.json
```

The original formal dataset contains 5,200 runs. The separate [quarantine follow-up](../docs/followup-protocol.md) contains 19,000 completed sensitivity runs at transfer rate 0.025, varying duration and sampling more random-policy draws on the same 20 networks and 100 epidemic blocks. None failed or was censored, and all 400 replayed original conditions match. See the [follow-up results](../docs/followup-results.md) for evidence and interpretation. This is not an independent confirmation dataset or a replacement for `formal-nested`.

The follow-up reproduction route, from the repository root, is:

```bash
.venv/bin/python scripts/run_followup.py experiments/config/followup-duration-policy.json --dry-run
.venv/bin/python scripts/run_followup.py experiments/config/followup-duration-policy.json --workers 4
.venv/bin/python scripts/analyse_followup.py
```

Use `--resume` to continue the follow-up's append-only raw file without retrying recorded configurations. Compact records go to `results/raw/followup-duration-policy.jsonl`, the per-run table to `results/summary/followup-duration-policy.csv`, and analysis outputs to `results/analysis/followup-duration-policy/`. The runner's `--output-dir` option and the analysis script's `--followup` and `--output` options allow reproduction in a separate directory. The analysis record stores source hashes, coverage checks and replay evidence for the completed batch.

The original raw-record format and the separate follow-up schema are documented in [run-result-schema.md](../docs/run-result-schema.md).
