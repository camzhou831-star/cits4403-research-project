# Research Plan Index and Decision Register

This file is the entry point for the non-code preparation stage. The authoritative details are in:

- `research-proposal.md` - why and what we study;
- `model-specification.md` - exact model behaviour;
- `assumptions.md` - numbered assumptions;
- `experiment-plan.md` - primary experiment and analysis;
- [followup-protocol.md](followup-protocol.md) - separate quarantine-duration and random-policy sensitivity design;
- `validation-plan.md` - future tests and verification;
- `timeline.md` and `risk-register.md` - delivery control.

## Fixed decisions

- Project title: **Bridge Transfers and Quarantine in a Captive Turtle Farm**.
- Model framing: **a stylised explanatory model**.
- 200 synthetic agents; 20 tanks; 4 regions × 5 tanks.
- Agent disease states: `S / I / R`.
- Tank management states: `open / quarantined`.
- No individual `Q` state in MVP.
- Quarantine blocks movement into/out of a tank but not internal transmission.
- Modular, non-uniform transfer network; bridge tanks may have high betweenness.
- Targeted policy uses only pre-outbreak network information.
- Strategies: no intervention, random quarantine, highest-betweenness quarantine.
- Primary experiment factors: transfer rate, response delay, strategy only.
- Primary metrics: final attack rate, affected tanks, peak infected, time to extinction.
- All population, network and experiment data are synthetic.

## Decision status

The facilitator raised no objections at Checkpoint 1 (2026-09-07). The team adopted the working proposals as final values on 2026-09-11. See `decision-log.md` for the full record and `model-specification.md` §18 for the two-layer freeze rule.

| ID | Decision | Final value | Status | Alternatives considered |
|---|---|---|---|---|
| D001 | Response-delay origin | From outbreak introduction at `t=0` | Frozen 2026-09-11 | First detection requires observation model and larger scope |
| D002 | Tank capacity | 12 for all tanks | Frozen 2026-09-11 | Higher value reduces blocking; heterogeneous value adds confounding |
| D003 | Quarantined tank count `k` | 2 | Frozen 2026-09-11 | Larger budget may remove much of a 20-node network |
| D004 | Quarantine duration `D` | Candidate after pilot | Value pending pilot (issue #4) | Too short has little effect; too long approximates permanent removal |
| D005 | Network `p_in/p_out` | Candidate after structural pilot | Value pending pilot (issue #5) | Must be modular, connected and non-symmetric |
| D006 | `max_days` | 365 | Frozen 2026-09-11 | Too short causes censoring; too long wastes runtime |
| D007 | No-intervention reporting | Shared baseline per transfer/network/epidemic block | Frozen 2026-09-11 | Repeated delay labels give balanced table but duplicate identical runs |
| D008 | Headline outcome | Attack rate and affected tanks co-primary | Frozen 2026-09-11 | Facilitator may prefer one for presentation emphasis |

## Decision process

1. Ask facilitator using `facilitator-questions.md`.
2. Record answer and date in `decision-log.md` and the relevant issue.
3. Update specification, assumptions, experiment plan and checkpoint material together.
4. Obtain approval from both members.
5. Freeze decisions before implementation.

## Quarantine follow-up

The [follow-up protocol](followup-protocol.md) was committed in `03fbb54` before its simulations, after the original results were known. Its 19,000 sensitivity runs at transfer rate 0.025 completed without failures or censoring, separately from the original 5,200-run formal experiment. It crosses durations of 7, 14 and 28 days with delays of 1, 12 and 33 days, using 20 random-policy draws per network. Draws can select duplicate pairs and are reused across conditions within a network.

The same 20 networks and 100 epidemic blocks support paired comparisons, not independent confirmation. Strategies have equal budgets within each duration; comparisons across durations change cost. Event observations distinguish infectious arrivals from local infections without changing the epidemic rules. The [experiment plan](experiment-plan.md#15-sensitivity-analysis) gives commands, output paths and interpretation limits; the [validation plan](validation-plan.md#11-follow-up-acceptance-checks) lists acceptance requirements. The [follow-up results](followup-results.md) record the findings and agreement of all 400 replayed original conditions.

## Non-code stage exit criteria

- [x] Canonical questions and hypothesis documented.
- [x] Model states, interactions and update order documented.
- [x] Experiment, validation, collaboration, timeline and risks documented.
- [x] Checkpoint brief and speaking notes prepared.
- [x] Facilitator resolves or accepts pending decisions (no objections at Checkpoint 1; recorded on 2026-09-11).
- [x] Both members confirm the final specification (issue #10, 2026-09-06/07).
- [x] Collaborator access and first cross-review evidence verified (PR #19 approved by Member B, 2026-09-06).
- [ ] Official rubric/submission details checked when released.
