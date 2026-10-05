# Clean-environment reproduction (2026-10-06)

Purpose: check that the committed results and report can be regenerated from a fresh clone, with nothing reused from the working copy.

## Setup

- Fresh `git clone` of branch `docs/readme-diagram-contribution` at `8d7311f` into a temporary directory. The clone had no `results/raw/`.
- New environment created with `uv venv --python 3.12` (Python 3.12.13) and `uv pip install -r requirements.txt`: numpy 2.5.2, networkx 3.6.1, pandas 3.0.5, matplotlib 3.11.1.
- Ran the README sequence in order: tests, pilot stage 1 (both rounds), `pilot_select.py stage1 --force`, pilot stage 2, `pilot_select.py stage2`, `formal`, `formal-nested`, `analyse_results.py` for both formal designs, `build_report.py`, `draw_concept_diagram.py`.

## Comparison with the committed files

The criteria were fixed before the comparison:

- **Must match exactly:** analysis tables, pilot criterion tables, the Stage 2 design and the report.
- **Excluded from the comparison:** run provenance fields (`run_id`, timestamps, `code_commit`).

| Output | Result |
|---|---|
| Tests | 166 passed (167 after the fix below) |
| Pilot selection | Same choice: `beta` 0.2, `gamma` 0.1, transfer levels 0 / 0.01 / 0.025 / 0.1, delays 1 / 12 / 33, `D` 14 |
| `results/pilot/*`, `experiments/config/pilot-stage2-intervention.json` | Byte-identical |
| `results/summary/formal*.csv` (all 10,400 runs) | Identical in every cell except `run_id` and `code_commit` |
| `results/summary/pilot-*.csv` (9,950 runs) | Identical in every result cell; `configuration_hash` differs (see below) |
| `results/analysis/formal-nested/*` (tables, figures 1-7) | Byte-identical, except `fig7-selection.json`, which stores the run's `run_id` |
| `report/report.md`, `docs/figures/concept-diagram.png` | Byte-identical |
| `results/analysis/formal/*` | **Analysis crashed**; see below |

Runtimes on this machine were 33 s, 41 s and 111 s for the three pilot stages, and 100 s and 104 s for the two formal runs.

## Findings

1. **Crash in `analyse_results.py formal` (fixed).** Figure 2 raised `'yerr' must not contain negative values`. When every value in a cell is identical, for example one affected tank at transfer rate 0, the cluster-bootstrap bound can differ from the mean by about 1e-16. That made the error-bar length slightly negative.

   - **How it was missed.** The crash first occurred during the round-2 review fixes. It went unnoticed because the command's output was filtered through `grep`, which hid the traceback.
   - **Effect.** In the committed `results/analysis/formal/` (the crossed-seed run, used only in report §3.5), figures 2-3 were stale and three summary files were missing. The tables used by the report were written before the crash and are correct.
   - **Fix.** Error-bar lengths are clipped at 0. A regression test was added that fails without the fix. All outputs were regenerated.
   - **Not affected.** `formal-nested`, the reported experiment.

2. **Pilot configuration hashes changed after the parameter freeze (documented, not changed).** `SimulationConfig.to_dict()` includes `provisional_fields`. This list had five entries when the pilot ran and is empty since the freeze (`f4eac85`), so the same pilot configuration now hashes differently. Results are unaffected.

   The consequence is for `--resume`: run against a pilot raw file produced before the freeze, it would not recognise any finished run and would rerun all of them. The formal runs were made after the freeze and are unaffected.

3. **Lesson for the remaining runs.** Every pipeline step is now run with `set -o pipefail`, so a failure inside a filtered command stops the sequence.
