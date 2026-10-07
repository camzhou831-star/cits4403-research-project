# Decision Log

Record the final decisions for D001-D008. Each decision must state its source (facilitator / team), date and rationale. Before freezing, all working proposals must be marked `provisional` in the code config.

## Status

| ID | Decision | Working proposal | Final value | Source | Date | Notes |
|---|---|---|---|---|---|---|
| D001 | Response-delay origin | From introduction at `t=0` | From introduction at `t=0` | Team (facilitator raised no objection) | 2026-09-11 | No change to the delay origin was requested at Checkpoint 1 (2026-09-07); working proposal adopted (spec §11) |
| D002 | Tank capacity | 12 | 12 | Team (facilitator raised no objection) | 2026-09-11 | Working proposal adopted |
| D003 | Quarantined tank count `k` | 2 | 2 | Team (facilitator raised no objection) | 2026-09-11 | Working proposal adopted |
| D004 | Quarantine duration `D` | Select after pilot | 14 | Member A (Member B's confirmation pending) | 2026-10-06 | Q1-Q3 met with cause-specific blocking counters (Q1 95.7%), pre-registered before the rerun; `pilot-report-2026-10-06.md` §8 |
| D005 | Network `p_in` / `p_out` | Select after structural pilot | 0.6 / 0.05 | Member A (Member B's confirmation pending) | 2026-10-06 | Structural audit candidate; S1-S6 can be met in the movement pilot with these network parameters, so no replacement is needed |
| D006 | `max_days` | 365 | 365 | Team (facilitator raised no objection) | 2026-09-11 | Working proposal adopted; `censored_max_days` status still recorded |
| D007 | No-intervention reporting | Shared baseline per block | Shared baseline per block | Team (facilitator raised no objection) | 2026-09-11 | Working proposal adopted |
| D008 | Headline outcome | Attack rate + affected tanks co-primary | Attack rate + affected tanks co-primary | Team (facilitator raised no objection) | 2026-09-11 | Working proposal adopted |

## Facilitator meeting record

- Date: 2026-09-07 (Checkpoint 1 facilitator meeting)
- Attendees: Cam Zhou, Wenhao Zhang, facilitator
- Questions asked (numbered according to `facilitator-questions.md`): the system, research questions, modelling approach and GitHub progress were presented using `checkpoint-1-brief.md`
- Answers: the facilitator was satisfied with the project overall, requested no changes to the system scope, research questions, model definitions or experiment design, and raised no objections to the working proposals for D001-D008
- Newly released rubric / submission requirements: no new rubric or submission-format information was obtained at the meeting; check official releases again during 3-8 October according to `timeline.md`

### Recorded conclusions

- D001, D002, D003, D006, D007, D008: the facilitator raised no objection; on 2026-09-11 the team adopted the working proposals as final values and removed their `provisional` labels from the code config.
- D004, D005: already scheduled for determination after the pilot, unaffected by the Checkpoint, and remain open.
- No decision changed, so the cross-document updates in `consistency-review.md` §6 were not triggered.

## Provisional-start decision

- [x] Both members confirmed: baseline SIR (no movement, no intervention) may start before D001-D008 are frozen, with provisional values labelled in the config.
  - Member A confirmation date: 2026-09-07 (comment on issue #10)
  - Member B confirmation date: 2026-09-06 (comment on issue #10, "D001-D008 remain provisional pending confirmation")

## Specification sign-off

- [x] Member A has read `model-specification.md` in full and confirmed the ability to implement it independently. Date: 2026-09-07 (issue #10)
- [x] Member B has read `model-specification.md` in full and confirmed the ability to implement it independently. Date: 2026-09-06 (issue #10)

## Protocol deviations

### 2026-10-06: Stage 1 pilot run before Member B signed the pilot protocol

- Deviation: `pilot-protocol.md` requires both members to confirm the criteria before running the pilot; Member A ran Stage 1 before Member B signed.
- Reason: the deadline was 2026-10-09 and Member B could not be reached that evening; Member A decided to run it to leave time for the formal experiment and report.
- Measures against outcome-driven tuning: the selection criteria (including 5 additions on 2026-10-06) were pushed to PR #34 in commit `d2be9bf` before execution, as was this record. Selection is performed mechanically by `scripts/pilot_select.py` under the pushed criteria.
- If Member B requests changes to the criteria during review: record the changes and reasons in this section, and report selections under both the original and revised criteria, not just the latter.
- Member B retrospective confirmation: pending (date: —)

### 2026-10-06: no candidate passed Stage 1 round 1; transfer grid expanded and stage rerun under rule 5

- Round 1 results (`pilot-stage1-disease`, 2000 runs, failed 0): all 8 `(beta, gamma)` candidates satisfied S1-S4 and S6, and all **failed solely on S5**. Criterion-level table: `results/pilot/pilot-stage1-disease-criteria.csv`.
- Reason for failure: S5 requires at least a twofold difference in mean accepted transfers per day between adjacent levels. The original grid's nominal ratios for 0.01→0.02 and 0.05→0.10 were exactly twofold; capacity blocking reduced measured ratios to about 1.77 and 1.88, so no three-level combination could meet S5.
- Action (rule 5): keep the threshold unchanged; add `0.025` to the transfer grid, yielding `[0, 0.01, 0.02, 0.025, 0.05, 0.1]`, so that `0.01 → 0.025 → 0.1` has nominal spacings of 2.5-fold and 4-fold. All other settings and seeds remain the same as round 1. Rerun all of Stage 1 under design name `pilot-stage1-disease-r2`. Retain the round 1 raw records; delete none.
- Disclosure: Member A chose the new grid after inspecting round 1 summaries of transfer volume, affected tanks and attack rate. The choice of 0.025 was based on transfer-volume ratios, not attack rate. This record was pushed before round 2 ran.
- Member B retrospective confirmation: pending (date: —)

### 2026-10-06: Stage 1 conclusions (round 2, `pilot-stage1-disease-r2`)

- 2400 runs, failed 0. 7/8 candidates satisfied S1-S6; `beta = 0.05, gamma = 0.2` failed S5. Criterion-level table: `results/pilot/pilot-stage1-disease-r2-criteria.csv`.
- Rule 3: all passing candidates have transfer levels `0.01 / 0.025 / 0.1` (largest span).
- Rule 2 (median final attack rate closest to 0.5 at middle level 0.025): selected `beta = 0.2, gamma = 0.1` (median 0.458, distance from 0.5 of 0.042); next closest was `beta = 0.15, gamma = 0.1` (0.435, 0.065).
- Response-delay levels (D1-D3, 40 non-minor runs): **1 / 12 / 33 days** (the D2 and D3 medians were already integers, so no rounding was applied).
- The script generated `experiments/config/pilot-stage2-intervention.json`: transfer levels 0.01 / 0.025 / 0.1, `D` candidates 7 / 14 / 21, policy seeds 900-902, 5550 runs.
- The report must state that, in the selected regime, the no-intervention median attack rate at `transfer_rate = 0.1` is 1.0 (near saturation), so intervention differences at that level may be limited by a ceiling effect.
- Member B retrospective confirmation: pending (date: —)

### 2026-10-06: Stage 2 conclusions; Q1 denominator revised after inspecting the data

- Run: `pilot-stage2-intervention`, 5550 runs, failed 0, censored 0. Historical proxy table: `results/pilot/stage2-criteria-legacy-proxy.csv`; corrected audit: `results/pilot/stage2-criteria.csv`.
- **Under the original definition (all intervention runs), no D candidate satisfied Q1**: the share for all three D values was 85.3% < 90%.
- Historical explanation, corrected after review: 284 / 1800 intervention runs ended before quarantine started, but their `blocked_transfers` is not necessarily zero: 60 per duration have capacity blocks. The started-runs share is 97.3%-97.4%, but both denominators use a mixed whole-run counter and neither verifies quarantine-specific blocking.
- Historical denominator adjustment (Member A, after inspecting the data): the Q1 proxy denominator was changed to runs where quarantine started. The former `Q1_original_all_runs` and `passed_original_q1` flags are preserved in `stage2-criteria-legacy-proxy.csv`; the current evaluator labels both denominators as proxies and leaves quarantine-specific Q1 unverified.
- Only D=14 satisfies Q2 (D ≤ 16.25) and Q3 (D ≥ 10). This narrows the candidates but does not validate Q1; the historical proxy selection must not be described as satisfying all three scientific criteria.
- Historical choice: **D=14**, planned budget 28 tank-days. Retained as the existing formal experiment setting, with Q1 unverified; see the counter correction below.
- Member B retrospective confirmation: pending (date: —)

## Parameter freeze record (experiment-plan §9; 2026-10-06)

| Item | Frozen value | Basis |
|---|---|---|
| `beta` / `gamma` | 0.2 / 0.1 | Stage 1 round 2 rule 2 |
| Transfer-rate levels | 0 / 0.01 / 0.025 / 0.1 | Stage 1 round 2 rule 3 |
| Response-delay levels | 1 / 12 / 33 days | D1-D3 |
| `D` (D004) | 14 | Q1-Q3 with cause-specific counters (2026-10-06 rerun); Q1 denominator still post hoc |
| `p_in` / `p_out` (D005) | 0.6 / 0.05 | Structural audit + pilot |
| Capacity / `k` / `max_days` | 12 / 2 / 365 | D002 / D003 / D006 (2026-09-11) |
| Network seeds | 200-219 (20 seeds) | experiment-plan §8: ≥ 10 networks; increase the number of networks when runtime allows to stabilise the bootstrap clustered by network |
| Epidemic seeds | 10000-10004 (5 per network) | experiment-plan §8: ≥ 5 per network |
| Policy seeds | 1000-1002 (3 per block) | experiment-plan §8: 2-3 |
| Excluded pilot seeds | network 100-104, epidemic 9000-9009, policy 900-902 | pilot-protocol §1 rule 3 |
| Planned runs | 5200 (4 transfer levels × 100 blocks × 13 runs) | `experiments/config/formal.json` |
| Replicates per condition | 100 blocks (≥ 30) | experiment-plan §8 |

- Added analysis scope (recorded before running the formal experiment): report paired effects for both all blocks and blocks where quarantine actually started (the `subset` column in `turtlefarm/analysis.py`); rationale in `pilot-report-2026-10-06.md` §5.
- After the formal experiment starts, do not change these parameters because results disagree with the hypothesis (experiment-plan §9).
- Confirmation by both members: Member A on 2026-10-06; Member B pending.

### 2026-10-06: crossed-seed issue in the first formal experiment (`formal`); rerun with nested seeds

- Problem: the 20 networks in `formal` shared the same 5 epidemic seeds (crossed by the runner using `itertools.product`). With event-keyed draws, the same epidemic seed gives the same initial infected agent and early draws across all networks, so networks are not independent:
  - In the pilot, seeds 9003 and 9006 reached extinction before day 12 in all 5 networks; none of the other 8 seeds did;
  - None of the 5 seeds in `formal` produced early extinction.
- Consequence: `formal` has only 5 independent epidemic starting points. A bootstrap clustered by network assumes independent clusters and will underestimate uncertainty. This conflicts with the "epidemic replicates nested within the same network" design in experiment-plan §5.
- Discovery: **Member A identified this after inspecting the condition summaries and paired effects from `formal`**, prompted by different quarantine-start rates in pilot and formal runs (delay 12: 80% vs 100%). The rerun follows the existing nesting requirement in experiment-plan §5, not the direction of the results.
- Action:
  - Add `nested_epidemic_seeds` to the runner, allocating epidemic seeds sequentially and equally across networks;
  - New design `formal-nested`: network 200-219, epidemic 20000-20099 (5 per network, none shared), policy 1000-1002; parameters identical to the freeze record; 5200 runs.
  - Retain the raw records from `formal`; delete none. Use `formal-nested` as the authoritative formal results, and disclose both runs and the reason in the report.
- Implication for the pilot: its seeds were also crossed, so Stage 1/2 assessments effectively rely on only 10 independent epidemic starting points (variation between networks remains valid). Do not rerun the pilot; disclose this in `pilot-report-2026-10-06.md`.
- Member B retrospective confirmation: pending (date: —)

## Analysis decisions made after the formal results (2026-10-06)

### Q1 mixed-counter correction (review follow-up)

The Stage 2 counter includes capacity blocking and events before/after the active quarantine interval. The earlier inference that a low S6 transfer-blocking fraction makes Q1 mainly a quarantine measure is withdrawn. In the D=14 started-run subset, the matched no-intervention baselines already meet the mixed ≥1-block proxy in 91.8206% of matches. Also, 60 of the 284 never-started runs have nonzero blocking. Reproduction details are in `pilot-report-2026-10-06.md` §7.

Both proxy percentages and their historical selection flags remain available for audit. The current evaluator marks quarantine-specific Q1 as unknown; the CLI exits 3 rather than selecting D automatically. Formal parameters, simulations, analysis tables and figures are unchanged. The report retains D=14 as the tested setting and explicitly discloses missing Q1 validation. Establishing quarantine-caused blocking requires a separate definition, counter and tests; this correction does not claim that work has been completed.

Member A review of this correction: pending. No member's sign-off is inferred from this implementation.

### Q1 measured with cause-specific blocking counters (2026-10-06)

Follow-up to the correction above. Order of events, each a separate commit on `experiment/q1-quarantine-blocking`:

1. `pilot-protocol.md` §4 pre-registered three counters partitioning `blocked_transfers` (origin quarantined / only quarantined neighbours with space / capacity), Q1 on the first two, the reproduction check, and the consequence of each outcome. No cause-specific count existed when this was written.
2. The counters were added to the model, with tests. They draw no randomness.
3. `pilot-stage2-intervention` was rerun. All 27 pre-existing summary columns (excluding `code_commit`, `run_id`, `configuration_hash`) are identical for all 5550 runs.
4. Q1 (started runs with ≥ 1 quarantine block) = 91.8% / 95.7% / 96.7% for D = 7 / 14 / 21. The unchanged rule selects **D=14**, matching the formal experiment. Under the pre-registered consequences, D004 is recorded as validated by Q1-Q3.

Still disclosed as post hoc: the started-runs denominator, and that this measurement came after the formal experiment (a failing Q1 could not have changed it). At transfer level 0.01 and D=14 the share is 90.9%, close to the threshold; Q1 is evaluated pooled over levels, as specified. For comparison, 90.6% of the same started runs had a capacity block, and 80.7% of no-intervention baselines had a blocked transfer of any kind.

Member B review: pending.

### Q1 completeness guard and interpretation (2026-10-07 review follow-up)

The follow-up retains the counter definitions, 90% threshold and duration-selection rule from PR #36. All three cause columns must exist and be non-missing before Q1 is verified; incomplete data leave it unknown and stop automatic duration selection. Regression tests cover missing columns and values, including CLI handling.

Q1 is an operational rule-interception check. A quarantined origin is checked before destination capacity, so its counter includes attempts that would also fail with full neighbours if quarantine were removed. This is not a counterfactual measure of additional transfers prevented or a measure of disease reduction. The protocol, schema, report and speaking notes clarify this distinction after the rerun, without retroactively changing the original definitions or simulated results. Review comments and the follow-up commit record implementation and verification; they do not imply either member has signed the outstanding protocol decisions.

The following decisions were all made after inspecting summary results from `formal` and/or `formal-nested`; each is labelled post-hoc in the report.

| # | Decision | Reason | Location |
|---|---|---|---|
| A1 | Add paired comparisons of "each strategy − the no-intervention baseline in the same block" (`baseline_differences`) as descriptive analysis | The delay effect in research question 1 can only be shown relative to baseline; the original plan compared only targeted with random | `turtlefarm/analysis.py`, report §3.3 / Table 2 |
| A2 | Representative-run rule (Figure 7): classify no-intervention runs at transfer rate 0.025 as local / cross-region; select the run in each class with final attack rate closest to that class's median, breaking ties by smaller seeds | experiment-plan §13 requires an objective rule; the rule was written after viewing only summary results, before inspecting any individual trajectory | `pick_representative_runs`, report Figure 7 |
| A3 | Report the comparison of `formal` (crossed seeds) and `formal-nested` (cells whose intervals do not cross 0: 7 vs 2) | Disclose overstated precision under the crossed design | Report §3.5 |
| A4 | `formal-nested` reuses `formal` network seeds 200-219 and policy seeds 1000-1002, changing only epidemic seeds | The crossing issue arises only from shared epidemic seeds; networks are generated deterministically from seeds, so reusing the same networks isolates the seed-design difference between the two runs | `experiments/config/formal-nested.json` |
| A5 | Change the 95% CIs for condition summaries from a normal approximation to a bootstrap clustered by network | External review found that runs within the same network are not independent and that the normal-approximation upper bound for attack rate at level 0.1 exceeded 1 | `condition_summary`, report Table 1 |
| A6 | Use tolerance 1e-9 when classifying paired differences as wins/losses/ties | External review found that floating-point error (about 1e-17) classified identical outcomes at transfer rate 0 as targeted wins; the report's 52% / 15% / 33% figures are unaffected | `DIFF_TOLERANCE` |
| A7 | `outbreak_class` uses daily snapshots and may miss infected agents that arrive and recover on the same day; `analyse_results.py` automatically lists affected runs | Found in external review; 5/400 baseline runs in `formal-nested` were affected, including 2 classified as local. Reruns confirmed that the affected tanks were all within the initial region, so the classifications were correct | `outbreak-class-check.json` |

External review: Codex CLI performed a read-only acceptance review on 2026-10-06, concluding ACCEPT WITH FIXES, with no Blocker. More than 20 independently recalculated report figures all matched. See PR #34 for the item-by-item responses.

Re-review (round 2): all report-level issues from the previous round were RESOLVED; A4 (reuse of network / policy seeds) was judged DISPUTED-ACCEPTABLE, with its rationale accepted. Independently recalculated figures, including the clustered CIs in Table 1, all matched. Three remaining items:

- Pairing-completeness checks now use the design file, strictly requiring exactly 1 targeted run, the specified number of distinct policy seeds and 1 baseline per block; incomplete blocks are excluded and counted;
- `--n-boot` / `--boot-seed` are now also passed to Table 1;
- The snapshot-based limitation of `outbreak_class` remains (fully resolving it would require changing model output and rerunning all experiments). It is disclosed in code documentation, automated checks and report limitations; the 2 affected runs in the current report have been manually verified.

These fixes change no numerical results in the report (`formal-nested` and `formal` both have 0 incomplete blocks).

## Change history

| Date | Decision changed | Documents updated | PR |
|---|---|---|---|
| 2026-09-11 | None (working proposals adopted as final values for D001-D003 and D006-D008) | `decision-log.md`, `README.md`, `checkpoint-1.md`, `turtlefarm/config.py` (provisional labels removed) | docs/checkpoint-1-feedback (PR #21) |
| 2026-09-11 | Semantic additions: spec §16 randomness changed from "independent substreams" to event-keyed draws (ensuring pairing across strategies); two-layer freeze rule added in §18 | `model-specification.md` §16/§18, `validation-plan.md` §9, `hand-trace-3tank.md` | model/validation-and-paired-rng (PR #22) |
| 2026-09-11 | Structural checks in spec §3.2 step 4 specified as 4 rules; D005 candidate values 0.6 / 0.05 | `model-specification.md` §3.2, `network-audit-2026-09-11.md`, `turtlefarm/network.py` | model/modular-network |
