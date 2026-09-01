# Documentation Consistency Review

Review date: 2026-09-02。Scope: all tracked project documents in the non-code preparation package。

## 1. Local sources checked before authoring

- `/Users/yuanqimaomao/Desktop/CITS4403_本地资产只读审查与选题建议.pdf` - 11 pages；reviewed scope, recommended direction, MVP, academic-integrity boundary and Checkpoint wording。
- `/Users/yuanqimaomao/Desktop/obsdian知识库/02知识库/09学习/4403/L01 复杂性科学导论.md` - model/question framing, explanatory vs predictive models, repeated stochastic runs。
- `/Users/yuanqimaomao/Desktop/obsdian知识库/02知识库/09学习/4403/L02 图论基础与ER随机图.md` - graph definitions, random baselines, connectivity and repeated instances。
- `/Users/yuanqimaomao/Desktop/obsdian知识库/02知识库/09学习/4403/L03 小世界与无标度网络.md` - clustering, path length, degree distribution, WS/BA limitations and network-model comparison。
- `/Users/yuanqimaomao/Desktop/课程总结/总结/4403/CITS4403 - 20 Jul 20-s1-full.md` - simple/valid/robust models, simulation vs model, project 25%, academic integrity。
- `/Users/yuanqimaomao/Desktop/课程总结/总结/4403/CITS4403 - 27 Jul 20-s1-full.md` - network assumptions, ER baseline, dynamic/static network meaning and GitHub collaboration requirement。
- `/Users/yuanqimaomao/Desktop/课程总结/总结/4403/CITS4403 - 03 Aug 20-s1-full.md` - WS/BA, betweenness-related structural reasoning, qualitative/quantitative comparison and model limitations。
- `/Users/yuanqimaomao/Desktop/课程总结/总结/4403/CITS4403 - 17 Aug 20-s1-full.md` - Week 7 checkpoint, 5-10 minute meeting, repository and GitHub evidence。
- Graph1 and Graph2 course notebooks - random seeds, repeated graph experiments, clustering/path/degree measures and model fitting workflow。No lab code copied。
- CITS1401 L22/L23 simulation notes - repeated random experiments, seed reproducibility, spiral development and unit/integration testing concepts。No assessed code copied。
- Current repository status and existing README/docs/commit history。

## 2. Availability findings

- All requested local notes, notebooks and the audit PDF were accessible。
- No separate local document containing the complete final report format, page limit, final technical submission format or full rubric was found。
- Course summaries support a Week 7 checkpoint and GitHub evidence；the user-supplied brief states Weeks 7-8。Documents therefore use “Weeks 7-8” and avoid a fabricated exact appointment。

## 3. Canonical consistency checks

| Check | Required value | Status |
|---|---|---|
| Primary question | Exact canonical sentence | Pass |
| Secondary question | Exact canonical sentence | Pass |
| Agent states | `S / I / R` only | Pass |
| Tank states | `open / quarantined` only | Pass |
| Individual Q state | Absent from MVP | Pass |
| Quarantine meaning | Blocks transfer in/out；internal spread continues | Pass |
| Strategies | None / Random / Highest-betweenness | Pass |
| Budget fairness | Same k/start/duration/network/epidemic seed | Pass |
| Main factors | transfer rate / response delay / strategy | Pass |
| Main metrics | attack rate / affected tanks / peak I / extinction time | Pass |
| Data | fully synthetic | Pass |
| Framing | stylised explanatory, not predictive | Pass |
| Future information | prohibited for policy selection | Pass |
| Results claims | no model/results claimed | Pass |
| Deadline | completion/freeze before 2026-10-09 23:59 | Pass |

## 4. Conflicts found and resolved

The initial repository documents contained three conflicts with the fixed design:

1. They described an individual SIR-Q model. Resolved to agent `S/I/R` plus tank `open/quarantined`。
2. They placed infection probability, recovery probability and capacity in the main experimental factors. Resolved: these are fixed in the main experiment and only limited sensitivity factors。
3. They combined primary and secondary questions into one sentence. Resolved by using the exact two canonical questions in all public-facing documents。

No unresolved contradiction remains among current canonical documents。Items not yet known are explicitly marked `Decision pending facilitator confirmation`。

## 5. No-code verification

- No `.py`, `.R`, `.java`, `.c` or new `.ipynb` model file was created in this phase。
- No simulation was run。
- No prototype data, chart, confidence interval or result was manufactured。
- Documents state that prototype results will only be added after implementation。

## 6. Review to repeat after facilitator meeting

If any D001-D008 decision changes, update at minimum:

- `model-specification.md`；
- `assumptions.md`；
- `experiment-plan.md`；
- `checkpoint-1-brief.md`；
- `checkpoint-1-speaking-notes.md`；
- `risk-register.md`；
- this consistency matrix。
