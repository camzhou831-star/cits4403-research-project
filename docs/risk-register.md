# Risk Register

Likelihood/impact 使用 Low / Medium / High。Owner 为主要跟进者，不表示只有该成员负责。

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| R001 | Bridge tank 定义不清 | Medium | High | 使用 pre-outbreak normalized betweenness；记录 ties；facilitator 确认 | A | 两人无法独立选出同一 targeted tanks |
| R002 | Network 过于对称，所有 betweenness 接近或相同 | Medium | High | stochastic modular generator、structure rejection criteria、跨 seeds | A | 多数 networks 出现大量 centrality ties |
| R003 | 所有 experiments 都不传播 | Medium | High | pilot 检查 beta/gamma/transfer regime；透明记录选择 | A+B | no-intervention 多数 run 只有 initial case |
| R004 | 所有 experiments 都完全感染 | Medium | High | pilot 避免 saturated regime；不为支持假设调参 | A+B | 多数 conditions attack rate 接近 1 |
| R005 | 参数组合过多 | High | High | 主实验只保留 3 factors；其他只做 limited sensitivity | B | estimated runs/runtime 超过 timeline |
| R006 | 缺少真实 disease calibration | High | Medium | 明确 stylised explanatory model；不用现实单位外推 | A | 文档开始使用“真实风险/建议”表述 |
| R007 | 把模型错误解释为现实预测 | Medium | High | 每份对外材料写 limitation；claims cross-review | Both | report/presentation 出现“证明真实龟场” |
| R008 | Centrality strategy 使用未来信息 | Low | High | selector 只接收 pre-outbreak network；provenance and review | A reviewer B | selected tanks 随 epidemic outcome 变化 |
| R009 | Intervention budget 比较不公平 | Medium | High | assert same k/start/duration/network/seed；paired audit | B reviewer A | strategies 的 cost/config 不一致 |
| R010 | 两人 Git 贡献不平衡 | Medium | High | issues、PR reviews、weekly contribution table、early escalation | Both | 一人连续 2 周无可见 contribution |
| R011 | 无法复现实验 | Medium | High | explicit seeds、config hash、commit hash、fresh rerun | B reviewer A | same config/seed gives different result |
| R012 | 直接复用旧 assessed/restricted code | Low | High | new implementation、PR integrity checklist、source inventory | Both | PR 含旧 coursework/vendor code |
| R013 | Report、code、figures、demo 结果不一致 | Medium | High | single frozen result set、cross-file consistency check | Both | 同一 metric 在材料中数值不同 |
| R014 | 后续 rubric/submission requirements 变化 | Medium | High | facilitator/LMS check、assign owner、update docs promptly | B | official requirements newly published |
| R015 | Response delay 含义不清 | High | High | Checkpoint 明确提问；实现前冻结 introduction vs detection | A | 文件对 delay 起点表述不一致 |
| R016 | Capacity 导致大部分 transfer 被阻止 | Medium | Medium | pilot 记录 attempted/accepted ratio；调整 fixed capacity once | A | accepted/attempted rate 长期接近 0 |
| R017 | Time horizon 太短，censoring 过多 | Low | Medium | pilot 检查；透明 time-to-event handling | B | censored runs 超过 working 5% trigger |
| R018 | Random policy variance 掩盖 policy comparison | Medium | Medium | multiple policy seeds 或 nested variance summary | B | random strategy CI 主要由 tank choice 驱动 |
| R019 | Outcome-driven pilot tuning | Medium | High | 预先写 pilot criteria；保留全部尝试；双人批准 freeze | Both | 参数因“不支持假设”被更换 |
| R020 | 模型开发挤压分析和报告时间 | Medium | High | MVP gate；10 月 3 日 feature freeze；先删 optional | Both | must-have implementation 晚于 9 月 18 日 |

## Escalation order

1. 先保护 research validity、academic integrity 和 reproducibility。
2. 再保护 must-have primary experiment。
3. 删除 optional extension，而不是减少公平比较或隐藏失败。
4. 若 teammate availability 或 official requirements 造成重大影响，尽早联系 facilitator/unit coordinator。
