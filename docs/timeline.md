# Project Timeline

Deadline: **2026-10-09 Friday, 11:59 pm**.

Priorities:

- **Must have:** Required to address the research questions and make a reliable submission.
- **Should have:** Strengthens the independent investigation, interpretation and quality, but may be reduced under time pressure.
- **Optional extension:** Start only once must-have and should-have work is stable.

## 1-4 September - Research design, repository and Checkpoint 1

### Must have

- Freeze canonical primary/secondary questions and hypothesis;
- Complete the proposal, model specification, assumptions and experiment/validation plans;
- Prepare the Checkpoint brief and speaking notes;
- Confirm the shared repository and collaborator access;
- Prepare facilitator questions;
- Both members review document consistency.

### Should have

- Create GitHub issues, labels, a milestone and initial cross-review evidence;
- Draw a conceptual system diagram that does not depict results.

### Optional

- Conduct an initial search for a small number of authoritative references; do not delay the Checkpoint.

## 5-11 September - Baseline model

### Must have

- Close pending model decisions after facilitator feedback;
- Implement minimal SIR states, daily updates and stopping conditions;
- Implement the synthetic population and fixed tank locations;
- Complete beta=0, population-conservation and same-seed tests;
- Jointly verify a small scenario by hand.

### Should have

- Modular network generator and metric audit;
- clear run metadata schema.

### Optional

- None.

## 12-18 September - Movement, intervention and experiment runner

### Must have

- network-constrained movement and capacity;
- tank `open/quarantined` management state;
- three strategies;
- pre-outbreak betweenness selection;
- strict budget-fair pairing;
- network/epidemic/policy seed separation;
- validation plan required cases.

### Should have

- batch runner, config validation, raw-result provenance;
- end-to-end trace and PR review.

### Optional

- runtime optimisation only if needed.

### Status at 2026-09-20

- Must have: all complete. Movement / capacity (PR #27), management state and three strategies (PR #29), pre-outbreak betweenness selection, budget-fair pairing, separation of the three seed types, validation cases (111 tests on `main`).
- Should have: batch runner, design validation and raw-result provenance were implemented two days behind schedule on 2026-09-20 (issue #30, `turtlefarm/runner.py`, 25 additional tests); the schema was merged on 2026-09-20 (PR #25). End-to-end coverage is provided by `experiments/config/smoke.json`.
- Workflow gap: PR #27 and #29 have no review record from the other member; see `collaboration-plan.md` §8.

## 19-25 September - Pilot and formal experiments

Status at 2026-09-20: `docs/pilot-protocol.md` has been drafted (selection criteria written before running), awaiting Member B's confirmation; once confirmed, Stage 1 should take about 1 minute to run. Neither the pilot nor the formal experiment has been run.

### Must have

- Run and document pilot without treating it as hypothesis evidence;
- Freeze parameters and seed lists;
- Estimate runtime and failure rate;
- Run complete primary experiment;
- Preserve failed/censored/anomalous runs;
- Generate reproducible summary tables.

### Should have

- Complete nested random-policy replicates;
- Begin limited sensitivity checks after primary runs finish.

### Optional

- Extra network structure sensitivity if runtime permits.

## 26 September-2 October - Analysis and report

### Must have

- Quantitative analysis with paired effects and uncertainty;
- Qualitative representative runs with declared selection rule;
- Explain results, limitations and alternative explanations;
- Draft methods, results and discussion;
- Verify all claims against data and configs.

### Should have

- Complete limited beta/gamma or capacity sensitivity;
- Improve figures and captions;
- Rehearse interpretation with both members.

### Optional

- Additional exploratory plot only if it answers an existing question.

## 3-8 October - Reproduction, demonstration and freeze

> **As a rule, do not add new model features after 3 October.**

### Must have

- Fresh-environment reproduction of selected runs/figures;
- Freeze model, configs and analysis;
- Resolve report/code/figure inconsistencies;
- Prepare demonstration and speaking roles;
- Check contribution evidence and academic integrity;
- Incorporate any published rubric/submission requirements.

### Should have

- Independent rerun by the member who did not author the runner;
- Final accessibility and figure-label review.

### Optional

- None unless all submission materials are frozen and verified.

## 9 October - Final check and submission

### Must have

- Verify final files, filenames and required formats against official instructions;
- Confirm report, code, figures and presentation use the same final results;
- Confirm repository commit/tag and both-member access;
- Submit before 23:59 and preserve submission receipt.

### Stop rule

On that day, fix only submission-blocking errors. Do not add model features, reselect parameters or reinterpret results to seek more attractive conclusions.
