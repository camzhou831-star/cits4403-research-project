# Validation Plan

本文件只定义未来的测试与验证，不包含测试代码。

## 1. Validation goals

1. 验证实现符合 `model-specification.md`；
2. 验证 stochastic behaviour 可复现；
3. 验证策略比较预算和随机条件公平；
4. 验证极端参数下出现可预期行为；
5. 区分 model logic error、configuration error 和合法随机结果。

## 2. Required invariants

| ID | Invariant | Planned evidence |
|---|---|---|
| V001 | Agent 总数始终等于 200 | 每日汇总与 agent table count 一致 |
| V002 | 每个 agent 只属于一个 tank | location uniqueness check |
| V003 | 每个 agent state 只为 S/I/R | enum/domain validation |
| V004 | `S + I + R = 200` 每日成立 | daily assertion and summary |
| V005 | Recovered agent 不能再次感染 | transition log 无 `R -> I` |
| V006 | Tank occupancy 不超过 capacity | 每次 movement 后检查 |
| V007 | Quarantined tank 无转入和转出 | movement event audit |
| V008 | Quarantine 内部传播仍可发生 | controlled scenario review |
| V009 | Random/targeted 使用相同 `k`、start、duration | paired configuration comparison |
| V010 | Centrality 只来自 pre-outbreak network | provenance and immutable network hash |
| V011 | Same config + seeds gives same outputs | repeated deterministic replay |
| V012 | Model reaches extinction or explicit horizon status | every run has stop reason |

## 3. Extreme and boundary cases

### V101 - `beta = 0`

- Initial infected may recover but no `S -> I` transition is allowed。
- Final ever-infected count must equal initial infected count。

### V102 - `transfer_rate = 0`

- No accepted cross-tank movement。
- Infection cannot enter any tank other than the initial infected tank。
- Number of affected tanks must remain 1。

### V103 - `gamma = 1`

- Existing infected agents recover at the first eligible recovery step after transmitting according to update order。
- Expected behaviour must match the documented “transmit then recover” rule。

### V104 - `beta = 1` with infected tank

- All susceptible agents sharing a tank with at least one infectious agent become infected in the transmission commit。
- Newly infected do not recover or infect further until next day。

### V105 - `transfer_rate = 1`

- Every eligible agent attempts movement once；capacity and quarantine still hold。
- Actual accepted rate may be below 1 due to capacity/no destination。

### V106 - Full tank

- No incoming movement may violate capacity。
- Blocked movement is recorded, not treated as simulation failure。

### V107 - Quarantine interval boundaries

- Tank blocks movement on days in `[start, end)`。
- Movement is allowed again at `end` before that day's movement stage。

### V108 - Zero-day response

- Intervention active before the first movement stage。
- It does not retroactively alter initial state。

### V109 - No intervention

- No tank enters quarantined state；cost = 0。
- Changing the unused response-delay label cannot change the run。

### V110 - Betweenness tie

- Ties resolve by ascending `tank_id`，unless this rule is later explicitly changed and documented。

## 4. Probability and configuration validation

- `0 <= beta <= 1`；
- `0 <= gamma <= 1`；
- `0 <= transfer_rate <= 1`；
- response delay、duration、`k`、capacity、`max_days` 为合法非负/正整数；
- `k <= 20`；
- initial occupancy <= capacity；
- exactly 20 tanks、4 regions、5 tanks per region；
- network simple、undirected、connected and has inter-region edges；
- seeds 可序列化且记录；
- invalid configuration 在 run 开始前拒绝，不能静默 clamp。

## 5. Strategy fairness validation

对每个 paired block 自动或人工核对：

- network hash 相同；
- epidemic seed 相同；
- initial infected agent/tank 相同；
- transfer rate、beta、gamma、capacity 相同；
- response day 相同；
- quarantine count 和 duration 相同；
- cost 相同；
- targeted selection 与 pre-outbreak centrality ranking 一致；
- random selection 与 policy seed 对应且无放回；
- 唯一主要 policy difference 是 selected tanks。

## 6. Future-information validation

- 保存 pre-outbreak network hash 和 centrality table。
- Intervention selector 接口只接受 network/topology、`k` 和 policy seed，不接受 epidemic state 或 output data。
- Targeted selected tanks 在不同 epidemic seeds 下应保持不变，只要 network seed 相同。
- 在 code review 中检查 selector 是否读取 daily infection/movement records。

## 7. Reproducibility validation

1. 对 selected configurations 连续运行两次；
2. 比较 daily event log、selected tanks、final metrics 和 stop reason；
3. Same seeds 必须 byte-equivalent 或 canonical-data-equivalent；
4. 改变一个 seed 应只改变它负责的 randomness：
   - network seed 改 topology；
   - epidemic seed 改 epidemic/movement trajectory；
   - policy seed 只改 random quarantine selection。

## 8. Model-level plausibility checks

这些不是现实 calibration，只检查 behaviour 是否 sensible：

- 提高 transfer rate 后 accepted transfer count 平均不应下降，除非 capacity/quarantine blocking 明确解释；
- `mu=0` 时只出现 local outbreak；
- intervention 越早并不要求每个 seed 都更好，但 aggregate anomalies 需要检查；
- highest-betweenness tanks 应与跨 region shortest paths 有清楚结构关系；
- network generator 不应经常产生所有 nodes 相同 centrality 的对称结构。

## 9. Integration validation

在单项规则验证后，使用一个极小、手工可推演 network 做 end-to-end trace：

- 少量 tanks 和 agents；
- 固定 random draws；
- 手工计算一至数天 movement、infection、recovery、quarantine；
- 与 model event log 对比。

该 fixture 只用于验证，不作为正式实验或结果。

## 10. Failure and completion criteria

模型进入正式实验前必须：

- 所有 V001-V012 通过；
- V101-V110 extreme cases 符合规范；
- same-seed replay 通过；
- fairness audit 通过；
- 两名成员分别阅读 event trace 并签字确认；
- 不存在未解释的不变量 failure。

每个 run 必须正常 extinction、`censored_max_days` 或 `failed`；不能无 stop reason 无限运行。
