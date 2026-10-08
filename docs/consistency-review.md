# Documentation Consistency Review

Review date: 2026-09-02. Scope: all tracked project documents in the non-code preparation package.

Sections 1-5 are the historical preparation review, not a claim about today's implementation, results or available rubric. The current D004/D005 review is recorded in §8. Current submission-time uncertainty is stated in the README; the historical deadline row below is not confirmation of the LMS deadline.

## 1. Local sources checked before authoring

The following are English descriptions of local sources held by the original reviewer, not repository paths. The original machine-specific paths are retained in Git history.

- *CITS4403 Local Asset Read-only Review and Topic Recommendations* (PDF, 11 pages) - reviewed scope, recommended direction, MVP, academic-integrity boundary and Checkpoint wording.
- CITS4403 knowledge-base note L01, *Introduction to Complexity Science* - model/question framing, explanatory vs predictive models, repeated stochastic runs.
- CITS4403 knowledge-base note L02, *Graph Theory Basics and ER Random Graphs* - graph definitions, random baselines, connectivity and repeated instances.
- CITS4403 knowledge-base note L03, *Small-world and Scale-free Networks* - clustering, path length, degree distribution, WS/BA limitations and network-model comparison.
- Local course summary `CITS4403 - 20 Jul 20-s1-full.md` - simple/valid/robust models, simulation vs model, project 25%, academic integrity.
- Local course summary `CITS4403 - 27 Jul 20-s1-full.md` - network assumptions, ER baseline, dynamic/static network meaning and GitHub collaboration requirement.
- Local course summary `CITS4403 - 03 Aug 20-s1-full.md` - WS/BA, betweenness-related structural reasoning, qualitative/quantitative comparison and model limitations.
- Local course summary `CITS4403 - 17 Aug 20-s1-full.md` - Week 7 checkpoint, 5-10 minute meeting, repository and GitHub evidence.
- Graph1 and Graph2 course notebooks - random seeds, repeated graph experiments, clustering/path/degree measures and model fitting workflow. No lab code copied.
- CITS1401 L22/L23 simulation notes - repeated random experiments, seed reproducibility, spiral development and unit/integration testing concepts. No assessed code copied.
- Current repository status and existing README/docs/commit history.

## 2. Availability findings

- All requested local notes, notebooks and the audit PDF were accessible.
- No separate local document containing the complete final report format, page limit, final technical submission format or full rubric was found.
- Course summaries support a Week 7 checkpoint and GitHub evidence; the user-supplied brief states Weeks 7-8. Documents therefore use "Weeks 7-8" and avoid a fabricated exact appointment.

## 3. Canonical consistency checks

| Check | Required value | Status |
|---|---|---|
| Primary question | Exact canonical sentence | Pass |
| Secondary question | Exact canonical sentence | Pass |
| Agent states | `S / I / R` only | Pass |
| Tank states | `open / quarantined` only | Pass |
| Individual Q state | Absent from MVP | Pass |
| Quarantine meaning | Blocks transfer in/out; internal spread continues | Pass |
| Strategies | None / Random / Highest-betweenness | Pass |
| Budget fairness | Same k/start/duration/network/epidemic seed | Pass |
| Main factors | transfer rate / response delay / strategy | Pass |
| Main metrics | attack rate / affected tanks / peak I / extinction time | Pass |
| Data | fully synthetic | Pass |
| Framing | stylised explanatory, not predictive | Pass |
| Future information | prohibited for policy selection | Pass |
| Results claims | no model/results claimed | Pass |
| Deadline | completion/freeze before 2026-10-09 23:59 | Pass |

## 4. Conflicts found and resolved

The initial repository documents contained three conflicts with the fixed design:

1. They described an individual SIR-Q model. Resolved to agent `S/I/R` plus tank `open/quarantined`.
2. They placed infection probability, recovery probability and capacity in the main experimental factors. Resolved: these are fixed in the main experiment and only limited sensitivity factors.
3. They combined primary and secondary questions into one sentence. Resolved by using the exact two canonical questions in all public-facing documents.

No unresolved contradiction remains among current canonical documents. Items not yet known are explicitly marked `Decision pending facilitator confirmation`.

## 5. No-code verification

- No `.py`, `.R`, `.java`, `.c` or new `.ipynb` model file was created in this phase.
- No simulation was run.
- No prototype data, chart, confidence interval or result was manufactured.
- Documents state that prototype results will only be added after implementation.

## 6. Review to repeat after facilitator meeting

If any D001-D008 decision changes, update at minimum:

- `model-specification.md`;
- `assumptions.md`;
- `experiment-plan.md`;
- `checkpoint-1-brief.md`;
- `checkpoint-1-speaking-notes.md`;
- `risk-register.md`;
- this consistency matrix.

## 7. Re-review record

| Date | Trigger | Outcome | Documents updated |
|---|---|---|---|
| 2026-09-11 | Checkpoint 1 held; no decision value changed; D001-D003, D006-D008 status pending → frozen | Status-only change; §6 semantic-update list not triggered | `decision-log.md`, `model-specification.md` (§1 note, §3, §6.2, §11, §14, §18), `research-plan.md`, `experiment-plan.md` (§3, §17), `assumptions.md`, `README.md`, `checkpoint-1.md`, `src/turtlefarm/config.py` |
| 2026-10-08 | Issues #4/#5: reconcile documentation with completed experiments and add the promised structural follow-up | D=14 and p_in/p_out=0.6/0.05 unchanged; Q1-Q3 recomputation matches; C1 passes on 30 seeds, C4 no-tie clause fails once; member confirmation remains pending | All seven documents in §6, `decision-log.md`, both network audits, `pilot-protocol.md`, `README.md`, report template and generated report |

## 8. D004/D005 consistency check (2026-10-08)

| Check | Current record | Outcome |
|---|---|---|
| Duration and alternatives | D=14; compared with 7 and 21 using Q1-Q3 | Matches the formal design and the criterion table recomputed from 5,550 Stage 2 rows |
| Q1 interpretation | 95.7% of started runs have at least one quarantine-attributed block at D=14 | Operational rule interception only; post-hoc denominator and measurement timing remain disclosed |
| Network probabilities | p_in=0.6, p_out=0.05 | Matches formal configuration; alternatives and rationale recorded in `decision-log.md` |
| Runtime acceptance | Connected, cross-region edge present, not complete, betweenness not all equal; at most 100 attempts | Unchanged; distinct from the C1-C5 candidate-comparison criteria |
| Expanded structural check | 30 seeds; mean 0.2 prior rejections, maximum 1; one exact rank-2 tie | C1 passes; C4 no-tie clause fails. Both tied tanks are selected; team acceptance of the limitation remains pending |
| Historical material | Checkpoint 1 scripts and the original structural audit | Preserved, with dated/current-status links rather than rewritten as if the results were known earlier |
| Decision approval | Member A's selection dated 2026-10-06; Member B confirmation pending | No personal sign-off inferred; issues #4 and #5 stay open |
| Model and results | Model code, experiment configurations, recorded epidemic data and figures | Unchanged; report regenerated only to add the structural limitation |

This check documents evidence and consistency. It does not approve unrelated protocol deviations, waive a failed criterion, or record the joint walkthrough required by issue #18.
