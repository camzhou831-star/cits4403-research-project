# CITS4403 Research Project

## Bridge Transfers and Quarantine in a Captive Turtle Farm

This repository holds the research design, model implementation, computational experiments, analysis and report for the CITS4403 Research Project. The project uses fully synthetic data to study disease spread and movement restrictions in a modular tank housing system. It is a **stylised explanatory model**: it does not predict any real turtle disease and uses no real turtle-farm customer data.

## Team

| Role | Name | GitHub | Contact |
|---|---|---|---|
| Member A | Cam Zhou | `camzhou831-star` | To be confirmed by the team |
| Member B | Wenhao Zhang | `Winston-2hang` | To be confirmed by the team |

- Deadline: Friday 9 October 2026, 11:59pm AWST (Week 1 lecture slides, Assessment table). Submission: the report, through Turnitin on LMS.
- Demonstration: Week 12.

## Status (8 October 2026)

| Part | State |
|---|---|
| Model (`src/turtlefarm/`) | Complete: SIR within tanks, modular network, network-constrained movement, tank quarantine (random / highest-betweenness), event-keyed paired randomness, batch runner. 202 tests pass. |
| Pilot | Run; formal settings recorded (`beta` 0.2, `gamma` 0.1, transfer levels 0 / 0.01 / 0.025 / 0.1, delays 1 / 12 / 33 days, `D` 14). `D` 14 selected by Q1-Q3 under the operational rule-attribution definition: 95.7% of started runs had an attempt intercepted by a quarantine rule, not necessarily an additional successful transfer prevented. See `docs/pilot-report-2026-10-06.md`. |
| Formal experiment | `formal-nested`: 5,200 runs, 20 networks, 100 nested epidemic seeds; none failed or censored. |
| Analysis and figures | `results/analysis/formal-nested/` (tables, figures 1-7). |
| Report | Full draft in `report/report.md`, rendered from `report/report.template.md`; every result number is filled from `results/`. PDF (`report/report.pdf`, A4, 11pt, 1-inch margins) built by `scripts/build_report_pdf.py`, which checks the five-page limit of the rubric. |
| Review | PRs #34 and #36 merged on 7 October; #37 (demo video), #39 (notebook), #42 (five-page report) and #43-#47 (decision confirmations, repository layout, exploratory analysis, demo plan, random-arm limitation) on 8 October. D004 and D005 were confirmed retrospectively (#43, closing #4 and #5); the pilot-protocol and extended-grid sign-offs are still pending. Issue #18 remains open. |
| Decision follow-up | D=14 criterion table reproduced from the recorded Stage 2 runs. The expanded 30-seed network check passes C1 but has one C4 rank-2 tie; both tied tanks are selected. See `docs/network-audit-2026-10-08.md`. |

Deviations from our own protocol are disclosed in `docs/decision-log.md` (sections "Protocol deviations" and "Analysis decisions made after the formal results") and in the report. The most important are:

- the pilot ran before Member B signed the protocol;
- the Stage 1 transfer grid was extended after the first round failed;
- Q1's denominator was changed after the Stage 2 data were seen; review then showed the mixed blocked-transfer counter could not measure Q1, so cause-specific counters were pre-registered, added, and the Stage 2 pilot rerun (outcomes unchanged; Q1 met);
- the first formal run crossed epidemic seeds with networks and was rerun with nested seeds.
- the promised expanded structural check was performed after the formal experiment; it passes generation stability but fails the original no-rank-2-tie clause once, as disclosed in the follow-up audit and report.

### Main findings (details and uncertainty in the report)

These findings come from the original 5,200-run `formal-nested` experiment. The separate follow-up below does not replace that result set or update the report.

- **Transfer rate** controls whether outbreaks stay local. Between transfer rates 0.01 and 0.025, most outbreaks change from staying in one region to crossing regions.
- **Quarantine** of 2 tanks for 14 days has a modest effect. The original means suggested different delay patterns for targeted and random selection. The [subsequent paired delay contrasts](docs/followup-results.md#direct-delay-comparisons-in-the-original-experiment) do not establish a universal timing order.
- **Targeted versus random:** under this budget, targeted quarantine did not beat random quarantine in general. Only one of nine transfer-rate × delay conditions shows an interval excluding zero.

## Proposed system

- 200 synthetic turtle agents are distributed across 20 tanks.
- The 20 tanks form a modular transfer network with 4 regions.
- An agent's disease state is one of `S / I / R` only.
- A tank's management state is one of `open / quarantined` only.
- Tank-level quarantine blocks transfers into and out of that tank for a fixed period, while transmission inside the tank continues.
- A few tanks that connect different regions may have high betweenness centrality and act as bridge tanks.

## Research questions

**Primary research question**

> How do cross-tank transfer rate and response delay affect the final outbreak size and the number of affected tanks in a modular captive-turtle housing system?

**Secondary research question**

> Under the same intervention budget, does quarantining high-betweenness tanks reduce disease spread more effectively than quarantining randomly selected tanks?

## Hypothesis

> A low but non-zero cross-tank transfer rate may allow a local outbreak to spread between otherwise separated tank groups, increasing the final attack rate and the number of affected tanks. Longer response delays are expected to reduce the effectiveness of quarantine because more cross-group transmission can occur before movement restrictions begin. Under the same intervention budget, quarantining high-betweenness tanks is expected to reduce cross-group transmission, final attack rate, and the number of affected tanks more effectively than random tank quarantine.

## Modelling approach

The project uses a discrete-time agent-based model (ABM) on a fixed tank-transfer network:

- the agent layer describes SIR disease state, current tank, within-tank transmission, recovery and individual transfers;
- the network layer describes which tank pairs allow transfers and the modular region structure;
- the management layer compares `No intervention`, `Random tank quarantine` and `Highest-betweenness tank quarantine`;
- the main experiment varies only cross-tank transfer rate, response delay and intervention strategy;
- every stochastic condition uses a traceable network seed, epidemic seed and random-policy seed.

The full specification is in [docs/model-specification.md](docs/model-specification.md).

![Conceptual system diagram](docs/figures/concept-diagram.png)

*Conceptual diagram (schematic, no simulated data): regions, bridge tanks, S/I/R agents, open and quarantined tanks, and the daily update order. Regenerate with `python scripts/draw_concept_diagram.py`.*

## Reproducing the results

Python 3.12, with dependencies pinned in `requirements.txt`.

```bash
uv venv --python 3.12 .venv          # or: python3.12 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt   # or: pip install -r requirements.txt
python -m pytest -q                  # 202 tests

# pilot (about 4 minutes in total) and parameter selection
python scripts/run_experiment.py experiments/config/pilot-stage1-disease.json
python scripts/run_experiment.py experiments/config/pilot-stage1-disease-r2.json
python scripts/pilot_select.py stage1 --design pilot-stage1-disease-r2 --force   # rewrites the committed Stage 2 design
python scripts/run_experiment.py experiments/config/pilot-stage2-intervention.json
python scripts/pilot_select.py stage2  # selects D=14

# formal experiment (about 2 minutes), analysis, figures and report
python scripts/run_experiment.py experiments/config/formal-nested.json
python scripts/analyse_results.py formal-nested
python scripts/mechanism_analysis.py   # exploratory measures of report Section 4.4
python scripts/build_report.py
```

Raw run records go to `results/raw/*.jsonl`. They are append-only and git-ignored, because they are large and fully regenerable: the scientific draws depend only on the configuration and seeds. Per-run summaries, pilot criterion tables and analysis outputs are committed.

Q1 is evaluated from the rule-attribution counters (`blocked_quarantine_out`, `blocked_quarantine_in`, `blocked_capacity`). All three must be present and complete; otherwise `pilot_select.py stage2` reports Q1 as unverified and exits 3, including for older records without the counters. Origin quarantine is checked before capacity, so Q1 does not establish how many additional transfers would have succeeded without quarantine. The historical mixed-counter table is preserved in `results/pilot/stage2-criteria-legacy-proxy.csv`.

`scripts/run_experiment.py` refuses to overwrite an existing raw file; pass `--resume` to continue one. Resume skips every recorded configuration, including failed runs. Failures belonging to the current design count towards its cumulative failure limit, and a recorded invariant failure or an exceeded limit stops continuation before any new records are written. Investigate a halted batch and retain its raw file; after a documented correction, use a separately named design/output for the rerun rather than deleting failed records.

After a full rerun, `git status` should show no change to `experiments/config/` or `results/pilot/`. The 6 October 2026 clean-environment reproduction check predates the blocked-by-cause counters; its criterion table is preserved as `stage2-criteria-legacy-proxy.csv`.

### Quarantine follow-up (9 October 2026)

The [follow-up protocol](docs/followup-protocol.md) and [configuration](experiments/config/followup-duration-policy.json) were committed in `03fbb54` before the follow-up simulations. The original results were already known. All 19,000 follow-up runs completed with no failures or censoring, using implementation `6832e6d`. All 400 replayed original conditions match the recorded scientific fields. The [follow-up results](docs/followup-results.md) describe the direct delay comparisons, broader random-policy sample, duration effects and event observations separately from the original 5,200 formal runs.

At transfer rate 0.025, the follow-up crosses durations of 7, 14 and 28 days with response delays of 1, 12 and 33 days. It keeps the disease parameters, capacity, network generator and epidemic rules fixed. Each of the same 20 networks has five nested epidemic replicates and 20 random-policy draws. A policy draw is reused across those replicates, durations and delays within its network. Different seeds may select the same tank pair, so 20 draws do not imply 20 distinct pairs. The study records duplicates and region coverage without replacing seeds.

Each of the 100 network/epidemic blocks contains one shared baseline and `3 durations x 3 delays x (1 targeted + 20 random)` intervention runs, giving 19,000 runs. Within a duration, targeted and random quarantine have the same budget, `2 x D` tank-days when activated. Comparing durations also changes cost. Reusing the original 20 networks and 100 epidemic blocks makes this a paired sensitivity study, not independent confirmation on new outbreaks.

Run from the repository root after installing the dependencies above:

```bash
# inspect the planned design without running simulations
.venv/bin/python scripts/run_followup.py experiments/config/followup-duration-policy.json --dry-run

# run the separate follow-up batch
.venv/bin/python scripts/run_followup.py experiments/config/followup-duration-policy.json --workers 4

# continue an existing batch without retrying recorded configurations
.venv/bin/python scripts/run_followup.py experiments/config/followup-duration-policy.json --workers 4 --resume

# reproduce follow-up analysis from saved inputs
.venv/bin/python scripts/analyse_followup.py
```

Compact, append-only records go to the git-ignored `results/raw/followup-duration-policy.jsonl`, and the per-run table is `results/summary/followup-duration-policy.csv`. Analysis outputs go to `results/analysis/followup-duration-policy/`. Keep these outputs separate from `formal-nested`. Resume retains failed records, requires matching protocol and schema versions and a single implementation commit, and applies the cumulative failure guard before appending more records. Duplicate or altered configurations are refused. To reproduce into a different directory, pass `--output-dir PATH` to the runner, then give the analysis script `--followup PATH/summary/followup-duration-policy.csv --output PATH/analysis/followup-duration-policy`.

The runner uses an exclusive `<raw>.lock` marker, normally `results/raw/followup-duration-policy.jsonl.lock`, to prevent overlapping coordinators. A hard crash can leave this marker behind. Inspect its PID and hostname and confirm that the coordinator is no longer active before removing only the lock and using `--resume`. Do not remove the raw data or a live process's lock. The recorded batch predates this runner hardening and retains its `6832e6d` provenance; the scientific rules are unchanged.

The analysis uses the original formal summary for direct delay contrasts at all non-zero transfer rates and the follow-up summary for duration and broader random-policy comparisons. Check complete paired blocks, recorded run keys, status counts and agreement of replayed original conditions before interpreting outcomes. The analysis command reads saved summaries and does not run simulations or rebuild the report.

The observer records infectious arrivals across regions and local infection events without changing random draws or epidemic rules. It distinguishes an infectious agent arriving outside the initial region from an S-to-I event there, including arrivals followed by recovery on the same day. A local infection event does not identify its infector or establish a transmission generation. Definitions and missing-value rules are in [the result schema](docs/run-result-schema.md#11-follow-up-observation-and-compact-records).

Follow-up comparisons use 2,000 whole-network bootstrap resamples with analysis seed `20261009`. Their intervals are pointwise, without a multiple-comparison adjustment; the contrasts are exploratory and correlated. Prefixes of 5, 10 and 20 policy draws assess descriptive stability, but network intervals do not capture every source of policy-sampling uncertainty. Sensitivity to disease parameters, capacity, new disease mechanisms and other network structures remains outside this follow-up. The report and its generation scripts are unchanged.

### Optional PDF export

The model and analysis use the Python dependencies above; notebook tools are listed separately in `requirements-notebook.txt`. Rebuilding `report/report.pdf` also requires **Chrome or Chromium** and **Poppler**, whose `pdfinfo` command must be on `PATH`. These are system tools and are not installed by `pip` or `uv pip`. On macOS with Homebrew, install Poppler with `brew install poppler`; install Chrome or Chromium separately if needed.

Check `pdfinfo -v` before exporting. The script finds a standard macOS Chrome installation or `google-chrome`, `chromium` or `chrome` on `PATH`. For another location, set `CHROME` to the browser executable, for example `export CHROME="/path/to/chromium"`.

```bash
python scripts/build_report.py
python scripts/build_report_pdf.py
```

The second command writes the submission PDF and a text-only page-count copy under `results/tmp/`, then checks the five-page limit. The committed PDF can be read without these export tools. Regenerating the optional backup video separately requires `ffmpeg`; see [docs/demo-video.md](docs/demo-video.md).

## Documentation map

### Project notebook

[notebooks/project-walkthrough.ipynb](notebooks/project-walkthrough.ipynb) explains the model rules and parameters, runs a paired example, shows daily updates, and presents the formal results with network-cluster confidence intervals. It includes saved tables and figures, so it can also be read without running the cells.

To run it, install the notebook tools in the project environment:

```bash
source .venv/bin/activate
uv pip install -r requirements-notebook.txt   # or: python -m pip install -r requirements-notebook.txt
python -m jupyterlab notebooks/project-walkthrough.ipynb
```

In VS Code, open the notebook and select the project's `.venv` Python interpreter using the Jupyter extension. In either editor, choose **Restart Kernel and Run All**. Run the notebook from within the repository so it can find the package and result files.

The notebook runs five example simulations and recalculates the displayed statistics from committed summaries. It does not run a new formal batch or write to the model, configurations, result tables or report. Its setup instructions and parameter cells are included in the notebook.

For a command-line check that preserves the saved notebook:

```bash
python -m jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.timeout=180 \
  --output-dir=results/tmp/notebook-check notebooks/project-walkthrough.ipynb
```

| File | Purpose |
|---|---|
| `notebooks/project-walkthrough.ipynb` | Runnable model walkthrough and formal-result analysis, with saved outputs |
| `report/report.md` | **Report draft** (generated; edit `report/report.template.md`) |
| `docs/research-proposal.md` | System, motivation, research questions, contribution and scope |
| `docs/model-specification.md` | Consistent model specification that can be implemented independently |
| `docs/assumptions.md` | Numbered assumptions, their impact and sensitivity needs |
| `docs/experiment-plan.md` | Main experiment, paired design, replication, analysis and figure plan |
| `docs/followup-protocol.md` | Separate duration and random-policy sensitivity study, recorded before its simulations |
| `docs/followup-results.md` | Completed follow-up results, replay checks, source tables and interpretation limits |
| `docs/validation-plan.md` | Invariants, extreme cases and validation evidence plan |
| `docs/pilot-protocol.md` | Two-stage pilot design and selection criteria, written before any pilot data |
| `docs/pilot-report-2026-10-06.md` | Pilot results, every candidate's criteria, selected parameters |
| `docs/decision-log.md` | Decisions D001-D008, parameter freeze, protocol deviations, post-hoc analysis decisions, review record |
| `docs/run-result-schema.md` | Original raw-run contract (`turtlefarm.run.v1`) and separate follow-up observation definitions |
| `docs/collaboration-plan.md` | Communication, GitHub workflow, review rules and the evidence-based contribution record |
| `docs/figures/concept-diagram.png` | Conceptual system diagram (issue #17) |
| `docs/network-audit-2026-09-11.md` | Structural audit of the network generator, D005 candidate values |
| `docs/network-audit-2026-10-08.md` | Retrospective 30-seed audit, complete grid and the C4 tie limitation |
| `docs/model-walkthrough.md` | Ten-minute daily-update and invariant walkthrough guide; actual session record pending (#18) |
| `docs/demo-plan.md` | Week 12 demonstration: requirements, run of show, live run, code walkthrough map, likely questions |
| `docs/demo-video.md` | Backup video for the demonstration |
| `docs/hand-trace-3tank.md` | Hand-traced 3-tank scenario, checked against `tests/test_hand_trace.py` |
| `docs/checkpoint-1-*.md`, `docs/checkpoint-2-speaking-notes.md` | Checkpoint briefs, speaking notes and rehearsals |
| `docs/timeline.md`, `docs/risk-register.md`, `docs/facilitator-questions.md`, `docs/literature-plan.md`, `docs/consistency-review.md`, `docs/week-plan-2026-09-05.md` | Planning records |

| Script | Purpose |
|---|---|
| `scripts/run_experiment.py` | Run a design from `experiments/config/*.json`; raw JSONL plus a per-run summary table |
| `scripts/pilot_select.py` | Apply the pre-registered pilot selection rules; writes the Stage 2 design |
| `scripts/analyse_results.py` | Tables and figures 1-7 for a formal design |
| `scripts/run_followup.py` | Separate 19,000-run duration and random-policy sensitivity design, with dry-run and resume modes |
| `scripts/analyse_followup.py` | Paired delay/duration contrasts, policy coverage and observation summaries from saved inputs |
| `scripts/build_report.py` | Render `report/report.md` from the template and result files |
| `scripts/build_report_pdf.py` | Render `report/report.pdf` (A4, 11pt, 1-inch margins) and check the five-page limit |
| `scripts/mechanism_analysis.py` | Exploratory position and timing measures for report Section 4.4 (`mechanism.json`) |
| `scripts/demo_final.py` | Live demonstration: rerun one paired block and check it against the stored records |
| `scripts/make_presentation_assets.py` | Slide images that are not report figures: timing chart and example animation |
| `scripts/make_demo_video.py` | 3-minute backup video of the demonstration |
| `scripts/draw_concept_diagram.py` | Draw the conceptual diagram |
| `scripts/audit_network.py` | Re-run the network structural audit |
| `scripts/demo_checkpoint2.py` | Checkpoint 2 demonstration (one seed block, not a result) |
| `scripts/create_github_issues.sh` | Create milestones, labels and the first issues |

## Repository structure

The layout follows the structure required by the project specification (`src/`, `utils/`, `data/`, `notebooks/`, `requirements.txt`, `README.md`), with tests, scripts, experiment designs, results, the report and documentation alongside.

```text
src/turtlefarm/  main code: SIR within tanks, event-keyed draws, network, movement, quarantine, batch runner, analysis
utils/           helper functions used by the scripts: network layout for figures, report number formatting
data/            no external dataset; README explains where the synthetic inputs and outputs live
notebooks/       executable model walkthrough, result comparisons and figures
requirements.txt dependencies (requirements-notebook.txt adds the notebook tools)
README.md        this overview, setup and usage
tests/           invariant, extreme-case, paired-draw, hand-trace, movement, quarantine, runner and analysis tests
scripts/         command-line entry points: experiments, pilot selection, analysis, report, PDF, figures, demo video
experiments/     experiment designs (experiments/config/*.json): smoke, pilot stages, formal, formal-nested, follow-up
results/         raw/ (git-ignored), summary/ (per-run tables), pilot/ (criteria), analysis/ (tables, figures), demo/
report/          report template, generated report and PDF
docs/            design, decisions, protocols, reports and figures
```

Scripts add `src/` and the repository root to the import path themselves, and `pytest` reads the same paths from `pyproject.toml`, so no package installation step is needed.

## Academic integrity boundary

The earlier `turtle-farm` project provides domain inspiration only. This project does not copy that project, the CITS4403 Lab Notebook, assessed work from CITS4012, CITS1401 or CITS5501, or restricted third-party code. The model, synthetic data, rules, experiments, analysis and text are all designed anew for this project.

## Use of AI tools

Most of Member A's commits were written with Claude (Claude Code). Commits up to 6 October 2026 carry a `Co-Authored-By: Claude` line; later commits do not carry the line, and AI assistance continued. Codex CLI was used for read-only acceptance reviews. Every suggestion was checked by a team member before being kept, and the team is responsible for all content. Counts are recorded in `docs/collaboration-plan.md` section 8.
