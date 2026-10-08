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

The raw-record format is documented in `docs/run-result-schema.md`.
