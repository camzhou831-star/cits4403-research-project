# Pilot Report (2026-10-06)

**Review correction:** Stage 2's whole-run blocked-transfer percentages in section 4 are historical proxies, not quarantine-specific effects (section 7). Q1 was then remeasured with pre-registered cause-specific counters, and `D=14` meets Q1-Q3 (section 8).

Prepared under `pilot-protocol.md` §6 step 1. The pilot is used only for parameter freezing, bug discovery and runtime estimation, not as hypothesis evidence: this report **contains no random-versus-betweenness comparison**, and all Stage 2 metrics pool the two strategies.

All assessments are calculated mechanically by `scripts/pilot_select.py` under the previously pushed criteria. Criterion-level tables are in `results/pilot/`, and raw records are in `results/raw/` (git-ignored, append-only; no run has been deleted). See "Protocol deviations" in `decision-log.md` for departures from the protocol.

## 1. Run overview

| Design | Runs | Completed | Censored | Failed | Runtime |
|---|---|---|---|---|---|
| `pilot-stage1-disease` (round 1) | 2000 | 2000 | 0 | 0 | 37 s |
| `pilot-stage1-disease-r2` (round 2, adding 0.025 to the grid) | 2400 | 2400 | 0 | 0 | 45 s |
| `pilot-stage2-intervention` | 5550 | 5550 | 0 | 0 | 123 s |

Seeds: network 100-104, epidemic 9000-9009, policy 900-902. These seeds are excluded from the formal experiment.

## 2. Stage 1 round 1: no candidate passed

All 8 `(beta, gamma)` candidates satisfied S1-S4 and S6; all **failed solely on S5**.

- S5 requires at least a twofold difference in mean accepted transfers per day between adjacent levels. In the original grid `0.01 / 0.02 / 0.05 / 0.1`, the nominal ratios for 0.01→0.02 and 0.05→0.10 are exactly twofold. Capacity blocking reduced the measured ratios to about 1.77 and 1.88, so no three-level combination satisfied S5.
- Under rule 5, the threshold was unchanged; 0.025 was added to the grid and the entire stage was rerun (`decision-log.md`, pushed before round 2).

## 3. Stage 1 round 2: selected disease regime and transfer levels

| beta | gamma | S1-S6 | S5 levels (rule 3) | Median attack rate at 0.025 | Distance from 0.5 |
|---|---|---|---|---|---|
| 0.05 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.192 | 0.308 |
| 0.05 | 0.2 | **fail (S5)** | — | — | — |
| 0.10 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.262 | 0.238 |
| 0.10 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.092 | 0.408 |
| 0.15 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.435 | 0.065 |
| 0.15 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.103 | 0.397 |
| **0.20** | **0.1** | **pass** | **0.01 / 0.025 / 0.1** | **0.458** | **0.042** |
| 0.20 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.112 | 0.388 |

Observations for the other criteria:

- S1: at `transfer_rate = 0`, all runs had `affected_tanks = 1`, as expected; no movement bug was found.
- S2: no run failed or was censored; the 365-day horizon was sufficient.
- S6: capacity-blocking shares across levels were 3.5%-7.7%, well below 20%.

Rule 2 selected `beta = 0.2, gamma = 0.1`. Transfer levels are **0 / 0.01 / 0.025 / 0.1**.

Response delays were calculated from 40 non-minor runs, yielding **1 / 12 / 33 days**:

- D2: median day on which infection first reaches the 2nd tank = 12.0;
- D3: median `time_to_peak` = 33.0;
- Both medians were integers, so no rounding was applied.

The report must state that, in the selected regime, the no-intervention median attack rate at `transfer_rate = 0.1` is 1.0 (near saturation), so intervention differences at that level may be limited by a ceiling effect.

## 4. Stage 2: quarantine duration `D`

| D | Runs | Quarantine started | blocked ≥ 1 (all runs) | blocked ≥ 1 (started) | All-runs proxy | Started-runs proxy | Q2 (D ≤ 16.25) | Q3 (D ≥ 10) |
|---|---|---|---|---|---|---|---|---|
| 7 | 1800 | 1516 | 85.3% | 97.3% | fail | pass | pass | fail |
| **14** | 1800 | 1516 | 85.3% | 97.4% | fail | pass | pass | pass |
| 21 | 1800 | 1516 | 85.3% | 97.4% | fail | pass | fail | pass |

No-intervention median `time_to_extinction` = 65 days, so the Q2 upper limit is 16.25 days.

- **No D passed the original all-runs proxy threshold.** Of 1,800 intervention runs per duration, 284 ended before quarantine started. They occur at delays 12 and 33. However, 60 of these 284 runs per duration still have blocked transfers, so non-start is not equivalent to zero blocking.
- Among runs where quarantine started, almost all runs with no blocked transfers were minor outbreaks (median attack rate 0.005).
- Q1's denominator was revised to "runs where quarantine actually started" after inspecting Stage 2 data; see `decision-log.md`.
- Only `D=14` meets Q2 and Q3 among the tested durations. This does not establish Q1: both historical percentages use a counter that mixes blocking causes and days outside quarantine.
- The completed experiment used **D=14**, with a planned budget of `k × D = 28` tank-days. This setting is retained for reporting the existing experiment, not certified as a fully validated Q1-Q3 selection.

## 5. Implications for the formal experiment

- At delays 12 and 33, about 20%-34% of runs ended before quarantine started. All three strategies have identical outcomes in these runs, with paired differences of 0. The formal analysis must report both:
  - Effects across all blocks;
  - Effects restricted to blocks with infection still present on the response day.
- Runtime is about 45 runs/s. The 5200-run formal experiment is expected to take 2 minutes.

## 6. Additional note (2026-10-06, discovered after the formal experiment)

The pilot seeds were crossed: every network used the same epidemic seeds 9000-9009. With event-keyed draws, the same epidemic seed gives the same initial infected agent and early draws across all networks. The proportions in this report therefore effectively rely on only **10 independent epidemic starting points** (variation between networks remains valid).

For example, of the 284 runs in §4 where quarantine never started at D = 14, 240 came from seeds 9003 and 9006: both seeds reached extinction before day 12 in every network. The remaining 44 came from 9002, 9005 and 9009.

Parameter selection will not be repeated. The formal experiment uses nested seeds instead (`formal-nested`); see `decision-log.md`.

## 7. Q1 counter audit after review (2026-10-06)

`blocked_transfers` sums all daily blocking, including capacity blocking and days outside the quarantine interval. Restricting the denominator to started runs does not isolate the cause or timing of a block. S6 limits the fraction of attempted transfers blocked by capacity; it does not limit the fraction of runs with at least one such event.

For the 1,516 started intervention runs at `D=14`, 1,476 have at least one block (97.3615%). Matching each to its no-intervention baseline by `(network_seed, epidemic_seed, transfer_rate)` gives 1,392 baseline matches with at least one block (91.8206%). These are repeated, matched baselines weighted like the intervention runs, not 1,516 independent baseline simulations. Capacity-only blocking already exceeds the 90% proxy threshold. Among the 284 never-started runs, 60 also have a nonzero counter.

The original table is preserved unchanged as `results/pilot/stage2-criteria-legacy-proxy.csv`. The regenerated `stage2-criteria.csv` labels both old checks as proxies, records `Q1_status=unverified_mixed_blocking_counter`, and leaves the quarantine-specific check unknown. `passed` is unknown for candidates satisfying Q2/Q3 and false when either of those criteria fails. No candidate is automatically selected.

This correction changes neither the model nor the formal design, results or figures. A future validation must define and count quarantine-caused blocking during the active interval, separately from capacity blocking, before asserting that Q1 is satisfied. No new threshold, duration or favourable outcome has been selected in this correction.

## 8. Q1 with cause-specific blocking counters (2026-10-06)

Definitions, rule and consequences were committed in `pilot-protocol.md` §4 before the counters existed. The model now records, per day, `blocked_quarantine_out` (origin quarantined), `blocked_quarantine_in` (no eligible destination, but a quarantined neighbour has space) and `blocked_capacity` (everything else); they sum to `blocked_transfers`.

Reproduction check: the Stage 2 pilot was rerun (5550 runs, 110 s). All 27 pre-existing summary columns other than `code_commit`, `run_id` and `configuration_hash` are identical, matched on the condition key.

Started intervention runs (1,516 per D), random and betweenness pooled:

| D | ≥ 1 quarantine block | ≥ 1 capacity block | Q1 (≥ 90%) | Q2 | Q3 | Pass |
|---|---|---|---|---|---|---|
| 7 | 91.8% | 90.7% | pass | pass | fail | fail |
| **14** | **95.7%** | 90.6% | pass | pass | pass | **pass** |
| 21 | 96.7% | 89.8% | pass | fail | pass | fail |

Selected: **D=14**, the setting the formal experiment already used. By transfer level at D=14 the quarantine share is 90.9% (0.01), 96.2% (0.025) and 99.8% (0.1); Q1 is defined on the pooled share. No-intervention baselines contain no quarantine blocks, as expected; 80.7% of them have at least one capacity block, which is why the mixed counter could not measure Q1.

Table: `results/pilot/stage2-criteria.csv`. The pre-counter table remains in `stage2-criteria-legacy-proxy.csv`.

## 9. Interpretation and input-completeness clarification (2026-10-07)

The section 8 percentages measure attempts intercepted by the first applicable quarantine rule, not a strict counterfactual count of successful transfers prevented. An origin-quarantine count can occur even when all neighbouring tanks are full; without quarantine that attempt would still fail. This clarification preserves the recorded counter definitions, the 90% threshold and D=14 selection under the operational Q1 criterion. It does not claim a causal reduction in movement or infections.

The evaluator now requires all three cause columns to exist and contain no missing values before marking Q1 as verified. Incomplete input remains unverified and cannot select a duration. No pilot or formal result is changed by this guard; the numerical table in section 8 remains applicable under the interpretation above.
