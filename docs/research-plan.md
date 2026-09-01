# Initial research plan

## Model scope

The first implementation should remain deliberately small:

- 20 tanks;
- 200 synthetic turtles;
- S, I, R, and Q states;
- daily discrete-time updates;
- within-tank transmission;
- probabilistic cross-tank transfers;
- probabilistic recovery;
- delayed quarantine after detection.

No real customer or farm data is required for the minimum viable model.

## Candidate update rules

At each simulated day:

1. Apply scheduled or probabilistic transfers between tanks.
2. Calculate new infections from infectious turtles in each tank.
3. Detect eligible infectious turtles and apply the configured quarantine delay.
4. Recover infectious turtles according to the recovery probability.
5. Record individual, tank-level, and farm-level metrics.

The exact update order is a modelling assumption. A later experiment may compare synchronous and asynchronous updates.

## Initial independent variables

- transfer probability;
- transmission probability;
- recovery probability;
- quarantine delay;
- tank capacity or occupancy;
- intervention strategy and intervention budget.

## Initial dependent variables

- final outbreak size;
- peak infected population;
- time to peak;
- number of affected tanks;
- outbreak duration;
- number of quarantined turtles;
- intervention cost or resource use.

## Baselines and interventions

- Structural baseline: static tanks with no cross-tank transfers.
- Intervention baseline: random quarantine under a fixed budget.
- Proposed intervention: quarantine based on bridge-tank or cross-tank connectivity.

## Minimum experiment matrix

- Four transfer rates.
- Three quarantine delays.
- Three intervention conditions: none, random, and bridge-based.
- At least 30 random seeds per condition.

The initial analysis should report distributions and confidence intervals, not only one representative run.

## Validation and tests

- Population count is conserved except where a model rule explicitly changes it.
- A turtle belongs to exactly one location at a time.
- Quarantined turtles do not participate in normal tank transmission.
- The same seed and configuration reproduce the same result.
- Zero transmission probability produces no secondary infections.
- With no cross-tank transfers, an outbreak cannot enter an initially uninfected disconnected tank.

## Main risks

- Disease parameters may not be empirically calibrated.
- The model must be described as explanatory rather than a real farm prediction.
- Too much interface or infrastructure work could distract from experiments.
- Results may depend on update order, so sensitivity to this assumption should be checked.

## Possible extensions

- Static versus dynamic contact networks.
- Synchronous versus asynchronous updates.
- Heterogeneous tank capacity.
- Degree-based, betweenness-based, and random interventions.
- Synthetic differences in susceptibility.
- Global sensitivity analysis.
