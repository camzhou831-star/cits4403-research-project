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
| Q1 | Quarantine 不是空操作 | pooled intervention runs 中**隔离实际启动（`intervention_start_day` 非空）的 runs** 里 `blocked_transfers ≥ 1` 的 share ≥ 90%（2026-10-06 看过 Stage 2 数据后修正分母，原定义为全部 intervention runs；见 `decision-log.md`，两种定义的结果都报告） | Q5：`k`、`D` 不能无效 |
| Q2 | Quarantine 不覆盖整个 epidemic | `D` ≤ 选定 regime 下 no-intervention `time_to_extinction` median 的 25%（取 Stage 2 全部 transfer levels 的共享 baseline 中 status = completed 的 runs 合并计算；censored runs 不计入） | Q5：不能“几乎删除整个 network” |
| Q3 | 至少覆盖一个平均 infectious period | `D ≥ 1 / gamma` | 短于 infectious period 的隔离在机制上难以解释 |

Q1 的局限：模型的 `blocked_transfers` 同时计入“origin 被隔离”和“没有 open 且未满的 neighbour”（含 capacity）两种拦截，不单独区分 quarantine。Stage 1 的 S6 已限制 capacity 拦截占比 ≤ 20%，因此 Q1 主要反映 quarantine；pilot report 需写明这一点。

选择规则：满足 Q1-Q3 的最小 `D`。Budget 为 `k × D` tank-days，对 random 和 betweenness 相同（D003：`k = 2`）。

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
