# Autopilot Execution Protocol

> Detailed execution checklist when running workflows in Autopilot Mode.
> Reference strictly during workflow execution.

## Activation Patterns

| User Command | Behavior |
|---|---|
| "run in autopilot mode", "execute workflow automatically", "fully automated run" | Sets `autopilot.enabled: true` in SOT and starts workflow |
| "disable autopilot", "switch to manual mode" | Sets `autopilot.enabled: false` in SOT — applies from next `(human)` step |

## Checkpoint Behaviors

| Checkpoint | Autopilot Behavior |
|---|---|
| `(human)` + Slash Command | Generates complete deliverable → auto-approves using quality-maximizing defaults → writes Decision Log |
| AskUserQuestion | Automatically selects the quality-maximizing option → writes Decision Log |
| `(hook)` exit code 2 | **NO CHANGE** — strictly blocked, feedback delivered, rework mandated |

## Decision Logs

Auto-approved decisions are recorded in `autopilot-logs/step-N-decision.md`: step, options, and selection rationale (grounded in Absolute Criterion 1).
Standard Decision Log Template: `references/autopilot-decision-template.md`.

## Runtime Enforcement Mechanisms

| Layer | Mechanism | Enforcement Details |
|---|---|---|
| **Hook** (Deterministic) | `restore_context.py` — SessionStart | Injects 6 execution rules + prior step deliverable validation results into context |
| **Hook** (Deterministic) | `generate_snapshot_md()` — Snapshot | Preserves Autopilot state + Agent Team state in IMMORTAL priority section |
| **Hook** (Deterministic) | `generate_context_summary.py` — Stop | Detects auto-approval patterns → backfills missing Decision Logs (safety net) |
| **Hook** (Deterministic) | `update_work_log.py` — PostToolUse | Tracks step progression via `autopilot_step` field |
| **Prompt** (Behavioral) | Execution Checklist (below) | Specifies mandatory actions at start, during, and after each step |

> The Hook layer accesses the SOT in read-only mode (Absolute Criterion 2 compliant), writing only to `context-snapshots/` and `autopilot-logs/`.

---

## Execution Checklist (MANDATORY)

When executing a workflow in Autopilot mode, the following checklist **MUST** be performed at every step:

### Before Starting Each Step
- [ ] Confirm SOT `current_step`
- [ ] Verify prior step deliverable exists on disk and is non-empty
- [ ] Verify prior step deliverable path is recorded in SOT `outputs`
- [ ] Read step `Verification` criteria — internalize the definition of "100% completion" upfront (`AGENTS.md §5.3`)

### During Step Execution
- [ ] Execute all tasks in the step **completely** (no abbreviations — Absolute Criterion 1)
- [ ] Produce deliverables with **uncompromised quality**

### After Step Completion (Verification Gate — steps with `Verification` field)
- [ ] Persist deliverable file to disk
- [ ] Self-verify deliverable against each declared `Verification` criterion
- [ ] If any criterion fails:
  - [ ] Check & increment P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate verification --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** (see diagnosis subsection) → rerun based on diagnosis
  - [ ] `can_retry: false` → Escalate to user (budget exhausted, counter not incremented)
- [ ] Verify all criteria evaluate to PASS
- [ ] Generate `verification-logs/step-N-verify.md`
- [ ] Run P1 verification: `python3 .claude/hooks/scripts/validate_verification.py --step N --project-dir .`
- [ ] Confirm P1 verification result is `valid: true` (V1a-V1c passed)

### After Step Completion (Cross-Step Traceability — steps requiring traceability)
- [ ] Ensure deliverable includes >= 3 `[trace:step-N:section-id]` markers
- [ ] Confirm all markers refer strictly to previous steps (no forward references)
- [ ] Run P1 verification: `python3 .claude/hooks/scripts/validate_traceability.py --step N --project-dir .`
- [ ] Confirm P1 verification result is `valid: true` (CT1-CT5 passed)
- [ ] Re-verify marker precision if CT3 WARNING (unresolved section ID) occurs

### After Step Completion (Domain Knowledge Structure — workflows using DKS)
- [ ] If step builds `domain-knowledge.yaml`: run P1 check `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir .`
- [ ] Confirm `valid: true` (DK1-DK5 passed)
- [ ] If step references DKS (`[dks:xxx]` markers): run P1 check `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir . --check-output --step N`
- [ ] Confirm `valid: true` (DK6-DK7 passed)

### After Step Completion (pACS — executed after passing Verification Gate)
- [ ] Answer all 3 Pre-mortem Protocol questions (`AGENTS.md §5.4`)
- [ ] Score Faithfulness, Completeness, Logic → calculate pACS = min(F, C, L)
- [ ] Generate `pacs-logs/step-N-pacs.md`
- [ ] Update SOT `pacs` field (`current_step_score`, `dimensions`, `weak_dimension`, `history`)
- [ ] On pACS RED (< 50):
  - [ ] Check & increment P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate pacs --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** → rework and rescore based on diagnosis
  - [ ] `can_retry: false` → Escalate to user (budget exhausted)
- [ ] On pACS YELLOW (50-69): Record weak dimension in Decision Log, then proceed
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_pacs.py --step N --check-l0 --project-dir .`
- [ ] Confirm P1 validation result is `valid: true` (PA1-PA7 + L0 passed)
- [ ] Record deliverable path in SOT `outputs`
- [ ] Increment SOT `current_step` by +1
- [ ] If `(human)` step: Generate `autopilot-logs/step-N-decision.md`
- [ ] If `(human)` step: Append to SOT `auto_approved_steps`

### Additional Checklist for `(team)` Steps
- [ ] Immediately after `TeamCreate` → Record SOT `active_team` (`name`, `status`, `tasks_pending`)
- [ ] Each Teammate self-verifies against assigned task criteria before reporting (L1 — `AGENTS.md §5.3`)
- [ ] Each Teammate performs pACS self-rating upon passing L1 (L1.5 — include score in report message)
- [ ] Upon Teammate completion → Team Lead executes comprehensive validation against step criteria (L2) and computes step pACS
- [ ] On L2 FAIL or Teammate pACS RED → SendMessage with specific actionable feedback and rerun instruction
- [ ] Upon Teammate completion → Update SOT `active_team.tasks_completed` and `completed_summaries`
- [ ] Upon all tasks completing → Record SOT `outputs`, increment `current_step` by +1, set `active_team.status` to `all_completed`
- [ ] Immediately after `TeamDelete` → Move SOT `active_team` to `completed_teams`
- [ ] Confirm Teammate deliverables contain Decision Rationale and Cross-Reference Cues

### After Step Completion (Adversarial Review — steps with `Review: @reviewer|@fact-checker`)
- [ ] Invoke designated agent as Sub-agent (recommended: `isolation: "worktree"` to protect Orchestrator context; see `reviewer.md § Context Isolation`)
- [ ] Persist review report to `review-logs/step-N-review.md`
- [ ] Run P1 validation: `python3 .claude/hooks/scripts/validate_review.py --step N --project-dir . --check-pacs-arithmetic`
- [ ] Confirm P1 validation result is `valid: true` (R1-R5 passed)
- [ ] Evaluate verdict:
  - [ ] PASS → Proceed to next step
  - [ ] FAIL → Check & increment P1 retry budget: `python3 .claude/hooks/scripts/validate_retry_budget.py --step N --gate review --project-dir . --check-and-increment`
  - [ ] `can_retry: true` → **Perform Abductive Diagnosis** → rework based on diagnosis
  - [ ] `can_retry: false` → Escalate to user (budget exhausted)
- [ ] If pACS Delta >= 15 → Record in Decision Log and document recalibration rationale
- [ ] Never proceed if Review status is FAIL

### Abductive Diagnosis on Quality Gate FAIL
- [ ] Step A — P1 Pre-evidence Collection: `python3 .claude/hooks/scripts/diagnose_context.py --step N --gate {verification|pacs|review} --project-dir .`
- [ ] Check Fast-Path: if `fast_path.eligible == true` → FP1/FP2 reruns immediately; FP3 escalates to user
- [ ] If no Fast-Path applies → Step B — LLM Diagnosis: Analyze root causes based on evidence bundle and hypothesis priority
- [ ] Persist diagnosis log: `diagnosis-logs/step-N-{gate}-{timestamp}.md`
- [ ] Step C — P1 Post-Validation: `python3 .claude/hooks/scripts/validate_diagnosis.py --step N --gate {verification|pacs|review} --project-dir .`
- [ ] Confirm P1 result is `valid: true` (AD1-AD10 passed)
- [ ] Execute rework grounded in the selected hypothesis (H1/H2/H3/H4)

---

## NEVER DO

- Never increment `current_step` by more than +1 at once.
- Never proceed to the next step without an existing, verified deliverable on disk.
- Never abbreviate or cut corners because it is "automated" — direct violation of Absolute Criterion 1.
- Never ignore a Safety Hook block (`(hook)` exit code 2).
- Never allow a Teammate in a `(team)` step to directly modify the SOT — only Team Lead updates SOT.
- Never initialize `active_team` to an empty object upon session restore — always preserve `completed_summaries`.
- Never proceed to the next step while Verification criteria evaluate to FAIL — retry up to 10 times (15 with ULW), then escalate to user.
- Never falsely record criteria as "ALL PASS" without concrete verifiable Evidence.
- Never assign pACS scores without performing the Pre-mortem Protocol.
- Never perform pACS in isolation without the Verification Gate — L1 PASS is the prerequisite for L1.5.
- Never grant indiscriminate scores of 90+ across all dimensions — scores must reflect Pre-mortem vulnerabilities.
- Never mark Review as PASS with 0 identified issues — P1 validation will reject it (R5 check).
- Never score Reviewer pACS by copying Generator pACS — independent scoring is mandatory.
- Never retry a failing quality gate with the exact same approach without diagnosis — Abductive Diagnosis or Fast-Path is mandatory.
- Never record only 1 hypothesis in a diagnosis log — minimum 2 competing hypotheses required (AD8).
- Never select the same hypothesis 3 consecutive times in diagnosis — triggers FP3 user escalation.
