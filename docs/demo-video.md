# Week 12 demo video and presentation script

![3-minute demo](../results/demo/demo-3min.gif)

Video: [`demo-3min.mp4`](../results/demo/demo-3min.mp4) (3:00, 1280×720, silent). It plays during the presentation while the presenter speaks. Regenerate it with `python scripts/make_demo_video.py` (about 1 min, needs `ffmpeg`).

The video runs `pytest` and `scripts/demo_final.py` while it renders and shows their real output. The pilot table comes from `results/pilot/stage2-criteria.csv`. The headline numbers come from `report/report.md`, and the script stops if the report no longer states them.

## Presentation script

About 450 words, which takes three minutes at a steady pace. Each section matches what is on screen. The bar at the bottom of the video shows which section is playing, so if you fall behind, skip to the first sentence of the next section.

### 1. Question (0:00-0:15)

> 画面：标题。要点：问题和预算。

Turtle farms move animals between tanks, and those transfers can carry an outbreak into other parts of the farm. Our question is this: if we can only quarantine two tanks for fourteen days, which two should we choose, and does it matter when we act?

### 2. Model (0:15-0:45)

> 画面：概念图。先指左边的网络，再指右边的每日步骤。

We built an agent-based model. Two hundred turtles live in twenty tanks, grouped into four regions. The tanks are linked by a random network that is dense inside a region and sparse between regions.

Each day, quarantine is updated, turtles try to move along the network, infection spreads inside each tank, and infected turtles recover. A quarantined tank blocks transfers in and out, but infection inside it carries on.

### 3. Verification (0:45-1:05)

> 画面：终端输出。要点：198 个测试；最后一行 "identical: yes"。

To check the model, we have one hundred and ninety-eight automated tests. They check invariants every day, extreme cases, and a three-tank example traced by hand. Random draws are tied to events, so every strategy sees the same outbreak until quarantine starts. Here we rerun one block of the experiment, and every run matches the stored record.

### 4. Parameter selection (1:05-1:30)

> 画面：Stage 2 表格，D = 14 那行高亮。要点：主动修正了 Q1。

Before the main experiment, a two-stage pilot fixed the parameters. Stage one chose the disease rates and the transfer levels. Stage two chose how long the quarantine lasts, using three criteria set in advance.

Our first version of one criterion also counted transfers blocked by full tanks. So we defined a quarantine-only measure in advance and reran the pilot. Every earlier result came out identical, and fourteen days passed all three criteria.

### 5. Experiment design (1:30-1:50)

> 画面：设计示意图。要点：100 个配对 block，5200 次运行。

The main experiment uses twenty networks with five outbreak seeds each, which gives one hundred paired blocks for each transfer rate. All strategies in a block share the same seeds, so we compare them within the block. Our confidence intervals come from a bootstrap that resamples whole networks. That is five thousand two hundred runs in total.

### 6. One example (1:50-2:20)

> 画面：三列并排的动画。第 33 天出现蓝色方框时，提醒大家看隔离开始。

Here is one block, played three times with the same outbreak: no quarantine, the two best-connected tanks closed, and two random tanks closed. Watch day thirty-three, when the blue squares appear.

In this run, targeting cut the attack rate from sixty-one to forty-seven percent, and random closure did not help. But this is only one block.

### 7. Results (2:20-2:50)

> 画面：先图 2，再图 4。要点：×3.3、最多 10.6%、18 个里只有 2 个。

Across all blocks, the transfer rate matters most. Going from 0.01 to 0.025 multiplies the attack rate by three point three. Quarantining two tanks for fourteen days cuts it by at most ten point six percent.

When we compare targeted with random quarantine, only two of the eighteen intervals exclude zero. So we found no consistent advantage for choosing the bridge tanks.

### 8. Limits and reproduction (2:50-3:00)

> 画面：局限和三条命令。

The system is synthetic, and we tested one budget and one disease regime. Every number you have seen can be regenerated from our repository with three commands. Thank you.

## Possible questions

- **Why did targeting win so clearly in the example?** That block was chosen by a fixed rule that looks only at the no-quarantine run, not at how well any strategy did. One block shows how the mechanism works; the 100-block comparison is the evidence.
- **Why can random quarantine make things worse?** Closing a tank also blocks turtles from leaving it and changes where other turtles can move. From that point the outbreak follows a different path, which can be worse.
- **What would you do next?** Vary one setting at a time (budget, disease rates, capacity), with the seeds and settings recorded before running.
