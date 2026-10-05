# Decision Log

记录 D001-D008 的最终决定。每条决定必须写明来源（facilitator / 组内）、日期和理由。在冻结前，所有 working proposal 在代码 config 中必须标注 `provisional`。

## Status

| ID | Decision | Working proposal | Final value | Source | Date | Notes |
|---|---|---|---|---|---|---|
| D001 | Response-delay origin | From introduction at `t=0` | From introduction at `t=0` | 组内（facilitator 未提出异议） | 2026-09-11 | Checkpoint 1（2026-09-07）未对 delay 起点提出修改要求，采用 working proposal（spec §11） |
| D002 | Tank capacity | 12 | 12 | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |
| D003 | Quarantined tank count `k` | 2 | 2 | 组内（facilitator 未提出异议） | 2026-09-11 | 采用 working proposal |
| D004 | Quarantine duration `D` | Select after pilot | 14 | Member A（Member B 待确认） | 2026-10-06 | Stage 2 pilot Q1-Q3（Q1 分母修正后），`pilot-report-2026-10-06.md` §4 |
| D005 | Network `p_in` / `p_out` | Select after structural pilot | 0.6 / 0.05 | Member A（Member B 待确认） | 2026-10-06 | Structural audit 候选值；movement pilot 中 S1-S6 在该网络参数下可满足，无需更换 |
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

### 2026-10-06：Stage 1 第 1 轮无 candidate 通过，按 rule 5 扩展 transfer grid 重跑

- 第 1 轮结果（`pilot-stage1-disease`，2000 runs，failed 0）：8 个 `(beta, gamma)` candidates 全部满足 S1-S4、S6，全部**只因 S5 失败**。逐项表：`results/pilot/pilot-stage1-disease-criteria.csv`。
- 失败原因：S5 要求相邻 level 的 mean accepted transfers per day 至少相差 2 倍。原 grid 中 0.01→0.02 与 0.05→0.10 的名义比例正好是 2 倍，capacity 拦截使实测只有约 1.77 倍和 1.88 倍，因此任何三档组合都无法满足 S5。
- 处理（rule 5）：阈值不变；transfer grid 增加 `0.025`，即 `[0, 0.01, 0.02, 0.025, 0.05, 0.1]`，使 `0.01 → 0.025 → 0.1` 的名义间隔为 2.5 倍和 4 倍；其余设置、seeds 与第 1 轮相同；完整重跑 Stage 1，design 名 `pilot-stage1-disease-r2`。第 1 轮 raw records 保留，不删除。
- 披露：新 grid 由 Member A 在看过第 1 轮的 transfer volume、affected tanks 和 attack rate 汇总后决定；选择 0.025 的依据是 transfer volume 的倍数关系，而非 attack rate。本条在第 2 轮运行前推送。
- Member B 事后确认：待定（日期：—）

### 2026-10-06：Stage 1 结论（第 2 轮，`pilot-stage1-disease-r2`）

- 2400 runs，failed 0。7/8 个 candidates 满足 S1-S6；`beta = 0.05, gamma = 0.2` 因 S5 失败。逐项表：`results/pilot/pilot-stage1-disease-r2-criteria.csv`。
- Rule 3：所有通过的 candidates 的 transfer levels 都是 `0.01 / 0.025 / 0.1`（跨度最大）。
- Rule 2（中间 level 0.025 的 median final attack rate 最接近 0.5）：选中 `beta = 0.2, gamma = 0.1`（median 0.458，距 0.5 为 0.042）；次近为 `beta = 0.15, gamma = 0.1`（0.435，0.065）。
- Response-delay levels（D1-D3，40 个 non-minor runs）：**1 / 12 / 33 天**（D2、D3 的 median 恰为整数，未发生取整）。
- 由脚本生成 `experiments/config/pilot-stage2-intervention.json`：transfer levels 0.01 / 0.025 / 0.1，`D` candidates 7 / 14 / 21，policy seeds 900-902，5550 runs。
- 需在报告中说明：在所选 regime 下，`transfer_rate = 0.1` 的 no-intervention median attack rate 为 1.0（接近饱和），该 level 上的 intervention 差异可能受天花板限制。
- Member B 事后确认：待定（日期：—）

### 2026-10-06：Stage 2 结论，Q1 分母在看过数据后修正

- 运行：`pilot-stage2-intervention`，5550 runs，failed 0、censored 0。逐项表：`results/pilot/pilot-stage2-intervention-criteria.csv`。
- **按原定义（全部 intervention runs），没有 D candidate 满足 Q1**：三个 D 的 share 都是 85.3% < 90%。
- 原因：284 / 1800 个 intervention runs 在 response day（12 或 33）之前已 extinction，隔离从未启动，`blocked_transfers` 必然为 0；这衡量的是“疫情是否活到 response day”，不是“隔离是否生效”。隔离实际启动的 runs 中 share 为 97.3%-97.4%。
- 修正（Member A 决定，看过数据之后）：Q1 的分母改为隔离实际启动的 runs（`pilot-protocol.md` Q1 行已更新）。`pilot_select.py` 同时输出 `Q1_original_all_runs` 与 `passed_original_q1`，两种结果都保留。
- 这一修正不影响选出哪个 D：在任何 Q1 定义下，只有 D = 14 同时满足 Q2（D ≤ 0.25 × 65 = 16.25）和 Q3（D ≥ 1/gamma = 10）。
- 结论：**D = 14**，budget = 2 × 14 = 28 tank-days。
- Member B 事后确认：待定（日期：—）

## Parameter freeze record（experiment-plan §9；2026-10-06）

| 项 | 冻结值 | 依据 |
|---|---|---|
| `beta` / `gamma` | 0.2 / 0.1 | Stage 1 第 2 轮 rule 2 |
| Transfer-rate levels | 0 / 0.01 / 0.025 / 0.1 | Stage 1 第 2 轮 rule 3 |
| Response-delay levels | 1 / 12 / 33 天 | D1-D3 |
| `D`（D004） | 14 | Stage 2 |
| `p_in` / `p_out`（D005） | 0.6 / 0.05 | Structural audit + pilot |
| Capacity / `k` / `max_days` | 12 / 2 / 365 | D002 / D003 / D006（2026-09-11） |
| Network seeds | 200-219（20 个） | experiment-plan §8：≥ 10 networks；runtime 允许时增加 network 数以稳定按 network 聚类的 bootstrap |
| Epidemic seeds | 10000-10004（每个 network 5 个） | experiment-plan §8：≥ 5 per network |
| Policy seeds | 1000-1002（每个 block 3 个） | experiment-plan §8：2-3 |
| 排除的 pilot seeds | network 100-104、epidemic 9000-9009、policy 900-902 | pilot-protocol §1 rule 3 |
| Planned runs | 5200（4 transfer levels × 100 blocks × 13 runs） | `experiments/config/formal.json` |
| 每个 condition 的 replicates | 100 blocks（≥ 30） | experiment-plan §8 |

- 新增分析口径（正式实验运行前写入）：配对效应同时报告全部 blocks，以及隔离实际启动的 blocks（`turtlefarm/analysis.py` 的 `subset` 列），原因见 `pilot-report-2026-10-06.md` §5。
- 正式实验开始后，不因结果与 hypothesis 不符而修改上述参数（experiment-plan §9）。
- 两名成员确认：Member A 2026-10-06；Member B 待确认。

### 2026-10-06：第一次正式实验（`formal`）的 seed 交叉问题，改为嵌套 seeds 重跑

- 问题：`formal` 中 20 个 network 共用同一组 5 个 epidemic seeds（runner 用 `itertools.product` 交叉）。在 event-keyed draws 下，同一 epidemic seed 在所有 network 上有相同的初始感染 agent 和相同的早期抽样，因此 network 之间并不独立：
  - pilot 中 seed 9003、9006 在全部 5 个 network 上都在第 12 天前 extinction，其余 8 个 seeds 都没有；
  - `formal` 的 5 个 seeds 中没有早期 extinction 的 seed。
- 后果：`formal` 只有 5 个独立的疫情起点。按 network 聚类的 bootstrap 假设 clusters 独立，会低估不确定性。这与 experiment-plan §5“epidemic replicates nested within the same network”的设计不符。
- 发现时间：**Member A 在看过 `formal` 的条件汇总和配对效应之后**发现，起因是 pilot 与 formal 的启动率不一致（delay 12：80% vs 100%）。重跑依据的是 experiment-plan §5 原有的嵌套要求，不是结果方向。
- 处理：
  - runner 增加 `nested_epidemic_seeds`，按顺序把 epidemic seeds 平均分给各 network；
  - 新 design `formal-nested`：network 200-219，epidemic 20000-20099（每个 network 5 个，互不共享），policy 1000-1002；参数与 freeze record 完全相同；5200 runs。
  - `formal` 的 raw records 保留，不删除；正式结果以 `formal-nested` 为准，报告中披露两次运行及原因。
- 对 pilot 的影响：pilot 同样是交叉 seeds，Stage 1/2 的判定实际只基于 10 个独立的疫情起点（network 间变异仍有效）。Pilot 不重跑，在 `pilot-report-2026-10-06.md` 中注明。
- Member B 事后确认：待定（日期：—）

## Analysis decisions made after the formal results（2026-10-06）

以下决定均在看过 `formal` 和/或 `formal-nested` 的汇总结果之后做出，在报告中逐项标注为 post-hoc。

| # | 决定 | 原因 | 位置 |
|---|---|---|---|
| A1 | 增加“各策略 − 同 block 无干预基线”的配对比较（`baseline_differences`），作为描述性分析 | 研究问题 1 的 delay 效应只能相对基线体现；原计划只比较 targeted 与 random | `turtlefarm/analysis.py`，报告 §3.3 / 表 2 |
| A2 | 代表性运行（图 7）规则：转移率 0.025 的无干预运行按 local / cross-region 分类，每类取 final attack rate 最接近该类中位数的一次，并列取较小 seeds | experiment-plan §13 要求客观规则；规则在只看过汇总结果、未看任何单次轨迹时写定 | `pick_representative_runs`，报告图 7 |
| A3 | 报告 `formal`（交叉 seeds）与 `formal-nested` 的对比（不跨 0 的格子数：7 vs 2） | 披露交叉设计高估精度 | 报告 §3.5 |
| A4 | `formal-nested` 复用 `formal` 的 network seeds 200-219 与 policy seeds 1000-1002，只更换 epidemic seeds | 交叉问题只来自共享 epidemic seeds；network 由 seed 确定性生成，复用同一批网络使两次运行的对比只差 seed 设计 | `experiments/config/formal-nested.json` |
| A5 | 条件汇总的 95% CI 由正态近似改为按 network 聚类的 bootstrap | 外部审查发现同一 network 的 runs 不独立，且正态近似在 attack rate 0.1 档的上限超过 1 | `condition_summary`，报告表 1 |
| A6 | 配对差的胜负/平局判定使用容差 1e-9 | 外部审查发现浮点误差（约 1e-17）在转移率 0 时把完全相同的结果计为 targeted 更优；报告引用的 52% / 15% / 33% 不受影响 | `DIFF_TOLERANCE` |
| A7 | `outbreak_class` 基于每日快照，可能看不到当天到达又当天恢复的感染个体；`analyse_results.py` 自动列出受影响的 runs | 外部审查发现；`formal-nested` 中 5/400 次基线运行受影响，其中 2 次被归为 local，重跑后确认受影响缸都在初始 region 内，分类正确 | `outbreak-class-check.json` |

外部审查：2026-10-06 由 Codex CLI 以只读模式做验收审查，结论 ACCEPT WITH FIXES，无 Blocker；独立重算的 20 余个报告数字全部一致。逐条处理见 PR #34。

复核（第二轮）：上一轮报告层面问题全部 RESOLVED；A4（复用 network / policy seeds）判为 DISPUTED-ACCEPTABLE，理由被接受；独立重算表 1 聚类 CI 等数字全部一致。剩余 3 项：

- 配对完整性检查改为对照设计文件，严格要求每个 block 恰好 1 个 targeted run、指定数量的不同 policy seeds 和 1 个基线，不完整的 block 排除并计数；
- `--n-boot` / `--boot-seed` 现在也传给表 1；
- `outbreak_class` 基于快照的局限保留（要彻底解决需改模型输出并重跑全部实验），已在代码文档、自动检查和报告局限性中披露，当前报告受影响的 2 次运行已人工核实。

以上修复不改变报告中的任何结果数字（`formal-nested` 与 `formal` 均为 0 个不完整 block）。

## Change history

| Date | Decision changed | Documents updated | PR |
|---|---|---|---|
| 2026-09-11 | 无（D001-D003、D006-D008 采纳 working proposal 为最终值） | `decision-log.md`、`README.md`、`checkpoint-1.md`、`turtlefarm/config.py`（移除 provisional 标注） | docs/checkpoint-1-feedback（PR #21） |
| 2026-09-11 | 语义补充：spec §16 randomness 由"独立 substreams"改为 event-keyed draws（保证跨策略配对）；§18 增加两层冻结规则 | `model-specification.md` §16/§18、`validation-plan.md` §9、`hand-trace-3tank.md` | model/validation-and-paired-rng（PR #22） |
| 2026-09-11 | spec §3.2 step 4 的结构检查具体化为 4 条；D005 候选值 0.6 / 0.05 | `model-specification.md` §3.2、`network-audit-2026-09-11.md`、`turtlefarm/network.py` | model/modular-network |
