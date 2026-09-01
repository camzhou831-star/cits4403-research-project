# Research Proposal

## 1. System

本项目研究一个模块化 captive-turtle housing system。系统由 20 个养殖缸组成，每个缸是 tank-transfer network 中的一个节点；200 个合成 turtle agents 分布在这些缸中。网络分成 4 个区域，每区 5 个缸。区域内部允许的转移连接较多，区域之间连接较少，因此少数连接不同区域的缸可能成为 bridge tanks。

每个 agent 的疾病状态为 susceptible (`S`)、infected (`I`) 或 recovered (`R`)。每个 tank 的管理状态为 `open` 或 `quarantined`。Quarantine 是缸级移动限制：在规定时间内禁止该缸的个体转入和转出，但不停止缸内部的疾病传播。

所有个体、网络和实验数据均为合成数据。本项目是 **a stylised explanatory model**，不是实际龟场的数字孪生，也不预测真实龟类疾病。

## 2. Motivation

在模块化系统中，同缸接触可能使感染在局部扩散，而少量跨缸转移可能把原本分隔的区域连接起来。宏观的系统范围暴发由局部传播规则、模块化网络结构和少量 bridge connections 共同产生，因此符合复杂系统中“局部交互产生整体行为”的研究视角。

资源有限时，关键不仅是隔离多少缸，还包括隔离哪些缸。在隔离相同数量、相同时间开始并持续相同天数时，利用干预前已知网络结构选择 high-betweenness tanks，可能比随机选择更有效。

## 3. Research gap and independent investigation

本项目不把“实现一个 SIR simulator”当作贡献。独立调查体现在：

1. 将 agent-level SIR dynamics 与 modular tank-transfer network 结合；
2. 系统改变 transfer rate 和 response delay，研究局部暴发何时扩展到多个区域；
3. 在严格相同的 intervention budget 下比较 random 和 highest-betweenness tank quarantine；
4. 分开记录 network-instance variance、epidemic stochastic variance 和 random-policy selection variance；
5. 检查结论对少量非主实验参数和更新假设是否稳健。

## 4. Primary research question

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

## 5. Secondary research question

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## 6. Hypotheses

**Canonical hypothesis**

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

为便于实验检验，拆分为：

- **H1:** Relative to zero or very low transfer, non-zero transfer is expected to increase final attack rate and the number of affected tanks by enabling cross-group spread.
- **H2:** For a fixed transfer rate and quarantine policy, longer response delay is expected to produce no smaller final attack rate and no fewer affected tanks on average.
- **H3:** Under an equal intervention budget and paired random conditions, highest-betweenness quarantine is expected to produce lower final attack rate and fewer affected tanks than random quarantine.

H2 的严格单调性可能受随机性和已经发生的传播状态影响；正式结论将基于分布和不确定性，而不是要求每一次 run 都单调。

## 7. Proposed modelling approach

- 模型类型：discrete-time agent-based model with a static modular transfer network。
- agent 层：每只龟具有唯一 ID、tank location、`S/I/R` 状态和状态进入时间。
- tank 层：每个缸具有容量、区域、邻接缸和 `open/quarantined` 状态。
- network 层：固定、无向、无权、简单图；边表示允许直接转移的路径，不表示某天必然发生转移。
- disease dynamics：同缸 complete mixing，感染按 susceptible agent 的风险计算；infected agents 按固定 recovery probability 恢复。
- movement dynamics：open tanks 之间的 agent transfers 受 transfer rate、邻接关系和容量限制。
- intervention：无干预、随机缸隔离、最高 betweenness 缸隔离。

详细规格见 `model-specification.md`。

## 8. Planned experiments

主实验只改变：

1. cross-tank transfer rate；
2. response delay；
3. intervention strategy。

其他参数在主实验中固定。初步设计使用 4 个 transfer-rate levels、3 个 response-delay levels、3 种 strategies，并以 pilot 确定具体数值。每个条件建议至少 30-50 个 epidemic replicates，并跨多个 network seeds。三种 strategy 使用相同 network instance 和 epidemic seed；random quarantine 另使用独立 policy seed。

主要指标为 final attack rate、number of affected tanks、peak infected population 和 time to extinction。辅助指标仅包括 time to peak、intervention cost 和 relative reduction compared with random quarantine。

## 9. Expected contribution

项目预期贡献不是给出真实疾病管理建议，而是说明在一个清楚、可复现的合成模型中：

- 模块化结构和少量跨组转移如何改变暴发尺度；
- response delay 如何改变移动限制的机会窗口；
- 只使用干预前网络结构的 high-betweenness strategy 是否在等预算下优于 random strategy；
- 哪些结果对随机网络实例和疾病过程较稳健。

在模型尚未运行前，以上均为待检验问题，不是已得到的结论。

## 10. Scope

### In scope

- 20 tanks、200 synthetic agents、4 modular regions；
- SIR disease states；
- static permitted-transfer network and dynamic agent movements；
- tank-level movement quarantine；
- 三种 intervention strategies；
- paired stochastic experiments；
- qualitative network/time-series inspection and quantitative summaries；
- limited sensitivity analysis。

## 11. Out of scope

- 真实龟类疾病预测或参数校准；
- 使用真实客户、农场、兽医或交易数据；
- 个体 `Q` disease state；
- mortality、birth、ageing、breeding、treatment 或 vaccination；
- Web 界面、数据库、登录系统或实时动画；
- 主实验中同时扫描大量传播、恢复和容量参数；
- 经济最优化或真实管理政策建议。

## 12. Limitations

- complete mixing within a tank 忽略细粒度接触差异；
- network 和 population 均为 synthetic，不能用于经验性外推；
- homogeneous susceptibility 忽略物种、年龄和健康差异；
- static transfer routes 忽略长期结构变化；
- response delay 是抽象的检测与行政延迟，不包含独立观察模型；
- quarantine 被理想化为完全阻止跨缸移动；
- betweenness 只反映网络结构，不保证在所有条件下都最优。

## 13. Academic integrity boundary

旧 `/Users/yuanqimaomao/Desktop/projects/turtle-farm` 只提供“多个缸、个体、疾病问题和隔离”这一领域启发。不会复用其中的客户数据、业务结果、数据库记录、报告文字或不存在的传播结论。

本项目的 synthetic population、network generator、SIR rules、quarantine rules、experiment design、analysis 和报告文字需要重新设计。课程 Notebook 只用于理解图、随机实验和网络指标；不会复制 CITS4403 Lab 实现，也不会复制 CITS4012、CITS1401、CITS5501 assessed code。

## 14. Requirements not yet published

截至 2026-09-02，本地资料没有提供完整的正式报告格式、页数、最终技术格式、rubric 或提交细节。相关要求发布后必须更新本仓库；本文件不作推测。
