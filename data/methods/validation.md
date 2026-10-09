# Validation and reproduction evidence

This record combines the model's validation requirements with the hand trace, the two structural network audits and the clean-environment reproduction. Requirements are not evidence that a check ran or that a member signed off. The dated records below state what was observed and what remained unresolved. The model rules are in [model.md](model.md), experimental choices in [experiments.md](experiments.md), and decision history in [decisions.md](decisions.md).

Current paths use `src/tests/`, `utils/`, `data/config/`, `data/results/` and `data/figures/`. Quoted historical commands and Git provenance retain the paths used at the time. The reproduction record refers to the report snapshot at the recorded commit, not a verification of the separately submitted final university report.

## Validation requirements

The original plan required conformance to the model specification, reproducible stochastic behaviour, equal intervention budgets and random conditions, correct extreme-case behaviour, and a distinction between logic errors, invalid configurations and valid stochastic outcomes.

### Invariants

| ID | Invariant | Required evidence |
|---|---|---|
| V001 | Total agent count always equals 200 | Daily summary agrees with agent-table count |
| V002 | Every agent belongs to exactly one tank | Location uniqueness check |
| V003 | Every agent state is S, I or R | Enum/domain validation |
| V004 | `S + I + R = 200` every day | Daily assertion and summary |
| V005 | Recovered agents cannot be reinfected | No `R -> I` in transition log |
| V006 | Tank occupancy does not exceed capacity | Check after each movement |
| V007 | Quarantined tanks allow neither incoming nor outgoing transfers | Movement-event audit |
| V008 | Transmission can still occur inside quarantined tanks | Controlled scenario review |
| V009 | Random and targeted policies use the same `k`, start and duration | Paired configuration comparison |
| V010 | Centrality uses only the pre-outbreak network | Provenance and immutable network hash |
| V011 | The same configuration and seeds give the same outputs | Repeated deterministic replay |
| V012 | Each run reaches extinction or an explicit horizon status | Recorded stop reason |

### Extreme and boundary cases

| ID | Case | Required behaviour |
|---|---|---|
| V101 | `beta = 0` | Initial infected agents may recover; no `S -> I` transition occurs. Final ever-infected count equals the initial infected count. |
| V102 | `transfer_rate = 0` | No accepted cross-tank movement; infection stays in the initial infected tank and affected tanks remains 1. |
| V103 | `gamma = 1` | Existing infected agents transmit according to update order, then recover at their first eligible recovery step. |
| V104 | `beta = 1` in an infected tank | All susceptible agents sharing a tank with at least one infectious agent become infected in the transmission commit. Newly infected agents neither transmit nor recover until the next day. |
| V105 | `transfer_rate = 1` | Every eligible agent attempts movement once; capacity and quarantine still hold. Accepted rate may be below 1 because of capacity or no destination. |
| V106 | Full tank | Incoming movement cannot violate capacity. A blocked movement is recorded, not treated as a simulation failure. |
| V107 | Quarantine boundaries | Movement is blocked on `[start, end)` and allowed again at `end`, before that day's movement stage. |
| V108 | Zero-day response | Intervention is active before the first movement stage and does not alter the initial state retroactively. |
| V109 | No intervention | No tank enters quarantine, cost is 0, and changing the unused response-delay label cannot change the run. |
| V110 | Betweenness tie | Exact ties resolve by ascending `tank_id`, unless an explicit documented decision changes the rule. |

### Configuration, fairness and future information

Before a run starts, reject invalid configurations without silent clamping. Require `0 <= beta, gamma, transfer_rate <= 1`; valid non-negative or positive integers as appropriate for response delay, duration, `k`, capacity and `max_days`; `k <= 20`; initial occupancy no greater than capacity; exactly 20 tanks in 4 regions of 5; a simple, undirected, connected network with cross-region edges; and serialisable, recorded seeds.

Within a paired block, check identical network hash, epidemic seed, initial infected agent/tank, transfer rate, beta, gamma, capacity, response day, quarantine count, duration and cost. Targeted selection must follow the pre-outbreak centrality ranking. Random selection must match the policy seed and sample without replacement. The selected tanks should be the only main policy difference.

Save the pre-outbreak network hash and centrality table. The selector interface accepts topology, `k` and policy seed, not epidemic state or outputs. For a fixed network seed, targeted tanks must stay unchanged across epidemic seeds. Code review must check whether the selector reads daily infection or movement records.

Replay selected configurations twice and compare daily events, selected tanks, final metrics and stop reason. Results must be byte-equivalent or equivalent as canonical data. A network seed changes topology, an epidemic seed changes epidemic/movement randomness, and a policy seed changes only random quarantine selection.

Model-level plausibility checks are not real-world calibration. Investigate unexplained decreases in mean accepted transfers as transfer rate increases, and require `mu = 0` to produce only a local outbreak. Earlier intervention need not improve every seed, but aggregate anomalies require investigation. High betweenness should correspond to cross-region shortest paths, and the generator should not frequently yield symmetric networks with identical centrality at every node.

### Integration and completion criteria

Use a small network, fixed draws and independently hand-calculated movement, infection, recovery and quarantine steps to check the event log. The [M1 hand trace](#hand-trace) contains 3 tanks, 6 agents, 3 days and 8 fixed draws, with comparison tests in `src/tests/test_hand_trace.py`. It uses `turtlefarm.scenario.Layout` and `design="scenario"`; formal `design="main"` remains fixed at 200 agents and 20 tanks. The experiment runner must reject `design != "main"`. The original plan called for extending this fixture with movement and quarantine after M2; the M1 evidence below does not establish that extension.

The pre-formal completion requirements were: all V001-V012 pass; V101-V110 conform to the specification; same-seed replay and fairness checks pass; both members independently read and sign off on the event trace; and no unexplained invariant failure remains. Every run must stop at extinction, `censored_max_days` or `failed`. The incomplete personal sign-off recorded below remains incomplete.

## Hand trace

This hand-calculated reference was recorded for issue #14. It is a validation fixture, not a formal experiment. Expected values must be calculated by hand, never backfilled from model output.

### Scenario and fixed draws

| Item | Value |
|---|---|
| Tanks | T0 (region 0), T1 (region 0), T2 (region 1), capacity 12 |
| Agents | 0, 1, 2 in T0; 3, 4 in T1; 5 in T2 |
| Initial state | Agent 0 is `I`; all others are `S` |
| `beta` | 0.5 |
| `gamma` | 0.5 |
| Movement / intervention | None (M1) |
| Config | `design="scenario"`, `n_agents=6`, `n_tanks=3`, `max_days=10` |

Take a snapshot at the start of each day. Each susceptible agent in a tank with `I_j > 0` becomes infected with probability `P = 1 - (1 - beta)^{I_j}`. Each infectious agent in the snapshot recovers with probability `gamma`. Commit both sets of draws synchronously, with recovery before infection in the transition log. Newly infected agents neither transmit nor recover that day; unexposed susceptible agents consume no draw.

`TableDraws` contains only required draws. Reading a missing draw raises an error, makes the run `failed`, and fails the test.

| Day | Process | Agent | Draw | Threshold | Outcome |
|---|---|---|---|---|---|
| 1 | transmission | 1 | 0.30 | P = 1 − 0.5¹ = 0.50 | 0.30 < 0.50: infected |
| 1 | transmission | 2 | 0.60 | 0.50 | 0.60 ≥ 0.50: remains S |
| 1 | recovery | 0 | 0.70 | gamma = 0.50 | 0.70 ≥ 0.50: remains I |
| 2 | transmission | 2 | 0.70 | P = 1 − 0.5² = 0.75 | 0.70 < 0.75: infected; incorrectly using P = 0.5 would miss this infection |
| 2 | recovery | 0 | 0.20 | 0.50 | Recovered |
| 2 | recovery | 1 | 0.90 | 0.50 | Remains I |
| 3 | recovery | 1 | 0.40 | 0.50 | Recovered |
| 3 | recovery | 2 | 0.10 | 0.50 | Recovered |

Intentionally absent draws are day 1 transmission for agents 3, 4 and 5 (no infectious agent in their tanks), day 2 recovery for agent 2 (newly infected), and all day 3 transmission (no susceptible agent left in T0).

### Daily calculation and expected output

On day 0, `S = {1,2,3,4,5}`, `I = {0}` and R is empty. One tank has been affected. On day 1, T0 has one infectious agent in the snapshot. Agent 1 becomes infected, agent 2 remains susceptible, and agent 0 remains infectious. The state is `S = {2,3,4,5}`, `I = {0,1}` and R is empty.

On day 2, T0 has two infectious agents. Agent 2's infection probability is `1 − (0.5)² = 0.75`; its draw of 0.70 causes infection. Agent 0 recovers and agent 1 remains infectious. After committing recovery before infection, `S = {3,4,5}`, `I = {1,2}` and `R = {0}`. Tank S/I/R counts are T0: 0/2/1, T1: 2/0/0 and T2: 1/0/0.

On day 3, T0 has two infectious agents and no susceptible agents, so no transmission draw occurs. Agents 1 and 2 both recover. `S = 3`, `I = 0`, `R = 3`: extinction occurs on day 3 with status `completed`.

| Day | S | I | R | new_inf | rec | affected_now | affected_ever |
|---|---|---|---|---|---|---|---|
| 0 | 5 | 1 | 0 | 0 | 0 | 1 | 1 |
| 1 | 4 | 2 | 0 | 1 | 0 | 1 | 1 |
| 2 | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| 3 | 3 | 0 | 3 | 0 | 2 | 0 | 1 |

The transition log `(day, agent, from, to)` is `(1,1,S,I), (2,0,I,R), (2,2,S,I), (3,1,I,R), (3,2,I,R)`. Expected metrics are `ever_infected = 3`, `final_attack_rate = 0.5`, `affected_tanks = 1`, `peak_infected = 2`, `time_to_peak = 1`, `time_to_extinction = 3` and `days_simulated = 3`.

### Comparison and personal sign-off

| Check | Recorded result | Evidence |
|---|---|---|
| Daily S/I/R, new infections, recoveries and affected tanks match every day | Match | `src/tests/test_hand_trace.py::test_hand_trace_matches_event_log` (2026-09-11) |
| Transition log matches, including commit order | Match | Same test |
| Consumed draws are exactly the 8 above, in the same order | Match | `draws.consulted` assertion |
| Remove the day 2 transmission draw for agent 2 | Fails as expected | `test_hand_trace_fails_loudly_if_an_unlisted_draw_is_consulted` |

The record reports no differences. Member B independently recalculated and confirmed on 2026-09-16. Member A's independent recalculation checkbox and date were still blank. This consolidation does not supply the missing sign-off.

## Network audit criteria and measurement

The structural audits address issue #16, issue #5, decision D005 and risk R002. They check network generation and target structure; they contain no epidemic simulation and are not evidence for epidemic hypotheses.

Each attempt samples edges in the lexicographic order of `itertools.combinations(range(20), 2)`, with within-region probability `p_in`, cross-region probability `p_out`, and `PCG64(SeedSequence(network_seed, spawn_key=(attempt,)))`. Accept a network only if it is connected, has at least one cross-region edge, is not complete, and does not have identical betweenness at every node. Record every rejection reason; after 100 failed attempts, raise `NetworkGenerationError` with the complete rejection record.

Betweenness is unweighted, exact rather than sampled, normalised node betweenness from NetworkX. Ties mean exactly equal calculated values and resolve by ascending `tank_id` (V110); `tie_groups` and `tie_ids_at_rank(k)` use the same rule. The network hash is the first 16 characters of SHA-256 over regions and edges, recorded for V010. `src/tests/test_network.py::test_golden_hash_literal` locks the seed-0 golden hash.

The following criteria were written before inspecting the original 10-seed table. The follow-up retained their numerical thresholds, expanding C1 to 30 seeds.

| Criterion | Threshold | Rationale |
|---|---|---|
| C1 | All sampled seeds accepted within 100 attempts; mean prior rejections ≤ 1 | Stable generation without failed seeds |
| C2 | Modularity ≥ 0.45 | A few bridges should connect otherwise separated regions |
| C3 | Mean cross-region edge count of 5-10 | Avoid extremely rare cross-group spread or a structure approaching uniform mixing |
| C4 | Rank-1 betweenness ≥ 4 × median, with no exact rank-2 tie | Identifiable targets under R002 |
| C5 | Rank-1 tank carries ≥ 40% of cross-region shortest paths | A structural relationship between betweenness and cross-region paths |

For aggregate comparisons, modularity and path shares are means across accepted networks; C4 compares mean rank-1 betweenness with 4 times mean within-network median betweenness and requires `tie_at_k = 0`. An aggregate pass does not mean every network meets each threshold.

`failed` counts seeds with no accepted network within 100 attempts. `mean_attempt` and `max_attempt` use the zero-based accepted-attempt index, equal to prior rejections: 0 is first-attempt acceptance, 1 is second-attempt acceptance. `mean_deg`, `inter_edges`, `density`, `clustering`, `modularity` and `diameter` are means across accepted networks; modularity uses the fixed partition into four regions. `bc_top1`, `bc_top2` and `bc_median` average rank-1, rank-2 and within-network median betweenness. `distinct_bc` averages the number of distinct betweenness values. `tie_at_k` counts seeds with an exact tie at rank 2, including a tie between ranks 1 and 2. `top1_is_bridge` counts seeds whose rank-1 tank has a cross-region edge.

For each network, `top1_xpath` and `top2_xpath` average over cross-region node pairs, excluding pairs with the tested tank as an endpoint. Each pair contributes the fraction of its shortest paths that pass through the tank as an interior node. The displayed values average those shares across networks. Within-region connectivity means links between tanks in the same region, not turtle contacts inside a tank.

## Network audit: 2026-09-11

This original structural pilot used seeds 0-9, `k = 2`, 20 tanks in 4 regions of 5, and 16 candidate pairs. Wording was revised and cross-path metrics added after the 2026-09-11 review. The original plan proposed freezing values after the 19-25 September movement pilot, with at least 30 network seeds checked before freezing. The [later audit](#network-audit-2026-10-08) records that the larger check instead occurred after the formal experiment.

Historical reproduction command:

```bash
source .venv/bin/activate
python scripts/audit_network.py --seeds 10 --k 2
```

The generator was `turtlefarm/network.py`. Its current location is `src/turtlefarm/network.py`; the current audit command is `python utils/audit_network.py --seeds 10 --k 2` from the repository root with the documented environment active.

### Full 10-seed grid

The original numeric table is retained. `tie_at_k` and `top1_is_bridge` are counts out of 10.

| p_in | p_out | failed | mean_attempt | max_attempt | mean_deg | inter_edges | density | clustering | modularity | diameter | bc_top1 | bc_top2 | bc_median | distinct_bc | tie_at_k | top1_is_bridge | top1_xpath | top2_xpath |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.030 | 0 | 2.800 | 6 | 2.740 | 6.200 | 0.144 | 0.218 | 0.515 | 7.700 | 0.475 | 0.406 | 0.092 | 14.500 | 0 | 10 | 0.576 | 0.495 |
| 0.500 | 0.050 | 0 | 1.100 | 4 | 2.990 | 9.500 | 0.157 | 0.234 | 0.420 | 6 | 0.373 | 0.287 | 0.075 | 16.200 | 0 | 10 | 0.440 | 0.333 |
| 0.500 | 0.080 | 0 | 0.400 | 2 | 3.310 | 12.500 | 0.174 | 0.254 | 0.363 | 5.300 | 0.275 | 0.238 | 0.074 | 17.500 | 0 | 10 | 0.324 | 0.280 |
| 0.500 | 0.100 | 0 | 0.400 | 2 | 3.680 | 16.200 | 0.194 | 0.265 | 0.302 | 4.900 | 0.263 | 0.205 | 0.059 | 18.100 | 0 | 10 | 0.308 | 0.237 |
| 0.600 | 0.030 | 0 | 1.900 | 6 | 3.000 | 6 | 0.158 | 0.295 | 0.539 | 6.700 | 0.426 | 0.361 | 0.071 | 15.900 | 0 | 10 | 0.532 | 0.441 |
| 0.600 | 0.050 | 0 | 0.400 | 1 | 3.300 | 8.800 | 0.174 | 0.303 | 0.476 | 6 | 0.360 | 0.272 | 0.068 | 16.700 | 0 | 10 | 0.440 | 0.330 |
| 0.600 | 0.080 | 0 | 0.100 | 1 | 3.640 | 11.800 | 0.192 | 0.317 | 0.419 | 5.200 | 0.233 | 0.199 | 0.073 | 17.800 | 0 | 10 | 0.284 | 0.239 |
| 0.600 | 0.100 | 0 | 0.100 | 1 | 4.010 | 15.500 | 0.211 | 0.298 | 0.358 | 4.700 | 0.220 | 0.177 | 0.060 | 18.800 | 0 | 10 | 0.265 | 0.208 |
| 0.700 | 0.030 | 0 | 1 | 3 | 3.340 | 5.700 | 0.176 | 0.446 | 0.571 | 6.700 | 0.407 | 0.358 | 0.054 | 15.100 | 1 | 10 | 0.512 | 0.450 |
| 0.700 | 0.050 | 0 | 0.300 | 1 | 3.610 | 8.300 | 0.190 | 0.425 | 0.515 | 5.600 | 0.351 | 0.278 | 0.060 | 17.100 | 0 | 10 | 0.438 | 0.345 |
| 0.700 | 0.080 | 0 | 0.100 | 1 | 3.990 | 11.800 | 0.210 | 0.406 | 0.449 | 4.700 | 0.239 | 0.203 | 0.060 | 17.800 | 0 | 10 | 0.297 | 0.247 |
| 0.700 | 0.100 | 0 | 0.100 | 1 | 4.360 | 15.500 | 0.229 | 0.376 | 0.390 | 4.200 | 0.215 | 0.178 | 0.048 | 18.600 | 0 | 10 | 0.264 | 0.218 |
| 0.800 | 0.030 | 0 | 1 | 3 | 3.750 | 5.700 | 0.197 | 0.575 | 0.593 | 6.200 | 0.412 | 0.356 | 0.040 | 14.500 | 0 | 10 | 0.518 | 0.449 |
| 0.800 | 0.050 | 0 | 0.300 | 1 | 3.960 | 8.300 | 0.208 | 0.501 | 0.537 | 5.400 | 0.343 | 0.273 | 0.051 | 16.900 | 0 | 10 | 0.430 | 0.342 |
| 0.800 | 0.080 | 0 | 0.100 | 1 | 4.360 | 11.800 | 0.229 | 0.476 | 0.477 | 4.400 | 0.239 | 0.189 | 0.053 | 18 | 0 | 10 | 0.299 | 0.234 |
| 0.800 | 0.100 | 0 | 0.100 | 1 | 4.730 | 15.500 | 0.249 | 0.436 | 0.420 | 3.900 | 0.199 | 0.165 | 0.043 | 18.700 | 0 | 10 | 0.247 | 0.203 |

### Original interpretation and D005 candidate

All 16 × 10 networks generated within 100 attempts. At `p_out = 0.03`, prior rejections reached 6, with means of 1-2.8. At `p_out = 0.05`, they reached 4 for `p_in = 0.5` and at most 1 for `p_in >= 0.6`; at `p_out >= 0.08`, the maximum was 2. The original reading identified C1 passes for combinations with `p_out >= 0.05` and `p_in >= 0.6`, and all combinations with `p_out >= 0.08`.

The original interpretation described modularity as rising when `p_out` falls, over approximately 0.30-0.59. At `p_out = 0.10`, modularity remained 0.30-0.42 and `p_in` was 5-8 times `p_out`, so these were weaker modular networks rather than uniform mixing; approximately 15 cross-region edges failed C3. At `p_out = 0.05`, the reported ranges were 8-10 cross-region edges and modularity 0.42-0.54; at `p_out = 0.03`, approximately 6 edges and 0.52-0.59.

The recorded rank-1-to-median ratio ranged from 3.7 (0.6/0.10) to 10.3 (0.8/0.03); all combinations with `p_out <= 0.05` had ratios at least 4.8. Only 0.7/0.03 had an exact rank-2 tie, once among its seeds and the only such tie among the 160 networks. The rank-1 tank had a cross-region edge in 10/10 seeds for every candidate, which alone was weak evidence of its bridge role. The original path-share reading was approximately 43-44% at `p_out = 0.05`, 51-58% at 0.03 and 25-32% at `p_out >= 0.08`; rank 2 carried approximately 33-35% at 0.05. `p_in` mainly changed clustering (approximately 0.22 to 0.58) and within-region connectivity redundancy, with little change in bridge structure.

The audit identified 0.6/0.05, 0.7/0.05 and 0.8/0.05 as meeting C1-C5. Their cross-region structures were similar: `inter_edges` 8.3-8.8, `top1_xpath` 0.43-0.44 and modularity 0.48-0.54; clustering differed at approximately 0.30 / 0.43 / 0.50. It preferred `p_in = 0.6`, `p_out = 0.05` because this was already the M1 default and had the lowest within-region density of these candidates, a mean of 6 edges among 10 possible pairs per region. It was a preference, not a unique solution. The suggested alternative was 0.7/0.05 if the movement pilot showed inadequate within-region path redundancy, such as frequent disconnection after quarantine.

The 0.6/0.03 alternative had fewer bridges and a stronger bridge effect, but failed C1, reached 6 prior rejections and had a larger diameter. The audit also mentioned 0.6/0.08 if cross-group spread proved too rare, while describing it as marginal on C3 and C5. It required a movement pilot and expansion to at least 30 seeds before freezing D005, with the decision recorded in the decision log and issue #5. These statements retain the original candidate rationale; they do not retrospectively satisfy the promised pre-freeze check.

## Network audit: 2026-10-08

The follow-up was recorded on 2026-10-08 (Australia/Perth), after the 2026-10-06 parameter freeze and formal experiment. Selected parameters 0.6/0.05 pass the expanded C1 check but fail the original C4 no-tie clause. At seed 12, tanks 7 and 13 tie at ranks 1 and 2, so both are selected for `k = 2`. The absence of a tie across the selected/excluded boundary does not turn the literal C4 failure into a pass.

### Provenance and command

The worktree was clean before the audit. Branch `docs/english-documentation` was at base commit `c9aa3d49eeab63c36c3bd0b43bbe4c79230007ae`. The recorded comparison found its model and scripts identical to `origin/main` at `2b2fbaf2f8210d7a8e550e054f8eae37db2c6f81`, using the historical command `git diff --exit-code origin/main HEAD -- turtlefarm scripts`.

Both historical files below were last changed by commit `ff1ad5bce149a83d46cd5e4122e36e407347f3bd` on 2026-09-11.

| Historical file | Git blob |
|---|---|
| `scripts/audit_network.py` | `f440fbab0b4910b417d57bb9161b15162abae3a9` |
| `turtlefarm/network.py` | `9faf2c753b774797a1d623d52d011f8ae7a1eac7` |

The working directory was `/Users/junhe/IT/4403/cits4403-docs-cleanup`. The exact historical command was:

```bash
/Users/junhe/IT/4403/cits4403-notebook/.venv/bin/python -B scripts/audit_network.py --seeds 30 --k 2
```

It exited successfully under Python 3.12.14, NumPy 2.5.2 and NetworkX 3.6.1. `-B` disables bytecode writes; the script imported the model from the working repository. The absolute interpreter path records that environment and is not a required layout. The current command, with this checkout's documented environment active, is:

```bash
python -B utils/audit_network.py --seeds 30 --k 2
```

Seeds 0-29 inclusive, `k = 2`, 20 tanks in 4 regions of 5, and the original 16 candidates were used: `p_in = 0.5 / 0.6 / 0.7 / 0.8`, each with `p_out = 0.03 / 0.05 / 0.08 / 0.10`. Seeds 0-9 overlap the earlier audit; seeds 10-29 extend it. These structural seeds differ from the formal experiment's network seeds 200-219.

### Full 30-seed grid

The script's numeric output is retained, with floats rounded to three decimal places where printed. Counts are out of 30. All 480 candidate/seed combinations generated successfully; generation alone does not imply a pass on C1-C5.

| p_in | p_out | failed | mean_attempt | max_attempt | mean_deg | inter_edges | density | clustering | modularity | diameter | bc_top1 | bc_top2 | bc_median | distinct_bc | tie_at_k | top1_is_bridge | top1_xpath | top2_xpath |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.030 | 0 | 2.700 | 10 | 2.693 | 5.633 | 0.142 | 0.257 | 0.532 | 8 | 0.497 | 0.411 | 0.085 | 13.767 | 2 | 30 | 0.603 | 0.502 |
| 0.500 | 0.050 | 0 | 0.600 | 4 | 2.973 | 8.367 | 0.156 | 0.265 | 0.460 | 6.633 | 0.399 | 0.333 | 0.072 | 15.667 | 1 | 30 | 0.481 | 0.395 |
| 0.500 | 0.080 | 0 | 0.233 | 2 | 3.347 | 12.100 | 0.176 | 0.258 | 0.381 | 5.400 | 0.295 | 0.236 | 0.069 | 17.533 | 2 | 30 | 0.350 | 0.274 |
| 0.500 | 0.100 | 0 | 0.233 | 2 | 3.660 | 15.233 | 0.193 | 0.259 | 0.326 | 4.767 | 0.250 | 0.195 | 0.062 | 18.233 | 0 | 30 | 0.293 | 0.226 |
| 0.600 | 0.030 | 0 | 1.267 | 6 | 2.977 | 5.200 | 0.157 | 0.370 | 0.568 | 7.467 | 0.462 | 0.389 | 0.066 | 14.867 | 1 | 30 | 0.572 | 0.479 |
| 0.600 | 0.050 | 0 | 0.200 | 1 | 3.273 | 7.867 | 0.172 | 0.356 | 0.503 | 6.200 | 0.387 | 0.310 | 0.064 | 16.267 | 1 | 30 | 0.475 | 0.377 |
| 0.600 | 0.080 | 0 | 0.067 | 1 | 3.640 | 11.467 | 0.192 | 0.335 | 0.429 | 5.033 | 0.272 | 0.220 | 0.063 | 17.767 | 1 | 30 | 0.330 | 0.264 |
| 0.600 | 0.100 | 0 | 0.067 | 1 | 3.977 | 14.833 | 0.209 | 0.319 | 0.372 | 4.533 | 0.233 | 0.184 | 0.055 | 18.633 | 0 | 30 | 0.281 | 0.220 |
| 0.700 | 0.030 | 0 | 0.733 | 5 | 3.340 | 5.100 | 0.176 | 0.490 | 0.591 | 6.933 | 0.444 | 0.384 | 0.052 | 14.033 | 2 | 30 | 0.556 | 0.478 |
| 0.700 | 0.050 | 0 | 0.167 | 1 | 3.610 | 7.700 | 0.190 | 0.456 | 0.531 | 5.733 | 0.369 | 0.307 | 0.054 | 16.233 | 0 | 30 | 0.460 | 0.382 |
| 0.700 | 0.080 | 0 | 0.067 | 1 | 3.977 | 11.467 | 0.209 | 0.404 | 0.456 | 4.767 | 0.268 | 0.212 | 0.055 | 17.900 | 0 | 30 | 0.330 | 0.261 |
| 0.700 | 0.100 | 0 | 0.033 | 1 | 4.290 | 14.767 | 0.226 | 0.372 | 0.400 | 4.233 | 0.224 | 0.181 | 0.049 | 18.800 | 0 | 30 | 0.273 | 0.223 |
| 0.800 | 0.030 | 0 | 0.500 | 3 | 3.713 | 5.100 | 0.195 | 0.616 | 0.609 | 6.367 | 0.448 | 0.374 | 0.037 | 13.100 | 1 | 30 | 0.563 | 0.470 |
| 0.800 | 0.050 | 0 | 0.133 | 1 | 3.957 | 7.700 | 0.208 | 0.548 | 0.552 | 5.467 | 0.361 | 0.302 | 0.047 | 15.967 | 0 | 30 | 0.453 | 0.379 |
| 0.800 | 0.080 | 0 | 0.033 | 1 | 4.340 | 11.500 | 0.228 | 0.487 | 0.482 | 4.433 | 0.258 | 0.206 | 0.050 | 17.800 | 0 | 30 | 0.321 | 0.256 |
| 0.800 | 0.100 | 0 | 0.033 | 1 | 4.667 | 14.767 | 0.246 | 0.447 | 0.431 | 4 | 0.206 | 0.168 | 0.047 | 18.800 | 0 | 30 | 0.255 | 0.208 |

### Selected parameters and limits

| Criterion | Observation for 0.6 / 0.05 | Result |
|---|---|---|
| C1 | 30/30 generated; mean prior rejections 0.200; maximum prior rejections 1, so at most 2 actual attempts | Pass |
| C2 | Mean modularity 0.5033778099 ≥ 0.45 | Pass on aggregate comparison |
| C3 | Mean cross-region edge count 7.8666666667, within 5-10 | Pass |
| C4 | Mean rank-1 / mean median betweenness = 6.0717848797 ≥ 4, but 1/30 seeds has an exact rank-2 tie | Fail: no-tie clause |
| C5 | Mean rank-1 cross-region path share 0.4748678228 ≥ 0.40 | Pass on aggregate comparison |

Of the 30 selected-parameter networks, 24 were accepted on the first attempt and 6 after one rejection. All 6 rejected attempts failed because the graph was disconnected. No seed exhausted the 100-attempt limit.

The sole rank-2 tie is at seed 12, accepted attempt index 0, network hash `5c9bbf8078da0b56`. Tanks 7 and 13 have exactly equal normalised betweenness, `0.4093567251461988`. Ascending tank ID puts 7 first and 13 second; `top_k(2)` selects both. The tie does not cross the selection boundary, but `ties_at_rank(2) = 2`, so the original no-rank-2-tie condition fails. The audit did not change the tie definition or threshold.

For selected parameters, modularity ranges from 0.4062 to 0.6072, with 5/30 networks below 0.45. Cross-region edge counts range from 4 to 13. Rank-1 path share ranges from 0.2671 to 0.7427, with 9/30 below 0.40. In 6/30 networks, rank-1 betweenness is less than 4 times that network's median. These per-network diagnostics do not revise the selection rules.

Across the grid, C1 fails for 0.5/0.03 and 0.6/0.03 because their mean prior-rejection counts are 2.700 and 1.267. All seeds still generated within the limit; the largest count was 10 prior rejections at 0.5/0.03, meaning acceptance on the eleventh attempt. All candidates at `p_out = 0.03` or 0.05 meet aggregate C2, C3 and C5. All at `p_out >= 0.08` fail C3 and C5; C2 also fails there except for 0.7/0.08 and 0.8/0.08.

Only 0.7/0.05 and 0.8/0.05 meet all C1-C5 in this 30-seed sample under the unchanged aggregate criteria and strict no-tie clause. The selected 0.6/0.05 parameters remain a C1 pass with a disclosed C4 exception. The audit did not choose replacement parameters or reinterpret the completed experiment.

Thirty deterministic seeds provide a finite structural check, not a guarantee for unseen seeds. Candidates share a seed range and are not 16 independent samples. Network and shortest-path metrics do not measure epidemic spread, quarantine effectiveness or sensitivity of the research conclusions. This audit changed no model, configuration or epidemic result file and ran no epidemic simulation. It does not establish that the promised check preceded freezing. The limitation was also disclosed in the university-submission report.

The audit itself supplied no personal sign-off and recorded Member B's D005 confirmation as pending at that stage. The later decision record and PR #43 record retrospective D004/D005 confirmations on 2026-10-08 and closure of issues #4 and #5; see [decisions.md](decisions.md). Those limited confirmations do not waive the C4 failure, establish a pre-freeze audit, or sign off other validation gates.

<a id="reproduction-2026-10-06"></a>

## Clean-environment reproduction: 2026-10-06

This historical check asked whether a fresh clone could regenerate committed results and the report without reusing the working copy. It predates the blocked-by-cause counters. Its Stage 2 table is retained as `data/results/pilot/stage2-criteria-legacy-proxy.csv`. A later Stage 2 rerun with those counters reproduced every previously recorded summary value; formal parameters and results stayed unchanged. The pilot history is in [experiments.md](experiments.md).

### Environment and comparison criteria

The run cloned branch `docs/readme-diagram-contribution` at `8d7311f` into a temporary directory, without the historical `results/raw/` directory. A new environment used `uv venv --python 3.12` (Python 3.12.13) and `uv pip install -r requirements.txt`: NumPy 2.5.2, NetworkX 3.6.1, pandas 3.0.5 and Matplotlib 3.11.1.

The recorded README sequence was tests; pilot stage 1, both rounds; `pilot_select.py stage1 --force`; pilot stage 2; `pilot_select.py stage2`; `formal`; `formal-nested`; `analyse_results.py` for both formal designs; the historical report builder `build_report.py`; and `draw_concept_diagram.py`. The script names record that execution sequence, rather than a claim that it was rerun during documentation consolidation. Current retained analysis and diagram scripts are under `utils/`.

Before comparing outputs, the check required exact matches for analysis tables, pilot criterion tables, the Stage 2 design and the report. It excluded run provenance fields: `run_id`, timestamps and `code_commit`. Paths in this table use the current layout, except that the historical report is identified in prose.

| Output | Recorded result |
|---|---|
| Tests | 166 passed (167 after the fix below) |
| Pilot selection | Same choice: `beta` 0.2, `gamma` 0.1, transfer levels 0 / 0.01 / 0.025 / 0.1, delays 1 / 12 / 33, `D` 14 |
| `data/results/pilot/*`, `data/config/pilot-stage2-intervention.json` | Byte-identical |
| `data/results/summary/formal*.csv` (all 10,400 runs) | Identical in every cell except `run_id` and `code_commit` |
| `data/results/summary/pilot-*.csv` (9,950 runs) | Identical in every result cell; `configuration_hash` differed as explained below |
| `data/results/analysis/formal-nested/*` (tables, figures 1-7) | Byte-identical except `fig7-selection.json`, which stores the run's `run_id` |
| Historical report snapshot and `data/figures/concept-diagram.png` | Byte-identical |
| `data/results/analysis/formal/*` | Analysis crashed; see the finding below |

Runtimes on that machine were 33 s, 41 s and 111 s for the three pilot stages, and 100 s and 104 s for the two formal runs.

### Failures, fixes and resume limitation

`analyse_results.py formal` crashed when Figure 2 raised `'yerr' must not contain negative values`. When every value in a cell is identical, for example one affected tank at transfer rate 0, a cluster-bootstrap bound can differ from the mean by approximately 1e-16 and make the error-bar length slightly negative. The crash first appeared during round-2 review fixes; filtering command output through `grep` hid the traceback.

The committed crossed-seed `formal` analysis then had stale figures 2-3 and three missing summary files. Its report tables had been written before the crash and were correct; that run appeared only in Appendix D of the historical report. The fix clipped error-bar lengths at 0, added a regression test that fails without the fix, and regenerated all outputs. `formal-nested`, the reported experiment, was unaffected.

Pilot configuration hashes also changed after parameter freeze. `SimulationConfig.to_dict()` includes `provisional_fields`, which had five entries during the pilot and was empty after freeze commit `f4eac85`. The same pilot configuration therefore hashes differently even though result values are unaffected. Using `--resume` with a pre-freeze pilot raw file would fail to recognise completed runs and rerun all of them. Formal runs were made after freezing and are unaffected. The record documents this limitation rather than changing the old hashes.

The resulting pipeline practice was to use `set -o pipefail` so a failure inside a filtered command stops the sequence.

## Follow-up acceptance checks

The separate [follow-up](followup.md) leaves the original 5,200 formal runs unchanged. Its protocol commit `03fbb54` preceded its simulations but followed inspection of the original results. All 19,000 follow-up runs completed with no failures or censoring, and all 400 replayed original conditions match. The follow-up document records batch acceptance evidence; the requirements below still apply to reproductions.

- Compare original `RunRecord` values with and without observation, including infectious arrival followed by same-day recovery, no qualifying event, and local S-to-I infection outside the initial region. Observation must preserve random draws, update order and epidemic state.
- Verify exactly the planned keys: 20 networks, five distinct nested epidemic seeds per network, one shared baseline per block and all duration/delay/strategy/policy combinations. Report failures and censoring; refuse missing, duplicate or inconsistent arms in paired analysis.
- Check identical network hashes and selected random pairs across paired conditions. Each network reuses 20 policy draws across epidemic replicates, durations and delays. Report duplicate pairs and region coverage; do not substitute seeds to obtain a preferred sample.
- Compare replayed baselines and targeted `D = 14` conditions with matching original formal outcomes. Execution IDs, timestamps and implementation commits may differ, but epidemic outcomes, networks and targeted tanks must agree.
- Verify compact-record and observation versions, protocol hash and configuration hashes. Check append-only persistence, incompatible-resume refusal, failure preservation and the cumulative failure guard before further append operations. Check that the exclusive raw-file lock rejects overlapping coordinators. Crash recovery must confirm the recorded process is inactive before removing only its lock.
- Pair contrasts before aggregation, average random outcomes within epidemic blocks, and bootstrap complete networks together. Keep non-activated blocks in primary comparisons. Distinguish missing event times from day zero and report event incidence separately.
- Reproduce analysis from saved summaries. Label intervals pointwise and contrasts exploratory. Budgets are equal within a duration; duration contrasts also change cost. Policy-prefix checks and conditional Monte Carlo error must account for policy-choice reuse across epidemic replicates.

Use the commands in [experiments.md](experiments.md) and the observation/compact-record definitions in [result-schema.md](result-schema.md). Record actual test execution separately from batch acceptance. Neither follows merely from this checklist or the original formal experiment's validation.
