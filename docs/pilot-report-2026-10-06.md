# Pilot Report（2026-10-06）

**Review correction:** Stage 2's whole-run blocked-transfer percentages are historical proxies, not verified quarantine-specific effects. Q1 remains unverified. `D=14` is retained as the completed experiment's setting; it must not be described as passing a fully validated Q1-Q3 gate. See section 7 below.

按 `pilot-protocol.md` §6 第 1 步编写。Pilot 只用于参数冻结、bug discovery 和 runtime estimation，不是假设证据：本报告**不包含任何 random 与 betweenness 的比较**，Stage 2 指标全部是两种策略合并后的结果。

所有判定由 `scripts/pilot_select.py` 按已推送的标准机械计算。逐项表在 `results/pilot/`，原始记录在 `results/raw/`（git-ignored，append-only，未删除任何 run）。偏离协议之处见 `decision-log.md` “Protocol deviations”。

## 1. 运行概况

| Design | Runs | Completed | Censored | Failed | Runtime |
|---|---|---|---|---|---|
| `pilot-stage1-disease`（第 1 轮） | 2000 | 2000 | 0 | 0 | 37 s |
| `pilot-stage1-disease-r2`（第 2 轮，grid 加 0.025） | 2400 | 2400 | 0 | 0 | 45 s |
| `pilot-stage2-intervention` | 5550 | 5550 | 0 | 0 | 123 s |

Seeds：network 100-104，epidemic 9000-9009，policy 900-902。这些 seeds 不进入正式实验。

## 2. Stage 1 第 1 轮：无 candidate 通过

8 个 `(beta, gamma)` candidates 全部满足 S1-S4、S6，全部**只因 S5 失败**。

- S5 要求相邻 level 的 mean accepted transfers per day 至少相差 2 倍。原 grid `0.01 / 0.02 / 0.05 / 0.1` 中，0.01→0.02 与 0.05→0.10 的名义比例正好是 2 倍。Capacity 拦截使实测比例约为 1.77 倍和 1.88 倍，因此任何三档组合都不满足 S5。
- 按 rule 5，阈值不变，grid 增加 0.025 后完整重跑（`decision-log.md`，第 2 轮运行前推送）。

## 3. Stage 1 第 2 轮：选定 disease regime 与 transfer levels

| beta | gamma | S1-S6 | S5 levels（rule 3） | 0.025 档 median attack rate | 距 0.5 |
|---|---|---|---|---|---|
| 0.05 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.192 | 0.308 |
| 0.05 | 0.2 | **fail（S5）** | — | — | — |
| 0.10 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.262 | 0.238 |
| 0.10 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.092 | 0.408 |
| 0.15 | 0.1 | pass | 0.01 / 0.025 / 0.1 | 0.435 | 0.065 |
| 0.15 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.103 | 0.397 |
| **0.20** | **0.1** | **pass** | **0.01 / 0.025 / 0.1** | **0.458** | **0.042** |
| 0.20 | 0.2 | pass | 0.01 / 0.025 / 0.1 | 0.112 | 0.388 |

其他标准的观察值：

- S1：`transfer_rate = 0` 时所有 runs 的 `affected_tanks = 1`，与预期一致，未发现 movement bug。
- S2：没有 failed run，也没有 censored run，365 天 horizon 足够。
- S6：各 level 的 capacity 拦截占比为 3.5%-7.7%，远低于 20%。

Rule 2 选中 `beta = 0.2, gamma = 0.1`。Transfer levels 为 **0 / 0.01 / 0.025 / 0.1**。

Response delays 由 40 个 non-minor runs 计算，结果为 **1 / 12 / 33 天**：

- D2：感染首次到达第 2 个 tank 的 day 的 median = 12.0；
- D3：`time_to_peak` 的 median = 33.0；
- 两个 median 都是整数，没有发生取整。

需要在报告中说明：在选定 regime 下，`transfer_rate = 0.1` 的 no-intervention median attack rate 为 1.0（接近饱和），该 level 上的 intervention 差异可能受天花板限制。

## 4. Stage 2：quarantine duration `D`

| D | Runs | 隔离实际启动 | blocked ≥ 1（全部 runs） | blocked ≥ 1（已启动） | All-runs proxy | Started-runs proxy | Q2（D ≤ 16.25） | Q3（D ≥ 10） |
|---|---|---|---|---|---|---|---|---|
| 7 | 1800 | 1516 | 85.3% | 97.3% | fail | pass | pass | fail |
| **14** | 1800 | 1516 | 85.3% | 97.4% | fail | pass | pass | pass |
| 21 | 1800 | 1516 | 85.3% | 97.4% | fail | pass | fail | pass |

No-intervention `time_to_extinction` median = 65 天，因此 Q2 的上限为 16.25 天。

- **No D passed the original all-runs proxy threshold.** Of 1,800 intervention runs per duration, 284 ended before quarantine started. They occur at delays 12 and 33. However, 60 of these 284 runs per duration still have blocked transfers, so non-start is not equivalent to zero blocking.
- 隔离实际启动的 runs 中，没有拦截任何转移的几乎都是 minor outbreak（median attack rate 0.005）。
- Q1 的分母已修正为“隔离实际启动的 runs”，这是看过 Stage 2 数据后的修正，见 `decision-log.md`。
- Only `D=14` meets Q2 and Q3 among the tested durations. This does not establish Q1: both historical percentages use a counter that mixes blocking causes and days outside quarantine.
- The completed experiment used **D=14**, with a planned budget of `k × D = 28` tank-days. This setting is retained for reporting the existing experiment, not certified as a fully validated Q1-Q3 selection.

## 5. 对正式实验的影响

- Delay 12 和 33 下，约 20%-34% 的 runs 在隔离开始前已经结束。三种 strategy 在这些 runs 中的 outcome 完全相同，配对差为 0。正式分析需要同时报告：
  - 全部 blocks 的效应；
  - 只看“response day 时仍有感染”的 blocks 的效应。
- Runtime 约 45 runs/s。正式实验 5200 runs 预计 2 分钟。

## 6. 补充说明（2026-10-06，正式实验后发现）

Pilot 的 seeds 是交叉的：每个 network 使用同一组 epidemic seeds 9000-9009。在 event-keyed draws 下，同一 epidemic seed 在所有 network 上有相同的初始感染 agent 和早期抽样，因此本报告中的比例实际只基于 **10 个独立的疫情起点**（network 间的变异仍然有效）。

例如，§4 中 D = 14 下“隔离从未启动”的 284 个 runs 有 240 个来自 seeds 9003 和 9006：这两个 seeds 在所有 network 上都在第 12 天前 extinction。其余 44 个来自 9002、9005、9009。

参数选择不重做。正式实验改为嵌套 seeds（`formal-nested`），见 `decision-log.md`。

## 7. Q1 counter audit after review (2026-10-06)

`blocked_transfers` sums all daily blocking, including capacity blocking and days outside the quarantine interval. Restricting the denominator to started runs does not isolate the cause or timing of a block. S6 limits the fraction of attempted transfers blocked by capacity; it does not limit the fraction of runs with at least one such event.

For the 1,516 started intervention runs at `D=14`, 1,476 have at least one block (97.3615%). Matching each to its no-intervention baseline by `(network_seed, epidemic_seed, transfer_rate)` gives 1,392 baseline matches with at least one block (91.8206%). These are repeated, matched baselines weighted like the intervention runs, not 1,516 independent baseline simulations. Capacity-only blocking already exceeds the 90% proxy threshold. Among the 284 never-started runs, 60 also have a nonzero counter.

The original table is preserved unchanged as `results/pilot/stage2-criteria-legacy-proxy.csv`. The regenerated `stage2-criteria.csv` labels both old checks as proxies, records `Q1_status=unverified_mixed_blocking_counter`, and leaves the quarantine-specific check unknown. `passed` is unknown for candidates satisfying Q2/Q3 and false when either of those criteria fails. No candidate is automatically selected.

This correction changes neither the model nor the formal design, results or figures. A future validation must define and count quarantine-caused blocking during the active interval, separately from capacity blocking, before asserting that Q1 is satisfied. No new threshold, duration or favourable outcome has been selected in this correction.
