# Research Plan Index and Decision Register

本文件是非代码阶段的入口。规范性内容分布在：

- `research-proposal.md` - why and what we study；
- `model-specification.md` - exact model behaviour；
- `assumptions.md` - numbered assumptions；
- `experiment-plan.md` - primary experiment and analysis；
- `validation-plan.md` - future tests and verification；
- `timeline.md` and `risk-register.md` - delivery control。

## Fixed decisions

- Project title: **Bridge Transfers and Quarantine in a Captive Turtle Farm**。
- Model framing: **a stylised explanatory model**。
- 200 synthetic agents；20 tanks；4 regions × 5 tanks。
- Agent disease states: `S / I / R`。
- Tank management states: `open / quarantined`。
- No individual `Q` state in MVP。
- Quarantine blocks movement into/out of a tank but not internal transmission。
- Modular, non-uniform transfer network；bridge tanks may have high betweenness。
- Targeted policy uses only pre-outbreak network information。
- Strategies: no intervention、random quarantine、highest-betweenness quarantine。
- Primary experiment factors: transfer rate、response delay、strategy only。
- Primary metrics: final attack rate、affected tanks、peak infected、time to extinction。
- All population, network and experiment data are synthetic。

## Decision status

Checkpoint 1（2026-09-07）facilitator 无异议；组内于 2026-09-11 采纳 working proposals 为最终值。完整记录见 `decision-log.md`，两层冻结规则见 `model-specification.md` §18。

| ID | Decision | Final value | Status | Alternatives considered |
|---|---|---|---|---|
| D001 | Response-delay origin | From outbreak introduction at `t=0` | Frozen 2026-09-11 | First detection requires observation model and larger scope |
| D002 | Tank capacity | 12 for all tanks | Frozen 2026-09-11 | Higher value reduces blocking；heterogeneous value adds confounding |
| D003 | Quarantined tank count `k` | 2 | Frozen 2026-09-11 | Larger budget may remove much of a 20-node network |
| D004 | Quarantine duration `D` | Candidate after pilot | Value pending pilot（issue #4） | Too short has little effect；too long approximates permanent removal |
| D005 | Network `p_in/p_out` | Candidate after structural pilot | Value pending pilot（issue #5） | Must be modular, connected and non-symmetric |
| D006 | `max_days` | 365 | Frozen 2026-09-11 | Too short causes censoring；too long wastes runtime |
| D007 | No-intervention reporting | Shared baseline per transfer/network/epidemic block | Frozen 2026-09-11 | Repeated delay labels give balanced table but duplicate identical runs |
| D008 | Headline outcome | Attack rate and affected tanks co-primary | Frozen 2026-09-11 | Facilitator may prefer one for presentation emphasis |

## Decision process

1. Ask facilitator using `facilitator-questions.md`。
2. Record answer and date in `decision-log.md` and the relevant issue。
3. Update specification、assumptions、experiment plan and checkpoint material together。
4. Obtain approval from both members。
5. Freeze decisions before implementation。

## Non-code stage exit criteria

- [x] Canonical questions and hypothesis documented。
- [x] Model states, interactions and update order documented。
- [x] Experiment, validation, collaboration, timeline and risks documented。
- [x] Checkpoint brief and speaking notes prepared。
- [x] Facilitator resolves or accepts pending decisions（Checkpoint 1，无异议；2026-09-11 记录）。
- [x] Both members confirm the final specification（issue #10，2026-09-06/07）。
- [x] Collaborator access and first cross-review evidence verified（PR #19 由 Member B approve，2026-09-06）。
- [ ] Official rubric/submission details checked when released。
