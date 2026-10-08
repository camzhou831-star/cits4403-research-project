# Model Assumptions Register

Categories include model simplification, computational constraint and data limitation.

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
| A013 | Random/targeted use the same `k`, start and duration | Answers the secondary question fairly | Does not study adaptive release | Main experiment uses `k=2`, `D=14`; see D004 evidence and pending confirmation | model simplification |
| A014 | S/I/R agents have the same movement probability | No evidence for symptom-dependent movement | May overestimate infected transfers | optional disease-dependent movement | simplification / data limitation |
| A015 | Tanks have equal capacity and initial occupancy in the main experiment | Avoids confounding capacity with centrality | Underestimates occupancy variation | heterogeneous capacity only sensitivity | simplification |
| A016 | Daily infection/recovery draws are conditionally independent given the state | Defines the stochastic process explicitly | No shared environmental shocks | Outside the MVP | simplification |
| A017 | Capacity is a hard constraint | Avoids invalid states | Blocked transfers change the actual movement rate | Record attempts/acceptance; check capacity | simplification / computational |
| A018 | Betweenness ties are resolved deterministically by `tank_id` | Preserves reproducibility without future information | May favour small IDs in symmetric networks | The 30-seed follow-up found one rank-2 tie; both tanks are selected for `k=2`. See `network-audit-2026-10-08.md`. | computational |

## Mandatory assumption clarifications

### Quarantine timing

D001 measures response delay from outbreak introduction (`t=0`), with activation before the movement stage on the relevant day. Day 0 is the initial snapshot; the first movement occurs on day 1. Measuring from the first observed infection would require an observation process; the meaning must not be changed silently.

### Intervention duration and budget

All intervention conditions use the same `k` and duration `D`:

```text
cost = k × D tank-days
```

`k = 2` was frozen on 2026-09-11 (D003). The formal experiment uses `D = 14`, selected on 2026-10-06 (D004), giving a planned cost of 28 tank-days when quarantine starts. The Q1-Q3 evidence and pending Member B confirmation are recorded in `decision-log.md`.

## Assumption decision status

Frozen (2026-09-11, `decision-log.md`): response-delay origin (introduction), fixed capacity (12), number of quarantined tanks (2) and maximum simulation horizon (365).

The completed formal experiment uses `D=14` and `p_in=0.6` / `p_out=0.05`. These values are implemented and recorded in the formal design, but Member B's retrospective confirmation is pending. The expanded network audit supports generation stability and identifies one failure of the original C4 no-tie clause. It does not change the model assumptions or remove the need to record that limitation.
