This rehearsal follows the repository's current division of work: Speaker A is Cam, and Speaker B is you. Swap roles if the meeting assignments differ. The facilitator's lines are anticipated rehearsal prompts, not official quotations. The core presentation takes about 4 minutes, with about 6 minutes for the facilitator's questions and your questions.

## Before the meeting

Open these in advance:

- The GitHub repository home page;
- [Checkpoint 1 Brief](/Users/junhe/IT/4403/cits4403-research-project/docs/checkpoint-1-brief.md);
- The Issues page;
- [Facilitator Questions](/Users/junhe/IT/4403/cits4403-research-project/docs/facilitator-questions.md).

Once both members are seated, Speaker A opens.

------

## 0:00–0:30 Facilitator's opening

**Facilitator (anticipated):**

> Hi. This is your first project checkpoint. Could you briefly introduce your proposed system, research question, modelling approach, and current progress?

**Speaker A:**

> Hi, thank you. Our project is called “Bridge Transfers and Quarantine in a Captive Turtle Farm”. We will first explain the system and research questions, then the model and experiment design, and finally show our current GitHub progress.

------

## 0:30–1:30 System and motivation

**Speaker A:**

> We study a fully synthetic system containing 200 turtle agents and 20 tanks. The tanks are divided into four regions, with five tanks in each region. Most permitted transfer links are within a region, while only a small number of tanks connect different regions.

> Infection spreads through contact within the same tank. Turtles may also move between connected tanks. Our motivation is that a local outbreak may remain within one region when movement is low, but a small number of cross-region transfers may allow it to spread through the whole system.

### Possible facilitator interruption: Is this real turtle data?

**Facilitator (anticipated):**

> Are you using real turtle-farm or disease data?

**Speaker A:**

> No. The population, tank network and disease parameters are synthetic. This is a stylised explanatory model. We want to study the mechanism created by local transmission, network structure and movement, rather than make predictions about a real disease or farm.

Resume the presentation:

> The synthetic setting also lets us control the network and compare interventions fairly.

------

## 1:30–2:30 Research questions and emergence

**Speaker A:**

> Our primary research question is: How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Speaker B:**

> Our secondary research question is: Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

> Our hypothesis is that a low but non-zero transfer rate may allow infection to cross between regions. We also expect longer response delays to reduce the effectiveness of quarantine, and targeted bridge-tank quarantine may perform better than random quarantine under the same budget.

### Possible facilitator interruption: Where is the emergence?

**Facilitator (anticipated):**

> Where is the emergent behaviour in this model?

**Speaker B:**

> We only program local rules: infection within a tank, recovery, and movement between connected tanks. We do not directly program a farm-wide outbreak. If a system-wide outbreak appears, it emerges from many local interactions and occasional movements through bridge tanks.

### Possible facilitator question: Are two research questions too many?

**Facilitator (anticipated):**

> Are these two separate projects? Is the scope too broad?

**Speaker B:**

> They use the same model, experiment factors and outcome measures. The primary question identifies when cross-tank spread becomes important. The secondary question then tests whether network structure can be used to reduce that spread. If the scope becomes too large, we will keep the primary question as the main result and treat the intervention comparison as the independent extension.

------

## 2:30–4:00 Model structure and daily rules

**Speaker B:**

> We plan to use a discrete-time stochastic agent-based model. One time step represents one day. Each turtle has a location and one disease state: susceptible, infected or recovered. Each tank has a management state: open or quarantined.

> The permitted-transfer network is static during a simulation run, but individual turtle movements and disease states change over time. Infection uses complete mixing within each tank.

> Each simulated day has the following order: first, activate or release quarantine; second, process movement; third, take a snapshot and calculate infections; fourth, calculate recoveries; fifth, apply disease-state changes synchronously; and finally record outputs and check whether the outbreak has ended.

### Possible facilitator question: Why is there no Q state?

**Facilitator (anticipated):**

> Why do turtles only have S, I and R states? Where is the quarantine state?

**Speaker B:**

> Quarantine is defined at the tank level rather than the individual level. A turtle remains susceptible, infected or recovered while its tank may be open or quarantined. This separates disease status from management status.

### Possible facilitator question: Why can transmission continue inside a quarantined tank?

**Speaker B:**

> Quarantine blocks movement into and out of the selected tank, but turtles already inside the tank still interact. This lets us isolate the effect of restricting cross-tank movement.

### Possible facilitator question: Can newly infected turtles transmit on the same day?

**Speaker B:**

> No. Infection and recovery are calculated from a fixed daily snapshot and committed synchronously. A newly infected turtle starts transmitting from the following day. This avoids results depending on the order in which agents are processed.

------

## 4:00–5:20 Three intervention strategies

**Speaker B:**

> We compare three strategies: no intervention, random tank quarantine, and highest-betweenness tank quarantine.

> Betweenness measures how often a tank lies on shortest paths between other tanks. A tank can have a relatively small number of direct connections but still be important because it connects different regions.

> Quarantining such a tank may block an important route for cross-region movement.

### Possible facilitator question: Do the three strategies correspond to complete, ER and BA graphs?

**Facilitator (anticipated):**

> Are you comparing different network types, such as random or scale-free networks?

**Speaker B:**

> No. All three strategies use the same modular transfer network. No intervention leaves all existing routes available. Random quarantine temporarily disables randomly selected tank nodes. Targeted quarantine temporarily disables the nodes with the highest betweenness. We are comparing intervention methods on the same network rather than generating three different network types.

### Possible facilitator question: Is the comparison fair?

**Speaker B:**

> The random and targeted strategies use the same number of quarantined tanks, the same start day, the same duration, the same network, and the same epidemic seed. The main difference is the tank-selection method. We define intervention cost as the number of quarantined tanks multiplied by quarantine duration.

------

## 5:20–6:40 Experiment design

**Speaker A:**

> The main experiment changes three factors: cross-tank transfer rate, response delay, and intervention strategy. Transmission probability, recovery probability, population size and the network-generation procedure will remain fixed in the main experiment.

> We plan to use four preliminary transfer-rate levels, three response-delay levels and three strategies. The exact numerical values will be selected after pilot checks.

> The primary outputs are final attack rate, number of affected tanks, peak infected population, and time to extinction.

### Possible facilitator question: Why are repeated runs needed?

**Facilitator (anticipated):**

> Why not run each condition only once?

**Speaker A:**

> Infection, recovery, movement and network generation are stochastic. One run may be unusually mild or severe. We will therefore use multiple network and epidemic seeds and analyse distributions and uncertainty rather than relying on one trajectory.

### Possible facilitator question: How many replicates are planned?

**Speaker A:**

> Our preliminary target is at least 30 to 50 epidemic replicates per main condition across multiple network instances. We will confirm the final number after measuring runtime and receiving your feedback.

### Possible facilitator question: When does a run end?

**Speaker B:**

> A run ends when the infected population reaches zero. It does not require every turtle to become recovered. Some turtles may remain susceptible because they were never infected. If infection remains at the maximum simulation horizon, the run will be recorded as censored rather than treated as extinct.

------

## 6:40–7:40 Current progress and GitHub

**Speaker B:**

> At the moment, we have defined the system, research questions, hypotheses, model rules, assumptions, experiment plan, validation plan and project timeline.

> We have created a shared GitHub repository with issues, milestones and assigned responsibilities. We have also reproduced the Python 3.12 environment from the same requirements file on both machines.

> We have not yet implemented the simulation or produced experimental results. The next milestone is the minimal SIR baseline, followed by validation tests, movement, quarantine and the experiment runner.

### Possible facilitator question: Why is there no code yet?

**Facilitator (anticipated):**

> Do you have a prototype or any results yet?

**Speaker B:**

> Not yet. We used the initial stage to define the model precisely so that both members implement and test the same rules. The environment is now reproducible, and the baseline implementation is the next scheduled task. We have also prepared invariant and extreme-case tests before running formal experiments.

Deliver this calmly and directly; no apology is needed.

### Possible facilitator question: How is the work divided between the two members?

**Speaker A:**

> I am leading the baseline model and network implementation.

**Speaker B:**

> I am leading validation tests, the hand-traced scenario, result schema and checkpoint material. We will review each other’s pull requests, and both members are responsible for understanding the complete model and final results.

------

## 7:40–9:20 Questions for the facilitator

Do not ask all 20 questions. Prioritise three.

**Speaker B:**

> We would like to confirm three modelling decisions before implementation.

### Question 1: Are the topic and independent investigation appropriate?

> First, is this synthetic explanatory system appropriate for the project, and is the equal-budget comparison between random and betweenness-based quarantine sufficient as an independent investigation?

**Possible facilitator response:**

> Yes, but keep the research question focused and make sure you analyse the behaviour rather than only demonstrate the simulation.

Your response:

> Understood. We will keep transfer rate, response delay and intervention strategy as the main factors, and use repeated experiments to support the conclusions.

If the facilitator considers the scope too broad:

> In that case, would you recommend keeping transfer rate and response delay as the primary study and treating the intervention comparison as an extension?

### Question 2: When does response delay start?

> Second, should response delay be measured from outbreak introduction at time zero, or from the first observed infection? Our current MVP measures it from time zero because using first detection would require an additional observation model.

If the facilitator accepts measuring from `t=0`:

> Thank you. We will record that definition explicitly and describe it as a combined detection and administrative delay.

If the facilitator requires measuring from first detection:

> Understood. Would a simple fixed detection delay be sufficient, or do you expect a stochastic observation process?

### Question 3: Marking and submission requirements

> Finally, have the full marking rubric, report format, page limit and exact GitHub evidence requirements been released?

If the facilitator says the requirements have not been released:

> Thank you. We will continue with the current plan and revise the documentation when those requirements are available.

------

## 9:20–10:00 Closing

**Facilitator (anticipated):**

> That sounds reasonable. Please record the decisions from this meeting and show a working model at the next checkpoint.

**Speaker A:**

> Thank you. We will record today’s feedback in our decision log and update the relevant model and experiment documents.

**Speaker B:**

> We will then complete the minimal SIR baseline and its validation tests before adding movement and quarantine. Thank you for your feedback.

------

## Additional questions and answers

**Facilitator: Why use an agent-based model?**

> Individual turtles have locations, disease states and movement decisions. An agent-based model allows us to represent these individual differences and observe how their local interactions produce system-level outbreak patterns.

**Facilitator: Why use complete mixing?**

> We do not have spatial contact data within each tank, and our main question concerns movement between tanks. Complete mixing keeps the within-tank rule simple and explicit. We will report it as a limitation.

**Facilitator: Why choose 20 tanks and 200 turtles?**

> This gives us four visible network regions with enough agents for local transmission while remaining computationally manageable. The values are synthetic and can be checked in sensitivity analysis if necessary.

**Facilitator: What if bridge-tank quarantine does not outperform random quarantine?**

> That would still be a valid result. We would examine whether the network has redundant paths, whether transfer is too low, or whether the response occurs after cross-region spread has already happened.

**Facilitator: How will you validate the code?**

> We will test population conservation, valid states, capacity limits, quarantine boundaries, zero-transmission and zero-movement cases, same-seed reproduction, and a small scenario calculated manually and compared with the event log.

**Facilitator: What is final attack rate?**

> It is the proportion of turtles that were infected at any time during the run, including the initial infected turtle.

**Facilitator: How does the project relate to Game of Life?**

> Both systems use repeated local update rules to generate global behaviour. Game of Life is a deterministic cellular automaton on a grid, while our model is a stochastic agent-based model on a modular network with movement and SIR states.

After the meeting, complete #9 that day by recording the facilitator's actual answers. If the facilitator changes any definitions, update the specification and other documents, then have both members complete the final sign-off for #10.
