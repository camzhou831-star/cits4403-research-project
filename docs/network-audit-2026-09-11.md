# Network Structural Audit（issue #16，risk R002，D005 candidates）

日期：2026-09-11。生成器：`turtlefarm/network.py`；脚本：`scripts/audit_network.py --seeds 10 --k 2`。

**这是 structural pilot，不涉及疫情模拟，不是假设证据。** 目的只有两个：确认生成器在候选参数下稳定产生 connected、modular、betweenness 排名非平凡的网络（spec §3、§4；R002），并为 D005 给出候选数值。数值在 19-25 Sep pilot 后冻结。

## 1. Accepted-structure rules（spec §3.2 step 4 的具体化）

每次 attempt 按固定 pair 顺序独立抽 edge（同区 `p_in`，跨区 `p_out`），generator 由 `SeedSequence(network_seed, spawn_key=(attempt,))` 派生。以下任一不满足即拒绝并尝试下一 attempt（原因逐条记录进 run metadata）：

1. connected；
2. 至少一条跨区域 edge；
3. 不是完全图；
4. 所有 node 的 betweenness 不全相等（排除环形等完全对称结构）。

`max_attempts = 100` 内无 attempt 通过则抛 `NetworkGenerationError`。Betweenness 为 unweighted normalised node betweenness（networkx），排名 tie 按 `tank_id` 升序（V110）。网络 hash（regions + edges 的 SHA-256 前 16 位）写入 run metadata，用于 V010 追溯。

## 2. Grid audit，network seeds 0-9

列说明：`failed` = 100 次内无法接受的 seed 数；`mean/max_attempt` = 被接受的 attempt 序号（0 表示首次即接受）；`inter_edges` = 跨区 edge 数；`modularity` 按 4 个 region 划分计算；`bc_top1/top2/median` = betweenness 第 1、第 2 名和中位数的跨 seed 均值；`distinct_bc` = 不同 betweenness 值个数；`tie_at_k` = 第 k=2 名有并列的 seed 数；`top1_is_bridge` = 第 1 名 tank 拥有跨区 edge 的 seed 数。

Seeds 0..9, k = 2. tie_at_k / top1_is_bridge are counts out of 10 seeds.

| p_in | p_out | failed | mean_attempt | max_attempt | mean_deg | inter_edges | density | clustering | modularity | diameter | bc_top1 | bc_top2 | bc_median | distinct_bc | tie_at_k | top1_is_bridge |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.030 | 0 | 2.800 | 6 | 2.740 | 6.200 | 0.144 | 0.218 | 0.515 | 7.700 | 0.475 | 0.406 | 0.092 | 14.400 | 0 | 10 |
| 0.500 | 0.050 | 0 | 1.100 | 4 | 2.990 | 9.500 | 0.157 | 0.234 | 0.420 | 6 | 0.373 | 0.287 | 0.075 | 16.200 | 0 | 10 |
| 0.500 | 0.080 | 0 | 0.400 | 2 | 3.310 | 12.500 | 0.174 | 0.254 | 0.363 | 5.300 | 0.275 | 0.238 | 0.074 | 17.400 | 0 | 10 |
| 0.500 | 0.100 | 0 | 0.400 | 2 | 3.680 | 16.200 | 0.194 | 0.265 | 0.302 | 4.900 | 0.263 | 0.205 | 0.059 | 18.100 | 0 | 10 |
| 0.600 | 0.030 | 0 | 1.900 | 6 | 3.000 | 6 | 0.158 | 0.295 | 0.539 | 6.700 | 0.426 | 0.361 | 0.071 | 15.900 | 0 | 10 |
| 0.600 | 0.050 | 0 | 0.400 | 1 | 3.300 | 8.800 | 0.174 | 0.303 | 0.476 | 6 | 0.360 | 0.272 | 0.068 | 16.700 | 0 | 10 |
| 0.600 | 0.080 | 0 | 0.100 | 1 | 3.640 | 11.800 | 0.192 | 0.317 | 0.419 | 5.200 | 0.233 | 0.199 | 0.073 | 17.700 | 0 | 10 |
| 0.600 | 0.100 | 0 | 0.100 | 1 | 4.010 | 15.500 | 0.211 | 0.298 | 0.358 | 4.700 | 0.220 | 0.177 | 0.060 | 18.700 | 0 | 10 |
| 0.700 | 0.030 | 0 | 1 | 3 | 3.340 | 5.700 | 0.176 | 0.446 | 0.571 | 6.700 | 0.407 | 0.358 | 0.054 | 15 | 1 | 10 |
| 0.700 | 0.050 | 0 | 0.300 | 1 | 3.610 | 8.300 | 0.190 | 0.425 | 0.515 | 5.600 | 0.351 | 0.278 | 0.060 | 17.100 | 0 | 10 |
| 0.700 | 0.080 | 0 | 0.100 | 1 | 3.990 | 11.800 | 0.210 | 0.406 | 0.449 | 4.700 | 0.239 | 0.203 | 0.060 | 17.700 | 0 | 10 |
| 0.700 | 0.100 | 0 | 0.100 | 1 | 4.360 | 15.500 | 0.229 | 0.376 | 0.390 | 4.200 | 0.215 | 0.178 | 0.048 | 18.600 | 0 | 10 |
| 0.800 | 0.030 | 0 | 1 | 3 | 3.750 | 5.700 | 0.197 | 0.575 | 0.593 | 6.200 | 0.412 | 0.356 | 0.040 | 14.500 | 0 | 10 |
| 0.800 | 0.050 | 0 | 0.300 | 1 | 3.960 | 8.300 | 0.208 | 0.501 | 0.537 | 5.400 | 0.343 | 0.273 | 0.051 | 16.900 | 0 | 10 |
| 0.800 | 0.080 | 0 | 0.100 | 1 | 4.360 | 11.800 | 0.229 | 0.476 | 0.477 | 4.400 | 0.239 | 0.189 | 0.053 | 18 | 0 | 10 |
| 0.800 | 0.100 | 0 | 0.100 | 1 | 4.730 | 15.500 | 0.249 | 0.436 | 0.420 | 3.900 | 0.199 | 0.165 | 0.043 | 18.600 | 0 | 10 |

## 3. Reading

- **接受率**：16 个组合 × 10 seeds 全部在 100 次内接受，`p_out ≥ 0.05` 时最多重试 1 次；`p_out = 0.03` 需要最多 6 次。生成器稳定。
- **模块性**：modularity 随 `p_out` 降低而升高（0.30 → 0.59）。`p_out ≤ 0.05` 时跨区 edge 约 6-9 条，属于"少数桥"结构；`p_out = 0.10` 时约 15 条，结构接近均匀混合，与研究动机不符。
- **Betweenness 非平凡（R002）**：所有组合第 1 名 betweenness 是中位数的 4-10 倍，第 2 名与第 1 名可区分，rank-2 tie 仅在 (0.7, 0.03) 出现 1 次。10/10 seeds 中第 1 名 tank 都拥有跨区 edge，说明高 betweenness 确实对应 bridge tank（validation-plan §8）。
- **`p_in` 的作用**：`p_in` 主要影响 clustering（0.22 → 0.58）和缸内连通冗余，对桥结构影响小。`p_in = 0.6` 时每区平均 6 条同区 edge（10 个 pair），区内既不稀疏到接近树也不接近完全图。

## 4. Candidate for D005（不是冻结值）

**`p_in = 0.6`，`p_out = 0.05`**：modularity ≈ 0.48，跨区 edge ≈ 9，mean degree ≈ 3.3，diameter ≈ 6，首次接受率 60%、最多重试 1 次，第 1 名 betweenness ≈ 0.36 对中位数 0.07。

备选：`(0.6, 0.03)` 桥更少、更能突出 bridge effect，但 diameter 更大、重试更多，movement pilot 时若 cross-group spread 过于罕见可以反向考虑 `(0.6, 0.08)`。最终数值在 M2 movement pilot 后按 experiment-plan §9 第 4 问冻结，记入 `decision-log.md` 和 issue #5。

## 5. Reproduce

```bash
source .venv/bin/activate
python scripts/audit_network.py --seeds 10 --k 2
```
