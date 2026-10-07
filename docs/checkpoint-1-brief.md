# Checkpoint 1 Brief

For the 5-10 minute facilitator meeting in Weeks 7-8. Aim for a 3-4 minute team presentation, leaving the remaining time for questions.

## Project title

**Bridge Transfers and Quarantine in a Captive Turtle Farm**

## Proposed system

We study a synthetic housing system with 200 turtle agents and 20 tanks arranged in four regions. Tanks are connected by a modular transfer network. Most transfer links are within a region, while a small number of tanks connect different regions. The model is a stylised explanatory model and does not predict a real turtle disease.

## Motivation

Within-tank contact can create local transmission. A small amount of movement between tanks may connect otherwise separated groups and turn a local outbreak into a system-wide outbreak. With limited quarantine resources, the position of quarantined tanks may matter as much as the number quarantined.

## Primary research question

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

## Secondary research question

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## Hypothesis

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

## Model structure

- 200 synthetic agents; 20 tanks; 4 regions of 5 tanks.
- Agent disease states: `S / I / R` only.
- Tank management states: `open / quarantined` only.
- Tank network: static, modular, undirected permitted-transfer graph.
- One time step: one day.
- Same-tank transmission uses complete mixing.
- Cross-tank movement follows network edges and capacity constraints.
- Quarantine blocks movement into and out of selected tanks, but internal transmission continues.

## Daily update rules

1. Activate or release quarantine at the start of the day.
2. Process cross-tank movements subject to network, quarantine and capacity.
3. Calculate within-tank infections from a fixed snapshot.
4. Calculate recoveries.
5. Apply SIR changes synchronously.
6. Record outputs and check extinction.

## Baseline and intervention strategies

1. `No intervention`
2. `Random tank quarantine`
3. `Highest-betweenness tank quarantine`

Random and targeted quarantine use the same number of tanks, start day, duration, network instance and epidemic seed. Their only main difference is how tanks are selected.

```text
intervention cost = quarantined tanks × quarantine duration
```

Targeted selection uses only betweenness computed from the pre-outbreak transfer network. It cannot use future infection or future movement information.

## Experiment design

### Independent variables

- cross-tank transfer rate: 4 preliminary levels;
- response delay: 3 preliminary levels;
- intervention strategy: 3 strategies.

Numeric levels will be selected after pilot checks, not invented in advance.

### Controlled variables

Population, tank number, capacity, initial infections, `beta`, `gamma`, network generation rule, quarantine count and duration.

### Main outputs

- final attack rate;
- number of affected tanks;
- peak infected population;
- time to extinction.

Also record time to peak, intervention cost and relative reduction vs random quarantine.

### Repetition and pairing

- multiple network seeds;
- multiple epidemic seeds per network;
- random-policy seeds for random tank choice;
- preliminary target: at least 30-50 replicates per condition;
- same network and epidemic seed across strategies.

## Independent investigation

- Combine modular network structure with agent-level SIR dynamics.
- Compare response timing and transfer intensity rather than only one simulation.
- Compare random and structural intervention under equal cost.
- Separate network, epidemic and random-policy variance.

## Academic integrity boundary

The previous `turtle-farm` project only provides domain inspiration. We will not use its customer data, business results or code as the research model. The synthetic data, model rules, experiments and analysis will be newly designed. Course lab and other assessed code will not be copied.

## Current completion

- Shared private GitHub repository exists.
- Research questions and hypothesis are defined.
- Model specification, assumptions, experiment plan, validation plan, collaboration plan, timeline and risks are documented.
- **No model code has been written and no experiment has been run.**
- **Prototype result to be added after the baseline model is implemented.**

## Next two weeks

1. Obtain facilitator feedback and freeze pending definitions.
2. Both members approve the model specification.
3. Implement and validate the smallest baseline SIR model.
4. Add modular network movement only after baseline invariants pass.
5. Prepare pilot configurations without generating formal results prematurely.

## Questions for facilitator

1. Is a synthetic explanatory turtle-farm model suitable?
2. Is tank-level movement quarantine sufficiently clear?
3. Should response delay be measured from outbreak introduction or first observed infection?
4. Is one primary question plus a closely related intervention question acceptable?
5. Is random vs betweenness quarantine sufficient independent investigation?
6. Should final attack rate or affected tanks be the headline outcome?
