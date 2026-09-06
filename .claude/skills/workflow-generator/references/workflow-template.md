# Workflow Template

Standard structure of a workflow.md file.

## Basic Template

```markdown
# [Workflow Name]

[One-line description of workflow purpose]

## Overview

- **Input**: [Input data/trigger]
- **Output**: [Final deliverable]
- **Frequency**: [Execution frequency — daily/weekly/on-demand, etc.]
- **Autopilot**: [disabled|enabled] — Mode for auto-approving human checkpoints (default: disabled)
- **pACS**: [enabled|disabled] — Self-confidence scoring protocol (default: enabled, AGENTS.md §5.4)

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.
> Purpose varies by domain; the genome is identical. See `soul.md §0`.

**Constitutional Principles** (adapted to this workflow's domain):

1. **Quality Absolutism** — [Specify what quality means in this workflow's domain]
2. **Single-File SOT** — Concentrate all shared state in `.claude/state.yaml`
3. **Code Change Protocol** — Perform the 3 steps (Intent → Ripple Effects → Design) when modifying code during implementation. Internalize Coding Anchor Points (CAP-1~4)

**Inherited Patterns**:

| DNA Component | Inherited Form |
|---|---|
| 3-Phase Structure | Research → Planning → Implementation |
| SOT Pattern | `.claude/state.yaml` — single writer (Orchestrator/Team Lead) |
| 4-Layer QA | L0 Anti-Skip → L1 Verification → L1.5 pACS → L2 Adversarial Review |
| P1 Hallucination Prevention | Deterministic validation scripts (`validate_*.py`) |
| P2 Expert Delegation | Specialized sub-agents for each task |
| Safety Hooks | `block_destructive_commands.py` — dangerous command blocking |
| Adversarial Review | `@reviewer` + `@fact-checker` — Enhanced L2 independent quality critique |
| Decision Log | `autopilot-logs/` — transparent decision tracking |
| Context Preservation | Snapshot + Knowledge Archive + RLM restoration |

**Domain-Specific Gene Expression**:
[Describe DNA components that are strongly expressed in this workflow. E.g., research workflows strongly express the P1 (data refinement) gene]

---

## Research

### 1. [Step Name]
- **Pre-processing**: [Data refinement via Python script, etc. — optional]
- **Agent**: `@[agent-name]`
- **Verification**:
  - [ ] [Specific, measurable criteria — structural completeness/functional goals/data integrity/pipeline connectivity/cross-step traceability]
  - [ ] [Specific, measurable criteria]
- **Task**: [Task to perform]
- **Output**: [Step deliverable]
- **Translation**: `@translator` → [output].translated.md | none
- **Post-processing**: [Deliverable refinement — optional]

### 2. [Step Name]
- **Pre-processing**: [Data pre-processing]
- **Agent**: `@[agent-name]`
- **Verification**:
  - [ ] [Specific, measurable criteria]
  - [ ] [Specific, measurable criteria]
- **Task**: [Task to perform]
- **Output**: [Step deliverable]
- **Translation**: `@translator` → [output].translated.md | none

### 3. (human) [Review Step Name]
- **Action**: [Action to be performed by human]
- **Command**: `/[command-name]`

---

## Planning

### 4. [Step Name]
- **Pre-processing**: [Data pre-processing]
- **Agent**: `@[agent-name]`
- **Verification**:
  - [ ] [Specific, measurable criteria]
  - [ ] [Pipeline connectivity: references core data from previous step deliverables]
- **Task**: [Task to perform]
- **Output**: [Step deliverable]
- **Translation**: `@translator` → [output].translated.md | none
- **Post-processing**: [Deliverable refinement]

### 5. [Step Name]
- **Agent**: `@[agent-name]`
- **Verification**:
  - [ ] [Specific, measurable criteria]
  - [ ] [Specific, measurable criteria]
- **Task**: [Task to perform]
- **Output**: [Step deliverable]
- **Translation**: `@translator` → [output].translated.md | none

### 6. (human) [Review Step Name]
- **Action**: [Action to be performed by human]
- **Command**: `/[command-name]`

---

## Implementation

### 7. [Step Name]
- **Pre-processing**: [Data pre-processing]
- **Agent**: `@[agent-name]`
- **Verification**:
  - [ ] [Specific, measurable criteria]
  - [ ] [Core insights from previous steps are reflected in final deliverable]
- **Task**: [Task to perform]
- **Output**: [Final deliverable]
- **Translation**: `@translator` → [output].translated.md | none

---

## Claude Code Configuration

### Sub-agents

```yaml
# .claude/agents/[agent-name].md frontmatter format
---
name: [unique identifier]
description: "[Auto-delegation trigger description]"
model: [opus|sonnet|haiku]        # Selected based on quality criteria (Absolute Criterion 1)
tools: [allowed tools — comma separated]
disallowedTools: [blocked tools]       # optional
permissionMode: [default|plan|dontAsk]
maxTurns: [maximum turns]
memory: [user|project|local]      # C-3: Scope definition below
skills: [list of skills to inject]         # optional
mcpServers: [available MCPs]       # optional
---

[Agent system prompt]
```

> **Model Selection Criteria (Absolute Criterion 1)**: opus = highest quality core tasks, sonnet = stable recurring tasks, haiku = simple auxiliary tasks. Judged not by "cost efficiency" but by "whether quality is sufficient."

#### Sub-agent Memory Scope Definitions (C-3)

| Scope | Access Scope | SOT | Parent Session Context | Knowledge Index | Purpose |
|---|---|---|---|---|---|
| `user` | Agents across all projects | read-only | None | Available | Global utility agent |
| `project` | Agents within current project | read-only | Passed via Task prompt | Available | Project specialist agent (default) |
| `local` | Single agent session | read-only | Passed via Task prompt | None | One-off analysis/processing task |

> **Relationship with Context Preservation**: A `project`-scoped agent can read session context if the parent's `latest.md` path is included in the Task prompt. The `local` scope uses only content passed in the prompt and has no cross-session memory.

### Agent Team (When Parallel Collaboration is Required)

```markdown
### [N]. (team) [Step Name]
- **Team**: `[team-name]`
- **Checkpoint Pattern**: [standard|dense] — Selection criteria: `references/claude-code-patterns.md §DCP`
- **Tasks**:
  - `@[teammate-1]` ([model]): [Task description]
    - **Checkpoints** (for dense pattern):
      - CP-1: [Direction-setting deliverable]
      - CP-2: [Intermediate deliverable]
      - CP-3: [Final deliverable]
  - `@[teammate-2]` ([model]): [Task description]
- **Join**: [Join condition — e.g. proceed to next step after all teammates complete]
- **SOT Write**: Team Lead alone updates `state.yaml` (teammates generate deliverable files only)
```

> **Selection Criterion**: Use Agent Team not because "it is fast," but only when independent specialist parallel work or multi-perspective cross-verification **raises quality**. Details: `references/claude-code-patterns.md §2`

**Team Lifecycle Patterns:**

| Pattern | Description | SOT Consistency | When to Use |
|---|---|---|---|
| **Step-scoped** (Default) | TeamCreate at step start → TeamDelete at step completion | Simple — tracks 1 active_team only | Most cases |
| **Multi-step** | Maintain team across multiple steps | Complex — teammate rotation/addition tracking required | When the same specialist group must execute consecutive steps |

> **The default is Step-scoped.** Use Multi-step only when quality improvement is clear, and document the rationale under "Quality-First Adjustment" in the SOT section.

### SOT (State Management)
- **SOT File**: `.claude/state.yaml`
- **Write Permission**: [Orchestrator or Team Lead — single write point]
- **Agent Access**: [Read-only — generate deliverable files only, direct modification of SOT prohibited]
- **Quality-First Adjustment**: [When default SOT pattern causes a quality bottleneck (e.g. teammates working with stale data), document structural adjustment rationale such as direct inter-teammate deliverable references here. If none, specify "Default pattern applied." Details: `references/claude-code-patterns.md §State Management`]

#### SOT Schema when using Agent Team (active_team)

Agent Team `(team)` step-enabled workflows add the `active_team` field to SOT:

```yaml
# state.yaml — Additional fields when Agent Team is active
workflow:
  # ... existing fields (name, current_step, status, outputs, autopilot) ...
  active_team:
    name: "[team-name]"
    status: "partial"               # partial | all_completed
    tasks_completed: ["task-1"]
    tasks_pending: ["task-2", "task-3"]
    completed_summaries:            # RLM Layer 2 — Preserves team task context upon session restoration
      task-1:
        agent: "@[agent-name]"
        model: "[opus|sonnet|haiku]"
        output: "[deliverable path]"
        summary: "[Task summary — 1-2 sentences]"
  completed_teams: []               # Completed team history (audit trail)
```

**SOT Update Timings (performed by Team Lead only):**
1. Immediately after `TeamCreate` → record `active_team`
2. Upon each Teammate completion (immediately) → append to `tasks_completed`, record `completed_summaries`
3. Upon all Tasks completion (immediately) → record `outputs`, increment `current_step`
4. Immediately after `TeamDelete` → move `active_team` → `completed_teams`

> **Detailed Protocol**: `references/claude-code-patterns.md §SOT Update Protocol`

### Task Management

```markdown
# Task Design within Workflow (when using Agent Team)
#### Task [N]: [Task Name]
- **subject**: "[Short title]"
- **description**: "[Execution details + deliverable path]"
- **activeForm**: "[In-progress status phrasing]"
- **owner**: `@[agent-name]`
- **blocks**: [List of other tasks dependent on this task]
- **blockedBy**: [List of other tasks this task depends on]
```

> **Caution**: The Task List (`~/.claude/tasks/`) is a task assignment and tracking tool, not the SOT. Workflow state must be managed in the SOT (`state.yaml`).

#### Task Lifecycle (Standard Flow)

Standard flow performed by Orchestrator (= Team Lead) in `(team)` step:

```
1. TeamCreate(team_name="step-N-team")
   → SOT active_team.name = "step-N-team", status = "partial"

2. TaskCreate(subject, description, activeForm, owner=@teammate-name)
   → Task ID generated (e.g. #1, #2, ...)
   → Append ID to SOT active_team.tasks_pending

3. Task(subagent_type, team_name, name=@teammate-name)
   → Create Teammate + automatically receive task assignment

4. Teammate task execution:
   a. TaskUpdate(taskId, status="in_progress")
   b. Generate deliverable (save file to disk)
   c. L1 self-verification (against Verification criteria)
   d. L1.5 pACS self-scoring (Pre-mortem → F/C/L)
   e. SendMessage(content="Report + pACS score", recipient="team-lead")
   f. TaskUpdate(taskId, status="completed")

5. Team Lead reception and SOT update:
   a. Receive report → L2 comprehensive verification
   b. Move ID to SOT active_team.tasks_completed
   c. Record summary in SOT active_team.completed_summaries
   d. If L2 FAILS → SendMessage(feedback) → Teammate rework

6. All tasks completed:
   a. Record SOT outputs.step-N
   b. Increment SOT current_step (+1)
   c. SOT active_team.status = "all_completed"
   d. TeamDelete → move SOT active_team → completed_teams
```

> **Task ID ↔ SOT Mapping**: Task IDs are automatically generated upon `TaskCreate`. Record Task subject in SOT `active_team.tasks_completed`, and record `{task_subject: {agent, output_path, pacs_score, summary}}` in `completed_summaries`.

### Hooks

```json
// .claude/settings.json format
{
  "hooks": {
    "[event_name]": [
      {
        "matcher": "[target_tool — e.g. Edit|Write]",  // optional
        "hooks": [
          {
            "type": "command",                      // command | prompt | agent
            "command": "[command to run]",
            "timeout": 30                            // in seconds
          }
        ]
      }
    ]
  }
}
```

**Exit Code Rules**: `0` = Pass, `2` = Block (stderr → feedback to Claude), other = non-blocking error
**Detailed Patterns**: `references/claude-code-patterns.md §3. Hooks`

### Setup Hooks (Optional — when infrastructure verification is required)

Included when workflow depends on infrastructure such as Hook scripts, external dependencies, or runtime directories.

```json
// .claude/settings.json (Setup event)
{
  "hooks": {
    "Setup": [
      {
        "matcher": "init",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/[setup_script].py",
          "timeout": 30
        }]
      }
    ]
  }
}
```

| Inclusion Criteria | Exclusion Criteria |
|---|---|
| 3 or more Hook scripts | Simple workflow without Hooks |
| External dependencies (PyYAML, npm, etc.) | Standard library only |
| Runtime directory pre-creation needed | No separate infrastructure required |
| CI/CD pipeline integration (`--init-only`) | Local-only workflow |

> **No SOT Access**: Setup Hooks operate at the infrastructure layer and do not access the SOT (`state.yaml`).
> **Detailed Patterns**: `references/claude-code-patterns.md §3-1. Setup Hooks`

### Slash Commands

```markdown
# .claude/commands/[command-name].md format
---
description: "[Command description]"
---

[Prompt passed to Claude when command executes]
$ARGUMENTS  ← User input parameters
```

### Required Skills
[Required skill list — `.claude/skills/[name]/SKILL.md`]

### MCP Servers
[External integrated servers — defined in `.mcp.json` or `.claude/settings.json`]

### Runtime Directories

Directories that must be auto-created during workflow execution. Pre-validated in Setup Hook (`--init`).

```yaml
runtime_directories:
  # Mandatory — Verification Gate deliverables
  verification-logs/:        # step-N-verify.md (L1 verification results)

  # Conditional — when feature is active
  autopilot-logs/:           # step-N-decision.md (Autopilot auto-approval decision log)
  pacs-logs/:                # step-N-pacs.md (pACS self-confidence evaluation result)
  review-logs/:              # step-N-review.md (Adversarial Review — Enhanced L2 result)
  translations/:             # glossary.yaml + translated outputs (@translator outputs)
```

> **Initialization Timing**: Create with `mkdir -p` before first workflow run, or include verification logic in Setup Hook.
> **gitignore Consideration**: Adding `verification-logs/`, `autopilot-logs/`, `pacs-logs/` to project `.gitignore` is recommended (runtime deliverables).

### Error Handling

```yaml
error_handling:
  on_agent_failure:
    action: retry_with_feedback
    max_attempts: 3
    escalation: human    # Escalate to user when exceeding 3 attempts

  on_validation_failure:
    action: retry_or_rollback
    retry_with_feedback: true
    rollback_after: 3    # Rollback to previous step after 3 failures

  on_hook_failure:
    action: log_and_continue   # Hook failure does not block workflow

  on_context_overflow:
    action: save_and_recover   # Automatic application of Context Preservation System

  on_teammate_failure:              # When using Agent Team
    attempt_1: retry_same_agent     # Feedback via SendMessage → same Teammate reworks
    attempt_2: replace_with_upgrade # Teammate shutdown → new Teammate (upgraded model)
    attempt_3: human_escalation     # Request user judgment via AskUserQuestion
```

> **Detailed Patterns**: `references/claude-code-patterns.md §Error Handling`

### Autopilot Logs (When using Autopilot mode)

```yaml
autopilot_logging:
  log_directory: "autopilot-logs/"
  log_format: "step-{N}-decision.md"
  required_fields:
    - step_number
    - checkpoint_type        # slash_command | ask_user_question
    - decision
    - rationale              # Grounded in Absolute Criterion 1
    - timestamp
  template: "references/autopilot-decision-template.md"
```

### pACS Logs (When pACS is active — default: enabled)

```yaml
pacs_logging:
  log_directory: "pacs-logs/"
  log_format: "step-{N}-pacs.md"
  translation_log_format: "step-{N}-translation-pacs.md"
  dimensions: [F, C, L]                  # Factual Grounding, Completeness, Logical Coherence
  translation_dimensions: [Ft, Ct, Nt]   # Fidelity, Translation Completeness, Naturalness
  scoring: "min-score"                    # pACS = min(F, C, L)
  triggers:
    GREEN: "≥ 70 → auto-proceed"
    YELLOW: "50-69 → proceed with flag"
    RED: "< 50 → rework or escalate"
  protocol: "AGENTS.md §5.4"
```

**Decision Log Example** (`autopilot-logs/step-3-decision.md`):

```markdown
# Decision Log — Step 3

- **Step**: 3
- **Checkpoint Type**: (human) — Review and select insights
- **Decision**: Select all top 5 insights (maximize comprehensiveness)
- **Rationale**: Absolute Criterion 1 — Chose to include all insights without
  exclusion to maximize quality, determining priorities during Planning Phase.
  Prematurely excluding specific insights risks information loss.
- **Timestamp**: 2026-02-16 14:30:00
- **Alternatives Considered**:
  - Select top 3 only → Rejected due to risk of information loss
  - Select 1 per category → Rejected because category classification is incomplete
```

> **Runtime Assistance**: The Stop hook (`generate_context_summary.py`) detects missing Decision Logs and automatically generates them as a safety net. Logs generated directly by Claude always take precedence.

```

## Notation Rules

| Notation | Meaning |
|---|---|
| `(human)` | Human intervention/review required |
| `(team)` | Agent Team parallel execution block |
| `(hook)` | Automated verification/quality gate |
| `@agent-name` | Sub-agent invocation |
| `@translator` | Translation sub-agent — invoked in `Translation` field |
| `/command-name` | Slash command execution |
| `[skill-name]` | Skill reference |
| `Review: @reviewer \| @fact-checker \| none` | Step-by-step adversarial review applicability (Enhanced L2 — AGENTS.md §5.5) |
| `Translation: ... \| none` | Step-by-step translation applicability (text deliverables only) |

## Example: Blog Content Generation Workflow

```markdown
# Blog Content Pipeline

A workflow for systematically researching, planning, and writing blog content.

## Overview

- **Input**: Content channels (RSS, Newsletter, SNS)
- **Output**: Publishing-ready blog post
- **Frequency**: Weekly
- **Autopilot**: disabled

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.

- **Quality Gene**: Content quality at each step is the sole criterion (speed and volume ignored)
- **SOT Gene**: Centralized pipeline state management via `.claude/state.yaml`
- **QA Gene**: L0 (file existence) → L1 (verification criteria) → L1.5 (pACS self-evaluation) → L2 (adversarial review) verification stack
- **Strongly Expressed**: P1 (data refinement — RSS noise reduction), P2 (expert delegation — separating collection, analysis, writing)

---

## Research

### 1. Resource Collection
- **Agent**: `@content-collector`
- **Verification**:
  - [ ] Collection completed across all defined channels (RSS, Newsletter, SNS)
  - [ ] Each collected item includes source URL + collection date
  - [ ] Minimum 10 collected items
- **Task**: Collect latest content from designated channels
- **Output**: `raw-contents.md`
- **Translation**: none

### 2. Insight Extraction
- **Agent**: `@insight-extractor`
- **Verification**:
  - [ ] Each insight includes supporting source (references item in Step 1 raw-contents.md)
  - [ ] Minimum 5 insights, each structured with title + summary + evidence
  - [ ] Structured in a format evaluable by Step 3 review agent (title, importance, category)
- **Task**: Derive core insights from collected content
- **Output**: `insights-list.md`
- **Translation**: `@translator` → `insights-list.translated.md`

### 3. (human) Review and Select Insights
- **Action**: Select insights to write into articles
- **Command**: `/review-insights`

---

## Planning

### 4. In-Depth Research
- **Agent**: `@deep-researcher`
- **Verification**:
  - [ ] Minimum 3 professional sources included for each topic selected in Step 3
  - [ ] Each source includes URL + publication date + key citation
  - [ ] Background data/trend metrics required for Step 5 outline drafting included
- **Task**: Research professional materials and trends on selected topics
- **Output**: `research-notes.md`
- **Translation**: `@translator` → `research-notes.translated.md`

### 5. Outline Drafting
- **Agent**: `@outline-writer`
- **Verification**:
  - [ ] Each article outline includes introduction-body-conclusion structure
  - [ ] Key data from Step 4 research results positioned in outline
  - [ ] Estimated word count and target audience specified
- **Task**: Draft article outline based on research content
- **Output**: `article-outlines.md`
- **Translation**: `@translator` → `article-outlines.translated.md`

### 6. (human) Outline Review and Feedback
- **Action**: Review outline and provide revision directions
- **Command**: `/review-outline`

---

## Implementation

### 7. Final Article Writing
- **Agent**: `@article-writer`
- **Verification**:
  - [ ] All revision items from Step 6 feedback reflected
  - [ ] Core insights from Step 4 research data cited in body
  - [ ] Introduction-body-conclusion structure + SEO metadata (title, description, keywords) included
- **Task**: Write final article reflecting feedback
- **Output**: `final-article.md`

---

## Claude Code Configuration

### Sub-agents

\`\`\`yaml
agents:
  content-collector:
    description: "Collect content from RSS/Newsletter"
    tools: [web-fetch, rss-reader]

  insight-extractor:
    description: "Extract core insights from content"
    prompt: "Extract insights that can serve as blog topics from the following content..."

  deep-researcher:
    description: "In-depth investigation of topics"
    tools: [web-search, scholar-search]

  outline-writer:
    description: "Draft article outlines"
    skills: [writing-style]

  article-writer:
    description: "Write final articles"
    skills: [writing-style, seo-optimization]
\`\`\`

### Slash Commands

\`\`\`yaml
commands:
  /review-insights:
    description: "Display extracted insights list and await selection"

  /review-outline:
    description: "Display drafted outline and await feedback input"

  /run-pipeline:
    description: "Execute entire workflow"
\`\`\`

### Agent Team (Research Phase Parallelization)

When performing Step 1~2 in parallel:
- Team name: `blog-research`
- `@content-collector`: RSS/Newsletter collection → generate `raw-contents.md`
- `@trend-analyzer`: Trend data analysis → generate `trend-data.md`
- **Join**: Team Lead receives deliverables from both teammates → merges state into `state.yaml` → proceed to Step 3
- **SOT Write**: Team Lead alone updates `state.yaml` (teammates generate deliverable files only)

### Hooks

\`\`\`json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "prettier --write \"$(jq -r '.tool_input.file_path')\" 2>/dev/null || true"
        }]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "prompt",
          "prompt": "Verify whether all sources of the deliverable are included.",
          "model": "haiku"
        }]
      }
    ]
  }
}
\`\`\`

### Required Skills
- writing-style
- seo-optimization
- content-formatting

### MCP Servers
- rss-reader-mcp
- notion-mcp (optional)
```
