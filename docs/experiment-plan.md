# Experiment Plan

## 1. Purpose

主实验回答两个 research questions，而不是展示 simulator 功能。实验必须比较多个 transfer rates、response delays 和 intervention strategies，并在 paired random conditions 下评估 highest-betweenness quarantine 是否优于 random quarantine。

## 2. Primary experiment

### Independent variables

1. **Cross-tank transfer rate (`mu`)**：初步 4 个 levels，包括 `0` 和 3 个由 pilot 确定的 non-zero levels。
2. **Response delay (`d`)**：初步 3 个 levels，例如 immediate / short / long；具体 days 由 facilitator feedback 和 pilot 决定。
3. **Intervention strategy**：
   - `No intervention`
   - `Random tank quarantine`
   - `Highest-betweenness tank quarantine`

不得在没有 pilot 的情况下把数值水平写成最终值。

### Control variables

主实验固定：

- population = 200；tanks = 20；regions = 4；
- initial occupancy distribution；fixed capacity；
- initial infected count = 1；
- `beta`、`gamma`；
- network generation rule and acceptance criteria；
- quarantine count `k` and duration `D`；
- daily update order；
- maximum horizon；
- metric definitions。

## 3. Baseline and treatment conditions

- **Structural baseline:** `mu = 0`, no intervention，检验感染不能进入其他 tanks。
- **Policy baseline:** random tank quarantine under the same budget。
- **Untreated baseline:** no intervention at each transfer-rate level。
- **Treatment:** highest-betweenness tank quarantine。

No-intervention 中 response delay 不生效。概念上可以在 4 × 3 × 3 matrix 中显示它，但同一 transfer/network/epidemic block 不应浪费资源重复完全相同的 no-intervention run。建议 unique condition structure：

```text
per transfer level:
  1 no-intervention baseline
  + 3 response delays × 2 quarantine strategies
```

是否为了表格平衡而重复显示 baseline：**不重复。每个 transfer/network/epidemic block 只运行一次 no-intervention baseline，作为 shared baseline 报告（D007，frozen 2026-09-11）**。

## 4. Dependent variables

### Primary metrics

| Metric | Calculation | Relation to question |
|---|---|---|
| Final attack rate | `ever infected / 200` | primary final outbreak size；secondary policy effect |
| Number of affected tanks | tanks ever containing at least one `I` | primary system-wide spread；secondary policy effect |
| Peak infected population | `max I(t)` including `t=0` | severity/dynamics support |
| Time to extinction | first day with `I(t)=0`; censored otherwise | duration/dynamics support |

### Auxiliary metrics

- time to peak：第一次达到 peak 的 day；
- intervention cost：`k × D` tank-days；
- relative reduction compared with random quarantine：paired outcome 的 `(random - targeted) / random`。

不再无理由增加指标。Daily transfer acceptance、network metrics 和 initial-tank centrality 作为 diagnostic variables，不作为额外 headline outcomes。

## 5. Seed hierarchy and variance separation

### Network seeds

每个 `network_seed` 生成一个独立 modular network。Network-level summaries 和 acceptance attempt 必须保存。多个 epidemic replicates 嵌套在同一 network 内，用于区分 network-instance variance。

### Epidemic seeds

每个 `epidemic_seed` 控制 initial infected agent、movement、infection 和 recovery draws。相同 network/epidemic pair 必须跨三种 strategies 配对。

### Policy seeds

`policy_seed` 只控制 random quarantine tank selection。Targeted strategy 是 deterministic；no-intervention 无 policy seed。若同一 network/epidemic pair 使用多个 random policy seeds，可以估计 random-policy selection variance。

### Variance interpretation

- **Network-instance variance:** 不同 topology 产生的结果差异。
- **Epidemic stochastic variance:** 固定 network 和 policy 后，不同 initial/disease/movement draws 的差异。
- **Random-policy selection variance:** 固定 network 和 epidemic draws 后，不同随机隔离 tanks 的差异。

分析不得把三种 variance 混成一个无法解释的误差来源。

## 6. Paired comparison design

每个 comparison block 至少由以下 key 标识：

```text
(network_seed, epidemic_seed, transfer_rate, response_delay, budget)
```

在该 block 内：

- 使用相同 network instance；
- 使用相同 initial infected agent；
- 使用相同 epidemic seed/substreams；
- random 和 targeted 在相同 day 开始、持续相同 `D`、隔离相同 `k`；
- 唯一主要差异是 selected tanks；
- random strategy 的 policy seed 单独记录。

主要 policy effect 使用 paired differences，而不仅比较两个独立均值。

## 7. Pilot experiment

Pilot 不用于验证假设或选择“好看”的结论，只用于检查模型是否处于有信息量的 regime，并冻结主实验参数。

### Pilot questions

1. 在 no intervention 下，是否出现“全部迅速 extinction”和“几乎全部感染”之外的中间行为？
2. transfer-rate levels 是否产生可区分的 accepted movements？
3. response-delay levels 是否覆盖 immediate、intermediate 和 late response？
4. network generator 是否稳定产生 connected modular graphs 和非平凡 betweenness ranking？
5. `k`、`D` 和 capacity 是否既不无效，也不几乎删除整个 network？
6. 365-day working horizon 是否足够？

### Preliminary pilot size

- 3-5 network seeds；
- 每个 network 5-10 epidemic seeds；
- 少量 candidate parameter sets；
- 输出只用于参数冻结、bug discovery 和 runtime estimation。

Pilot 选择标准、所有尝试过的参数和失败情况必须记录，避免 outcome-driven tuning。

## 8. Repetition recommendation

课程笔记强调 stochastic experiments 要重复运行；本项目比课堂 15-20 次更需要分层方差估计。初步正式设计建议：

- 至少 10 network seeds；
- 每个 network 至少 5 epidemic seeds，即每个主要 condition 至少 50 network-epidemic blocks；
- random policy 可对每个 block 使用 2-3 个 policy seeds，若 runtime 允许。

这是 preliminary recommendation，不是最终 sample size。Pilot 后依据 runtime、variance 和置信区间稳定性决定，但每个 condition 不应少于 30 replicates。

## 9. Parameter freezing

Pilot 后创建 parameter-freeze record，包含：

- selected transfer-rate and delay levels；
- fixed `beta`、`gamma`、capacity、`k`、`D`、`max_days`；
- network parameters and rejection rules；
- seed lists；
- planned run count；
- 选择理由和日期；
- 两名成员确认。

正式实验开始后不得因为结果不符合假设而改变参数。若发现 bug，按 failure protocol 处理并重新运行受影响的完整 seed set。

## 10. Raw results and provenance

未来 raw result 一行对应一个 run，至少含：

- run ID、timestamp、commit hash、configuration hash；
- all parameter values and seeds；
- network ID、adjacency/centrality reference；
- selected quarantine tanks；
- status and stop reason；
- all predefined metrics；
- error/censoring fields。

保存层次建议：

```text
results/raw/        append-only raw run records (not manually edited)
results/summary/    reproducible aggregated tables
results/figures/    generated figures
experiments/config/ frozen machine-readable configurations
```

本阶段不创建这些结果或虚假示例。

## 11. Anomalies and failed runs

- 不隐藏、删除或手工改写异常结果。
- 每个 run 必须有 `completed`、`censored_max_days` 或 `failed` status。
- 参数合法但结果极端不是 failure，应保留并解释。
- 不变量失败或异常必须保存 configuration/seeds/error。
- 只有确认 implementation bug 并记录修复 commit 后才能 rerun；使用原 seeds 重跑整个受影响 block。
- 不允许只重跑不利或异常的单个 outcome。

## 12. Quantitative analysis

- 对每个 condition 报告 count、mean、median、standard deviation、IQR 和 95% confidence interval。
- 对 random vs targeted 报告 paired mean/median difference 和 paired bootstrap CI。
- final attack rate 和 affected tanks 优先报告 absolute difference，同时给 relative reduction。
- bootstrap 应按 network instance 做 cluster resampling，避免把同一 network 内 replicates 当成完全独立。
- time to extinction 对 censored runs 单独报告；若 censoring 非罕见，使用适当 time-to-event summary，而不是把 horizon 当作 extinction。
- 不仅报告 p-values；effect size 和 uncertainty 是主要解释依据。

## 13. Qualitative analysis

- 展示少量预先定义或按客观规则选择的 representative runs，例如中位数附近的 run，而不是挑最好看的图。
- 使用 network diagram 标示 regions、betweenness、quarantined tanks 和 affected tanks。
- 使用 S/I/R time series 解释传播阶段。
- 展示 local-only outbreak 与 cross-group outbreak 的机制差异。
- 每个 qualitative example 必须给出完整 seed 和 configuration。

## 14. Planned figures

1. 模块化 tank-transfer network 图，node colour 表示 region，size 表示 betweenness。
2. Final attack rate vs transfer rate，按 strategy 分组、response delay 分面，并显示 uncertainty。
3. Number of affected tanks vs transfer rate，布局同上。
4. Paired targeted-minus-random differences，按 delay 和 transfer rate。
5. Peak infected population distributions。
6. Time-to-extinction distributions or censored summary。
7. 一个 local outbreak 和一个 cross-group outbreak 的 time series/network snapshots。

本阶段不制造 prototype data 或图表。

## 15. Sensitivity analysis

主实验完成后，仅做小规模 one-factor-at-a-time 或小型设计：

- 较低/较高 `beta`；
- 较低/较高 `gamma`；
- homogeneous vs limited heterogeneous capacity；
- optional movement/update-order assumption。

敏感性分析不应扩展成全部参数笛卡尔积，也不能替代主实验。

## 16. Stop-running rules

- 单 run 在 infection extinction 时停止；达到 `max_days` 则 censor。
- 正式批次在预先定义的 seed list 完成前不得因趋势明显而提前停止。
- 若 failure rate 超过预设阈值（working trigger 1%）或出现不变量失败，暂停整个 batch、调查原因并记录决定。
- 若 runtime 超出 timeline，优先减少 optional policy-seed replicates，不删除核心 transfer/delay/strategy cells。

## 17. Decision status

已冻结（2026-09-11，见 `decision-log.md`）：capacity = 12、`k` = 2、`max_days` = 365、delay 从 introduction 起算、shared baseline reporting、attack rate 与 affected tanks co-primary。

数值待 19-25 Sep pilot 后冻结（`model-specification.md` §18 第二层）：

- 数值 transfer-rate levels；
- 数值 response-delay levels；
- `beta`、`gamma`、`D`；
- network generation parameters `p_in` / `p_out`；
- final network/epidemic/policy replication counts。
