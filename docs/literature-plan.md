# Literature Search Plan

本阶段不编造文献、作者、DOI 或研究结论。本文件只定义后续检索方向、关键词、筛选标准和证据记录方式；尚未建立正式 reference list。

## 1. Review purposes

文献只用于：

- justify the modelling framework；
- identify standard definitions and validation practices；
- compare intervention concepts；
- explain limitations and alternative assumptions；
- position the independent investigation。

文献不能被用来声称本 synthetic turtle system 已被真实 farm data 验证。

## 2. Search topics and suggested queries

| Topic | Suggested keywords |
|---|---|
| Agent-based epidemic models | `agent-based epidemic model stochastic SIR validation` |
| Metapopulation epidemic models | `metapopulation epidemic movement between patches SIR` |
| Modular contact networks | `epidemic spreading modular networks community structure` |
| Temporal/dynamic networks | `epidemic temporal network dynamic contact movement` |
| Targeted intervention | `network targeted intervention epidemic node removal` |
| Betweenness intervention | `betweenness centrality immunization quarantine epidemic` |
| Movement restriction | `quarantine movement restriction metapopulation epidemic` |
| Stochastic validation | `stochastic simulation model verification validation sensitivity` |
| Reproducible experiments | `reproducible computational experiments random seed provenance` |
| Paired simulation design | `common random numbers paired stochastic simulation experiment` |

## 3. Preferred source hierarchy

1. Original peer-reviewed research papers introducing or evaluating a method；
2. Authoritative textbooks or review articles for established concepts；
3. Official software/method documentation only for implementation definitions；
4. Secondary summaries only to discover primary sources, not as final evidence。

## 4. Inclusion criteria

- clear author and publication venue；
- stable DOI or publisher/institution URL；
- directly supports a modelling, network, intervention or validation statement；
- methods and system scale are understandable；
- publication can be independently verified；
- no reliance on an abstract alone for a detailed claim。

## 5. Exclusion criteria

- unverifiable citation or DOI；
- blog/marketing claim without primary evidence；
- paper only mentions “network” but does not support the used concept；
- turtle-specific source that does not actually concern movement or disease transmission；
- source used to imply real-world calibration that the model does not have。

## 6. Evidence extraction template

For each accepted source record:

```text
Full citation:
DOI or stable URL:
Source type:
Model/system studied:
Relevant method or finding:
Exact claim supported in our report:
Important limitations:
Where it will be cited:
Verified by:
Verification date:
```

## 7. Search workflow

1. Search each topic in scholarly databases/library search。
2. Read title/abstract only for initial screening。
3. Open and verify the primary source and DOI。
4. Extract only claims the source directly supports。
5. Have the second member verify citation metadata and claim fit。
6. Add accepted sources to a shared bibliography file only after verification。
7. Record rejected or uncertain sources separately，不放入正式 references。

## 8. Minimum literature coverage before report drafting

建议至少覆盖：

- one authoritative source for ABM/stochastic epidemic modelling；
- one for metapopulation or patch movement；
- one for modular network effects；
- one for targeted/betweenness intervention；
- one for movement restriction/quarantine abstraction；
- one for stochastic verification, sensitivity or reproducibility。

数量不是目标；每条引用必须与实际 claim 对应。

## 9. Current status

- 本轮按照 local-first 要求检查了本地课程资料，没有进行互联网文献检索。
- 当前正式 bibliography：**empty by design**。
- 下一步：Checkpoint feedback 后由两名成员分配检索主题并交叉验证。
