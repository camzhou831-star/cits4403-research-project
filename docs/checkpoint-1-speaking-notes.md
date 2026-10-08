# Checkpoint 1 Speaking Notes

Historical speaking notes. References to decisions still awaiting the pilot describe Checkpoint 1, not current progress. The completed formal experiment uses `D=14`, `p_in=0.6` and `p_out=0.05`; the [decision log](decision-log.md) records the evidence, pending confirmations and retrospective network-audit limitation. The original script is retained below.

Approximate speaking time: 3-4 minutes. Leave the remaining meeting time for facilitator questions.

## Speaker A

Hi, our project is called **Bridge Transfers and Quarantine in a Captive Turtle Farm**.

We are studying a synthetic system with 200 turtle agents living in 20 tanks. The tanks are divided into four regions. Most transfer links are inside a region, but a few tanks connect different regions.

The main idea is that an outbreak may stay inside one tank group when movement is very low. However, even a small number of transfers may connect separate groups and allow the infection to spread much further.

Our primary research question is:

**How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?**

This is a stylised explanatory model. We are not trying to predict a real turtle disease, and all population and network data will be synthetic.

## Speaker B

Our secondary question is:

**Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?**

Each turtle will have one of three disease states: susceptible, infected, or recovered. Quarantine is not an individual disease state. It is a management state for a tank.

When a tank is quarantined, turtles cannot move into or out of it for a fixed number of days. Infection can still spread inside that tank.

We will compare three strategies: no intervention, random tank quarantine, and highest-betweenness tank quarantine. The random and targeted strategies will quarantine the same number of tanks, start on the same day, and last for the same time. They will also use the same network and epidemic seed.

## Speaker A

The main experiment will change only three factors: transfer rate, response delay, and intervention strategy. Other values, such as transmission probability and recovery probability, will stay fixed in the main experiment.

Our main outputs are final attack rate, number of affected tanks, peak infected population, and time to extinction. We will repeat each condition with multiple network and epidemic seeds instead of relying on one simulation.

## Speaker B

The independent part is the equal-cost comparison between random quarantine and quarantine based on network betweenness. The targeted strategy will only use the transfer network known before the outbreak. It will not use future infection or movement information.

At the moment, we have completed the research and model documents and set up the shared repository. We have not written the model or produced any results yet.

We would like your feedback on three points: whether this synthetic explanatory system is suitable, whether response delay should start from outbreak introduction or first detection, and whether the random versus betweenness comparison is enough for independent investigation.

Thank you. We are happy to explain any part of the model.
