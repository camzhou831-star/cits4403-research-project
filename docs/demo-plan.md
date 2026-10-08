# Week 12 Demo Preparation

Status: draft 2026-10-06, prepared by Member A, awaiting Member B's confirmation.

> **The official demo format has not yet been recorded** (duration, live or recorded, and whether questions will be addressed to each member individually). The only known requirement comes from the lecture (2026-08-10): "You may use built-in functions directly in the project, but during the demo you must be able to explain the code you submit." Update this file first when the format becomes available.

## 1. Goals

1. Explain the questions, model, main results and limitations in 5-8 minutes; reuse sections 1-8 of `checkpoint-3-speaking-notes.md`, shortening them to fit the available time.
2. Run the code live to demonstrate that the results are reproducible (`scripts/demo_final.py`).
3. **Each person must be able to explain any core code in the repository**, including code written by the other member. This is the most likely topic for individual questioning.

## 2. Code walkthrough map

Each person must be able to explain every row below using the code: what it does, why it works that way and where it is tested. The "Author" column follows the GitHub record and assigns the lead speaker; both members still need to understand it.

| Topic | Location | Author (PR) | Key points | Tests |
|---|---|---|---|---|
| Daily order | `turtlefarm/model.py` `step()` | Cam (#19) | management → movement → transmission → recovery → commit; why disease states update synchronously | `tests/test_invariants.py`, `tests/test_hand_trace.py` |
| Transmission and recovery | `model.py` `_transmission_and_recovery()`, `_commit()` | Cam (#19) | `1-(1-beta)^I`; newly infected agents do not transmit on the same day | `tests/test_extreme_cases.py` (`beta=0`, `gamma=1`) |
| Movement | `model.py` `_movement_stage()` | Wenhao (#27) | Random order, immediate capacity and quarantine checks, two causes of blocked transfers | `tests/test_movement.py` |
| Quarantine selection and timing | `model.py` `_select_intervention_tanks()`, `_management_update()` | Wenhao (#29) | Uses only the pre-outbreak network; half-open interval `[start, start+D)`; equal budget | `tests/test_quarantine.py` |
| Network | `turtlefarm/network.py` `generate_network()`, `rank_by_betweenness()` | Cam (#23) | `p_in` / `p_out`, 4 acceptance rules, ties broken by tank id | `tests/test_network.py` |
| Paired random numbers | `turtlefarm/rng.py` | Cam (#22/#23) | Every strategy receives identical draws under the same seed; these are common random numbers | `tests/test_paired_draws.py` |
| Batch runs | `turtlefarm/runner.py` `ExperimentDesign.configs()`, `run_design()` | Cam (#31, #34) | Block structure, shared baseline, nested seeds, append-only records | `tests/test_runner.py` |
| Result-record format | `docs/run-result-schema.md` | Wenhao (#25) | Fields recorded for each run and how failures are recorded | `tests/test_runner.py` |
| Analysis | `turtlefarm/analysis.py` `paired_differences()`, `cluster_bootstrap_ratio()` | Cam (#34) | Why resampling is by network; why relative reduction uses a ratio of means | `tests/test_analysis.py` |

**Practice** (each person should do this at least once, preferably setting questions for each other):

- Without looking at the documentation, draw the 8 daily steps on a whiteboard and name the function for each step.
- Open a function written by the other member and explain it to them line by line.
- Change a parameter live and predict the result, for example setting `quarantine_duration` to 0 or `transfer_rate` to 0, then run `python scripts/demo_final.py` to check. Remember to restore the change with `git checkout` afterwards.
- Answer: "What would need to change to add a detection process / prevent sick turtles from moving?"

## 3. Live demo sequence (about 2 minutes)

```bash
source .venv/bin/activate
python -m pytest -q                       # Expected: 198 passed, about 4 seconds
python scripts/demo_final.py              # delay 33: targeted 0.475, random 0.625-0.900; final line yes
python scripts/demo_final.py --delay 1    # Same block, but targeted is worse → why we need 100 blocks
```

Then open the figures: `fig2` (transfer-rate effect) → `fig7` (cross-region spread mechanism) → `fig4` (paired differences and confidence intervals).

Do not run the full experiment live during the demo (it takes about 2 minutes and is unnecessary). If asked, explain that `docs/reproduction-2026-10-06.md` records the results of a rerun in a clean environment.

## 4. Backup plan

- Put screenshots of the figures and demo output in one folder in advance, or export a PDF; show the screenshots if the network or computer fails.
- Prepare the environment on both computers: `.venv` installed, `pytest` passing and the demo run once.
- If the projector can only show GitHub pages, prepare links to the relevant files, pinned to a commit (press `y` on the GitHub page).

## 5. Schedule

| Date | Task | Who |
|---|---|---|
| Day 1 after submission | Confirm demo format and duration; shorten the script to fit | Both |
| Day 2 | Explain each other's code (Section 2 table), noting anything that is difficult to explain | Both |
| Day 3 | Rehearse the full demo twice and time it; one person speaks while the other asks questions as the teacher | Both |
| Day before the demo | Run the Section 3 commands on the demo computer; prepare backup screenshots | Both |

## 6. Likely questions

In addition to the questions in `checkpoint-3-speaking-notes.md`, the demo may include:

- Why betweenness and not degree? → We are interested in cross-region paths; a high-degree tank may have only within-region connections. Reference [5] (Salathé & Jones) found that targeting bridge nodes is more effective in networks with strong community structure.
- Why is the model stochastic, and how many runs did you need? → 100 blocks per condition, with a network-cluster bootstrap; the pilot was used to estimate runtime.
- What would you do with more time? → A larger quarantine budget, sensitivity analysis (`beta`, `gamma`, capacity), a pre-specified strategy × delay test, and records of when each tank became infected to test the mechanism in report §4.2.
- Show me where X is tested. → Use the last column of the Section 2 table.
