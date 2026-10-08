# Week 12 Demonstration Plan

Status: rewritten 2026-10-08 for the slide-deck presentation, by Member A; awaiting Member B's confirmation.

## 1. Requirements

From the project specification (rubric section 2.3, Project Demonstration, 5% of the unit mark):

- Book a slot on the sign-up sheet. Both members must be present **five minutes before** the slot, with the model ready to run on a computer and all data files and outputs available.
- The demonstration lasts **at most 10 minutes**, and both members take part.
- It must explain the motivation, background and aims; describe the modelling approach and justify the key choices; present results with figures, plots, animations or simulations; and discuss conclusions and insights.
- The marker then asks questions, and **each member's answers are assessed individually**. The code rubric (section 2.1) also assesses each member's "Code Understanding and Explanation": explaining their own contributions, how key functions implement the model rules, and the likely effect of a proposed change.

## 2. Materials

| Material | Where | Notes |
|---|---|---|
| Slide deck, 14 slides, with speaker notes | Claude artifact (link held by Member A; share it with Member B from the deck's Share menu) | Export it as PDF and PPTX onto the demo laptop as an offline copy |
| Live run | `scripts/demo_final.py` | Reruns one paired block of `formal-nested` in about a second and checks it against the stored records |
| Slide images that are not report figures | `results/demo/timing-window.png`, `results/demo/example-block.gif` | Rendered by `python scripts/make_presentation_assets.py` from `mechanism.json` and the `demo_final.py` block |
| Slide images from the report | `docs/figures/concept-diagram.png`; `results/analysis/formal-nested/fig1`, `fig2`, `fig4`, `fig7` | Same files as in the report |
| Backup video | `results/demo/demo-3min.mp4` (3 min, silent) | Only if the live run or the deck fails; see `docs/demo-video.md` |

## 3. Run of show (about 9 minutes)

Speaking time is based on the speaker notes (about 1,100 words at 140 words per minute) plus the live run. The section label at the top of every slide names the speaker.

| Slide | Content | Speaker | Time |
|---|---|---|---|
| 1 | Title, names and student numbers, repository | Cam | 0:20 |
| 2 | Motivation, the two research questions, hypotheses H1-H3 | Cam | 0:35 |
| 3 | Background: metapopulations, bridges, betweenness; the gap we address | Cam | 0:30 |
| 4 | Model overview (concept diagram) | Wenhao | 0:35 |
| 5 | Daily update rules; random vs targeted quarantine under the same budget | Wenhao | 0:40 |
| 6 | Verification, then the **live run** of `demo_final.py` | Wenhao | 0:25 + 0:40 |
| 7 | Pilot parameter selection, including the Q1 counter correction | Cam | 0:35 |
| 8 | Experiment design: 100 paired blocks per transfer rate, 5,200 runs | Cam | 0:35 |
| 9 | Result 1: the transfer rate dominates (report Figure 2) | Cam | 0:35 |
| 10 | One example block, animated | Wenhao | 0:35 |
| 11 | Result 2: targeting is not consistently better (report Figure 4) | Wenhao | 0:35 |
| 12 | Result 3, exploratory: position and timing | Cam | 0:45 |
| 13 | Conclusions, limitations, next steps | Wenhao | 0:35 |
| 14 | Thank you; questions | Cam | 0:10 |

Each member presents the parts closest to their own code, so the individual questions that follow are on familiar ground: Wenhao wrote movement, the quarantine strategies and the run-record schema, and Cam wrote the network, paired draws, runner, analysis and report (`docs/collaboration-plan.md`). If time runs short, shorten slides 3 and 7 first; never cut the live run or slide 12.

## 4. Live run (slide 6)

Before the demonstration, on the demo laptop:

```bash
git pull                                  # main, after all pull requests are merged
source .venv/bin/activate
python -m pytest -q                       # all tests pass, about 5 seconds
python scripts/demo_final.py              # last line: "All runs identical ... : yes"
```

Then enlarge the terminal font, close notifications, and open the deck in Present mode with the terminal one keystroke away.

During slide 6, Wenhao switches to the terminal and runs `python scripts/demo_final.py`. Point out three things: no quarantine gives 0.610, targeted 0.475, and the three random choices 0.670, 0.625 and 0.900; every row says "yes" in the last column; and the closing line confirms that all runs match the stored records. Then switch back. Do not run the full experiment (about 2 minutes); if asked, say that `docs/reproduction-2026-10-06.md` records a clean-environment rerun.

If the marker asks for a change to be tested, a safe example is `python scripts/demo_final.py --delay 1`: the same block with an immediate response, where targeting does worse, which shows why 100 blocks are needed.

## 5. Code walkthrough map

Each member should be able to explain every row: what the code does, why, and where it is tested. The "Author" column follows the GitHub record and names the lead speaker; both members still need to understand each row.

| Topic | Location | Author (PR) | Key points | Tests |
|---|---|---|---|---|
| Daily order | `src/turtlefarm/model.py` `step()` | Cam (#19) | management → movement → transmission → recovery → commit; disease states update together | `tests/test_invariants.py`, `tests/test_hand_trace.py` |
| Transmission and recovery | `model.py` `_transmission_and_recovery()`, `_commit()` | Cam (#19) | `1-(1-beta)^I`; a newly infected agent neither transmits nor recovers that day | `tests/test_extreme_cases.py` |
| Movement | `model.py` `_movement_stage()` | Wenhao (#27) | random order, immediate capacity and quarantine checks, blocked transfers | `tests/test_movement.py` |
| Blocked-by-cause counters | `model.py` `_movement_stage()` | Cam (#36) | quarantined origin / quarantined neighbour with space / capacity; partition of `blocked_transfers` | `tests/test_blocked_causes.py` |
| Quarantine selection and timing | `model.py` `_select_intervention_tanks()`, `_management_update()` | Wenhao (#29) | pre-outbreak network only; half-open interval `[start, start+D)`; equal budget | `tests/test_quarantine.py` |
| Network | `src/turtlefarm/network.py` `generate_network()`, `rank_by_betweenness()` | Cam (#23) | `p_in` / `p_out`, four acceptance rules, ties broken by tank id | `tests/test_network.py` |
| Paired random numbers | `src/turtlefarm/rng.py` | Cam (#22/#23) | the same seed gives every strategy identical draws (common random numbers) | `tests/test_paired_draws.py` |
| Batch runs | `src/turtlefarm/runner.py` `ExperimentDesign.configs()`, `run_design()` | Cam (#31, #34) | block structure, shared baseline, nested seeds, append-only records | `tests/test_runner.py` |
| Result-record format | `docs/run-result-schema.md` | Wenhao (#25) | fields recorded per run; how failures are recorded | `tests/test_runner.py` |
| Analysis | `src/turtlefarm/analysis.py` `paired_differences()`, `cluster_bootstrap_ratio()` | Cam (#34) | resampling by network; relative reduction as a ratio of means | `tests/test_analysis.py` |
| Exploratory mechanism measures | `src/turtlefarm/mechanism.py`, `scripts/mechanism_analysis.py` | Cam (#45) | bridge coverage, first cross-region day, previously infected tanks | `tests/test_mechanism.py` |
| Notebook | `notebooks/project-walkthrough.ipynb` | Wenhao (#39) | reruns five example arms, recomputes the formal estimates | runs end to end |

Practice, each member at least once:

- Without notes, list the daily steps and name the function for each.
- Open a function the other member wrote and explain it to them line by line.
- Change one parameter, predict the result, then check it with `python scripts/demo_final.py` (for example `--delay 1`, or temporarily `quarantine_duration` 0 in a local copy). Restore any edit with `git checkout`.
- Answer: "What would change to add a detection process, or to stop infectious turtles from moving?"

## 6. Backup plan

- Keep the exported PDF and PPTX of the deck on the demo laptop; the PDF needs no internet connection.
- If the live run fails, slide 6 already shows the expected output; say so and move on. If the deck fails, play `results/demo/demo-3min.mp4` and speak over it.
- Prepare both laptops: `.venv` installed, tests passing, `demo_final.py` run once.
- If only a browser is available, open the repository on GitHub at a fixed commit (press `y` on a file page).

## 7. Likely questions

- **Why betweenness and not degree?** We care about paths between regions; a high-degree tank may have only within-region links. Salathé and Jones found that targeting bridges works better than targeting hubs in networks with communities.
- **Is the example on slide 10 cherry-picked?** No: it was chosen by a rule fixed in advance that looks only at the no-quarantine run (closest to the class median), and the random arm shown is the median of three. It illustrates the mechanism; slide 11 is the evidence.
- **Is the timing result causal?** No. It is exploratory and post hoc, and the crossing days come from runs without quarantine, so it shows potential overlap with the window, not crossings that quarantine prevented. It is consistent with a timing mismatch and suggests the next experiments.
- **Can quarantine make things worse?** Yes, in single blocks: with `--delay 1`, the same block gives 0.980 under targeted quarantine against 0.610 with none. Closing tanks changes which neighbours are open, so moving turtles take different paths, and the outbreak can follow a worse one. Across 100 blocks this averages out, which is why single blocks are not evidence.
- **Why not a longer quarantine?** The pilot required the closure to cover less than a quarter of the median epidemic; 14 days was the only candidate that also lasted at least one infectious period. Longer or detection-triggered closures are our proposed next experiment.
- **Why are the intervals so wide?** 20 networks and 100 blocks per condition, with a bootstrap that resamples whole networks; the intervals are pointwise and not adjusted for 18 comparisons.
- **What would you do with more time?** A larger budget, sensitivity analyses on `beta`, `gamma` and capacity, a pre-specified strategy × delay test, and closures triggered by detection outside the initial region.
- **Show me where X is tested.** Use the last column of the table in Section 5.

## 8. Schedule

| When | Task | Who |
|---|---|---|
| After the report is submitted | Book the slot; share the deck; export PDF and PPTX | Both |
| Next two days | Explain each other's code using Section 5 | Both |
| Before the slot | Rehearse twice with a timer; one presents, the other asks questions as the marker | Both |
| Day before | Run Section 4 on the demo laptop | Both |
