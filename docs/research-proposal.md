# Research Proposal

## 1. System

This project studies a modular captive-turtle housing system. The system consists of 20 tanks, each represented as a node in a tank-transfer network, with 200 synthetic turtle agents distributed among them. The network has 4 regions of 5 tanks each. More transfer connections are permitted within regions than between them, so the few tanks connecting different regions may act as bridge tanks.

Each agent has a disease state of susceptible (`S`), infected (`I`) or recovered (`R`). Each tank has a management state of `open` or `quarantined`. Quarantine is a tank-level movement restriction: agents cannot enter or leave the tank during a specified period, but disease transmission within the tank continues.

All agents, networks and experimental data are synthetic. This project is **a stylised explanatory model**, not a digital twin of a real turtle farm, and it does not predict real turtle diseases.

## 2. Motivation

In a modular system, contact within a tank may spread infection locally, while a small number of cross-tank transfers may connect otherwise separated regions. A system-wide outbreak emerges from local transmission rules, the modular network structure and a few bridge connections. This fits the complex-systems perspective in which local interactions produce collective behaviour.

When resources are limited, both the number and the choice of quarantined tanks matter. With the same number of tanks, start time and duration, selecting high-betweenness tanks from the network known before intervention may be more effective than random selection.

## 3. Research gap and independent investigation

Implementing an SIR simulator is not itself the contribution of this project. The independent investigation consists of:

1. Combining agent-level SIR dynamics with a modular tank-transfer network;
2. Systematically varying transfer rate and response delay to study when a local outbreak spreads to multiple regions;
3. Comparing random and highest-betweenness tank quarantine under strictly equal intervention budgets;
4. Recording network-instance variance, epidemic stochastic variance and random-policy selection variance separately;
5. Checking whether conclusions are robust to a small number of parameters outside the main experiment and to update assumptions.

## 4. Primary research question

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

## 5. Secondary research question

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## 6. Hypotheses

**Canonical hypothesis**

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

For experimental testing, this is divided into:

- **H1:** Relative to zero or very low transfer, non-zero transfer is expected to increase final attack rate and the number of affected tanks by enabling cross-group spread.
- **H2:** For a fixed transfer rate and quarantine policy, longer response delay is expected to produce no smaller final attack rate and no fewer affected tanks on average.
- **H3:** Under an equal intervention budget and paired random conditions, highest-betweenness quarantine is expected to produce lower final attack rate and fewer affected tanks than random quarantine.

Strict monotonicity in H2 may be affected by randomness and the spread that has already occurred. Formal conclusions will be based on distributions and uncertainty, without requiring every run to be monotonic.

## 7. Proposed modelling approach

- Model type: discrete-time agent-based model with a static modular transfer network.
- Agent layer: each turtle has a unique ID, tank location, `S/I/R` state and state-entry time.
- Tank layer: each tank has a capacity, region, neighbouring tanks and `open/quarantined` state.
- Network layer: a fixed, undirected, unweighted simple graph; an edge permits a direct transfer but does not mean a transfer must occur on any particular day.
- Disease dynamics: complete mixing within a tank, with infection calculated from each susceptible agent's risk; infected agents recover with a fixed recovery probability.
- Movement dynamics: agent transfers between open tanks are constrained by transfer rate, adjacency and capacity.
- Intervention: no intervention, random tank quarantine and highest-betweenness tank quarantine.

See `model-specification.md` for the detailed specification.

## 8. Planned experiments

The main experiment varies only:

1. cross-tank transfer rate;
2. response delay;
3. intervention strategy.

Other parameters remain fixed in the main experiment. The preliminary design uses 4 transfer-rate levels, 3 response-delay levels and 3 strategies, with specific values determined by a pilot. At least 30-50 epidemic replicates per condition are recommended, across multiple network seeds. The three strategies use the same network instance and epidemic seed; random quarantine also uses a separate policy seed.

The primary metrics are final attack rate, number of affected tanks, peak infected population and time to extinction. Secondary metrics are limited to time to peak, intervention cost and relative reduction compared with random quarantine.

## 9. Expected contribution

The expected contribution is to explain the following in a clear, reproducible synthetic model, rather than provide real disease-management advice:

- How modular structure and a small number of cross-group transfers change outbreak scale;
- How response delay changes the window of opportunity for movement restrictions;
- Whether a high-betweenness strategy using only the network structure known before intervention outperforms a random strategy under an equal budget;
- Which results are relatively robust across random network instances and disease processes.

Until the model has been run, these remain questions to test, not established conclusions.

## 10. Scope

### In scope

- 20 tanks, 200 synthetic agents, 4 modular regions;
- SIR disease states;
- static permitted-transfer network and dynamic agent movements;
- tank-level movement quarantine;
- Three intervention strategies;
- paired stochastic experiments;
- qualitative network/time-series inspection and quantitative summaries;
- limited sensitivity analysis.

## 11. Out of scope

- Real turtle-disease prediction or parameter calibration;
- Use of real customer, farm, veterinary or transaction data;
- An agent-level `Q` disease state;
- Mortality, birth, ageing, breeding, treatment or vaccination;
- A Web interface, database, login system or real-time animation;
- Simultaneously sweeping many transmission, recovery and capacity parameters in the main experiment;
- Economic optimisation or real management-policy recommendations.

## 12. Limitations

- Complete mixing within a tank ignores fine-grained contact differences;
- The network and population are synthetic and do not support empirical extrapolation;
- Homogeneous susceptibility ignores differences in species, age and health;
- Static transfer routes ignore long-term structural changes;
- Response delay abstracts detection and administrative delays without a separate observation model;
- Quarantine is idealised as completely preventing cross-tank movement;
- Betweenness reflects only network structure and is not guaranteed to be optimal under all conditions.

## 13. Academic integrity boundary

The old `/Users/yuanqimaomao/Desktop/projects/turtle-farm` project provides only the domain inspiration of multiple tanks, agents, disease concerns and quarantine. Its customer data, business results, database records and report text will not be reused, nor will transmission conclusions that do not exist in that project.

This project's synthetic population, network generator, SIR rules, quarantine rules, experiment design, analysis and report text must be developed afresh. Course notebooks are used only to understand graphs, stochastic experiments and network metrics. CITS4403 Lab implementations and CITS4012, CITS1401 and CITS5501 assessed code will not be copied.

## 14. Requirements not yet published

As of 2026-09-02, local materials do not provide the complete formal report format, page count, final technical format, rubric or submission details. This repository must be updated when those requirements are published; this document does not speculate about them.
