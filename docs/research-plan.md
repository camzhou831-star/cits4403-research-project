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

## Decision pending facilitator confirmation

| ID | Decision | Working proposal | Alternatives / impact |
|---|---|---|---|
| D001 | Response-delay origin | From outbreak introduction at `t=0` | First detection requires observation model and larger scope |
| D002 | Tank capacity | 12 for all tanks | Higher value reduces blocking；heterogeneous value adds confounding |
| D003 | Quarantined tank count `k` | 2 | Larger budget may remove much of a 20-node network |
| D004 | Quarantine duration `D` | Select after pilot | Too short has little effect；too long approximates permanent removal |
| D005 | Network `p_in/p_out` | Select after structural pilot | Must be modular, connected and non-symmetric |
| D006 | `max_days` | 365 | Too short causes censoring；too long wastes runtime |
| D007 | No-intervention reporting | Shared baseline per transfer/network/epidemic block | Repeated delay labels give balanced table but duplicate identical runs |
| D008 | Headline outcome | Treat attack rate and affected tanks as co-primary | Facilitator may prefer one for presentation emphasis |

## Decision process

1. Ask facilitator using `facilitator-questions.md`。
2. Record answer and date in the relevant issue。
3. Update specification、assumptions、experiment plan and checkpoint material together。
4. Obtain approval from both members。
5. Freeze decisions before implementation。

## Non-code stage exit criteria

- [x] Canonical questions and hypothesis documented。
- [x] Model states, interactions and update order documented。
- [x] Experiment, validation, collaboration, timeline and risks documented。
- [x] Checkpoint brief and speaking notes prepared。
- [ ] Facilitator resolves or accepts pending decisions。
- [ ] Both members confirm the final specification。
- [ ] Collaborator access and first cross-review evidence verified。
- [ ] Official rubric/submission details checked when released。
