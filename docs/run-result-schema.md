# Run Metadata and Raw-Result Schema

Status: draft for issue #15. This document defines the recording contract for pilot and formal runs. It does not contain simulated, prototype, or fabricated results.

## 1. Storage contract

- Raw results use UTF-8 JSON Lines (`.jsonl`), with exactly one self-contained JSON object per run.
- Files under `results/raw/` are append-only and must not be edited by hand.
- Each record includes its schema version, complete configuration, seeds, network provenance, intervention details, daily observations, predefined metrics, and completion or failure information.
- Summary tables and figures are generated from raw records and stored separately under `results/summary/` and `results/figures/`.
- Validation-only scenarios use the same field names but must have `config.design = "scenario"`; the formal experiment runner must refuse them.

The initial schema identifier is `turtlefarm.run.v1`. A change that removes a field, changes its meaning, or changes its type requires a new schema version.

## 2. Top-level run record

| Field | Type | Required | Null rule | Producer and meaning |
|---|---|---:|---|---|
| `schema_version` | string | yes | never | Runner; fixed to `turtlefarm.run.v1` for this schema. |
| `run_id` | string | yes | never | Runner; unique opaque identifier for this execution. Rerunning the same configuration creates a new `run_id`. |
| `timestamp_utc` | string | yes | never | Runner; ISO 8601 UTC time at run start, ending in `Z`. |
| `code_commit` | string | yes | allowed only when Git metadata is unavailable | Model; Git commit used for the run. |
| `configuration_hash` | string | yes | never | Runner; SHA-256 of canonical `config`, as defined in section 8. |
| `config` | object | yes | never | Model; complete `SimulationConfig`, including provisional-field markers. |
| `seeds` | object | yes | never | Model; `network_seed`, `epidemic_seed`, and nullable `policy_seed`. |
| `network` | object | yes for main design | null only for a failed run before network construction or an explicit validation layout | Model; immutable pre-outbreak network and structural provenance. |
| `initial_infected_agents` | array of integer | yes | never | Model; agent IDs infected at `t = 0`. |
| `initial_infected_tanks` | array of integer | yes | never | Model; tank IDs containing the initial infected agents. |
| `selected_tanks` | array of integer | yes | never | Model; quarantine targets. Empty for no intervention or failure before selection. |
| `intervention_start_day` | integer | yes | null for no intervention or failure before activation | Model; first quarantined day. |
| `intervention_duration_days` | integer | yes | null for no intervention | Runner projection of `config.quarantine_duration`. |
| `intervention_cost` | integer | yes | never | Model; `k × duration` tank-days for an activated intervention, otherwise `0`. |
| `status` | enum string | yes | never | Model; `completed`, `censored_max_days`, or `failed`. |
| `stop_reason` | string | yes | never | Model; explicit extinction, horizon, validation failure, or runtime-failure reason. |
| `error` | string | yes | null unless `status = "failed"` | Model; error type, message, and traceback where available. |
| `daily` | array of object | yes | never | Model; ordered observations from day 0 through the final recorded day. May be empty only if failure occurs before initial recording. |
| `metrics` | object | yes | never | Model; predefined run-level outcomes. May be empty only if no daily state was recorded. |
| `transitions` | array | yes | never | Model; optional validation audit trail represented as `[day, agent_id, from_state, to_state]`. Empty in production unless transition recording is enabled. |

All `config` values are retained even when a run fails. No failed or censored record may be silently dropped.

## 3. Configuration object

`config` is the complete serialised `SimulationConfig`; fields must not be selected manually by the runner.

| Group | Fields |
|---|---|
| Design | `design`, `n_agents`, `n_tanks`, `n_regions`, `initial_per_tank`, `initial_infected` |
| Disease | `beta`, `gamma` |
| Network | `p_in`, `p_out`, `network_max_attempts` |
| Movement | `transfer_rate`, `capacity` |
| Intervention | `strategy`, `response_delay`, `quarantine_duration`, `k` |
| Horizon | `max_days` |
| Seeds | `network_seed`, `epidemic_seed`, `policy_seed` |
| Provenance | `label`, `provisional_fields` |

The duplicated seed values in `seeds` are deliberate: `config` preserves the complete input while `seeds` provides a stable field for grouping paired runs.

## 4. Network object

The `network` object records the accepted pre-outbreak network. Its `network_hash` is the network ID and is used to verify that paired strategies share one network instance.

| Field | Type | Meaning |
|---|---|---|
| `network_hash` | string | Stable hash of regions and accepted edges; canonical network ID. |
| `network_seed` | integer | Seed used to generate the network. |
| `attempt` | integer | Zero-based accepted generation attempt. |
| `rejected` | array of string | Rejection reason for every earlier attempt. |
| `n_tanks` | integer | Number of tank nodes. |
| `regions` | array of integer | Region index by tank ID. |
| `edges` | array of integer pairs | Immutable undirected edge list. |
| `adjacency` | object | Tank ID to sorted neighbouring tank IDs. |
| `p_in`, `p_out` | number | Within-region and between-region edge probabilities. |
| `betweenness` | array of number | Pre-outbreak normalised betweenness by tank ID. |
| `ranking` | array of integer | Descending betweenness order with the specified tie-break. |
| `tie_groups` | array of integer arrays | Exact-equality centrality ties. |
| `metrics` | object | Structural diagnostics such as density, clustering, modularity, and diameter. |

The selector may read this object but must not replace it with centrality calculated from epidemic states.

## 5. Daily observation

Each item in `daily` has the following fields:

| Field | Type | Meaning |
|---|---|---|
| `day` | integer | Simulation day, beginning at `0`. |
| `S`, `I`, `R` | integer | End-of-day population counts. |
| `new_infections` | integer | `S -> I` transitions committed that day. |
| `recoveries` | integer | `I -> R` transitions committed that day. |
| `attempted_transfers` | integer | Eligible movement attempts. |
| `accepted_transfers` | integer | Successful cross-tank movements. |
| `blocked_transfers` | integer | Attempts blocked by quarantine, capacity, or no destination under the final M2 event definition. |
| `affected_tanks_now` | integer | Tanks containing at least one infectious agent at the end of the day. |
| `affected_tanks_ever` | integer | Distinct tanks that have contained an infectious agent up to that day. |
| `tanks` | array of object | Per-tank `tank_id`, `region_id`, `occupancy`, `S`, `I`, `R`, and `management_state`. |

Daily rows must be ordered by `day`, contain no duplicate day, and satisfy the model invariants for every recorded state.

## 6. Metrics object

| Field | Type | Null rule |
|---|---|---|
| `final_attack_rate` | number | Present when at least one daily state exists. |
| `ever_infected` | integer | Present when at least one daily state exists. |
| `affected_tanks` | integer | Present when at least one daily state exists. |
| `peak_infected` | integer | Present when at least one daily state exists. |
| `time_to_peak` | integer | Present when at least one daily state exists. |
| `time_to_extinction` | integer | Null for censored or failed runs without observed extinction. |
| `days_simulated` | integer | Final recorded day. |
| `intervention_cost` | integer | Same quantity as the top-level `intervention_cost`. |

Relative reduction between strategies is a paired-analysis output, not a property of one run, and therefore belongs in a generated summary table rather than the raw run record.

## 7. Status and failure rules

| Status | Required interpretation |
|---|---|
| `completed` | Extinction was observed; `time_to_extinction` is the first day with `I = 0`. |
| `censored_max_days` | Infection remained at the configured horizon; `time_to_extinction` is null. |
| `failed` | A validation or runtime error stopped the run; `error` is non-null and configuration, seeds, and any available partial observations are retained. |

An extreme but valid outcome is not a failure. A rerun after a confirmed implementation bug retains the original record and uses the same seed block after the corrective commit is documented.

## 8. Runner-derived provenance

The M2 runner supplies four fields that do not belong to the disease model itself:

1. `schema_version` from the runner's supported schema.
2. `run_id` as a unique execution identifier.
3. `timestamp_utc` at execution start.
4. `configuration_hash`, computed as lowercase hexadecimal SHA-256 over UTF-8 canonical JSON for `config`, using sorted keys and compact separators.

The runner must serialise dataclasses and tuples into ordinary JSON objects and arrays without changing their meaning. It must write the final record once per attempted run, including failed and censored runs.

## 9. Current implementation coverage

| Requirement | Current source | Status before M2 |
|---|---|---|
| Complete configuration and three seeds | `RunRecord.config`, `RunRecord.seeds` | available |
| Commit provenance | `RunRecord.code_commit` | available |
| Network ID, adjacency, centrality, attempt and diagnostics | `RunRecord.network` | available |
| Initial case provenance | `initial_infected_agents`, `initial_infected_tanks` | available |
| Daily S/I/R, tank states and transfer counters | `RunRecord.daily` | structure available; movement counters remain zero in M1 |
| Status, stop reason, errors and censoring | `status`, `stop_reason`, `error`, `metrics` | available |
| Selected tanks, intervention timing and cost | existing `RunRecord` fields plus `config` | structure available; values remain baseline placeholders in M1 |
| Schema version, run ID, timestamp and configuration hash | none | runner must add in M2 |
| JSONL persistence | none | runner must add in M2 |

The baseline therefore supplies all model-owned information required by this schema. The M2 runner must add the execution envelope and persistence layer, while movement and intervention implementation must replace the existing baseline placeholder values.

## 10. Review checklist for issue #15

Member A should confirm that:

- every model-owned field is emitted or can be derived without reading future outcomes;
- `network_hash` is an adequate network identifier;
- intervention duration and budget have one consistent meaning across model, runner, and analysis;
- failed and censored runs retain sufficient provenance;
- the M2 runner owns only execution metadata and serialisation, not scientific outcome calculation.
