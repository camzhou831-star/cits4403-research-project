# Week 12 demo videos

Two silent videos for voice-over, 1280×720:

| Version | Covers | Files | Rendered by |
|---|---|---|---|
| **3 minutes** (main) | The whole project in eight sections | [`demo-3min.mp4`](../results/demo/demo-3min.mp4), [`demo-3min.gif`](../results/demo/demo-3min.gif) | `python scripts/make_demo_video_3min.py` (about 1 min) |
| 30 seconds | One example block and the headline results | [`demo-30s.mp4`](../results/demo/demo-30s.mp4), [`demo-30s.gif`](../results/demo/demo-30s.gif) | `python scripts/make_demo_video.py` |

Both need `ffmpeg`. The 3-minute video runs `pytest` and `scripts/demo_final.py` while it renders and shows their real output. It reads the pilot table from `results/pilot/stage2-criteria.csv` and the headline numbers from `report/report.md`, and it stops if the report no longer states them.

## 3-minute version

![3-minute demo](../results/demo/demo-3min.gif)

### Narration (about 420 words, at about 140 words per minute)

| Time | Section | Say |
|---|---|---|
| 0:00-0:15 | 1 Question | Turtle farms move animals between tanks, and those transfers can carry an outbreak into other parts of the farm. Our question: with a budget of two tanks for fourteen days, which tanks should we quarantine, and does it matter when? |
| 0:15-0:45 | 2 Model | We built an agent-based model. Two hundred turtles live in twenty tanks, grouped into four regions. Tanks are linked by a random network, dense inside a region and sparse between regions. Each day, quarantine is updated, turtles try to move along the network, infection spreads only inside a tank, and infected turtles recover. A quarantined tank blocks transfers in and out, but infection inside it continues. |
| 0:45-1:05 | 3 Verification | We check the model with one hundred and ninety-eight automated tests. They check invariants every day, extreme cases, and a three-tank example traced by hand. Random draws are keyed to events, so every strategy sees the same outbreak until quarantine starts. Here we rerun one block, and all runs match the stored records exactly. |
| 1:05-1:30 | 4 Parameter selection | A two-stage pilot fixed the parameters before the main experiment. Stage one chose the disease rates and transfer levels. Stage two chose the quarantine length with three criteria. Our first check counted capacity blocks as well, so we registered a quarantine-only counter, reran the pilot with identical results, and fourteen days passed all three criteria. |
| 1:30-1:50 | 5 Experiment design | The experiment uses twenty networks with five outbreak seeds each: one hundred paired blocks per transfer rate. Every strategy in a block shares the same seeds, so we compare them within the block. Confidence intervals come from a bootstrap that resamples whole networks. In total, five thousand two hundred runs. |
| 1:50-2:20 | 6 One example | Here is one block. The same outbreak runs three times. On day thirty-three, targeted quarantine closes the two best-connected tanks, and random quarantine closes two others. In this run, targeting cut the attack rate from sixty-one to forty-seven percent, while random closure did not help. But this is only one block. |
| 2:20-2:50 | 7 Results | Across all blocks, transfer rate dominates: going from 0.01 to 0.025 multiplies the attack rate by three point three. The quarantine budget cuts it by at most about eleven percent. Targeted against random, only two of eighteen intervals exclude zero, so we found no consistent advantage for targeting. |
| 2:50-3:00 | 8 Limits | The system is synthetic, with one budget and one disease regime. Every number here can be regenerated from the repository with three commands. |

## 30-second version

![30-second demo](../results/demo/demo-30s.gif)

One paired block of `formal-nested`, the same one `scripts/demo_final.py` reruns: network 211, epidemic seed 20059, transfer rate 0.025, response delay 33 days. The block was picked by a rule on the no-intervention run only (figure 7). The random arm shown is the policy seed with the median attack rate of the three random arms (seed 1000), not the worst one. The 3-minute version reuses this animation in section 6.

| Arm | Attack rate | Tanks hit |
|---|---|---|
| No quarantine | 0.610 | 11 |
| Targeted (tanks 9, 19) | 0.475 | 9 |
| Random (tanks 3, 10) | 0.670 | 13 |

This block favours targeting much more than the average; the narration says so.

| Time | Screen | Say |
|---|---|---|
| 0-3 s | Title | Two hundred turtles live in twenty tanks, and transfers carry infection between them. |
| 3-13 s | Days 0-58; quarantine appears on day 33 (at about 9 s) | Here is one outbreak, run three times with identical random draws. On day thirty-three we close two tanks for fourteen days: either the best-connected tanks, or two at random. |
| 13-23 s | Days 58-115 | In this run, closing the bridge tanks cut the attack rate from sixty-one to forty-seven percent. Random closure did not help. |
| 23-30 s | Results card | But over a hundred blocks per condition, targeting showed no consistent advantage. The transfer rate mattered far more. |
