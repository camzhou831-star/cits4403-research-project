# Week 12 Demo Preparation

Status：draft 2026-10-06，Member A 起草，待 Member B 确认。

> **Demo 的官方格式尚未记录**（时长、现场还是录像、是否逐人提问）。已知的唯一要求来自 lecture（2026-08-10）：“项目里可以直接用内置函数，但 demo 时必须能解释自己交的代码”。拿到格式后先改本文件。

## 1. 目标

1. 用 5-8 分钟讲清楚问题、模型、主要结果和局限；可以直接复用 `checkpoint-3-speaking-notes.md` 的 sections 1-8，按时长删减。
2. 现场运行代码，证明结果可以复现（`scripts/demo_final.py`）。
3. **每个人都能讲解仓库里的任何核心代码**，而不只是自己写的部分。这一点最可能被单独提问。

## 2. 代码讲解地图

每人都要能对着代码讲清楚下表每一行：做什么、为什么这样做、在哪里被测试。“作者”一栏按 GitHub 记录填写，用来分配主讲人，不代表另一个人可以不懂。

| 主题 | 位置 | 作者（PR） | 要点 | 测试 |
|---|---|---|---|---|
| 每日顺序 | `turtlefarm/model.py` `step()` | Cam（#19） | management → movement → transmission → recovery → commit；为什么 disease 同步更新 | `tests/test_invariants.py`、`tests/test_hand_trace.py` |
| 传播与恢复 | `model.py` `_transmission_and_recovery()`、`_commit()` | Cam（#19） | `1-(1-beta)^I`；新感染当天不传播 | `tests/test_extreme_cases.py`（`beta=0`、`gamma=1`） |
| 移动 | `model.py` `_movement_stage()` | Wenhao（#27） | 随机顺序、即时检查容量和隔离、blocked 的两种原因 | `tests/test_movement.py` |
| 隔离选择与时间 | `model.py` `_select_intervention_tanks()`、`_management_update()` | Wenhao（#29） | 只看疫情前的网络；`[start, start+D)` 半开区间；同等预算 | `tests/test_quarantine.py` |
| 网络 | `turtlefarm/network.py` `generate_network()`、`rank_by_betweenness()` | Cam（#23） | `p_in` / `p_out`、4 条接受规则、平局按 tank id 打破 | `tests/test_network.py` |
| 配对随机数 | `turtlefarm/rng.py` | Cam（#22/#23） | 同一 seed 下所有策略的抽样完全相同；这就是 common random numbers | `tests/test_paired_draws.py` |
| 批量运行 | `turtlefarm/runner.py` `ExperimentDesign.configs()`、`run_design()` | Cam（#31、#34） | block 结构、共享 baseline、嵌套 seeds、append-only | `tests/test_runner.py` |
| 结果记录格式 | `docs/run-result-schema.md` | Wenhao（#25） | 每次 run 记录哪些字段、失败如何记录 | `tests/test_runner.py` |
| 分析 | `turtlefarm/analysis.py` `paired_differences()`、`cluster_bootstrap_ratio()` | Cam（#34） | 为什么按网络重抽样；relative reduction 为什么用均值之比 | `tests/test_analysis.py` |

**练习方法**（每人至少做一次，最好互相出题）：

- 不看文档，在白板上画出每日 8 步，并说出每一步在哪个函数里。
- 打开对方写的一个函数，逐行解释给对方听。
- 现场改一个参数并预测结果，例如把 `quarantine_duration` 改成 0，或者把 `transfer_rate` 改成 0，然后运行 `python scripts/demo_final.py` 验证。改完记得 `git checkout` 恢复。
- 回答“如果要加一个检测过程 / 让生病的龟不移动，要改哪里？”

## 3. 现场演示流程（约 2 分钟）

```bash
source .venv/bin/activate
python -m pytest -q                       # Expected: 198 passed, about 4 seconds
python scripts/demo_final.py              # delay 33：targeted 0.475，random 0.625-0.900；最后一行 yes
python scripts/demo_final.py --delay 1    # 同一 block，targeted 反而更差 → 为什么需要 100 个 block
```

然后打开图：`fig2`（transfer rate 效应）→ `fig7`（跨区传播机制）→ `fig4`（配对差和置信区间）。

不要在 demo 中现场运行完整实验（约 2 分钟，而且没有必要）；如果被问到，就说明 `docs/reproduction-2026-10-06.md` 记录了从干净环境重跑的结果。

## 4. 备用方案

- 提前把会用到的图和 demo 输出截图放进一个文件夹，或导出一份 PDF；网络或电脑出问题时直接展示截图。
- 两台电脑都准备好环境：`.venv` 已安装，`pytest` 已通过，demo 已运行一次。
- 如果投影只能用 GitHub 网页，就准备好对应文件的网页链接，链接里固定到 commit（在 GitHub 页面按 `y`）。

## 5. 时间表

| 日期 | 事项 | 谁 |
|---|---|---|
| 提交后第 1 天 | 确认 demo 格式和时长；按格式删减讲稿 | 两人 |
| 第 2 天 | 交换讲解对方的代码（第 2 节表格），记录讲不清的地方 | 两人 |
| 第 3 天 | 完整排练两次并计时；一人讲、一人扮演老师提问 | 两人 |
| demo 前一天 | 在 demo 用的电脑上跑一遍第 3 节命令；准备截图备份 | 两人 |

## 6. 预计会被问到的问题

除 `checkpoint-3-speaking-notes.md` 的问答外，demo 时还可能被问：

- Why betweenness and not degree? → 我们关心的是跨区路径；degree 高的缸可能都在区域内部。文献 [5]（Salathé & Jones）发现在社区结构强的网络里，针对桥接节点更有效。
- Why is the model stochastic, and how many runs did you need? → 每个条件 100 个 block，按网络聚类的 bootstrap；pilot 用于估计运行时间。
- What would you do with more time? → 更大的隔离预算、敏感性分析（`beta`、`gamma`、容量）、预先设计的 strategy × delay 检验、记录每个缸被感染的时间，以检验报告 §4.2 的机制。
- Show me where X is tested. → 用第 2 节表格的最后一列。
