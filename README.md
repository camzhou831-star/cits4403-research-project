# CITS4403 Research Project

## Bridge Transfers and Quarantine in a Captive Turtle Farm

This repository holds the research design, model implementation, computational experiments, analysis and final presentation for the CITS4403 Research Project. The project uses fully synthetic data to study disease spread and movement restrictions in a modular tank housing system. It is a **stylised explanatory model**: it does not predict any real turtle disease and uses no real turtle-farm customer data.

## Team

| Role | Name | GitHub | Contact |
|---|---|---|---|
| Member A | Cam Zhou | `camzhou831-star` | To be confirmed by the team |
| Member B | Wenhao Zhang | `Winston-2hang` | To be confirmed by the team |

- Deadline: Friday 9 October 2026, 23:59.
- Current stage: **code stage (M1 and M2 implemented; the pilot runs once both members confirm the pilot protocol)**.
- Implementation status: **`turtlefarm/` implements the minimal SIR baseline, the modular network, network-constrained movement, tank quarantine strategies and the batch experiment runner; neither the pilot nor the formal experiment has been run, and the repository contains no experiment results.**
- Checkpoint 1 is complete and the facilitator requested no changes; D001-D003 and D006-D008 adopted the working proposals as final values, D004/D005 will be decided after the pilot (see `docs/decision-log.md`).
- The shared GitHub repository is set up; all changes reach `main` through a feature branch and PR review.

## Proposed system

- 200 synthetic turtle agents are distributed across 20 tanks.
- The 20 tanks form a modular transfer network with 4 regions.
- An agent's disease state is one of `S / I / R` only.
- A tank's management state is one of `open / quarantined` only.
- Tank-level quarantine blocks transfers into and out of that tank for a fixed period, while transmission inside the tank continues.
- A few tanks that connect different regions may have high betweenness centrality and act as bridge tanks.

## Research questions

**Primary research question**

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Secondary research question**

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## Hypothesis

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

## Modelling approach

The project uses a discrete-time agent-based model (ABM) on a fixed tank-transfer network:

- the agent layer describes SIR disease state, current tank, within-tank transmission, recovery and individual transfers;
- the network layer describes which tank pairs allow transfers and the modular region structure;
- the management layer compares `No intervention`, `Random tank quarantine` and `Highest-betweenness tank quarantine`;
- the main experiment varies only cross-tank transfer rate, response delay and intervention strategy;
- every stochastic condition uses a traceable network seed, epidemic seed and random-policy seed.

The full specification is in [docs/model-specification.md](docs/model-specification.md).

## Current stage and gates

**Gates already met (entering the code stage, 2026-09-11)**

1. Checkpoint 1 is complete and the facilitator requested no changes;
2. D001-D003 and D006-D008 are frozen; D004/D005 have frozen semantics and numeric values pending the pilot (two-layer freeze rule, `docs/model-specification.md` section 18);
3. both members signed off the model specification (issue #10);
4. the GitHub collaborator accepted the invitation, and PR #19 has a cross-member review;
5. the official rubric / submission format has not been released; this is recorded in `docs/decision-log.md` and will be checked again on 3-8 October.

**M2 gate (movement / intervention / experiment runner) — met, 2026-09-20**

- formal tests V001-V005, V011, V012, V101, V103 and V104 pass (issue #13, closed);
- the hand trace matches the event log and is signed by both members (issue #14, closed);
- the paired-randomness scheme (event-keyed draws) is written into specification section 16 and implemented (`turtlefarm/rng.py`);
- the run metadata / failure record schema is frozen (issue #15, PR #25, merged 2026-09-20).

Recorded deviation: movement (PR #27) and quarantine (PR #29) were merged before the schema, which does not follow the gate order above. Neither writes raw records; the experiment runner, which depends on the schema, was implemented only after PR #25 was merged (issue #30), so no raw record was produced before the schema was frozen.

**Must be met before the formal experiment**

- the selection criteria in `docs/pilot-protocol.md` are confirmed by both members before the pilot runs;
- the pilot is complete, and `beta`, `gamma`, `D`, `p_in`/`p_out`, levels and seed lists are frozen and recorded;
- V001-V012, V101-V110 and the fairness audit all pass (`docs/validation-plan.md` section 10).

## Environment

Python 3.12, with dependencies pinned in `requirements.txt`. Both members use the same versions so that same-seed results are comparable.

```bash
uv venv --python 3.12 .venv          # or: python3.12 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt   # or: pip install -r requirements.txt
python -c "import numpy, networkx, pandas, matplotlib, pytest; print('ok')"
```

`.venv/` is listed in `.gitignore` and is not committed.

## Documentation map

| File | Purpose |
|---|---|
| `docs/research-proposal.md` | System, motivation, research questions, contribution and scope |
| `docs/model-specification.md` | Consistent model specification that can be implemented independently |
| `docs/assumptions.md` | Numbered assumptions, their impact and sensitivity needs |
| `docs/experiment-plan.md` | Main experiment, paired design, replication, analysis and figure plan |
| `docs/validation-plan.md` | Invariants, extreme cases and validation evidence plan |
| `docs/checkpoint-1-brief.md` | Brief for the 10-minute facilitator meeting |
| `docs/checkpoint-1-speaking-notes.md` | 3-4 minute English speaking notes for both members |
| `docs/collaboration-plan.md` | Communication, GitHub workflow, review and contribution record |
| `docs/timeline.md` | Must/should/optional schedule up to the deadline |
| `docs/risk-register.md` | Risks, triggers, owners and mitigation |
| `docs/facilitator-questions.md` | Questions to confirm at checkpoints |
| `docs/literature-plan.md` | Literature search directions and inclusion criteria |
| `docs/consistency-review.md` | Cross-document consistency review and pending decisions |
| `docs/decision-log.md` | Final decisions D001-D008, facilitator feedback record and specification sign-off |
| `docs/week-plan-2026-09-05.md` | Weekly execution checklist for the 5-11 September baseline model |
| `docs/checkpoint-1-prediction.md` | Checkpoint 1 rehearsal: predicted questions, prepared answers and follow-up actions |
| `docs/checkpoint-1-rehearsal-member-b.md` | Member B's Checkpoint 1 rehearsal script (Chinese-English, 2026-09-07) |
| `docs/hand-trace-3tank.md` | M1 hand-trace fixture: 3 tanks / 6 agents / 3 days, checked against `tests/test_hand_trace.py` |
| `docs/run-result-schema.md` | Field contract of a raw run record (`turtlefarm.run.v1`); the runner writes JSONL to it |
| `docs/pilot-protocol.md` | Two-stage pilot design and selection criteria **written before any data** (draft, pending Member B) |
| `docs/checkpoint-2-speaking-notes.md` | Checkpoint 2 speaking notes for both members, screen positions, demo step and Q&A split |
| `docs/network-audit-2026-09-11.md` | Structural audit of the modular network generator (16 p_in/p_out combinations x 10 seeds), D005 candidate values |
| `scripts/audit_network.py` | Re-run the network structural audit |
| `scripts/demo_checkpoint2.py` | Checkpoint 2 functionality demonstration (one seed block, not an experiment result) |
| `scripts/run_experiment.py` | Run a batch from `experiments/config/*.json`; writes raw JSONL and a per-run summary table |
| `scripts/create_github_issues.sh` | Create milestones, labels and the first issues (supports `--dry-run`) |

## Repository structure

```text
turtlefarm/    model implementation (SIR; event-keyed draws; modular network; movement; quarantine; batch runner)
tests/         V-numbered invariant, extreme-case, paired-draw, hand-trace, movement, quarantine and runner tests
scripts/       checkpoint demo, network audit, experiment runner and repository bootstrap helpers
experiments/   machine-readable experiment designs (experiments/config/*.json)
results/       raw run records (git-ignored), summaries and selected figures (created when the pilot runs)
```

## Experiment and result records

Every future run records at least the model version / commit hash, complete configuration, network seed, epidemic seed, policy seed, network instance, strategy, response delay, quarantine budget, run status, stop reason, error information and all predefined output metrics.

Anomalous or failed runs must not be deleted silently. Raw results and cleaned analysis tables are stored separately and must be reproducible from the configuration, seeds and code version.

## Academic integrity boundary

The earlier `turtle-farm` project provides domain inspiration only. This project does not copy that project, the CITS4403 Lab Notebook, assessed work from CITS4012, CITS1401 or CITS5501, or restricted third-party code. The model, synthetic data, rules, experiments, analysis and text are all designed anew for this project.
