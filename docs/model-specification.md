# Model Specification

This document is the normative model specification. D001-D003 and D006-D008 were frozen on 2026-09-11 (see `decision-log.md`). Items still marked `Candidate value, frozen after pilot` (D004 quarantine duration, D005 network parameters, `beta`, and `gamma`) follow the two-layer freeze rule in §18. Both members should be able to implement the same behaviour independently from this document.

## 1. Model type, purpose and time

- Type: discrete-time stochastic agent-based model.
- Network: static modular tank-transfer network.
- Purpose: explain how transfer rate, response delay and quarantine selection jointly change spread in a synthetic system.
- Framing: **a stylised explanatory model**, not a model for real-world prediction.
- One simulation step represents one day; the initial state is `t = 0`, and each daily update produces the state at `t + 1`.

## 2. Entities

### 2.1 Turtle agent

| Field | Meaning |
|---|---|
| `agent_id` | Unique ID within a run |
| `tank_id` | The single tank currently occupied by the agent |
| `disease_state` | `S`, `I` or `R` |
| `state_entered_day` | Day on which the agent entered its current disease state |
| `ever_infected` | Whether the agent has ever entered `I`, used for final attack rate |

The MVP has no individual `Q` state. S, I and R agents may all move unless quarantine at the origin or destination tank blocks movement.

### 2.2 Tank

| Field | Meaning |
|---|---|
| `tank_id` | Unique ID from 0-19 |
| `region_id` | 0-3, with 5 tanks per region |
| `capacity` | Maximum number of agents |
| `management_state` | `open` or `quarantined` |
| `quarantine_start_day` | Empty when not quarantined |
| `quarantine_end_day` | Empty when not quarantined; uses the half-open interval `[start, end)` |

Transmission and recovery continue inside a quarantined tank; only transfers into and out of the tank are prohibited.

## 3. Transfer network

### 3.1 Graph definition

- 20 tank nodes divided into 4 modules of 5 nodes each.
- The network is an undirected, unweighted, simple graph.
- An edge means direct transfers between two tanks are permitted.
- The network is fixed within a run; agent movement occurs over time.
- Within-region edge probability `p_in` exceeds cross-region probability `p_out`.
- The generated network must be connected and contain cross-region edges.
- Complete graphs, fully uniform random mixing and artificially identical, symmetric copies of modules are prohibited.

### 3.2 Generation procedure

1. Create 4 regions using fixed tank IDs.
2. Generate edges independently with probability `p_in` for node pairs in the same region.
3. Generate edges independently with the lower probability `p_out` for node pairs in different regions.
4. If the network is disconnected, has no cross-region edge or fails a predefined structural check, deterministically generate the next attempt from the same network seed and record the attempt index. The predefined structural checks (specified on 2026-09-11 in `turtlefarm/network.py`) are: (a) connected; (b) at least one cross-region edge; (c) not a complete graph; (d) node betweenness values are not all equal. Deterministic convention (frozen on 2026-09-11): each attempt uses `PCG64(SeedSequence(network_seed, spawn_key=(attempt,)))`, drawing one uniform value for each of the 190 node pairs in the lexicographic order of `itertools.combinations(range(20), 2)`. Every rejection reason is recorded. If no attempt passes within 100 attempts, the run is marked `failed` and all rejection reasons are retained.
5. Save the adjacency list, region assignment, network seed, attempt index, network hash, mean degree, density, clustering coefficient, modularity, diameter and node betweenness.

`p_in`, `p_out` and structural acceptance thresholds: **Candidate value, frozen after structural pilot (D005, issue #5)**. The generation algorithm and acceptance rules (steps 1-5 in this section) are frozen; only their numerical values remain pending. The working proposal is to use the pilot to select parameters that reliably generate connected modular graphs without fixing a single bridge tank too rigidly. The structural audit (`docs/network-audit-2026-09-11.md`) proposes `p_in = 0.6` and `p_out = 0.05`. Manually specifying bridge edges is interpretable but gives low network-instance variance; a pure stochastic block model has more natural variance but may need rejection criteria.

## 4. Betweenness centrality

- Use the complete transfer network generated and saved before the outbreak.
- The MVP uses unweighted normalized node betweenness centrality.
- For node `v`, calculate the proportion of shortest paths between all other source-target pairs that pass through `v`.
- Calculate centrality once before the outbreak; do not update it during a run.
- Ranking ties mean **exactly equal** calculated normalised betweenness values (no tolerance). Prefer the smaller `tank_id` to ensure deterministic selection, and record the sets of tied tanks in run metadata.
- The network object is immutable after generation (tuple / read-only mapping). The selector may read only the network, `k` and policy seed; it must not receive simulation state.
- Future infection, future movements, future affected tanks and outcomes must not be used to select targeted tanks.

Weighted or dynamic betweenness is outside the MVP.

## 5. Disease states

| State | Definition | Allowed transition |
|---|---|---|
| `S` | Never infected and susceptible to infection | `S -> I` |
| `I` | Currently infectious | `I -> R` |
| `R` | Recovered and immune for the remainder of the run | None |

- There is no `I -> S` or `R -> S/I` transition.
- Newly infected agents enter `I` at the end of the day and begin transmitting and participating in recovery draws the following day.

## 6. Initialisation

### 6.1 Population and initial infection

- 200 agents, initially 10 per tank.
- Initial state: 199 `S`, 1 `I`, 0 `R`.
- Use the epidemic seed to select the initial infected agent uniformly from the 200 agents.
- All three strategies use the same initial agent and location within a paired block.
- The initial location is not selected using centrality or future results; it is recorded only as a diagnostic variable.

### 6.2 Capacity

All tanks use the same fixed capacity in the main experiment. Exact value: **capacity = 12, Frozen 2026-09-11 (D002; the team adopted the working proposal after Checkpoint 1; see `decision-log.md`)**.

- Rationale: with initial occupancy = 10, there is limited room for movement.
- Higher capacity reduces blocked transfers; heterogeneous capacity introduces confounding and is suitable only for sensitivity analysis.

## 7. Within-tank transmission

After the movement stage, calculate the current infectious count `I_j(t)` in tank `j`. For each susceptible agent in that tank:

```text
P(S -> I) = 1 - (1 - beta) ^ I_j(t)
```

Each infectious agent contributes an independent daily opportunity to infect a susceptible agent, implementing complete mixing within each tank.

- `beta` is fixed in the main experiment.
- Infection probability is 0 when `I_j(t) = 0`.
- Draws for susceptible agents are independent.
- Newly infected agents do not infect other agents on the same day.
- The pilot selects the baseline value of `beta` so that no-intervention outbreaks do not always die out immediately or always infect everyone; values must not be selected to support the hypothesis.

## 8. Recovery

- Each agent already in `I` before the day's transmission stage changes to `R` with fixed daily probability `gamma`.
- Recovery is sampled after transmission is calculated, so an agent can still transmit on the day it recovers.
- Newly infected agents do not participate in recovery draws on the same day.
- `gamma` is fixed in the main experiment; its value is determined by the pilot and recorded.

## 9. Cross-tank movement

### 9.1 Transfer-rate definition

The `cross-tank transfer rate` is the probability `mu` that each agent attempts one cross-tank movement per day.

### 9.2 Eligibility and update

An agent can complete a movement only if its origin tank is `open` and at least one neighbouring tank is `open` with spare capacity.

- At the start of each day, every agent receives an event-keyed movement draw. Ascending draw order (ascending `agent_id` for exact ties) defines the randomized asynchronous processing order.
- An attempt is recorded when that same movement draw is less than `mu`; each agent makes at most one attempt per day.
- When processing an attempt, immediately check the origin and neighbouring tanks' management states and capacities. Record the attempt as blocked if the origin is quarantined or no destination is eligible.
- Sort eligible neighbouring tanks by ascending `tank_id` and use the agent's `movement_destination` draw for that day to select a destination uniformly.
- On acceptance, immediately update the location and both tanks' occupancies.
- If no destination is eligible, the agent stays in its original tank and a blocked/no-destination event is recorded.
- Disease state does not affect movement probability; this is an explicit model simplification.

## 10. Capacity constraint

- At all times, `occupancy(tank) <= capacity(tank)`.
- Movement checks the current occupancy immediately.
- Temporarily exceeding capacity and correcting it afterwards is prohibited.
- Initialisation must respect capacity.

## 11. Response delay and quarantine trigger

The MVP does not model a detection process. Working definition:

```text
response delay d = intervention activation day measured from outbreak introduction at t = 0
```

- `d = 0`: activate before the first movement stage.
- `d > 0`: activate before the movement stage on day `d`.
- The intervention triggers only once.

In the implementation, day `0` is the initial snapshot with no movement; the first movement stage is recorded as day `1`. The recorded value is therefore `intervention_start_day = max(1, d)`; both `d = 0` and `d = 1` activate before the first movement stage. Main-experiment delay levels should not include both of these semantically duplicate values.

**Delay origin: measured from outbreak introduction (`t = 0`), Frozen 2026-09-11 (D001; the team adopted the working proposal after Checkpoint 1; see `decision-log.md`).** The alternative, first observed infection, requires an observation model or an additional detection assumption and would expand the scope. This project interprets delay as a combined abstraction of detection and administrative response.

Selected tanks are `quarantined` during `[start_day, start_day + D)` and return to `open` on day `start_day + D`. Duration `D` is fixed in the main experiment; its value is **Candidate value, frozen after pilot (D004, issue #4)**. The semantics (half-open interval, one-time trigger and cost measured in tank-days) are frozen. In the implementation, `D` is an ordinary configuration value marked provisional in the config.

## 12. Intervention strategies

An intervention quarantines `k` tanks for `D` days.

### No intervention

- Tank states do not change; cost = 0.
- Response delay has no effect. Reporting may share a baseline within the same transfer/network/epidemic block to avoid duplicating identical runs.

### Random tank quarantine

- Select `k` of the 20 tanks uniformly without replacement.
- Selection uses only `policy_seed`; it does not read infection state or future movement.
- Generate and record the selection at the start of the run, but activate it only on the response day.

### Highest-betweenness tank quarantine

- Select the top `k` tanks by betweenness in the pre-outbreak network.
- Break ties by ascending `tank_id`.
- Do not use epidemic state or future information.
- Start on the same day as the random strategy and use the same duration `D`.

### Budget fairness

Random and targeted strategies must use the same `k`, start day, `D`, network instance, epidemic seed, disease parameters and movement parameters. Their only main difference is the tank selection method.

```text
intervention cost = number of quarantined tanks × quarantine duration
                  = k × D tank-days
```

`k`: **2 tanks, Frozen 2026-09-11 (D003, see `decision-log.md`)**. Rationale: avoid an intervention covering most of the 20-node network.

## 13. Daily update order

1. **Management update**: activate quarantine according to response delay or release it according to duration.
2. **Movement stage**: randomized asynchronous movement; quarantine and capacity apply immediately.
3. **Transmission snapshot**: freeze post-movement membership and disease states.
4. **Transmission draws**: generate pending `S -> I` transitions.
5. **Recovery draws**: generate pending `I -> R` transitions for agents already in `I` in the snapshot.
6. **Synchronous disease commit**: apply infection and recovery transitions simultaneously.
7. **Record outputs**.
8. **Check stopping condition**.

Movement is therefore randomized asynchronous, while disease updates are synchronous. This order is fixed in the main experiment; a small update-order sensitivity analysis may be conducted if time permits.

## 14. Stopping conditions

Normal stopping occurs at the first observation of:

```text
total infected population I(t) = 0
```

Safety horizon `max_days`: **365 days, Frozen 2026-09-11 (D006; the team adopted the working proposal after Checkpoint 1; see `decision-log.md`)**. If infection remains at the horizon:

- Mark the run `censored_max_days`;
- Do not fabricate an extinction time;
- Retain the complete record;
- Handle it separately in time-to-extinction analysis.

An invalid state, invariant failure or exception ends the run as `failed`, not as normal extinction.

## 15. Output recording rules

### 15.1 Daily outputs

- day; S/I/R population;
- occupancy, S/I/R and management state for each tank;
- attempted, accepted and blocked transfers;
- new infections, recoveries and current affected tanks.

### 15.2 Run metadata

- complete configuration and code commit;
- network, epidemic and policy seeds;
- network attempt index, adjacency list and centralities;
- selected tanks, start day, duration and budget;
- run status, stop reason and error details.

### 15.3 Metrics

| Metric | Definition | Research link |
|---|---|---|
| Final attack rate | `ever_infected agents / 200`, including the initial case | primary final outbreak size |
| Number of affected tanks | Number of distinct tanks that have contained at least one `I` agent during the run, including the initial tank | primary cross-tank spread |
| Peak infected population | Maximum `I(t)` across daily snapshots, including `t=0` | outbreak burden/dynamics |
| Time to extinction | Time from `t=0` to the first `I(t)=0`; do not insert fictitious values for censored runs | outbreak duration |
| Time to peak | First day the peak is reached | auxiliary dynamics |
| Intervention cost | `k × D` tank-days | fairness/resource use |
| Relative reduction vs random | `(Y_random - Y_targeted) / Y_random` | secondary comparison |

If `Y_random = 0`, record relative reduction as undefined, not 0.

## 16. Random-number and seed management

| Seed | Controls |
|---|---|
| `network_seed` | topology and regeneration attempts |
| `epidemic_seed` | initial case, movement, transmission, recovery (event-keyed; see below) |
| `policy_seed` | random quarantine selection only |

To preserve paired comparisons, epidemic randomness uses **event-keyed draws** (decided on 2026-09-11, replacing the "independent substreams" proposal; see `turtlefarm/rng.py` for the implementation):

- For each process ∈ {movement, movement_destination, transmission, recovery}, derive a generator on each day `t` using `SeedSequence(epidemic_seed, spawn_key=(process, t))` and generate a uniform array of length `n_agents`. Agent `a` always consumes array entry `a` for that process and day.
- The movement draw serves as both the agent's processing priority and attempt draw for that day. The `movement_destination` draw maps via `floor(u × m)` to the `m` currently eligible destinations sorted by `tank_id`. This convention avoids adding a third random stream and fully specifies replay behaviour for asynchronous movement.
- The draw for `(process, day, agent)` therefore depends only on the epidemic seed, not on how many agents are exposed that day or on prior history. A policy preventing one exposure does not shift the draws for other agents or later days.
- Independent substreams (one sequential stream per process) do not have this property: changing the exposed set shifts draw indices within a stream, making random and targeted strategies paired in name only.
- Initialisation uses a separate `spawn_key=(0,)` generator, consumed once when selecting the initial case. The policy seed has its own stream, used only for random tank selection.
- Checking exposure does not itself consume a draw: an `S` agent does not read a transmission draw when `I_j = 0` in its tank, and newly infected agents do not read a recovery draw that day.
- The draw source is a replaceable interface. The hand trace replaces seed derivation with an explicit draw table (`TableDraws`); reading a draw missing from the table fails immediately, testing the rules for draws that must not be consumed.

Identical configurations and seeds must produce identical results.

## 17. Prohibition on future information

Intervention selection must not use future infection states, future transfers, future affected tanks, final metrics or disease-informed centrality recalculated during the run. Targeted selection uses only the fixed pre-outbreak network; random selection uses only the policy seed.

## 18. Decision status and two-layer freeze rule

| ID | Item | Status | Value / rule |
|---|---|---|---|
| D001 | Response-delay origin | Frozen 2026-09-11 | From introduction at `t = 0` (§11) |
| D002 | Fixed capacity | Frozen 2026-09-11 | 12 (§6.2) |
| D003 | Quarantined tank count `k` | Frozen 2026-09-11 | 2 (§12) |
| D004 | Quarantine duration `D` | Semantics frozen; value after pilot | §11; issue #4 |
| D005 | `p_in` / `p_out` / acceptance thresholds | Algorithm frozen; values after structural pilot | §3; issue #5 |
| D006 | `max_days` | Frozen 2026-09-11 | 365 (§14) |
| D007 | No-intervention reporting | Frozen 2026-09-11 | Shared baseline per block (experiment-plan §3) |
| D008 | Headline outcome | Frozen 2026-09-11 | Attack rate + affected tanks co-primary (§15.3) |

**Two-layer freeze rule (effective from 2026-09-11, replacing the requirement that "all decisions must be frozen before code implementation"):**

1. **Semantic freeze (before implementation)**: state definitions, update order, transmission/recovery/movement/quarantine rules, seed derivation and output fields. All are frozen. M2 implementation must follow this document without making additional semantic choices.
2. **Numerical freeze (before formal experiments)**: `beta`, `gamma`, `D`, `p_in`/`p_out`, transfer-rate levels, delay levels and replication counts are frozen after the 19-25 Sep pilot and recorded in `decision-log.md` and the experiment config. Until then, these fields are ordinary configuration values, automatically marked provisional by the code and written to run metadata; pilot results are not hypothesis evidence.

Any semantic change still triggers cross-document updates under `consistency-review.md` §6.
