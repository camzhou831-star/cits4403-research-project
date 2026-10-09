# Experiments and pilot evidence

The completed original formal experiment is `formal-nested`, with 5,200 runs. The earlier `formal` dataset is retained as a historical crossed-seed comparison. The separate 19,000-run [follow-up](followup.md) does not replace or enlarge the original formal result set.

The submission layout places configurations in `data/config/`, outputs in `data/results/`, command-line entry points in `utils/` and tests in `src/tests/`. Paths below use that layout unless explicitly quoted as historical evidence; dates, recorded commits and numerical results are unchanged.

## Formal design

The main factors are transfer rate `0 / 0.01 / 0.025 / 0.1`, response delay `1 / 12 / 33` days from introduction, and strategy `none / random / betweenness`. Fixed settings are 200 agents, 20 tanks, 4 regions, initial occupancy 10, one initial infection, `beta=0.2`, `gamma=0.1`, capacity 12, `k=2`, `D=14`, `p_in=0.6`, `p_out=0.05` and `max_days=365`. The network generator, daily order and metric definitions are fixed.

Network seeds are 200-219. For network position i, the five distinct epidemic seeds are `20000 + 5*i + j`, j=0,...,4, yielding 100 nested network/epidemic blocks and no shared epidemic seed between networks. Random-policy seeds are 1000-1002. These are distinct from pilot seeds 100-104, 9000-9009 and 900-902.

One block at each transfer rate contains a shared no-intervention baseline plus three delays, each with one targeted and three random runs: `1 + 3*(1+3) = 13`. Four transfer rates times 100 blocks times 13 runs gives 5,200. Delay does not affect the baseline, so identical untreated runs are not repeated. At `mu=0`, infection must remain in the initial tank.

A paired comparison shares network, initial case, epidemic seed, transfer rate, disease parameters, capacity, delay, k and D; selection method is the only intervention difference. Epidemic draws are event-keyed rather than sequential draws that shift when policies alter exposure. Policy draws are recorded separately. Multiple networks, epidemic seeds and random policies represent distinct sources of variation; they must not be treated as interchangeable independent replicates.

Random and targeted arms have the same committed 28 tank-days if intervention activates. An outbreak ending before activation has cost 0 and stays in the primary analysis. The protocol originally recommended at least 10 networks, five epidemics each, 2-3 policy seeds and at least 30 replicates per condition; the final design used 20 networks and 100 blocks.

## Outcomes and analysis

Final attack rate (ever infected / 200, including the initial case) and the number of tanks ever containing an infectious agent are co-primary. Peak daily infected population, extinction time, first peak time and committed tank-days provide supporting dynamics. Censored extinction times remain missing; reaching the horizon is not extinction.

Condition summaries report sample count, mean, median, standard deviation, IQR and 95% confidence intervals. Policy comparisons first average the random arm within each network/epidemic block and then calculate paired targeted-minus-random differences. Absolute differences are primary; relative reduction is `(mean random - mean targeted) / mean random`, with an undefined result for a zero denominator, not the mean of individual ratios. The formal defaults use 2,000 percentile bootstrap resamples of whole networks, retaining their nested epidemic blocks, with bootstrap seed 0. Pointwise intervals are not multiplicity-adjusted or independent confirmations.

The formal analysis reports both all blocks and the subset in which quarantine starts, as recorded before formal execution after the pilot. Baseline contrasts, representative-run rules and other decisions made after seeing results are identified in [decisions.md](decisions.md#analysis-decisions-made-after-the-formal-results-2026-10-06). Complete pairing is checked against the design; incomplete blocks are counted and excluded rather than silently pooled. Both recorded formal datasets have zero incomplete blocks.

Qualitative examples use documented seeds and an objective selection rule, not the best-looking outcome. The saved figures cover network structure, attack rate, affected tanks, paired differences, peak infection, extinction and representative local/cross-region trajectories. Snapshot-based classifications can miss same-day infectious arrivals and recoveries; the audit and its qualifications remain in the decision record.

## Pilot protocol

Member A drafted the protocol on 2026-09-20. It required both members' confirmation and merge before execution. Member B's pre-run confirmation did not occur. The criteria and five 2026-10-06 clarifications were pushed in `d2be9bf` before the pilot ran; the pilot-before-sign-off deviation and later grid changes are in [decisions.md](decisions.md#protocol-deviations). Limited retrospective D004/D005 confirmations on 2026-10-08 do not approve all these departures.

The pilot is for parameter freezing, bug discovery and runtime estimation, not hypothesis evidence. It must not calculate random-versus-betweenness differences or group outcomes by strategy; Stage 2 pools both strategies. Retain every candidate, rejected candidate, failed and censored run. If none passes, record the failure, expand the grid only with a documented reason and confirmation, and rerun the complete stage without relaxing thresholds.

### 3. Stage 1: disease regime and transfer-rate levels (no intervention only)

Design: `data/config/pilot-stage1-disease.json`.

| Item | Value |
|---|---|
| Strategy | `none` only (no quarantine runs, so strategy effects cannot be revealed) |
| `beta` candidates | 0.05, 0.10, 0.15, 0.20 |
| `gamma` candidates | 0.10, 0.20 |
| Transfer-rate candidates | 0, 0.01, 0.02, 0.05, 0.10 |
| `p_in` / `p_out` | 0.6 / 0.05 (D005 candidate from the structural audit) |
| Seeds | 5 network × 10 epidemic = 50 blocks per candidate per level |
| Runs | 8 × 5 × 50 = 2000 |

This stage checks outbreak regime, movement distinguishability, capacity and the horizon; network stability is covered by the structural audits.

#### Selection criteria (written before running)

All metrics below come from `data/results/summary/pilot-stage1-disease.csv`. A "minor outbreak" is defined as `final_attack_rate ≤ 0.06` (the initial tank holds at most 12 agents, corresponding to an outbreak largely confined to the initial tank).

| # | Criterion | Threshold | Related question |
|---|---|---|---|
| S1 | Hard check: `affected_tanks = 1` when `transfer_rate = 0` | 100% of runs; any violation is a bug and pauses the pilot | Structural baseline (the structural baseline) |
| S2 | No failed run; censored share | failed = 0; `censored_max_days` ≤ 1% | Q6: whether the 365-day horizon is sufficient |
| S3 | Outbreaks are not all minor | At the highest two non-zero transfer levels, minor-outbreak share ≤ 70% | Q1: avoid all outbreaks rapidly reaching extinction |
| S4 | No saturation | At the lowest non-zero transfer level, median `final_attack_rate` ≤ 0.90 | Q1: avoid near-universal infection, leaving room to observe intervention effects |
| S5 | Transfer levels are distinguishable | There are 3 non-zero levels with strictly increasing median `affected_tanks` and at least a twofold difference in mean `accepted_transfers / days_simulated` between adjacent levels | Q2 |
| S6 | Capacity does not dominate movement | `blocked_transfers / attempted_transfers` ≤ 20% at every non-zero level | Q5 |

Selection rules:

1. Retain `(beta, gamma)` candidates satisfying all of S1-S6.
2. If more than one remains, select the candidate whose median `final_attack_rate` at the **middle level** of the three levels selected by S5 is closest to 0.5 (maximising room for variation in both directions). If still tied, choose the smaller `beta`.
3. Transfer-rate levels = `0` + the three non-zero levels satisfying S5. If multiple sets qualify, select the set with the largest span (highest level − lowest level). If spans are tied, select the set with the **smaller middle level** (retaining finer resolution at the low transfer rates of interest to the hypothesis; this rule does not inspect any outcome). For example, if `(0.01, 0.02, 0.1)` and `(0.01, 0.05, 0.1)` are tied, choose the former.

These criteria use only no-intervention runs and are therefore independent of the direction of the hypothesis.

### 4. Stage 2: response-delay levels and quarantine duration `D`

Create the Stage 2 design file only after recording the Stage 1 conclusions in `decisions.md` (it requires the selected `beta`, `gamma` and transfer levels). Name it `data/config/pilot-stage2-intervention.json`.

| Item | Value |
|---|---|
| Strategies | `none` + `random` + `betweenness` (the runner's standard block structure) |
| `D` candidates (`sweep.quarantine_duration`) | 7, 14, 21 |
| Response-delay candidates | Derived from Stage 1 data using D1-D3 below, without an additional sweep |
| Policy seeds | 900, 901, 902 |
| Transfer rates | The three **non-zero** levels selected in Stage 1. At `transfer_rate = 0`, quarantine cannot intercept any transfer (Q1 necessarily fails); including it would only dilute Q1, so it is excluded from Stage 2 |
| Seeds | The same 5 × 10 blocks as Stage 1 |

#### Response-delay levels (determined only from Stage 1 no-intervention data)

For runs that are **not minor outbreaks**, at the selected `(beta, gamma)` and middle transfer level:

| Level | Rule |
|---|---|
| D1 immediate | `1` (effective before the first movement stage, D001) |
| D2 intermediate | Median day on which `affected_tanks_ever` first reaches 2 (infection first leaves the initial tank) |
| D3 late | Median `time_to_peak` |

Round non-integer medians to whole days using round-half-up (0.5 rounds up, `floor(x + 0.5)`).

If D2 ≥ D3 or D2 ≤ 1, the three levels are not distinguishable: record this outcome and return to the next candidate under the Stage 1 selection rules; do not choose delays manually.

#### Selection criteria for `D` (calculated with strategies pooled, without comparing strategies)

| # | Criterion | Threshold | Rationale |
|---|---|---|---|
| Q1 | Quarantine rules intercept attempted movement | At least one attempt attributed to a quarantine rule in ≥ 90% of intervention runs whose quarantine started; counter definitions and threshold below are unchanged. Both historical mixed-counter denominators remain proxies only. | Operational check of rule interception, not proof of additional successful transfers prevented; see the 2026-10-07 clarification below. |
| Q2 | Quarantine does not cover the entire epidemic | `D` ≤ 25% of the median no-intervention `time_to_extinction` in the selected regime (pool shared-baseline runs with status = completed across all Stage 2 transfer levels; exclude censored runs) | Q5: must not "almost remove the entire network" |
| Q3 | Covers at least one mean infectious period | `D ≥ 1 / gamma` | Quarantine shorter than the infectious period is difficult to justify mechanistically |

Q1 correction after review (2026-10-06): `blocked_transfers` combines quarantine and capacity blocking across the whole run, including days before and after quarantine. A low capacity-blocking fraction per transfer (S6) does not imply that few runs have at least one capacity block. Consequently neither historical proxy verifies Q1. Verification requires a separately defined, tested quarantine-specific counter restricted to the active interval; no such evidence is added in this correction.

Selection rule: the smallest `D` satisfying Q1-Q3. Budget is `k × D` tank-days, identical for random and betweenness (D003: `k = 2`).

At the mixed-counter correction stage, the selector returned no automatically validated duration. D=14 was retained as the already completed formal setting; Q2 and Q3 alone could not repair the missing Q1 evidence. The historical proxy output remains in `data/results/pilot/stage2-criteria-legacy-proxy.csv`. The subsequent pre-specified cause-counter procedure below supplied the operational Q1 evidence, with the post-hoc denominator still disclosed.

##### Quarantine-specific Q1 (pre-registered 2026-10-06, before the counter exists or the pilot is rerun)

This section is committed before any model change and before `pilot-stage2-intervention` is rerun. Nobody has seen a quarantine-specific blocking count when it is written. The historical proxy results above are already known.

Classification of every blocked transfer attempt, in the order the movement stage checks them:

| Counter | Condition |
|---|---|
| `blocked_quarantine_out` | The origin tank is `QUARANTINED`. |
| `blocked_quarantine_in` | The origin is `OPEN`, no neighbour is an eligible destination, and at least one neighbour is `QUARANTINED` with `occupancy < capacity`. Had quarantine not applied, that neighbour would have been eligible. |
| `blocked_capacity` | Every other blocked attempt: all neighbours are full or there are none, regardless of their management state. |

The three counters partition `blocked_transfers` on every day. Quarantine counters can be nonzero only while a tank is quarantined, so they are restricted to the active interval by construction. Adding them must not change any simulated trajectory: all random draws are event-keyed and the counters do not draw.

Q1 (quarantine is not a no-op): among intervention runs (random and betweenness pooled, status not `failed`) in which quarantine started (`intervention_start_day` not null), the share with `blocked_quarantine_out + blocked_quarantine_in ≥ 1` is ≥ 90%. The started-runs denominator was itself chosen after seeing data (see decision log); the all-runs share is reported alongside it.

Procedure and pre-specified consequences:

1. Rerun `pilot-stage2-intervention` with the new counters. Every pre-existing summary column except `code_commit`, `run_id` (a fresh UUID per run) and `configuration_hash` must be identical to the committed summary, matched on the condition key (`network_seed`, `epidemic_seed`, `policy_seed`, `transfer_rate`, `response_delay`, `strategy`, `quarantine_duration`). `configuration_hash` changes because the parameter freeze (`f4eac85`) emptied `provisional_fields` after the pilot ran; with the old list restored, all 5550 hashes match. If not, stop: the counters changed the model, and no Q1 result is used.
2. Run `pilot_select.py stage2`. The selection rule is unchanged: the smallest `D` meeting Q1-Q3.
3. If `D=14` is selected, D004 is recorded as validated by Q1-Q3, with the denominator change still disclosed.
4. If no `D` passes, `D=14` remains the setting of the completed formal experiment, the report states that Q1 failed and by how much, and the formal experiment is not rerun or changed.
5. Q2 and Q3 admit only `D=14`, so no other `D` can be selected. Should that nonetheless happen, it is reported and the formal experiment is still not changed.

##### Interpretation and completeness clarification (2026-10-07 review follow-up)

This clarification was added after the rerun; it does not amend the pre-registered counter definitions, threshold or selection rule above. The counters classify attempts by the first blocking rule reached. In particular, `blocked_quarantine_out` includes an attempted departure from a quarantined origin even when every neighbouring tank is full. Removing quarantine would not make that attempt succeed. Q1 therefore verifies operational interception by quarantine rules, not a strict counterfactual effect on successful transfers or on disease outcomes. The recorded 95.7% at D=14 must be interpreted in that limited sense.

All three cause columns must be present and non-missing for every summary row before the evaluator marks Q1 as verified. Missing columns or values leave Q1 unknown and prevent automatic duration selection; the mixed total cannot replace them. The two other acceptance criteria and all completed experiment settings remain unchanged.

### 5. Implementation of selection rules

The criteria above are implemented in `src/turtlefarm/analysis.py`. `utils/pilot_select.py stage1` / `stage2` applies them to recorded pilot results and writes each candidate's criterion-by-criterion assessment to `data/results/pilot/`. If the rules cannot yield a unique choice (for example, no candidate passes, or rule 2 remains tied with equal `beta`), the script stops with exit code 3 without selecting automatically; record the outcome, obtain confirmation for any expanded grid and rerun the full stage without relaxing thresholds.

Additions on 2026-10-06 (before running or inspecting any pilot data): tie-breaking for Stage 1 rule 3, Stage 2 transfer levels, delay rounding, the baseline scope for Q2 and the counting limitation for Q1.



## Pilot results

Recorded 2026-10-06, with the interpretation clarification on 2026-10-07. The criterion tables in `data/results/pilot/` retain every tried candidate. The following numbered result subsections preserve the chronology: the mixed-counter conclusions in sections 4 and 7 were superseded by the cause-counter measurement in section 8, not silently rewritten as pre-run evidence. All Stage 2 metrics pool strategies.

### 1. Run overview

| Design | Runs | Completed | Censored | Failed | Runtime |
|---|---|---|---|---|---|
| `pilot-stage1-disease` (round 1) | 2000 | 2000 | 0 | 0 | 37 s |
| `pilot-stage1-disease-r2` (round 2, adding 0.025 to the grid) | 2400 | 2400 | 0 | 0 | 45 s |
| `pilot-stage2-intervention` | 5550 | 5550 | 0 | 0 | 123 s |

Seeds: network 100-104, epidemic 9000-9009, policy 900-902. These seeds are excluded from the formal experiment.

### 2. Stage 1 round 1: no candidate passed

All 8 `(beta, gamma)` candidates satisfied S1-S4 and S6; all **failed solely on S5**.

- S5 requires at least a twofold difference in mean accepted transfers per day between adjacent levels. In the original grid `0.01 / 0.02 / 0.05 / 0.1`, the nominal ratios for 0.01→0.02 and 0.05→0.10 are exactly twofold. Capacity blocking reduced the measured ratios to about 1.77 and 1.88, so no three-level combination satisfied S5.
- Under rule 5, the threshold was unchanged; 0.025 was added to the grid and the entire stage was rerun (`decisions.md`, pushed before round 2).

### 3. Stage 1 round 2: selected disease regime and transfer levels

| beta | gamma | S1-S6 | S5 levels (rule 3) | Median attack rate at 0.025 | Distance from 0.5 |
|---|---|---|---|---|---|
| 0.05 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.192 | 0.308 |
| 0.05 | 0.2 | **fail (S5)** | - | - | - |
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

### 4. Stage 2: quarantine duration `D`

| D | Runs | Quarantine started | blocked ≥ 1 (all runs) | blocked ≥ 1 (started) | All-runs proxy | Started-runs proxy | Q2 (D ≤ 16.25) | Q3 (D ≥ 10) |
|---|---|---|---|---|---|---|---|---|
| 7 | 1800 | 1516 | 85.3% | 97.3% | fail | pass | pass | fail |
| **14** | 1800 | 1516 | 85.3% | 97.4% | fail | pass | pass | pass |
| 21 | 1800 | 1516 | 85.3% | 97.4% | fail | pass | fail | pass |

No-intervention median `time_to_extinction` = 65 days, so the Q2 upper limit is 16.25 days.

- **No D passed the original all-runs proxy threshold.** Of 1,800 intervention runs per duration, 284 ended before quarantine started. They occur at delays 12 and 33. However, 60 of these 284 runs per duration still have blocked transfers, so non-start is not equivalent to zero blocking.
- Among runs where quarantine started, almost all runs with no blocked transfers were minor outbreaks (median attack rate 0.005).
- Q1's denominator was revised to "runs where quarantine actually started" after inspecting Stage 2 data; see `decisions.md`.
- Only `D=14` meets Q2 and Q3 among the tested durations. This does not establish Q1: both historical percentages use a counter that mixes blocking causes and days outside quarantine.
- The completed experiment used **D=14**, with a planned budget of `k × D = 28` tank-days. At that point it was retained for reporting, not yet certified as a Q1-Q3 selection; the later cause-counter results below supersede that evidence status.

### 5. Implications for the formal experiment

- At delays 12 and 33, about 20%-34% of runs ended before quarantine started. All three strategies have identical outcomes in these runs, with paired differences of 0. The formal analysis must report both:
  - Effects across all blocks;
  - Effects restricted to blocks with infection still present on the response day.
- The pilot estimated runtime at about 45 runs/s, or 2 minutes for the planned 5200-run formal experiment.

### 6. Additional note (2026-10-06, discovered after the formal experiment)

The pilot seeds were crossed: every network used the same epidemic seeds 9000-9009. With event-keyed draws, the same epidemic seed gives the same initial infected agent and early draws across all networks. The proportions in this report therefore effectively rely on only **10 independent epidemic starting points** (variation between networks remains valid).

For example, of the 284 runs in §4 where quarantine never started at D = 14, 240 came from seeds 9003 and 9006: both seeds reached extinction before day 12 in every network. The remaining 44 came from 9002, 9005 and 9009.

Parameter selection was not repeated. The formal experiment uses nested seeds instead (`formal-nested`); see `decisions.md`.

### 7. Q1 counter audit after review (2026-10-06)

`blocked_transfers` sums all daily blocking, including capacity blocking and days outside the quarantine interval. Restricting the denominator to started runs does not isolate the cause or timing of a block. S6 limits the fraction of attempted transfers blocked by capacity; it does not limit the fraction of runs with at least one such event.

For the 1,516 started intervention runs at `D=14`, 1,476 have at least one block (97.3615%). Matching each to its no-intervention baseline by `(network_seed, epidemic_seed, transfer_rate)` gives 1,392 baseline matches with at least one block (91.8206%). These are repeated, matched baselines weighted like the intervention runs, not 1,516 independent baseline simulations. Capacity-only blocking already exceeds the 90% proxy threshold. Among the 284 never-started runs, 60 also have a nonzero counter.

The original table is preserved unchanged as `data/results/pilot/stage2-criteria-legacy-proxy.csv`. At this correction stage, the regenerated `stage2-criteria.csv` labelled both old checks as proxies, recorded `Q1_status=unverified_mixed_blocking_counter`, and left the quarantine-specific check unknown. `passed` was unknown for candidates satisfying Q2/Q3 and false when either failed. No candidate was automatically selected before the later cause-counter rerun.

This correction changes neither the model nor the formal design, results or figures. The correction required a subsequent definition and measurement of quarantine-rule blocking during the active interval before Q1 could be asserted. No new threshold, duration or favourable outcome has been selected in this correction.

### 8. Q1 with cause-specific blocking counters (2026-10-06)

Definitions, rule and consequences were committed in `experiments.md#pilot-protocol` §4 before the counters existed. The model now records, per day, `blocked_quarantine_out` (origin quarantined), `blocked_quarantine_in` (no eligible destination, but a quarantined neighbour has space) and `blocked_capacity` (everything else); they sum to `blocked_transfers`.

Reproduction check: the Stage 2 pilot was rerun (5550 runs, 110 s). All 27 pre-existing summary columns other than `code_commit`, `run_id` and `configuration_hash` are identical, matched on the condition key.

Started intervention runs (1,516 per D), random and betweenness pooled:

| D | ≥ 1 quarantine block | ≥ 1 capacity block | Q1 (≥ 90%) | Q2 | Q3 | Pass |
|---|---|---|---|---|---|---|
| 7 | 91.8% | 90.7% | pass | pass | fail | fail |
| **14** | **95.7%** | 90.6% | pass | pass | pass | **pass** |
| 21 | 96.7% | 89.8% | pass | fail | pass | fail |

Selected: **D=14**, the setting the formal experiment already used. By transfer level at D=14 the quarantine share is 90.9% (0.01), 96.2% (0.025) and 99.8% (0.1); Q1 is defined on the pooled share. No-intervention baselines contain no quarantine blocks, as expected; 80.7% of them have at least one capacity block, which is why the mixed counter could not measure Q1.

Table: `data/results/pilot/stage2-criteria.csv`. The pre-counter table remains in `stage2-criteria-legacy-proxy.csv`.

### 9. Interpretation and input-completeness clarification (2026-10-07)

The section 8 percentages measure attempts intercepted by the first applicable quarantine rule, not a strict counterfactual count of successful transfers prevented. An origin-quarantine count can occur even when all neighbouring tanks are full; without quarantine that attempt would still fail. This clarification preserves the recorded counter definitions, the 90% threshold and D=14 selection under the operational Q1 criterion. It does not claim a causal reduction in movement or infections.

The evaluator now requires all three cause columns to exist and contain no missing values before marking Q1 as verified. Incomplete input remains unverified and cannot select a duration. No pilot or formal result is changed by this guard; the numerical table in section 8 remains applicable under the interpretation above.


## Reproduction and failure handling

Use the project environment and run commands from the repository root:

```bash
.venv/bin/python utils/run_experiment.py data/config/pilot-stage1-disease.json --dry-run
.venv/bin/python utils/run_experiment.py data/config/pilot-stage1-disease.json
.venv/bin/python utils/run_experiment.py data/config/pilot-stage1-disease-r2.json
.venv/bin/python utils/pilot_select.py stage1 --design pilot-stage1-disease-r2 --force
.venv/bin/python utils/run_experiment.py data/config/pilot-stage2-intervention.json
.venv/bin/python utils/pilot_select.py stage2
.venv/bin/python utils/run_experiment.py data/config/formal-nested.json
.venv/bin/python utils/analyse_results.py formal-nested
```

Raw records belong in `data/results/raw/` (git-ignored, append-only); per-run CSVs in `data/results/summary/`; derived tables and figures in `data/results/analysis/`. Frozen designs are in `data/config/`. The Stage 1 command explicitly uses round 2 because no candidate passed round 1. Its `--force` option regenerates the existing Stage 2 configuration from those selected results; the regenerated configuration must match the committed design. Check for unexpected changes rather than accepting a different design silently.

An existing raw file requires `--resume`. Resume skips recorded configurations, including failures. Current-design failures count towards the cumulative limit; a recorded invariant failure or a failure count exceeding the default 1% of the full planned design stops continuation before new appends. Never delete a valid extreme outcome or stop a formal batch because a trend looks clear. A confirmed implementation bug requires a documented corrective commit and separately named rerun output for the complete affected seed block, not selective rerunning of unfavourable outcomes.

The historical smoke estimate was 20 runs in 0.4 s on 2026-09-20, with about 300 MB estimated raw output for 2,000 Stage 1 runs. Measured pilot runtimes are retained above; they are machine-specific evidence, not performance guarantees. [Validation](validation.md#reproduction-2026-10-06) records the later clean-environment reproduction, including a discovered analysis failure.

## Sensitivity scope

The completed [follow-up](followup.md) crosses D=7/14/28 with delays 1/12/33 at transfer rate 0.025, using 20 random-policy draws per network. It reuses the original 20 networks and 100 epidemic blocks, retains duplicate tank pairs, and compares equal strategy budgets within D. Across durations both closure length and cost change.

The earlier plan also proposed lower/higher beta, lower/higher gamma, homogeneous versus limited heterogeneous capacity and movement/update-order checks. Those checks are not covered by the duration follow-up. New disease mechanisms, network rewiring and cross-region movement restrictions remain outside scope. The results do not support real turtle-disease forecasts or an empirically optimal policy.
