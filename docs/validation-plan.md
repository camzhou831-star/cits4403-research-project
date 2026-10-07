# Validation Plan

This document defines future tests and validation only; it contains no test code.

## 1. Validation goals

1. Verify that the implementation conforms to `model-specification.md`;
2. Verify that stochastic behaviour is reproducible;
3. Verify fair budgets and random conditions in strategy comparisons;
4. Verify expected behaviour at extreme parameter values;
5. Distinguish model logic errors, configuration errors and valid stochastic outcomes.

## 2. Required invariants

| ID | Invariant | Planned evidence |
|---|---|---|
| V001 | Total agent count always equals 200 | Daily summary matches the agent table count |
| V002 | Every agent belongs to exactly one tank | location uniqueness check |
| V003 | Every agent state is S/I/R only | enum/domain validation |
| V004 | `S + I + R = 200` holds every day | daily assertion and summary |
| V005 | Recovered agents cannot be reinfected | No `R -> I` in the transition log |
| V006 | Tank occupancy does not exceed capacity | Check after each movement |
| V007 | No incoming or outgoing transfers at quarantined tanks | movement event audit |
| V008 | Transmission can still occur inside quarantined tanks | controlled scenario review |
| V009 | Random/targeted use the same `k`, start and duration | paired configuration comparison |
| V010 | Centrality comes only from the pre-outbreak network | provenance and immutable network hash |
| V011 | Same config + seeds gives same outputs | repeated deterministic replay |
| V012 | Model reaches extinction or explicit horizon status | every run has stop reason |

## 3. Extreme and boundary cases

### V101 - `beta = 0`

- Initial infected may recover but no `S -> I` transition is allowed.
- Final ever-infected count must equal initial infected count.

### V102 - `transfer_rate = 0`

- No accepted cross-tank movement.
- Infection cannot enter any tank other than the initial infected tank.
- Number of affected tanks must remain 1.

### V103 - `gamma = 1`

- Existing infected agents recover at the first eligible recovery step after transmitting according to update order.
- Expected behaviour must match the documented "transmit then recover" rule.

### V104 - `beta = 1` with infected tank

- All susceptible agents sharing a tank with at least one infectious agent become infected in the transmission commit.
- Newly infected do not recover or infect further until next day.

### V105 - `transfer_rate = 1`

- Every eligible agent attempts movement once; capacity and quarantine still hold.
- Actual accepted rate may be below 1 due to capacity/no destination.

### V106 - Full tank

- No incoming movement may violate capacity.
- Blocked movement is recorded, not treated as simulation failure.

### V107 - Quarantine interval boundaries

- Tank blocks movement on days in `[start, end)`.
- Movement is allowed again at `end` before that day's movement stage.

### V108 - Zero-day response

- Intervention active before the first movement stage.
- It does not retroactively alter initial state.

### V109 - No intervention

- No tank enters quarantined state; cost = 0.
- Changing the unused response-delay label cannot change the run.

### V110 - Betweenness tie

- Ties resolve by ascending `tank_id`, unless this rule is later explicitly changed and documented.

## 4. Probability and configuration validation

- `0 <= beta <= 1`;
- `0 <= gamma <= 1`;
- `0 <= transfer_rate <= 1`;
- response delay, duration, `k`, capacity and `max_days` are valid non-negative/positive integers;
- `k <= 20`;
- initial occupancy <= capacity;
- exactly 20 tanks, 4 regions, 5 tanks per region;
- network simple, undirected, connected and has inter-region edges;
- seeds are serialisable and recorded;
- invalid configurations are rejected before a run starts, without silent clamping.

## 5. Strategy fairness validation

Check each paired block automatically or manually for:

- identical network hash;
- identical epidemic seed;
- identical initial infected agent/tank;
- identical transfer rate, beta, gamma and capacity;
- identical response day;
- identical quarantine count and duration;
- identical cost;
- targeted selection consistent with the pre-outbreak centrality ranking;
- random selection corresponding to the policy seed and without replacement;
- selected tanks as the only main policy difference.

## 6. Future-information validation

- Save the pre-outbreak network hash and centrality table.
- The intervention selector interface accepts only network/topology, `k` and policy seed, not epidemic state or output data.
- Targeted selected tanks should remain unchanged across epidemic seeds whenever the network seed is the same.
- Check during code review whether the selector reads daily infection/movement records.

## 7. Reproducibility validation

1. Run selected configurations twice consecutively;
2. Compare the daily event log, selected tanks, final metrics and stop reason;
3. The same seeds must produce byte-equivalent or canonical-data-equivalent results;
4. Changing one seed should change only the randomness it controls:
   - network seed changes topology;
   - epidemic seed changes the epidemic/movement trajectory;
   - policy seed changes only random quarantine selection.

## 8. Model-level plausibility checks

These are plausibility checks, not real-world calibration:

- Increasing transfer rate should not reduce the mean accepted transfer count unless capacity/quarantine blocking clearly explains it;
- `mu=0` should produce only a local outbreak;
- Earlier intervention need not improve every seed, but aggregate anomalies require investigation;
- Highest-betweenness tanks should have a clear structural relationship with cross-region shortest paths;
- The network generator should not frequently produce symmetric structures where all nodes have the same centrality.

## 9. Integration validation

After validating individual rules, use a very small network that can be calculated by hand for an end-to-end trace:

- A few tanks and agents;
- Fixed random draws;
- Hand calculation of one or several days of movement, infection, recovery and quarantine;
- Comparison with the model event log.

This fixture is for validation only, not a formal experiment or result.

M1 fixture: `docs/hand-trace-3tank.md` (3 tanks, 6 agents, 3 days, 8 fixed draws), with automated comparison in `tests/test_hand_trace.py`. Small scenarios are constructed using `turtlefarm.scenario.Layout` and config `design="scenario"`; the formal `design="main"` configuration remains fixed at 200 agents / 20 tanks. The experiment runner must reject `design != "main"`. Extend the fixture to include movement and quarantine after M2 is merged.

## 10. Failure and completion criteria

Before the model enters formal experiments:

- All V001-V012 must pass;
- V101-V110 extreme cases must conform to the specification;
- Same-seed replay must pass;
- The fairness audit must pass;
- Both members must independently read and sign off on the event trace;
- No unexplained invariant failure may remain.

Every run must end with normal extinction, `censored_max_days` or `failed`; it must not run indefinitely without a stop reason.
