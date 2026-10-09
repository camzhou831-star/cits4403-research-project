# Quarantine follow-up results

Recorded 9 October 2026. The separate follow-up completed all 19,000 planned runs, with no failures or censoring. At transfer rate 0.025, the broader random-policy sample gives some condition-specific advantages for highest-betweenness quarantine. Longer closures generally reduce the recorded outcomes, but they also cost more. These findings do not establish a universal ranking of response delays or strategies.

## Scope and checks

The [protocol](followup-protocol.md) and [configuration](../experiments/config/followup-duration-policy.json) were committed in `03fbb54` before the follow-up simulations. The original results were already known. Simulation records identify implementation commit `6832e6d`, before subsequent runner-lock and resume-guard hardening; that hardening did not change scientific rules or regenerate the batch. The original 5,200-run `formal-nested` dataset and report remain unchanged.

The follow-up reuses the original 20 networks and 100 nested network/epidemic blocks. It fixes `mu=0.025`, `beta=0.2`, `gamma=0.1`, capacity 12 and `k=2`, and crosses durations 7/14/28 with delays 1/12/33. Each network has 20 random-policy draws, reused across its epidemic replicates and conditions. This is a paired sensitivity study, not independent confirmation on new networks or epidemic seeds.

The [analysis record](../results/analysis/followup-duration-policy/analysis-summary.json) reports complete planned run keys, consistent pairing and protocol hashes, and agreement of all 400 replayed original conditions: 100 baselines plus 300 targeted `D=14` runs. Compared scientific fields agree within the recorded numeric tolerance of `1e-12`; execution identifiers and other metadata are excluded. Observer tests compare complete original run records and random-draw order with and without observation, including an arrival followed by same-day recovery.

Final validation on 9 October passed all 294 tests, including the runner guards. The notebook's 17 code cells ran top to bottom with no errors, recalculating all seven analysis tables and the replay comparison. A full-batch resume check skipped all 19,000 records, wrote none and reported no failures; the summary CSV checksum stayed identical.

All intervals below are pointwise 95% percentile intervals from 2,000 whole-network bootstrap resamples, seed `20261009`. The many contrasts are exploratory and correlated, without multiplicity adjustment. Random outcomes are averaged within each epidemic block before pairing. Blocks in which quarantine never activates remain included.

## Direct delay comparisons in the original experiment

[formal-delay-effects.csv](../results/analysis/followup-duration-policy/formal-delay-effects.csv) contains 36 comparisons: three non-zero transfer rates, two strategies, three delay pairs and two primary outcomes. Four intervals exclude zero, all for random quarantine at `mu=0.1`:

| Later minus earlier delay | Attack-rate difference, percentage points [95% CI] | Affected-tank difference [95% CI] |
|---|---|---|
| 33 minus 1 days | 1.19 [0.35, 2.18] | 0.243 [0.073, 0.443] |
| 33 minus 12 days | 1.37 [0.50, 2.53] | 0.297 [0.117, 0.530] |

The other 32 intervals include zero, including every targeted-quarantine contrast. This does not establish equivalence or prove that timing never matters. The original descriptive means should not be presented as a universal delay ordering.

## Broader random-policy coverage

The [coverage table](../results/analysis/followup-duration-policy/policy-coverage.csv) records 400 policy draws across 20 networks. There are 17 to 20 distinct pairs per network, totalling 377 distinct network/pair combinations and 23 repeated draws. Both selected tanks belong to the same region in 115 draws (28.75%). Every region is represented in each network's 20 draws, but coverage is not balanced or exhaustive. Duplicate pairs were retained.

The [stability table](../results/analysis/followup-duration-policy/policy-stability.csv) compares prefixes of 5, 10 and 20 draws. Across the nine conditions, moving from 5 to 20 draws changes a primary strategy estimate by at most 1.743 attack-rate percentage points or 0.349 tanks; moving from 10 to 20 changes it by at most 0.436 points or 0.099 tanks. With 20 draws, conditional policy Monte Carlo standard errors range from 0.261 to 0.564 percentage points and from 0.054 to 0.111 tanks. These checks describe sampling stability for the recorded networks and epidemics; they do not prove convergence or quantify all uncertainty.

## Strategy and duration comparisons at transfer rate 0.025

The table shows targeted minus random differences from [strategy-effects.csv](../results/analysis/followup-duration-policy/strategy-effects.csv). Negative values favour targeting. Both strategies use the same budget within each row.

| Duration D | Delay | Attack-rate difference, percentage points [95% CI] | Affected-tank difference [95% CI] |
|---|---|---|---|
| 7 | 1 | -0.73 [-4.63, 2.92] | -0.073 [-0.836, 0.695] |
| 7 | 12 | -1.57 [-4.69, 1.70] | -0.319 [-0.948, 0.349] |
| 7 | 33 | -3.36 [-5.85, -0.55] | -0.730 [-1.246, -0.148] |
| 14 | 1 | -3.07 [-7.01, 0.72] | -0.544 [-1.347, 0.238] |
| 14 | 12 | -1.39 [-5.01, 2.09] | -0.135 [-0.849, 0.570] |
| 14 | 33 | -3.82 [-6.19, -1.63] | -0.789 [-1.252, -0.343] |
| 28 | 1 | -5.59 [-11.40, 0.48] | -1.019 [-2.193, 0.195] |
| 28 | 12 | -6.12 [-10.32, -1.68] | -1.079 [-1.932, -0.183] |
| 28 | 33 | -4.64 [-7.48, -1.64] | -0.902 [-1.443, -0.335] |

Both primary intervals lie below zero in four of the nine cells. The other cells do not establish a strategy difference, despite negative mean estimates. The original finding of no consistent targeting advantage across the formal grid concerned `D=14` and its three policy seeds. These conditional follow-up differences use a broader random arm and additional durations; they do not overwrite that original result or justify a general claim that targeting always wins.

[duration-effects.csv](../results/analysis/followup-duration-policy/duration-effects.csv) directly pairs durations. At delay 1, increasing D from 7 to 28 changes attack rate by -10.68 percentage points [-17.80, -3.90] for targeting and -5.83 [-7.34, -4.18] for random selection. The corresponding affected-tank differences are -2.060 [-3.510, -0.680] and -1.114 [-1.413, -0.794]. However, D=28 commits 56 tank-days when activated, compared with 14 for D=7 and 28 for D=14. These are duration-and-cost comparisons, not evidence of greater efficiency at equal cost or a selected optimal duration.

The [follow-up delay contrasts](../results/analysis/followup-duration-policy/delay-effects.csv) also depend on duration. For random quarantine, delay 12 minus 1 has a negative attack-rate interval at D=7, while delay 33 minus 1 has a positive interval at D=28. All targeted primary delay intervals include zero. The results do not support a simple rule that every later response must worsen every outcome.

## What the event observations show

In the 100 no-intervention runs, 79 have an infectious arrival outside the initial region and 79 have a local S-to-I event there. Conditional mean first-event days are 21.72 and 21.89, respectively; the 21 non-events remain missing, not day zero. Baseline means are 6.01 infectious cross-region transfers, 2.65 regions visited by infectious agents, 2.62 regions with local transmission and 60.63 local infections outside the initial region. See [condition-summary.csv](../results/analysis/followup-duration-policy/condition-summary.csv).

For an illustrative intervention condition, targeted D=28 at delay 1 has 4.13 infectious cross-region transfers per run, 2.15 regions visited and 41.94 local infections outside the initial region. An infectious arrival occurs in 65 of its 100 runs. These event summaries describe different aspects of spread. They do not identify infectors or show that a change in one event count caused the change in final outbreak size. First-event means condition on an event occurring, so they should not be read as unconditional delays or compared without the event incidence.

## Reproduction and limits

Use the commands in [README.md](../README.md#quarantine-follow-up-9-october-2026) to reproduce the separate raw records, [per-run CSV](../results/summary/followup-duration-policy.csv) and analysis. The analysis record stores source hashes, source commits, bootstrap settings and acceptance checks. The original data are not pooled with the follow-up to claim a larger independent sample.

These synthetic results cover one disease regime, one capacity, one transfer rate for the duration follow-up and one network generator. Sensitivity to beta, gamma, capacity, different network structures and new disease mechanisms remains untested here. The additional comparisons narrow some conclusions under this design; they do not calibrate the model to a real turtle infection.
