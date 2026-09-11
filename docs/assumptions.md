# Model Assumptions Register

类别包括 model simplification（模型简化）、computational constraint（计算限制）和 data limitation（数据限制）。

| ID | Assumption | Why needed / reasonableness | Potential effect | Sensitivity | Category |
|---|---|---|---|---|---|
| A001 | 200 个 agents 全为 synthetic population，不对应真实记录 | 避免隐私与经验数据不足；适合解释性实验 | 不代表真实 farm | population size 仅 optional | data limitation |
| A002 | 20-tank modular network 为 synthetic | 没有经授权的 movement logs；可控制结构 | bridge importance 依赖生成规则 | 跨 network seeds；小规模 modularity check | data limitation / simplification |
| A003 | Complete mixing within each tank | 缺少 tank 内空间数据，主问题关注跨缸 | 可能高估均匀接触 | 主实验固定；检查 `beta` | simplification |
| A004 | Homogeneous susceptibility and infectiousness | 无物种、年龄、健康校准；隔离 network effect | 忽略个体异质性和 superspreading | optional heterogeneity | simplification / data limitation |
| A005 | 没有真实 disease calibration | 无可靠兽医数据和 calibration target | 不能外推真实概率和天数 | 小规模 `beta/gamma` robustness | data limitation |
| A006 | Disease progression 只有 `S -> I -> R` | 控制状态空间；MVP 无 E/Q/death/treatment | 改变真实时间尺度的表达 | 在 limitations 讨论，不扩展 MVP | simplification |
| A007 | Recovered agent 在一次 run 中不会再次感染 | 保持 SIR 封闭并允许 extinction | 若真实免疫短暂，会低估后期传播 | future extension | simplification |
| A008 | Permitted-transfer network 在 run 中 static | centrality 稳定；动态性来自 agent movement | 忽略临时 route changes | static/dynamic 为 should-have extension | simplification |
| A009 | 完整 network information 在 intervention 前可获得 | targeted policy 只能用可获得信息 | 不完整观测会降低 policy 表现 | facilitator 确认；optional observation error | simplification / data limitation |
| A010 | Quarantine 完全阻止转入和转出 | 使 intervention 含义明确可验证 | 可能高估现实 compliance | partial compliance optional | simplification |
| A011 | Quarantined tank 内传播和恢复继续 | 分离 movement restriction 与 treatment | 隔离缸内仍可高 attack rate | 固定定义，不做主敏感性 | simplification |
| A012 | Intervention 在固定 response day 立即执行 | 避免 detection/rollout 子模型 | 忽略渐进实施 | delay 是主因素；起点待确认 | simplification |
| A013 | Random/targeted 使用相同 `k`、start、duration | 公平回答 secondary question | 不研究 adaptive release | pilot 冻结 `k,D` | model simplification |
| A014 | S/I/R agents 有相同 movement probability | 无 symptom-dependent movement 证据 | 可能高估 infected transfer | optional disease-dependent movement | simplification / data limitation |
| A015 | 主实验 tanks capacity 相同，initial occupancy 相同 | 避免 capacity 与 centrality 混杂 | 低估 occupancy variation | heterogeneous capacity only sensitivity | simplification |
| A016 | 给定状态后，daily infection/recovery draws 条件独立 | 明确 stochastic process | 无共同环境冲击 | 不在 MVP | simplification |
| A017 | Capacity 是 hard constraint | 避免非法状态 | blocked transfers 改变实际 movement rate | 记录 attempts/acceptance；检查 capacity | simplification / computational |
| A018 | Betweenness ties 按 `tank_id` deterministic | 保持 reproducibility 且不用未来信息 | 对对称网络可能偏好小 ID | 记录 ties；避免对称网络 | computational |

## Mandatory assumption clarifications

### Quarantine timing

当前 working assumption 是 response delay 从 outbreak introduction (`t=0`) 计算，并在相应 day 的 movement stage 前立即激活。若 facilitator 要求从 first observed infection 计算，必须先定义 observation process，不能静默改变。

### Intervention duration and budget

所有 intervention conditions 使用同一 `k` 和 duration `D`：

```text
cost = k × D tank-days
```

`k = 2` 已于 2026-09-11 冻结（D003）；`D` 的语义已冻结，数值在 pilot 后确定（D004）。

## Assumption decision status

已冻结（2026-09-11，`decision-log.md`）：response delay 起点（introduction）、fixed capacity（12）、number of quarantined tanks（2）、maximum simulation horizon（365）。

数值待 pilot 后冻结：quarantine duration `D`、network generation parameters `p_in` / `p_out`。
