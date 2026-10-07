# Collaboration Plan

## 1. Team and communication

| Member | Initial focus | GitHub |
|---|---|---|
| Member A - Cam Zhou | 模型规则、network generation、validation、methods structure | `camzhou831-star` |
| Member B - Wenhao Zhang | experiment design、intervention strategy、statistics/visualisation planning、results structure | `Winston-2hang` |

- Primary communication channel：**待组内确认**。
- Backup channel / phone：**待组内确认**。
- 固定 meeting：每周至少 2 次，每次 30-45 分钟；其中一次检查技术工作，一次检查研究解释和进度。
- Checkpoint、formal experiment freeze、report freeze 前增加 joint review。

不能把项目简单分成“一人写代码、一人写报告”。每名成员必须能解释完整模型、研究问题、实验公平性和主要结果。

## 2. Shared responsibilities

双方共同负责：

- 确认 research questions、hypothesis 和 assumptions；
- 交叉 review model and experiment changes；
- 共同检查 seed、budget 和 metric definitions；
- 共同解释 model limitations 和 results；
- 共同参加 Checkpoint；
- 保持 report、code、figures 和 speaking claims 一致；
- 识别 assessed/restricted material，防止不当复用。

## 3. GitHub workflow

### Main branch

- `main` 只保留 reviewable、documented、reproducible work。
- 禁止直接把未经 review 的 substantial model/experiment/report changes 合入 `main`。

### Feature branches

建议命名：

```text
docs/model-specification
model/sir-baseline
model/modular-network
intervention/tank-quarantine
experiment/paired-runner
analysis/primary-metrics
report/methods
```

### Pull requests

- substantial change 必须使用 pull request；
- PR 描述包含 purpose、assumptions changed、validation evidence、affected documents/results；
- 至少另一名成员 review 后 merge；
- reviewer 不只看代码风格，还要检查研究含义、预算公平和未来信息泄漏；
- 小 typo 可直接 commit，但应保持 commit focused。

### Issues and task tracking

每个 must-have task 建 issue，并包含：

- acceptance criteria；
- owner and reviewer；
- due date；
- dependencies；
- status；
- linked PR/commit。

Decision pending items 单独建 decision issues，关闭时写明选择、替代方案和理由。

## 4. Commit messages

格式建议：

```text
docs: define response-delay decision
model: add SIR daily transition rules
test: cover zero-transfer invariant
experiment: freeze primary seed matrix
analysis: add paired attack-rate summary
fix: preserve capacity during movement
```

原则：

- 一个 commit 只表达一个主要改变；
- message 描述意图，不写“update files”；
- 不提交 secrets、真实客户数据、virtual environments 或不可解释的 raw output；
- experiment/result commit 需关联 config 和 code version。

## 5. Review requirements by work type

| Work | Author checks | Reviewer checks |
|---|---|---|
| Model rule | 与 specification 一致；边界情况明确 | 是否改变研究含义；是否可独立实现 |
| Network/intervention | 无未来信息；centrality provenance | fairness、ties、budget、seed handling |
| Experiment config | 参数已冻结；完整 seed list | pairing、controls、run count、scope |
| Analysis | 包含失败/censored runs；指标定义一致 | uncertainty、effect size、no cherry-picking |
| Report | claims 有结果支持；limitations 明确 | 与 code/figures 一致；不夸大现实意义 |

## 6. Conflict resolution

1. 先把争议写成具体 modelling/engineering decision。
2. 各自说明备选方案、对 research question、runtime 和 interpretation 的影响。
3. 回到 `model-specification.md`、facilitator feedback 和 frozen experiment plan。
4. 不能在 24 小时内解决时，在 issue 中记录并询问 facilitator。
5. 决定后更新相关文档，不能只在聊天中口头决定。

Git merge conflict 由 branch author 先处理，reviewer 再确认语义没有丢失；禁止用 destructive reset 覆盖对方工作。

## 7. Ensuring both members understand the full model

- 每周进行一次 10-minute model walkthrough，由不同成员主讲。
- Member A 能解释实验 pairing、CI 和 plots；Member B 能解释 daily update、state transitions 和 invariants。
- 在 pilot 前，双方分别根据 specification 画出一日 update flow，再对照。
- Checkpoint 和 presentation 前交换 speaker sections 演练，确保可以回答对方部分。
- 重大 model change 需要双方在 issue/PR 明确 approve。

## 8. Contribution record

证据来源：

- GitHub issues and assignments；
- feature branches and commits；
- PR descriptions and reviews；
- meeting notes and decisions；
- experiment ownership and verification records；
- report section authorship plus cross-review。

每周更新贡献表：

最近更新：2026-10-06（issue #18）；2026-09-20 首次填写。每一行只写 GitHub 上有记录的证据；“无记录”表示 PR 页面上没有 review 或 comment，不代表没有口头沟通。

| Week | Task | Primary owner | Reviewer / verification | Issue/PR | Outcome |
|---|---|---|---|---|---|
| W7（1-4 Sep） | Non-code research design package（proposal、spec、assumptions、experiment/validation plans、timeline、risks） | Member A | 两名成员签署 spec（issue #10） | #10 | Done |
| W8（5-11 Sep） | Python 环境和 pinned requirements | Member A | — | #11 | Done |
| W8 | M1 baseline SIR、config validation、seed streams | Member A | Member B approve | #12 / PR #19 | Merged |
| W8 | Checkpoint 1 prediction 和排练稿 | Member B | Member A 合并；按 review 修订（commit 2026-09-07） | PR #20 | Merged |
| W8 | Checkpoint 1 feedback、D001-D003 / D006-D008 冻结、两层冻结规则 | Member A | 已 @Member B 请求 review；PR 上无 review 记录 | #1-#3、#6-#9 / PR #21 | Merged |
| W8 | Event-keyed paired draws、正式 V-tests、scenario layouts | Member A | Member B 在 issue #13 记录本地复跑和 update order 检查 | #13 / PR #22（经 PR #23 合入） | Done |
| W8-W9 | 3-tank hand trace | Member A 编写；Member B 独立重算 | 两名成员在 issue #14 签署 | #14 / PR #24 | Done |
| W8 | Modular network generator、structural checks、betweenness ranking、structural audit | Member A | Review follow-up 在 commit `ff1ad5b`；PR 上无 review 记录 | #16 / PR #23 | Merged |
| W9（12-18 Sep） | Run metadata 和 raw-result schema | Member B | Member A 合并；`tests/test_runner.py` 逐字段对照 schema §2 和 `RunRecord` | #15 / PR #25 | Merged 2026-09-20 |
| W9 | Network-constrained movement 和 capacity | Member B | PR 上无 review 记录（自行合并） | #26 / PR #27 | Merged |
| W9 | Tank quarantine strategies 和 Checkpoint 2 demo script | Member B | PR 上无 review 记录（自行合并）；Member A 于 2026-09-20 在 `origin/main` 复跑 111 tests 和 demo | #28 / PR #29 | Merged |
| W10（19-25 Sep） | Batch experiment runner、design files、pilot protocol draft | Member A | Member B 于 2026-10-03 合并；PR 页面无 review 评论；pilot 选择标准的确认仍待 Member B 签署（pilot-protocol §7） | #30 / PR #31 | Merged |
| W10 | Checkpoint 2 讲稿、贡献表、README gate 更新 | Member A 起草；Member B 负责自己的 sections | Member B approve 并于 2026-10-03 合并 | #18 / PR #32 | Approved；但合入的是 `experiment/batch-runner` 而非 `main`（见下方流程缺口），内容由 PR #35 带回 |
| W10-W11 | Conceptual system diagram | 原计划 Member B；实际由 Member A 绘制（2026-10-06，`scripts/draw_concept_diagram.py`） | Member A 于 2026-10-06 将 PR #35 合入 PR #34 的分支，PR #35 页面无 review 记录；待 Member B 在 PR #34 中 review | #17 / PR #35 → PR #34 | 随 PR #34 进入 `main` |
| W11（2-6 Oct） | Pilot 运行（Stage 1 两轮、Stage 2）和 parameter freeze | Member A | Member B 确认待定：pilot 在其签署 protocol 前运行，偏离已记入 decision-log | #4、#5 / PR #34 | In review |
| W11 | Pilot selection 实现、formal experiment（`formal`，发现 seed 交叉后以 `formal-nested` 重跑）、analysis、figures 1-7 | Member A | Codex CLI 两轮只读验收（ACCEPT WITH FIXES，修复见 PR #34）；待 Member B review | #4、#5 / PR #34 | In review |
| W11 | 报告初稿（全文，数字由脚本渲染）、文献核对 | Member A | 待 Member B review；3 条文献的 claim fit 待 Member B 交叉核实 | PR #34 | In review |
| W11 | README 收尾、贡献表更新、找回 PR #32 内容、干净环境复现、Checkpoint 3 讲稿和 demo 计划 | Member A | 同上：经 PR #35 合入 PR #34 的分支；讲稿和 demo 计划在 PR #35 合并后推送，另行合入（merge `6fe077f`）；待 Member B review | #17、#18 / PR #35 → PR #34 | 随 PR #34 进入 `main` |

已知流程缺口（2026-09-20 记录）：PR #27 和 PR #29 由作者自行合并，PR 页面没有跨成员 review，不符合 §5 对 model 变更的 review 要求。补救：Member A 已在 `origin/main` 上复跑完整测试和 demo；从 issue #30 起，model / experiment PR 必须有另一名成员的 GitHub review 记录后才能合并。

已知流程缺口（2026-10-06 记录）：PR #32 叠在 `experiment/batch-runner` 上。PR #31 先把该分支合入 `main`，3 分钟后 PR #32 才合并，结果只合进了 `experiment/batch-runner`，它的内容（Checkpoint 2 讲稿、本贡献表、README 更新）一直没有进入 `main`。补救：PR #35 合并 merge commit `1495833`。以后叠加的 PR 合并前先确认 base 分支仍然存在且指向 `main`。

AI 工具使用记录（2026-10-06 统计，全部分支）：自 2026-09-05 起，Member A 的 39 个提交中有 30 个在 Claude 协助下完成（commit 中带 `Co-Authored-By: Claude` 行）；2026-10-06 的外部验收审查使用 Codex CLI。2026-10-06 之后的提交不再加署名行，此后 Claude 协助的提交无法从 commit 记录中识别，以本说明为准。Member A 对所有提交内容负责，并逐条核实了工具给出的审查意见。

贡献不以 commit 数量单独衡量；model decisions、reviews、experiment verification 和 presentation preparation 同样记录。

## 9. If one member falls behind

Trigger：任务延误超过 2 天、连续错过 2 次 meeting、关键 PR 超过 48 小时无人响应，或 must-have timeline 受影响。

Response：

1. 在 issue 中说明 blocker，不作个人指责；
2. 把任务拆成最小可交付项；
3. 重新分配 must-have，暂停 optional extension；
4. 保留原 owner 作为 reviewer 或 knowledge-transfer participant；
5. 若持续影响公平合作，尽早联系 facilitator/unit coordinator，并保留 GitHub 和 meeting evidence。

## 10. Checkpoint collaboration evidence

Checkpoint 前应展示：

- shared repository；
- collaborator access；
- 至少一个分配明确的 issue；
- 至少一个由另一成员 review 的 PR 或文档 review；
- 当前 contribution table；
- 双方对 research questions 和 model definitions 的共同确认。
