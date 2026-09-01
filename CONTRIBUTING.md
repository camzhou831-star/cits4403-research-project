# Collaboration workflow

## Branches

- Keep `main` in a reviewable and reproducible state.
- Use short feature branches such as `model/sir-q`, `experiment/quarantine-delay`, or `analysis/network-metrics`.
- Open a pull request before merging substantial model, experiment, or report changes.

## Commits

- Make focused commits with clear messages.
- Do not commit secrets, local databases, virtual environments, or large raw outputs.
- Record important changes to assumptions or experimental definitions in `docs/research-plan.md` or a separate decision note.

## Review checklist

- Are model assumptions and update rules explicit?
- Are stochastic results reproducible from a recorded seed?
- Is the baseline comparable to the intervention condition?
- Are units, metrics, and aggregation rules documented?
- Are tests included for new model rules and invariants?
- Does the change contain any copied assessed or restricted material?

## Suggested division of work

- Modelling stream: agent states, update rules, validation and model tests.
- Experiment stream: parameter sweeps, statistical summaries and visualisation.
- Both team members review assumptions, results and report claims.
