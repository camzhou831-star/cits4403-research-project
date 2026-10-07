# Collaboration Plan

## 1. Team and communication

| Member | Initial focus | GitHub |
|---|---|---|
| Member A - Cam Zhou | Model rules, network generation, validation, methods structure | `camzhou831-star` |
| Member B - Wenhao Zhang | experiment design, intervention strategy, statistics/visualisation planning, results structure | `Winston-2hang` |

- Primary communication channel: **To be confirmed by the team**.
- Backup channel / phone: **To be confirmed by the team**.
- Regular meetings: at least 2 per week, 30-45 minutes each; one reviews technical work, and the other reviews research interpretation and progress.
- Hold additional joint reviews before Checkpoints, the formal experiment freeze and the report freeze.

The project must not simply be divided into "one person writes code and the other writes the report". Each member must be able to explain the full model, research questions, experimental fairness and main results.

## 2. Shared responsibilities

Both members share responsibility for:

- Confirming research questions, the hypothesis and assumptions;
- Cross-reviewing model and experiment changes;
- Checking seeds, budgets and metric definitions together;
- Interpreting model limitations and results together;
- Attending Checkpoints together;
- Keeping the report, code, figures and spoken claims consistent;
- Identifying assessed/restricted material to prevent inappropriate reuse.

## 3. GitHub workflow

### Main branch

- Keep only reviewable, documented, reproducible work on `main`.
- Do not merge substantial model/experiment/report changes directly into `main` without review.

### Feature branches

Suggested names:

```text
docs/model-specification
model/sir-baseline
model/modular-network
intervention/tank-quarantine
experiment/paired-runner
analysis/primary-metrics
report/methods
```

### Pull requests

- Substantial changes require a pull request;
- PR descriptions include purpose, assumptions changed, validation evidence and affected documents/results;
- Merge only after at least one other member has reviewed it;
- Reviewers check research implications, budget fairness and future-information leakage as well as code style;
- Small typos may be committed directly, but commits should remain focused.

### Issues and task tracking

Create an issue for every must-have task, including:

- acceptance criteria;
- owner and reviewer;
- due date;
- dependencies;
- status;
- linked PR/commit.

Create separate decision issues for pending decisions. When closing them, record the choice, alternatives and rationale.

## 4. Commit messages

Suggested format:

```text
docs: define response-delay decision
model: add SIR daily transition rules
test: cover zero-transfer invariant
experiment: freeze primary seed matrix
analysis: add paired attack-rate summary
fix: preserve capacity during movement
```

Principles:

- Each commit expresses one main change;
- The message describes the intent, rather than saying "update files";
- Do not commit secrets, real customer data, virtual environments or unexplained raw output;
- Experiment/result commits must link to the config and code version.

## 5. Review requirements by work type

| Work | Author checks | Reviewer checks |
|---|---|---|
| Model rule | Consistent with the specification; explicit edge cases | Whether research meaning changes; whether it can be implemented independently |
| Network/intervention | No future information; centrality provenance | fairness, ties, budget, seed handling |
| Experiment config | Frozen parameters; complete seed list | pairing, controls, run count, scope |
| Analysis | Includes failed/censored runs; consistent metric definitions | uncertainty, effect size, no cherry-picking |
| Report | Claims supported by results; explicit limitations | Consistent with code/figures; no overstated real-world implications |

## 6. Conflict resolution

1. Write the disagreement as a specific modelling/engineering decision.
2. Each member explains the alternatives and their effects on the research question, runtime and interpretation.
3. Refer to `model-specification.md`, facilitator feedback and the frozen experiment plan.
4. If it cannot be resolved within 24 hours, record it in an issue and ask the facilitator.
5. Update the relevant documents after deciding; do not leave the decision only in a conversation.

The branch author resolves Git merge conflicts first, then the reviewer confirms that no meaning was lost. Do not use a destructive reset to overwrite the other member's work.

## 7. Ensuring both members understand the full model

- Hold one 10-minute model walkthrough each week, alternating the lead speaker.
- Member A must be able to explain experiment pairing, CIs and plots; Member B must be able to explain daily updates, state transitions and invariants.
- Before the pilot, both members independently draw a daily update flow from the specification, then compare them.
- Before Checkpoints and presentations, swap speaking sections during rehearsal so both can answer questions about the other's part.
- Major model changes require explicit approval from both members in the issue/PR.

## 8. Contribution record

Evidence sources:

- GitHub issues and assignments;
- feature branches and commits;
- PR descriptions and reviews;
- meeting notes and decisions;
- experiment ownership and verification records;
- report section authorship plus cross-review.

Update the contribution table weekly:

Last updated: 2026-10-06 (issue #18); first completed on 2026-09-20. Each row includes only evidence recorded on GitHub. "No record" means there is no review or comment on the PR page, not that no verbal communication took place.

| Week | Task | Primary owner | Reviewer / verification | Issue/PR | Outcome |
|---|---|---|---|---|---|
| W7 (1-4 Sep) | Non-code research design package (proposal, spec, assumptions, experiment/validation plans, timeline, risks) | Member A | Both members signed off the spec (issue #10) | #10 | Done |
| W8 (5-11 Sep) | Python environment and pinned requirements | Member A | — | #11 | Done |
| W8 | M1 baseline SIR, config validation, seed streams | Member A | Member B approve | #12 / PR #19 | Merged |
| W8 | Checkpoint 1 prediction and rehearsal script | Member B | Merged by Member A; revised following review (commit 2026-09-07) | PR #20 | Merged |
| W8 | Checkpoint 1 feedback, D001-D003 / D006-D008 freeze, two-layer freeze rules | Member A | @Member B requested to review; no review record on the PR | #1-#3, #6-#9 / PR #21 | Merged |
| W8 | Event-keyed paired draws, formal V-tests, scenario layouts | Member A | Member B recorded a local rerun and update-order check in issue #13 | #13 / PR #22 (merged via PR #23) | Done |
| W8-W9 | 3-tank hand trace | Written by Member A; independently recalculated by Member B | Both members signed off in issue #14 | #14 / PR #24 | Done |
| W8 | Modular network generator, structural checks, betweenness ranking, structural audit | Member A | Review follow-up in commit `ff1ad5b`; no review record on the PR | #16 / PR #23 | Merged |
| W9 (12-18 Sep) | Run metadata and raw-result schema | Member B | Merged by Member A; `tests/test_runner.py` checks every field against schema §2 and `RunRecord` | #15 / PR #25 | Merged 2026-09-20 |
| W9 | Network-constrained movement and capacity | Member B | No review record on the PR (self-merged) | #26 / PR #27 | Merged |
| W9 | Tank quarantine strategies and Checkpoint 2 demo script | Member B | No review record on the PR (self-merged); Member A reran 111 tests and the demo on `origin/main` on 2026-09-20 | #28 / PR #29 | Merged |
| W10 (19-25 Sep) | Batch experiment runner, design files, pilot protocol draft | Member A | Merged by Member B on 2026-10-03; no review comments on the PR page; confirmation of pilot selection criteria still awaits Member B's sign-off (pilot-protocol §7) | #30 / PR #31 | Merged |
| W10 | Checkpoint 2 speaking notes, contribution table, README gate update | Drafted by Member A; Member B responsible for their own sections | Approved by Member B and merged on 2026-10-03 | #18 / PR #32 | Approved; but merged into `experiment/batch-runner` rather than `main` (see the workflow gap below); contents recovered through PR #35 |
| W10-W11 | Conceptual system diagram | Originally assigned to Member B; actually drawn by Member A (2026-10-06, `scripts/draw_concept_diagram.py`) | Member A merged PR #35 into the PR #34 branch on 2026-10-06; no review record on the PR #35 page; awaiting Member B's review in PR #34 | #17 / PR #35 → PR #34 | Enters `main` with PR #34 |
| W11 (2-6 Oct) | Pilot runs (two Stage 1 rounds, Stage 2) and parameter freeze | Member A | Member B's confirmation pending: the pilot ran before their protocol sign-off; the deviation is recorded in decision-log | #4, #5 / PR #34 | In review |
| W11 | Pilot selection implementation, formal experiment (`formal`, rerun as `formal-nested` after crossed seeds were identified), analysis, figures 1-7 | Member A | Two read-only acceptance reviews with Codex CLI (ACCEPT WITH FIXES; fixes in PR #34); awaiting Member B's review | #4, #5 / PR #34 | In review |
| W11 | Full report draft (numbers rendered by script), reference checks | Member A | Awaiting Member B's review; Member B to cross-check how well 3 references support the associated claims | PR #34 | In review |
| W11 | README completion, contribution-table update, recovery of PR #32 contents, clean-environment reproduction, Checkpoint 3 speaking notes and demo plan | Member A | As above: merged via PR #35 into the PR #34 branch; speaking notes and demo plan were pushed after PR #35 merged and merged separately (merge `6fe077f`); awaiting Member B's review | #17, #18 / PR #35 → PR #34 | Enters `main` with PR #34 |

Known workflow gap (recorded 2026-09-20): PR #27 and PR #29 were self-merged by their author, with no review by the other member on the PR pages. This does not meet the model-change review requirements in §5. Remedy: Member A has rerun the full tests and demo on `origin/main`; from issue #30 onwards, model / experiment PRs must have a GitHub review record from the other member before merging.

Known workflow gap (recorded 2026-10-06): PR #32 was stacked on `experiment/batch-runner`. PR #31 merged that branch into `main` first, and PR #32 merged 3 minutes later, so it merged only into `experiment/batch-runner`. Its contents (Checkpoint 2 speaking notes, this contribution table and README updates) never reached `main`. Remedy: PR #35 merges merge commit `1495833`. Before merging stacked PRs in future, confirm that the base branch still exists and points to `main`.

AI tool usage record (counted on 2026-10-06, across all branches): since 2026-09-05, 30 of Member A's 39 commits were completed with Claude's assistance (the commits contain a `Co-Authored-By: Claude` line); the external acceptance review on 2026-10-06 used Codex CLI. Commits after 2026-10-06 no longer include an attribution line, so subsequent Claude-assisted commits cannot be identified from commit records; this statement is the record of that usage. Member A is responsible for all committed content and checked each review suggestion from the tools.

Contributions are not measured by commit count alone; model decisions, reviews, experiment verification and presentation preparation are also recorded.

## 9. If one member falls behind

Trigger: a task is more than 2 days late, a member misses 2 consecutive meetings, a key PR has no response for more than 48 hours, or the must-have timeline is affected.

Response:

1. Describe the blocker in an issue without personal blame;
2. Split the task into the smallest deliverable parts;
3. Reassign must-have work and pause optional extensions;
4. Keep the original owner involved as a reviewer or knowledge-transfer participant;
5. If fair collaboration continues to be affected, contact the facilitator/unit coordinator early and retain GitHub and meeting evidence.

## 10. Checkpoint collaboration evidence

Before a Checkpoint, show:

- shared repository;
- collaborator access;
- At least one clearly assigned issue;
- At least one PR or document review by the other member;
- The current contribution table;
- Both members' shared confirmation of research questions and model definitions.
