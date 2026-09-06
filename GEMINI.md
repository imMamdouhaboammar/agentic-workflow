# AgenticWorkflow — Gemini CLI Directive

> All AI agents working on this project must follow the AgenticWorkflow methodology.

## Essential References

@AGENTS.md

The above document defines all Absolute Criteria, design principles, and workflow structures for this project.
Refer to `AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md` for architectural design and rationale.
Refer to `DECISION-LOG.md` for historical design decisions (ADRs).

## Genetic Design (DNA Inheritance)

This project is a parent organism that births child agentic workflow systems.
Every child system structurally embeds the parent genome: 3 Absolute Criteria, Single-File SOT, 4-Layer Verification, Safety Hooks, and Memory Systems.
Details: `soul.md`, `AGENTS.md §1`.

## Absolute Criteria (Core Summary)

### Absolute Criterion 1: Quality of the Final Deliverable
> Speed, token cost, workload, and length limits are completely ignored.
> The sole criterion for every decision is the **quality of the final deliverable**.

### Absolute Criterion 2: Single-File SOT
> All shared state is concentrated in a single file (`state.yaml`). Write permission is held exclusively by the Orchestrator / Team Lead. Parallel agents concurrently modifying the same file is strictly prohibited.

### Absolute Criterion 3: Code Change Protocol (CCP)
> Before writing, modifying, adding, or deleting code, you must internally perform 3 steps:
> Step 1: Understand Intent → Step 2: Ripple Effect Analysis → Step 3: Change Plan.
> Analysis depth scales proportionally with change scope (Minor: Step 1 only, Standard: full 3 steps, Large-scale: full 3 steps + mandatory user approval).
> **Coding Anchor Points (CAP-1~4)**: Think Before Coding, Simplicity First, Goal-Based Execution, Surgical Changes. Details: `AGENTS.md §2`.

## Basic Workflow Structure

Every workflow consists of three stages:
1. **Research** — Information gathering and analysis
2. **Planning** — Plan formulation, structuring, human review and approval
3. **Implementation** — Actual execution and verified deliverable generation

## Gemini CLI Implementation Mapping

| AgenticWorkflow Concept | Gemini CLI Implementation |
|---|---|
| Specialized Agent (Sub-agent) | Gemini CLI is a single-session model. Simulate domain expertise by switching roles within the prompt or using subagents. |
| Agent Group (Agent Team) | Parallel Gemini CLI / Antigravity subagent sessions coordinated by Orchestrator. |
| Automated Verification (Hooks) | External Python and shell scripts executing automated verification pipelines. |
| Reusable Modules (Skills) | Injected via `@file.md` imports or skills directory. |
| External Integration (MCP) | Gemini extensions or external API scripts. |
| SOT State Management | `state.yaml` file — single write point principle applies identically. |
| Autopilot Mode | Controlled by `autopilot.enabled` field in SOT. Auto-approves `(human)` review steps. Includes Anti-Skip Guard and Decision Logs (`autopilot-logs/`). See `AGENTS.md §5.1`. |
| ULW (Ultrawork) Mode | Activated when `ulw` is present in prompt. Thoroughness intensity overlay orthogonal to Autopilot. 3 Intensifiers: Sisyphus Persistence (3 retries), Mandatory Task Decomposition, Bounded Retry Escalation. See `AGENTS.md §5.1.1`. |
| Verification Protocol | Verifies 100% functional goal achievement of step deliverables. Verification Gate layer sitting atop physical Anti-Skip Guard. Retries up to 10 times (15 with ULW). See `AGENTS.md §5.3`. |
| pACS (Self-Confidence Scoring) | 3-dimensional self-evaluation (Faithfulness, Completeness, Logic) with mandatory Pre-mortem protocol and min-score principle. GREEN (>=70): proceed, YELLOW (50-69): flag and proceed, RED (<50): rework. See `AGENTS.md §5.4`. |
| Adversarial Review (Enhanced L2) | Independent evaluation replacing legacy calibration. `@reviewer` (critical analysis of code/deliverables, read-only) + `@fact-checker` (external fact verification, web access). P1 validation (`validate_review.py`) ensures review rigor. See `AGENTS.md §5.5`. |
| Terminology Protocol | Maintains terminology consistency via `translations/glossary.yaml`. Deterministic validation guarantees glossary freshness and integrity. See `AGENTS.md §5.2`. |
| Predictive Debugging (L-1) | Pre-tool warning on risky files based on error history. `predictive_debug_guard.py` (PreToolUse warning) + `aggregate_risk_scores()` (SessionStart P1 aggregation) + `validate_risk_scores()` (RS1-RS6 validation). Cached in `risk-scores.json`. |
| Abductive Diagnosis | 3-step structured diagnosis triggered on quality gate failure before retry: Step A: P1 evidence gathering (`diagnose_context.py`), Step B: Multi-hypothesis root cause analysis, Step C: P1 post-validation (`validate_diagnosis.py` AD1-AD10). Recorded in `diagnosis-logs/`. See `AGENTS.md §5.6`. |

## Context Preservation

In environments without automatic Claude Code hook dispatching:
- **Manual Snapshot**: Direct the agent to save progress to `context-snapshot.md`.
- **Session Memory**: Utilize agent memory mechanisms to track core architectural state.
- **SOT-Based Recovery**: Restore workflow state seamlessly by reading `state.yaml`.

## Core Design Principles

- **P1**: Remove noise via deterministic scripts before passing context to AI.
- **P2**: Maximize quality through specialized delegation.
- **P3**: Explicit paths for all resources; no placeholders.
- **P4**: User questions: maximum 4, ~3 options each. If unambiguous, proceed without questions.

## Language and Style Rules

- **Framework Documentation & User Dialogue**: Pure English
- **Workflow Execution**: Pure English (maximizes reasoning performance — Absolute Criterion 1)
- **Deliverables**: English primary deliverables
- **Technical Terminology**: Keep standard English terms (SOT, Agent, Orchestrator, Hooks, etc.)
- **Visualization**: Prefer clean Mermaid diagrams with quoted labels
- **Depth**: Comprehensive, data-backed exposition over superficial summaries
