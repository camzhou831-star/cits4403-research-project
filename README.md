# CITS4403 Research Project

## Bridge Transfers and Quarantine in a Captive Turtle Farm

This is the shared repository for our CITS4403 Research Project.

- Course: CITS4403 Computational Modelling
- Team: Cam Zhou (`camzhou831-star`) and Wenhao Zhang (`Winston-2hang`)
- Due: 9 October 2026, 11:59 pm
- Repository status: Checkpoint 1 planning

## Proposed system

We study disease transmission among captive turtles housed in multiple tanks. Turtles mainly interact within a tank, while occasional transfers create connections between otherwise separate groups.

## Motivation

A disease outbreak may remain local when tanks are isolated. However, even a small number of transfers may act as network shortcuts and allow the outbreak to spread across the farm. Quarantine resources are limited, so the choice of intervention strategy matters.

## Research question

How do cross-tank transfer rate and quarantine delay affect outbreak size, and does targeted quarantine of bridge tanks perform better than random quarantine under the same intervention budget?

## Hypothesis

A low but non-zero transfer rate will greatly increase the number of affected tanks. Targeted quarantine will reduce outbreak size more than random quarantine, especially when detection is delayed.

## Modelling approach

We plan to build an agent-based SIR-Q model with a dynamic contact network:

- Each turtle is an agent in one of four states: susceptible, infected, recovered, or quarantined.
- Tanks are local contact groups.
- Infection occurs through contact within a tank.
- Turtles may move between tanks with a configurable transfer probability.
- Detected infections are quarantined after a configurable delay.
- Random and bridge-based quarantine strategies will be compared using the same intervention budget.

## Planned experiments

We will vary:

- cross-tank transfer rate;
- infection and recovery probabilities;
- quarantine delay;
- tank capacity and occupancy;
- intervention strategy.

Main outputs will include final outbreak size, peak prevalence, time to peak, affected tanks, outbreak duration, and quarantine cost. Each experimental condition will be repeated with multiple random seeds, and both qualitative and quantitative results will be reported.

## Independent investigation

The project will compare static and dynamic contact assumptions and evaluate random quarantine against bridge-based targeted quarantine under an equal intervention budget.

## Planned repository structure

```text
docs/          Research plan, checkpoint material, assumptions and decisions
src/           Model and simulation implementation
experiments/   Parameter configurations and repeatable experiment runners
tests/         Unit tests, invariants and reproducibility checks
results/       Generated summaries and selected figures
```

## Reproducibility rules

- Every stochastic run must record its random seed.
- Raw parameters and model assumptions must be stored with each experiment.
- Baseline and intervention conditions must use comparable settings.
- Failed or anomalous runs must not be silently removed.
- Generated data and figures must be reproducible from committed code and configuration.

## Academic integrity

This repository is a new CITS4403 project. Previous projects and course notebooks may inform general engineering practices and modelling concepts, but assessed code, reports, results, and third-party restricted code will not be copied into this repository. The model, research question, experiments, analysis, and written discussion will be produced specifically for this project.

See [docs/checkpoint-1.md](docs/checkpoint-1.md) and [docs/research-plan.md](docs/research-plan.md) for the initial plan.
