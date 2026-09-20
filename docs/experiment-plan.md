# Experiment Plan

## 1. Purpose

The main experiment answers the two research questions; it is not a demonstration of simulator features. It must compare several transfer rates, response delays and intervention strategies, and evaluate under paired random conditions whether highest-betweenness quarantine outperforms random quarantine.

## 2. Primary experiment

### Independent variables

1. **Cross-tank transfer rate (`mu`)**: provisionally 4 levels, namely `0` and 3 non-zero levels to be set by the pilot.
2. **Response delay (`d`)**: provisionally 3 levels, e.g. immediate / short / long; the exact days are set by facilitator feedback and the pilot.
3. **Intervention strategy**:
   - `No intervention`
   - `Random tank quarantine`
   - `Highest-betweenness tank quarantine`

Numeric levels must not be written down as final values before the pilot.

### Control variables

Fixed in the main experiment:

- population = 200; tanks = 20; regions = 4;
- initial occupancy distribution; fixed capacity;
- initial infected count = 1;
- `beta`, `gamma`;
- network generation rule and acceptance criteria;
- quarantine count `k` and duration `D`;
- daily update order;
- maximum horizon;
- metric definitions.

## 3. Baseline and treatment conditions

- **Structural baseline:** `mu = 0`, no intervention; checks that infection cannot enter other tanks.
- **Policy baseline:** random tank quarantine under the same budget.
- **Untreated baseline:** no intervention at each transfer-rate level.
- **Treatment:** highest-betweenness tank quarantine.

Response delay has no effect under no intervention. It can be shown conceptually in a 4 x 3 x 3 matrix, but one transfer/network/epidemic block should not waste resources repeating an identical no-intervention run. Proposed unique condition structure:

```text
per transfer level:
  1 no-intervention baseline
  + 3 response delays × 2 quarantine strategies
```

Whether to repeat the baseline to balance the table: **no. Each transfer/network/epidemic block runs the no-intervention baseline once and reports it as a shared baseline (D007, frozen 2026-09-11)**.

## 4. Dependent variables

### Primary metrics

| Metric | Calculation | Relation to question |
|---|---|---|
| Final attack rate | `ever infected / 200` | primary final outbreak size; secondary policy effect |
| Number of affected tanks | tanks ever containing at least one `I` | primary system-wide spread; secondary policy effect |
| Peak infected population | `max I(t)` including `t=0` | severity/dynamics support |
| Time to extinction | first day with `I(t)=0`; censored otherwise | duration/dynamics support |

### Auxiliary metrics

- time to peak: the first day on which the peak is reached;
- intervention cost: `k × D` tank-days;
- relative reduction compared with random quarantine: `(random - targeted) / random` on the paired outcome.

No further metrics are added without a reason. Daily transfer acceptance, network metrics and initial-tank centrality are diagnostic variables, not additional headline outcomes.

## 5. Seed hierarchy and variance separation

### Network seeds

Each `network_seed` generates one independent modular network. Network-level summaries and the acceptance attempt must be saved. Several epidemic replicates are nested within the same network so that network-instance variance can be separated.

### Epidemic seeds

Each `epidemic_seed` controls the initial infected agent and the movement, infection and recovery draws. The same network/epidemic pair must be paired across all three strategies.

### Policy seeds

`policy_seed` controls only the random quarantine tank selection. The targeted strategy is deterministic; no intervention has no policy seed. Using several random policy seeds on the same network/epidemic pair allows random-policy selection variance to be estimated.

### Variance interpretation

- **Network-instance variance:** differences in outcome caused by different topologies.
- **Epidemic stochastic variance:** differences across initial/disease/movement draws with network and policy fixed.
- **Random-policy selection variance:** differences across randomly quarantined tanks with network and epidemic draws fixed.

The analysis must not merge these three variances into one uninterpretable error source.

## 6. Paired comparison design

Each comparison block is identified by at least this key:

```text
(network_seed, epidemic_seed, transfer_rate, response_delay, budget)
```

Within that block:

- the same network instance is used;
- the same initial infected agent is used;
- the same epidemic seed/substreams are used;
- random and targeted start on the same day, last the same `D`, and quarantine the same `k`;
- the only main difference is the selected tanks;
- the policy seed of the random strategy is recorded separately.

The main policy effect uses paired differences, not only a comparison of two independent means.

## 7. Pilot experiment

The pilot is not used to test the hypothesis or to pick a "good-looking" conclusion. It only checks that the model is in an informative regime and freezes the main-experiment parameters.

### Pilot questions

1. Under no intervention, is there intermediate behaviour other than "everything goes extinct quickly" and "almost everyone is infected"?
2. Do the transfer-rate levels produce distinguishable accepted movements?
3. Do the response-delay levels cover immediate, intermediate and late response?
4. Does the network generator reliably produce connected modular graphs with a non-trivial betweenness ranking?
5. Are `k`, `D` and capacity neither ineffective nor close to removing the whole network?
6. Is the 365-day working horizon sufficient?

### Preliminary pilot size

- 3-5 network seeds;
- 5-10 epidemic seeds per network;
- a small number of candidate parameter sets;
- output is used only for parameter freezing, bug discovery and runtime estimation.

The pilot selection criteria, every parameter set tried and every failure must be recorded, to avoid outcome-driven tuning.

## 8. Repetition recommendation

The course notes stress repeating stochastic experiments; this project needs layered variance estimates more than the 15-20 runs used in class. Preliminary formal design:

- at least 10 network seeds;
- at least 5 epidemic seeds per network, i.e. at least 50 network-epidemic blocks per main condition;
- 2-3 policy seeds per block for the random policy, if runtime allows.

This is a preliminary recommendation, not the final sample size. It is decided after the pilot from runtime, variance and confidence-interval stability, but no condition should have fewer than 30 replicates.

## 9. Parameter freezing

After the pilot, create a parameter-freeze record containing:

- selected transfer-rate and delay levels;
- fixed `beta`, `gamma`, capacity, `k`, `D`, `max_days`;
- network parameters and rejection rules;
- seed lists;
- planned run count;
- the reasons for each choice and the date;
- confirmation by both members.

Once the formal experiment starts, parameters must not change because results disagree with the hypothesis. If a bug is found, follow the failure protocol and rerun the complete affected seed set.

## 10. Raw results and provenance

Each future raw result is one line per run and contains at least:

- run ID, timestamp, commit hash, configuration hash;
- all parameter values and seeds;
- network ID, adjacency/centrality reference;
- selected quarantine tanks;
- status and stop reason;
- all predefined metrics;
- error/censoring fields.

Proposed storage layout:

```text
results/raw/        append-only raw run records (not manually edited)
results/summary/    reproducible aggregated tables
results/figures/    generated figures
experiments/config/ frozen machine-readable configurations
```

No such results or fake examples are created at this stage.

## 11. Anomalies and failed runs

- Anomalous results are never hidden, deleted or edited by hand.
- Every run must have a `completed`, `censored_max_days` or `failed` status.
- A valid configuration with an extreme outcome is not a failure; it is kept and explained.
- An invariant failure or exception must keep its configuration/seeds/error.
- A rerun is allowed only after an implementation bug is confirmed and the fixing commit is recorded; the whole affected block is rerun with the original seeds.
- Rerunning only an unfavourable or anomalous single outcome is not allowed.

## 12. Quantitative analysis

- For each condition report count, mean, median, standard deviation, IQR and a 95% confidence interval.
- For random vs targeted report the paired mean/median difference and a paired bootstrap CI.
- For final attack rate and affected tanks report the absolute difference first, and the relative reduction as well.
- The bootstrap should resample clusters by network instance, so replicates within one network are not treated as fully independent.
- Time to extinction is reported separately for censored runs; if censoring is not rare, use a suitable time-to-event summary rather than treating the horizon as extinction.
- p-values are not reported alone; effect size and uncertainty are the main basis for interpretation.

## 13. Qualitative analysis

- Show a few representative runs that are predefined or chosen by an objective rule, e.g. runs near the median, not the best-looking plots.
- Use a network diagram to mark regions, betweenness, quarantined tanks and affected tanks.
- Use S/I/R time series to explain the phases of spread.
- Show the difference in mechanism between a local-only outbreak and a cross-group outbreak.
- Every qualitative example must give its complete seeds and configuration.

## 14. Planned figures

1. Modular tank-transfer network, with node colour for region and node size for betweenness.
2. Final attack rate vs transfer rate, grouped by strategy and faceted by response delay, with uncertainty shown.
3. Number of affected tanks vs transfer rate, same layout.
4. Paired targeted-minus-random differences, by delay and transfer rate.
5. Peak infected population distributions.
6. Time-to-extinction distributions or censored summary.
7. Time series/network snapshots of one local outbreak and one cross-group outbreak.

No prototype data or figures are produced at this stage.

## 15. Sensitivity analysis

After the main experiment, only a small one-factor-at-a-time or small designed analysis:

- lower/higher `beta`;
- lower/higher `gamma`;
- homogeneous vs limited heterogeneous capacity;
- optional movement/update-order assumption.

The sensitivity analysis must not grow into a full Cartesian product of parameters and does not replace the main experiment.

## 16. Stop-running rules

- A single run stops at infection extinction; it is censored on reaching `max_days`.
- A formal batch must not stop early because a trend looks clear before the predefined seed list is complete.
- If the failure rate exceeds the preset threshold (working trigger 1%) or an invariant fails, pause the whole batch, investigate and record the decision.
- If runtime exceeds the timeline, first reduce the optional policy-seed replicates; do not drop core transfer/delay/strategy cells.

## 17. Decision status

Frozen (2026-09-11, see `decision-log.md`): capacity = 12, `k` = 2, `max_days` = 365, delay measured from introduction, shared baseline reporting, attack rate and affected tanks co-primary.

Numeric values to be frozen after the 19-25 Sep pilot (`model-specification.md` section 18, second layer):

- numeric transfer-rate levels;
- numeric response-delay levels;
- `beta`, `gamma`, `D`;
- network generation parameters `p_in` / `p_out`;
- final network/epidemic/policy replication counts.
