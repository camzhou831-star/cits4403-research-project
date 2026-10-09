# Model and assumptions

This specification describes the implemented synthetic model. D001-D003 and D006-D008 were frozen on 2026-09-11. The formal settings selected on 2026-10-06 are `beta=0.2`, `gamma=0.1`, `D=14`, `p_in=0.6` and `p_out=0.05`. The [decision record](decisions.md) distinguishes later D004/D005 confirmations from unresolved protocol sign-offs.

The submission layout places configurations in `data/config/`, outputs in `data/results/`, command-line entry points in `utils/` and tests in `src/tests/`. Paths below use that layout unless explicitly quoted as historical evidence; dates, recorded commits and numerical results are unchanged.

## Research questions and hypotheses

A modular housing system permits frequent local contacts but relatively few transfers between regions. The experiment asks how these local rules produce outbreaks that remain local or reach other regions, and whether pre-outbreak network structure helps allocate a limited quarantine budget.

Primary question: How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

Secondary question: Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

The original hypotheses were predictions to test, not findings:

- H1: Relative to zero or very low transfer, non-zero transfer is expected to increase final attack rate and the number of affected tanks by enabling cross-group spread.
- H2: For a fixed transfer rate and quarantine policy, longer response delay is expected to produce no smaller final attack rate and no fewer affected tanks on average.
- H3: Under an equal intervention budget and paired random conditions, highest-betweenness quarantine is expected to produce lower final attack rate and fewer affected tanks than random quarantine.

Strict monotonicity was not required in individual stochastic runs. Results and intervals determine the conclusions; the [follow-up](followup.md#results) does not establish a universal delay or strategy ordering. The contribution is a controlled paired experiment across networks and outbreaks, not merely an SIR simulator.

All agents, networks and data are synthetic. The model does not predict a real turtle disease. It has no mortality, births, ageing, breeding, treatment, vaccination, exposed state, waterborne layer or calibrated detection process. Recovery means immunity for the remainder of one run as an SIR simplification; it is not evidence for lifetime immunity in real turtles.

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
4. If the network is disconnected, has no cross-region edge or fails a predefined structural check, deterministically generate the next attempt from the same network seed and record the attempt index. The predefined structural checks (specified on 2026-09-11 in `src/turtlefarm/network.py`) are: (a) connected; (b) at least one cross-region edge; (c) not a complete graph; (d) node betweenness values are not all equal. Deterministic convention (frozen on 2026-09-11): each attempt uses `PCG64(SeedSequence(network_seed, spawn_key=(attempt,)))`, drawing one uniform value for each of the 190 node pairs in the lexicographic order of `itertools.combinations(range(20), 2)`. Every rejection reason is recorded. If no attempt passes within 100 attempts, the run is marked `failed` and all rejection reasons are retained.
5. Save the adjacency list, region assignment, network seed, attempt index, network hash, mean degree, density, clustering coefficient, modularity, diameter and node betweenness.

The formal experiment uses **`p_in = 0.6`, `p_out = 0.05` (D005, selected 2026-10-06)** with the generation and acceptance rules above. The original structural audit compared 16 parameter pairs and preferred the lowest within-region density among its three passing candidates. The movement pilot supported retaining that setting. Both members confirmed retaining the setting retrospectively on 2026-10-08; see `decisions.md` for the limited scope of that confirmation.

The follow-up in `validation.md#network-audit-2026-10-08` finds that all 30 checked networks generate within the retry limit, but one has an exact tie at rank 2 under the original C4 criterion. Both tied tanks are selected for `k=2`. This limitation does not change the runtime acceptance or tie-breaking rules, and must not be described as all C1-C5 criteria passing on the expanded sample. Manual bridge edges would be easier to prescribe but would reduce network-instance variation; they are not used here.

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

All tanks use the same fixed capacity in the main experiment. Exact value: **capacity = 12, Frozen 2026-09-11 (D002; the team adopted the working proposal after Checkpoint 1; see `decisions.md`)**.

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

- When `mu > 0`, every agent receives an event-keyed movement draw; at `mu = 0`, the movement stage returns without reading movement draws. Ascending draw order (ascending `agent_id` for exact ties) defines the randomized asynchronous processing order.
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

**Delay origin: measured from outbreak introduction (`t = 0`), Frozen 2026-09-11 (D001; the team adopted the working proposal after Checkpoint 1; see `decisions.md`).** The alternative, first observed infection, requires an observation model or an additional detection assumption and would expand the scope. This project interprets delay as a combined abstraction of detection and administrative response.

Selected tanks are `quarantined` during `[start_day, start_day + D)` and return to `open` on day `start_day + D`. The main experiment fixes **`D=14` (D004, selected 2026-10-06)**. Of the 7/14/21-day candidates, only 14 meets Q1-Q3; the criterion table was reproduced on 2026-10-08. See `decisions.md` for the alternatives, post-hoc Q1 qualifications and the retrospective 2026-10-08 confirmation. The half-open interval, one-time trigger and tank-day cost are unchanged. The implementation's provisional-field list is empty for the formal experiment; that metadata does not establish team sign-off.

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
intervention cost = k × D committed tank-days when activated; 0 if never activated
```

`k`: **2 tanks, Frozen 2026-09-11 (D003, see `decisions.md`)**. Rationale: avoid an intervention covering most of the 20-node network.

## 13. Daily update order

1. **Management update**: activate quarantine according to response delay or release it according to duration.
2. **Movement stage**: randomized asynchronous movement; quarantine and capacity apply immediately.
3. **Transmission snapshot**: freeze post-movement membership and disease states.
4. **Transmission draws**: generate pending `S -> I` transitions.
5. **Recovery draws**: generate pending `I -> R` transitions for agents already in `I` in the snapshot.
6. **Synchronous disease commit**: apply the pending transitions from that frozen snapshot. The implementation records recoveries before infections; the disjoint decisions were both made before either set is committed.
7. **Record outputs**.
8. **Check stopping condition**.

Movement is therefore randomized asynchronous, while disease updates are synchronous. This order is fixed in the main experiment; a small update-order sensitivity analysis may be conducted if time permits.

## 14. Stopping conditions

Normal stopping occurs at the first observation of:

```text
total infected population I(t) = 0
```

Safety horizon `max_days`: **365 days, Frozen 2026-09-11 (D006; the team adopted the working proposal after Checkpoint 1; see `decisions.md`)**. If infection remains at the horizon:

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
| Intervention cost | `k × D` committed tank-days if activated; 0 otherwise | fairness/resource use |
| Relative reduction vs random | `(Y_random - Y_targeted) / Y_random` | secondary comparison |

If `Y_random = 0`, record relative reduction as undefined, not 0.

## 16. Random-number and seed management

| Seed | Controls |
|---|---|
| `network_seed` | topology and regeneration attempts |
| `epidemic_seed` | initial case, movement, transmission, recovery (event-keyed; see below) |
| `policy_seed` | random quarantine selection only |

To preserve paired comparisons, epidemic randomness uses **event-keyed draws** (decided on 2026-09-11, replacing the "independent substreams" proposal; see `src/turtlefarm/rng.py` for the implementation):

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


## Assumptions

| ID | Assumption | Why needed / reasonableness | Potential effect | Sensitivity | Category |
|---|---|---|---|---|---|
| A001 | All 200 agents form a synthetic population with no corresponding real records | Avoids privacy issues and insufficient empirical data; suitable for explanatory experiments | Does not represent a real farm | population size only optional | data limitation |
| A002 | The 20-tank modular network is synthetic | No authorised movement logs; structure can be controlled | Bridge importance depends on the generation rule | Multiple network seeds; small modularity check | data limitation / simplification |
| A003 | Complete mixing within each tank | No within-tank spatial data; the main question concerns cross-tank movement | May overestimate uniform contact | Fixed in the main experiment; check `beta` | simplification |
| A004 | Homogeneous susceptibility and infectiousness | No species, age or health calibration; isolates the network effect | Ignores individual heterogeneity and superspreading | optional heterogeneity | simplification / data limitation |
| A005 | No real disease calibration | No reliable veterinary data or calibration target | Cannot extrapolate to real probabilities or durations in days | Small `beta/gamma` robustness check | data limitation |
| A006 | Disease progression is limited to `S -> I -> R` | Controls the state space; no E/Q/death/treatment in the MVP | Changes how real timescales are represented | Discuss in limitations without extending the MVP | simplification |
| A007 | A recovered agent cannot be reinfected within a run | Keeps SIR closed and allows extinction | May underestimate later spread if real immunity is short-lived | future extension | simplification |
| A008 | The permitted-transfer network is static within a run | Stable centrality; dynamics arise from agent movement | Ignores temporary route changes | Static/dynamic comparison is a should-have extension | simplification |
| A009 | Complete network information is available before intervention | The targeted policy may use only available information | Incomplete observation may reduce policy performance | Facilitator confirmation; optional observation error | simplification / data limitation |
| A010 | Quarantine completely blocks incoming and outgoing transfers | Makes the intervention clear and verifiable | May overestimate real compliance | partial compliance optional | simplification |
| A011 | Transmission and recovery continue inside a quarantined tank | Separates movement restriction from treatment | Attack rate can remain high in quarantined tanks | Fixed definition, not a main sensitivity factor | simplification |
| A012 | Intervention is applied immediately on a fixed response day | Avoids detection/rollout submodels | Ignores gradual implementation | Delay is a main factor, measured from introduction (D001) | simplification |
| A013 | Random/targeted use the same `k`, start and duration | Answers the secondary question fairly | Does not study adaptive release | Main experiment uses `k=2`, `D=14`; see D004 evidence and retrospective confirmation | model simplification |
| A014 | S/I/R agents have the same movement probability | No evidence for symptom-dependent movement | May overestimate infected transfers | optional disease-dependent movement | simplification / data limitation |
| A015 | Tanks have equal capacity and initial occupancy in the main experiment | Avoids confounding capacity with centrality | Underestimates occupancy variation | heterogeneous capacity only sensitivity | simplification |
| A016 | Daily infection/recovery draws are conditionally independent given the state | Defines the stochastic process explicitly | No shared environmental shocks | Outside the MVP | simplification |
| A017 | Capacity is a hard constraint | Avoids invalid states | Blocked transfers change the actual movement rate | Record attempts/acceptance; check capacity | simplification / computational |
| A018 | Betweenness ties are resolved deterministically by `tank_id` | Preserves reproducibility without future information | May favour small IDs in symmetric networks | The 30-seed follow-up found one rank-2 tie; both tanks are selected for `k=2`. See `validation.md#network-audit-2026-10-08`. | computational |


## Implementation checkpoints

Day 0 records the initial state; `step()` increments the day before executing day 1. Agent and tank IDs are contiguous and start at 0. Movement immediately changes membership, occupancy and `tank_id`, so later movement attempts see those changes. An infectious arrival marks the destination as ever affected even if the agent recovers later that day.

After movement, `_transmission_and_recovery()` freezes the infectious agents in `infectious_today`. Susceptible agents with no infectious tank-mates read no transmission draw. Only agents already infectious in that snapshot receive recovery draws. Thus an infectious agent can transmit and recover on the same day, while a newly infected agent can do neither until the next day. With `gamma=1`, the initial case recovers on day 1 and an agent infected on day d recovers on day d+1.

`_check_invariants()` runs before `_record()`; stopping follows recording. `_transition()` permits only `S -> I` and `I -> R`, and updates `state_entered_day`. The record also checks that blocking causes sum to total blocked transfers. See [validation](validation.md#hand-trace) for the hand-calculated event sequence and [result schema](result-schema.md) for fields and failure handling.

The original walkthrough guide was preparation material. It did not establish that the joint ten-minute session required by issue #18 took place or that either member demonstrated understanding. The retained record contains no completed session or participant confirmation.

## Scope of robustness evidence

Multiple network and epidemic seeds test stochastic variation under the chosen generator. The [duration and policy-sampling follow-up](followup.md) changes duration and policy draws while holding the disease regime, capacity and transfer rate fixed. Checks of beta, gamma, heterogeneous capacity, different update orders, changing routes, incomplete network information, partial compliance and disease-dependent movement remain extensions, not completed validation of real-world applicability.
