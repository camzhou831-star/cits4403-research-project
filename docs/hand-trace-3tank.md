# Hand Trace: 3 tanks, 6 agents, 3 days (issue #14)

This supports integration validation in `validation-plan.md` §9. The fixture is for validation only; it is not an experiment and produces no experimental results. Automated comparison tests are in `tests/test_hand_trace.py`. This document provides the hand-calculated reference: **expected values must be calculated by hand, never backfilled from model output**.

## 1. Scenario

| Item | Value |
|---|---|
| Tanks | T0 (region 0), T1 (region 0), T2 (region 1), capacity 12 |
| Agents | 0, 1, 2 in T0; 3, 4 in T1; 5 in T2 |
| Initial state | agent 0 = `I`, all others `S` |
| `beta` | 0.5 |
| `gamma` | 0.5 |
| Movement / intervention | None (M1) |
| Config | `design="scenario"`, `n_agents=6`, `n_tanks=3`, `max_days=10` |

Rule recap (spec §7, §8, §13): take a snapshot of the state at the start of each day. Each `S` agent with `I_j > 0` in its tank is infected with probability `P = 1 - (1 - beta)^{I_j}`; each `I` agent in the snapshot recovers with probability `gamma`. Both sets of draws are committed synchronously (recovery before infection). **Newly infected agents neither transmit nor recover that day; unexposed S agents consume no draw.**

## 2. Fixed draws (TableDraws)

Only draws that the specification requires to be consumed are listed. If the model reads a draw missing from the table, `TableDraws` raises an error, the run becomes `failed`, and the test fails.

| Day | Process | Agent | Draw | Threshold | Outcome |
|---|---|---|---|---|---|
| 1 | transmission | 1 | 0.30 | P = 1 − 0.5¹ = 0.50 | 0.30 < 0.50 → infected |
| 1 | transmission | 2 | 0.60 | 0.50 | 0.60 ≥ 0.50 → remains S |
| 1 | recovery | 0 | 0.70 | gamma = 0.50 | 0.70 ≥ 0.50 → remains I |
| 2 | transmission | 2 | 0.70 | P = 1 − 0.5² = **0.75** | 0.70 < 0.75 → infected (incorrectly using P = 0.5 would produce no infection, so this value tests whether the exponent is correct) |
| 2 | recovery | 0 | 0.20 | 0.50 | recovered |
| 2 | recovery | 1 | 0.90 | 0.50 | remains I |
| 3 | recovery | 1 | 0.40 | 0.50 | recovered |
| 3 | recovery | 2 | 0.10 | 0.50 | recovered |

Draws that must not be consumed (intentionally absent from the table): day 1 transmission for agents 3, 4, 5 (no I in their tanks); day 2 recovery for agent 2 (newly infected that day); any day 3 transmission (no S left in T0).

## 3. Day-by-day hand computation

**Day 0 (initial)**: S = {1,2,3,4,5} = 5, I = {0} = 1, R = 0. affected tanks = 1.

**Day 1**
- Snapshot: T0 contains 1 I (agent 0).
- Exposed S: agent 1 (P = 0.5, draw 0.30 → infected), agent 2 (draw 0.60 → not infected). Agents 3, 4, 5 are unexposed.
- Recovery: agent 0 (draw 0.70 → no recovery).
- Commit: agent 1 → I.
- Result: S = {2,3,4,5} = 4, I = {0,1} = 2, R = 0. new_infections = 1, recoveries = 0.

**Day 2**
- Snapshot: T0 contains 2 I (agents 0, 1).
- Exposed S: agent 2, P = 1 − (0.5)² = 0.75, draw 0.70 → infected.
- Recovery: agent 0 (0.20 → recovered), agent 1 (0.90 → no recovery). Agent 2 is newly infected that day and has no recovery draw.
- Commit (recovery before infection): agent 0 → R, agent 2 → I.
- Result: S = {3,4,5} = 3, I = {1,2} = 2, R = {0} = 1. new_infections = 1, recoveries = 1.
- T0 row: S 0 / I 2 / R 1; T1: 2/0/0; T2: 1/0/0.

**Day 3**
- Snapshot: T0 contains 2 I (agents 1, 2), no S and no transmission draw.
- Recovery: agent 1 (0.40 → recovered), agent 2 (0.10 → recovered).
- Result: S = 3, I = 0, R = 3. new_infections = 0, recoveries = 2. I = 0 → **extinction on day 3**, status `completed`.

## 4. Expected summary

| Day | S | I | R | new_inf | rec | affected_now | affected_ever |
|---|---|---|---|---|---|---|---|
| 0 | 5 | 1 | 0 | 0 | 0 | 1 | 1 |
| 1 | 4 | 2 | 0 | 1 | 0 | 1 | 1 |
| 2 | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| 3 | 3 | 0 | 3 | 0 | 2 | 0 | 1 |

Transition log (day, agent, from, to): (1,1,S,I), (2,0,I,R), (2,2,S,I), (3,1,I,R), (3,2,I,R).

Metrics: ever_infected 3, final_attack_rate 0.5, affected_tanks 1, peak_infected 2, time_to_peak 1, time_to_extinction 3, days_simulated 3.

## 5. Model comparison and sign-off

| Check | Result | Evidence |
|---|---|---|
| Daily S/I/R, new_infections, recoveries and affected tanks match on every day | Match | `tests/test_hand_trace.py::test_hand_trace_matches_event_log` (2026-09-11) |
| Transition log matches (including commit order) | Match | Same as above |
| Consumed draws are exactly the 8 in table 2, in the same order | Match | `draws.consulted` assertion |
| Run fails after removing the day 2 transmission draw for agent 2 | Fails as expected | `test_hand_trace_fails_loudly_if_an_unlisted_draw_is_consulted` |

Differences found: none.

- [ ] Member A independently recalculated and confirmed (date: )
- [x] Member B independently recalculated and confirmed (date: 2026-09-16)
