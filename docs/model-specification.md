# Model Specification

本文档是规范性模型。D001-D003、D006-D008 已于 2026-09-11 冻结（见 `decision-log.md`）；仍标注 `Candidate value, frozen after pilot` 的项目（D004 quarantine duration、D005 network parameters、`beta`、`gamma`）按 §18 的两层冻结规则处理。两名成员应能依据本文件独立实现出相同行为。

## 1. Model type, purpose and time

- 类型：discrete-time stochastic agent-based model（离散时间随机 ABM）。
- 网络：static modular tank-transfer network。
- 用途：解释 transfer rate、response delay 和 quarantine selection 如何共同改变合成系统中的传播。
- 定位：**a stylised explanatory model**，不是现实预测模型。
- 一个 simulation step 表示 one day；初始状态为 `t = 0`，每日更新产生 `t + 1` 状态。

## 2. Entities

### 2.1 Turtle agent

| Field | Meaning |
|---|---|
| `agent_id` | 运行内唯一 ID |
| `tank_id` | 当前所在的唯一 tank |
| `disease_state` | `S`、`I` 或 `R` |
| `state_entered_day` | 进入当前疾病状态的日数 |
| `ever_infected` | 是否曾进入 `I`，用于 final attack rate |

MVP 不设置个体 `Q` 状态。S、I、R agents 均可能转移，除非所在或目标 tank 的 quarantine 阻止移动。

### 2.2 Tank

| Field | Meaning |
|---|---|
| `tank_id` | 0-19 的唯一 ID |
| `region_id` | 0-3，每区 5 个 tanks |
| `capacity` | 最大 agents 数量 |
| `management_state` | `open` 或 `quarantined` |
| `quarantine_start_day` | 未隔离时为空 |
| `quarantine_end_day` | 未隔离时为空；采用半开区间 `[start, end)` |

Quarantined tank 内部传播和恢复继续发生；只禁止跨缸转入和转出。

## 3. Transfer network

### 3.1 Graph definition

- 20 个 tank nodes，分为 4 个 modules，每个 module 5 个 nodes。
- 网络为 undirected、unweighted、simple graph。
- edge 表示两个 tanks 之间允许直接转移。
- 网络在一次 run 中固定；agent movement 随时间发生。
- 同区域 edge probability `p_in` 高于跨区域 `p_out`。
- 生成后网络必须 connected，且至少存在跨区域 edges。
- 禁止完全图、完全均匀随机混合和人为完全对称的模块复制。

### 3.2 Generation procedure

1. 按固定 tank IDs 建立 4 个 regions。
2. 对同区域 node pairs，以 `p_in` 独立生成 edges。
3. 对不同区域 node pairs，以较低的 `p_out` 独立生成 edges。
4. 若网络不 connected、没有跨区域 edge 或违反预先定义的结构检查，则从同一 network seed 确定性产生下一次尝试，并记录 attempt index。
5. 保存 adjacency list、region assignment、network seed、平均度、density、clustering coefficient 和 node betweenness。

`p_in`、`p_out` 和结构接受阈值：**Candidate value, frozen after structural pilot（D005，issue #5）**。生成算法和接受规则（本节 1-5 条）已冻结，只有数值待定。工作方案是由 pilot 选出能稳定产生 connected modular graphs、又不过度固定单一 bridge tank 的参数。手工指定 bridge edges 可解释性强但 network-instance variance 低；纯 stochastic block model 的方差更自然，但可能需要 rejection criteria。

## 4. Betweenness centrality

- 使用 outbreak 前生成并保存的完整 transfer network。
- MVP 使用 unweighted normalized node betweenness centrality。
- 对 node `v`，计算所有其他 source-target pairs 的 shortest paths 中经过 `v` 的比例。
- centrality 在 outbreak 前计算一次，run 中不更新。
- ranking ties 使用较小 `tank_id` 优先，保证 deterministic selection。
- 不允许使用未来 infection、future movements、future affected tanks 或结果选择 targeted tanks。

Weighted 或 dynamic betweenness 不属于 MVP。

## 5. Disease states

| State | Definition | Allowed transition |
|---|---|---|
| `S` | 从未感染且可被感染 | `S -> I` |
| `I` | 当前具有传染性 | `I -> R` |
| `R` | 已恢复并在本次 run 内免疫 | 无 |

- 不存在 `I -> S` 或 `R -> S/I`。
- Newly infected agents 在当日结束时进入 `I`，从下一天开始传播和参与 recovery draw。

## 6. Initialisation

### 6.1 Population and initial infection

- 200 agents；初始每 tank 10 agents。
- 初始状态：199 `S`、1 `I`、0 `R`。
- 使用 epidemic seed 从 200 agents 中均匀选择 initial infected agent。
- 三种 strategies 在同一 paired block 使用相同 initial agent 和 location。
- initial location 不根据 centrality 或 future results 选择；只作为诊断变量记录。

### 6.2 Capacity

主实验中所有 tanks 使用同一 fixed capacity。确切值：**capacity = 12，**Frozen 2026-09-11（D002，Checkpoint 1 后组内采纳 working proposal，见 `decision-log.md`）****。

- 理由：initial occupancy = 10 时有有限移动空间。
- 更高 capacity 会减少 blocked transfers；异质 capacity 会引入混杂，只适合作 sensitivity analysis。

## 7. Within-tank transmission

Movement stage 后，对 tank `j` 计算当前 infectious count `I_j(t)`。对其中每个 susceptible agent：

```text
P(S -> I) = 1 - (1 - beta) ^ I_j(t)
```

这表示每个 infectious agent 对 susceptible agent 产生独立每日感染机会，实现 complete mixing within each tank。

- `beta` 在主实验固定。
- `I_j(t) = 0` 时感染概率为 0。
- susceptible agents 独立抽样。
- Newly infected agents 不在同日继续感染其他 agents。
- `beta` 的 baseline value 由 pilot 选择，使无干预条件既不总是立即消失，也不总是完全感染；不得为支持假设而挑值。

## 8. Recovery

- 每个在当日 transmission stage 开始前已为 `I` 的 agent，以固定每日概率 `gamma` 转为 `R`。
- Recovery 在 transmission calculation 后抽样，因此 agent 在恢复当天仍可传播。
- Newly infected agents 当天不参与 recovery draw。
- `gamma` 在主实验固定，具体值由 pilot 确定并记录。

## 9. Cross-tank movement

### 9.1 Transfer-rate definition

`cross-tank transfer rate` 是每个 agent 每天尝试一次跨缸移动的概率 `mu`。

### 9.2 Eligibility and update

agent 只有在 origin tank 为 `open`，且至少一个相邻 tank 为 `open` 并有 spare capacity 时才 eligible。

- 当日开始时，用 movement random stream 打乱 agents 的处理顺序。
- 按 randomized asynchronous order 处理；每个 agent 每天最多一次 attempt。
- eligible agent 以概率 `mu` 尝试移动。
- 尝试时均匀选择一个当前 open 且有 capacity 的 neighbouring tank。
- 接受后立即更新 location 和两个 tanks 的 occupancy。
- 无合格 destination 时留在原 tank，并记录 blocked/no-destination event。
- disease state 不影响 movement probability；这是明确的模型简化。

## 10. Capacity constraint

- 任何时刻 `occupancy(tank) <= capacity(tank)`。
- movement 使用当前 occupancy 即时检查。
- 不允许暂时超容量再事后修正。
- 初始化必须满足 capacity。

## 11. Response delay and quarantine trigger

MVP 不建立 detection process。工作定义：

```text
response delay d = intervention activation day measured from outbreak introduction at t = 0
```

- `d = 0`：第一个 movement stage 前激活。
- `d > 0`：day `d` 的 movement stage 前激活。
- intervention 只触发一次。

**Delay 起点：从 outbreak introduction（`t = 0`）计算，**Frozen 2026-09-11（D001，Checkpoint 1 后组内采纳 working proposal，见 `decision-log.md`）**。** 替代方案 first observed infection 需要 observation model 或额外 detection assumption，会扩大范围；本项目把 delay 解释为 detection plus administrative response 的合并抽象。

被选 tanks 在 `[start_day, start_day + D)` 为 `quarantined`，day `start_day + D` 恢复 `open`。Duration `D` 在主实验固定，具体值为 **Candidate value, frozen after pilot（D004，issue #4）**。语义（half-open interval、只触发一次、按 tank-days 计 cost）已冻结；实现时 `D` 是普通配置数值，在 config 中标注 provisional。

## 12. Intervention strategies

设 intervention 隔离 `k` 个 tanks，持续 `D` days。

### No intervention

- 不改变 tank states；cost = 0。
- response delay 无实际作用。报告可在同一 transfer/network/epidemic block 内共享 baseline，避免重复相同 runs。

### Random tank quarantine

- 从 20 tanks 中均匀、无放回选 `k` 个。
- 选择只用 `policy_seed`，不读取 infection state 或 future movement。
- run 开始时生成并记录选择，response day 才激活。

### Highest-betweenness tank quarantine

- 根据 outbreak 前 network 的 betweenness 排名选前 `k` 个。
- ties 按 `tank_id` 升序。
- 不使用 epidemic state 或 future information。
- 与 random strategy 同日开始并持续同一 `D`。

### Budget fairness

Random 和 targeted strategies 必须具有相同 `k`、start day、`D`、network instance、epidemic seed、disease parameters 和 movement parameters。唯一主要区别是 tank selection method。

```text
intervention cost = number of quarantined tanks × quarantine duration
                  = k × D tank-days
```

`k`：**2 个 tanks，Frozen 2026-09-11（D003，见 `decision-log.md`）**。理由：避免 intervention 覆盖大部分 20-node 网络。

## 13. Daily update order

1. **Management update**：按 response delay 激活或按 duration 解除 quarantine。
2. **Movement stage**：randomized asynchronous movement；quarantine 和 capacity 即时生效。
3. **Transmission snapshot**：冻结 movement 后 membership 和 disease states。
4. **Transmission draws**：生成 pending `S -> I` transitions。
5. **Recovery draws**：为 snapshot 中原有 `I` 生成 pending `I -> R` transitions。
6. **Synchronous disease commit**：同时应用 infection and recovery transitions。
7. **Record outputs**。
8. **Check stopping condition**。

因此 movement 为 randomized asynchronous，disease updates 为 synchronous。该顺序在主实验固定；若时间允许，可做小规模 update-order sensitivity analysis。

## 14. Stopping conditions

正常停止条件为第一次出现：

```text
total infected population I(t) = 0
```

安全 horizon `max_days`：**365 days，**Frozen 2026-09-11（D006，Checkpoint 1 后组内采纳 working proposal，见 `decision-log.md`）****。达到 horizon 仍有 infection 时：

- 标记 `censored_max_days`；
- 不伪造 extinction time；
- 保留完整记录；
- 在 time-to-extinction 分析中单独处理。

非法状态、不变量失败或异常以 `failed` 结束，不算正常 extinction。

## 15. Output recording rules

### 15.1 Daily outputs

- day；S/I/R population；
- 每个 tank 的 occupancy、S/I/R 和 management state；
- attempted、accepted、blocked transfers；
- new infections、recoveries 和 current affected tanks。

### 15.2 Run metadata

- complete configuration and code commit；
- network、epidemic、policy seeds；
- network attempt index、adjacency list 和 centralities；
- selected tanks、start day、duration、budget；
- run status、stop reason 和 error details。

### 15.3 Metrics

| Metric | Definition | Research link |
|---|---|---|
| Final attack rate | `ever_infected agents / 200`，包含 initial case | primary final outbreak size |
| Number of affected tanks | run 中曾至少出现一个 `I` agent 的不同 tanks 数，包含 initial tank | primary cross-tank spread |
| Peak infected population | 包含 `t=0` 的 daily snapshots 中最大 `I(t)` | outbreak burden/dynamics |
| Time to extinction | 从 `t=0` 到 first `I(t)=0`；censored 不填虚值 | outbreak duration |
| Time to peak | 第一次达到 peak 的 day | auxiliary dynamics |
| Intervention cost | `k × D` tank-days | fairness/resource use |
| Relative reduction vs random | `(Y_random - Y_targeted) / Y_random` | secondary comparison |

若 `Y_random = 0`，relative reduction 记为 undefined，而不是 0。

## 16. Random-number and seed management

| Seed | Controls |
|---|---|
| `network_seed` | topology and regeneration attempts |
| `epidemic_seed` | initial case、movement、transmission、recovery |
| `policy_seed` | random quarantine selection only |

为保持 paired comparison，epidemic randomness 应使用独立 substreams 或 event-keyed random draws，避免某策略少发生一次 draw 后使后续随机序列整体错位。至少分别建立 initialisation、movement、transmission 和 recovery streams，并从 epidemic seed 确定性派生。

相同 configuration 和 seeds 必须得到相同结果。

## 17. Prohibition on future information

Intervention selection 禁止使用 future infection states、future transfers、future affected tanks、final metrics 或 run 中重算的 disease-informed centrality。Targeted selection 只使用 pre-outbreak fixed network；random selection 只使用 policy seed。

## 18. Decision status and two-layer freeze rule

| ID | Item | Status | Value / rule |
|---|---|---|---|
| D001 | Response-delay origin | Frozen 2026-09-11 | From introduction at `t = 0`（§11） |
| D002 | Fixed capacity | Frozen 2026-09-11 | 12（§6.2） |
| D003 | Quarantined tank count `k` | Frozen 2026-09-11 | 2（§12） |
| D004 | Quarantine duration `D` | Semantics frozen；value after pilot | §11；issue #4 |
| D005 | `p_in` / `p_out` / acceptance thresholds | Algorithm frozen；values after structural pilot | §3；issue #5 |
| D006 | `max_days` | Frozen 2026-09-11 | 365（§14） |
| D007 | No-intervention reporting | Frozen 2026-09-11 | Shared baseline per block（experiment-plan §3） |
| D008 | Headline outcome | Frozen 2026-09-11 | Attack rate + affected tanks co-primary（§15.3） |

**两层冻结规则（2026-09-11 起生效，取代原"所有决定必须在代码实现前冻结"）：**

1. **语义冻结（实现前）**：状态定义、更新顺序、传播/恢复/移动/隔离规则、seed 派生方式、输出字段。以上全部已冻结。M2 实现只能依据本文件，不得在实现中另作语义选择。
2. **数值冻结（正式实验前）**：`beta`、`gamma`、`D`、`p_in`/`p_out`、transfer-rate levels、delay levels、replication counts 在 19-25 Sep pilot 后冻结，记录在 `decision-log.md` 和 experiment config。在此之前这些字段是普通配置数值，由代码自动标注为 provisional 并写入 run metadata；pilot 结果不作为假设证据。

任何语义变更仍按 `consistency-review.md` §6 触发跨文档更新。
