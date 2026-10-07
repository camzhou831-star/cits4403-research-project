# Checkpoint 2 Speaking Notes

Status：draft 2026-09-20，Member A 起草；Member B 的 sections（8-16）来自组内讲稿，待 Member B 确认或修改。

汇报内容：模型主要组件、实验计划、当前进展、问题和下一步。总时长约 8-10 分钟，每人 4-5 分钟，中间只交接一次。

> 官方 Checkpoint 2 要求和 rubric 在仓库中没有记录（README “Current stage and gates” 第 5 条）。会前在 LMS 核对一次；若要求不同，先改本文件。

行号核对基准：`main` @ `37a7fe3` 之后 `turtlefarm/config.py`、`entities.py`、`network.py`、`model.py`、`docs/experiment-plan.md` 和 README 第 1-37 行均未改动。在 GitHub 网页上打开文件后按 `y` 可把链接固定到当前 commit。

## 会前检查

```bash
git switch main && git pull          # 本地落后时行号会对不上
python -m pytest -q                  # 记下通过数，Section 10 要念
python scripts/demo_checkpoint2.py   # 确认 demo 能跑，约 1 秒
```

提前打开的 tabs：`README.md`（网页上用 `?plain=1` 才显示行号）、`turtlefarm/config.py`、`entities.py`、`network.py`、`model.py`、`docs/experiment-plan.md`、一个已进入仓库目录并激活 `.venv` 的终端。

---

# Member A — Cam（Sections 1-7）

## 1. 开场与研究问题（约 40 秒）

**Show：** `README.md` 第 20-37 行（第 20-27 行是中文，主要停在第 29-37 行的英文研究问题）。

> Good morning. Today we will show our model, our experiment plan, our progress, and our open issues.
>
> Our project is about how a disease spreads in a turtle farm. The farm is not real. It is a simple model to help us understand spread, not to predict a real disease.
>
> We have 200 turtles, 20 tanks, and 4 regions. Each turtle is susceptible, infectious, or recovered. The tanks are joined in a network, and turtles can only move along the links.
>
> Our main question is: how do the transfer rate and the response delay change the outbreak size and the number of affected tanks?
>
> Our second question is: with the same budget, is it better to quarantine the high-betweenness tanks, or random tanks?

## 2. 仓库结构（约 20 秒）

**Show：** 仓库首页，依次指 `turtlefarm`、`scripts`、`tests`、`docs`。

> The repository has four parts. `turtlefarm` is the model code. `scripts` has demos and checking tools. `tests` checks that the code is correct. `docs` has the model specification, the experiment plan, and our decisions.
>
> I will start with the model code.

## 3. 参数（约 60 秒）

**Show：** `turtlefarm/config.py` 第 13 行。

> We have three strategies: no quarantine, random quarantine, and highest-betweenness quarantine.

**Show：** 第 17-26 行。

> The system has 200 turtles, 20 tanks, 4 regions, and one infected turtle at the start. Each tank starts with 10 turtles and can hold 12. The quarantine picks 2 tanks. A run stops after 365 days at most.

**Show：** 第 46-71 行。

> Beta is the chance of infection inside a tank. Gamma is the chance of recovery each day.
>
> `p_in` and `p_out` build the network. Two tanks in the same region are much more likely to be linked than two tanks in different regions.
>
> Transfer rate is how often a turtle tries to move. Response delay is the day quarantine starts. Quarantine duration is how long it lasts. `k` is how many tanks we quarantine.
>
> The three seeds make every run repeatable.

**Show：** 第 78 行（`PROVISIONAL_FIELDS`）。

> Some values are not final yet: beta, gamma, quarantine duration, `p_in` and `p_out`. We will fix them after the pilot, not from one demo run.

## 4. Agent 和 Tank（约 25 秒）

**Show：** `turtlefarm/entities.py` 第 7-31 行。

> This file defines our two entities.
>
> A turtle knows which tank it is in, and its disease state: S, I, or R.
>
> A tank knows its region, its capacity, whether it is open or quarantined, when the quarantine starts and ends, and which turtles are inside.

## 5. 网络（约 50 秒）

**Show：** `turtlefarm/network.py` 顶部。

> Tanks are the nodes of a fixed network. A link means turtles can move between those two tanks.
>
> Links are common inside a region and rare between regions. So the network has clusters, and a few tanks act as bridges between regions.

**Show：** 第 51-69 行（`structural_rejection_reason`）。

> We reject a network if it is not connected, if it has no link between regions, if every tank is linked to every other tank, or if all tanks have the same betweenness. These checks make sure that "bridge tank" really means something.

**Show：** 第 127-132 行（`ranking` / `top_k`）。

> We rank tanks by betweenness before the outbreak starts. The targeted strategy takes the top `k`. It only uses the network. It never uses information about the future outbreak.

## 6. 每日运行规则（约 90 秒）

**Show：** `turtlefarm/model.py` 第 429-443 行（`step()`），逐行指第 431-437 行。

> This function is one simulated day.
>
> First the day number goes up. Then we update quarantine. Then turtles move. Then we work out infection and recovery. Then we apply the changes. Then we check that nothing is broken. Last, we record the day.
>
> The `run()` method below just calls `step()` again and again, until no turtle is infectious or we reach the maximum number of days.

**Show：** 第 224-275 行（`_movement_stage`），可指第 244 行和第 254-259 行。

> For movement, each turtle gets a random number. If it is smaller than the transfer rate, the turtle tries to move.
>
> The destination must be a neighbour in the network, it must be open, and it must have space.
>
> If the turtle's own tank is quarantined, or there is no valid destination, the move is blocked.

**Show：** 第 277-307 行（`_transmission_and_recovery`），指第 296 行 `p = 1.0 - (1.0 - cfg.beta) ** i_j`。

> For infection and recovery, we first take a snapshot of who is infectious today.
>
> If a susceptible turtle shares a tank with `i_j` infectious turtles, its chance of infection is one minus, one minus beta, to the power `i_j`.
>
> Each infectious turtle recovers with chance gamma.
>
> Because we use the snapshot, a turtle infected today cannot infect others or recover until tomorrow.

## 7. 交接

> That is how the model is built and how one day works. Wenhao will now explain the quarantine strategies, the outputs, the tests, the experiment plan, and our progress.

---

# Member B — Wenhao（Sections 8-16）

## 8. 隔离策略

**Show：** `turtlefarm/model.py` 第 173-187 行。

> I will first explain how the intervention strategies are implemented.
>
> Under no intervention, no tank is selected.
>
> Under random quarantine, the model uses the policy seed to select `k` tanks.
>
> Under the targeted strategy, it selects the `k` tanks with the highest pre-outbreak betweenness centrality.

**Show：** 第 194-216 行。

> At the start of each simulated day, the model updates the management state.
>
> When the response-delay day is reached, the selected tanks become quarantined. They remain quarantined for `D` days and reopen before movement on the end day.
>
> Quarantine prevents movement into and out of the selected tanks. However, transmission can still occur among turtles already inside the same tank.

## 8b. 功能演示（约 30 秒）

**Do：** 在终端运行 `python scripts/demo_checkpoint2.py`，指 “PAIRED STRATEGY COMPARISON” 表和 “BETWEENNESS QUARANTINE TIMELINE”。

> This script runs the three strategies on the same network and the same epidemic seed.
>
> You can see that random and targeted quarantine select different tanks, start on the same day, and have the same cost of 14 tank-days. In the timeline, the two tanks are quarantined from day 2 to day 8 and reopen on day 9, and some movements are blocked during that period.
>
> This is a single seeded run. It shows that the components work together. It is not a scientific result, and we do not draw any conclusion about the strategies from it.

不要念或解读表中的 attack rate 数值；若被问到，重复最后一句。

## 9. 结果记录

**Show：** `turtlefarm/model.py` 第 33 行（`DailyRecord`）。

> The model records a daily result containing the S, I, and R counts, new infections, recoveries, attempted movements, accepted movements, blocked movements, affected tanks, and per-tank states.

**Show：** 第 495-514 行（`compute_metrics`）。

> At the end of a run, it calculates final attack rate, number of affected tanks, peak infected population, time to peak, time to extinction, total simulated days, and intervention cost.
>
> These are the measurements required for our later experiment.

## 10. 验证和测试

**Show：** Explorer 中展开 `tests/`。

> The tests are not the formal experiment. They verify that the implementation follows the model specification.
>
> We test that the population remains constant, each turtle belongs to exactly one tank, recovered turtles cannot become infected again, capacity is respected, quarantine blocks movement, and the same seeds reproduce the same output.
>
> We also test extreme cases such as beta equal to zero, beta equal to one, gamma equal to one, and transfer rate equal to zero or one.
>
> The current test suite contains [N] passing tests.

`[N]` 以会前 `python -m pytest -q` 的输出为准：`main` @ `37a7fe3` 为 111；issue #30 合入后为 136。若 facilitator 要求证明，现场运行并说：

> All tests pass. This supports implementation correctness, but it is not evidence for our research hypothesis.

## 11. 实验计划

**Show：** `docs/experiment-plan.md` 第 9-18 行。

> Our formal experiment varies three independent variables.
>
> The first is cross-tank transfer rate, including zero and several non-zero levels.
>
> The second is response delay, representing early, intermediate, and late intervention.
>
> The third is intervention strategy: no intervention, random quarantine, or highest-betweenness quarantine.
>
> The final numerical levels will be selected after the pilot.

**Show：** 第 51-68 行。

> Our two primary outcomes are final attack rate and the number of affected tanks.
>
> Supporting outcomes include peak infected population and time to extinction. We will also record intervention cost and paired differences between random and targeted quarantine.

## 12. 重复实验和公平比较

**Show：** 第 70-109 行。

> Because this is a stochastic model, one run is not enough.
>
> Network seeds represent different network topologies. Epidemic seeds control initial infection, movement, transmission, and recovery. Policy seeds control only random quarantine selection.
>
> Within each comparison block, the strategies will use the same network, epidemic seed, transfer rate, response delay, and intervention budget.
>
> Random and targeted quarantine will start on the same day, last for the same duration, and select the same number of tanks. The main difference is which tanks are selected.
>
> This allows us to use paired comparisons.

## 13. Pilot 计划

**Show：** 第 111-141 行；若 issue #30 已合入，再打开 `docs/pilot-protocol.md` §3 的标准表。

> Before the formal experiment, we will run a pilot.
>
> The pilot will check whether outbreaks show useful variation, whether movement occurs often enough, whether capacity blocks too many transfers, and whether the time horizon is sufficient.
>
> The pilot is not used to select parameters that support our hypothesis. We wrote the selection criteria down before running it, and no criterion compares random with targeted quarantine.
>
> Our preliminary pilot will use five network seeds and ten epidemic seeds per network.
>
> The formal experiment is expected to use at least ten network seeds and five epidemic seeds per network. The final number will depend on runtime and observed variance.

## 14. 当前进展

**Show：** `README.md` 第 14-18 行。

> Our current progress is as follows.
>
> We have implemented the baseline SIR model, modular network generation, network-constrained movement, quarantine strategies, daily recording, stopping rules, and reproducible random draws. These components are on the main branch and the test suite passes.
>
> This week we also implemented the batch experiment runner, which writes one raw record per run in a fixed schema, and we drafted the pilot protocol. [若 issue #30 尚未合入，改说 "are under review in a pull request"。]
>
> The pilot itself, final parameter freezing, the formal experiment, statistical analysis, and final figures have not yet been completed.

## 15. 遇到的问题

> We have encountered three main issues.
>
> First, the strategy comparison must use fair random conditions. We addressed this with event-keyed random draws, so matching agent-day events use matching draws across strategies.
>
> Second, within-day update order could allow newly infected turtles to transmit or recover immediately. We addressed this with a frozen snapshot and synchronous state updates.
>
> Third, several numerical parameters are still provisional. In particular, quarantine duration and final network parameters must be selected after the pilot.
>
> Therefore, Issues 4 and 5 remain open intentionally. Closing them before the pilot would mean choosing values without sufficient evidence.

若被问到协作流程：`collaboration-plan.md` §8 如实记录了 PR #27、#29 没有跨成员 review 记录，以及补救措施。

## 16. 下一步和结尾

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

# 问答分工

| Member A（Cam） | Member B（Wenhao） |
|---|---|
| 为什么使用 ABM | 三种隔离策略 |
| 网络如何生成；`p_in` / `p_out` | 为什么比较 random 和 targeted |
| Betweenness centrality | 公平预算 |
| 移动规则 | network / epidemic / policy seeds |
| 感染公式 | 重复实验数量 |
| 每日更新顺序 | Pilot 目的；输出指标 |
| 为什么新感染者当天不康复 | 为什么 issues #4、#5 仍然开放；当前进展和下一步 |

## Member A 的准备答复

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

## 不确定时

> We have not fixed this value yet. It will be decided after the pilot, and it is recorded as an open issue.

> I will let my teammate answer this, because this part belongs to his section.

# 向 facilitator 提的问题

会后把答复和日期写入 `decision-log.md`（research-plan “Decision process”）。前三个会直接影响 pilot 和分析。

1. **参数选择依据。** Beta and gamma have no real turtle data behind them. Is it acceptable to choose them from a no-intervention pilot so that outbreaks show useful variation, as long as the criteria are written down before we look at any data?
2. **统计方法。** For random versus targeted quarantine we use paired runs with the same seeds. Are paired differences with confidence intervals enough, or do you expect a formal test?
3. **负面结果。** If targeted quarantine turns out not to be better than random, is a negative result acceptable as long as the analysis is sound?
4. **重复次数。** We plan at least 10 networks times 5 epidemic seeds per condition. Is that enough, or should we justify it with a variance check?
5. **Rubric。** Has the final rubric been released? How much weight goes on model validation compared with experiment results?
6. **模型简化。** We use one network size and only S, I, R states. Is that acceptable as a stated limitation, or should we add a sensitivity check?
