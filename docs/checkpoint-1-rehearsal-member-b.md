下面按仓库现有分工设计：Speaker A 为 Cam，Speaker B 为你。如果现场分工不同，直接交换即可。老师的台词属于排练预测，不是官方原话。核心陈述约 4 分钟，老师提问和你们反问约 6 分钟。

## 会前准备

提前打开：

- GitHub 仓库主页；
- [Checkpoint 1 Brief](/Users/junhe/IT/4403/cits4403-research-project/docs/checkpoint-1-brief.md)；
- Issues 页面；
- [Facilitator Questions](/Users/junhe/IT/4403/cits4403-research-project/docs/facilitator-questions.md)。

两人坐下后，由 Speaker A 先开场。

------

## 0:00–0:30 老师开场

**Facilitator（预测）：**

> Hi. This is your first project checkpoint. Could you briefly introduce your proposed system, research question, modelling approach, and current progress?

中文意思：

> 你们好，这是第一次项目检查。请简要介绍系统、研究问题、建模方法和当前进展。

**Speaker A：**

> Hi, thank you. Our project is called “Bridge Transfers and Quarantine in a Captive Turtle Farm”. We will first explain the system and research questions, then the model and experiment design, and finally show our current GitHub progress.

中文：

> 您好，谢谢。我们的项目叫“圈养龟场中的桥梁转移与隔离”。我们会先介绍系统和研究问题，然后介绍模型与实验设计，最后展示 GitHub 上的当前进展。

------

## 0:30–1:30 系统与动机

**Speaker A：**

> We study a fully synthetic system containing 200 turtle agents and 20 tanks. The tanks are divided into four regions, with five tanks in each region. Most permitted transfer links are within a region, while only a small number of tanks connect different regions.

中文：

> 我们研究一个完全合成的系统，其中有 200 只乌龟和 20 个水缸。水缸被分成四个区域，每个区域五个缸。大多数允许的转移连接位于同一区域内，只有少数水缸连接不同区域。

> Infection spreads through contact within the same tank. Turtles may also move between connected tanks. Our motivation is that a local outbreak may remain within one region when movement is low, but a small number of cross-region transfers may allow it to spread through the whole system.

中文：

> 感染通过同缸接触传播，乌龟也可能在相连的水缸之间移动。我们的动机是：移动较少时，局部疫情可能只停留在一个区域；但少量跨区域转移可能使疫情扩散到整个系统。

### 老师可能打断：这是真实乌龟数据吗？

**Facilitator（预测）：**

> Are you using real turtle-farm or disease data?

**Speaker A：**

> No. The population, tank network and disease parameters are synthetic. This is a stylised explanatory model. We want to study the mechanism created by local transmission, network structure and movement, rather than make predictions about a real disease or farm.

中文：

> 没有。种群、水缸网络和疾病参数都是合成的。这是一个风格化的解释性模型，研究局部传播、网络结构和移动共同产生的机制，不用于预测真实疾病或真实养殖场。

恢复陈述：

> The synthetic setting also lets us control the network and compare interventions fairly.

中文：

> 合成系统也让我们能够控制网络条件并公平比较干预策略。

------

## 1:30–2:30 研究问题与涌现

**Speaker A：**

> Our primary research question is: How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

中文：

> 我们的主要研究问题是：在模块化的乌龟养殖系统中，跨缸转移率和响应延迟如何影响最终疫情规模与受影响水缸数量？

**Speaker B：**

> Our secondary research question is: Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

中文：

> 次要研究问题是：在相同干预预算下，隔离高介数中心性水缸是否比随机隔离水缸更能减少疾病传播？

> Our hypothesis is that a low but non-zero transfer rate may allow infection to cross between regions. We also expect longer response delays to reduce the effectiveness of quarantine, and targeted bridge-tank quarantine may perform better than random quarantine under the same budget.

中文：

> 我们假设，较低但非零的转移率可能使感染跨越不同区域。更长的响应延迟可能降低隔离效果；在相同预算下，针对桥梁缸的隔离可能比随机隔离更有效。

### 老师可能打断：涌现体现在哪里？

**Facilitator（预测）：**

> Where is the emergent behaviour in this model?

**Speaker B：**

> We only program local rules: infection within a tank, recovery, and movement between connected tanks. We do not directly program a farm-wide outbreak. If a system-wide outbreak appears, it emerges from many local interactions and occasional movements through bridge tanks.

中文：

> 我们只编写局部规则：同缸感染、康复以及相连水缸之间的移动。我们不会直接编写“产生全场疫情”这条规则。如果出现全系统疫情，它是由大量局部交互和偶尔经过桥梁缸的移动共同涌现出来的。

### 老师可能问：两个研究问题会不会太多？

**Facilitator（预测）：**

> Are these two separate projects? Is the scope too broad?

**Speaker B：**

> They use the same model, experiment factors and outcome measures. The primary question identifies when cross-tank spread becomes important. The secondary question then tests whether network structure can be used to reduce that spread. If the scope becomes too large, we will keep the primary question as the main result and treat the intervention comparison as the independent extension.

中文：

> 两个问题使用同一个模型、实验因素和结果指标。主要问题确定跨缸传播何时变得重要，次要问题进一步检验能否利用网络结构减少传播。如果范围过大，我们会保留主要问题作为核心结果，并把干预比较作为独立扩展。

------

## 2:30–4:00 模型结构与每日规则

**Speaker B：**

> We plan to use a discrete-time stochastic agent-based model. One time step represents one day. Each turtle has a location and one disease state: susceptible, infected or recovered. Each tank has a management state: open or quarantined.

中文：

> 我们计划使用离散时间的随机个体模型。一个时间步代表一天。每只乌龟都有位置以及易感、感染或康复中的一种疾病状态。每个水缸具有开放或隔离的管理状态。

> The permitted-transfer network is static during a simulation run, but individual turtle movements and disease states change over time. Infection uses complete mixing within each tank.

中文：

> 一次模拟中，允许转移的网络保持固定，但乌龟的位置和疾病状态会随时间改变。同缸感染采用完全混合假设。

> Each simulated day has the following order: first, activate or release quarantine; second, process movement; third, take a snapshot and calculate infections; fourth, calculate recoveries; fifth, apply disease-state changes synchronously; and finally record outputs and check whether the outbreak has ended.

中文：

> 每个模拟日依次执行：开启或解除隔离、处理移动、对当前状态取快照并计算感染、计算康复、同步应用状态变化，最后记录结果并检查疫情是否结束。

### 老师可能问：为什么没有 Q 状态？

**Facilitator（预测）：**

> Why do turtles only have S, I and R states? Where is the quarantine state?

**Speaker B：**

> Quarantine is defined at the tank level rather than the individual level. A turtle remains susceptible, infected or recovered while its tank may be open or quarantined. This separates disease status from management status.

中文：

> 隔离被定义在水缸层面，而非个体层面。乌龟仍然保持易感、感染或康复状态，同时它所在的水缸可以处于开放或隔离状态。这样可以区分疾病状态和管理状态。

### 老师可能问：隔离后为什么缸内仍能传播？

**Speaker B：**

> Quarantine blocks movement into and out of the selected tank, but turtles already inside the tank still interact. This lets us isolate the effect of restricting cross-tank movement.

中文>

中文：

> 隔离禁止乌龟进出被选中的水缸，但缸内原有乌龟仍然接触。这样能够单独研究限制跨缸移动的效果。

### 老师可能问：新感染者能否当天继续感染？

**Speaker B：**

> No. Infection and recovery are calculated from a fixed daily snapshot and committed synchronously. A newly infected turtle starts transmitting from the following day. This avoids results depending on the order in which agents are processed.

中文：

> 不能。感染和康复根据固定的每日快照计算，并同步更新。新感染乌龟从下一天开始传播，这样可以避免个体处理顺序改变结果。

------

## 4:00–5:20 三种干预策略

**Speaker B：**

> We compare three strategies: no intervention, random tank quarantine, and highest-betweenness tank quarantine.

中文：

> 我们比较三种策略：无干预、随机水缸隔离，以及隔离介数中心性最高的水缸。

> Betweenness measures how often a tank lies on shortest paths between other tanks. A tank can have a relatively small number of direct connections but still be important because it connects different regions.

中文>

中文：

> 介数中心性衡量一个水缸位于其他水缸之间最短路径上的频率。一个水缸的直接连接数可能不多，但如果它连接不同区域，仍然可能非常关键。

> Quarantining such a tank may block an important route for cross-region movement.

中文：

> 隔离这种水缸可能切断重要的跨区域移动路线。

### 老师可能问：三种策略是否对应完全图、ER 图和 BA 图？

**Facilitator（预测）：**

> Are you comparing different network types, such as random or scale-free networks?

**Speaker B：**

> No. All three strategies use the same modular transfer network. No intervention leaves all existing routes available. Random quarantine temporarily disables randomly selected tank nodes. Targeted quarantine temporarily disables the nodes with the highest betweenness. We are comparing intervention methods on the same network rather than generating three different network types.

中文：

> 不是。三种策略使用相同的模块化转移网络。无干预保留所有原有路线；随机隔离暂时禁止随机选中的水缸节点；定向隔离暂时禁止介数中心性最高的节点。我们比较的是同一网络上的干预方法，而不是生成三种不同类型的网络。

### 老师可能问：比较是否公平？

**Speaker B：**

> The random and targeted strategies use the same number of quarantined tanks, the same start day, the same duration, the same network, and the same epidemic seed. The main difference is the tank-selection method. We define intervention cost as the number of quarantined tanks multiplied by quarantine duration.

中文：

> 随机策略和定向策略使用相同的隔离水缸数、开始时间、持续时间、网络和疫情种子。主要区别只有水缸的选择方式。干预成本定义为隔离水缸数乘以隔离持续时间。

------

## 5:20–6:40 实验设计

**Speaker A：_STA**

> The main experiment changes three factors: cross-tank transfer rate, response delay, and intervention strategy. Transmission probability, recovery probability, population size and the network-generation procedure will remain fixed in the main experiment.

中文：

> 主实验改变三个因素：跨缸转移率、响应延迟和干预策略。感染概率、康复概率、种群数量及网络生成方法在主实验中保持固定。

> We plan to use four preliminary transfer-rate levels, three response-delay levels and three strategies. The exact numerical values will be selected after pilot checks.

中文：

> 我们计划使用四个初步转移率水平、三个响应延迟水平和三种策略。具体数值将在初步试运行后确定。

> The primary outputs are final attack rate, number of affected tanks, peak infected population, and time to extinction.

中文：

> 主要输出包括最终感染比例、受影响水缸数量、感染人数峰值以及疫情消失时间。

### 老师可能问：为什么需要重复运行？

**Facilitator（预测）：**

> Why not run each condition only once?

**Speaker A：**

> Infection, recovery, movement and network generation are stochastic. One run may be unusually mild or severe. We will therefore use multiple network and epidemic seeds and analyse distributions and uncertainty rather than relying on one trajectory.

中文：

> 感染、康复、移动和网络生成都具有随机性，一次运行可能偶然特别轻微或特别严重。因此我们会使用多个网络和疫情种子，分析结果分布和不确定性，而不是依赖单次轨迹。

### 老师可能问：预计重复多少次？

**Speaker A：**

> Our preliminary target is at least 30 to 50 epidemic replicates per main condition across multiple network instances. We will confirm the final number after measuring runtime and receiving your feedback.

中文：

> 初步计划是每个主要条件至少进行 30 至 50 次疫情重复，并覆盖多个网络实例。最终数量会根据运行时间和您的反馈确定。

### 老师可能问：一次运行什么时候结束？

**Speaker B：**

> A run ends when the infected population reaches zero. It does not require every turtle to become recovered. Some turtles may remain susceptible because they were never infected. If infection remains at the maximum simulation horizon, the run will be recorded as censored rather than treated as extinct.

中文：

> 当感染乌龟数量变成零时，一次运行结束。并不要求所有乌龟都康复，因为部分乌龟可能从未感染。如果到模拟时间上限时仍有感染，则记录为截尾运行，而不是假装疫情已经结束。

------

## 6:40–7:40 当前进展与 GitHub

**Speaker B：**

> At the moment, we have defined the system, research questions, hypotheses, model rules, assumptions, experiment plan, validation plan and project timeline.

中文：

> 目前我们已经确定了系统、研究问题、假设、模型规则、假设清单、实验计划、验证计划和项目时间表。

> We have created a shared GitHub repository with issues, milestones and assigned responsibilities. We have also reproduced the Python 3.12 environment from the same requirements file on both machines.

中文：

> 我们已经建立共享 GitHub 仓库，其中包含 Issues、里程碑和任务分配。两台电脑也已经使用相同的 requirements 文件复现了 Python 3.12 环境。

> We have not yet implemented the simulation or produced experimental results. The next milestone is the minimal SIR baseline, followed by validation tests, movement, quarantine and the experiment runner.

中文：

> 我们还没有实现模拟或生成实验结果。下一个里程碑是最小 SIR 基线模型，然后完成验证测试、移动、隔离和实验运行器。

### 老师可能问：为什么还没有代码？

**Facilitator（预测）：**

> Do you have a prototype or any results yet?

**Speaker B：**

> Not yet. We used the initial stage to define the model precisely so that both members implement and test the same rules. The environment is now reproducible, and the baseline implementation is the next scheduled task. We have also prepared invariant and extreme-case tests before running formal experiments.

中文：

> 目前还没有。我们先明确模型定义，确保两名成员实现和测试的是同一套规则。环境现在已经可复现，下一项计划是实现基线模型。正式实验前需要完成的不变量和极端情况测试也已经规划好。

这段要平静、直接，不需要道歉。

### 老师可能问：两个人怎样分工？

**Speaker A：**

> I am leading the baseline model and network implementation.

中文：

> 我主要负责基线模型和网络实现。

**Speaker B：**

> I am leading validation tests, the hand-traced scenario, result schema and checkpoint material. We will review each other’s pull requests, and both members are responsible for understanding the complete model and final results.

中文：

> 我主要负责验证测试、人工推演场景、结果数据结构和 Checkpoint 材料。我们会互相审查 Pull Request，并且两个人都需要理解完整模型和最终结果。

------

## 7:40–9:20 向老师提问

不要把 20 个问题全部问完。优先问三个。

**Speaker B：**

> We would like to confirm three modelling decisions before implementation.

中文：

> 在开始实现前，我们希望确认三个建模决定。

### 问题一：选题与独立研究是否合适？

> First, is this synthetic explanatory system appropriate for the project, and is the equal-budget comparison between random and betweenness-based quarantine sufficient as an independent investigation?

中文：

> 第一，这个合成解释性系统是否适合作为项目？在相同预算下比较随机隔离与基于介数中心性的隔离，是否足以构成独立研究？

**老师可能回答：**

> Yes, but keep the research question focused and make sure you analyse the behaviour rather than only demonstrate the simulation.

你们回答：

> Understood. We will keep transfer rate, response delay and intervention strategy as the main factors, and use repeated experiments to support the conclusions.

中文：

> 明白。我们会把转移率、响应延迟和干预策略作为主要因素，并用重复实验支持结论。

如果老师认为范围太大：

> In that case, would you recommend keeping transfer rate and response delay as the primary study and treating the intervention comparison as an extension?

中文：

> 在这种情况下，您是否建议保留转移率和响应延迟作为主要研究，把干预比较作为扩展？

### 问题二：response delay 从哪里开始？

> Second, should response delay be measured from outbreak introduction at time zero, or from the first observed infection? Our current MVP measures it from time zero because using first detection would require an additional observation model.

中文：

> 第二，响应延迟应从疫情在时间零引入开始计算，还是从首次观察到感染开始计算？当前最小模型从时间零开始，因为首次发现需要加入额外的观测模型。

如果老师说从 `t=0` 可以：

> Thank you. We will record that definition explicitly and describe it as a combined detection and administrative delay.

中文：

> 谢谢。我们会明确记录这个定义，并将其解释为检测与行政响应延迟的合并抽象。

如果老师要求从首次检测开始：

> Understood. Would a simple fixed detection delay be sufficient, or do you expect a stochastic observation process?

中文：

> 明白。使用固定检测延迟是否足够，还是需要随机的观测过程？

### 问题三：评分和提交要求

> Finally, have the full marking rubric, report format, page limit and exact GitHub evidence requirements been released?

中文：

> 最后，完整评分标准、报告格式、页数限制以及 GitHub 协作证据要求是否已经发布？

如果老师说尚未发布：

> Thank you. We will continue with the current plan and revise the documentation when those requirements are available.

中文：

> 谢谢。我们会继续当前计划，并在要求发布后更新文档。

------

## 9:20–10:00 结束

**Facilitator（预测）：**

> That sounds reasonable. Please record the decisions from this meeting and show a working model at the next checkpoint.

中文：

> 这个方向听起来合理。请记录本次会议的决定，并在下次检查点展示可运行模型。

**Speaker A：**

> Thank you. We will record today’s feedback in our decision log and update the relevant model and experiment documents.

中文：

> 谢谢。我们会把今天的反馈记录到决策日志，并更新相关模型和实验文档。

**Speaker B：**

> We will then complete the minimal SIR baseline and its validation tests before adding movement and quarantine. Thank you for your feedback.

中文：

> 接下来我们会先完成最小 SIR 基线及其验证测试，再加入移动和隔离。感谢您的反馈。

------

## 备用问答

**老师：为什么使用 agent-based model？**

> Individual turtles have locations, disease states and movement decisions. An agent-based model allows us to represent these individual differences and observe how their local interactions produce system-level outbreak patterns.

个体拥有位置、疾病状态和移动决策，ABM 可以表示这些个体行为，并观察它们如何产生整体疫情模式。

**老师：为什么使用 complete mixing？**

> We do not have spatial contact data within each tank, and our main question concerns movement between tanks. Complete mixing keeps the within-tank rule simple and explicit. We will report it as a limitation.

没有缸内空间接触数据，研究重点是跨缸移动。完全混合让缸内规则保持简单明确，并会作为局限讨论。

**老师：为什么选择 20 个缸和 200 只乌龟？**

> This gives us four visible network regions with enough agents for local transmission while remaining computationally manageable. The values are synthetic and can be checked in sensitivity analysis if necessary.

这样可以形成四个清楚的网络区域，也有足够个体产生局部传播，同时计算量可控。数字是合成的，必要时可以进行敏感性分析。

**老师：如果桥梁隔离没有优于随机隔离怎么办？**

> That would still be a valid result. We would examine whether the network has redundant paths, whether transfer is too low, or whether the response occurs after cross-region spread has already happened.

这仍然是有效结果。我们会检查是否存在替代路径、转移率是否太低，或者响应时疾病是否已经完成跨区域传播。

**老师：你们怎样验证代码正确？**

> We will test population conservation, valid states, capacity limits, quarantine boundaries, zero-transmission and zero-movement cases, same-seed reproduction, and a small scenario calculated manually and compared with the event log.

我们会测试种群守恒、状态合法性、容量限制、隔离边界、零传播和零移动、相同种子复现，以及人工计算的小场景与程序日志的一致性。

**老师：什么是 final attack rate？**

> It is the proportion of turtles that were infected at any time during the run, including the initial infected turtle.

它是一次运行中曾经感染过的乌龟比例，包括最初感染的乌龟。

**老师：项目和 Game of Life 有什么关系？**

> Both systems use repeated local update rules to generate global behaviour. Game of Life is a deterministic cellular automaton on a grid, while our model is a stochastic agent-based model on a modular network with movement and SIR states.

两者都通过重复执行局部规则产生整体行为。Game of Life 是网格上的确定性元胞自动机；本项目是模块化网络上包含移动和 SIR 状态的随机个体模型。

会议结束后，当天完成 #9：记录老师的实际回答。若老师修改任何定义，再更新规格和其他文档，之后双方完成 #10 的最终签署。