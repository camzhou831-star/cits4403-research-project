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

| Week | Task | Primary owner | Reviewer | Issue/PR | Outcome |
|---|---|---|---|---|---|
| W7 | Non-code research design | Member A / Member B | Cross-review | 待创建 | In progress |

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
