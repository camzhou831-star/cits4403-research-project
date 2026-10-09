# Quarantine follow-up protocol

Issue: #52. Baseline: main commit `76fa981`. This protocol is recorded before the follow-up simulations. The original results have already been seen, so this is a planned follow-up, not a preregistration of the original study. The original formal data and report remain unchanged.

## Questions

1. How do outcomes differ between the recorded response delays when the same network, epidemic and policy choice are compared directly?
2. Does broader sampling of random tank pairs change the comparison with highest-betweenness quarantine?
3. How does quarantine duration change the strategy comparison and its dependence on response delay?

## Fixed design

`experiments/config/followup-duration-policy.json` fixes transfer rate at 0.025, beta at 0.2, gamma at 0.1, capacity at 12 and k at 2. It uses network seeds 200 through 219 and the same five nested epidemic seeds per network as formal-nested. For network position i in that ordered list, epidemic seeds are `20000 + 5*i + j`, j = 0,...,4. Reusing these outbreaks makes this a paired sensitivity study, not independent confirmation on new networks.

Durations are 7, 14 and 28 days; response delays are 1, 12 and 33 days. Each network uses 20 random policy draws, with policy seed `50000 + 20*i + s`, s = 0,...,19. The same draw is reused across epidemic replicates, durations and delays within that network. Seeds are fixed without inspecting epidemic outcomes. Different seeds can select the same pair. Pair duplication, same-region coverage and coverage by region will be reported, not corrected by replacing seeds.

Each network/epidemic block has one shared baseline plus 3 durations x 3 delays x (1 targeted + 20 random) runs. The planned total is 19,000 runs. Duration 14 targeted runs and baselines are replayed to check agreement with matching formal results. The simulator, network generator and random-number keys are unchanged.

Within each duration, random and targeted strategies have the same committed budget, 2 x D tank-days when activated. Comparing durations changes the budget. Such contrasts test duration and timing together, not a pure timing effect at equal cost. Quarantine may never activate if infection has already disappeared; these blocks remain in the primary comparisons.

## Outcomes and observation

Primary outcomes remain final attack rate and affected tanks. Observation of the existing movement and infection stages also records:

- `first_infectious_arrival`: first accepted transfer of an infectious agent from the initial region into another region, or any later arrival into a non-initial region if reached first through a different path. No such event is missing, not day zero.
- `first_local_secondary_infection`: first S-to-I transition outside the initial region. This measures a local infection event, not an identified infector or a second-generation transmission chain.
- `infectious_cross_region_transfers`: accepted transfers of infectious agents between different regions.
- `regions_visited_by_I`: distinct regions visited by infectious agents, including the initial region.
- `regions_with_local_transmission`: distinct regions with at least one S-to-I event, including the initial region when it has such an event.
- `local_infections_outside_initial_region`: number of S-to-I events outside the initial region.

Observation must not draw random numbers, change agent order or modify model state. Tests compare original RunRecord outputs with and without observation, including an infectious arrival followed by recovery on the same day. Event definitions have their own version in the saved data. The existing affected-tanks metric already counts infectious arrivals; event timing is additional information.

## Comparisons and uncertainty

The original formal CSV supplies direct delay contrasts at every non-zero transfer rate. The follow-up supplies strategy contrasts within each duration and delay, delay contrasts within each duration and strategy, and duration contrasts within each delay and strategy. Delay pairs are 12 minus 1, 33 minus 1 and 33 minus 12 days. Duration pairs are 14 minus 7, 28 minus 14 and 28 minus 7 days. All directions refer to outcome differences; a negative strategy contrast (targeted minus random) favours targeting.

Average random outcomes within each epidemic block before comparing with its targeted run. Pair before aggregating and retain all complete blocks. Do not compare significance in separate conditions as a substitute for a contrast. Missing arms, duplicate records, failed runs or inconsistent disease/capacity conditions must be reported and must not be silently pooled.

Use 2,000 percentile bootstrap resamples of complete networks with a fixed analysis seed. Policy draws remain paired across conditions. These intervals are pointwise, without multiplicity adjustment; the several contrasts are exploratory and correlated. The network intervals do not by themselves quantify every source of policy-sampling uncertainty. Prefixes of 5, 10 and 20 policy draws provide a descriptive stability check; conditional Monte Carlo error must respect reuse of each policy choice across epidemic replicates. No stopping rule based on a favourable strategy effect is used.

## Recording and acceptance

Save compact per-run results, complete configurations, selected tanks, network hashes, source commit, protocol hash, observation version, run status and error information separately from formal-nested. Preserve failed records and use the same cumulative failure guard on resume. Large daily trajectories need not be duplicated in the follow-up dataset; the pinned configurations reproduce them.

Before interpretation, check planned versus recorded run keys, 20 networks with five distinct epidemic seeds each, identical policy choices across paired conditions, failure/censoring counts, event-observation neutrality, and agreement of repeated original conditions. Reproduce analysis from saved inputs and execute the notebook top to bottom. Keep report files, report-generation scripts and original formal results unchanged. New disease mechanisms, network rewiring and cross-region movement restrictions are outside this follow-up.
