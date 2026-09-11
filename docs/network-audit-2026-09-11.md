# Network Structural Audit（issue #16，risk R002，D005 candidates）

日期：2026-09-11（2026-09-11 review 后修订措辞并增加 cross-path 指标）。生成器：`turtlefarm/network.py`；脚本：`scripts/audit_network.py --seeds 10 --k 2`。

**这是 structural pilot，不涉及疫情模拟，不是假设证据。** 目的只有两个：确认生成器在候选参数下稳定产生 connected、modular、betweenness 排名非平凡的网络（spec §3、§4；R002），并为 D005 给出候选数值。数值在 19-25 Sep pilot 后冻结。

## 1. Accepted-structure rules（spec §3.2 step 4 的具体化）

每次 attempt 按固定 pair 顺序（`itertools.combinations(range(20), 2)` 字典序）独立抽 edge（同区 `p_in`，跨区 `p_out`），generator 为 `PCG64(SeedSequence(network_seed, spawn_key=(attempt,)))`。以下任一不满足即拒绝并尝试下一 attempt（原因逐条记录进 run metadata；100 次内无 attempt 通过则抛 `NetworkGenerationError`，异常对象携带完整拒绝记录）：

1. connected；
2. 至少一条跨区域 edge；
3. 不是完全图；
4. 所有 node 的 betweenness 不全相等（排除环形等完全对称结构）。

Betweenness 为 unweighted、exact（非抽样）normalised node betweenness（networkx）；排名 tie 定义为计算值**精确相等**，按 `tank_id` 升序打破（V110）。`tie_groups` 和 `tie_ids_at_rank(k)` 用同一规则，写入 metadata。网络 hash（regions + edges 的 SHA-256 前 16 位）写入 run metadata，用于 V010 追溯；seed 0 的 golden hash 由 `tests/test_network.py::test_golden_hash_literal` 锁定。

## 2. Selection criteria（在看表之前写下）

候选 (p_in, p_out) 需要同时满足：

| # | 标准 | 阈值 | 理由 |
|---|---|---|---|
| C1 | 10 个 seed 全部在 100 次内接受，且平均重试 ≤ 1 | 稳定性 | 避免 network-seed 列表里出现不可生成的 seed |
| C2 | modularity ≥ 0.45 | 模块性 | 研究动机是"少数桥连接原本分离的区域" |
| C3 | 跨区 edge 平均 5-10 条 | 桥数量 | 太少则 cross-group spread 极罕见，太多则接近均匀混合 |
| C4 | rank-1 betweenness ≥ 4 × 中位数，且 rank-2 无 tie | R002 | targeted 策略要有可辨识目标 |
| C5 | rank-1 tank 承载 ≥ 40% 的跨区 shortest paths | bridge 语义 | validation-plan §8："高 betweenness 应与跨 region shortest paths 有清楚结构关系" |

## 3. Grid audit，network seeds 0-9

列说明：`failed` = 100 次内无法接受的 seed 数；`mean/max_attempt` = 被接受的 attempt 序号（0 表示首次即接受，等于之前被拒次数）；`inter_edges` = 跨区 edge 数；`modularity` 按 4 个 region 划分计算；`bc_top1/top2/median` = betweenness 第 1、第 2 名和中位数的跨 seed 均值；`distinct_bc` = 不同 betweenness 值个数；`tie_at_k` = 第 k=2 名有精确并列的 seed 数；`top1_is_bridge` = 第 1 名 tank 拥有跨区 edge 的 seed 数；`top1_xpath / top2_xpath` = 跨区 node pair 的 shortest paths 中经过第 1 / 第 2 名 tank（作为中间节点）的平均比例。

Seeds 0..9, k = 2. tie_at_k / top1_is_bridge are counts out of 10 seeds; top1_xpath / top2_xpath = mean share of cross-region shortest paths passing through the rank-1 / rank-2 tank.

| p_in | p_out | failed | mean_attempt | max_attempt | mean_deg | inter_edges | density | clustering | modularity | diameter | bc_top1 | bc_top2 | bc_median | distinct_bc | tie_at_k | top1_is_bridge | top1_xpath | top2_xpath |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.030 | 0 | 2.800 | 6 | 2.740 | 6.200 | 0.144 | 0.218 | 0.515 | 7.700 | 0.475 | 0.406 | 0.092 | 14.500 | 0 | 10 | 0.576 | 0.495 |
| 0.500 | 0.050 | 0 | 1.100 | 4 | 2.990 | 9.500 | 0.157 | 0.234 | 0.420 | 6 | 0.373 | 0.287 | 0.075 | 16.200 | 0 | 10 | 0.440 | 0.333 |
| 0.500 | 0.080 | 0 | 0.400 | 2 | 3.310 | 12.500 | 0.174 | 0.254 | 0.363 | 5.300 | 0.275 | 0.238 | 0.074 | 17.500 | 0 | 10 | 0.324 | 0.280 |
| 0.500 | 0.100 | 0 | 0.400 | 2 | 3.680 | 16.200 | 0.194 | 0.265 | 0.302 | 4.900 | 0.263 | 0.205 | 0.059 | 18.100 | 0 | 10 | 0.308 | 0.237 |
| 0.600 | 0.030 | 0 | 1.900 | 6 | 3.000 | 6 | 0.158 | 0.295 | 0.539 | 6.700 | 0.426 | 0.361 | 0.071 | 15.900 | 0 | 10 | 0.532 | 0.441 |
| 0.600 | 0.050 | 0 | 0.400 | 1 | 3.300 | 8.800 | 0.174 | 0.303 | 0.476 | 6 | 0.360 | 0.272 | 0.068 | 16.700 | 0 | 10 | 0.440 | 0.330 |
| 0.600 | 0.080 | 0 | 0.100 | 1 | 3.640 | 11.800 | 0.192 | 0.317 | 0.419 | 5.200 | 0.233 | 0.199 | 0.073 | 17.800 | 0 | 10 | 0.284 | 0.239 |
| 0.600 | 0.100 | 0 | 0.100 | 1 | 4.010 | 15.500 | 0.211 | 0.298 | 0.358 | 4.700 | 0.220 | 0.177 | 0.060 | 18.800 | 0 | 10 | 0.265 | 0.208 |
| 0.700 | 0.030 | 0 | 1 | 3 | 3.340 | 5.700 | 0.176 | 0.446 | 0.571 | 6.700 | 0.407 | 0.358 | 0.054 | 15.100 | 1 | 10 | 0.512 | 0.450 |
| 0.700 | 0.050 | 0 | 0.300 | 1 | 3.610 | 8.300 | 0.190 | 0.425 | 0.515 | 5.600 | 0.351 | 0.278 | 0.060 | 17.100 | 0 | 10 | 0.438 | 0.345 |
| 0.700 | 0.080 | 0 | 0.100 | 1 | 3.990 | 11.800 | 0.210 | 0.406 | 0.449 | 4.700 | 0.239 | 0.203 | 0.060 | 17.800 | 0 | 10 | 0.297 | 0.247 |
| 0.700 | 0.100 | 0 | 0.100 | 1 | 4.360 | 15.500 | 0.229 | 0.376 | 0.390 | 4.200 | 0.215 | 0.178 | 0.048 | 18.600 | 0 | 10 | 0.264 | 0.218 |
| 0.800 | 0.030 | 0 | 1 | 3 | 3.750 | 5.700 | 0.197 | 0.575 | 0.593 | 6.200 | 0.412 | 0.356 | 0.040 | 14.500 | 0 | 10 | 0.518 | 0.449 |
| 0.800 | 0.050 | 0 | 0.300 | 1 | 3.960 | 8.300 | 0.208 | 0.501 | 0.537 | 5.400 | 0.343 | 0.273 | 0.051 | 16.900 | 0 | 10 | 0.430 | 0.342 |
| 0.800 | 0.080 | 0 | 0.100 | 1 | 4.360 | 11.800 | 0.229 | 0.476 | 0.477 | 4.400 | 0.239 | 0.189 | 0.053 | 18 | 0 | 10 | 0.299 | 0.234 |
| 0.800 | 0.100 | 0 | 0.100 | 1 | 4.730 | 15.500 | 0.249 | 0.436 | 0.420 | 3.900 | 0.199 | 0.165 | 0.043 | 18.700 | 0 | 10 | 0.247 | 0.203 |

## 4. Reading

- **接受率（C1）**：16 个组合 × 10 seeds 全部在 100 次内接受。`p_out = 0.03` 最多重试 6 次、平均 1-2.8 次；`p_out = 0.05` 在 `p_in = 0.5` 时最多重试 4 次、`p_in ≥ 0.6` 时最多 1 次；`p_out ≥ 0.08` 最多 2 次。满足 C1 的是 `p_out ≥ 0.05` 且 `p_in ≥ 0.6` 的组合，以及 `p_out ≥ 0.08` 的全部组合。
- **模块性（C2、C3）**：modularity 随 `p_out` 下降而上升，范围 0.30-0.59。`p_out = 0.10` 时 modularity 仍有 0.30-0.42（`p_in` 仍是 `p_out` 的 5-8 倍），只是相对更弱的模块化，并非均匀混合；但跨区 edge 约 15 条，不满足 C3。`p_out = 0.05` 时跨区 edge 8-10 条、modularity 0.42-0.54；`p_out = 0.03` 时 6 条、0.52-0.59。
- **Betweenness 非平凡（C4，R002）**：rank-1 与中位数之比在 3.7（0.6/0.10）到 10.3（0.8/0.03）之间；`p_out ≤ 0.05` 的组合全部 ≥ 4.8。rank-2 精确 tie 只在 (0.7, 0.03) 出现 1 次，160 个网络中其余都无 tie。
- **Bridge 语义（C5）**：10/10 seeds 中 rank-1 tank 都有跨区 edge，这是弱证据；更直接的 `top1_xpath` 显示 `p_out = 0.05` 时 rank-1 tank 承载约 43-44% 的跨区 shortest paths，`p_out = 0.03` 时 51-58%，`p_out ≥ 0.08` 时降到 25-32%。rank-2 tank 在 `p_out = 0.05` 时承载约 33-35%。
- **`p_in` 的作用**：主要影响 clustering（0.22 → 0.58）和缸内连通冗余，对桥结构影响小。

## 5. Candidate for D005（不是冻结值）

同时满足 C1-C5 的组合：**(0.6, 0.05)、(0.7, 0.05)、(0.8, 0.05)**。三者跨区结构几乎相同（inter_edges 8.3-8.8，top1_xpath 0.43-0.44，modularity 0.48-0.54），区别只在缸内 clustering（0.30 / 0.43 / 0.50）。

选 **`p_in = 0.6`，`p_out = 0.05`**：三者中缸内密度最低（每区 10 个 pair 平均 6 条 edge），区内不接近完全图，同时是 M1 config 现有默认值。这是一个偏好选择而非唯一解；若 M2 movement pilot 显示缸内路径冗余不足（例如 quarantine 后区内经常断开），可切换到 0.7/0.05。

备选：`(0.6, 0.03)` 桥更少、bridge effect 更突出，但 C1 不满足（最多重试 6 次）且 diameter 更大；`(0.6, 0.08)` 在 cross-group spread 过于罕见时可反向考虑，但 C3、C5 边缘。最终数值在 M2 movement pilot 后按 experiment-plan §7 第 4 问冻结，冻结前应把 network seeds 扩到 ≥ 30 个复核 C1；记入 `decision-log.md` 和 issue #5。

## 6. Reproduce

```bash
source .venv/bin/activate
python scripts/audit_network.py --seeds 10 --k 2
```
