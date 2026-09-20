# CITS4403 Research Project

## Bridge Transfers and Quarantine in a Captive Turtle Farm

本仓库用于 CITS4403 Research Project 的研究设计、模型实现、计算实验、分析和最终展示。项目使用完全合成的数据，研究模块化养殖缸系统中的疾病传播和移动限制。它是一个 **stylised explanatory model（风格化解释性模型）**，不预测真实龟类疾病，也不使用真实龟场客户数据。

## Team

| Role | Name | GitHub | Contact |
|---|---|---|---|
| Member A | Cam Zhou | `camzhou831-star` | 待组内确认 |
| Member B | Wenhao Zhang | `Winston-2hang` | 待组内确认 |

- 截止时间：2026 年 10 月 9 日星期五 23:59。
- 当前阶段：**代码阶段（M1、M2 已实现；pilot protocol 待两名成员确认后运行 pilot）**。
- 当前实现状态：**`turtlefarm/` 已实现最小 SIR baseline、模块化网络、network-constrained movement、tank quarantine strategies 和 batch experiment runner；pilot 和正式实验尚未运行，仓库中没有任何实验结果。**
- Checkpoint 1 已完成，facilitator 无修改要求；D001-D003、D006-D008 已采纳 working proposal 为最终值，D004/D005 待 pilot 后确定（见 `docs/decision-log.md`）。
- 共享 GitHub repository 已建立；所有改动经 feature branch 和 PR review 合入 `main`。

## Proposed system

- 200 个合成 turtle agents 分布在 20 个 tanks 中。
- 20 个 tanks 构成一个包含 4 个区域的模块化转移网络（modular transfer network）。
- 个体疾病状态只有 `S / I / R`。
- 缸的管理状态只有 `open / quarantined`。
- 缸级 quarantine 在固定时间内禁止该缸的个体转入和转出，但缸内传播继续发生。
- 少数连接不同区域的 tanks 可能具有较高 betweenness centrality，并形成 bridge tanks。

## Research questions

**Primary research question**

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Secondary research question**

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## Hypothesis

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

## Modelling approach

项目计划使用离散时间的 agent-based model（ABM）和固定的 tank-transfer network：

- agent 层描述 SIR 疾病状态、所在 tank、同缸传播、恢复和个体转移；
- network 层描述允许转移的 tank pairs 和模块化区域结构；
- management 层比较 `No intervention`、`Random tank quarantine` 和 `Highest-betweenness tank quarantine`；
- 主实验只改变 cross-tank transfer rate、response delay 和 intervention strategy；
- 每个随机条件使用可追踪的 network seed、epidemic seed 和 random-policy seed。

完整规格见 [docs/model-specification.md](docs/model-specification.md)。

## Current stage and gates

**已满足的 gate（进入代码阶段，2026-09-11）**

1. Checkpoint 1 已完成，facilitator 无修改要求；
2. D001-D003、D006-D008 已冻结，D004/D005 的语义已冻结、数值待 pilot（`docs/model-specification.md` §18 两层冻结规则）；
3. 两名成员已签署模型规格（issue #10）；
4. GitHub collaborator 已接受邀请，PR #19 有跨成员 review；
5. 正式 rubric / 提交格式尚未发布，已记录在 `docs/decision-log.md`，3-8 October 再次核对。

**M2（movement / intervention / experiment runner）gate（已满足，2026-09-20）**

- 正式 V001-V005、V011、V012、V101、V103、V104 测试通过（issue #13，closed）；
- 手工 trace 与 event log 一致并由两名成员签署（issue #14，closed）；
- paired randomness 方案（event-keyed draws）已写入规格 §16 并实现（`turtlefarm/rng.py`）；
- run metadata / failure record schema 冻结（issue #15，PR #25，2026-09-20 合入）。

偏差记录：movement（PR #27）和 quarantine（PR #29）在 schema 合入之前已合并，与上面的 gate 顺序不一致。两者都不写 raw records；依赖 schema 的 experiment runner 是在 PR #25 合入之后才实现的（issue #30），因此没有任何 raw record 是在 schema 冻结前产生的。

**进入正式实验前必须满足**

- `docs/pilot-protocol.md` 的选择标准在运行前由两名成员确认；
- pilot 完成，`beta`、`gamma`、`D`、`p_in`/`p_out`、levels 和 seed lists 冻结并记录；
- V001-V012、V101-V110、fairness audit 全部通过（`docs/validation-plan.md` §10）。

## Environment

Python 3.12，依赖固定在 `requirements.txt`。两名成员使用相同版本，保证 same-seed 结果可比。

```bash
uv venv --python 3.12 .venv          # 或 python3.12 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt   # 或 pip install -r requirements.txt
python -c "import numpy, networkx, pandas, matplotlib, pytest; print('ok')"
```

`.venv/` 已在 `.gitignore` 中，不提交。

## Documentation map

| File | Purpose |
|---|---|
| `docs/research-proposal.md` | 系统、动机、研究问题、贡献和范围 |
| `docs/model-specification.md` | 可独立实现的一致模型规格 |
| `docs/assumptions.md` | 编号假设、影响和敏感性需求 |
| `docs/experiment-plan.md` | 主实验、配对设计、重复、分析和图表计划 |
| `docs/validation-plan.md` | 不变量、极端情况和验证证据计划 |
| `docs/checkpoint-1-brief.md` | 10 分钟 facilitator meeting 简报 |
| `docs/checkpoint-1-speaking-notes.md` | 两名成员 3-4 分钟英文讲稿 |
| `docs/collaboration-plan.md` | 沟通、GitHub workflow、review 和贡献记录 |
| `docs/timeline.md` | 截止日前 must/should/optional 时间表 |
| `docs/risk-register.md` | 风险、trigger、owner 和 mitigation |
| `docs/facilitator-questions.md` | Checkpoint 需要确认的问题 |
| `docs/literature-plan.md` | 文献检索方向和纳入标准 |
| `docs/consistency-review.md` | 跨文档一致性审查和待确认决定 |
| `docs/decision-log.md` | D001-D008 最终决定、facilitator 反馈记录和规格签署 |
| `docs/week-plan-2026-09-05.md` | 5-11 September baseline model 周执行清单 |
| `docs/checkpoint-1-prediction.md` | Checkpoint 1 排练稿：预测提问、准备答复和会后动作 |
| `docs/checkpoint-1-rehearsal-member-b.md` | Member B 的 Checkpoint 1 会前排练稿（中英对照，2026-09-07） |
| `docs/hand-trace-3tank.md` | M1 手工 trace fixture：3 tanks / 6 agents / 3 days，与 `tests/test_hand_trace.py` 对照 |
| `docs/run-result-schema.md` | Raw run record 的字段契约（`turtlefarm.run.v1`），runner 按此写 JSONL |
| `docs/pilot-protocol.md` | Pilot 两阶段设计和**运行前写下的**选择标准（draft，待 Member B 确认） |
| `docs/checkpoint-2-speaking-notes.md` | Checkpoint 2 两名成员英文讲稿、翻页位置、demo 步骤和问答分工 |
| `docs/network-audit-2026-09-11.md` | 模块化网络生成器结构审计（16 个 p_in/p_out 组合 × 10 seeds），D005 候选值 |
| `scripts/audit_network.py` | 重跑网络结构审计 |
| `scripts/demo_checkpoint2.py` | Checkpoint 2 功能演示（单个 seed block，不是实验结果） |
| `scripts/run_experiment.py` | 按 `experiments/config/*.json` 运行 batch，写 raw JSONL 和逐 run 汇总表 |
| `scripts/create_github_issues.sh` | 创建 milestones、labels 和首批 issues（支持 `--dry-run`） |

## Repository structure

```text
turtlefarm/    model implementation (SIR; event-keyed draws; modular network; movement; quarantine; batch runner)
tests/         V-numbered invariant, extreme-case, paired-draw, hand-trace, movement, quarantine and runner tests
scripts/       checkpoint demo, network audit, experiment runner and repository bootstrap helpers
experiments/   machine-readable experiment designs (experiments/config/*.json)
results/       raw run records (git-ignored), summaries and selected figures (created when the pilot runs)
```

## Experiment and result records

未来每次运行至少记录 model version / commit hash、complete configuration、network seed、epidemic seed、policy seed、network instance、strategy、response delay、quarantine budget、run status、stop reason、错误信息和全部预先定义的输出指标。

异常或失败运行不得静默删除。原始结果与清理后的分析表必须分开保存，并能从配置、seed 和代码版本重新生成。

## Academic integrity boundary

旧 `turtle-farm` 项目只提供领域启发。项目不会复制旧项目、CITS4403 Lab Notebook、CITS4012、CITS1401、CITS5501 assessed work 或受限制第三方代码。模型、合成数据、规则、实验、分析和文字均需要为本项目重新设计。
