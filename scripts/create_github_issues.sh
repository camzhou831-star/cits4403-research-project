#!/usr/bin/env bash
# Create milestones, labels and the first batch of issues for the CITS4403 project.
# Usage:
#   scripts/create_github_issues.sh --dry-run   # print what would be created
#   scripts/create_github_issues.sh             # create on GitHub (requires gh auth)
# Safe to re-run: existing labels/milestones are skipped; issues with an identical title are skipped.
set -euo pipefail

REPO="camzhou831-star/cits4403-research-project"
A="camzhou831-star"
B="Winston-2hang"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

run() { if [[ $DRY -eq 1 ]]; then echo "+ $*"; else "$@"; fi; }

# ---------- labels ----------
declare -a LABELS=(
  "decision|Pending or recorded modelling decision|5319e7"
  "must-have|Required for the primary experiment or submission|b60205"
  "should-have|Improves quality; can be cut under time pressure|fbca04"
  "model|Model rules, states, update order|0e8a16"
  "network|Transfer network generation and centrality|1d76db"
  "validation|Tests, invariants, traces|006b75"
  "experiment|Runner, configs, seeds, pilot|c2e0c6"
  "analysis|Statistics and figures|bfd4f2"
  "report|Report, checkpoint, presentation|d4c5f9"
)
existing_labels=$(gh label list --repo "$REPO" --limit 100 --json name --jq '.[].name')
for entry in "${LABELS[@]}"; do
  IFS='|' read -r name desc color <<<"$entry"
  if grep -qx "$name" <<<"$existing_labels"; then echo "label exists: $name"; continue; fi
  run gh label create "$name" --repo "$REPO" --description "$desc" --color "$color"
done

# ---------- milestones ----------
declare -a MILESTONES=(
  "M1 Baseline model|2026-09-11T23:59:00Z"
  "M2 Movement, intervention, runner|2026-09-18T23:59:00Z"
  "M3 Pilot and formal experiments|2026-09-25T23:59:00Z"
  "M4 Analysis and report|2026-10-02T23:59:00Z"
  "M5 Freeze and submission|2026-10-09T23:59:00Z"
)
existing_ms=$(gh api "repos/$REPO/milestones?state=all" --jq '.[].title')
for entry in "${MILESTONES[@]}"; do
  IFS='|' read -r title due <<<"$entry"
  if grep -qxF "$title" <<<"$existing_ms"; then echo "milestone exists: $title"; continue; fi
  run gh api "repos/$REPO/milestones" -f title="$title" -f due_on="$due" --silent
done

# ---------- issues ----------
existing_issues=$(gh issue list --repo "$REPO" --state all --limit 200 --json title --jq '.[].title')
mk() { # title | labels | milestone | assignee | body
  local title="$1" labels="$2" ms="$3" assignee="$4" body="$5"
  if grep -qxF "$title" <<<"$existing_issues"; then echo "issue exists: $title"; return; fi
  run gh issue create --repo "$REPO" --title "$title" --label "$labels" --milestone "$ms" --assignee "$assignee" --body "$body"
}

DEC_BODY_TAIL=$'\n\nClose this issue only after recording: chosen value, alternatives considered, reason, source (facilitator/team), date. Then update docs/decision-log.md and the documents listed in docs/consistency-review.md section 6.'

mk "D001 Response-delay origin: introduction vs first detection" "decision,must-have,model" "M1 Baseline model" "$A" \
"Working proposal: delay measured from outbreak introduction at t=0 (spec section 11). Facilitator question 7.$DEC_BODY_TAIL"
mk "D002 Fixed tank capacity" "decision,must-have,model" "M1 Baseline model" "$A" \
"Working proposal: capacity = 12 for all tanks (spec section 6.2).$DEC_BODY_TAIL"
mk "D003 Quarantined tank count k" "decision,must-have,experiment" "M2 Movement, intervention, runner" "$B" \
"Working proposal: k = 2 (spec section 12). Facilitator question 13.$DEC_BODY_TAIL"
mk "D004 Quarantine duration D" "decision,must-have,experiment" "M3 Pilot and formal experiments" "$B" \
"Working proposal: select after pilot (spec section 11).$DEC_BODY_TAIL"
mk "D005 Network p_in / p_out and acceptance thresholds" "decision,must-have,network" "M2 Movement, intervention, runner" "$A" \
"Working proposal: select after structural pilot; must be modular, connected, non-symmetric (spec section 3.2).$DEC_BODY_TAIL"
mk "D006 max_days horizon" "decision,should-have,model" "M1 Baseline model" "$A" \
"Working proposal: 365 days with censored_max_days status (spec section 14).$DEC_BODY_TAIL"
mk "D007 No-intervention baseline reporting layout" "decision,should-have,analysis" "M4 Analysis and report" "$B" \
"Working proposal: one shared baseline per transfer/network/epidemic block (experiment plan section 3). Facilitator question 14.$DEC_BODY_TAIL"
mk "D008 Headline outcome metric" "decision,should-have,report" "M4 Analysis and report" "$B" \
"Working proposal: final attack rate and affected tanks as co-primary. Facilitator question 6.$DEC_BODY_TAIL"

mk "Record facilitator Checkpoint 1 feedback in decision log" "must-have,report" "M1 Baseline model" "$B" \
"Ask questions in docs/facilitator-questions.md order. Same day: fill docs/decision-log.md meeting record and comment on each D00x issue. Acceptance: decision-log meeting record complete; each D00x issue has an answer or 'no answer, keep working proposal'."
mk "Both members sign off model specification" "must-have,model" "M1 Baseline model" "$A" \
"Each member reads docs/model-specification.md fully, raises questions as comments here, then ticks the sign-off in docs/decision-log.md. Acceptance: both dates filled."
mk "Set up Python environment and requirements.txt" "must-have,model" "M1 Baseline model" "$A" \
"uv venv --python 3.12; install numpy networkx pandas matplotlib pytest; commit requirements.txt. Acceptance: teammate can create identical env from requirements.txt."
mk "Implement minimal SIR baseline (no movement, no intervention)" "must-have,model" "M1 Baseline model" "$A" \
"Branch model/sir-baseline. Scope: config validation, Agent/Tank structures, seed-derived substreams (spec 16), initialisation (spec 6.1), daily order (spec 13) with movement and management as no-ops, transmission 1-(1-beta)^I (spec 7), recovery (spec 8), synchronous commit, stop condition and censored/failed status (spec 14), daily outputs and metadata (spec 15). All provisional config values labelled. Acceptance: PR reviewed by Member B, tests in the validation issue pass."
mk "Write baseline invariant and extreme-case tests" "must-have,validation" "M1 Baseline model" "$B" \
"pytest coverage for V001-V005, V011 same-seed replay, V101 beta=0, V103 gamma=1, V104 beta=1 (docs/validation-plan.md). Acceptance: tests pass on the baseline PR; reviewer confirms 'transmit then recover' rule."
mk "Hand-traced small scenario against model event log" "must-have,validation" "M1 Baseline model" "$B" \
"Fixture: 3 tanks, 6 agents, fixed draws, 3 days computed by hand (validation plan section 9). Both members compare with the event log; differences recorded in the PR. Acceptance: trace matches or every difference is explained and fixed."
mk "Draft run metadata and raw-result schema" "should-have,experiment" "M1 Baseline model" "$B" \
"Field list per experiment plan section 10 and spec 15.2. No results generated. Acceptance: Member A confirms the baseline model can emit every field."
mk "Modular network generator and structural audit" "should-have,network" "M1 Baseline model" "$A" \
"Branch model/modular-network. 4x5 modules, p_in > p_out, connected + inter-region edge checks, attempt index, unweighted normalised betweenness, ties by ascending tank_id (spec 3-4). Audit 5-10 seeds for non-trivial betweenness ranking (risk R002). Only start after the baseline PR is merged."
mk "Conceptual system diagram (non-result)" "should-have,report" "M1 Baseline model" "$B" \
"One figure: regions, bridge tanks, S/I/R agents, open/quarantined tanks, daily update order. No simulated data."
mk "Weekly contribution table and model walkthrough" "should-have,report" "M1 Baseline model" "$B" \
"Update collaboration-plan.md section 8 for W8; Friday 10-minute walkthrough of daily update and invariants presented by Member B."

echo "done (dry-run=$DRY)"
