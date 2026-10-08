# Network structural follow-up (issue #5, D005, risk R002)

Date: 2026-10-08 (Australia/Perth).

The selected parameters, `p_in = 0.6` and `p_out = 0.05`, pass the promised 30-seed C1 stability check: all 30 networks generated within 100 attempts, with a mean of 0.2 prior rejections. The expanded sample also contains one exact rank-2 tie, so it **does not pass the original C4 no-tie clause**. At seed 12, tanks 7 and 13 tie for ranks 1 and 2 and are both selected when `k = 2`. There is no ambiguity between a selected tank and an excluded third tank, but the literal C4 result remains a failure.

This is a retrospective structural follow-up to [the 2026-09-11 audit](network-audit-2026-09-11.md), which called for at least 30 network seeds to recheck C1 before freezing. The check is recorded after the 2026-10-06 parameter freeze and formal experiment. It does not establish that the promised check was completed before freezing, change the historical 10-seed results, or provide epidemic hypothesis evidence.

## Provenance and command

The worktree was clean before this audit. The run used branch `docs/english-documentation` at base commit `c9aa3d49eeab63c36c3bd0b43bbe4c79230007ae`. The model and scripts at that commit are identical to `origin/main` at `2b2fbaf2f8210d7a8e550e054f8eae37db2c6f81`, as checked with `git diff --exit-code origin/main HEAD -- turtlefarm scripts`.

Both `scripts/audit_network.py` and `turtlefarm/network.py` were last changed in commit `ff1ad5bce149a83d46cd5e4122e36e407347f3bd` (2026-09-11). Their Git blob IDs are:

| File | Git blob |
|---|---|
| `scripts/audit_network.py` | `f440fbab0b4910b417d57bb9161b15162abae3a9` |
| `turtlefarm/network.py` | `9faf2c753b774797a1d623d52d011f8ae7a1eac7` |

Working directory: `/Users/junhe/IT/4403/cits4403-docs-cleanup`.

Exact command:

```bash
/Users/junhe/IT/4403/cits4403-notebook/.venv/bin/python -B scripts/audit_network.py --seeds 30 --k 2
```

The command exited successfully. The interpreter was Python 3.12.14 with NumPy 2.5.2 and NetworkX 3.6.1. The `-B` flag disables bytecode-file writes; the script imports the model from the working repository.

On another checkout, activate its documented environment and run `python -B scripts/audit_network.py --seeds 30 --k 2` from the repository root. The absolute interpreter path above records this run's environment; it is not a required directory layout.

The script uses network seeds **0-29 inclusive**, `k = 2`, 20 tanks in 4 regions of 5, and the original 16 candidate pairs: `p_in = 0.5 / 0.6 / 0.7 / 0.8`, each with `p_out = 0.03 / 0.05 / 0.08 / 0.10`. Seeds 0-9 overlap the earlier audit; seeds 10-29 extend it. These are structural audit seeds, not the formal experiment's network seeds 200-219.

## Criteria and measurement

The original numerical thresholds are retained:

| Criterion | Original threshold applied to this follow-up |
|---|---|
| C1 | All sampled seeds generate within 100 attempts; mean prior rejections ≤ 1. The sample expands from 10 to 30 seeds. |
| C2 | Modularity ≥ 0.45. |
| C3 | Mean cross-region edge count from 5 to 10. |
| C4 | Rank-1 betweenness ≥ 4 × median betweenness, with no exact rank-2 tie. |
| C5 | Rank-1 tank carries ≥ 40% of cross-region shortest paths. |

For C2-C5, the aggregate comparison follows the earlier audit's reading of its table: modularity and path share are means across accepted networks; the betweenness comparison is mean rank-1 betweenness against 4 times mean within-network median betweenness. The no-tie clause requires `tie_at_k = 0`. These aggregate comparisons do not assert that every individual network meets each numerical threshold.

`failed` counts seeds with no accepted network within 100 attempts. `mean_attempt` and `max_attempt` use the zero-based accepted-attempt index, which equals the number of earlier rejected attempts: 0 means acceptance on the first attempt, and 1 means acceptance on the second attempt.

`mean_deg`, `inter_edges`, `density`, `clustering`, `modularity` and `diameter` are means across accepted networks; modularity uses the fixed four-region partition. `bc_top1`, `bc_top2` and `bc_median` are the means of rank-1, rank-2 and within-network median betweenness. `distinct_bc` is the mean number of distinct betweenness values. `tie_at_k` counts seeds with an exact tie at rank 2, including a tie between ranks 1 and 2. `top1_is_bridge` counts seeds whose rank-1 tank has a cross-region edge.

For each network, `top1_xpath` and `top2_xpath` first average over cross-region node pairs, excluding pairs with the tested tank as an endpoint. Each pair contributes the fraction of its shortest paths that pass through the tank as an interior node. The reported values then average those shares across networks.

## Full 30-seed grid

The following table is the unchanged standard output of the audit script, rounded to three decimal places where the script prints floating-point values. Counts are out of 30 seeds. All 480 candidate/seed combinations generated successfully; this alone does not imply that every candidate passes C1-C5.

| p_in | p_out | failed | mean_attempt | max_attempt | mean_deg | inter_edges | density | clustering | modularity | diameter | bc_top1 | bc_top2 | bc_median | distinct_bc | tie_at_k | top1_is_bridge | top1_xpath | top2_xpath |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.030 | 0 | 2.700 | 10 | 2.693 | 5.633 | 0.142 | 0.257 | 0.532 | 8 | 0.497 | 0.411 | 0.085 | 13.767 | 2 | 30 | 0.603 | 0.502 |
| 0.500 | 0.050 | 0 | 0.600 | 4 | 2.973 | 8.367 | 0.156 | 0.265 | 0.460 | 6.633 | 0.399 | 0.333 | 0.072 | 15.667 | 1 | 30 | 0.481 | 0.395 |
| 0.500 | 0.080 | 0 | 0.233 | 2 | 3.347 | 12.100 | 0.176 | 0.258 | 0.381 | 5.400 | 0.295 | 0.236 | 0.069 | 17.533 | 2 | 30 | 0.350 | 0.274 |
| 0.500 | 0.100 | 0 | 0.233 | 2 | 3.660 | 15.233 | 0.193 | 0.259 | 0.326 | 4.767 | 0.250 | 0.195 | 0.062 | 18.233 | 0 | 30 | 0.293 | 0.226 |
| 0.600 | 0.030 | 0 | 1.267 | 6 | 2.977 | 5.200 | 0.157 | 0.370 | 0.568 | 7.467 | 0.462 | 0.389 | 0.066 | 14.867 | 1 | 30 | 0.572 | 0.479 |
| 0.600 | 0.050 | 0 | 0.200 | 1 | 3.273 | 7.867 | 0.172 | 0.356 | 0.503 | 6.200 | 0.387 | 0.310 | 0.064 | 16.267 | 1 | 30 | 0.475 | 0.377 |
| 0.600 | 0.080 | 0 | 0.067 | 1 | 3.640 | 11.467 | 0.192 | 0.335 | 0.429 | 5.033 | 0.272 | 0.220 | 0.063 | 17.767 | 1 | 30 | 0.330 | 0.264 |
| 0.600 | 0.100 | 0 | 0.067 | 1 | 3.977 | 14.833 | 0.209 | 0.319 | 0.372 | 4.533 | 0.233 | 0.184 | 0.055 | 18.633 | 0 | 30 | 0.281 | 0.220 |
| 0.700 | 0.030 | 0 | 0.733 | 5 | 3.340 | 5.100 | 0.176 | 0.490 | 0.591 | 6.933 | 0.444 | 0.384 | 0.052 | 14.033 | 2 | 30 | 0.556 | 0.478 |
| 0.700 | 0.050 | 0 | 0.167 | 1 | 3.610 | 7.700 | 0.190 | 0.456 | 0.531 | 5.733 | 0.369 | 0.307 | 0.054 | 16.233 | 0 | 30 | 0.460 | 0.382 |
| 0.700 | 0.080 | 0 | 0.067 | 1 | 3.977 | 11.467 | 0.209 | 0.404 | 0.456 | 4.767 | 0.268 | 0.212 | 0.055 | 17.900 | 0 | 30 | 0.330 | 0.261 |
| 0.700 | 0.100 | 0 | 0.033 | 1 | 4.290 | 14.767 | 0.226 | 0.372 | 0.400 | 4.233 | 0.224 | 0.181 | 0.049 | 18.800 | 0 | 30 | 0.273 | 0.223 |
| 0.800 | 0.030 | 0 | 0.500 | 3 | 3.713 | 5.100 | 0.195 | 0.616 | 0.609 | 6.367 | 0.448 | 0.374 | 0.037 | 13.100 | 1 | 30 | 0.563 | 0.470 |
| 0.800 | 0.050 | 0 | 0.133 | 1 | 3.957 | 7.700 | 0.208 | 0.548 | 0.552 | 5.467 | 0.361 | 0.302 | 0.047 | 15.967 | 0 | 30 | 0.453 | 0.379 |
| 0.800 | 0.080 | 0 | 0.033 | 1 | 4.340 | 11.500 | 0.228 | 0.487 | 0.482 | 4.433 | 0.258 | 0.206 | 0.050 | 17.800 | 0 | 30 | 0.321 | 0.256 |
| 0.800 | 0.100 | 0 | 0.033 | 1 | 4.667 | 14.767 | 0.246 | 0.447 | 0.431 | 4 | 0.206 | 0.168 | 0.047 | 18.800 | 0 | 30 | 0.255 | 0.208 |

## Selected parameters: 0.6 / 0.05

| Criterion | Observation | Result |
|---|---|---|
| C1 | 30/30 generated; mean prior rejections 0.200; maximum prior rejections 1, so at most 2 actual attempts | Pass |
| C2 | Mean modularity 0.5033778099 ≥ 0.45 | Pass on the aggregate comparison |
| C3 | Mean cross-region edge count 7.8666666667, within 5-10 | Pass |
| C4 | Mean rank-1 / mean median betweenness = 6.0717848797 ≥ 4, but 1/30 seeds has an exact rank-2 tie | Fail: no-tie clause |
| C5 | Mean rank-1 cross-region path share 0.4748678228 ≥ 0.40 | Pass on the aggregate comparison |

Of the 30 selected-parameter networks, 24 were accepted on the first attempt and 6 after one rejection. All 6 rejected attempts failed because the graph was not connected. No seed exhausted the 100-attempt limit.

The sole rank-2 tie occurs at **seed 12**, accepted attempt index 0, network hash `5c9bbf8078da0b56`. Tanks **7 and 13** have exactly equal normalised betweenness, `0.4093567251461988`. Ascending tank ID puts tank 7 first and tank 13 second. Both are selected by `top_k(2)`; the tie does not cross the selection boundary. Nevertheless, `ties_at_rank(2) = 2`, so the original no-rank-2-tie condition is not satisfied. This observation is reported without changing the tie definition or the threshold.

The aggregate values conceal variation across seeds. Selected-parameter modularity ranges from 0.4062 to 0.6072, with 5/30 networks below 0.45. Cross-region edge counts range from 4 to 13. Rank-1 path share ranges from 0.2671 to 0.7427, with 9/30 networks below 0.40. In 6/30 networks, rank-1 betweenness is less than 4 times that network's median. These are per-network diagnostics, not revised selection rules.

## Other candidates and limits

Across the grid, C1 fails for 0.5/0.03 and 0.6/0.03 because their mean prior-rejection counts are 2.700 and 1.267. All seeds still generate within the limit; the largest rejected-attempt count is 10 at 0.5/0.03, corresponding to acceptance on the eleventh attempt.

All candidates at `p_out = 0.03` or `0.05` meet the aggregate C2, C3 and C5 thresholds. All candidates at `p_out ≥ 0.08` fail C3 and C5. At those higher cross-region probabilities, C2 also fails except for 0.7/0.08 and 0.8/0.08. The full table reports the exact-tie counts for every candidate.

Under the unchanged aggregate criteria and strict no-tie clause, only **0.7/0.05 and 0.8/0.05** meet all C1-C5 in this 30-seed sample. The original selected parameters remain a C1 pass with a disclosed C4 exception. This audit does not select replacement parameters or reinterpret the completed experiment.

Thirty deterministic seeds provide a finite structural check, not a guarantee for unseen seeds. Candidate results use the same seed range and are not 16 independent samples. The metrics describe networks and shortest paths; they do not measure epidemic spread, quarantine effectiveness or sensitivity of the research conclusions.

No model, configuration or epidemic result file was changed by this audit. No epidemic simulation or epidemic rerun was performed. The observed limitation is also disclosed in the report. No personal sign-off is supplied or inferred, and this record does not resolve the pending Member B confirmation of D005 or other research decisions.
