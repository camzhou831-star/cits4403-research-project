# Checkpoint 1 Prediction

This document is a rehearsal script based on the current project specification. Its purpose is to prepare the team for Checkpoint 1 and ensure that both members share a consistent understanding of the model, experimental design, and planned responses. Speaker A is Cam and Speaker B is Wenhao, although the roles may be exchanged if necessary.

The facilitator's dialogue is included only to anticipate possible questions and interruptions. It does not represent official guidance. The prepared introduction should take approximately four minutes, leaving about six minutes for discussion.

## Before the Meeting

Have the following resources ready:

- the GitHub repository homepage;
- [Checkpoint 1 Brief](checkpoint-1-brief.md);
- the GitHub Issues page;
- [Facilitator Questions](facilitator-questions.md).

Speaker A begins once both team members are ready.

---

## Three-Minute Priority Version

Use this version if the facilitator limits the meeting to approximately five minutes. It presents the essential project information in three minutes and raises the highest-priority question before open discussion.

### 0:00-0:40 — System and Research Focus

**Speaker A:**

> Our project is titled *Bridge Transfers and Quarantine in a Captive Turtle Farm*. It uses a fully synthetic system of 200 turtle agents in 20 tanks arranged as four network regions.
>
> Disease spreads through contact within a tank, while turtle movements across permitted links can connect otherwise separated regions. We study how these local processes generate system-level outbreak patterns.

### 0:40-1:15 — Canonical Research Questions

**Speaker A:**

> Our primary research question is: How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Speaker B:**

> Our secondary research question is: Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

### 1:15-1:55 — Model and Current Progress

**Speaker A:**

> We use a discrete-time stochastic agent-based model with susceptible, infected, and recovered turtle states. Each simulated day applies management, movement, transmission, recovery, synchronous state updates, output recording, and a stopping check in a fixed order.
>
> The baseline SIR model has been implemented in PR #19, and all smoke tests pass. The formal V-series validation suite is now in progress. We have not yet generated formal experimental results.

### 1:55-2:30 — Strategies and Experimental Design

**Speaker B:**

> We compare no intervention, random tank quarantine, and targeted quarantine of high-betweenness tanks. The main experiment varies transfer rate, response delay, and intervention strategy under paired random conditions and an equal quarantine budget.
>
> We will evaluate final attack rate, affected tanks, peak infection, and time to extinction across repeated stochastic runs.

### 2:30-3:00 — Priority Question

**Speaker B:**

> Our highest-priority question concerns response delay. Should it be measured from outbreak introduction at time zero or from the first detected infection? Our current minimum viable model measures it from time zero as a combined detection and management delay. Measuring it from first detection would require an additional observation mechanism.

**If time remains:**

> We would also appreciate confirmation that the equal-budget comparison between random and betweenness-based quarantine is an appropriate scope for the independent investigation.

---

## Full Discussion Version

## 0:00-0:30 — Opening

**Possible facilitator opening:**

> Welcome to your first project checkpoint. Could you briefly introduce your system, research question, modelling approach, and current progress?

**Speaker A:**

> Thank you. Our project is titled *Bridge Transfers and Quarantine in a Captive Turtle Farm*.
>
> We will first introduce the system and our research questions, then describe the model and experimental design, and finally summarise our current progress on GitHub.

---

## 0:30-1:30 — System and Motivation

**Speaker A:**

> Our study uses a fully synthetic system consisting of 200 turtle agents distributed across 20 tanks.
>
> The tanks are organised into four regions, with five tanks in each region. Connections are denser within regions, while only a small number of bridge links connect different regions.
>
> Disease transmission occurs through contact between turtles in the same tank. Turtles may also move between tanks connected by the transfer network.
>
> With a very low transfer rate, an outbreak may remain confined to one region. However, even a small number of movements across bridge links may allow the disease to spread through the entire system. This interaction between local transmission and network structure is the central motivation for our study.

### Possible Interruption: Are You Using Real Data?

**Facilitator:**

> Are you using empirical data from a turtle farm or a particular disease?

**Speaker A:**

> No. The turtle population, tank network, and epidemiological parameters are all synthetic.
>
> This is a stylised explanatory model rather than a predictive model of a particular farm or disease. A synthetic system allows us to control the network structure and compare intervention strategies under consistent conditions.

**Return to the presentation:**

> I will now outline our research questions.

---

## 1:30-2:30 — Research Questions and Emergence

**Speaker A:**

> Our primary research question is:
>
> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Speaker B:**

> Our secondary research question is:
>
> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?
>
> We hypothesise that a low but non-zero transfer rate may be sufficient for disease to move between regions, that a longer response delay will reduce the effectiveness of quarantine, and that targeting high-betweenness tanks may outperform random quarantine under the same intervention budget.

### Possible Interruption: Where Is the Emergent Behaviour?

**Facilitator:**

> What constitutes emergent behaviour in this model?

**Speaker B:**

> Each turtle follows only local rules governing movement, infection, and recovery. No rule directly specifies the size or geographical extent of the outbreak.
>
> System-level epidemic patterns emerge from the accumulation of local transmission events and occasional movements through bridge tanks. For example, a small change in the transfer rate may produce a disproportionate change from a locally contained outbreak to system-wide spread.

### Possible Interruption: Is the Scope Too Broad?

**Facilitator:**

> Do these research questions make the project too broad?

**Speaker B:**

> The questions are examined using the same model, parameter sets, and outcome measures. The primary question identifies when cross-tank transmission becomes important, while the secondary question examines whether information about network structure can be used to reduce that transmission.
>
> If this scope is considered too ambitious, we can retain transfer rate and response delay as the main investigation and present the intervention comparison as an extension.

**Return to the presentation:**

> We will now describe the model structure and update process.

---

## 2:30-4:00 — Model Structure and Daily Rules

**Speaker A:**

> We propose a discrete-time stochastic agent-based model in which one time step represents one day.
>
> Every turtle has a tank location and one epidemiological state: susceptible, infected, or recovered. Each tank also has a management state: open or quarantined.
>
> The permitted-transfer network remains fixed during a simulation run, while turtles may move and change epidemiological state over time. Within each tank, we assume homogeneous or complete mixing.
>
> Each simulated day follows a defined sequence. First, scheduled quarantine measures begin or end. Second, turtle movements are processed. Third, the model takes a snapshot of the population and calculates new infections. Fourth, it calculates recoveries. Infection and recovery updates are then applied simultaneously. Finally, the model records the daily outputs and evaluates the stopping condition.

### Possible Interruption: Why Is There No Q State?

**Facilitator:**

> Why do turtles have only S, I, and R states? Why is quarantine not represented by a Q state?

**Speaker A:**

> Quarantine is modelled as a tank-level management intervention rather than an epidemiological state of an individual turtle.
>
> A turtle therefore remains susceptible, infected, or recovered, while its current tank may be either open or quarantined. This distinction prevents disease status from being conflated with movement restrictions.

### Possible Interruption: Why Can Transmission Continue Within a Quarantined Tank?

**Facilitator:**

> Why can infection continue to spread within a quarantined tank?

**Speaker A:**

> In our model, quarantine blocks movement into and out of a tank but does not isolate turtles from one another within that tank.
>
> Consequently, transmission may continue among turtles already present. This definition allows us to isolate and study the effect of restricting movement between tanks.

### Possible Interruption: Can a Newly Infected Turtle Transmit on the Same Day?

**Facilitator:**

> Can a turtle that becomes infected during a time step infect another turtle in that same time step?

**Speaker A:**

> No. Infection and recovery events are calculated from a single daily snapshot, and all epidemiological state changes are applied simultaneously.
>
> A newly infected turtle can begin transmitting on the following day. This synchronous update rule prevents the arbitrary order in which agents are processed from affecting the outcome.

---

## 4:00-5:20 — Intervention Strategies

**Speaker B:**

> We compare three intervention strategies: no intervention, random tank quarantine, and targeted quarantine based on betweenness centrality.
>
> Betweenness centrality measures how frequently a node lies on shortest paths between other nodes. A tank with high betweenness may therefore act as an important bridge between regions. Temporarily quarantining such a tank may interrupt a major route for cross-region disease transmission.

### Possible Interruption: Are These Different Graph Types?

**Facilitator:**

> Are you comparing different network models, such as complete, Erdős-Rényi, Watts-Strogatz, or Barabási-Albert networks?

**Speaker B:**

> No. All intervention strategies are applied to the same modular transfer network.
>
> Under no intervention, all permitted routes remain available. Random quarantine temporarily removes movement through randomly selected tank nodes, while targeted quarantine temporarily removes movement through tanks with the highest betweenness centrality.
>
> The comparison concerns different intervention policies on a controlled network, not different classes of network topology.

### Possible Interruption: How Will You Ensure a Fair Comparison?

**Facilitator:**

> How will you ensure that the intervention comparison is fair?

**Speaker B:**

> Random and targeted quarantine will involve the same number of tanks, begin at the same time, and remain active for the same duration.
>
> Paired comparisons will also use the same network, epidemiological parameters, movement parameters, and epidemic seed. The principal difference will therefore be the method used to select quarantined tanks.
>
> We define intervention cost as the number of quarantined tanks multiplied by the quarantine duration.

---

## 5:20-6:40 — Experimental Design

**Speaker B:**

> The main experiment varies three factors: cross-tank transfer rate, intervention response delay, and intervention strategy.
>
> Other quantities, including transmission probability, recovery probability, population size, and network-generation settings, will remain fixed in the main experiment.
>
> We currently plan to evaluate four transfer-rate levels, three response-delay levels, and three intervention strategies. Exact parameter values will be finalised after small pilot experiments.
>
> Our primary outcome measures are final attack rate and the number of affected tanks. We will also record the peak number of infected turtles and the time to extinction.

### Possible Interruption: Why Are Repeated Runs Necessary?

**Facilitator:**

> Why not simulate each experimental condition only once?

**Speaker B:**

> The model contains stochastic network generation, movement, transmission, and recovery. A single run may therefore be unrepresentative because of random variation.
>
> Repeated runs allow us to estimate both the typical behaviour and the uncertainty associated with each condition. We will vary the network and epidemic seeds and record every seed to ensure reproducibility.

### Possible Interruption: How Many Replicates Will You Use?

**Facilitator:**

> How many times will you repeat each condition?

**Speaker B:**

> Our provisional plan is to conduct 30 to 50 epidemic replicates per main condition across several independently generated network instances.
>
> We will determine the final number after evaluating computational cost, the stability of summary statistics, and your feedback.

### Possible Interruption: When Does a Simulation Run End?

**Facilitator:**

> What is the stopping condition for an individual simulation run?

**Speaker B:**

> A run ends when no infected turtles remain. Some turtles may remain susceptible because they were never infected, so the model does not require the entire population to enter the recovered state.
>
> If infected turtles remain when the predefined maximum duration is reached, the run will be recorded as censored rather than incorrectly treated as extinct.

---

## 6:40-7:40 — Current Progress and GitHub

**Speaker B:**

> We have documented the system definition, research questions, hypotheses, model rules, assumptions, experimental design, validation strategy, and project timeline.
>
> We have established a shared GitHub repository containing Issues, milestones, and assigned responsibilities. Both team members have also reproduced the same Python 3.12 environment from the shared requirements file.
>
> The baseline SIR model has now been implemented in PR #19, and all 11 smoke tests pass locally. The formal V-series tests are being developed under Issue #13.
>
> Cross-tank movement, network generation, quarantine policies, and the experiment runner remain to be implemented. We have not yet generated formal experimental results.

### Possible Interruption: Do You Have a Prototype or Preliminary Results?

**Facilitator:**

> Have you produced a working prototype or any preliminary results?

**Speaker B:**

> We now have a working M1 baseline for within-tank SIR transmission and recovery. It implements the specified daily order, synchronous disease updates, stopping rules, run records, and deterministic random-number substreams.
>
> Its smoke tests pass, and the formal invariant and extreme-case tests are currently in progress. Movement and quarantine are not yet included, so we do not claim any experimental findings at this stage.

### Possible Interruption: How Is the Work Divided?

**Facilitator:**

> How have you divided the project work between the two team members?

**Speaker A:**

> I am leading model implementation and will present the model structure and daily update rules.

**Speaker B:**

> I am leading validation testing, the hand-traced example, the result schema, and the checkpoint materials. I will present the intervention strategies and experimental design.
>
> We will review each other's pull requests, and both team members will maintain a complete understanding of the model and final analysis.

---

## 7:40-9:20 — Questions for the Facilitator

**Speaker B:**

> Before proceeding to the next implementation stage, we would like to confirm three points.

### Question 1: Definition of Response Delay

> First, should response delay be measured from outbreak introduction at time zero or from the first detected infection?
>
> Our current minimum viable model measures it from time zero. Measuring from first detection would require an additional detection mechanism.

**If the facilitator accepts time zero:**

> Thank you. We will document this definition explicitly and describe it as a combined detection and management delay.

**If the facilitator requires first detection:**

> Understood. Would a fixed detection delay be sufficient, or should detection itself be modelled as a stochastic process?

### Question 2: Project Scope

> Second, is a synthetic explanatory system of this kind appropriate for the project?
>
> In particular, is an equal-budget comparison between random quarantine and betweenness-based quarantine sufficiently substantial for the independent investigation?

**Possible facilitator response:**

> Yes, provided that the research question remains focused. Your analysis should explain the model's behaviour rather than merely demonstrate that the simulation runs.

**Team response:**

> Understood. We will retain transfer rate, response delay, and intervention strategy as the principal experimental factors and use repeated simulations to support our conclusions.

**If the facilitator considers the scope too broad:**

> Would you recommend treating transfer rate and response delay as the main investigation and presenting the intervention comparison as an extension?

### Question 3: Assessment Requirements

> Finally, are the complete marking rubric, report format, page limit, and specific GitHub requirements currently available?

**If they are not yet available:**

> Thank you. We will proceed with the current plan and revise our documentation when the remaining requirements are released.

---

## 9:20-10:00 — Closing

**Possible facilitator closing:**

> The proposal appears reasonable. Please record the decisions made today and use them to guide the remaining implementation and final submission.

**Speaker A:**

> Thank you. We will record your feedback in the decision log and update the model and experiment documentation accordingly.

**Speaker B:**

> Our immediate next step is to implement the minimal SIR model and its validation tests, followed by movement and quarantine mechanisms. Thank you for your guidance.

---

## Additional Questions and Prepared Answers

### Why Are You Using an Agent-Based Model?

> Individual turtles differ in epidemiological state and tank location, and movement occurs at the level of individual agents.
>
> An agent-based model represents this heterogeneity directly and allows system-level outbreak patterns to emerge from local interactions and movement decisions.

### Why Do You Assume Complete Mixing Within Each Tank?

> We do not have detailed within-tank contact data, and our primary research focus is movement between tanks.
>
> The complete-mixing assumption provides a transparent within-tank transmission mechanism while keeping the analysis focused on the transfer network. We will state this assumption clearly as a limitation.

### Why Did You Choose 20 Tanks and 200 Turtles?

> This configuration provides four distinct network regions and a sufficient local population for within-tank transmission, while remaining computationally manageable for repeated simulation experiments.
>
> These values are synthetic design choices rather than estimates of a real farm. We may include sensitivity analysis if time permits.

### What If Targeted Quarantine Does Not Outperform Random Quarantine?

> That would still be an informative result rather than a failed experiment.
>
> We would examine whether alternative routes, response delay, transfer rate, or variation in network structure reduces the advantage of targeting high-betweenness tanks. The analysis would explain the conditions under which the two strategies become similar.

### How Will You Validate the Implementation?

> We will test population conservation, valid SIR states, tank-capacity constraints, quarantine restrictions, and exact reproducibility under fixed random seeds.
>
> We will also construct a small three-day scenario by hand and compare every expected event and state transition against the program's event log.

### What Is the Final Attack Rate?

> The final attack rate is the proportion of the population infected at any point during a simulation run, including the initially infected turtle.

### How Is This Model Related to Conway's Game of Life?

> Both systems demonstrate how system-level behaviour can arise from repeated local update rules.
>
> However, the Game of Life is a deterministic cellular automaton defined on a regular grid. Our model is a stochastic agent-based epidemic model operating on a modular tank-transfer network, with explicit movement and SIR state transitions.

### What Do the Three Random Seeds Control?

> The network seed controls generation of the tank-transfer network.
>
> The epidemic seed controls the initial infection and the stochastic movement, transmission, and recovery events.
>
> The policy seed is used only to select tanks under the random-quarantine strategy.

### What Happens to a Recovered Turtle?

> A recovered turtle remains recovered for the rest of the run. It can neither transmit the disease nor become infected again under the current SIR assumptions.
>
> It may still move between open tanks and continues to count towards tank capacity.

### Where Did the Project Topic Come From, and How Do You Maintain Academic Integrity?

> The general domain was inspired by an earlier turtle-farm project involving multiple tanks, animal movement, disease, and quarantine. However, that project is used only as broad domain inspiration.
>
> We have not reused its code, data, database records, business logic, results, or report text. The synthetic population, network generator, SIR rules, intervention design, experiments, analysis, and written material for this project are being developed independently.
>
> Course materials are used to understand concepts such as random graphs, network measures, stochastic simulation, and reproducibility. We do not copy assessed code or claim course examples as our own implementation.

### How Is Your Network Generator Related to the ER, WS, and BA Models Discussed in the Course?

> Our proposed network is a modular random graph. Edges are sampled independently, but within-region pairs use a higher probability than between-region pairs. This resembles a simple stochastic block model and extends the independent-edge idea used in an Erdős-Rényi graph.
>
> It is not a Watts-Strogatz network because it does not begin with a regular ring and rewire edges. It is not a Barabási-Albert network because it does not use preferential attachment or aim to produce a scale-free degree distribution.
>
> We selected a modular generator because the research question requires four known regions with dense internal connections and relatively rare bridge links. ER, WS, and BA remain useful conceptual references, but they are not the three intervention conditions in our experiment.

### Why Do You Target Betweenness Centrality Rather Than Degree Centrality?

> Degree centrality measures how many direct neighbours a tank has. A tank may have high degree because it has many connections within its own region, without being important for movement between regions.
>
> Betweenness centrality measures how often a tank lies on shortest paths between other tanks. It is therefore more closely aligned with our aim of identifying bridge tanks that may connect otherwise separated regions.
>
> Betweenness is calculated once from the pre-outbreak network and does not use future epidemic information. Degree-based targeting could be included later as a sensitivity comparison if time permits.

### How Many Simulation Runs Will Be Required, and Is the Plan Feasible?

> The provisional factorial design contains four transfer-rate levels, three response-delay levels, and three strategies, giving 36 experimental conditions.
>
> With 30 to 50 epidemic replicates per condition, the main design requires approximately 1,080 to 1,800 runs, distributed across several network seeds. The exact allocation will be finalised after pilot timing and stability checks.
>
> Each run contains only 200 agents and 20 tanks, so the model is expected to be computationally lightweight. We will benchmark the implementation, execute runs in batches, and reuse the no-intervention baseline across response-delay labels where appropriate because response delay has no effect when no intervention occurs.

---

## Useful Phrases During the Meeting

If a question was unclear:

> Could you please repeat or rephrase the question?

To confirm your interpretation:

> Am I correct in understanding that you recommend simplifying the model?

> Do you mean that response delay should be measured from the first detected infection?

If you need time to consider a question:

> Let me consider that for a moment.

If the team has not yet made a decision:

> We have not finalised that decision. We will record your recommendation and revise the specification accordingly.

If your teammate is better placed to answer:

> Cam, would you like to address that question?

To return to the prepared presentation:

> Thank you. I will continue with the model specification.

---

## After the Meeting

Complete the following actions on the same day:

1. Record the facilitator's confirmed guidance in the decision log and Issue #9.
2. Add each decision to the corresponding D001-D008 Issue.
3. Revise the model documentation if any definitions or assumptions change.
4. Complete the final sign-off for Issue #10 once both members understand and accept the updated specification.
5. Do not close a decision Issue unless the meeting produces an explicit resolution.
