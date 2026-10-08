# Pilot Protocol (experiment-plan §7, §9; D004 / D005; issues #4, #5)

Current record (2026-10-08): this protocol preserves the original draft and dated amendments. The pilot and formal experiment have since run. Recomputing Stage 2 criteria confirms the recorded D=14 selection. Member B's pre-run approval did not occur; retrospective confirmations remain pending in `decision-log.md`. The expanded structural check in `network-audit-2026-10-08.md` was completed after the formal experiment and reports one C4 no-tie failure. None of those facts changes the original ordering of decisions or approvals below.

Status: **DRAFT: drafted by Member A (2026-09-20), pending Member B's confirmation. Do not run the pilot or inspect any pilot outcome before both members confirm.**

This document follows the approach in `network-audit-2026-09-11.md`: **write selection criteria before inspecting data**. The pilot is used only for parameter freezing, bug discovery and runtime estimation, not as hypothesis evidence (experiment-plan §7). This document contains no simulation results.

## 1. Rules against outcome-driven tuning

1. Both members must confirm this document's selection criteria and merge them into `main` before running the pilot. Any later change to confirmed criteria must be recorded with its reason in `decision-log.md`.
2. **Do not calculate random-versus-betweenness differences on pilot data** or compare outcomes grouped by strategy. Stage 2 uses only mechanistic metrics pooled across strategies.
3. Pilot seeds must not enter the formal experiment: list network seeds `100-104`, epidemic seeds `9000-9009` and policy seeds `900-902` as excluded in the parameter-freeze record.
4. Retain all attempted candidates, rejected candidates and failed / censored runs and include them in the pilot report; delete none.
5. If no candidate meets the criteria, do not relax thresholds ad hoc to select one. Record the outcome, expand the candidate grid, obtain both members' confirmation of the new grid and rerun the complete stage.

## 2. Running the pilot

```bash
python scripts/run_experiment.py experiments/config/pilot-stage1-disease.json --dry-run   # Validate and print the run count only
python scripts/run_experiment.py experiments/config/pilot-stage1-disease.json
```

Raw records are written to `results/raw/<name>.jsonl` (git-ignored, append-only), and per-run summaries to `results/summary/<name>.csv`. Runtime estimate (2026-09-20, measured `smoke` design: 20 runs / 0.4 s): Stage 1's 2000 runs should take about 1 minute, with a raw file of about 300 MB.

## 3. Stage 1: disease regime and transfer-rate levels (no intervention only)

Design: `experiments/config/pilot-stage1-disease.json`.

| Item | Value |
|---|---|
| Strategy | `none` only (no quarantine runs, so strategy effects cannot be revealed) |
| `beta` candidates | 0.05, 0.10, 0.15, 0.20 |
| `gamma` candidates | 0.10, 0.20 |
| Transfer-rate candidates | 0, 0.01, 0.02, 0.05, 0.10 |
| `p_in` / `p_out` | 0.6 / 0.05 (D005 candidate from the structural audit) |
| Seeds | 5 network × 10 epidemic = 50 blocks per candidate per level |
| Runs | 8 × 5 × 50 = 2000 |

This answers pilot questions 1, 2, 5 (capacity component) and 6. Question 4 (network generator stability) has already been answered by the structural audit.

### Selection criteria (written before running)

All metrics below come from `results/summary/pilot-stage1-disease.csv`. A "minor outbreak" is defined as `final_attack_rate ≤ 0.06` (the initial tank holds at most 12 agents, corresponding to an outbreak largely confined to the initial tank).

| # | Criterion | Threshold | Related question |
|---|---|---|---|
| S1 | Hard check: `affected_tanks = 1` when `transfer_rate = 0` | 100% of runs; any violation is a bug and pauses the pilot | Structural baseline (experiment-plan §3) |
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

## 4. Stage 2: response-delay levels and quarantine duration `D`

Create the Stage 2 design file only after recording the Stage 1 conclusions in `decision-log.md` (it requires the selected `beta`, `gamma` and transfer levels). Name it `experiments/config/pilot-stage2-intervention.json`.

| Item | Value |
|---|---|
| Strategies | `none` + `random` + `betweenness` (the runner's standard block structure) |
| `D` candidates (`sweep.quarantine_duration`) | 7, 14, 21 |
| Response-delay candidates | Derived from Stage 1 data using D1-D3 below, without an additional sweep |
| Policy seeds | 900, 901, 902 |
| Transfer rates | The three **non-zero** levels selected in Stage 1. At `transfer_rate = 0`, quarantine cannot intercept any transfer (Q1 necessarily fails); including it would only dilute Q1, so it is excluded from Stage 2 |
| Seeds | The same 5 × 10 blocks as Stage 1 |

### Response-delay levels (determined only from Stage 1 no-intervention data)

For runs that are **not minor outbreaks**, at the selected `(beta, gamma)` and middle transfer level:

| Level | Rule |
|---|---|
| D1 immediate | `1` (effective before the first movement stage, D001) |
| D2 intermediate | Median day on which `affected_tanks_ever` first reaches 2 (infection first leaves the initial tank) |
| D3 late | Median `time_to_peak` |

Round non-integer medians to whole days using round-half-up (0.5 rounds up, `floor(x + 0.5)`).

If D2 ≥ D3 or D2 ≤ 1, the three levels are not distinguishable: record this outcome and return to the next candidate under the Stage 1 selection rules; do not choose delays manually.

### Selection criteria for `D` (calculated with strategies pooled, without comparing strategies)

| # | Criterion | Threshold | Rationale |
|---|---|---|---|
| Q1 | Quarantine rules intercept attempted movement | At least one attempt attributed to a quarantine rule in ≥ 90% of intervention runs whose quarantine started; counter definitions and threshold below are unchanged. Both historical mixed-counter denominators remain proxies only. | Operational check of rule interception, not proof of additional successful transfers prevented; see the 2026-10-07 clarification below. |
| Q2 | Quarantine does not cover the entire epidemic | `D` ≤ 25% of the median no-intervention `time_to_extinction` in the selected regime (pool shared-baseline runs with status = completed across all Stage 2 transfer levels; exclude censored runs) | Q5: must not "almost remove the entire network" |
| Q3 | Covers at least one mean infectious period | `D ≥ 1 / gamma` | Quarantine shorter than the infectious period is difficult to justify mechanistically |

Q1 correction after review (2026-10-06): `blocked_transfers` combines quarantine and capacity blocking across the whole run, including days before and after quarantine. A low capacity-blocking fraction per transfer (S6) does not imply that few runs have at least one capacity block. Consequently neither historical proxy verifies Q1. Verification requires a separately defined, tested quarantine-specific counter restricted to the active interval; no such evidence is added in this correction.

Selection rule: the smallest `D` satisfying Q1-Q3. Budget is `k × D` tank-days, identical for random and betweenness (D003: `k = 2`).

Until Q1 is verified, the selector must return no automatically validated duration. `D=14` remains the setting of the already completed formal experiment, not a newly validated Q1-Q3 selection. Q2 and Q3 alone identify 14 among the tested candidates. Keeping this setting avoids changing the experiment in response to its outcomes; it does not repair the missing Q1 evidence. Historical proxy output is retained in `results/pilot/stage2-criteria-legacy-proxy.csv`.

#### Quarantine-specific Q1 (pre-registered 2026-10-06, before the counter exists or the pilot is rerun)

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

#### Interpretation and completeness clarification (2026-10-07 review follow-up)

This clarification was added after the rerun; it does not amend the pre-registered counter definitions, threshold or selection rule above. The counters classify attempts by the first blocking rule reached. In particular, `blocked_quarantine_out` includes an attempted departure from a quarantined origin even when every neighbouring tank is full. Removing quarantine would not make that attempt succeed. Q1 therefore verifies operational interception by quarantine rules, not a strict counterfactual effect on successful transfers or on disease outcomes. The recorded 95.7% at D=14 must be interpreted in that limited sense.

All three cause columns must be present and non-missing for every summary row before the evaluator marks Q1 as verified. Missing columns or values leave Q1 unknown and prevent automatic duration selection; the mixed total cannot replace them. The two other acceptance criteria and all completed experiment settings remain unchanged.

## 5. Implementation of selection rules

The criteria above are implemented in `turtlefarm/analysis.py`. `scripts/pilot_select.py stage1` / `stage2` applies them to recorded pilot results and writes each candidate's criterion-by-criterion assessment to `results/pilot/`. If the rules cannot yield a unique choice (for example, no candidate passes, or rule 2 remains tied with equal `beta`), the script stops with exit code 3 without selecting automatically; follow §1 rule 5.

Additions on 2026-10-06 (before running or inspecting any pilot data): tie-breaking for Stage 1 rule 3, Stage 2 transfer levels, delay rounding, the baseline scope for Q2 and the counting limitation for Q1.

## 6. After the pilot

1. Write `docs/pilot-report-<date>.md`: criterion-by-criterion results for each candidate, excluded candidates, failed / censored runs and runtime.
2. Freeze `beta`, `gamma`, `D`, `p_in` / `p_out`, transfer-rate levels, delay levels, seed lists and replication counts in `decision-log.md`, and close issues #4 and #5.
3. Create `experiments/config/formal.json` (no `sweep`; no overlap with pilot seeds).
4. Remove frozen fields from `PROVISIONAL_FIELDS` in `turtlefarm/config.py`.

## 7. Sign-off

| Member | Criteria confirmation (before running) | Date |
|---|---|---|
| Member A (Cam Zhou) | Drafted | 2026-09-20 |
| Member B (Wenhao Zhang) | Pending confirmation | — |
