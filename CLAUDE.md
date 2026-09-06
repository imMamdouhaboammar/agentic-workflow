# AgenticWorkflow

Claude Code-based agent workflow automation project.

## Final Goal

1. **Workflow Design**: Systematically design complex tasks into a 3-stage `workflow.md` (Research → Planning → Implementation).
2. **Workflow Execution**: Actually implement the agents, scripts, and automation pipeline configured in `workflow.md`.

> Designing `workflow.md` is an intermediate blueprint. **Ensuring the workflow actually executes and produces verified deliverables** is the final goal.

### Purpose of Existence — DNA Inheritance

AgenticWorkflow is a **parent organism that gives birth to child agentic workflow systems**. The `workflow-generator` skill serves as the production line, and every child system **structurally embeds** the parent genome (Constitution, Structure, Verification, Safety, Memory, Adversarial Criticism, and Transparency). Details: `soul.md §0`.

## Absolute Criteria

> The top-level rules applied to every design, implementation, and modification decision. These supersede all guidelines and principles below.

### Absolute Criterion 1: Quality of the Final Deliverable
> **Speed, token cost, workload, and length limits are completely ignored.** The sole criterion for every decision is the **quality of the final deliverable**.

### Absolute Criterion 2: Single-File SOT + Hierarchical Memory Structure
> All shared state is concentrated in a single file (`state.yaml`). SOT write permission belongs exclusively to the Orchestrator / Team Lead. Concurrent modification of the same file by parallel agents is strictly prohibited.

### Absolute Criterion 3: Code Change Protocol (CCP)
> Before writing, modifying, adding, or deleting code, you must internally perform **Step 1 (Understand Intent) → Step 2 (Ripple Effect Analysis) → Step 3 (Change Plan)**. Analysis depth scales with change scope. **Details**: `docs/protocols/code-change-protocol.md`.

**Coding Anchor Points (CAP)**: CAP-1 (Think Before Coding), CAP-2 (Simplicity First), CAP-3 (Goal-Based Execution), CAP-4 (Surgical Changes). When conflicting with Absolute Criterion 1, Quality always wins.

### Priority Among Absolute Criteria
> **Absolute Criterion 1 (Quality) is paramount.** Absolute Criterion 2 (SOT) and Absolute Criterion 3 (CCP) are co-equal means to guarantee quality.

---

## Project Structure

```
AgenticWorkflow/
├── CLAUDE.md                        ← This file (Claude Code directive — lightweight TOC)
├── AGENTS.md                        ← Universal AI agent common directive (Hub — methodology SOT)
├── GEMINI.md                        ← Gemini CLI / Antigravity directive (Spoke)
├── soul.md                          ← DNA inheritance definition
├── DECISION-LOG.md                  ← Architecture Decision Records (ADR, 51+ records)
├── AGENTICWORKFLOW-USER-MANUAL.md   ← User manual
├── AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md ← Design philosophy and architectural bird's-eye view
├── docs/protocols/                  ← Detailed protocols (on-demand references)
│   ├── autopilot-execution.md       (Workflow execution checklist + NEVER DO)
│   ├── quality-gates.md             (L0-L2 4-layer + P1 14-item validation details)
│   ├── ulw-mode.md                  (ULW 3 intensifier rules + runtime mechanics)
│   ├── context-preservation-detail.md (Hook internal mechanics + D-7 instances)
│   └── code-change-protocol.md      (CCP 3 steps + CAP + Proportionality Rule)
├── .claude/
│   ├── settings.json                ← Hook configuration
│   ├── agents/
│   │   ├── translator.md            (Terminology consistency specialist)
│   │   ├── reviewer.md              (Adversarial reviewer, Enhanced L2)
│   │   └── fact-checker.md          (Fact-checker, claim-by-claim verification)
│   ├── commands/
│   │   ├── install.md               (/install — Setup Init validation)
│   │   └── maintenance.md           (/maintenance — Health check)
│   ├── hooks/scripts/               ← Hook + validation scripts
│   │   ├── context_guard.py         (Unified dispatcher)
│   │   ├── _context_lib.py          (Shared library — parsing, generation, validation, compression)
│   │   ├── save_context.py          (SessionEnd/PreCompact snapshot persistence)
│   │   ├── restore_context.py       (SessionStart restore + RLM pointers)
│   │   ├── update_work_log.py       (PostToolUse 9 tools tracking)
│   │   ├── generate_context_summary.py (Stop incremental snapshot + safety net)
│   │   ├── diagnose_context.py      (Abductive Diagnosis pre-analysis)
│   │   ├── validate_diagnosis.py    (AD1-AD10 post-validation)
│   │   ├── validate_pacs.py         (PA1-PA7 + L0 validation)
│   │   ├── validate_review.py       (R1-R5 review validation)
│   │   ├── validate_traceability.py (CT1-CT5 traceability validation)
│   │   ├── validate_domain_knowledge.py (DK1-DK7 domain knowledge validation)
│   │   ├── validate_translation.py  (T1-T9 translation & glossary validation)
│   │   ├── validate_verification.py (V1a-V1c verification log validation)
│   │   ├── validate_workflow.py     (W1-W8 DNA inheritance validation)
│   │   ├── validate_retry_budget.py (RB1-RB3 retry budget decision)
│   │   ├── setup_init.py            (Infrastructure health check + SOT write pattern check)
│   │   ├── setup_maintenance.py     (Periodic health check + doc-code sync)
│   │   ├── block_destructive_commands.py (Dangerous command blocking: network/system/git/rm, exit 2)
│   │   ├── block_test_file_edit.py  (TDD Guard, .tdd-guard toggle)
│   │   ├── predictive_debug_guard.py (Risk file warning based on error history, exit 0)
│   │   ├── output_secret_filter.py  (Secret detection: 3-tier, 25+ regexes, 2-pass scan)
│   │   ├── security_sensitive_file_guard.py (Security sensitive file modification warning)
│   │   ├── query_workflow.py        (Workflow observability: dashboard/weakest/retry/blocked)
│   │   ├── _test_secret_filter.py   (output_secret_filter tests — 44 cases)
│   │   ├── _test_sensitive_file_guard.py (security_sensitive_file_guard tests — 44 cases)
│   │   └── _test_block_destructive.py (block_destructive_commands tests — 43 cases)
│   ├── context-snapshots/           ← Runtime snapshots (gitignored)
│   └── skills/
│       ├── workflow-generator/      (Workflow design & generation skill)
│       └── doctoral-writing/        (Doctoral academic writing skill)
├── translations/glossary.yaml       ← Terminology glossary
├── prompt/                          ← PRD investigation frameworks & agent prompts
└── coding-resource/                 ← Theoretical foundations
```

## Context Preservation System

An automatic persistence and recovery system that prevents loss of work context upon context token exhaustion, `/clear`, or compaction.

| Hook Event | Script | Action |
|---|---|---|
| Setup (`--init`) | `setup_init.py` | Infrastructure health check + SOT write safety + runtime directory init |
| Setup (`--maintenance`) | `setup_maintenance.py` | Periodic health check + doc-code synchronization |
| PreToolUse (Bash) | `block_destructive_commands.py` | Blocks dangerous commands: network exfil, raw format, git reset/force, rm -rf (exit 2) |
| PreToolUse (Edit\|Write) | `block_test_file_edit.py` | Protects test files during active TDD Guard (exit 2) |
| PreToolUse (Edit\|Write) | `predictive_debug_guard.py` | Warns on high-risk files based on past failure history |
| SessionStart | `restore_context.py` | RLM pointers + past session index + Predictive Debugging risk cache |
| PostToolUse (9 tools) | `update_work_log.py` | Accumulates granular tool usage logs |
| PostToolUse (Bash\|Read) | `output_secret_filter.py` | Detects leaked secrets (3-tier extraction, 2-pass scan) |
| PostToolUse (Edit\|Write) | `security_sensitive_file_guard.py` | Warns on security-sensitive file changes |
| Stop | `generate_context_summary.py` | Incremental snapshot + Knowledge Archive indexing + safety net |
| PreCompact | `save_context.py` | Saves full snapshot before context compaction |
| SessionEnd | `save_context.py` | Saves full snapshot on `/clear` or session exit |

**Mandatory Action**: When `[CONTEXT RECOVERY]` appears at session start, **you must read the indicated snapshot file** via Read tool to restore prior working context.

**Details**: Hook internal mechanics, Knowledge Archive schema, and D-7 instances → `docs/protocols/context-preservation-detail.md`.

## Skill Invocation Routing

| User Request Pattern | Skill | Entry Point |
|---|---|---|
| "create workflow", "design automation pipeline", "build workflow" | `workflow-generator` | SKILL.md |
| "write in doctoral style", "academic writing", "dissertation polish" | `doctoral-writing` | SKILL.md |

## Core Design Principles

1. **P1 — Data Refinement for Accuracy**: Strip noise deterministically via Python code before handing off to AI agents.
2. **P2 — Expertise-Based Delegation Structure**: Delegate specialized tasks to domain agents; Orchestrator focuses on coordination.
3. **P3 — Resource Accuracy**: Explicit paths for all files, dependencies, and external assets; placeholders are forbidden.
4. **P4 — Question Design Rules**: Maximum 4 questions, each with ~3 options. Proceed without questions if unambiguous.

## Autopilot Mode

Autonomous execution mode that auto-approves `(human)` review stages and questions. Details: `AGENTS.md §5.1`.

**4-Layer Quality Assurance**: L0 (Anti-Skip Guard) → L1 (Verification Gate) → L1.5 (pACS Self-Scoring) → L2 (Adversarial Review). Details: `docs/protocols/quality-gates.md`.

**Required Reading Before Execution**: `docs/protocols/autopilot-execution.md` — step-by-step checklist and NEVER DO rules.

## ULW (Ultrawork) Mode

Activated whenever `ulw` is present in the prompt. Acts as an **intensity overlay on rigor**. Orthogonal to Autopilot. 3 Intensifiers: I-1 (Sisyphus Persistence), I-2 (Mandatory Task Decomposition), I-3 (Bounded Retry Escalation).

**Details**: `docs/protocols/ulw-mode.md`.

## Language and Style Rules

- **Framework Documentation & User Dialogue**: Pure English
- **Workflow Execution**: Pure English (maximizes AI reasoning capability — Absolute Criterion 1)
- **Deliverables**: English primary deliverables
- **Technical Terminology**: Maintain standard English terms (SOT, Agent Team, Hooks, pACS, etc.)
- **Visualization**: Prefer clean Mermaid diagrams with quoted labels
- **Depth**: Comprehensive, data-backed exposition over superficial summaries

## Skill Development Rules

1. **Embed all Absolute Criteria** — contextualized for the target domain.
2. **Strict division of file responsibilities** — `SKILL.md` (WHY / Routing), `references/` (WHAT / HOW / VERIFY).
3. **Explicit conflict resolution scenarios** among Absolute Criteria.
4. Always reflect and audit against the Absolute Criteria after any modification.
