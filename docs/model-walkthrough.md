# Daily model walkthrough

Prepared on 2026-10-08 for issue #18. **Status: guide prepared; completed session not recorded.**

Member B (Wenhao Zhang) presents; Member A (Cam Zhou) attends and asks questions. Allow about 10 minutes. The purpose is to demonstrate understanding of the daily update and its invariants, as required by [collaboration-plan.md §7](collaboration-plan.md#7-ensuring-both-members-understand-the-full-model). Preparing this guide or running tests does not establish that either member has presented it.

## Preparation

Open [model.py](../src/turtlefarm/model.py), [rng.py](../src/turtlefarm/rng.py), [entities.py](../src/turtlefarm/entities.py) and the [3-tank hand trace](hand-trace-3tank.md). Use the Python 3.12 project environment described in the [README](../README.md#reproducing-the-results). Only the focused tests below are needed; this session does not require a pilot or formal experiment rerun.

Record the revision actually used and any local changes:

```bash
git rev-parse HEAD
git status --short
```

## Ten-minute sequence

| Time | Presenter task | Code to open |
|---|---|---|
| 0:00-1:00 | Identify agent state, tank membership and the day-0 snapshot. | `Agent`, `Tank`; `Simulation._initialise()` |
| 1:00-2:00 | Follow one call to `step()` and explain quarantine activation and release. | `Simulation.step()`, `_management_update()` |
| 2:00-3:00 | Explain an attempted move and when capacity changes become visible. | `Simulation._movement_stage()` |
| 3:00-5:00 | Derive infection probability, identify who may recover and explain synchronous commit. | `Simulation._transmission_and_recovery()`, `_commit()`, `_transition()` |
| 5:00-6:00 | Explain why skipping a random draw does not shift later paired draws. | `EventKeyedDraws.uniform()`, `TableDraws.uniform()` |
| 6:00-7:00 | Show invariant checks, daily recording and the stopping decision. | `Simulation._check_invariants()`, `_record()`, `run()` |
| 7:00-9:00 | Work through day 2 of the hand trace, then compare it with the test. | `tests/test_hand_trace.py`, `test_hand_trace_matches_event_log` |
| 9:00-10:00 | Answer the check questions and record any corrections or follow-up. | Session record below |

All `Simulation` methods above are in [model.py](../src/turtlefarm/model.py); random-draw classes are in [rng.py](../src/turtlefarm/rng.py). `Agent` and `Tank` are in [entities.py](../src/turtlefarm/entities.py).

## Points to explain

**Day and index conventions.** Day 0 records initial conditions before any movement or disease update. `step()` increments `self.day` first, so its first call executes day 1. In a normally completed run, `daily[0]` is day 0 and `daily[d]` is the end-of-day record for day `d`. Agent and tank IDs start at 0 and index their respective lists. Explicit validation layouts enforce contiguous IDs in [scenario.py](../src/turtlefarm/scenario.py), `Layout.validate()`.

**Management before movement.** Tanks are selected from the pre-outbreak network during initialisation. `_management_update()` releases expired quarantines, then activates a pending intervention once. The first possible activation day is `max(1, response_delay)`. A quarantine starting on day `s` lasts on days `s` through `s + D - 1`; release occurs before movement on day `s + D`. An outbreak that ends before activation has zero intervention cost. Quarantine restricts transfers, while disease updates inside the tank continue.

**Movement is sequential.** With non-zero `transfer_rate`, one event-keyed `movement` draw per agent determines both attempt eligibility (`draw < transfer_rate`) and processing order; ties use agent ID. At zero transfer rate, this stage returns without consulting movement draws. An open origin may send an agent only to an adjacent, open tank with spare capacity, chosen uniformly using `movement_destination`. Membership and `tank_id` change immediately, so later attempts see the new occupancy. An infectious arrival immediately marks the destination as ever affected. Blocking counters attribute an attempt first to origin quarantine, then to destination quarantine if an otherwise available quarantined neighbour exists, otherwise to capacity/no-neighbour blocking. They are rule-attribution counts, not additional successful transfers prevented.

**Disease decisions use a frozen snapshot.** After all movement, `_transmission_and_recovery()` counts infectious agents in each tank and saves their IDs in `infectious_today`. Each susceptible agent with `I_j > 0` has infection probability `1 - (1 - beta)**I_j`; an unexposed susceptible agent consumes no transmission draw. Recovery uses `draw < gamma` only for agents in `infectious_today`. Both results are pending lists: this method does not change disease states.

**Commit follows both sets of draws.** `_commit()` applies recoveries first, then infections. This is still a synchronous disease update because both disjoint lists were decided from the same snapshot. An infectious agent may contribute to transmission and recover on the same day. A newly infected agent cannot transmit or recover until the next day. With `gamma=1`, the initial case recovers on day 1; an agent infected on day `d` recovers on day `d + 1`. `_transition()` permits only `S -> I` and `I -> R` and updates `state_entered_day`.

**Pairing concerns draws, not identical outcomes.** `EventKeyedDraws` keys each uniform value by epidemic seed, process, day and agent ID; agent `a` reads array position `a`. Skipping an exposure leaves later keyed values unchanged. Different strategies may nevertheless encounter different eligible destinations or exposures. Initial-case selection has its own stream, network generation uses `network_seed`, and random tank selection uses `policy_seed`. `TableDraws` instead supplies explicit values for validation and rejects any unlisted lookup.

**Checks precede recording; stopping follows recording.** `_check_invariants()` checks the configured population total, valid states, unique tank membership, matching locations, capacity and quarantine timing. `_transition()` guards legal disease transitions, and `_record()` checks that blocking causes sum to the total. `run()` then checks the recorded infectious count: zero means completed; otherwise reaching `max_days` means `censored_max_days`. Censoring is not extinction, and `time_to_extinction` is `None`. An invariant failure during `run()` produces a failed record with an error and provenance.

## Hand-trace exercise and test commands

Use the existing fixture, with 3 tanks, 6 agents, `beta=gamma=0.5` and no movement or intervention. These are validation settings, not formal experiment settings. Ask Member B to calculate day 2 before opening the expected values in the test:

- At its snapshot, agents 0 and 1 are infectious in T0. Agent 2 has infection probability `1 - 0.5**2 = 0.75`; draw `0.70` schedules infection.
- Recovery draws `0.20` for agent 0 and `0.90` for agent 1 schedule only agent 0's recovery. Agent 2 receives no recovery draw that day.
- Commit records `(2, 0, I, R)` before `(2, 2, S, I)`. The result is `S=3, I=2, R=1`. Day 3 ends with `S=3, I=0, R=3` and extinction.

In [test_hand_trace.py](../tests/test_hand_trace.py), `test_hand_trace_matches_event_log` checks daily values, transition order and all 8 consulted draws. The missing-draw test verifies that an incomplete table fails. Expected values must remain hand-calculated; do not regenerate them from the model.

Run from the repository root in the project environment:

```bash
source .venv/bin/activate
python -m pytest -q tests/test_hand_trace.py tests/test_paired_draws.py
python -m pytest -q tests/test_extreme_cases.py tests/test_movement.py
python -m pytest -q tests/test_quarantine.py -k "V107 or V108"
python -m pytest -q tests/test_invariants.py -k "V001_daily or V002_duplicate or V012_horizon"
```

The selected tests cover explicit draws and pairing, infection/recovery timing, movement and capacity, quarantine boundaries, population conservation, duplicate membership and censoring. Useful examples to open are `test_V103_transmit_then_recover_within_a_day`, `test_V104_newly_infected_do_not_transmit_or_recover_on_their_infection_day`, `test_V107_quarantine_interval_is_half_open_and_releases_before_end_day_movement` and `test_V002_duplicate_membership_is_detected` in their corresponding test files above.

Member A should ask: Why does `gamma=1` still permit transmission that day? Why can movement use updated occupancy while disease decisions use a snapshot? What would an unexpected recovery draw for agent 2 do to the hand trace? Record the actual answers and any correction, rather than assuming that passing tests demonstrates understanding.

## Session record: complete only after the walkthrough

The [contribution record](collaboration-plan.md#8-contribution-record) lists Member B's local rerun and update-order check under issue #13, and independent hand-trace work under issue #14. Those are prior verification activities. They do not establish that this 10-minute walkthrough occurred. Retain their historical records separately.

| Field | Actual session record |
|---|---|
| Status | Guide prepared; completed session not recorded |
| Actual date, time and duration | Pending |
| Presenter | Member B (Wenhao Zhang); participation pending |
| Attendee | Member A (Cam Zhou); participation pending |
| Repository revision and local changes | Pending; record the actual commit and working-tree state used |
| Code and tests discussed or run | Pending; include actual command results where run |
| Questions and Member B's answers | Pending |
| Corrections and follow-up owners | Pending; record "none" only if confirmed during the session |
| Outcome | Pending; record what was demonstrated and what remains unresolved |
| Both members' confirmation | Pending |

Issue #18 remains open; this prepared guide is not a record of completion or human sign-off.
