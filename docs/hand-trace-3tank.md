# Hand Trace: 3 tanks, 6 agents, 3 days（issue #14）

对应 `validation-plan.md` §9 integration validation。本 fixture 只用于验证，不是实验，不产生结果。自动化对照测试在 `tests/test_hand_trace.py`；本文件是手算依据，**期望值由人手算，不得从模型输出反填**。

## 1. Scenario

| Item | Value |
|---|---|
| Tanks | T0（region 0）、T1（region 0）、T2（region 1），capacity 12 |
| Agents | 0、1、2 在 T0；3、4 在 T1；5 在 T2 |
| Initial state | agent 0 = `I`，其余 `S` |
| `beta` | 0.5 |
| `gamma` | 0.5 |
| Movement / intervention | 无（M1） |
| Config | `design="scenario"`，`n_agents=6`，`n_tanks=3`，`max_days=10` |

规则回顾（spec §7、§8、§13）：每天先对 day 开始时的状态做 snapshot；每个 `S` agent 在同缸有 `I_j > 0` 时以 `P = 1 - (1 - beta)^{I_j}` 感染；每个 snapshot 中的 `I` agent 以 `gamma` 恢复；两组 draws 同步 commit（先恢复后感染）。**当天新感染者不传播、不恢复；无暴露的 S agent 不消耗 draw。**

## 2. Fixed draws（TableDraws）

只列出规格规定会被消耗的 draws。表中不存在的 draw 若被模型读取，`TableDraws` 抛错、run 变为 `failed`，测试即失败。

| Day | Process | Agent | Draw | Threshold | Outcome |
|---|---|---|---|---|---|
| 1 | transmission | 1 | 0.30 | P = 1 − 0.5¹ = 0.50 | 0.30 < 0.50 → 感染 |
| 1 | transmission | 2 | 0.60 | 0.50 | 0.60 ≥ 0.50 → 仍 S |
| 1 | recovery | 0 | 0.70 | gamma = 0.50 | 0.70 ≥ 0.50 → 仍 I |
| 2 | transmission | 2 | 0.70 | P = 1 − 0.5² = **0.75** | 0.70 < 0.75 → 感染（若误用 P = 0.5 则不会感染，故此值能区分指数是否正确） |
| 2 | recovery | 0 | 0.20 | 0.50 | 恢复 |
| 2 | recovery | 1 | 0.90 | 0.50 | 仍 I |
| 3 | recovery | 1 | 0.40 | 0.50 | 恢复 |
| 3 | recovery | 2 | 0.10 | 0.50 | 恢复 |

不应被消耗的 draws（表中故意缺失）：day 1 agents 3、4、5 的 transmission（同缸无 I）；day 2 agent 2 的 recovery（当天新感染）；day 3 任何 transmission（T0 已无 S）。

## 3. Day-by-day hand computation

**Day 0（初始）**：S = {1,2,3,4,5} = 5，I = {0} = 1，R = 0。affected tanks = 1。

**Day 1**
- Snapshot：T0 有 1 个 I（agent 0）。
- 暴露的 S：agent 1（P = 0.5，draw 0.30 → 感染）、agent 2（draw 0.60 → 不感染）。agents 3、4、5 无暴露。
- Recovery：agent 0（draw 0.70 → 不恢复）。
- Commit：agent 1 → I。
- 结果：S = {2,3,4,5} = 4，I = {0,1} = 2，R = 0。new_infections = 1，recoveries = 0。

**Day 2**
- Snapshot：T0 有 2 个 I（agents 0、1）。
- 暴露的 S：agent 2，P = 1 − (0.5)² = 0.75，draw 0.70 → 感染。
- Recovery：agent 0（0.20 → 恢复），agent 1（0.90 → 不恢复）。agent 2 当天新感染，无 recovery draw。
- Commit（先恢复后感染）：agent 0 → R，agent 2 → I。
- 结果：S = {3,4,5} = 3，I = {1,2} = 2，R = {0} = 1。new_infections = 1，recoveries = 1。
- T0 行：S 0 / I 2 / R 1；T1：2/0/0；T2：1/0/0。

**Day 3**
- Snapshot：T0 有 2 个 I（agents 1、2），T0 无 S，无 transmission draw。
- Recovery：agent 1（0.40 → 恢复），agent 2（0.10 → 恢复）。
- 结果：S = 3，I = 0，R = 3。new_infections = 0，recoveries = 2。I = 0 → **extinction on day 3**，status `completed`。

## 4. Expected summary

| Day | S | I | R | new_inf | rec | affected_now | affected_ever |
|---|---|---|---|---|---|---|---|
| 0 | 5 | 1 | 0 | 0 | 0 | 1 | 1 |
| 1 | 4 | 2 | 0 | 1 | 0 | 1 | 1 |
| 2 | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| 3 | 3 | 0 | 3 | 0 | 2 | 0 | 1 |

Transition log（day, agent, from, to）：(1,1,S,I)、(2,0,I,R)、(2,2,S,I)、(3,1,I,R)、(3,2,I,R)。

Metrics：ever_infected 3、final_attack_rate 0.5、affected_tanks 1、peak_infected 2、time_to_peak 1、time_to_extinction 3、days_simulated 3。

## 5. Model comparison and sign-off

| Check | Result | Evidence |
|---|---|---|
| Daily S/I/R、new_infections、recoveries、affected tanks 逐日一致 | 一致 | `tests/test_hand_trace.py::test_hand_trace_matches_event_log`（2026-09-11） |
| Transition log 一致（含 commit 顺序） | 一致 | 同上 |
| 消耗的 draws 恰好是表 2 的 8 个，顺序一致 | 一致 | `draws.consulted` 断言 |
| 删除 day 2 agent 2 的 transmission draw 后 run 失败 | 失败如预期 | `test_hand_trace_fails_loudly_if_an_unlisted_draw_is_consulted` |

Differences found：无。

- [ ] Member A 已独立重算并确认（日期：）
- [x] Member B 已独立重算并确认（日期：2026-09-16）
