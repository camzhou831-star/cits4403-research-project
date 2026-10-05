# Decision Log

记录 D001-D008 的最终决定。每条决定必须写明来源（facilitator / 组内）、日期和理由。在冻结前，所有 working proposal 在代码 config 中必须标注 `provisional`。

## Status

| ID | Decision | Working proposal | Final value | Source | Date | Notes |
|---|---|---|---|---|---|---|
| D001 | Response-delay origin | From introduction at `t=0` | From introduction at `t=0` | 组内（facilitator 未提出异议） | 2026-09-11 | Checkpoint 1（2026-09-07）未对 delay 起点提出修改要求，采用 working proposal（spec §11） |
| D002 | Tank capacity | 12 | 12 | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |
| D003 | Quarantined tank count `k` | 2 | 2 | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |
| D004 | Quarantine duration `D` | Select after pilot | （待 pilot） | — | — | 按 experiment-plan 在 19-25 Sep pilot 后确定，issue #4 保持 open |
| D005 | Network `p_in` / `p_out` | Select after structural pilot | （candidate 0.6 / 0.05，待 M2 pilot 冻结） | — | — | Structural audit 2026-09-11（`network-audit-2026-09-11.md`）给出候选值；数值在 movement pilot 后冻结，issue #5 保持 open |
| D006 | `max_days` | 365 | 365 | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal；仍记录 `censored_max_days` 状态 |
| D007 | No-intervention reporting | Shared baseline per block | Shared baseline per block | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |
| D008 | Headline outcome | Attack rate + affected tanks co-primary | Attack rate + affected tanks co-primary | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |

## Facilitator meeting record

- Date：2026-09-07（Checkpoint 1 facilitator meeting）
- Attendees：Cam Zhou、Wenhao Zhang、facilitator
- Questions asked（按 `facilitator-questions.md` 编号）：按 `checkpoint-1-brief.md` 介绍系统、研究问题、建模方法和 GitHub 进展
- Answers：facilitator 对项目整体表示满意，未对系统范围、研究问题、模型定义或实验设计提出修改要求，也未对 D001-D008 的 working proposal 提出异议
- Newly released rubric / submission requirements：会上未获得新的 rubric 或提交格式信息；按 `timeline.md` 在 3-8 October 阶段再次核对官方发布

### 记录结论

- D001、D002、D003、D006、D007、D008：facilitator 无异议，组内于 2026-09-11 采纳 working proposal 为最终值，代码 config 中移除 `provisional` 标注。
- D004、D005：本来就计划在 pilot 后确定，不受 Checkpoint 影响，继续 open。
- 无任何决策改变，因此不触发 `consistency-review.md` §6 的跨文档更新。

## Provisional-start decision

- [x] 两名成员确认：baseline SIR（无 movement、无 intervention）可在 D001-D008 冻结前开始，config 中 provisional 值已标注。
  - Member A 确认日期：2026-09-07（issue #10 评论）
  - Member B 确认日期：2026-09-06（issue #10 评论，"D001-D008 remain provisional pending confirmation"）

## Specification sign-off

- [x] Member A 已通读 `model-specification.md` 并确认可独立实现。日期：2026-09-07（issue #10）
- [x] Member B 已通读 `model-specification.md` 并确认可独立实现。日期：2026-09-06（issue #10）

## Protocol deviations

### 2026-10-06：Stage 1 pilot 在 Member B 签署 pilot-protocol 前运行

- 偏离内容：`pilot-protocol.md` 要求两名成员确认标准后才运行 pilot；Stage 1 由 Member A 在 Member B 签署前运行。
- 原因：截止 2026-10-09，Member B 当晚无法联系；为留出正式实验和报告时间，Member A 决定先运行。
- 防止 outcome-driven tuning 的措施：选择标准（含 2026-10-06 的 5 处补充）在运行前以 commit `d2be9bf` 推送到 PR #34，本条记录也在运行前推送；selection 由 `scripts/pilot_select.py` 按已推送的标准机械执行。
- 若 Member B 在 review 中要求修改标准：修改及原因写入本节，并同时报告“按原标准”和“按修改后标准”的选择结果，不得只报告后者。
- Member B 事后确认：待定（日期：—）

## Change history

| Date | Decision changed | Documents updated | PR |
|---|---|---|---|
| 2026-09-11 | 无（D001-D003、D006-D008 采纳 working proposal 为最终值） | `decision-log.md`、`README.md`、`checkpoint-1.md`、`turtlefarm/config.py`（移除 provisional 标注） | docs/checkpoint-1-feedback（PR #21） |
| 2026-09-11 | 语义补充：spec §16 randomness 由"独立 substreams"改为 event-keyed draws（保证跨策略配对）；§18 增加两层冻结规则 | `model-specification.md` §16/§18、`validation-plan.md` §9、`hand-trace-3tank.md` | model/validation-and-paired-rng（PR #22） |
| 2026-09-11 | spec §3.2 step 4 的结构检查具体化为 4 条；D005 候选值 0.6 / 0.05 | `model-specification.md` §3.2、`network-audit-2026-09-11.md`、`turtlefarm/network.py` | model/modular-network |
