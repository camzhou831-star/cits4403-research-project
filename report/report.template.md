# Bridge Transfers and Quarantine in a Captive Turtle Farm

*CITS4403 Research Project, 2026. Cam Zhou (24349432) and Wenhao Zhang (24364285).*

*Code, notebook and demonstration video: <https://github.com/camzhou831-star/cits4403-research-project> (walkthrough: `notebooks/project-walkthrough.ipynb`; animated example: `results/demo/demo-3min.mp4`).*

## 1. Introduction

Moving animals between housing units is a routine part of captive husbandry, and it is also a pathway for infection. In livestock systems, recorded animal movements have been linked to the spread of bovine tuberculosis [1], and the structure of the movement network shapes how pathogens spread [2]. A facility made of many tanks has the structure of a **metapopulation**: transmission is local within each unit, and units are connected by occasional transfers. In metapopulation models, an infection reaches a large share of subpopulations only when mobility exceeds an invasion threshold [3]. More generally, the structure of a contact network shapes how an epidemic spreads [4], and in networks with strong community structure the few links between communities strongly affect whether a local outbreak becomes a global one [5].

This structure raises a practical question for anyone who can restrict movement: if only a few tanks can be closed, does it matter *which* tanks they are? In heterogeneous networks, targeting nodes by their network position is far more effective than uniform random action [6], and network measures have been used to identify individuals at high risk of infection [7]. In networks with strong community structure, interventions aimed at individuals that bridge communities outperform those aimed at highly connected individuals [5]. Betweenness centrality [8], the fraction of shortest paths passing through a node, is a natural measure of such bridging that can be computed before an outbreak.

We study these ideas in a deliberately simple system: 200 synthetic turtles in 20 tanks, grouped into 4 regions of a modular transfer network. Our primary question is how the cross-tank transfer rate and the response delay affect the final outbreak size and the number of affected tanks. Our secondary question is whether, under the same intervention budget, quarantining the highest-betweenness tanks reduces spread more than quarantining randomly chosen tanks. Before the experiment we stated three hypotheses: (H1) a low but non-zero transfer rate lets a local outbreak spread between regions, raising both outcomes; (H2) a longer response delay does not lower either outcome; and (H3) under an equal budget, highest-betweenness quarantine lowers both outcomes more than random quarantine.

**Contribution.** Our contribution is a controlled computational experiment, not a new simulator. The studies above target individuals in contact networks; here the unit of control is a tank with finite capacity, so closing a tank both isolates its occupants and changes where other agents can move. We compare strategies under an identical budget in tank-days and with common random numbers [9], so every strategy in a comparison sees exactly the same outbreak until the quarantine starts, and any later difference is caused by the choice of tanks. Parameters were chosen by criteria written down before the pilot data were seen, and confidence intervals resample whole network instances rather than single runs. The model is a stylised explanation of mechanism, not a forecast for any real facility.

## 2. Model

We built a discrete-time stochastic agent-based model (ABM); one time step is one day, and all data are synthetic. Each of the 200 turtle agents has a disease state, susceptible (`S`), infectious (`I`) or recovered (`R`), and lives in exactly one of 20 tanks. A tank holds at most 12 agents and is either `open` or `quarantined`. At the start, every tank holds 10 agents and one agent, chosen uniformly at random, is infected. The spare capacity matters: a transfer can fail because every neighbouring tank is full, so movement is constrained in the same way as in a real facility.

Tanks are the nodes of a static, undirected **modular transfer network**, in which an edge means that agents may be moved directly between two tanks. The 20 tanks form 4 regions of 5 tanks. Each within-region pair is joined with probability `p_in` = {{p_in}} and each between-region pair with `p_out` = {{p_out}}, so regions are internally dense and joined by a few bridge edges (Figure 1). A generated network is accepted only if it is connected, has at least one between-region edge, is not complete, and does not give every node the same betweenness; otherwise it is redrawn deterministically from the same seed. These checks guarantee that the question "which tanks are bridges?" has an answer in every network. Network statistics are given in Appendix C.

![Figure 1]({{figdir}}/fig1-network.png)

*Figure 1. Transfer network for network seed {{fig1_network_seed}}. Colour marks the region and node area is proportional to betweenness centrality. Dark edges join different regions. The black rings mark the two tanks that highest-betweenness quarantine closes (tanks {{fig1_top_k}}).*

Each day runs the same steps in a fixed order. First, quarantine starts or ends. Second, each agent attempts a transfer with probability `transfer_rate`. Attempts are processed in a random order and each is checked at once against the current tank states: a transfer is blocked if the origin is quarantined or if no neighbouring tank is both open and below capacity; otherwise the agent moves to an eligible neighbour chosen uniformly at random. Disease state does not affect movement. Third, mixing within a tank is complete, and a susceptible agent in tank *j* becomes infected with probability 1 − (1 − `beta`)^*I_j*, where *I_j* is the number of infectious agents in the tank after movement. Fourth, each agent that was infectious at the start of the day recovers with probability `gamma` and stays immune. Infections and recoveries are applied together, so a newly infected agent neither transmits nor recovers on the day it is infected. A run stops on the first day with no infectious agents, or is recorded as censored at day 365.

We compare three strategies: no intervention; **random quarantine**, which closes *k* tanks chosen uniformly at random; and **highest-betweenness quarantine**, which closes the *k* tanks with the highest normalised betweenness [8] in the pre-outbreak network (computed with networkx, which implements Brandes' algorithm [11]). Neither selector can see the infection. Both close *k* = 2 tanks on the same response day for *D* = {{D}} days, so each costs {{budget}} tank-days, and the only difference between them is which tanks are chosen. A quarantined tank cannot send or receive transfers, but transmission and recovery inside it continue. The response delay is counted from the introduction of infection on day 0 and stands in for detection plus administrative response.

The disease parameters, the transfer-rate and delay levels and *D* were chosen in a two-stage pilot whose selection criteria were committed before the pilot ran; the pilot seeds were excluded from the formal experiment, and the pilot never compared the two quarantine strategies. The first stage chose `beta` = {{beta}} and `gamma` = {{gamma}} (a mean infectious period of {{mean_infectious_days}} days) and the transfer levels {{transfer_levels}}, which range from no movement to a saturating epidemic. The three delays, {{delay_levels}} days, represent an immediate response, the median day on which infection first reaches a second tank, and the median time to the epidemic peak. The second stage chose *D* = {{D}} days as the only candidate that is at least one infectious period long, short enough not to cover most of the epidemic, and long enough for quarantine to intercept transfers. Appendix B gives the full procedure, including two changes made after data were seen.

The model is checked by {{n_tests}} automated tests covering invariants (agent count, `S + I + R = 200`, one tank per agent, capacity), extreme cases such as `beta = 0` and `transfer_rate = 0`, and a three-tank scenario traced by hand by both team members. The invariants are also checked on every day of every run; no pilot or formal run failed (Appendix A).

## 3. Experimental design

The formal experiment crosses three factors: transfer rate ({{transfer_levels}}), response delay ({{delay_levels}} days) and strategy. We used {{n_networks}} network instances, each with {{epi_per_network}} epidemic seeds of its own. Each combination of network, epidemic seed and transfer rate forms one **paired block**, giving {{formal_blocks_per_rate}} blocks per transfer rate. A block contains {{runs_per_block}} runs: one no-intervention baseline, shared by all delays because the delay has no effect without an intervention, and, for each delay, one betweenness run and {{n_policy}} random runs with different policy seeds. This gives {{formal_runs}} runs in total.

Pairing relies on how randomness is generated. Each run has a network seed, an epidemic seed and, for random quarantine, a policy seed. Epidemic draws are *event-keyed*, an implementation of common random numbers [9]: the random number used for any (process, day, agent) event depends only on the epidemic seed and that key. Every strategy in a block therefore follows an identical trajectory until the quarantine starts.

The co-primary outcomes are the **final attack rate**, the share of the 200 agents ever infected, and the number of **affected tanks**, the tanks that ever held an infectious agent. For each block we take the difference *targeted − random*, averaging the random arm over its policy seeds; a negative value favours targeted quarantine. We report the mean difference and the relative reduction −mean(difference)/mean(random arm), with 95% confidence intervals from a percentile bootstrap that resamples whole network instances (2000 resamples), so that blocks sharing a network are not treated as independent. After seeing the formal results we added a descriptive comparison of each strategy with its block's own baseline, and a version of the targeted − random comparison restricted to blocks in which the quarantine started. A first formal run had crossed rather than nested the epidemic seeds; we reran it with the intended nested design and report the nested run (Appendix D). Every number in this report is rendered from the result files by `scripts/build_report.py`, and Appendix E lists the commands that regenerate them.

## 4. Results

All {{formal_runs}} formal runs completed (failed: {{formal_failed}}; censored: {{formal_censored}}). In {{not_started_d1}}, {{not_started_d12}} and {{not_started_d33}} of the non-zero-transfer blocks at delays of 1, 12 and 33 days, the outbreak died out before the quarantine started, and all strategies in those blocks are identical by construction.

### 4.1 Transfer rate drives the spread across regions

Without intervention, the transfer rate decides whether an outbreak stays in its first tank or spreads through the system (Table 1, Figure 2). With no movement, infection never leaves the initial tank: the mean attack rate is {{base_final_attack_rate_0}}, an average of {{base_infected_0}} of the 10 agents in that tank. The attack rate rises to {{base_final_attack_rate_0p01}} at a transfer rate of 0.01 ({{base_affected_tanks_0p01}} affected tanks) and to {{base_final_attack_rate_0p025}} at 0.025 ({{base_affected_tanks_0p025}} tanks); at 0.1 the outbreak saturates the system, with an attack rate of {{base_final_attack_rate_0p1}} and {{base_affected_tanks_0p1}} of the 20 tanks affected. Epidemics last longest at the intermediate rate (median time to extinction {{base_time_to_extinction_0p025_median}} days at 0.025 against {{base_time_to_extinction_0p1_median}} days at 0.1), because infection moves slowly from region to region there but reaches every region quickly at the highest rate.

*Table 1. No-intervention outcomes by transfer rate ({{formal_blocks_per_rate}} runs each; 95% CIs from a bootstrap that resamples whole networks).*

{{table:baseline}}

![Figure 2]({{figdir}}/fig2-attack-rate.png)

*Figure 2. Mean final attack rate (95% CI) by transfer rate and strategy, with one panel per response delay. The no-intervention baseline is the same in every panel. Affected tanks follow the same pattern (Appendix F, Figure F1).*

Individual runs show how the spread happens (Figure 3). At transfer rate {{fig7_rate}}, infection never left its initial region in {{local_share_0p025}} of the baseline runs. In the representative cross-region outbreak, infection first peaks in its home region and appears in two further regions only weeks later, and those regions carry the second part of the epidemic.

![Figure 3]({{figdir}}/fig7-representative-runs.png)

*Figure 3. Representative no-intervention runs at transfer rate {{fig7_rate}}: a local outbreak (network {{fig7_local_network}}, epidemic seed {{fig7_local_epidemic}}, attack rate {{fig7_local_ar}}) and a cross-region outbreak (network {{fig7_cross_region_network}}, epidemic seed {{fig7_cross_region_epidemic}}, attack rate {{fig7_cross_region_ar}}). Each is the run whose attack rate is closest to the median of its class (local: {{fig7_local_n}} runs; cross-region: {{fig7_cross_region_n}}), a rule fixed before any trajectory was viewed. Top: S/I/R counts. Bottom: infectious agents per region.*

### 4.2 Effect of quarantine and response delay

A budget of 2 tanks for {{D}} days reduces the attack rate only modestly, and the largest effects are at transfer rate 0.025 (Appendix F, Table F1). There, highest-betweenness quarantine cuts the attack rate by a similar amount at every delay ({{vsbase_betweenness_final_attack_rate_0p025_d1}}, {{vsbase_betweenness_final_attack_rate_0p025_d12}} and {{vsbase_betweenness_final_attack_rate_0p025_d33}} at delays of 1, 12 and 33 days), whereas random quarantine loses most of its effect as the delay grows ({{vsbase_random_final_attack_rate_0p025_d1}}, {{vsbase_random_final_attack_rate_0p025_d12}} and {{vsbase_random_final_attack_rate_0p025_d33}}). At 0.01 the reductions are at most a few per cent and mostly indistinguishable from zero, and at 0.1 they are about 2% or less because nearly every agent is infected anyway. The intervals are wide and overlap across delays, so the contrast between the strategies is a description, not a tested result.

### 4.3 Targeted versus random quarantine

Table 2 and Figure 4 give the paired targeted − random differences. Of the {{tvr_cells}} comparisons with non-zero transfer (3 transfer rates × 3 delays × 2 outcomes), {{tvr_cells_excluding_zero}} have a 95% CI that excludes 0, both at transfer rate 0.025 with a 33-day delay: the attack rate differs by {{tvr_final_attack_rate_0p025_d33}} {{tvr_final_attack_rate_0p025_d33_ci}}, a relative reduction of {{tvr_final_attack_rate_0p025_d33_rel}}, and the number of affected tanks by {{tvr_affected_tanks_0p025_d33}} {{tvr_affected_tanks_0p025_d33_ci}}. This is the condition in which random quarantine had lost most of its effect. Even here the advantage is not consistent from block to block: targeted quarantine gives a lower attack rate in {{tvr_final_attack_rate_0p025_d33_share}} of blocks, the same in {{tvr_final_attack_rate_0p025_d33_equal}} and a higher one in {{tvr_final_attack_rate_0p025_d33_worse}}. Restricting to the {{tvr_started_ar_0p025_d33_blocks}} blocks in which the quarantine started gives {{tvr_started_ar_0p025_d33}} {{tvr_started_ar_0p025_d33_ci}}. In all other conditions the intervals include 0; at 0.01 the point estimates slightly favour random quarantine.

*Table 2. Paired differences, targeted − random (negative favours targeted quarantine), with network-cluster bootstrap 95% CIs. The relative reduction is −mean(difference)/mean(random). † marks a CI that includes 0.*

{{table:targeted_vs_random}}

![Figure 4]({{figdir}}/fig4-paired-effects.png)

*Figure 4. Mean paired difference, targeted − random, with 95% cluster-bootstrap CIs.*

## 5. Discussion

**H1 is supported.** The no-intervention attack rate rises steeply with the transfer rate, and the steepest change falls between 0.01 and 0.025. Over this range, the share of outbreaks that reach a second region rises from {{cross_share_0p01}} to {{cross_share_0p025}} ({{cross_share_0p1}} at 0.1), so outbreaks switch from mostly staying in one region to mostly crossing regions. This is consistent with the mobility threshold for invading new subpopulations in metapopulation models [3], although we did not estimate the threshold itself.

**H2 is supported in direction, but the effect is small.** The mean attack rate does not fall as the delay grows, apart from one dip of under 0.01. At transfer rate 0.025 it rises under random quarantine from {{arm_random_final_attack_rate_0p025_d1}} to {{arm_random_final_attack_rate_0p025_d33}} but stays almost flat under targeted quarantine, from {{arm_betweenness_final_attack_rate_0p025_d1}} to {{arm_betweenness_final_attack_rate_0p025_d33}}. Because a 2-tank, {{D}}-day quarantine has a modest effect overall, there is little room for the delay to matter.

**H3 receives limited support.** Targeted quarantine has the lower point estimate in most conditions at transfer rates 0.025 and 0.1, but only one condition has intervals excluding 0, and even there targeted quarantine is worse in a third of the blocks. With 18 correlated comparisons, about one interval in twenty would exclude 0 by chance alone, so this result needs replication. The data do not support the general claim that targeted quarantine is better under this budget; they are consistent with the narrower pattern that, at an intermediate transfer rate, the effect of targeted quarantine did not decline with a later response while that of random quarantine did.

One explanation, which this experiment did not test, is that a randomly chosen tank is a useful barrier only if the infection has not yet reached or passed it, and as the outbreak grows more random choices are already infected or far from the remaining susceptible regions. A high-betweenness tank lies on many shortest paths between regions, so it stays relevant while any region remains uninfected; in the cross-region run of Figure 3, regions were invaded weeks apart, so a quarantine on day 33 could still block a later invasion. Testing this would require recording, for each quarantined tank, whether it was infected on the response day and how many between-region transfers it blocked; both can be derived from the existing raw records.

These conclusions are limited in several ways. The turtles, tanks, disease and network are synthetic and uncalibrated, so magnitudes should not be read as predictions. We studied one quarantine budget and one disease regime, and the planned sensitivity analyses on `beta`, `gamma` and capacity were not run. The response delay has no explicit detection model, and movement does not depend on disease state. With {{n_networks}} networks, the intervals are wide relative to the differences between strategies. An expanded 30-seed check of the network generator, done only after the formal experiment, found one exact tie for the second-highest betweenness, so the original no-tie acceptance criterion is not met (Appendix C). Finally, several choices were made after data were seen, including an added transfer level, a corrected pilot criterion for *D*, the nested-seed rerun and the comparison with baselines; each is flagged in the text, recorded in Appendix B and the decision log, and the original results are kept.

## 6. Conclusion

In a modular tank system, the transfer rate decides whether a local outbreak stays local: moving from a transfer rate of 0.01 to 0.025 multiplies the attack rate by {{ar_ratio_0p01_to_0p025}} and the number of affected tanks by {{tanks_ratio_0p01_to_0p025}}. A small quarantine budget of 2 tanks for {{D}} days reduces the attack rate by at most {{max_vsbase_reduction}}, and across all conditions we could not show that targeted quarantine beats random quarantine. Within this model, the transfer rate changes outcomes far more than the choice of quarantined tanks does under this budget. We did not test whether reducing cross-region transfers would be a better use of resources than quarantine, because the transfer rate was an experimental factor rather than an intervention with a cost; that comparison, and larger budgets, are natural next steps.

## References

[1] M. Gilbert, A. Mitchell, D. Bourn, J. Mawdsley, R. Clifton-Hadley and W. Wint, "Cattle movements and bovine tuberculosis in Great Britain," *Nature*, vol. 435, no. 7041, pp. 491–496, 2005. doi:10.1038/nature03548

[2] R. Kao, L. Danon, D. Green and I. Kiss, "Demographic structure and pathogen dynamics on the network of livestock movements in Great Britain," *Proceedings of the Royal Society B*, vol. 273, no. 1597, pp. 1999–2007, 2006. doi:10.1098/rspb.2006.3505

[3] V. Colizza and A. Vespignani, "Epidemic modeling in metapopulation systems with heterogeneous coupling pattern: Theory and simulations," *Journal of Theoretical Biology*, vol. 251, no. 3, pp. 450–467, 2008. doi:10.1016/j.jtbi.2007.11.028

[4] M. J. Keeling and K. T. Eames, "Networks and epidemic models," *Journal of the Royal Society Interface*, vol. 2, no. 4, pp. 295–307, 2005. doi:10.1098/rsif.2005.0051

[5] M. Salathé and J. H. Jones, "Dynamics and control of diseases in networks with community structure," *PLoS Computational Biology*, vol. 6, no. 4, e1000736, 2010. doi:10.1371/journal.pcbi.1000736

[6] R. Pastor-Satorras and A. Vespignani, "Immunization of complex networks," *Physical Review E*, vol. 65, no. 3, 036104, 2002. doi:10.1103/PhysRevE.65.036104

[7] R. M. Christley, G. L. Pinchbeck, R. G. Bowers, D. Clancy, N. P. French, R. Bennett and J. Turner, "Infection in social networks: Using network analysis to identify high-risk individuals," *American Journal of Epidemiology*, vol. 162, no. 10, pp. 1024–1031, 2005. doi:10.1093/aje/kwi308

[8] L. C. Freeman, "A set of measures of centrality based on betweenness," *Sociometry*, vol. 40, no. 1, pp. 35–41, 1977. doi:10.2307/3033543

[9] P. Glasserman and D. D. Yao, "Some guidelines and guarantees for common random numbers," *Management Science*, vol. 38, no. 6, pp. 884–908, 1992. doi:10.1287/mnsc.38.6.884

[10] M. E. J. Newman, "Modularity and community structure in networks," *Proceedings of the National Academy of Sciences*, vol. 103, no. 23, pp. 8577–8582, 2006. doi:10.1073/pnas.0601602103

[11] U. Brandes, "A faster algorithm for betweenness centrality," *Journal of Mathematical Sociology*, vol. 25, no. 2, pp. 163–177, 2001. doi:10.1080/0022250X.2001.9990249

## Appendix A. Verification

The test suite has {{n_tests}} automated tests. They cover the invariants (agent count, `S + I + R = 200`, one tank per agent, capacity, no reinfection, quarantine blocking both directions, and reproducibility under identical seeds); extreme cases such as `beta = 0`, `gamma = 1`, `transfer_rate = 0` and a full tank; the half-open quarantine interval and deterministic tie-breaking; and a 3-tank, 6-agent scenario traced by hand by both team members and matched against the model's event log. The invariants are also checked at runtime on every day of every run, and any violation ends the run as `failed`. No pilot or formal run failed.

## Appendix B. Parameter selection (pilot)

`beta`, `gamma`, the transfer-rate levels, the response-delay levels and *D* were chosen in a two-stage pilot. Its selection criteria were committed to the repository before the pilot ran, and the pilot seeds were excluded from the formal experiment. The pilot never compared random with targeted quarantine.

**Stage 1** used no-intervention runs only. It required, among other things, that with `transfer_rate = 0` the infection never leaves the first tank; that the higher transfer levels do not consist almost entirely of minor outbreaks; that the lowest level does not saturate; and that three non-zero levels differ by at least a factor of two in accepted transfers per day.

In the first round ({{pilot1_runs}} runs) none of the {{pilot1_candidates}} `(beta, gamma)` candidates met the last criterion. The grid's adjacent levels differ by a nominal factor of exactly 2, and capacity blocking pulled the realised ratio below 2. As the protocol requires, we kept the threshold and reran the whole stage ({{pilot2_runs}} runs) on an extended grid. The added level, 0.025, was chosen by one member after seeing the first round's transfer volumes; the protocol also requires both members to confirm a new grid, and this confirmation was still pending. {{pilot2_passed}} candidates then passed. The pre-registered selection rule picks the candidate whose median attack rate at the middle transfer level is closest to 0.5; it chose `beta` = {{beta}} and `gamma` = {{gamma}} (mean infectious period {{mean_infectious_days}} days), with transfer levels {{transfer_levels}}.

The three response delays are 1 (immediate), the median day on which infection first reaches a second tank, and the median time to peak. They were computed from {{pilot_nonminor_runs}} non-minor outbreaks and gave delays of {{delay_levels}} days. The pilot used a crossed seed design (10 epidemic seeds shared by 5 networks), so these quantities rest on only 10 independent outbreak origins.

**Stage 2** considered *D* = 7, 14 and 21 days, with three acceptance criteria: (Q1) at least one attempted transfer is intercepted by a quarantine rule in ≥ 90% of runs whose quarantine starts; (Q2) *D* ≤ 25% of the median time to extinction; and (Q3) *D* ≥ the mean infectious period.

Under the original definition, which counted every blocked transfer in every run, no candidate passed Q1: {{pilot_q1_all}} of runs had a blocked transfer. After inspecting the data we changed the denominator to runs whose quarantine started, giving {{pilot_q1_started}}. Review then showed that this counter cannot measure Q1 at all. It also counts transfers blocked because every neighbouring tank was full, and in the no-intervention baselines {{pilot_baseline_blocked}} of runs already had such a block.

We therefore added three counters that attribute each blocked attempt to the first blocking rule reached: a quarantined origin; an open origin with no eligible destination but at least one quarantined neighbour with space; or remaining capacity/no-neighbour blocking. The definitions, the Q1 rule on them, and what would follow from each outcome were committed before the counters were implemented or the pilot rerun. The counters draw no random numbers, and the rerun reproduced all 27 pre-existing summary columns other than the run identifier, code commit and configuration hash across {{pilot3_runs}} runs exactly.

With these counters, the share of started runs with at least one attempt attributed to a quarantine rule was {{pilot_q1_quarantine_range}} for *D* = {{pilot_d_candidates}} days, so all candidates meet the operational Q1 criterion. For comparison, {{pilot_capacity_started}} of the same runs at *D* = {{D}} also had an attempt attributed to capacity. *D* = {{D}} is the only candidate that also satisfies Q2 (*D* ≤ {{pilot_q2_limit}}) and Q3, and the unchanged selection rule picks it. This is the duration the formal experiment had already used. The margin is narrowest at the lowest transfer level ({{pilot_q1_lowest_rate}}), where {{pilot_q1_quarantine_lowest_rate}} of started runs had an attempt attributed to quarantine. The started-runs denominator remains a post-hoc choice.

The interpretation was clarified during the 7 October review without changing the counters or threshold: an attempted departure from a quarantined origin is counted even when all neighbours are full. Q1 measures interception by a rule, not whether removing quarantine would have made that particular attempt succeed, and not a causal reduction in infections. The Q1 check was measured only after the formal experiment had run, so a different result could not have changed the completed experiment.

Other post-hoc elements are the strategy-minus-baseline comparison and the rule for choosing representative runs. The second team member had not yet signed off the pilot protocol when the pilot ran, nor confirmed the extended transfer grid. All of these are recorded in `docs/decision-log.md`, and the original results are kept in the repository.

## Appendix C. Network statistics

Across the {{n_networks}} networks of the formal experiment:

| Property | Median | Range |
|---|---|---|
| Modularity of the region partition [10] | {{net_modularity_median}} | {{net_modularity_min}}–{{net_modularity_max}} |
| Between-region edges | {{net_n_inter_edges_median}} | {{net_n_inter_edges_min}}–{{net_n_inter_edges_max}} |
| Mean degree | {{net_mean_degree_median}} | {{net_mean_degree_min}}–{{net_mean_degree_max}} |
| Diameter | {{net_diameter_median}} | {{net_diameter_min}}–{{net_diameter_max}} |

{{net_resampled}} networks needed at least one redraw.

The promised expanded structural check (network seeds 0-29) was completed only after the formal experiment. The selected setting meets the generation-stability criterion but fails the original no-rank-2-tie clause: at one seed, the two highest-betweenness tanks tie and are both selected when *k* = 2, so there is no tie across the selected/excluded boundary. The audit retains the failed criterion and the existing parameters; it does not alter the runtime tie rule or demonstrate robustness of the epidemic conclusions. Details are in `docs/network-audit-2026-10-08.md`.

## Appendix D. Sensitivity to the seed design

A first formal run reused the same {{crossed_epidemic_seeds}} epidemic seeds in every network, so the networks were crossed with the seeds instead of having seeds nested within them. Because draws are event-keyed, this gave every network the same initial infected agent and the same random draws, so outcomes were strongly correlated across networks; for example, whether an outbreak died out early depended on the seed rather than the network. The intended design nests epidemic seeds within networks. We found the problem after viewing that run's results, reran with nested seeds, and report the nested run. In the crossed run, {{crossed_cells_excluding_zero}} of the {{tvr_cells}} targeted − random comparisons had a CI excluding 0, against {{tvr_cells_excluding_zero}} in the nested design: with only five shared outbreak origins, the crossed run overstated its precision.

The local/cross-region classification of outbreaks uses end-of-day snapshots, so an infectious agent that arrives in a tank and recovers on the same day is not seen. This happened in {{oc_hidden_runs}} of {{oc_baseline_runs}} baseline runs. The {{oc_hidden_local}} of them classed as local were rerun, and their affected tanks were all inside the initial region.

## Appendix E. Reproduction

All results can be regenerated from the repository:

```bash
python scripts/run_experiment.py experiments/config/formal-nested.json
python scripts/analyse_results.py formal-nested
python scripts/build_report.py
```

## Appendix F. Additional results

*Table F1. Relative reduction in mean final attack rate compared with the block's own no-intervention baseline (descriptive; added after the formal results). † marks a mean-difference CI that includes 0.*

{{table:vs_baseline}}

![Figure F1]({{figdir}}/fig3-affected-tanks.png)

*Figure F1. Mean number of affected tanks, laid out as in Figure 2.*
