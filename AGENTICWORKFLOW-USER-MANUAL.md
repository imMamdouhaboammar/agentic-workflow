# AgenticWorkflow User Manual

> **Scope of this document**: This manual guides you on how to use the **AgenticWorkflow codebase itself**.
> In other words, it covers the **usage of the tool (this codebase)** for designing and implementing workflows.
>
> For instructions on using **individual projects created with this codebase** (e.g., blog pipelines, research systems, etc.),
> refer to each project's `workflow.md` and the manual within that respective project.

| Document | Target Audience / Purpose |
|----------|---------------------------|
| **This Document (`AGENTICWORKFLOW-USER-MANUAL.md`)** | Usage of the AgenticWorkflow codebase itself — how to design and implement workflows |
| **`README.md`** | First introduction to the project — overview, objectives, document reading order |
| **`AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md`** | Design philosophy, full architectural overview, relationships between components — understanding "Why it was designed this way" |
| **`DECISION-LOG.md`** | Record of all design decisions in the project (ADR) — tracking context, rationale, and alternatives chronologically |
| **Individual Project Manuals** (within each project) | Usage of specific projects built with AgenticWorkflow — running and operating completed systems |

---

## 1. Getting Started

### 1.1 Prerequisites

| Item | Required | Description |
|------|----------|-------------|
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) | Required | `npm install -g @anthropic-ai/claude-code` |
| GitHub Account | Recommended | Repository cloning and collaboration |
| Python 3.10+ | Optional | For running data pre-processing / post-processing scripts |
| Node.js 18+ | Optional | When integrating MCP Servers |

### 1.2 Installation

```bash
git clone https://github.com/idoforgod/AgenticWorkflow.git
cd AgenticWorkflow
```

### 1.3 Opening the Project

```bash
claude          # Launch Claude Code (from the AgenticWorkflow directory)
```

When Claude Code starts, it automatically reads `CLAUDE.md` and applies the project's Absolute Criteria and design principles.

---

## 2. Overall Flow

```
User's idea or specification document
        ↓
┌──────────────────────────────────────────────┐
│ Phase 1: Workflow Design                     │
│  Use workflow-generator skill                │
│  → Generate workflow.md (blueprint)          │
│  → (Optional) Distill verification           │
└──────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────┐
│ Phase 2: Workflow Implementation             │
│  Actual implementation based on workflow.md  │
│  → Configure agents, scripts, and automation │
│  → Executing autonomous system (final goal)  │
└──────────────────────────────────────────────┘
```

> **DNA Inheritance**: When `workflow-generator` creates a workflow, the entire parent genome (AgenticWorkflow) — including Absolute Criteria, SOT pattern, 4-layer verification, Safety Hooks, etc. — is automatically embedded into the child workflow.
> Users do not need to manually configure the DNA — the production pipeline structurally inherits it. Details: [`soul.md`](soul.md)

---

## 3. Absolute Criteria

These are the top-level rules applied to every design, implementation, and modification decision in this codebase.
They supersede all principles, guidelines, and conventions below.

### Absolute Criterion 1: Quality of the Final Deliverable

> **Speed, token cost, workload, and length limits are completely ignored.**
> The sole criterion for every decision is the **quality of the final deliverable**.
> Rather than making things fast by reducing steps, choose the direction that raises quality even if that means adding steps.

### Absolute Criterion 2: Single-File SOT + Hierarchical Memory Structure

> **Under the design of a single-file SOT (Single Source of Truth) + hierarchical memory structure, no data inconsistency occurs even when dozens of agents operate simultaneously.**

- **State Management**: All shared state is concentrated in a single file. Do not scatter state across multiple files.
- **Write Permission**: SOT file writing is restricted to the Orchestrator / Team Lead only. All other agents have read-only access and produce their results as separate deliverable files.
- **Conflict Prevention**: Structures in which parallel agents modify the same file simultaneously are prohibited.

### Absolute Criterion 3: Code Change Protocol (CCP)

> **Before writing, modifying, adding, or deleting code, you must internally perform the 3 steps below.**

- **Step 1 — Understand Intent**: Define the purpose and constraints of the change in 1-2 sentences.
- **Step 2 — Ripple Effect Analysis**: Investigate cascading changes across direct dependencies, call relationships, structural relationships, data models, tests, configurations, and documentation. Flag high-coupling risks in advance.
- **Step 3 — Change Plan**: Propose a step-by-step modification sequence. Propose opportunities to reduce coupling alongside the plan.

Analysis depth scales proportionally with the scope of the change (Minor → Step 1 only / Standard → Full 3 steps / Large-scale → Full 3 steps + mandatory prior approval).

> **Coding Anchor Points (CAP-1~4)**: Think Before Coding, Simplicity First, Goal-Based Execution, Surgical Changes. Details: `AGENTS.md §2` Absolute Criterion 3.

### Priority Among Absolute Criteria

> **Absolute Criterion 1 (Quality) is highest. Absolute Criterion 2 (SOT) and Absolute Criterion 3 (CCP) are co-equal means to guarantee quality.**
> Whichever criterion it is, when it conflicts with Absolute Criterion 1, quality wins.

All Absolute Criteria apply to both Phase 1 (Design) and Phase 2 (Implementation).

---

## 4. Design Principles

These are subordinate principles under the Absolute Criteria. They must be applied when designing and implementing workflows.

### P1. Data Refinement for Accuracy

Passing large, raw data directly to an AI degrades accuracy due to noise.

- Specify **pre-processing** at each stage: remove noise before handing data to the agent.
- Specify **post-processing** at each stage: refine deliverables before passing them to the next stage.
- Pre-compute code-calculable relationships in advance → enable the AI to focus entirely on judgment and analysis.

```
Bad:  "Pass the entire collected HTML of the web page directly to the agent"
Good: "Extract only body text via a Python script → pass only essential text to the agent"
```

### P2. Expertise-Based Delegation Structure

Maximize quality by delegating each task to the specialized agent best equipped to perform it.

```
Orchestrator (quality coordination + flow management)
  ├→ Agent A: Specialized research
  ├→ Agent B: In-depth analysis
  └→ Agent C: Verification and quality gate
```

### P3. Resource Accuracy

Specify exact paths for any stage requiring images, files, or external resources. Placeholders may not be omitted.

### P4. Question Design Rules

When asking the user questions:
- Maximum of 4 questions
- Provide approximately 3 options per question
- If there is no ambiguity, proceed without questions

---

## 5. Phase 1: Workflow Design

### 5.1 Requesting Workflow Generation

In Claude Code, request as follows:

```
Create a workflow
```

Or:

```
Design an automation pipeline
```

The `workflow-generator` skill will activate automatically.

### 5.2 Two Cases

#### Case 1: Idea Only

When you only have an idea without specification documents. The AI collects requirements through interactive questioning.

```
User: "Create a workflow that automatically researches and writes blog content"

AI sample questions:
1. "What output do you want to produce?"
2. "What are the primary input sources?"
3. "At which stage is human review required?"
```

#### Case 2: With Documentation

When attaching a concrete specification document such as a PDF. The AI analyzes the document first before asking clarifying questions.

```
User: "Create a workflow based on this PDF" + [file attached]

AI actions:
1. In-depth document analysis → extract purpose, stages, inputs/outputs, and constraints
2. Present analysis summary
3. Clarification questions (concise)
4. Generate workflow.md
```

During document analysis, the AI follows the checklist in `.claude/skills/workflow-generator/references/document-analysis-guide.md`.

### 5.3 Generated workflow.md Structure

Every workflow consists of three stages:

```markdown
# [Workflow Name]

## Overview
- Input: [Input data]
- Output: [Final deliverable]
- Frequency: [Execution frequency]

## Research
### 1. [Research Stage]
- Pre-processing: [Data pre-processing — P1]
- Agent: @[agent-name]
- Verification:
  - [ ] [Specific, measurable criterion — structural completeness/functional goal/data integrity/pipeline connectivity]
  - [ ] [Specific, measurable criterion]
- Task: [Task to perform]
- Output: [Deliverable]
- Review: @reviewer | @fact-checker | @reviewer + @fact-checker | none
- Translation: @translator → [output].ko.md | none
- Post-processing: [Deliverable refinement — P1]

## Planning
### 2. [Planning Stage]
...
### 3. (human) [Review Stage]
- Action: [Action to be performed by human]

## Implementation
### 4. [Execution Stage]
...

## Claude Code Configuration
### Sub-agents / Agent Team / Hooks / Slash Commands / Skills / MCP Servers / Task Management / SOT / Error Handling
```

For details on the standard structure, refer to `.claude/skills/workflow-generator/references/workflow-template.md`.

### 5.4 Workflow Notation

| Notation | Meaning |
|----------|---------|
| `(human)` | Human intervention / review required |
| `(team)` | Agent Team parallel execution segment |
| `(hook)` | Automated verification / quality gate |
| `@agent-name` | Sub-agent invocation |
| `@translator` | Translation sub-agent — invoked in `Translation` field |
| `@reviewer` | Adversarial Review — critical analysis of code/deliverables (read-only) |
| `@fact-checker` | Adversarial Review — external fact verification (web access) |
| `/command-name` | Slash command execution |
| `[skill-name]` | Skill reference |

### 5.5 (Optional) Distill Verification

An inspection step following `workflow.md` generation to maximize quality. Uses the interview framework from `prompt/distill-partner.md`.

| Review Question | Purpose |
|-----------------|---------|
| "Does this step contribute to final quality?" | Eliminate only steps that are irrelevant to quality |
| "Will quality be more consistent if this step is automated?" | Identify automation opportunities |
| "Are there additional steps needed to enhance quality?" | Add verification and reinforcement steps |

> While optional, this step is strongly recommended under Absolute Criterion 1 (Quality First).

---

## 6. Phase 2: Workflow Implementation

Once `workflow.md` is generated, you build the actual components defined within it.

> **Note**: The files listed below are created **within the target project when starting a new project with this codebase**.
> It is completely normal that these files do not exist in the AgenticWorkflow codebase itself.
> The codebase itself contains only skills and reference materials; implementation deliverables belong to each respective project.

### 6.1 Components to Implement

| Defined in workflow.md | Actual File to Create | Location (Within Project) |
|------------------------|-----------------------|---------------------------|
| Sub-agents | `.md` files | `.claude/agents/` |
| Slash commands | `.md` files | `.claude/commands/` |
| Hooks | JSON configuration | `.claude/settings.json` |
| Pre/Post-processing scripts | Python / Bash | `scripts/` |
| SOT file | YAML / JSON | `.claude/state.yaml` |
| MCP Server configuration | JSON | `.mcp.json` |
| Task design | Task definitions (in `workflow.md`) | Within workflow stages |

For details on implementation patterns (Sub-agents frontmatter, Agent Team architecture, Hook events, SOT flow, etc.),
refer to `.claude/skills/workflow-generator/references/claude-code-patterns.md`.

### 6.2 Creating Sub-agents

If `@researcher` is defined in `workflow.md`:

```markdown
# .claude/agents/researcher.md
---
name: researcher
description: Specialized in web search and material research
model: sonnet
tools: Read, Glob, Grep, WebSearch, WebFetch
maxTurns: 30
---

You are a research specialist.
Systematically collect and summarize materials on the given topic.

## Working Principles
- Sources (URLs) mandatory for all information
- Organize key insights in a structured format
```

**Model Selection Criteria:**

| Model | Suitable Tasks |
|-------|----------------|
| `opus` | Complex analysis, research, writing — core tasks requiring the highest quality |
| `sonnet` | Collection, scanning, structuring — repetitive tasks requiring consistent quality |
| `haiku` | Status checks, simple judgments — low-complexity auxiliary tasks |

### 6.3 Agent Team Configuration (Parallel Collaboration)

If there is a `(team)` segment in `workflow.md`:

```json
// .claude/settings.json — Enable Agent Teams
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Team Workflow:**
```
Team Lead (coordination + SOT write)
  ├→ Teammate A → Generate deliverable file (output-a.md)
  ├→ Teammate B → Generate deliverable file (output-b.md)
  └→ Team Lead → Merge state into state.yaml → Next stage
```

### 6.4 Hooks Configuration (Automated Gates)

If there is a `(hook)` segment in `workflow.md`:

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "prettier --write \"$(jq -r '.tool_input.file_path')\" 2>/dev/null || true",
          "statusMessage": "Auto-formatting..."
        }]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "agent",
          "prompt": "Verify the deliverable quality of the completed task.",
          "timeout": 60
        }]
      }
    ]
  }
}
```

**Hook Exit Codes:**

| Code | Behavior |
|------|----------|
| `0` | Pass |
| `2` | Block — deliver feedback to agent, rework |

> **Context Preservation System**: This codebase itself operates a context preservation system using 5 Hooks (`SessionStart`, `PostToolUse`, `Stop`, `PreCompact`, `SessionEnd`). It automatically saves work history on `/clear`, context compaction, and response completion, and restores previous context in a new session via the RLM pattern (pointer + summary + completion state + Git state + dynamic RLM query hints). `PostToolUse` tracks 9 tools (`Edit`, `Write`, `Bash`, `Task`, `NotebookEdit`, `TeamCreate`, `SendMessage`, `TaskCreate`, `TaskUpdate`). The `Stop` hook minimizes noise with 30-second throttling + a 5KB growth threshold while recording session metadata into the Knowledge Archive (`knowledge-index.jsonl`, `sessions/`), including `phase` (stage), `phase_flow` (transition flow), `primary_language`, `error_patterns` (Error Taxonomy 12-pattern classification + resolution matching), `tool_sequence` (RLE-compressed tool sequences), `final_status` (session exit state), `tags` (path-based search tags), and `session_duration_entries` (session length). Design decisions in snapshots are ordered by quality tag priority (`[explicit]` > `[decision]` > `[rationale]` > `[intent]`) to filter out noise, IMMORTAL sections are preserved first during snapshot compression (with a compression audit trail), and an atomic write (`temp` → `rename`) pattern applies to all file writes (snapshots, archives, log truncation). Deterministic P1 hallucination containment performs KI schema validation, partial failure isolation, SOT write pattern validation (`setup_init.py`), SOT schema validation (8 checks: S1-S6 basic + S7 pacs 5 fields + S8 active_team 5 fields), Adversarial Review P1 validation (`validate_review.py` — R1-R5), **secret detection** (`output_secret_filter.py` — 3-tier extraction, 25+ patterns, PostToolUse `Bash`|`Read`), and **security-sensitive file warnings** (`security_sensitive_file_guard.py` — 12 patterns, PostToolUse `Edit`|`Write`). Across the 3 Safety Hooks, 131 automated tests (44 + 44 + 43) are established. At `SessionStart`, Error→Resolution matching results surface automatically to prevent recurring errors. For details, refer to `AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md §4.10`.

### 6.5 Creating Slash Commands

If there are user intervention points in `workflow.md`:

```markdown
# .claude/commands/review-output.md
---
description: "Review and approve/reject deliverable"
---

Displays current stage deliverable and awaits user approval/rejection.
- On approval: automatically proceed to next stage
- On rejection: pass feedback to agent for rework
```

### 6.6 Initializing the SOT File

```yaml
# .claude/state.yaml
workflow:
  name: "my-workflow"
  current_step: 1
  status: "ready"
  outputs: {}
```

**SOT Rules:**
- Write: Orchestrator or Team Lead only
- Read: Accessible by all agents
- Teammates: Generate deliverable files only; direct modification of SOT is prohibited

---

## 7. Execution Patterns

### 7.1 Sequential Pipeline (Default)

```
@agent-1 → @agent-2 → (human) Review → @agent-3
```

Used when a single specialist maintains deep context and processes tasks with consistency.

### 7.2 Parallel Branching (Agent Team)

```
           ┌→ @teammate-a ─┐
Team Lead ─┤                ├→ (human) Review → @agent-merge
           └→ @teammate-b ─┘
```

Used when distinct domains of expertise must each be handled at the highest level.

### 7.3 Automated Verification Gate (Hook)

```
@agent-1 → [Hook: Quality Verification] → @agent-2
                ↓ On failure
           Deliver feedback → Rework
```

Used when code quality, security verification, and standards compliance are critical.

### 7.4 Conditional Flow

```
@agent-1 → Evaluate Condition → Path A: @agent-2a
                              → Path B: @agent-2b
                              → Merge → @agent-3
```

Used when routing through different paths depending on previous stage results, data types, quality thresholds, or user choices.

### 7.5 Team + Hook Combination (Advanced Hybrid)

```
Team Lead ─┬→ @researcher   [Hook: Source Verification]
           ├→ @writer       [Hook: Quality Verification]
           └→ @fact-checker [Hook: Result Merge]
                    ↓ All completed
               (human) Review → @editor → Final Version
```

Triple quality assurance combining parallel specialist execution + automated quality gates + human review. Used when complex workflows demand the highest level of quality.

---

## 8. Skill Details

### 8.1 workflow-generator

**Trigger Keywords:** create workflow, design automation pipeline, define workflow

**Entry Point:** `.claude/skills/workflow-generator/SKILL.md`

**Reference Files Guide:**

| File | Role | When to Use |
|------|------|-------------|
| `references/claude-code-patterns.md` | Implementation pattern details for Sub-agents, Agent Teams, Hooks, SOT, etc. | When building components in Phase 2 |
| `references/workflow-template.md` | Standard structure and notation rules for `workflow.md` | When generating `workflow.md` in Phase 1 |
| `references/document-analysis-guide.md` | Checklist and output format for analyzing attached documents | When analyzing documents in Phase 1 Case 2 |
| `references/context-injection-patterns.md` | Pattern guide for injecting context into agent prompts | When designing agent prompts in Phase 2 |
| `references/autopilot-decision-template.md` | Standard template for Autopilot Decision Logs | When recording decisions during Autopilot execution |
| `references/state.yaml.example` | SOT file structure example and field descriptions | When initializing SOT in Phase 2 |

### 8.2 doctoral-writing

**Trigger Keywords:** write in dissertation style, academic writing, polish academic prose

**Entry Point:** `.claude/skills/doctoral-writing/SKILL.md`

**Use Cases:**
- Reviewing and drafting dissertation chapters
- Editing papers submitted to academic journals
- Writing research reports and conference papers

**Reference Files Guide:**

| File | Role | When to Use |
|------|------|-------------|
| `references/clarity-checklist.md` | Evaluation checklist for clarity, conciseness, and academic rigor (VERIFY) | When verifying after manuscript revisions |
| `references/common-issues.md` | Catalog of frequent academic writing issues + solutions (WHAT) | When identifying recurring error patterns |
| `references/before-after-examples.md` | Real doctoral dissertation revision examples (HOW — practical) | When concrete revision examples are needed |
| `references/discipline-guides.md` | Disciplinary conventions across humanities, social sciences, and natural sciences (WHERE — disciplinary context) | When checking citation styles, voice/person, and structure by discipline |
| `references/academic-quick-reference.md` | Academic ❌/✅ conversion patterns (HOW — Academic Patterns) | Quick reference when writing and polishing academic papers |

> **Role Division Among Files**: While the same topic (e.g., passive voice overuse) appears across multiple files, this represents role specialization rather than redundancy.
> `SKILL.md` (WHY) → `common-issues.md` (WHAT) → `academic-quick-reference.md` / `before-after-examples.md` (HOW) → `clarity-checklist.md` (VERIFY)

---

## 9. Prompt Materials

| File | Purpose | When to Use in Workflow |
|------|---------|-------------------------|
| `prompt/crystalize-prompt.md` | Compress lengthy AI agent instructions while retaining core elements | **Phase 2**: When Sub-agent `.md` prompts are excessively long |
| `prompt/distill-partner.md` | Essence extraction and optimization interview | **Phase 1**: When checking workflow quality during the Distill verification stage |
| `prompt/crawling-skill-sample.md` | Anti-scraping defense skill sample for Naver News crawling | **Phase 2**: Reference for writing new skill files |

---

## 10. Theoretical Foundation

`coding-resource/recursive language models.pdf`

A seminal research paper containing essential theory for implementing long-term memory. It serves as the theoretical foundation for mechanisms enabling agents to accumulate and utilize knowledge across sessions.

---

## 11. Usage with Other AI Tools

This project employs a **Hub-and-Spoke pattern** so that the exact same methodology applies automatically regardless of which AI CLI tool you use.

**Hub (Methodology SOT):** `AGENTS.md` — Absolute Criteria, design principles, and workflow structures common to all tools

**Spoke (Tool-Specific Extensions):**

| AI CLI Tool | System Prompt File | Automatically Applied |
|-------------|--------------------|-----------------------|
| Claude Code | `CLAUDE.md` | Yes — Full feature support including Hooks, Skills, and Context Preservation |
| Gemini CLI | `GEMINI.md` + `.gemini/settings.json` | Yes — Loads Hub directly via `@AGENTS.md` import |
| Codex CLI | `AGENTS.md` (read directly) | Yes — No separate Spoke needed |
| Copilot CLI | `.github/copilot-instructions.md` | Yes — Automatically recognizes `AGENTS.md` as well |
| Cursor | `.cursor/rules/agenticworkflow.mdc` | Yes — Configured with `alwaysApply: true` |

Usage: Entering this project directory with any supported AI CLI tool causes it to automatically read its respective Spoke file and adhere to the AgenticWorkflow methodology. No additional configuration is necessary.

> Detailed Architecture: See `AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md §7.1`

---

## 12. Autopilot Mode

A mode for executing workflows without interruption. Automatically approves human intervention points (`(human)`).

### Activation

1. **Workflow Declaration**: In Overview: `- **Autopilot**: enabled`
2. **Instruction at Runtime**: "Run workflow in autopilot mode"
3. **Toggle During Execution**: "Disable autopilot" / "Enable autopilot"

### Operating Mechanism

| Checkpoint | Normal Mode | Autopilot Mode |
|------------|-------------|----------------|
| `(human)` Slash Command | Waits for user input | Automatically approves with quality-maximizing default |
| AskUserQuestion | Waits for user selection | Automatically selects quality-maximizing option |
| `(hook)` exit code 2 | Blocks | **Blocks identically** |

### 4-Layer Quality Assurance Stack

Upon completing each stage, deliverables must pass through up to 4 layers of verification before advancing to the next stage:

| Layer | Name | Type | Condition |
|-------|------|------|-----------|
| **L0** | Anti-Skip Guard | Deterministic | Always |
| **L1** | Verification Gate | Semantic | Stages with `Verification` field |
| **L1.5** | pACS (Self-Rating) | Self-evaluation | pACS active + Verification passed |
| **L2** | Adversarial Review (Enhanced) | Adversarial review | Stages with `Review:` field |

**L0: Anti-Skip Guard (Deterministic)**
1. Deliverable file path is recorded in SOT `outputs`
2. The specified file exists on disk
3. File size is at least 100 bytes (meaningful content)

**L1: Verification Gate (Semantic — Stages with `Verification` field only)**
4. Agent self-verifies that the deliverable achieves 100% of the `Verification` criteria
5. If failing criteria are detected, executes **Abductive Diagnosis** (P1 pre-evidence gathering → LLM root cause analysis → P1 post-validation) before retrying, followed by diagnosis-informed re-execution (up to 10 retries, 15 with ULW)
6. Records PASS/FAIL + Evidence per criterion in `verification-logs/step-N-verify.md`. Diagnosis logs are recorded in `diagnosis-logs/step-N-{gate}-{timestamp}.md`

**L1.5: pACS — predicted Agent Confidence Score (Self-Confidence Scoring)**
7. After passing Verification, the agent self-scores its deliverable across 3 dimensions: F (Factual Grounding) / C (Completeness) / L (Logical Coherence)
8. pACS = min(F, C, L) — the weakest dimension determines overall confidence
9. RED (< 50) → Executes **Abductive Diagnosis** followed by diagnosis-informed rework; YELLOW (50–69) → Proceeds with warning; GREEN (≥ 70) → Passes
10. Records Pre-mortem answers + scores in `pacs-logs/step-N-pacs.md`

**L2: Adversarial Review (Enhanced — Stages with `Review:` field only)**
11. `@reviewer` (critical analysis of code/deliverables) or `@fact-checker` (external fact verification) sub-agents conduct independent adversarial reviews
12. Deterministic P1 validation (`validate_review.py`) guarantees review quality
13. Recorded in `review-logs/step-N-review.md`
14. Details: `AGENTS.md §5.5`

> Stages without a `Verification` field proceed with L0 (Anti-Skip Guard) only (backward compatibility).
> pACS cannot be used standalone without Verification — passing L1 is a prerequisite for L1.5.

### Decision Log

Auto-approved decisions are recorded in `autopilot-logs/step-N-decision.md`:

- **Required Fields**: `step_number`, `checkpoint_type`, `decision`, `rationale`, `timestamp`
- **Optional Fields**: `alternatives_considered`, `output_path`, `quality_assessment`
- **Standard Template**: `.claude/skills/workflow-generator/references/autopilot-decision-template.md`

### Guarantees

- Every stage executes completely in sequence (no skipping)
- All deliverables maintain the exact same quality and depth as with human review
- Hook automated verifications execute identically
- Auto-approval decisions are logged in `autopilot-logs/`

### Runtime Reinforcement (Claude Code)

In Claude Code, the Hook system reinforces Autopilot's design intent deterministically at runtime:

| Timing | Mechanism | Effect |
|--------|-----------|--------|
| Session Start / Restore | `SessionStart` injects Autopilot execution rules | Embeds execution rules into context across every session boundary |
| After Every Response | Preserves Autopilot state section in snapshots | Prevents loss of Autopilot state across session boundaries (IMMORTAL priority) |
| Response Completion | `Stop` hook detects missing Decision Logs | Synthesizes missing logs when auto-approval patterns lack documentation |
| Post-Tool Use | `PostToolUse` tracks `autopilot_step` (across 9 tools) | Records stage progression patterns in `work_log` (for post-hoc analysis) |

> In other AI tools lacking this Hook-based reinforcement, SOT and Decision Logs must be managed manually.

---

## 12-1. ULW (Ultrawork) Mode

ULW is a **thoroughness intensity overlay orthogonal to Autopilot**. It activates whenever `ulw` is included in the prompt.

- **Autopilot** = Automation Axis (HOW) — bypasses `(human)` approvals
- **ULW** = Thoroughness Axis (HOW THOROUGHLY) — exhaustive execution, persisting until errors are completely resolved

### 2x2 Matrix

| | **ULW OFF** (Standard) | **ULW ON** (Maximum Thoroughness) |
|---|---|---|
| **Autopilot OFF** | Standard interactive | Interactive + Sisyphus Persistence (3 retries) + Mandatory Task Decomposition |
| **Autopilot ON** | Standard automated workflow | Automated workflow + Sisyphus reinforcement (3 retries) + Team thoroughness |

### 2-Axis Comparison

| Axis | Primary Concern | Activation | Deactivation | Scope |
|------|-----------------|------------|--------------|-------|
| **Autopilot** | Automation (HOW) | SOT `autopilot.enabled: true` | SOT modification | Workflow stages |
| **ULW** | Thoroughness (HOW THOROUGHLY) | `ulw` in prompt | Implicit (inactive in new session without `ulw`) | All tasks |

### Activation

Automatically activates when `ulw` is included in the prompt:

```
ulw do this
ulw refactor this
```

In a new session, prompts without `ulw` automatically deactivate it (implicit release). An explicit deactivation command is unnecessary.

### 3 Intensifiers

| Intensifier | Description | Interactive Effect | Autopilot Combination Effect |
|-------------|-------------|--------------------|------------------------------|
| **I-1. Sisyphus Persistence** | Up to 3 retries, each attempting a distinct approach. 100% completion or report impossibility rationale | Attempts up to 3 alternatives on error | Quality gate (Verification/pACS) retry limit raised from 10 to 15 |
| **I-2. Mandatory Task Decomposition** | Mandatory `TaskCreate` → `TaskUpdate` → `TaskList` | Enforces task decomposition for non-trivial tasks | No change (Autopilot already tracks via SOT) |
| **I-3. Bounded Retry Escalation** | Prohibits exceeding 3 retries on the same target (quality gates follow separate budgets) — escalates to user upon exhaustion | Prevents infinite loops | Safety Hook blocks are always respected |

### Runtime Reinforcement (Claude Code)

The Hook system deterministically enforces ULW's 3 intensifiers:

| Timing | Mechanism | Effect |
|--------|-----------|--------|
| Transcript Parsing | `detect_ulw_mode()` — word-boundary regex | Detects `ulw` keyword with zero false positives |
| After Every Response | Preserves ULW state section in snapshots (IMMORTAL) | Prevents loss of ULW state across session boundaries |
| Session Start / Restore | `SessionStart` injects ULW intensification rules | Re-injects rules upon `clear`/`compact`/`resume` (except `startup` — implicit release) |
| After Every Response | `check_ulw_compliance()` — Compliance Guard | Deterministically verifies adherence to 3 intensifiers; issues IMMORTAL warnings on violation |
| After Every Response | `generate_context_summary.py` — ULW safety net | Outputs warning to stderr upon violation |
| Session End | Tags `ulw_active: true` in Knowledge Archive | Enables cross-session RLM queries |

### Combination with Autopilot

When Autopilot and ULW are active simultaneously, **ULW reinforces Autopilot**: it elevates the quality gate retry budget from 10 to 15 while always strictly respecting Safety Hook blocks.

> Other AI tools lack Hook-based ULW reinforcement, requiring manual use of `TaskCreate`/`TaskUpdate`/`TaskList` to observe ULW intensifiers.

Details: `docs/protocols/ulw-mode.md`, `AGENTS.md §5.1.1`

---

## 13. Verification Protocol (Work Verification)

A protocol that verifies whether deliverables at each stage of a workflow have achieved **100% of their functional goals**.

### Why the Verification Protocol Is Necessary

Anti-Skip Guard only checks "whether the file exists and is non-empty." However, a file can exist and still contain incomplete content. The Verification Protocol bridges this critical gap.

```
Anti-Skip Guard: "File exists, 2,847 bytes" → PASS (Physical)
Verification Gate: "Only 2 out of 3 competitors analyzed" → FAIL (Substantive)
  → Re-run analysis for the missing competitor → PASS → Advance
```

### How to Write Verification Fields

Define a `Verification` field before the `Task` at each stage of the workflow:

```markdown
### 1. Competitor Research
- **Agent**: `@researcher`
- **Verification**:
  - [ ] Includes pricing data for at least 3 competitors (at least 3 tiers each + exact amounts)
  - [ ] All URLs are valid with no placeholders or example.com domains
  - [ ] Includes competitor_name and pricing_tiers fields required by Step 4 analysis agent
- **Task**: Collect pricing models and feature comparison data for target competitors
- **Output**: `research/competitor-analysis.md`
```

### 4 Criterion Types

| Type | Target of Verification | Good Example | Bad Example |
|------|------------------------|--------------|-------------|
| **Structural Completeness** | Internal structure of deliverable | "All 5 sections included" | "Well structured" |
| **Functional Goals** | Task objective achievement | "At least 3 tiers per competitor price" | "Contains pricing information" |
| **Data Integrity** | Data accuracy and validity | "All URLs valid, no placeholders" | "Check links" |
| **Pipeline Connectivity** | Input compatibility for next stage | "Includes fields required by Step 4" | "Compatible with next step" |

> **Core Rule**: Every criterion must be **mechanically verifiable as True/False by a third party**. Subjective descriptions such as "high quality" or "sufficient depth" must never be used as criteria.

### Execution Flow

```
Agent reads Verification criteria (before Task)
  ↓
Execute stage — generate deliverable at full quality
  ↓
Anti-Skip Guard — file exists + ≥ 100 bytes
  ↓
Verification Gate — agent self-verifies deliverable against each criterion
  ├─ All criteria PASS → generate verification-logs/step-N-verify.md → Advance
  └─ FAIL → re-execute only failed portions (up to 10 retries) → escalate to user if exceeded
```

### 3-Layer Verification in Team Stages

In `(team)` stages, verification operates in 3 layers: L1 → L1.5 → L2:

| Layer | Actor | Verification Target | SOT Write |
|-------|-------|---------------------|-----------|
| **L1** | Teammate (Self-Verification) | Verification criteria of own Task | **None** — completed internally within session |
| **L1.5** | Teammate (pACS) | Confidence score of own Task deliverable | **None** — score included in report message |
| **L2** | Team Lead (Comprehensive Verification + Stage pACS) | Verification criteria for the entire stage | **Yes** — updates SOT outputs + pacs |

```
Teammate: Execute Task → Self-Verification (L1) → PASS → Self-score pACS (L1.5) → Report to Team Lead
                                                → On FAIL: self-correct and re-verify

Team Lead: Receive Teammate deliverable + pACS → Comprehensive verification against stage criteria + compute stage pACS (L2)
                                                → On PASS: update SOT
                                                → On FAIL or Teammate pACS RED: provide specific feedback + order re-execution
```

### Backward Compatibility

Existing workflows without a `Verification` field **maintain their legacy behavior (Anti-Skip Guard only)**. Newly generated workflows must always include the `Verification` field.

Details: `AGENTS.md §5.3`

---

## 14. Bilingual Workflow (English-First + Korean Translation)

When executing workflows, all agents operate in **English**, and the `@translator` sub-agent generates Korean translations for text deliverables.

### Why English-First?

| Reason | Explanation |
|--------|-------------|
| AI Performance Optimization | Most LLMs exhibit their highest analysis and reasoning quality in English |
| Translation Quality Assurance | Dedicated translation agent performs terminology consistency checks + self-reviews |
| Dual Deliverables | Secures both English originals (archiving/reuse) and Korean translations (communication/reporting) |

### Language Boundaries

| Segment | Language |
|---------|----------|
| `workflow.md` (Design document) | English or Korean — blueprint read by users |
| Agent execution + deliverables | English — AI performance optimization |
| Translation deliverables (`*.ko.md`) | Korean — generated by `@translator` |

### Translation Field

Each stage in a workflow includes a `Translation` field:

```markdown
- **Translation**: `@translator` → research-notes.ko.md    # Text deliverable → Translate
- **Translation**: none                                     # Code/Data → Translation unnecessary
```

**Determining Translation Targets:**

| Deliverable Type | Translation Setting |
|------------------|---------------------|
| Text documents (`.md`, `.txt`) | `@translator` |
| Code / Scripts (`.py`, `.js`) | `none` |
| Data files (`.json`, `.csv`) | `none` |
| Configuration files (`.yaml`, `.json`) | `none` |

### Terminology Consistency — Glossary

`@translator` uses `translations/glossary.yaml` as an RLM external persistent state:

- Loads existing terminology upon every translation to maintain consistency
- Appends newly identified terms to the glossary
- Ensures the same term is translated consistently across the entire workflow

### SOT Recording

Translation results are recorded in the SOT under the `step-N-ko` key:

```yaml
outputs:
  step-1: "research-notes.md"       # English original
  step-1-ko: "research-notes.ko.md" # Korean translation
```

> The `.isdigit()` guard in the legacy Hook code (`restore_context.py`) automatically skips `step-N-ko` keys, maintaining complete backward compatibility without code modifications.

---

## 15. Overall Summary: Workflow Design → Implementation Checklist

### Phase 1: Design

- [ ] Prepare idea or specification documents
- [ ] Generate `workflow.md` using `workflow-generator` skill
- [ ] Review generated workflow — verify stages, agents, human intervention points, and Verification criteria
- [ ] (Optional) Distill verification — inspect quality with `prompt/distill-partner.md`

### Phase 2: Implementation

> Create the files below inside your new project (not in this codebase itself).

- [ ] Create Sub-agent `.md` files (`.claude/agents/`)
- [ ] Create Slash command `.md` files (`.claude/commands/`)
- [ ] Configure Hooks (`.claude/settings.json`)
- [ ] Write pre/post-processing scripts (`scripts/`)
- [ ] Initialize SOT file (`.claude/state.yaml`)
- [ ] Configure MCP Server integration (`.mcp.json`, if needed)
- [ ] Configure Agent Teams (if parallel collaboration is needed)
- [ ] Design Tasks (when using Agent Teams — define Tasks in `workflow.md`)
- [ ] Define Verification criteria (specific and measurable criteria per stage — see §13)
- [ ] Configure Review field (assign `@reviewer` / `@fact-checker` to high-risk stages — see `AGENTS.md §5.5`)
- [ ] Configure Error Handling (retry, rollback, and escalation rules)
- [ ] Configure Translation field (`@translator` or `none` per stage)
- [ ] Initialize `translations/glossary.yaml` (if translation target stages exist)

### Verification

- [ ] Full workflow end-to-end execution test
- [ ] Verify deliverable quality at each stage (Absolute Criterion 1)
- [ ] Verify proper functioning of Verification Gate (confirm generation of `verification-logs/step-N-verify.md`)
- [ ] Verify SOT file consistency (Absolute Criterion 2)
- [ ] Verify existence of translation files (`*.ko.md`) + terminology consistency
- [ ] Verify proper functioning of Hook gates
