# Checkpoint 1

## System

Disease transmission among captive turtles housed in multiple tanks, with occasional transfers between tanks.

## Motivation

Turtles in the same tank have frequent contact. Even a small number of transfers may connect separate tanks and allow a local outbreak to spread across the whole farm.

## Research question

How do cross-tank transfer rate and quarantine delay affect outbreak size, and does targeted quarantine of bridge tanks perform better than random quarantine under the same intervention budget?

## Hypothesis

A low but non-zero transfer rate will greatly increase the number of affected tanks. Targeted quarantine will reduce outbreak size more than random quarantine, especially when detection is delayed.

## Modelling approach

We will build an agent-based SIR-Q model. Each turtle is susceptible, infected, recovered, or quarantined. Infection occurs through contact within a tank, while transfers create a dynamic contact network between tanks.

## Planned experiments

We will vary transfer rate, infection probability, quarantine delay, tank capacity, and intervention strategy. Each condition will be repeated with multiple random seeds. We will measure final outbreak size, peak infection, time to peak, affected tanks, and quarantine cost.

## Independent investigation

We will compare static and dynamic contact assumptions and test random quarantine against bridge-based targeted quarantine using the same intervention budget.

## Expected contribution

The project will show when occasional transfers change a contained outbreak into a farm-wide outbreak, and which quarantine strategy is most effective under limited resources.

## Material to prepare for the checkpoint

- A diagram of tanks, within-tank contacts, and cross-tank transfers.
- A table defining S, I, R, and Q states.
- A short description of the daily update rules.
- The baseline and two intervention strategies.
- A table of independent variables and output metrics.
- A small prototype plot or example run.
- The planned experiment matrix and number of repeated runs.
