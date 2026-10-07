# Network Structural Audit (issue #16, risk R002, D005 candidates)

Date: 2026-09-11 (wording revised and cross-path metrics added after the 2026-09-11 review). Generator: `turtlefarm/network.py`; script: `scripts/audit_network.py --seeds 10 --k 2`.

**This is a structural pilot, with no epidemic simulation, and is not hypothesis evidence.** It has only two purposes: confirm that the generator reliably produces connected, modular networks with non-trivial betweenness rankings under the candidate parameters (spec §3, §4; R002), and propose candidate values for D005. Values will be frozen after the 19-25 Sep pilot.

## 1. Accepted-structure rules (specifying spec §3.2 step 4)

Each attempt independently samples edges (within-region `p_in`, cross-region `p_out`) in a fixed pair order (lexicographic order of `itertools.combinations(range(20), 2)`) using `PCG64(SeedSequence(network_seed, spawn_key=(attempt,)))`. Failure to meet any of the following rules rejects the network and starts the next attempt. Each rejection reason is recorded in run metadata; if no attempt passes within 100 attempts, `NetworkGenerationError` is raised with the complete rejection record in the exception object:

1. Connected;
2. At least one cross-region edge;
3. Not a complete graph;
4. Node betweenness values are not all equal (excluding fully symmetric structures such as rings).

Betweenness is unweighted, exact (not sampled), normalised node betweenness (networkx). Ranking ties mean **exactly equal** calculated values and are broken by ascending `tank_id` (V110). `tie_groups` and `tie_ids_at_rank(k)` use the same rule and are recorded in metadata. The network hash (the first 16 characters of the SHA-256 of regions + edges) is recorded in run metadata for V010 traceability; the golden hash for seed 0 is locked by `tests/test_network.py::test_golden_hash_literal`.

## 2. Selection criteria (written before inspecting the table)

Candidate (p_in, p_out) pairs must satisfy all of the following:

| # | Criterion | Threshold | Rationale |
|---|---|---|---|
| C1 | All 10 seeds accepted within 100 attempts, with mean retries ≤ 1 | Stability | Avoid seeds in the network-seed list for which generation fails |
| C2 | modularity ≥ 0.45 | Modularity | The research motivation is "a few bridges connect otherwise separated regions" |
| C3 | Mean cross-region edge count of 5-10 | Bridge count | Too few makes cross-group spread extremely rare; too many approaches uniform mixing |
| C4 | rank-1 betweenness ≥ 4 × median, with no rank-2 tie | R002 | The targeted strategy needs identifiable targets |
| C5 | rank-1 tank carries ≥ 40% of cross-region shortest paths | Bridge interpretation | validation-plan §8: "high betweenness should have a clear structural relationship with cross-region shortest paths" |

## 3. Grid audit, network seeds 0-9

Column definitions: `failed` = number of seeds not accepted within 100 attempts; `mean/max_attempt` = index of the accepted attempt (0 means acceptance on the first attempt and equals the number of prior rejections); `inter_edges` = cross-region edge count; `modularity` is calculated using the partition into 4 regions; `bc_top1/top2/median` = means across seeds of rank-1, rank-2 and median betweenness; `distinct_bc` = number of distinct betweenness values; `tie_at_k` = number of seeds with an exact tie at rank k=2; `top1_is_bridge` = number of seeds where the rank-1 tank has a cross-region edge; `top1_xpath / top2_xpath` = mean share of shortest paths between cross-region node pairs that pass through the rank-1 / rank-2 tank as an intermediate node.

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

- **Acceptance rate (C1)**: all 16 combinations × 10 seeds were accepted within 100 attempts. At `p_out = 0.03`, retries reached 6, with means of 1-2.8. At `p_out = 0.05`, retries reached 4 for `p_in = 0.5` and at most 1 for `p_in ≥ 0.6`; at `p_out ≥ 0.08`, the maximum was 2. C1 is satisfied by combinations with `p_out ≥ 0.05` and `p_in ≥ 0.6`, and by all combinations with `p_out ≥ 0.08`.
- **Modularity (C2, C3)**: modularity rises as `p_out` falls, ranging from 0.30-0.59. At `p_out = 0.10`, modularity remains 0.30-0.42 (`p_in` is still 5-8 times `p_out`), indicating relatively weaker modularity, not uniform mixing; however, about 15 cross-region edges fails C3. At `p_out = 0.05`, there are 8-10 cross-region edges and modularity of 0.42-0.54; at `p_out = 0.03`, the values are 6 edges and 0.52-0.59.
- **Non-trivial betweenness (C4, R002)**: the rank-1-to-median ratio ranges from 3.7 (0.6/0.10) to 10.3 (0.8/0.03); all combinations with `p_out ≤ 0.05` have ratios ≥ 4.8. Only (0.7, 0.03) produces an exact rank-2 tie, once; no other network among the 160 has such a tie.
- **Bridge interpretation (C5)**: the rank-1 tank has a cross-region edge in 10/10 seeds, which is weak evidence. The more direct `top1_xpath` shows that the rank-1 tank carries about 43-44% of cross-region shortest paths at `p_out = 0.05`, 51-58% at `p_out = 0.03`, and 25-32% at `p_out ≥ 0.08`. The rank-2 tank carries about 33-35% at `p_out = 0.05`.
- **Effect of `p_in`**: mainly affects clustering (0.22 → 0.58) and within-region connectivity redundancy, with little effect on bridge structure.

## 5. Candidate for D005 (not a frozen value)

Combinations satisfying all of C1-C5: **(0.6, 0.05), (0.7, 0.05), (0.8, 0.05)**. Their cross-region structures are almost identical (inter_edges 8.3-8.8, top1_xpath 0.43-0.44, modularity 0.48-0.54). They differ in clustering (0.30 / 0.43 / 0.50) as within-region connectivity changes.

Select **`p_in = 0.6`, `p_out = 0.05`**: it has the lowest within-region density of the three (a mean of 6 edges among 10 pairs per region), does not approach a complete graph within each region, and is already the M1 config default. This is a preference, not a unique solution; if the M2 movement pilot shows insufficient within-region path redundancy (for example, regions frequently become disconnected after quarantine), 0.7/0.05 is an alternative.

Alternatives: `(0.6, 0.03)` has fewer bridges and a stronger bridge effect, but fails C1 (up to 6 retries) and has a larger diameter. Conversely, `(0.6, 0.08)` could be considered if cross-group spread is too rare, but is marginal on C3 and C5. Freeze the final values after the M2 movement pilot under experiment-plan §7 question 4; before freezing, expand to ≥ 30 network seeds to recheck C1, and record the decision in `decision-log.md` and issue #5.

Terminology clarification: within-region connectivity means links between tanks in the same region, not contacts between turtles inside one tank.

## 6. Reproduce

```bash
source .venv/bin/activate
python scripts/audit_network.py --seeds 10 --k 2
```
