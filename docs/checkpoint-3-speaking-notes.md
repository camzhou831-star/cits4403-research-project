# Checkpoint 3 Speaking Notes

Status: draft 2026-10-06, drafted by Member A. Member B's sections (6-9) are a suggested draft awaiting Member B's confirmation or rewrite.

Coverage: final results, changes since Checkpoint 2 (pilot, deviations and formal experiment), validation and reproduction, live demo, and work remaining before submission. Total duration is about 8-10 minutes, with 4-5 minutes per member and one handover.

> **Required checks before the meeting:**
> - The official Checkpoint 3 requirements are not recorded in the repository. Prepare using the Checkpoint 2 format (an 8-10 minute facilitator meeting), and check the LMS before the meeting; if the requirements differ, update this file first.
> - The numbers in this script come from `report/report.md` (commit `cd6a1cb`, tag `repro-2026-10-06`). If the experiment is rerun or the analysis changes, rerun `python scripts/build_report.py` and update the numbers here from the report.

## Before the meeting

```bash
git switch docs/readme-diagram-contribution && git pull   # Change to main after merging.
source .venv/bin/activate
python -m pytest -q                   # Expected: 198 passed; mention in Section 8.
python scripts/demo_final.py          # About 1 second; the last line should be "All runs identical ...: yes"
python scripts/demo_final.py --delay 1
```

Open these tabs in advance:

1. `docs/figures/concept-diagram.png`
2. `results/analysis/formal-nested/fig1-network.png`
3. `results/analysis/formal-nested/fig2-attack-rate.png`
4. `results/analysis/formal-nested/fig7-representative-runs.png`
5. Table 2 and Table 3 in `report/report.md` (rendered as tables on GitHub)
6. `results/analysis/formal-nested/fig4-paired-effects.png`
7. The "Protocol deviations" section in `docs/decision-log.md`
8. `docs/reproduction-2026-10-06.md`
9. A terminal in the repository directory with `.venv` activated and a larger font

---

# Member A — Cam (Sections 1-5, about 4.5 minutes)

## 1. Opening (about 30 seconds)

**Show:** `docs/figures/concept-diagram.png`

> Good morning. Since the last checkpoint we ran the pilot, froze the parameters, ran the formal experiment, and wrote a full draft of the report.
>
> As a reminder, this is our system. Two hundred turtles live in twenty tanks. The tanks form four regions. Inside a tank, disease spreads by SIR rules. Turtles move between tanks along network edges. A quarantined tank cannot send or receive turtles.
>
> We ask two questions. First, how do the transfer rate and the response delay change the outbreak? Second, with the same budget, is it better to quarantine the bridge tanks with the highest betweenness, or random tanks?

## 2. Pilot and frozen parameters (about 60 seconds)

**Show:** The "Parameter freeze record" table in `docs/decision-log.md`.

> We chose the parameters with a two-stage pilot. We wrote the selection rules before we saw any pilot data, and the pilot never compared the two strategies.
>
> The pilot chose beta 0.2 and gamma 0.1, so a turtle is infectious for about ten days. The transfer rates are 0, 0.01, 0.025 and 0.1 per turtle per day. The response delays are 1, 12 and 33 days. The quarantine closes two tanks for fourteen days, so both strategies cost twenty-eight tank-days.

## 3. Deviations and corrections (about 60 seconds)

**Show:** The "Protocol deviations" section in `docs/decision-log.md`.

> We want to be open about four places where we did not follow our own plan.
>
> One. The pilot ran before both of us had signed the protocol, because of the deadline.
>
> Two. In the first pilot round, no parameter set passed one rule, so we added a transfer level of 0.025 and ran the round again.
>
> Three. We changed the denominator of one duration check after seeing the data. Review then found that the counter mixed capacity blocks with quarantine blocks. We defined separate counters, added them and reran the pilot. The earlier simulation outcomes stayed the same. At fourteen days, the quarantine rules intercepted a movement attempt in about ninety-six percent of runs where quarantine started, so fourteen days passes our operational check and the other two checks. This does not prove that those moves would all have succeeded without quarantine: some would still fail because the other tanks were full.
>
> Four. Our first formal run used the same five epidemic seeds in every network. That made the networks correlated, so the confidence intervals were too narrow. We ran it again with one hundred separate seeds, and we report the new run. We kept the old one and compare the two in the report.
>
> Every change is written in the decision log with the original result.

## 4. Result 1: transfer rate (about 60 seconds)

**Show:** `results/analysis/formal-nested/fig2-attack-rate.png`, then `fig7-representative-runs.png`.

> The formal experiment has 5,200 runs. None failed, and none hit the 365-day limit.
>
> The transfer rate is the strongest factor. Without any quarantine, the final attack rate goes from 5 percent at rate zero, to 16 percent at 0.01, to 52 percent at 0.025, and 97 percent at 0.1.
>
> **[Switch to fig7]** The reason is spread between regions. At 0.01, about a third of outbreaks leave their first region. At 0.025, about four out of five do. Here on the right, the infection peaks in region zero first, and only weeks later it reaches regions one and three.
>
> So our first hypothesis is supported.

## 5. Result 2: delay and strategy (about 60 seconds), then handover

**Show:** Table 2 in `report/report.md`, then `fig4-paired-effects.png`.

> The quarantine itself has a small effect. Two tanks for fourteen days lowers the attack rate by at most about 11 percent.
>
> But there is an interesting pattern at transfer rate 0.025. Targeted quarantine keeps its effect when the response is late: about 10 percent at every delay. Random quarantine loses it: from about 8 percent at day 1 to 2 percent at day 33. We call this a descriptive pattern, because we did not plan this test before.
>
> **[Switch to fig4]** When we compare targeted with random directly, only one condition out of nine has an interval that excludes zero: transfer rate 0.025 with a 33-day delay, where the attack rate is about 4 points lower. Even there, targeted is worse in one third of the blocks. So we cannot say that targeted quarantine is better in general.
>
> Wenhao will now show a live run and how we checked the model.

---

# Member B — Wenhao (Sections 6-9, about 4.5 minutes; suggested draft awaiting confirmation)

## 6. Quarantine implementation (about 45 seconds)

**Show:** `results/analysis/formal-nested/fig1-network.png`

> This is one real network from the experiment. Colour shows the region, and node size shows betweenness. The black rings are the two tanks that targeted quarantine closes. Tank 19 is the only link between region 3 and region 2.
>
> In our code, the selection happens before the outbreak and uses only the network, never the infection state. Random quarantine uses its own policy seed. A quarantined tank blocks moves in and out, but disease inside it continues.

## 7. Live demo (about 90 seconds)

**Do:** Run `python scripts/demo_final.py` in the terminal.

> This script reruns one block of the formal experiment live. It is the cross-region outbreak from figure 7, so it was not chosen because one strategy looks good.
>
> Each row is one strategy with the same random draws. With a 33-day delay, targeted quarantine closes tanks 9 and 19, and the attack rate is 0.475. The three random choices give between 0.625 and 0.9.
>
> The last column checks every run against the stored result of the formal experiment, and they are identical.

**Do:** Run `python scripts/demo_final.py --delay 1`.

> Now the same outbreak with a one-day delay. This time targeted quarantine is much worse than random. So one block can point either way, and that is why we use a hundred blocks per condition and confidence intervals, not single runs.

## 8. Validation and reproduction (about 60 seconds)

**Show:** The comparison table in `docs/reproduction-2026-10-06.md`.

> We have 198 automated tests. They check the invariants, for example that the number of turtles stays two hundred and that no tank goes over capacity, and they check extreme cases. Both of us also traced a small three-tank example by hand and matched it to the code.
>
> The invariants are also checked on every day of every run. None of the more than twenty thousand pilot and formal runs failed.
>
> We also used Codex CLI for two rounds of review. It recomputed the numbers in our report independently, and all of them matched.
>
> Finally, we cloned the repository into a new folder and ran everything from zero. We got the same results, the same figures, and the same report. This check also found one bug in a figure, which we fixed.

## 9. Remaining work and questions (about 45 seconds)

> Before the deadline we still need to: review and merge the last two pull requests, put the report into the required format, and prepare the final demo.
>
> We have three questions for you.

**Ask the facilitator:**

1. Is the deadline 1:59 pm or 11:59 pm on Friday, and what exactly should we submit: a PDF report, the repository link, or both?
2. Is there a page limit for the report?
3. What format will the Week 12 demo have, and how long is it?

---

# Question-and-answer responsibilities

| Member A (Cam) | Member B (Wenhao) |
|---|---|
| Research questions, pilot and parameter selection, reasons for protocol deviations | Quarantine implementation, movement rules, betweenness selection |
| Statistical methods: pairing, bootstrap, reasons for rerunning | Tests, invariants, hand trace, demo script |
| Report content and limitations | Reproduction process, GitHub workflow |

## Prepared answers

**Q: Why is targeted quarantine not clearly better?**

> With only two tanks for fourteen days, the quarantine is small compared with the whole system, so the differences are small and the intervals are wide. The literature found bridge targeting works well in networks with strong community structure. Our networks have about eight links between regions, so closing two tanks may not cut a region off. We think this is one reason, but we did not test it.

**Q: In the demo, why can random quarantine make things worse than no quarantine?**

> A quarantine changes which neighbour tanks are open, so turtles that move are sent along different paths. Sometimes that sends infection somewhere it would not have gone. The model does not stop all movement, only movement through the closed tanks.

**Q: Did you change rules to get the result you wanted?**

> The pilot did not compare strategies to choose favourable outcomes. We did make changes after seeing data, and we kept the original results and recorded those changes. The original all-runs proxy did not pass. Later, the rule-attribution counters passed the operational Q1 check using a started-runs denominator, and the selected duration was fourteen days, the setting already used. This is not a counterfactual proof of additional transfers prevented. Analyses added after seeing results are disclosed in the report.

**Q: Why did you rerun the formal experiment?**

> In the first run, every network used the same five epidemic seeds, so all networks started from the same infected turtle with the same random draws. That gave only five independent outbreaks. Our plan said seeds should be nested in networks, so we fixed it. The old run had seven significant cells; the correct run has two. That shows the first run was too confident.

**Q: How did you use AI tools?**

> We used Claude Code to help write code and documents, and Codex CLI to review them. The README explains how we used them. We checked every suggestion ourselves, and we can explain all of the code.

**Q: Who did what?**

> The contribution table in `docs/collaboration-plan.md` lists each task, its owner and its reviewer from the GitHub record. For example, the movement and quarantine code was written by Wenhao, and the network, runner and analysis by Cam.

## When unsure

> We are not sure about that detail. We will check it in the code and reply after the meeting.

Do not guess numbers during the meeting; use `report/report.md` as the source for all numbers.
