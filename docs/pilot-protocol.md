# Pilot Protocol（experiment-plan §7、§9；D004 / D005；issues #4、#5）

Status：**DRAFT — Member A 起草（2026-09-20），待 Member B 确认。两名成员确认前不得运行 pilot，也不得查看任何 pilot outcome。**

本文件沿用 `network-audit-2026-09-11.md` 的做法：**在看数据之前写下选择标准**。Pilot 只用于参数冻结、bug discovery 和 runtime estimation，不是假设证据（experiment-plan §7）。本文件不含任何模拟结果。

## 1. 防止 outcome-driven tuning 的规则

1. 本文件的选择标准在运行前由两名成员确认并合入 `main`；确认后修改标准必须写入 `decision-log.md` 并说明原因。
2. **Pilot 数据上不得计算 random 与 betweenness 的差值**，也不得按 strategy 分组比较 outcome。Stage 2 只使用 strategy 合并（pooled）后的机制性指标。
3. Pilot seeds 不进入正式实验：network seeds `100-104`、epidemic seeds `9000-9009`、policy seeds `900-902` 在 parameter-freeze record 中列为排除。
4. 所有尝试过的 candidate、未通过的 candidate 和 failed / censored runs 全部保留并写入 pilot report，不删除。
5. 若所有 candidate 都不满足标准，不得临时放宽阈值后挑一个；应记录结果、扩展 candidate grid、由两名成员确认新 grid 后重跑完整 stage。

## 2. 运行方式

```bash
python scripts/run_experiment.py experiments/config/pilot-stage1-disease.json --dry-run   # 只校验并打印 run 数
python scripts/run_experiment.py experiments/config/pilot-stage1-disease.json
```

Raw records 写入 `results/raw/<name>.jsonl`（git-ignored，append-only），逐 run 汇总表写入 `results/summary/<name>.csv`。Runtime 估计（2026-09-20，`smoke` design 实测 20 runs / 0.4 s）：Stage 1 的 2000 runs 约 1 分钟，raw 文件约 300 MB。

## 3. Stage 1 — disease regime 和 transfer-rate levels（只跑 no intervention）

Design：`experiments/config/pilot-stage1-disease.json`。

| 项 | 值 |
|---|---|
| Strategy | 只有 `none`（不含任何 quarantine run，因此不可能泄露 strategy 效果） |
| `beta` candidates | 0.05、0.10、0.15、0.20 |
| `gamma` candidates | 0.10、0.20 |
| Transfer-rate candidates | 0、0.01、0.02、0.05、0.10 |
| `p_in` / `p_out` | 0.6 / 0.05（D005 candidate，来自 structural audit） |
| Seeds | 5 network × 10 epidemic = 50 blocks per candidate per level |
| Runs | 8 × 5 × 50 = 2000 |

回答 pilot questions 1、2、5（capacity 部分）、6。Question 4（network generator 稳定性）已由 structural audit 回答。

### 选择标准（运行前写下）

以下指标全部来自 `results/summary/pilot-stage1-disease.csv`。“minor outbreak” 定义为 `final_attack_rate ≤ 0.06`（初始 tank 最多 12 个 agents，即感染基本未离开初始 tank 的规模）。

| # | 标准 | 阈值 | 对应问题 |
|---|---|---|---|
| S1 | Hard check：`transfer_rate = 0` 时 `affected_tanks = 1` | 100% runs；任何违反都是 bug，暂停 pilot | 结构 baseline（experiment-plan §3） |
| S2 | 无 failed run；censored share | failed = 0；`censored_max_days` ≤ 1% | Q6：365-day horizon 是否足够 |
| S3 | 不全是 minor outbreak | 在最高的两个 non-zero transfer levels，minor-outbreak share ≤ 70% | Q1：避免“全部迅速 extinction” |
| S4 | 不触顶 | 在最低的 non-zero transfer level，`final_attack_rate` median ≤ 0.90 | Q1：避免“几乎全部感染”，给 intervention 留下可观测空间 |
| S5 | Transfer levels 可区分 | 存在 3 个 non-zero levels，其 median `affected_tanks` 严格递增，且相邻 level 的 mean `accepted_transfers / days_simulated` 至少相差 2 倍 | Q2 |
| S6 | Capacity 不主导 movement | 每个 non-zero level 的 `blocked_transfers / attempted_transfers` ≤ 20% | Q5 |

选择规则：

1. 保留同时满足 S1-S6 的 `(beta, gamma)` candidates。
2. 若多于一个：选 S5 所选三个 levels 中**中间 level** 的 median `final_attack_rate` 最接近 0.5 的 candidate（上下都有最大变化空间）；仍并列则选较小的 `beta`。
3. Transfer-rate levels = `0` + S5 中满足条件的三个 non-zero levels；若有多组满足，选跨度（最高 level − 最低 level）最大的一组；跨度仍并列时，选**中间 level 较小**的一组（在 hypothesis 关心的低转移率一侧保留更细的分辨率；该规则不看任何 outcome）。例：`(0.01, 0.02, 0.1)` 与 `(0.01, 0.05, 0.1)` 并列时选前者。

这些标准只使用 no-intervention runs，因此与 hypothesis 的方向无关。

## 4. Stage 2 — response-delay levels 和 quarantine duration `D`

Stage 2 的 design 文件在 Stage 1 结论写入 `decision-log.md` 之后才创建（需要填入选定的 `beta`、`gamma` 和 transfer levels），命名 `experiments/config/pilot-stage2-intervention.json`。

| 项 | 值 |
|---|---|
| Strategies | `none` + `random` + `betweenness`（runner 的标准 block 结构） |
| `D` candidates（`sweep.quarantine_duration`） | 7、14、21 |
| Response-delay candidates | 由下方 D1-D3 规则从 Stage 1 数据推出，不再另行扫描 |
| Policy seeds | 900、901、902 |
| Transfer rates | Stage 1 选出的三个 **non-zero** levels。`transfer_rate = 0` 时 quarantine 不可能拦截任何转移（Q1 必然不满足），加入只会稀释 Q1，因此不纳入 Stage 2 |
| Seeds | 与 Stage 1 相同的 5 × 10 blocks |

### Response-delay levels（只用 Stage 1 的 no-intervention 数据决定）

在选定的 `(beta, gamma)` 和中间 transfer level 下，对**非 minor outbreak** 的 runs：

| Level | 规则 |
|---|---|
| D1 immediate | `1`（第一个 movement stage 之前生效，D001） |
| D2 intermediate | `affected_tanks_ever` 首次达到 2 的 day 的 median（感染首次离开初始 tank） |
| D3 late | `time_to_peak` 的 median |

Median 不是整数时按四舍五入（0.5 进位，`floor(x + 0.5)`）取整为 day。

若 D2 ≥ D3 或 D2 ≤ 1，说明三个 levels 无法区分：记录该结果，回到 Stage 1 选择规则的下一个 candidate，不得手动挑选 delay。

### `D` 的选择标准（strategy 合并后计算，不比较 strategy）

| # | 标准 | 阈值 | 理由 |
|---|---|---|---|
| Q1 | Quarantine rules intercept attempted movement | At least one attempt attributed to a quarantine rule in ≥ 90% of intervention runs whose quarantine started; counter definitions and threshold below are unchanged. Both historical mixed-counter denominators remain proxies only. | Operational check of rule interception, not proof of additional successful transfers prevented; see the 2026-10-07 clarification below. |
| Q2 | Quarantine 不覆盖整个 epidemic | `D` ≤ 选定 regime 下 no-intervention `time_to_extinction` median 的 25%（取 Stage 2 全部 transfer levels 的共享 baseline 中 status = completed 的 runs 合并计算；censored runs 不计入） | Q5：不能“几乎删除整个 network” |
| Q3 | 至少覆盖一个平均 infectious period | `D ≥ 1 / gamma` | 短于 infectious period 的隔离在机制上难以解释 |

Q1 correction after review (2026-10-06): `blocked_transfers` combines quarantine and capacity blocking across the whole run, including days before and after quarantine. A low capacity-blocking fraction per transfer (S6) does not imply that few runs have at least one capacity block. Consequently neither historical proxy verifies Q1. Verification requires a separately defined, tested quarantine-specific counter restricted to the active interval; no such evidence is added in this correction.

选择规则：满足 Q1-Q3 的最小 `D`。Budget 为 `k × D` tank-days，对 random 和 betweenness 相同（D003：`k = 2`）。

Until Q1 is verified, the selector must return no automatically validated duration. `D=14` remains the setting of the already completed formal experiment, not a newly validated Q1-Q3 selection. Q2 and Q3 alone identify 14 among the tested candidates. Keeping this setting avoids changing the experiment in response to its outcomes; it does not repair the missing Q1 evidence. Historical proxy output is retained in `results/pilot/stage2-criteria-legacy-proxy.csv`.

#### Quarantine-specific Q1 (pre-registered 2026-10-06, before the counter exists or the pilot is rerun)

This section is committed before any model change and before `pilot-stage2-intervention` is rerun. Nobody has seen a quarantine-specific blocking count when it is written. The historical proxy results above are already known.

Classification of every blocked transfer attempt, in the order the movement stage checks them:

| Counter | Condition |
|---|---|
| `blocked_quarantine_out` | The origin tank is `QUARANTINED`. |
| `blocked_quarantine_in` | The origin is `OPEN`, no neighbour is an eligible destination, and at least one neighbour is `QUARANTINED` with `occupancy < capacity`. Had quarantine not applied, that neighbour would have been eligible. |
| `blocked_capacity` | Every other blocked attempt: all neighbours are full or there are none, regardless of their management state. |

The three counters partition `blocked_transfers` on every day. Quarantine counters can be nonzero only while a tank is quarantined, so they are restricted to the active interval by construction. Adding them must not change any simulated trajectory: all random draws are event-keyed and the counters do not draw.

Q1 (quarantine is not a no-op): among intervention runs (random and betweenness pooled, status not `failed`) in which quarantine started (`intervention_start_day` not null), the share with `blocked_quarantine_out + blocked_quarantine_in ≥ 1` is ≥ 90%. The started-runs denominator was itself chosen after seeing data (see decision log); the all-runs share is reported alongside it.

Procedure and pre-specified consequences:

1. Rerun `pilot-stage2-intervention` with the new counters. Every pre-existing summary column except `code_commit`, `run_id` (a fresh UUID per run) and `configuration_hash` must be identical to the committed summary, matched on the condition key (`network_seed`, `epidemic_seed`, `policy_seed`, `transfer_rate`, `response_delay`, `strategy`, `quarantine_duration`). `configuration_hash` changes because the parameter freeze (`f4eac85`) emptied `provisional_fields` after the pilot ran; with the old list restored, all 5550 hashes match. If not, stop: the counters changed the model, and no Q1 result is used.
2. Run `pilot_select.py stage2`. The selection rule is unchanged: the smallest `D` meeting Q1-Q3.
3. If `D=14` is selected, D004 is recorded as validated by Q1-Q3, with the denominator change still disclosed.
4. If no `D` passes, `D=14` remains the setting of the completed formal experiment, the report states that Q1 failed and by how much, and the formal experiment is not rerun or changed.
5. Q2 and Q3 admit only `D=14`, so no other `D` can be selected. Should that nonetheless happen, it is reported and the formal experiment is still not changed.

#### Interpretation and completeness clarification (2026-10-07 review follow-up)

This clarification was added after the rerun; it does not amend the pre-registered counter definitions, threshold or selection rule above. The counters classify attempts by the first blocking rule reached. In particular, `blocked_quarantine_out` includes an attempted departure from a quarantined origin even when every neighbouring tank is full. Removing quarantine would not make that attempt succeed. Q1 therefore verifies operational interception by quarantine rules, not a strict counterfactual effect on successful transfers or on disease outcomes. The recorded 95.7% at D=14 must be interpreted in that limited sense.

All three cause columns must be present and non-missing for every summary row before the evaluator marks Q1 as verified. Missing columns or values leave Q1 unknown and prevent automatic duration selection; the mixed total cannot replace them. The two other acceptance criteria and all completed experiment settings remain unchanged.

## 5. 选择规则的实现

上述标准由 `turtlefarm/analysis.py` 实现，`scripts/pilot_select.py stage1` / `stage2` 应用于记录好的 pilot 结果，并把每个 candidate 的逐项判定写入 `results/pilot/`。规则无法给出唯一选择时（例如没有 candidate 通过、规则 2 在 `beta` 也相同时仍并列），脚本以 exit code 3 停止，不自动挑选；按 §1 rule 5 处理。

2026-10-06 补充（运行前、未看任何 pilot 数据）：Stage 1 规则 3 的并列处理、Stage 2 的 transfer levels、delay 取整、Q2 的 baseline 范围和 Q1 的计数局限。

## 6. Pilot 之后

1. 写 `docs/pilot-report-<date>.md`：每个 candidate 的标准逐项结果、被排除的 candidate、failed / censored runs、runtime。
2. 在 `decision-log.md` 冻结 `beta`、`gamma`、`D`、`p_in` / `p_out`、transfer-rate levels、delay levels、seed lists 和 replication counts，关闭 issues #4、#5。
3. 创建 `experiments/config/formal.json`（无 `sweep`；seeds 与 pilot seeds 不重叠）。
4. 从 `turtlefarm/config.py` 的 `PROVISIONAL_FIELDS` 中移除已冻结的字段。

## 7. Sign-off

| Member | 确认标准（运行前） | 日期 |
|---|---|---|
| Member A（Cam Zhou） | 起草 | 2026-09-20 |
| Member B（Wenhao Zhang） | 待确认 | — |
