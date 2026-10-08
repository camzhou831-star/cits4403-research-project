# Risk Register

Likelihood/impact use Low / Medium / High. The owner is the main person following up, not the only member responsible.

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| R001 | Unclear definition of a bridge tank | Medium | High | Use pre-outbreak normalized betweenness; record ties; obtain facilitator confirmation | A | The two members cannot independently select the same targeted tanks |
| R002 | Network is too symmetric, with all betweenness values close or identical | Medium | High | Stochastic modular generator, structure rejection criteria, multiple seeds | A | Most networks have many centrality ties |
| R003 | Infection does not spread in any experiment | Medium | High | Check the beta/gamma/transfer regime in the pilot; document choices transparently | A+B | Most no-intervention runs have only the initial case |
| R004 | All experiments infect the entire population | Medium | High | Avoid a saturated regime in the pilot; do not tune parameters to support the hypothesis | A+B | Attack rate is close to 1 in most conditions |
| R005 | Too many parameter combinations | High | High | Keep only 3 factors in the main experiment; use limited sensitivity checks for others | B | Estimated runs/runtime exceed the timeline |
| R006 | No real disease calibration | High | Medium | State that this is a stylised explanatory model; do not extrapolate using real-world units | A | Documents start using claims about "real risks/recommendations" |
| R007 | Model is misinterpreted as a real-world prediction | Medium | High | State limitations in every external document; cross-review claims | Both | Report/presentation claims to "prove something about real turtle farms" |
| R008 | Centrality strategy uses future information | Low | High | Selector receives only the pre-outbreak network; provenance and review | A reviewer B | Selected tanks change with epidemic outcomes |
| R009 | Unfair intervention-budget comparison | Medium | High | Assert same k/start/duration/network/seed; paired audit | B reviewer A | Strategies have inconsistent cost/config |
| R010 | Unequal Git contributions between the two members | Medium | High | Issues, PR reviews, weekly contribution table, early escalation | Both | One member has no visible contribution for 2 consecutive weeks |
| R011 | Experiments cannot be reproduced | Medium | High | Explicit seeds, config hash, commit hash, fresh rerun | B reviewer A | same config/seed gives different result |
| R012 | Direct reuse of old assessed/restricted code | Low | High | New implementation, PR integrity checklist, source inventory | Both | PR contains old coursework/vendor code |
| R013 | Inconsistent results across report, code, figures and demo | Medium | High | Single frozen result set, cross-file consistency check | Both | The same metric has different values in different materials |
| R014 | Later changes to rubric/submission requirements | Medium | High | Facilitator/LMS check, assign owner, update docs promptly | B | official requirements newly published |
| R015 | Unclear meaning of response delay | High | High | Ask explicitly at the Checkpoint; freeze introduction vs detection before implementation | A | Documents disagree on the starting point of the delay |
| R016 | Capacity blocks most transfers | Medium | Medium | Record attempted/accepted ratio in the pilot; adjust fixed capacity once | A | Accepted/attempted rate remains close to 0 |
| R017 | Time horizon is too short, causing excessive censoring | Low | Medium | Check in the pilot; handle time-to-event data transparently | B | Censored runs exceed the working 5% trigger |
| R018 | Random policy variance obscures policy comparison | Medium | Medium | Multiple policy seeds or a nested variance summary | B | Random strategy CI is driven mainly by tank choice |
| R019 | Outcome-driven pilot tuning | Medium | High | Write pilot criteria in advance; retain all attempts; require both members to approve the freeze | Both | Parameters are changed because they "do not support the hypothesis" |
| R020 | Model development reduces time for analysis and reporting | Medium | High | MVP gate; feature freeze on 3 October; remove optional work first | Both | Must-have implementation extends beyond 18 September |

## Escalation order

1. Protect research validity, academic integrity and reproducibility first.
2. Then protect the must-have primary experiment.
3. Remove optional extensions rather than weaken fair comparisons or hide failures.
4. If teammate availability or official requirements have a major impact, contact the facilitator/unit coordinator early.

## Evidence update (2026-10-08)

| Risk | Evidence and remaining action |
|---|---|
| R002: network symmetry and ties | The expanded structural audit generated all 30 selected-parameter networks within the retry limit. One seed has an exact tie at ranks 1 and 2, so the original C4 no-tie clause fails; both tanks are selected for `k=2`. Runtime tie-breaking remains deterministic. Record the team's decision on accepting this limitation; do not report an all-criteria pass. See `network-audit-2026-10-08.md`. |
| R009: budget fairness | The formal setting is `k=2`, `D=14`, a planned 28 tank-days when quarantine starts. Recomputing the Stage 2 criteria reproduces the existing selection; it does not establish a counterfactual number of prevented transfers. |
| R010: contribution and understanding | The contribution table has been updated to distinguish merged work from pending reviews. Issue #18's joint walkthrough is still unrecorded; `model-walkthrough.md` supplies preparation material, not evidence that it took place. |
| R013: inconsistent documentation | Current specifications and plans now state the settings used in the formal design. Checkpoint 1 scripts retain their historical wording with a current-status note. The expanded network-audit limitation is included in the report. |
| R019: outcome-driven tuning and sign-off | The 30-seed follow-up occurred after the formal experiment. Parameters and criteria remain unchanged, and its failed C4 clause is reported. Member B's outstanding confirmations remain pending; neither this update nor merging its PR backdates approval. |
