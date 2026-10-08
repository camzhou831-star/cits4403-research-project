# Checkpoint 2 Speaking Notes

Status: draft 2026-09-20, drafted by Member A; Member B's sections (8-16) come from the team's speaking script and await Member B's confirmation or revision.

Coverage: main model components, experiment plan, current progress, issues and next steps. Total duration is about 8-10 minutes, with 4-5 minutes per member and one handover.

> The official Checkpoint 2 requirements and rubric are not recorded in the repository (README, "Current stage and gates", item 5). Check the LMS before the meeting; if the requirements differ, update this file first.

Line-number reference: `src/turtlefarm/config.py`, `entities.py`, `network.py`, `model.py`, `docs/experiment-plan.md` and README lines 1-37 have not changed since `main` @ `37a7fe3`. After opening a file on GitHub, press `y` to pin the link to the current commit.

## Before the meeting

```bash
git switch main && git pull          # Line numbers will differ if the local checkout is behind.
python -m pytest -q                  # Note the passing test count to read in Section 10.
python scripts/demo_checkpoint2.py   # Confirm the demo runs; about 1 second.
```

Open these tabs in advance: `README.md` (use `?plain=1` on the web page to show line numbers), `src/turtlefarm/config.py`, `entities.py`, `network.py`, `model.py`, `docs/experiment-plan.md`, and a terminal in the repository directory with `.venv` activated.

---

# Member A — Cam (Sections 1-7)

## 1. Opening and research questions (about 40 seconds)

**Show:** `README.md` lines 20-37 (lines 20-27 are in Chinese; focus on the English research questions in lines 29-37).

> Good morning. Today we will show our model, our experiment plan, our progress, and our open issues.
>
> Our project is about how a disease spreads in a turtle farm. The farm is not real. It is a simple model to help us understand spread, not to predict a real disease.
>
> We have 200 turtles, 20 tanks, and 4 regions. Each turtle is susceptible, infectious, or recovered. The tanks are joined in a network, and turtles can only move along the links.
>
> Our main question is: how do the transfer rate and the response delay change the outbreak size and the number of affected tanks?
>
> Our second question is: with the same budget, is it better to quarantine the high-betweenness tanks, or random tanks?

## 2. Repository structure (about 20 seconds)

**Show:** The repository home page, pointing to `turtlefarm`, `scripts`, `tests` and `docs` in order.

> The repository has four parts. `turtlefarm` is the model code. `scripts` has demos and checking tools. `tests` checks that the code is correct. `docs` has the model specification, the experiment plan, and our decisions.
>
> I will start with the model code.

## 3. Parameters (about 60 seconds)

**Show:** `src/turtlefarm/config.py` line 13.

> We have three strategies: no quarantine, random quarantine, and highest-betweenness quarantine.

**Show:** Lines 17-26.

> The system has 200 turtles, 20 tanks, 4 regions, and one infected turtle at the start. Each tank starts with 10 turtles and can hold 12. The quarantine picks 2 tanks. A run stops after 365 days at most.

**Show:** Lines 46-71.

> Beta is the chance of infection inside a tank. Gamma is the chance of recovery each day.
>
> `p_in` and `p_out` build the network. Two tanks in the same region are much more likely to be linked than two tanks in different regions.
>
> Transfer rate is how often a turtle tries to move. Response delay is the day quarantine starts. Quarantine duration is how long it lasts. `k` is how many tanks we quarantine.
>
> The three seeds make every run repeatable.

**Show:** Line 78 (`PROVISIONAL_FIELDS`).

> Some values are not final yet: beta, gamma, quarantine duration, `p_in` and `p_out`. We will fix them after the pilot, not from one demo run.

## 4. Agent and Tank (about 25 seconds)

**Show:** `src/turtlefarm/entities.py` lines 7-31.

> This file defines our two entities.
>
> A turtle knows which tank it is in, and its disease state: S, I, or R.
>
> A tank knows its region, its capacity, whether it is open or quarantined, when the quarantine starts and ends, and which turtles are inside.

## 5. Network (about 50 seconds)

**Show:** The top of `src/turtlefarm/network.py`.

> Tanks are the nodes of a fixed network. A link means turtles can move between those two tanks.
>
> Links are common inside a region and rare between regions. So the network has clusters, and a few tanks act as bridges between regions.

**Show:** Lines 51-69 (`structural_rejection_reason`).

> We reject a network if it is not connected, if it has no link between regions, if every tank is linked to every other tank, or if all tanks have the same betweenness. These checks make sure that "bridge tank" really means something.

**Show:** Lines 127-132 (`ranking` / `top_k`).

> We rank tanks by betweenness before the outbreak starts. The targeted strategy takes the top `k`. It only uses the network. It never uses information about the future outbreak.

## 6. Daily update rules (about 90 seconds)

**Show:** `src/turtlefarm/model.py` lines 429-443 (`step()`), pointing to lines 431-437 one by one.

> This function is one simulated day.
>
> First the day number goes up. Then we update quarantine. Then turtles move. Then we work out infection and recovery. Then we apply the changes. Then we check that nothing is broken. Last, we record the day.
>
> The `run()` method below just calls `step()` again and again, until no turtle is infectious or we reach the maximum number of days.

**Show:** Lines 224-275 (`_movement_stage`); you can point to line 244 and lines 254-259.

> For movement, each turtle gets a random number. If it is smaller than the transfer rate, the turtle tries to move.
>
> The destination must be a neighbour in the network, it must be open, and it must have space.
>
> If the turtle's own tank is quarantined, or there is no valid destination, the move is blocked.

**Show:** Lines 277-307 (`_transmission_and_recovery`), pointing to line 296, `p = 1.0 - (1.0 - cfg.beta) ** i_j`.

> For infection and recovery, we first take a snapshot of who is infectious today.
>
> If a susceptible turtle shares a tank with `i_j` infectious turtles, its chance of infection is one minus, one minus beta, to the power `i_j`.
>
> Each infectious turtle recovers with chance gamma.
>
> Because we use the snapshot, a turtle infected today cannot infect others or recover until tomorrow.

## 7. Handover

> That is how the model is built and how one day works. Wenhao will now explain the quarantine strategies, the outputs, the tests, the experiment plan, and our progress.

---

# Member B — Wenhao (Sections 8-16)

## 8. Quarantine strategies

**Show:** `src/turtlefarm/model.py` lines 173-187.

> I will first explain how the intervention strategies are implemented.
>
> Under no intervention, no tank is selected.
>
> Under random quarantine, the model uses the policy seed to select `k` tanks.
>
> Under the targeted strategy, it selects the `k` tanks with the highest pre-outbreak betweenness centrality.

**Show:** Lines 194-216.

> At the start of each simulated day, the model updates the management state.
>
> When the response-delay day is reached, the selected tanks become quarantined. They remain quarantined for `D` days and reopen before movement on the end day.
>
> Quarantine prevents movement into and out of the selected tanks. However, transmission can still occur among turtles already inside the same tank.

## 8b. Functionality demo (about 30 seconds)

**Do:** Run `python scripts/demo_checkpoint2.py` in the terminal and point to the "PAIRED STRATEGY COMPARISON" table and "BETWEENNESS QUARANTINE TIMELINE".

> This script runs the three strategies on the same network and the same epidemic seed.
>
> You can see that random and targeted quarantine select different tanks, start on the same day, and have the same cost of 14 tank-days. In the timeline, the two tanks are quarantined from day 2 to day 8 and reopen on day 9, and some movements are blocked during that period.
>
> This is a single seeded run. It shows that the components work together. It is not a scientific result, and we do not draw any conclusion about the strategies from it.

Do not read out or interpret the attack rate values in the table; if asked, repeat the last sentence.

## 9. Result recording

**Show:** `src/turtlefarm/model.py` line 33 (`DailyRecord`).

> The model records a daily result containing the S, I, and R counts, new infections, recoveries, attempted movements, accepted movements, blocked movements, affected tanks, and per-tank states.

**Show:** Lines 495-514 (`compute_metrics`).

> At the end of a run, it calculates final attack rate, number of affected tanks, peak infected population, time to peak, time to extinction, total simulated days, and intervention cost.
>
> These are the measurements required for our later experiment.

## 10. Validation and testing

**Show:** Expand `tests/` in Explorer.

> The tests are not the formal experiment. They verify that the implementation follows the model specification.
>
> We test that the population remains constant, each turtle belongs to exactly one tank, recovered turtles cannot become infected again, capacity is respected, quarantine blocks movement, and the same seeds reproduce the same output.
>
> We also test extreme cases such as beta equal to zero, beta equal to one, gamma equal to one, and transfer rate equal to zero or one.
>
> The current test suite contains [N] passing tests.

Use the output of `python -m pytest -q` before the meeting for `[N]`: it is 111 at `main` @ `37a7fe3`, and 136 after issue #30 is merged. If the facilitator asks for evidence, run it live and say:

> All tests pass. This supports implementation correctness, but it is not evidence for our research hypothesis.

## 11. Experiment plan

**Show:** `docs/experiment-plan.md` lines 9-18.

> Our formal experiment varies three independent variables.
>
> The first is cross-tank transfer rate, including zero and several non-zero levels.
>
> The second is response delay, representing early, intermediate, and late intervention.
>
> The third is intervention strategy: no intervention, random quarantine, or highest-betweenness quarantine.
>
> The final numerical levels will be selected after the pilot.

**Show:** Lines 51-68.

> Our two primary outcomes are final attack rate and the number of affected tanks.
>
> Supporting outcomes include peak infected population and time to extinction. We will also record intervention cost and paired differences between random and targeted quarantine.

## 12. Replication and fair comparison

**Show:** Lines 70-109.

> Because this is a stochastic model, one run is not enough.
>
> Network seeds represent different network topologies. Epidemic seeds control initial infection, movement, transmission, and recovery. Policy seeds control only random quarantine selection.
>
> Within each comparison block, the strategies will use the same network, epidemic seed, transfer rate, response delay, and intervention budget.
>
> Random and targeted quarantine will start on the same day, last for the same duration, and select the same number of tanks. The main difference is which tanks are selected.
>
> This allows us to use paired comparisons.

## 13. Pilot plan

**Show:** Lines 111-141; if issue #30 has been merged, also open the criteria table in `docs/pilot-protocol.md` §3.

> Before the formal experiment, we will run a pilot.
>
> The pilot will check whether outbreaks show useful variation, whether movement occurs often enough, whether capacity blocks too many transfers, and whether the time horizon is sufficient.
>
> The pilot is not used to select parameters that support our hypothesis. We wrote the selection criteria down before running it, and no criterion compares random with targeted quarantine.
>
> Our preliminary pilot will use five network seeds and ten epidemic seeds per network.
>
> The formal experiment is expected to use at least ten network seeds and five epidemic seeds per network. The final number will depend on runtime and observed variance.

## 14. Current progress

**Show:** `README.md` lines 14-18.

> Our current progress is as follows.
>
> We have implemented the baseline SIR model, modular network generation, network-constrained movement, quarantine strategies, daily recording, stopping rules, and reproducible random draws. These components are on the main branch and the test suite passes.
>
> This week we also implemented the batch experiment runner, which writes one raw record per run in a fixed schema, and we drafted the pilot protocol. [If issue #30 has not yet been merged, say "are under review in a pull request" instead.]
>
> The pilot itself, final parameter freezing, the formal experiment, statistical analysis, and final figures have not yet been completed.

## 15. Issues encountered

> We have encountered three main issues.
>
> First, the strategy comparison must use fair random conditions. We addressed this with event-keyed random draws, so matching agent-day events use matching draws across strategies.
>
> Second, within-day update order could allow newly infected turtles to transmit or recover immediately. We addressed this with a frozen snapshot and synchronous state updates.
>
> Third, several numerical parameters are still provisional. In particular, quarantine duration and final network parameters must be selected after the pilot.
>
> Therefore, Issues 4 and 5 remain open intentionally. Closing them before the pilot would mean choosing values without sufficient evidence.

If asked about the collaboration process: `collaboration-plan.md` §8 records that PR #27 and #29 have no cross-member review records, along with the remedial actions.

## 16. Next steps and closing

> Our next step is to confirm the pilot criteria together, run the pilot, and record all candidate settings, including the ones we reject.
>
> After the pilot, we will freeze beta, gamma, quarantine duration, network parameters, transfer-rate levels, response-delay levels, and seed lists.
>
> We will then run the paired experiments and generate statistical summaries and figures.
>
> At this checkpoint, the main model components have been implemented and tested. Our next stage is to move from model functionality to systematic experiments and analysis.
>
> Thank you. We are ready for questions.

---

# Question-and-answer responsibilities

| Member A (Cam) | Member B (Wenhao) |
|---|---|
| Why use an ABM | The three quarantine strategies |
| Network generation; `p_in` / `p_out` | Why compare random and targeted quarantine |
| Betweenness centrality | Equal budgets |
| Movement rules | network / epidemic / policy seeds |
| Infection formula | Number of replicates |
| Daily update order | Pilot purpose; output metrics |
| Why newly infected turtles cannot recover on the same day | Why issues #4 and #5 remain open; current progress and next steps |

## Member A's prepared answers

**Why an agent-based model?**

> Each turtle is in one tank and moves on its own. An equation model treats everyone as mixed together, so it cannot show tanks, bridges, or tank-level quarantine. An ABM can.

**How is the network generated?**

> For every pair of tanks we flip a coin. Same region: link with probability `p_in`, 0.6. Different regions: `p_out`, 0.05. Then we run the structural checks. If it fails, we try again, up to 100 times. Same network seed, same network.

**What is betweenness centrality?**

> It counts how often a tank lies on the shortest path between two other tanks. A high value means many routes pass through it, so it is a bridge. If two tanks tie exactly, the smaller tank ID wins, so the result is always the same.

**Movement details?**

> Turtles are processed in random order. A successful move updates the tanks straight away, so the next turtle sees the real capacity. The destination is picked evenly from the valid neighbours.

**Why that infection formula?**

> Each infectious turtle gives an independent chance beta. One minus beta is the chance to escape one of them. To the power `i_j` is the chance to escape all of them. One minus that is the chance to be infected.

**Why this update order?**

> Quarantine first, so it already applies to today's movement. Movement before transmission, so a turtle that moves today can infect its new tank today.

**Why can a newly infected turtle not recover the same day?**

> Without the snapshot, the result would depend on the order we loop over the turtles. A turtle could also be infected and recover in the same day, which makes no sense. The snapshot makes the update fair and order-independent.

## When unsure

> We have not fixed this value yet. It will be decided after the pilot, and it is recorded as an open issue.

> I will let my teammate answer this, because this part belongs to his section.

# Questions for the facilitator

After the meeting, record the answers and date in `decision-log.md` (research-plan, "Decision process"). The first three questions directly affect the pilot and analysis.

1. **Basis for parameter selection.** Beta and gamma have no real turtle data behind them. Is it acceptable to choose them from a no-intervention pilot so that outbreaks show useful variation, as long as the criteria are written down before we look at any data?
2. **Statistical methods.** For random versus targeted quarantine we use paired runs with the same seeds. Are paired differences with confidence intervals enough, or do you expect a formal test?
3. **Negative results.** If targeted quarantine turns out not to be better than random, is a negative result acceptable as long as the analysis is sound?
4. **Number of replicates.** We plan at least 10 networks times 5 epidemic seeds per condition. Is that enough, or should we justify it with a variance check?
5. **Rubric.** Has the final rubric been released? How much weight goes on model validation compared with experiment results?
6. **Model simplifications.** We use one network size and only S, I, R states. Is that acceptable as a stated limitation, or should we add a sensitivity check?
