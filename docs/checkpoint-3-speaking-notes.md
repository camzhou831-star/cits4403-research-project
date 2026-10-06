# Checkpoint 3 Speaking Notes

Status：draft 2026-10-06，Member A 起草。Member B 的 sections（6-9）是建议稿，待 Member B 确认或改写。

汇报内容：最终结果、相对 Checkpoint 2 的变化（pilot、偏离、正式实验）、验证与复现、现场演示、提交前的剩余工作。总时长约 8-10 分钟，每人 4-5 分钟，中间只交接一次。

> **会前必须核对：**
> - Checkpoint 3 的官方要求在仓库中没有记录，按 Checkpoint 2 的格式（facilitator 面谈，8-10 分钟）准备，会前在 LMS 核对一次；若要求不同，先改本文件。
> - 讲稿中的数字取自 `report/report.md`（commit `cd6a1cb`，tag `repro-2026-10-06`）。若之后重新运行或修改分析，重新运行 `python scripts/build_report.py`，并按报告更新这里的数字。

## 会前检查

```bash
git switch docs/readme-diagram-contribution && git pull   # 合并后改为 main
source .venv/bin/activate
python -m pytest -q                   # Expected: 183 passed; mention in Section 8.
python scripts/demo_final.py          # 约 1 秒；最后一行应为 "All runs identical ...: yes"
python scripts/demo_final.py --delay 1
```

提前打开的 tabs：

1. `docs/figures/concept-diagram.png`
2. `results/analysis/formal-nested/fig1-network.png`
3. `results/analysis/formal-nested/fig2-attack-rate.png`
4. `results/analysis/formal-nested/fig7-representative-runs.png`
5. `report/report.md` 的 Table 2 和 Table 3（GitHub 网页上渲染为表格）
6. `results/analysis/formal-nested/fig4-paired-effects.png`
7. `docs/decision-log.md` 的 “Protocol deviations” 节
8. `docs/reproduction-2026-10-06.md`
9. 一个已进入仓库目录并激活 `.venv` 的终端，字体调大

---

# Member A — Cam（Sections 1-5，约 4.5 分钟）

## 1. 开场（约 30 秒）

**Show：** `docs/figures/concept-diagram.png`

> Good morning. Since the last checkpoint we ran the pilot, froze the parameters, ran the formal experiment, and wrote a full draft of the report.
>
> As a reminder, this is our system. Two hundred turtles live in twenty tanks. The tanks form four regions. Inside a tank, disease spreads by SIR rules. Turtles move between tanks along network edges. A quarantined tank cannot send or receive turtles.
>
> We ask two questions. First, how do the transfer rate and the response delay change the outbreak? Second, with the same budget, is it better to quarantine the bridge tanks with the highest betweenness, or random tanks?

## 2. Pilot 和冻结的参数（约 60 秒）

**Show：** `docs/decision-log.md` 的 “Parameter freeze record” 表。

> We chose the parameters with a two-stage pilot. We wrote the selection rules before we saw any pilot data, and the pilot never compared the two strategies.
>
> The pilot chose beta 0.2 and gamma 0.1, so a turtle is infectious for about ten days. The transfer rates are 0, 0.01, 0.025 and 0.1 per turtle per day. The response delays are 1, 12 and 33 days. The quarantine closes two tanks for fourteen days, so both strategies cost twenty-eight tank-days.

## 3. 偏离和修正（约 60 秒）

**Show：** `docs/decision-log.md` 的 “Protocol deviations” 节。

> We want to be open about four places where we did not follow our own plan.
>
> One. The pilot ran before both of us had signed the protocol, because of the deadline.
>
> Two. In the first pilot round, no parameter set passed one rule, so we added a transfer level of 0.025 and ran the round again.
>
> Three. We changed the denominator of one duration check after seeing the data. Review then found that the counter mixed capacity blocks with quarantine blocks, so it could not measure that check. We wrote down a cause-specific definition first, then added the counters and reran the pilot. Every earlier result came out identical, and quarantine blocked a transfer in about ninety-six percent of runs at fourteen days, so fourteen days now passes all three checks.
>
> Four. Our first formal run used the same five epidemic seeds in every network. That made the networks correlated, so the confidence intervals were too narrow. We ran it again with one hundred separate seeds, and we report the new run. We kept the old one and compare the two in the report.
>
> Every change is written in the decision log with the original result.

## 4. 结果一：transfer rate（约 60 秒）

**Show：** `results/analysis/formal-nested/fig2-attack-rate.png`，然后 `fig7-representative-runs.png`。

> The formal experiment has 5,200 runs. None failed, and none hit the 365-day limit.
>
> The transfer rate is the strongest factor. Without any quarantine, the final attack rate goes from 5 percent at rate zero, to 16 percent at 0.01, to 52 percent at 0.025, and 97 percent at 0.1.
>
> **[切到 fig7]** The reason is spread between regions. At 0.01, about a third of outbreaks leave their first region. At 0.025, about four out of five do. Here on the right, the infection peaks in region zero first, and only weeks later it reaches regions one and three.
>
> So our first hypothesis is supported.

## 5. 结果二：delay 和策略（约 60 秒），然后交接

**Show：** `report/report.md` 的 Table 2，然后 `fig4-paired-effects.png`。

> The quarantine itself has a small effect. Two tanks for fourteen days lowers the attack rate by at most about 11 percent.
>
> But there is an interesting pattern at transfer rate 0.025. Targeted quarantine keeps its effect when the response is late: about 10 percent at every delay. Random quarantine loses it: from about 8 percent at day 1 to 2 percent at day 33. We call this a descriptive pattern, because we did not plan this test before.
>
> **[切到 fig4]** When we compare targeted with random directly, only one condition out of nine has an interval that excludes zero: transfer rate 0.025 with a 33-day delay, where the attack rate is about 4 points lower. Even there, targeted is worse in one third of the blocks. So we cannot say that targeted quarantine is better in general.
>
> Wenhao will now show a live run and how we checked the model.

---

# Member B — Wenhao（Sections 6-9，约 4.5 分钟；建议稿，待确认）

## 6. 隔离怎么实现（约 45 秒）

**Show：** `results/analysis/formal-nested/fig1-network.png`

> This is one real network from the experiment. Colour shows the region, and node size shows betweenness. The black rings are the two tanks that targeted quarantine closes. Tank 19 is the only link between region 3 and region 2.
>
> In our code, the selection happens before the outbreak and uses only the network, never the infection state. Random quarantine uses its own policy seed. A quarantined tank blocks moves in and out, but disease inside it continues.

## 7. 现场演示（约 90 秒）

**Do：** 终端运行 `python scripts/demo_final.py`

> This script reruns one block of the formal experiment live. It is the cross-region outbreak from figure 7, so it was not chosen because one strategy looks good.
>
> Each row is one strategy with the same random draws. With a 33-day delay, targeted quarantine closes tanks 9 and 19, and the attack rate is 0.475. The three random choices give between 0.625 and 0.9.
>
> The last column checks every run against the stored result of the formal experiment, and they are identical.

**Do：** 运行 `python scripts/demo_final.py --delay 1`

> Now the same outbreak with a one-day delay. This time targeted quarantine is much worse than random. So one block can point either way, and that is why we use a hundred blocks per condition and confidence intervals, not single runs.

## 8. 验证和复现（约 60 秒）

**Show：** `docs/reproduction-2026-10-06.md` 的比对表。

> We have 183 automated tests. They check the invariants, for example that the number of turtles stays two hundred and that no tank goes over capacity, and they check extreme cases. Both of us also traced a small three-tank example by hand and matched it to the code.
>
> The invariants are also checked on every day of every run. None of the more than twenty thousand pilot and formal runs failed.
>
> We also used Codex CLI for two rounds of review. It recomputed the numbers in our report independently, and all of them matched.
>
> Finally, we cloned the repository into a new folder and ran everything from zero. We got the same results, the same figures, and the same report. This check also found one bug in a figure, which we fixed.

## 9. 剩余工作和问题（约 45 秒）

> Before the deadline we still need to: review and merge the last two pull requests, put the report into the required format, and prepare the final demo.
>
> We have three questions for you.

**Ask（向 facilitator 提问）：**

1. Is the deadline 1:59 pm or 11:59 pm on Friday, and what exactly should we submit: a PDF report, the repository link, or both?
2. Is there a page limit for the report?
3. What format will the Week 12 demo have, and how long is it?

---

# 问答分工

| Member A（Cam） | Member B（Wenhao） |
|---|---|
| 研究问题、pilot 和参数选择、偏离协议的原因 | 隔离实现、movement 规则、betweenness 选择 |
| 统计方法：配对、bootstrap、为什么重跑 | 测试、不变量、hand trace、demo 脚本 |
| 报告内容和限制 | 复现过程、GitHub 流程 |

## 准备答复

**Q: Why is targeted quarantine not clearly better?**

> With only two tanks for fourteen days, the quarantine is small compared with the whole system, so the differences are small and the intervals are wide. The literature found bridge targeting works well in networks with strong community structure. Our networks have about eight links between regions, so closing two tanks may not cut a region off. We think this is one reason, but we did not test it.

**Q: In the demo, why can random quarantine make things worse than no quarantine?**

> A quarantine changes which neighbour tanks are open, so turtles that move are sent along different paths. Sometimes that sends infection somewhere it would not have gone. The model does not stop all movement, only movement through the closed tanks.

**Q: Did you change rules to get the result you wanted?**

> No. The rules we changed were about choosing parameters, and the pilot never compared strategies. For each change we kept the original result, and for the quarantine duration both versions give fourteen days. The one analysis we added after seeing results is labelled as descriptive in the report.

**Q: Why did you rerun the formal experiment?**

> In the first run, every network used the same five epidemic seeds, so all networks started from the same infected turtle with the same random draws. That gave only five independent outbreaks. Our plan said seeds should be nested in networks, so we fixed it. The old run had seven significant cells; the correct run has two. That shows the first run was too confident.

**Q: How did you use AI tools?**

> We used Claude Code to help write code and documents, and Codex CLI to review them. The README explains how we used them. We checked every suggestion ourselves, and we can explain all of the code.

**Q: Who did what?**

> The contribution table in `docs/collaboration-plan.md` lists each task, its owner and its reviewer from the GitHub record. For example, the movement and quarantine code was written by Wenhao, and the network, runner and analysis by Cam.

## 不确定时

> We are not sure about that detail. We will check it in the code and reply after the meeting.

不要现场猜测数字；所有数字以 `report/report.md` 为准。
