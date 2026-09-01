# Facilitator Questions

按 meeting 优先级排列。建议先说明当前 working decision，再请 facilitator 判断。

## Project suitability

1. **Is a synthetic, explanatory turtle-farm model appropriate for this project?**
   - Working position: yes, if we clearly avoid real-disease claims and use the model to answer a focused experiment question.

2. **Is tank-level movement quarantine a sufficiently clear intervention?**
   - Definition: a quarantined tank blocks all incoming and outgoing transfers for a fixed duration, while internal transmission continues.

3. **Is it acceptable to use one primary question and one closely related secondary intervention question?**
   - The primary question studies transfer rate and response delay; the secondary question compares random and structural selection under equal cost.

4. **Does comparing random and betweenness-based quarantine provide sufficient independent investigation?**
   - We also plan paired seeds, multiple network instances and variance separation rather than a single demonstration.

5. **Is a modular synthetic transfer network acceptable without real farm movement data?**
   - We will report the generation rule and never claim it represents a measured farm network.

6. **Should the project prioritise affected tanks or final attack rate as the main outcome?**
   - Current plan treats both as co-primary outcomes because one measures population burden and the other cross-group spread.

## Model definition

7. **Should response delay be measured from outbreak introduction or from the first observed infection?**
   - Working MVP: from introduction at `t=0`, representing combined detection and administrative delay. A detection-based definition requires an observation model.

8. **Is a static permitted-transfer network with dynamic individual movements an appropriate interpretation of a dynamic system?**

9. **Is unweighted betweenness centrality sufficient for the MVP, or should edge weights be included?**
   - Working MVP: unweighted, because transfer frequency is controlled separately by `mu`.

10. **Is complete mixing within each tank an acceptable simplification if it is clearly stated and tested with sensitivity analysis?**

11. **Should the initial infected tank be uniformly random, or fixed to a non-bridge tank for easier interpretation?**
   - Working plan: uniformly random and paired across strategies to avoid hand-selecting a favourable origin.

## Experimental design

12. **Is the proposed equal-budget definition appropriate?**

```text
cost = number of quarantined tanks × quarantine duration
```

13. **Would quarantining two tanks be a reasonable working budget for a 20-tank network, subject to pilot checks?**

14. **Should no-intervention runs be repeated for each response-delay label, or treated as one shared baseline because delay has no effect without intervention?**

15. **Is 30-50 replicates per condition sufficient if they include multiple network and epidemic seeds?**

16. **Is it useful to run several random-policy seeds for each fixed network/epidemic pair to estimate tank-selection variance?**

17. **Are paired effect sizes and confidence intervals sufficient, or is a specific statistical test expected?**

## Assessment requirements

18. **Have the final report format, page limit, technical submission format and rubric been released?**

19. **What exact GitHub collaboration evidence will be checked: commits, issues, pull-request reviews, or all of these?**

20. **Is a conceptual diagram sufficient for Checkpoint 1 before the baseline model is implemented?**

## Decisions to record immediately after meeting

- response-delay definition；
- primary headline metric；
- independent-investigation adequacy；
- network and centrality scope；
- quarantine count/duration guidance；
- expected replication/statistical evidence；
- any newly released rubric/submission requirements。
