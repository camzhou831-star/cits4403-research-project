# Project Timeline

截止：**2026-10-09 Friday, 11:59 pm**。

优先级：

- **Must have:** 没有这些不能完成研究问题或可靠提交。
- **Should have:** 增强独立调查、解释和质量，但可在时间压力下缩减。
- **Optional extension:** 只有 must/should 稳定后才做。

## 1-4 September - Research design, repository and Checkpoint 1

### Must have

- 冻结 canonical primary/secondary questions and hypothesis；
- 完成 proposal、model specification、assumptions、experiment/validation plans；
- 准备 Checkpoint brief and speaking notes；
- 确认 shared repository and collaborator access；
- 建 facilitator questions；
- 两名成员 review 文档一致性。

### Should have

- 创建 GitHub issues、labels、milestone 和 first cross-review evidence；
- 画一张非结果性质的 conceptual system diagram。

### Optional

- 初步检索少量权威文献；不得拖延 Checkpoint。

## 5-11 September - Baseline model

### Must have

- Facilitator feedback 后关闭 pending model decisions；
- 实现最小 SIR states、daily update 和 stopping condition；
- 实现 synthetic population and fixed tank locations；
- 完成 beta=0、population conservation、same-seed tests；
- 共同手工验证小场景。

### Should have

- 模块化 network generator and metric audit；
- clear run metadata schema。

### Optional

- 无。

## 12-18 September - Movement, intervention and experiment runner

### Must have

- network-constrained movement and capacity；
- tank `open/quarantined` management state；
- three strategies；
- pre-outbreak betweenness selection；
- strict budget-fair pairing；
- network/epidemic/policy seed separation；
- validation plan required cases。

### Should have

- batch runner、config validation、raw-result provenance；
- end-to-end trace and PR review。

### Optional

- runtime optimisation only if needed。

## 19-25 September - Pilot and formal experiments

### Must have

- Run and document pilot without treating it as hypothesis evidence；
- Freeze parameters and seed lists；
- Estimate runtime and failure rate；
- Run complete primary experiment；
- Preserve failed/censored/anomalous runs；
- Generate reproducible summary tables。

### Should have

- Complete nested random-policy replicates；
- Begin limited sensitivity checks after primary runs finish。

### Optional

- Extra network structure sensitivity if runtime permits。

## 26 September-2 October - Analysis and report

### Must have

- Quantitative analysis with paired effects and uncertainty；
- Qualitative representative runs with declared selection rule；
- Explain results, limitations and alternative explanations；
- Draft methods, results and discussion；
- Verify all claims against data and configs。

### Should have

- Complete limited beta/gamma or capacity sensitivity；
- Improve figures and captions；
- Rehearse interpretation with both members。

### Optional

- Additional exploratory plot only if it answers an existing question。

## 3-8 October - Reproduction, demonstration and freeze

> **10 月 3 日后原则上不再增加新的模型功能。**

### Must have

- Fresh-environment reproduction of selected runs/figures；
- Freeze model, configs and analysis；
- Resolve report/code/figure inconsistencies；
- Prepare demonstration and speaking roles；
- Check contribution evidence and academic integrity；
- Incorporate any published rubric/submission requirements。

### Should have

- Independent rerun by the member who did not author the runner；
- Final accessibility and figure-label review。

### Optional

- None unless all submission materials are frozen and verified。

## 9 October - Final check and submission

### Must have

- Verify final files, filenames and required formats against official instructions；
- Confirm report, code, figures and presentation use the same final results；
- Confirm repository commit/tag and both-member access；
- Submit before 23:59 and preserve submission receipt。

### Stop rule

当天只修复 submission-blocking errors。不得增加模型功能、重新选择参数或重新解释结果来追求更漂亮的结论。
