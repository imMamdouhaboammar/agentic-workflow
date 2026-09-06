# Claude Code Implementation Patterns

Implementation patterns for executing workflow.md in Claude Code.

## Core Components

### 1. Sub-agents

Specialized agents defined as `.md` files in the `.claude/agents/` directory.
Delegate context within a single session to perform independent tasks.

```markdown
# .claude/agents/researcher.md
---
name: researcher
description: Web search and data investigation specialist. Automatically delegated for research tasks.
model: sonnet
tools: Read, Glob, Grep, WebSearch, WebFetch
maxTurns: 30
memory: project
---

You are a research specialist.
You systematically collect and summarize materials on given topics.

## Operating Principles
- Sources (URLs) mandatory for all information
- Organize core insights in structured formats
- Save collection results as markdown files
```

```markdown
# .claude/agents/writer.md
---
name: writer
description: Content writing specialist
model: opus
tools: Read, Write, Edit, Glob, Grep
skills:
  - writing-style
memory: project
---

You are a professional writer.
You craft high-quality content based on research materials.
```

```markdown
# .claude/agents/reviewer.md
---
name: reviewer
description: Quality review and feedback generation. Automatic review after code/document changes.
model: sonnet
tools: Read, Glob, Grep
permissionMode: plan
---

You are a rigorous editor.
Review against the following criteria:
- Accuracy, consistency, completeness
- Source verification status
- Target audience suitability
```

**Key Frontmatter Fields:**

| Field | Description | Example |
|---|---|---|
| `name` | Unique identifier | `researcher` |
| `description` | Auto-delegation trigger description | `"Automatically delegated for research tasks"` |
| `model` | Model used | `opus`, `sonnet`, `haiku` |
| `tools` | Allowed tools (comma-separated) | `Read, Write, Bash` |
| `disallowedTools` | Blocked tools | `Write, Edit` |
| `permissionMode` | Permission mode | `default`, `plan`, `dontAsk` |
| `maxTurns` | Maximum turns | `30` |
| `memory` | Persistent memory scope | `user`, `project`, `local` |
| `skills` | List of skills to inject | `[writing-style]` |
| `mcpServers` | Available MCP servers | `[slack, github]` |
| `hooks` | Agent-scoped hooks | (See Hooks section below) |

**Design Principles:**
- Single responsibility: One role per agent
- Clear inputs/outputs: Defined at the Task level
- Minimal tools: Assign only necessary tools
- Appropriate model allocation: Choose opus/sonnet/haiku based on complexity

**Model Selection Protocol (grounded in Absolute Criterion 1):**

> The sole criterion for model selection is **the quality demand level of the given task**. Judged not by "cost efficiency" but by "whether quality is sufficient."

| Model | Suitable Tasks | Quality Characteristics |
|---|---|---|
| `opus` | Complex analysis, research, writing — core tasks requiring highest quality | Highest standard |
| `sonnet` | Collection, scanning, structuring — stable quality recurring tasks | High standard |
| `haiku` | Dashboard, status checking, simple judgment — low-complexity auxiliary tasks | Sufficient standard |

**Model Selection Judgment Procedure:**

1. What is the **core quality factor** of the task? (Accuracy? Creativity? Analytical depth? Pattern recognition?)
2. Is the **quality difference between models significant** for that quality factor?
   - **Yes** → Choose higher model (if a quality difference exists, the best must be used)
   - **No** → Lower model permitted (exploration results are model-agnostic — haiku permitted)
3. **If uncertain** → Choose higher model (Absolute Criterion 1 — quality guarantee principle)

**Concrete Examples:**

| Task | Quality Factor | Difference Across Models | Selection | Rationale |
|---|---|---|---|---|
| File exploration/directory structure inspection | Exploration accuracy | Insignificant | `haiku` | Exploration results are model-agnostic |
| Research results synthesis and analysis | Analytical depth and nuance | Significant | `opus` | Analytical depth is core to quality |
| Code review/quality verification | Pattern recognition | Significant | `sonnet`+ | Requires structural issue detection capability |
| Data format conversion | Rule compliance | Insignificant | `haiku` | Deterministic conversion is model-agnostic |
| Professional content writing | Creativity and accuracy | Significant | `opus` | Writing quality dictates final deliverable quality |

---

### 2. Agent Teams (Swarm)

Team-based parallel task system where multiple independent sessions collaborate.
Unlike Sub-agents, each teammate possesses a completely independent context.

> **Experimental Feature** — Must be enabled in `settings.json`

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Architecture:**

```
┌──────────────────────────────────────────────────────┐
│                    Team Lead                          │
│  (TaskCreate → Assignment → SendMessage → Coordinate) │
│  ★ SOT Write Permission: state.yaml updated by Team  │
│    Lead only                                         │
├──────────┬──────────┬────────────────────────────────┤
│ Teammate │ Teammate │ Teammate                       │
│@researcher│ @writer │ @data-processor                │
│(indep.   │(indep.   │(indep.                         │
│ session) │ session) │ session)                       │
│Read-only │Read-only │Read-only                       │
└──────────┴──────────┴────────────────────────────────┘
     │            │           │
     ├── Shared Task List ────┤  ← Task assignment/tracking tool
     │  (~/.claude/tasks/)    │
     └── SOT (state.yaml) ───┘  ← Workflow state (Team Lead write only)
```

**Team Creation → Task → Termination Flow:**

```markdown
## Agent Team Definition in workflow.md

### Team: content-pipeline
- **Members**:
  - `@researcher` (sonnet): Data collection
  - `@writer` (opus): Content writing
  - `@fact-checker` (opus): Fact checking
- **Shared Tasks**: `~/.claude/tasks/content-pipeline/`
- **Coordination**: Team Lead assigns via TaskCreate, automatic notification upon completion
```

**Workflow Notation:**

```markdown
### 2. (team) Parallel Research
- **Team**: `content-pipeline`
- **Tasks**:
  - `@researcher`: Collect latest trends from web sources
  - `@data-processor`: Organize existing data and statistical analysis
- **Join**: Proceed to Step 3 after all teammates complete
```

**Sub-agent vs Agent Team — Quality-Based Selection:**

> Choose not based on speed or cost, but on **which structure achieves the highest final deliverable quality**.

**Quality Judgment Matrix (5 Factors):**

| Quality Factor | Sub-agent Advantage | Agent Team Advantage | Assessment Question |
|---|---|---|---|
| **Context Depth** | Must deeply reference prior step results | Each task requires independent expertise | "Will quality degrade if nuance from previous steps is lost?" |
| **Cross-Validation** | Single perspective guarantees consistency | Multi-perspective analysis eliminates bias | "Is one person's analysis sufficient, or are multiple expert opinions needed?" |
| **Deliverable Consistency** | Unification of style/tone is critical | Each deliverable is independently complete | "Must deliverables be unified, or are they independent?" |
| **Error Isolation** | Errors must be caught in overall context | Individual task failures must not affect other tasks | "If one fails, must the entire workflow restart?" |
| **Information Transfer Loss** | High risk of nuance loss via file transfer | Transferring structured data alone is sufficient | "Is there tacit context not captured in the transfer file?" |

**Judgment Rules:**
1. If Sub-agent advantage in 3+ factors → **Sub-agent**
2. If Agent Team advantage in 3+ factors → **Agent Team**
3. If tied → **Context Depth** factor serves as tiebreaker (context loss is irrecoverable)
4. If uncertain → **Sub-agent** (safe default — context preservation is the baseline of quality)

**When Agent Team Elevates Quality:**
- When distinct expert domains must each be handled at the highest level of depth
- When multi-perspective analysis/cross-validation yields richer outcomes than a single agent
- When quality requires each specialist to focus 100% within an independent context

**When Sub-agent Elevates Quality:**
- When a single specialist must maintain deep context with consistent handling
- When accuracy of context transfer across steps is core to outcome quality
- When strong sequential dependencies exist where prior step quality directly affects subsequent steps

**Teammate Deliverable Quality Requirements:**

> When using Agent Team, to prevent information disconnect due to context isolation, each teammate's deliverable file must contain the following structure:

```markdown
# [Deliverable Title]

## Main Output
[Task result body — Absolute Criterion 1: full quality, no abbreviations]

## Decision Rationale
- Uncertain items: [Explicit notation]
- Excluded information and exclusion rationale: [Why not included]
- Data validity scope/constraints: [Time range, source limitations, etc.]

## Cross-Reference Cues
- Context other Teammates need to know: [Dependency information]
- Conditions affecting subsequent steps: [Prerequisites, caveats]
```

This requirement solves the **nuance loss problem of file-based transfer**. By communicating decision context alongside structured facts, quality degradation is prevented even in independent contexts.

**Team Lifecycle Patterns:**

> Default recommendation is **Step-scoped Team** (team creation/destruction per step). Guarantees SOT consistency and error isolation.

| Pattern | Description | SOT Consistency | Error Isolation | Usage Condition |
|---|---|---|---|---|
| **Step-scoped** (Default) | TeamCreate at workflow step start, TeamDelete at completion | Simple (updates SOT upon step transition) | High (step failure does not propagate) | Most cases |
| **Multi-step** | Maintain team across multiple steps | Complex (intermediate state management needed) | Low (propagation risk) | Only when cross-references among teammates are core to quality |

```markdown
## Step-scoped Team Flow

### N. (team) Parallel Research
- TeamCreate("research-pipeline") → record SOT active_team
- Assign Tasks → Teammate execution → deliverable generation
- All Tasks completed → verify deliverables (Anti-Skip Guard)
- Record SOT outputs + increment current_step (+1)
- TeamDelete → remove SOT active_team, move to completed_teams
```

> **Reference**: The 3 patterns for passing context to agents (Full Delegation, Filtered Delegation, Recursive Decomposition) are covered in detail in `references/context-injection-patterns.md`.

#### Dense Checkpoint Pattern (DCP)

In a `(team)` step, the baseline structure where Team Lead verifies only after Teammates complete their entire Tasks can cause full rework if an early direction error occurs. DCP inserts intermediate checkpoints (CP) to detect directional errors early.

**Uses existing infrastructure only**: `TaskCreate` + `SendMessage` primitives. No new Hooks or scripts required.

**Application Criteria:**

| Condition | Pattern |
|---|---|
| Expected turns for Task ≤ 10 | `standard` (baseline approach) |
| Expected turns for Task > 10 | `dense` (CP-1/2/3) |
| Task contains direction-determining points | `dense` recommended |
| Rework cost on Task failure is high | `dense` strongly recommended |

**Checkpoint Structure (Maximum 3):**

| CP | Role | Deliverable |
|---|---|---|
| CP-1 | Discovery/Setup — Direction setting | Target list, data sources, methodology report |
| CP-2 | Collection/Draft — Intermediate deliverable | Collected data summary, draft, gap identification |
| CP-3 | Final — Final deliverable | Completed analysis + pACS self-evaluation |

**Embed CP Protocol in TaskCreate Description:**

```markdown
### Checkpoint Protocol (Dense Checkpoint Pattern)
You MUST report at each checkpoint BEFORE proceeding.
Wait for Team Lead acknowledgment before continuing.

**CP-1: [Phase Name]**
- [What to do]
- Report via SendMessage: [what to report]
- STOP and wait for Team Lead response

**CP-2: [Phase Name]** (after CP-1 approval)
- [What to do]
- Report via SendMessage: [what to report]
- STOP and wait for Team Lead response

**CP-3: [Phase Name]** (after CP-2 approval)
- [Final work + output]
- SendMessage: final report + pACS self-rating
- TaskUpdate(completed)
```

**SOT Impact**: None. No change to `active_team` schema. CPs are temporary coordinations based on `SendMessage` and are not recorded in SOT. CP history may optionally be included in natural language in the `summary` field of `completed_summaries`.

---

### 3. Hooks

Deterministic automation that runs automatically at specific points in the workflow lifecycle.
Utilized for code formatting, quality verification, security gates, etc.

#### 3-1. Setup Hooks (Infrastructure Validation)

Deterministic infrastructure validation hooks that run **before** session start.
Triggered by `--init` or `--maintenance` CLI flags and do not access session context.

> **Quality Impact Path (Absolute Criterion 1)**:
> Infrastructure validation → Silent Failure prevention →
> Context Preservation integrity → Session recovery accuracy →
> Infrastructure floor for workflow output quality

**3-Level Progressive Execution (Hierarchical Execution Model):**

| Level | CLI Command | Execution Content | Purpose |
|---|---|---|---|
| **Level 1** — Deterministic Only | `claude --init` | Run Setup Hook script only (Python) | CI/CD, automated verification |
| **Level 2** — Deterministic + Agentic | `claude --init "/install"` | Setup Hook → Agent analyzes/repairs logs | Problem resolution |
| **Level 3** — Interactive | `claude` (normal session) | Setup + full session | Daily work |

**Setup Hook Configuration Format:**

```json
// .claude/settings.json (Project — project-specific infrastructure validation)
{
  "hooks": {
    "Setup": [
      {
        "matcher": "init",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/setup_init.py",
          "timeout": 30
        }]
      },
      {
        "matcher": "maintenance",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/setup_maintenance.py",
          "timeout": 30
        }]
      }
    ]
  }
}
```

**hookSpecificOutput Protocol:**

stdout JSON output format for Setup Hooks. Parsed by Claude Code and injected into context at session start:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Setup",
    "additionalContext": "Infrastructure validation: 10/12 passed (1 critical, 1 warning)"
  }
}
```

**Exit Code Rules (identical to standard Hooks):**

| Code | Behavior | Meaning in Setup Hook |
|---|---|---|
| `0` | Success | Infrastructure healthy — session start permitted |
| `2` | Block | Critical issue detected — remediation required before session start |
| Other | Non-blocking error | Hook internal error (session proceeds) |

**Application Criteria in Workflows:**

| Inclusion Condition | Description |
|---|---|
| 3 or more Hook scripts | Script syntax errors could cause Silent Failure |
| External dependencies required (PyYAML, etc.) | Missing dependencies cause runtime degradation |
| Runtime directories required | Pre-creating runtime infrastructure like Context Preservation |
| CI/CD pipeline integration | Headless verification enabled via `--init-only` |

| Exclusion Condition | Description |
|---|---|
| Simple workflow without Hooks | No targets to verify |
| No external dependencies | Environment verification unnecessary |

**SOT Non-Access Principle:**

Setup Hooks **never access** the SOT (`state.yaml`).
Setup belongs to the infrastructure layer, while SOT belongs to the workflow state layer.
Infrastructure verification operates at a layer beneath workflow execution.

**context_guard.py Bypass Rationale:**

Setup Hooks execute directly from Project settings (`.claude/settings.json`).
Reasons for bypassing the Global dispatcher (`context_guard.py`):
1. Setup is project-unique infrastructure validation — not a Global concern
2. Executes **before** session start — unrelated to in-session event routing
3. `--init`/`--maintenance` triggers are independent of SessionStart/Stop Hooks

**Slash Command Integration (Level 2):**

Slash Commands for analyzing Setup Hook log files:

| Slash Command | Trigger | Analysis Target |
|---|---|---|
| `/install` | `claude --init "/install"` | `setup.init.log` — diagnose and fix issues |
| `/maintenance` | `claude --maintenance "/maintenance"` | `setup.maintenance.log` — health check and cleanup |

**Configuration Locations:**

| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | Global (all projects) | No |
| `.claude/settings.json` | Project | Yes (can be committed) |
| `.claude/settings.local.json` | Project (local) | No |
| Agent frontmatter `hooks:` | Agent-scoped | Yes |

**Major Hook Events:**

| Event | Firing Timing | Blockable | Workflow Purpose |
|---|---|---|---|
| `Setup` | **Before session start** (`--init`/`--maintenance`) | Yes (exit 2) | Infrastructure verification, health check (§3-1 details) |
| `SessionStart` | Session start/resume | No | Context restoration, environment variable configuration |
| `PreToolUse` | Before tool execution | Yes | Blocking dangerous commands, input modification |
| `PostToolUse` | After tool execution | No | Automated formatting, logging |
| `Stop` | Claude response completed | Yes | Context saving, summary generation |
| `SessionEnd` | Session exit (`/clear`) | No | Full snapshot saving, Knowledge Archive |
| `UserPromptSubmit` | After user input | Yes | Input validation, pre-processing |
| `SubagentStart` | Sub-agent spawned | No | Environment preparation |
| `SubagentStop` | Sub-agent terminated | Yes | Deliverable verification |
| `TeammateIdle` | Teammate transitioned to idle | Yes | Additional task assignment |
| `TaskCompleted` | Task completed | Yes | Quality gate (blocked via exit 2) |
| `PreCompact` | Before context compaction | No | Preserving critical state |

**Hook Types:**

```json
// Type 1: Command — Execute shell script
{
  "type": "command",
  "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/validate.py",
  "timeout": 30
}

// Type 2: Prompt — LLM single-turn evaluation
{
  "type": "prompt",
  "prompt": "Evaluate whether this change breaks backward API compatibility. $ARGUMENTS",
  "model": "haiku"
}

// Type 3: Agent — Sub-agent based verification (up to 50 turns)
{
  "type": "agent",
  "prompt": "Run test suite and verify results. $ARGUMENTS",
  "timeout": 120
}
```

**Workflow Application Example:**

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs prettier --write 2>/dev/null || true",
            "statusMessage": "Formatting automatically..."
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/block-destructive.sh && bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/block-destructive.sh || true"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify deliverable quality of completed task. Reject if below standard.",
            "timeout": 60
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "test -f \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/restore_context.py && python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/restore_context.py || true"
          }
        ]
      }
    ]
  }
}
```

**Exit Code Rules:**

| Code | Behavior | When to Use |
|---|---|---|
| `0` | Allow (parse JSON output) | Standard pass |
| `2` | Block (stderr → feedback to Claude) | Preventing hazardous actions, sub-standard quality |
| Other | Non-blocking error (logged only) | Debugging information |

**Agent Built-in Hook (frontmatter):**

```markdown
---
name: db-reader
description: Read-only DB query execution
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

---

### 4. Slash Commands

User interaction and workflow control.
Defined as `.md` files in the `.claude/commands/` directory.

```markdown
# .claude/commands/start-workflow.md
---
description: "Start workflow execution"
---

Read the $ARGUMENTS workflow from workflow.md
and execute each step sequentially.
```

```markdown
# .claude/commands/review-output.md
---
description: "Review and approve/reject deliverable"
---

Display deliverable of current step and await user approval or rejection.
- On approval: automatically advance to next step
- On rejection: pass feedback to agent for rework
```

**Passing Command Parameters:**

Slash Commands can accept user inputs via `$ARGUMENTS`:

```markdown
# .claude/commands/select-topic.md
---
description: "Select topic and advance workflow"
---

Selected topic number: $ARGUMENTS

Advance to the next step of the workflow based on this topic.
- Update selected_topic field in state.yaml
- Delegate research to @deep-researcher suited for the topic
```

---

### 4-1. AskUserQuestion (User Inquiry)

A tool for programmatically presenting structured questions to the user during workflow execution.
While Slash Commands "define" user intervention points, AskUserQuestion is a tool for agents to "actively" query the user.

> **P4 Rule Application**: Maximum 4 questions, 2-4 options per question. If there is no ambiguity, proceed without questions.

**Workflow Application Example:**

```markdown
### 1. (research) Requirements Gathering
- **Agent**: Orchestrator (direct execution)
- **Tool**: AskUserQuestion
- **Strategy**: Iterative questioning to refine requirements

#### Question Design:

**Round 1: Purpose Identification**
1. "What is the primary purpose of this workflow?"
   - (a) New content generation
   - (b) Refactoring existing content
   - (c) Data analysis and report generation

2. "Who is the target audience?"
   - (a) Technical specialists
   - (b) Business decision-makers
   - (c) General users

**Round 2: Constraint Identification** (Dynamic questions based on Round 1 results)
3. "Which quality criterion takes highest priority?"
   - (a) Accuracy (source verification mandatory)
   - (b) Readability (accessible exposition first)
   - (c) Comprehensiveness (covering all dimensions)

- **Output**: `requirements.md` (structured requirements document)
- **SOT Update**: Record summary of collected requirements in state.yaml
```

**Utilization in Case 1 (Idea-Only) Workflows:**

When the user provides only an idea without specific requirements, use AskUserQuestion as the core tool of the Research Phase:

```markdown
### Research Phase — Requirements Clarification
1. Ask 2-3 core directional questions via AskUserQuestion (adhering to P4 rules)
2. @researcher collects relevant materials based on responses
3. Ask Round 2 questions via AskUserQuestion based on collected results (present options)
4. Generate final requirements document → pass to Planning Phase
```

**Slash Command vs AskUserQuestion:**

| Attribute | Slash Command | AskUserQuestion |
|---|---|---|
| **Trigger** | Directly executed by user | Actively invoked by agent |
| **Definition Location** | `.claude/commands/*.md` | Within workflow step |
| **Purpose** | Review/approval/selection (predefined checkpoints) | Requirements gathering/option selection (dynamic questions) |
| **Suitable Phase** | Planning (review), Implementation (approval) | Research (requirements gathering), Planning (option selection) |
| **P4 Rules** | Not applicable (user-driven) | Applied (maximum 4 questions, 2-4 options) |
| **State Management** | User input reflected in SOT | User input reflected in SOT |

---

### 5. Skills Integration

Reusable knowledge and logic packages. Provides two execution contexts:

#### Inline Skill (Default)

Skill contents are injected directly into the main conversation. Access to conversation history is preserved.

```markdown
# Inline skill reference in workflow.md

### 5. Article Writing
- **Agent**: `@writer`
- **Skills**: `[writing-style]`, `[seo-optimization]`
- **Task**: Draft final article based on outline
```

- **Suitable for**: Guidelines, conversational workflows, injecting domain expertise
- **SOT**: Directly accessed within the main conversation context

#### Forked Skill (`context: fork`)

Skill contents become the **task prompt for a separate sub-agent**. Executes in an isolated context.

```yaml
# SKILL.md frontmatter
---
name: code-analyzer
description: Analyzes codebase structure and produces reports.
context: fork
agent: general-purpose    # Explore | Plan | general-purpose | <custom-agent>
---
```

- **Suitable for**: Independent analysis, bulk processing, codebase exploration, file transformation
- **Conversation History**: None (isolated)
- **SOT Access**: Indirect — inject SOT state via `!`command`` pre-processing

**Agent Type Selection:**

| Agent Type | Model | Tools | Purpose |
|---|---|---|---|
| `Explore` | Haiku | Read-only | File exploration, code search |
| `Plan` | Inherited | Read-only | Architecture research, implementation planning |
| `general-purpose` | Inherited | All | Multi-step tasks, file generation |
| Custom Agent | Per config | Per config | Specialized roles defined in `.claude/agents/` |

#### Fork + SOT Integration Pattern

Forked skills cannot modify the SOT directly. For data consistency:

1. **Inject SOT via Pre-processing**: Inject SOT snapshot in skill content via `!`cat state.yaml`` syntax
2. **Output to File**: Fork saves deliverable as file → Orchestrator records path in SOT `outputs`
3. **No SOT Write**: Direct SOT modification from within fork is strictly prohibited (Absolute Criterion 2)

#### Skill Hot-Reload

Modifications to skill files in `~/.claude/skills/` or `.claude/skills/` **take effect immediately without session restart**. Sub-agents (`.claude/agents/`) require the `/agents` command or session restart.

**Inline vs Fork Selection Criteria:**

| Criterion | Inline | Fork |
|---|---|---|
| User dialogue required (Q&A, confirmation) | ✅ | ❌ |
| Operating within conversational context (in-progress drafts, discussions) | ✅ | ❌ |
| Independent analysis/transformation tasks | ❌ | ✅ |
| Execution details clutter the main conversation | ❌ | ✅ |
| SOT state access | Direct | Indirect (`!`cmd`` pre-processing) |

### 6. MCP Server Integration

External service integration. Defined in `.claude/settings.json` or `.mcp.json`.

```json
// .mcp.json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/mcp-server"],
      "env": { "NOTION_TOKEN": "${NOTION_TOKEN}" }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-slack"],
      "env": { "SLACK_TOKEN": "${SLACK_TOKEN}" }
    }
  }
}
```

---

## Workflow Execution Patterns

### Pattern 1: Sequential Pipeline (Sub-agent)

Default pattern where steps execute sequentially.

```
@agent-1 → @agent-2 → (human) → @agent-3 → @agent-4
```

**Quality Rationale:** A single specialist maintaining deep context maximizes deliverable consistency and accuracy.

### Pattern 2: Parallel Branches (Agent Team)

Independent steps executing in parallel.

```
               ┌→ @teammate-a ─┐
(team-lead) ──┤                ├→ (human) → @agent-merge
               └→ @teammate-b ─┘
```

**Quality Rationale:** Combining independent focus from each specialist with multiple perspectives yields richer quality than a single agent.

### Pattern 3: Conditional Flow

Branching based on conditions.

```
@agent-1 → Condition? ─┬→ Path A → @agent-3
                        └→ Path B → @agent-3
```

### Pattern 4: Hook-gated Pipeline

Pipeline incorporating automated validation gates.

```
@agent-1 → [Hook: Format Check] → @agent-2 → [Hook: Quality Check] → (human)
                 ↓ fail                                ↓ fail
            Auto-retry                         Feedback to Claude
```

**Suitable for:** When code quality, security verification, and deliverable compliance standards are critical.

### Pattern 5: Team + Hook Combined

Advanced pattern combining team collaboration with quality gates.

```
(team-lead)
  ├→ @researcher [TaskCompleted hook: Source verification]
  ├→ @writer [TaskCompleted hook: Quality verification]
  └→ @fact-checker [SubagentStop hook: Merge results]
       ↓ all complete
  (human) → @editor → Final Deliverable
```

---

## Human-in-the-Loop Patterns

### Review Then Proceed

```markdown
### 3. (human) Review and Approval
- **Pause**: Automatic pause
- **Display**: Display results from prior step
- **Input**: Approval / Rejection / Revision request
- **Resume**: `/approve` or `/request-revision "feedback"`
```

### Selectable Input

```markdown
### 3. (human) Option Selection
- **Display**: Display option list
- **Input**: Select numbers or items
- **Command**: `/select 1,3,5`
```

### Hook-Based Automated Quality Gate

Pattern for verifying quality automatically without human intervention.

```markdown
### 3. (hook) Automated Quality Verification
- **Event**: `TaskCompleted`
- **Type**: `agent`
- **Check**: Whether deliverable meets quality criteria
- **Pass**: Automatically advance to next step
- **Fail**: exit 2 → feedback passed to agent, rework
```

## Autopilot Execution Pattern

Orchestrator pattern for handling `(human)` steps in Autopilot mode.

### Auto-Approve with Full Execution

```markdown
### 3. (human) Review and Select Insights
- **Autopilot Behavior**:
  1. Generate prior step deliverable **completely** (no abbreviations)
  2. Review deliverable and determine quality-maximizing default (Absolute Criterion 1)
  3. Record decision in `autopilot-logs/step-3-decision.md`
  4. Update SOT: append 3 to `auto_approved_steps`
  5. Advance to next step
- **Interactive Behavior (Default)**:
  - Same as above, but pause and await user input at step 3
```

### Anti-Skip Invariant

```
FOR step IN workflow.steps:
  EXECUTE(step)                    # Execute all steps — skipping prohibited
  ASSERT output_exists(step)       # Confirm deliverable exists
  ASSERT output_not_empty(step)    # Empty deliverables prohibited
  IF step.is_human AND autopilot.enabled:
    auto_approve(step)             # Auto-approve
    log_decision(step)             # Decision log
  UPDATE_SOT(step)                 # Update SOT
```

### Anti-Skip Execution Protocol (Concrete Execution Pseudocode)

```python
MAX_VERIFICATION_RETRIES = 2

def execute_workflow_step(step, sot):
    """Protocol for Orchestrator executing each workflow step.

    Absolute Criterion 1: All deliverables generated with complete quality.
    Absolute Criterion 2: SOT is the sole source of truth for state.
    Verification Protocol: Confirm 100% functional goal achievement (AGENTS.md §5.3).
    """
    # 1. Pre-validation (verify prior step deliverable)
    if step.number > 1:
        prev_key = f"step-{step.number - 1}"
        prev_path = sot.outputs.get(prev_key)
        assert prev_path, f"Step {step.number - 1} output not in SOT"
        assert file_exists(prev_path), f"Step {step.number - 1} output missing"
        assert file_size(prev_path) >= 100, f"Step {step.number - 1} output too small (< 100 bytes)"

    # 1b. Read Verification Criteria BEFORE execution
    verification_criteria = step.get_verification_criteria()  # None if absent

    # 2. Execute step FULLY (Anti-Abbreviation Rule)
    output = step.execute()  # Complete execution, abbreviation prohibited

    # 3. Save output to disk
    write_file(step.output_path, output)

    # 4. Handle (human) checkpoint
    if step.is_human and sot.autopilot.enabled:
        decision = auto_approve_with_quality_default(step, output)
        write_decision_log(step.number, decision)
        # Decision Log: autopilot-logs/step-N-decision.md
        sot.autopilot.auto_approved_steps.append(step.number)

    # 5. Handle (hook) — NEVER override exit code 2
    if step.is_hook and result.exit_code == 2:
        handle_hook_failure(step, result.stderr)
        return  # BLOCKED — do NOT advance

    # 6. Verification Gate (AGENTS.md §5.3 — backward compatible: skip if criteria absent)
    if verification_criteria:
        verify_result = self_verify(step.output, verification_criteria)
        retry_count = 0
        while not verify_result.all_pass and retry_count < MAX_VERIFICATION_RETRIES:
            # Identify failed criteria only and remediate specific portion (not entire rework)
            remediate(step.output, verify_result.failed_criteria)
            write_file(step.output_path, step.output)  # Save updated deliverable
            verify_result = self_verify(step.output, verification_criteria)
            retry_count += 1

        if not verify_result.all_pass:
            escalate_to_user(step, verify_result)  # Escalate to user when exceeding 2 retries
            return  # BLOCKED — do NOT advance

        write_verification_log(step.number, verify_result, retry_count)
        # Verification Log: verification-logs/step-N-verify.md

    # 6b. pACS Self-Rating (AGENTS.md §5.4)
    # ... (Standard pACS logic)

    # 6c. Adversarial Review — Enhanced L2 (AGENTS.md §5.5)
    if step.review_agent:  # Review: @reviewer | @fact-checker | none
        review_output = invoke_subagent(step.review_agent, {
            "artifact": step.output_path,
            "context": step.context_files,
            "generator_pacs": pacs_score,
        })
        write_file(f"review-logs/step-{step.number}-review.md", review_output)

        # P1 Validation (deterministic — validate_review.py)
        validation = run_bash(f"python3 .claude/hooks/scripts/validate_review.py "
                              f"--step {step.number} --project-dir .")
        if not validation.valid:
            escalate_to_user(step, validation.warnings)
            return  # BLOCKED

        if validation.verdict == "FAIL":
            retry_count = 0
            while validation.verdict == "FAIL" and retry_count < MAX_VERIFICATION_RETRIES:
                remediate(step.output, review_output.critical_issues)
                write_file(step.output_path, step.output)
                review_output = invoke_subagent(step.review_agent, {...})
                write_file(f"review-logs/step-{step.number}-review.md", review_output)
                validation = run_bash(f"python3 validate_review.py --step {step.number}")
                retry_count += 1
            if validation.verdict == "FAIL":
                escalate_to_user(step, "Review FAIL after max retries")
                return  # BLOCKED

    # 6d. Translation (only AFTER Review PASS — AGENTS.md §5.5 sequence constraint)
    if step.translation_agent and (not step.review_agent or validation.verdict == "PASS"):
        invoke_subagent(step.translation_agent, step.output_path)

    # 7. Update SOT (increment by exactly +1 sequentially)
    sot.outputs[f"step-{step.number}"] = step.output_path
    sot.current_step += 1  # NEVER increment by more than 1
```

**Verification Gate Design Principles:**
- **Placement**: After Hook (#5), before SOT update (#7) — sequence of deterministic gate → semantic gate
- **Backward Compatibility**: If `verification_criteria` is `None`, skip Gate to preserve existing behavior
- **Partial Rework**: Remediate only components corresponding to failed criteria, not the entire deliverable
- **No SOT Impact**: Verification state is recorded in `verification-logs/`. No SOT schema modification needed — advancing `current_step` inherently signifies successful verification

**Adversarial Review Design Principles:**
- **Placement**: After pACS (#6b), before Translation (#6d) — translation executes only after passing review
- **Backward Compatibility**: If `step.review_agent` is `None`, skip Review to preserve existing behavior
- **P1 Validation**: `validate_review.py` deterministically verifies structural integrity of review reports
- **Rework Loop**: On Review FAIL, remediate critical issues and re-review (up to 10 retries)

### Anti-Abbreviation Rule

Even in Autopilot mode, agents must generate complete deliverables as if under human review.
"Keeping it brief because it's automated" is a **direct violation of Absolute Criterion 1**.

### Hook Behavior (No Changes)

```
(human) → Target for Autopilot auto-approval
(hook)  → Unaffected by Autopilot — blocks/passes as configured
(team)  → Autopilot: Team Lead automatically performs task assignment, model selection, deliverable validation
```

### Autopilot + Agent Team Checklist

> Checklist items to perform when executing `(team)` steps in Autopilot mode.

```markdown
#### Before (team) Step Start
- [ ] Record team info in SOT active_team after TeamCreate
- [ ] Record owner assignment rationale for each Task in Decision Log
- [ ] Record model selection rationale in Decision Log (refer to Model Selection Protocol)

#### During (team) Step Execution
- [ ] Each Teammate performs self-verification prior to reporting (L1 — AGENTS.md §5.3)
- [ ] Immediately update SOT active_team upon each Teammate completion
- [ ] Team Lead verifies each Teammate deliverable against step verification criteria (L2)
- [ ] On L2 FAIL, issue concrete feedback and rerun instruction via SendMessage
- [ ] Apply Team error handling protocol on failures

#### After (team) Step Completion
- [ ] Perform cross-validation across all deliverables (Quality Gate)
- [ ] Generate verification-logs/step-N-verify.md (when Verification criteria exist)
- [ ] Record final deliverable paths in SOT outputs
- [ ] Increment SOT current_step (+1)
- [ ] TeamDelete → move SOT active_team to completed_teams
- [ ] Record team decisions in autopilot-logs/step-N-decision.md
```

### Runtime Reinforcement Mechanisms

A hybrid (Hook + Prompt) architecture reinforcing Autopilot design intent at runtime:

| Layer | Mechanism | Role |
|---|---|---|
| **Hook** | `restore_context.py` | Injects AUTOPILOT EXECUTION RULES at SessionStart |
| **Hook** | `generate_context_summary.py` | Automatically compensates missing Decision Logs + detects missing Reviews at Stop |
| **Hook** | `_context_lib.py` | Preserves Autopilot state section in snapshots (IMMORTAL) + Review P1 validation functions |
| **Hook** | `update_work_log.py` | Autopilot step tracking fields in work_log |
| **Prompt** | `docs/protocols/autopilot-execution.md` | Autopilot Execution Checklist (MANDATORY) |
| **Prompt** | This file | Anti-Skip Execution Protocol + Verification Gate pseudocode |
| **Prompt** | `AGENTS.md §5.3` | Verification Protocol — criteria types, execution protocol, log formats |

---

## State Management (SOT Design)

> **Application of Absolute Criterion 2**: All shared state in a workflow is concentrated in a **single file (SOT)**. Write permissions are held exclusively by the Orchestrator (or Team Lead).
>
> **Absolute Criterion 1 Priority**: If the SOT structure impairs final deliverable quality (e.g. single write bottleneck causing agents to operate on stale data), structural adjustments for quality are permitted. SOT is a **means** to guarantee quality, not an **end** that constrains quality.

### SOT File Structure

```yaml
# .claude/state.yaml — Single SOT file
workflow:
  name: "blog-pipeline"
  current_step: 3
  status: "paused"               # running | paused | completed | escalated
  outputs:
    step-1: "raw-contents.md"
    step-2: "insights-list.md"
  pending_input:
    type: "selection"
    options: [...]

  # Agent Team state (exists only while team step is active)
  active_team:
    name: "research-pipeline"       # team_name passed to TeamCreate
    status: "partial"               # partial | all_completed
    tasks_completed: ["task-1"]     # List of completed Task IDs
    tasks_pending: ["task-2", "task-3"]  # List of pending Task IDs
    completed_summaries:            # RLM compatible — Teammate task summaries (for session restoration)
      task-1:
        agent: "@researcher"
        model: "sonnet"
        output: "research/trends.md"
        summary: "5 core trends derived from 10 sources"
  completed_teams: []               # Terminated team history (audit trail)

  # Autopilot field — under workflow (AGENTS.md §5.1 canonical schema)
  autopilot:
    enabled: true
    activated_at: "2026-02-16T10:30:00"
    auto_approved_steps: [3, 6]  # List of auto-approved (human) steps
```

### SOT State Management Protocol (C-1)

Operational protocol for managing SOT safely during workflow execution.

#### SOT Access Rules

| Role | Read | Write | Notes |
|---|---|---|---|
| Orchestrator / Team Lead | O | O | Sole writing authority |
| Sub-agent | O | X | Generates deliverable files only |
| Teammate | O | X | Reports results to Team Lead |
| Hook Scripts | O | X | Writes to `context-snapshots/` only |

#### SOT Lifecycle

```
1. Workflow start → SOT generated (state.yaml)
2. Each step completion → record path in outputs, increment current_step (+1)
3. (team) step → create active_team → teammate execution → update completed_summaries
4. (human) + autopilot → append to auto_approved_steps
5. Workflow completion → status: "completed"
```

#### Anti-Skip Guard Verification (MIN_OUTPUT_SIZE: 100 bytes)

```python
# Mandatory before advancing steps
assert os.path.exists(output_path), "Deliverable file does not exist"
assert os.path.getsize(output_path) >= 100, "Deliverable size insufficient (minimum 100 bytes)"
sot.outputs[f"step-{N}"] = output_path
sot.current_step += 1  # Exactly +1 only
```

### SOT Update Protocol (When Using Team)

> Deterministic protocol defining **when** the Team Lead updates the SOT. Eliminates state inconsistency arising from timing ambiguities.

```
Deterministic SOT Update Timings:

1. Immediately after TeamCreate:
   → Record team info in SOT active_team (name, status: "partial", tasks_pending)

2. Upon receiving completion notification from each Teammate (immediately):
   → Verify deliverable file existence (Anti-Skip Guard)
   → Append to SOT active_team.tasks_completed
   → Record summary in SOT active_team.completed_summaries
   → Remove from SOT active_team.tasks_pending

3. Upon completion of all Tasks in step (immediately):
   → SOT active_team.status = "all_completed"
   → Record step deliverable paths in SOT outputs
   → Increment SOT current_step by +1

4. Immediately after TeamDelete:
   → Move entire SOT active_team to completed_teams
   → Remove SOT active_team field

Invariants:
  - Deliverable must exist on disk before updating SOT
  - All Tasks must be completed before incrementing current_step
  - Exactly one active_team can exist at a time (concurrent teams prohibited — SOT single-write principle)
```

> **Relationship between SOT and Task System**: The Task System (`.claude/tasks/`) is the runtime execution layer. The SOT (`state.yaml`) is the sole truth, and the Task System is a coordination tool between agents. Because `active_team` in SOT summarizes and reflects the state of the Task System, reading SOT alone allows reconstructing full team context during session recovery.
>
> **Canonical Schema**: The `workflow.autopilot` structure defined in AGENTS.md §5.1 is canonical. `_context_lib.read_autopilot_state()` supports both schemas (`workflow.autopilot` and top-level `autopilot`), prioritizing the AGENTS.md location. Fallback regex execution is supported in environments without PyYAML.

### Write Permission Rules

| Structure | SOT Write Authority | Other Agents |
|---|---|---|
| Sub-agent Sequential | Orchestrator | Return results to Orchestrator → Orchestrator updates SOT |
| Agent Team | Team Lead | Teammates create deliverable files only → Team Lead merges state into SOT |
| Hook-based | Hook Script | Read-only (for validation). State modification prohibited |

> **Absolute Criterion 1 Priority Exception**: If the rules above create a quality bottleneck (e.g. Team Lead being sole write point causes teammates to work on stale data), the structure may be adjusted under these conditions:
> 1. **Direct Deliverable References**: Teammates are permitted to read peer deliverable files (`.md`, `.json`, etc.) directly without traversing SOT — SOT records only the final merged state
> 2. **Document Rationale**: Explicitly document why the baseline SOT pattern impairs quality in the workflow
> 3. **Preserve SOT**: Even when adjusting structure, never eliminate the SOT file itself — preserve the single write point for final state recording

### Hierarchical Memory Structure

```
Global Memory (SOT — Single File)
  └─ .claude/state.yaml
       ├─ workflow state (current_step, status)
       ├─ step deliverable paths (outputs)
       └─ error/rollback information

Local Memory (Per Agent — Individual Working Context)
  ├─ Sub-agent: Delegated Task + prior step deliverables (read-only)
  ├─ Teammate: Assigned Task + required input files (read-only)
  └─ Hook: Deliverable target for verification (read-only)
```

### SOT Flow in Agent Team

**Baseline Pattern (Default):**

```
Teammate A → Generate deliverable file (output-a.md)
Teammate B → Generate deliverable file (output-b.md)
     ↓ Completion notification (SendMessage)
Team Lead → Merge state into state.yaml (sole write point)
     ↓
Advance to next step
```

**Quality-First Pattern (Applied under Absolute Criterion 1 Priority):**

```
Teammate A → Generate deliverable file (output-a.md)
     ↓ Teammate B references output-a.md directly (cross-validation for quality)
Teammate B → Generate deliverable file (output-b.md reflecting output-a.md)
     ↓ Completion notification (SendMessage)
Team Lead → Merge final state into state.yaml (SOT single write point preserved)
     ↓
Advance to next step
```

> **Application Condition**: Direct referencing of peer deliverables between teammates is permitted only when **quality improvement is demonstrable**, such as cross-validation or feedback loops. Direct references for mere convenience are prohibited. The single write point of the SOT file itself is preserved under all circumstances.
>
> **Caution**: The Claude Code Task List (`~/.claude/tasks/{team-name}/`) is a **task assignment and tracking tool**, not workflow state (SOT). Progress state, deliverable paths, and error data of the workflow must be managed in the SOT file (`state.yaml`).

---

## Task Management System (TaskCreate/TaskUpdate/TaskList)

Claude Code's built-in Task management tools. Used for task assignment, tracking, and coordination in Agent Teams.

> **Relationship with SOT**: The Task List (`~/.claude/tasks/{team-name}/`) is a **task assignment/tracking tool**. Workflow state (current_step, status, outputs) must always be managed in the SOT (`state.yaml`). The Task List never replaces the SOT.

### TaskCreate — Task Creation

```markdown
## Task Design in workflow.md

### 2. (team) Parallel Research
- **Team**: `research-pipeline`
- **Task Definitions**:

  #### Task 1: Web Trend Collection
  - **subject**: "Latest AI Trends Web Research"
  - **description**: "Collect 2024-2025 AI industry trends from the web. Minimum 10 sources required. Save results to research/trends.md"
  - **activeForm**: "Researching AI trends"
  - **owner**: `@researcher`
  - **blocks**: [Task 3]  ← Task 3 depends on this result

  #### Task 2: Existing Data Analysis
  - **subject**: "Internal Data Statistical Analysis"
  - **description**: "Analyze CSV files in data/ directory. Extract key metrics. Save results to research/analysis.md"
  - **activeForm**: "Analyzing data"
  - **owner**: `@data-processor`
  - **blocks**: [Task 3]

  #### Task 3: Comprehensive Insight Derivation
  - **subject**: "Research Synthesis and Insight Derivation"
  - **description**: "Synthesize research/trends.md + research/analysis.md. Derive 5 core insights"
  - **blockedBy**: [Task 1, Task 2]  ← Explicit dependencies
  - **owner**: `@writer`
```

### TaskUpdate — State Management and Dependencies

**State Transition Rules:**

```
pending → in_progress → completed
                     → (blocked → pending)  ← Automatic transition when blockedBy resolved
```

**Team Lead Task Coordination Pattern:**

```markdown
## Orchestrator Role
1. Create all Tasks with TaskCreate + set dependencies (blocks/blockedBy)
2. Assign owners via TaskUpdate → notify teammates to start via SendMessage
3. When teammate completes:
   a. Teammate calls TaskUpdate(status: completed)
   b. Teammate notifies Team Lead via SendMessage
   c. Team Lead updates SOT (state.yaml)
   d. Notify owners of Tasks whose blockedBy dependencies are cleared
4. Advance to next workflow step once all Tasks are completed
```

### TaskList — Progress Monitoring

```markdown
## Orchestrator Inspection Pattern
- Periodically invoke TaskList to assess overall progress
- If blocked Tasks exist, analyze blocking causes
- Verify deliverable quality of completed Tasks before updating SOT
```

---

## Context Memory Integration Patterns

Patterns for leveraging the Context Preservation System during workflow execution.

### Context Strategy by Workflow Phase

```markdown
## Context Specifications in workflow.md

### Phase 1: Research (Context Accumulation Phase)
- **Context Strategy**: Maximum Preservation Mode
- Include all research findings and decision rationales in snapshots
- Stop Hook automatically generates incremental snapshots after each response

### Phase 2: Planning (Context Utilization Phase)
- **Context Strategy**: Selective Reference Mode
- Reference Phase 1 snapshots, reading only sections needed for plan creation
- Record planning state in SOT

### Phase 3: Implementation (Context Distribution Phase)
- **Context Strategy**: Minimal Context per Agent
- Each agent references only its Task description + required input files
- Only Team Lead maintains full context (SOT + snapshots)
```

### Agent Team and RLM Compatibility Pattern

> Teammates in an Agent Team operate in independent sessions and might not be captured in the main session's snapshots. This 2-tier RLM pattern resolves this gap.

```markdown
## 2-Tier RLM (Recursive Language Model) Pattern

### Tier 1 (Baseline): Main Session Automatic Preservation
- Stop hook → latest.md snapshot (automatic)
- SessionEnd/PreCompact → full snapshot + Knowledge Archive (automatic)
- This tier captures the Team Lead (= Orchestrator) session only

### Tier 2 (Active): Team Lead Active Team Context Preservation
- Upon each Teammate completion → record task summary in SOT active_team.completed_summaries
- Upon Team termination → preserve team history in SOT completed_teams
- This tier is executed by Team Lead via SOT writes (complying with Absolute Criterion 2)

### Session Restoration Flow:
1. SessionStart hook → output latest.md pointer
2. Claude reads latest.md → restore main session context
3. Team State section present in latest.md snapshot → determine team task state
4. Read SOT active_team → confirm team progress + each Teammate work summary
5. **Preserving Resumption Protocol** (details below)

### Preserving Resumption Protocol:
> When resuming team tasks after session crash, /clear, or compaction, resume while preserving existing RLM Tier 2 data.

**Step 5a — SOT State Determination:**
- Does SOT `active_team` exist? → Team work was in progress
- Is `active_team.status` set to `"partial"`? → Interrupted team work needs resumption
- If `active_team` is absent or `status: "all_completed"` → No team resumption needed, advance to next workflow step

**Step 5b — Verify Completed Task Files (Anti-Duplicate Guard):**
- For each Task in `tasks_pending`:
  - Check expected output path from workflow definition (workflow.md)
  - Does the output file already exist on disk?
  - Does the file exist and is it ≥ 100 bytes? (Same standard as Anti-Skip Guard)
  - **If present**: Move Task to `tasks_completed`, record `"(restored from disk)"` in `completed_summaries`
  - **If absent**: Truly incomplete Task → target for new Teammate creation

**Step 5c — Team Re-creation (Merge, Not Overwrite):**
- When invoking `TeamCreate`, **mandatory to preserve existing SOT `completed_summaries`**
- Concrete procedure:
  1. Store entire existing `active_team` from SOT into a variable
  2. Create new team (register incomplete Tasks only via TaskCreate)
  3. When updating SOT `active_team`, merge existing `completed_summaries`
  4. Preserve existing `tasks_completed` list (reflecting Step 5b results)
- **Strictly Prohibited**: Initializing `active_team` to empty object and losing `completed_summaries`

**Step 5d — Teammate Spawning and Resumption:**
- Spawn new Teammates only for Tasks confirmed as truly incomplete in Step 5b
- Include context "Resuming work interrupted from previous session" in each Teammate's Task description
- If partially completed deliverables exist, pass their paths as input
```

**Core Takeaway**: While Teammate independent sessions are not directly included in RLM snapshots, SOT `completed_summaries` serves as an "external memory object" that persists team context. This aligns precisely with RLM's "external memory → pointer-based recovery" principle.

### Session Recovery in Long-Running Workflows

```markdown
## Session Recovery Pattern (Workflows Spanning Multiple Sessions)

### Recovery Flow:
1. SessionStart Hook outputs latest.md pointer
2. Claude loads snapshot via Read tool
3. Check current_step in SOT (state.yaml)
4. Verify deliverable file existence for that step
5. Resume workflow from the exact point of interruption

### Design Considerations for Workflows:
- Deliverables from each step **must be saved to files** (in-memory data prohibited)
- Record step deliverable paths in SOT (outputs field)
- Design such that reading SOT alone enables reconstructing the entire state upon recovery
```

---

## Orchestrator Advanced Patterns

### Retry Pattern (Retry with Feedback)

```markdown
### 3. Content Writing (With Retry)
- **Agent**: `@writer`
- **Task**: Content writing based on research
- **Quality Gate**: TaskCompleted Hook (agent type)
- **On Failure**:
  - Attempt 1: Pass Hook feedback to agent → automatic rework
  - Attempt 2: Provide additional context and retry
  - Attempt 3: (human) Request manual intervention
- **Max Attempts**: 3
- **SOT Update**: Record result of each attempt in state.yaml
```

### Escalation Pattern

```markdown
### Orchestrator Escalation Rules:
1. **Automated Resolution**: Retry based on Hook feedback (Attempts 1-2)
2. **Team Lead Intervention**: Swap agent or partition Task (Attempt 3)
3. **Human Escalation**: Request user decision via AskUserQuestion (Attempt 4+)

### SOT Recording on Escalation:
```yaml
workflow:
  current_step: 3
  status: "escalated"
  escalation:
    reason: "Failed quality verification 3 times"
    failed_attempts: 3
    last_feedback: "Source verification insufficient"
```
```

### Conditional Routing Pattern

```markdown
### 4. Conditional Processing
- **Input**: Step 3 deliverable
- **Condition**: Branch based on length/complexity of deliverable
  - **Path A** (Simple): Direct editing with `@quick-editor`
  - **Path B** (Complex): Parallel processing with Agent Team
- **Condition Evaluator**:
  - Hook (command type): File size / structural check (deterministic)
  - Or Hook (prompt type): Complexity evaluation via haiku (semantic)
- **SOT Update**: Record chosen path in state.yaml
```

---

## Error Handling

```yaml
error_handling:
  on_agent_failure:
    action: retry_with_feedback
    max_attempts: 3
    escalation: human  # Escalate to user when exceeding 3 attempts

  on_tool_failure:
    action: notify_and_pause
    message: "Tool execution failed. Manual intervention required."
    sot_update: true  # Record error state in SOT

  on_validation_failure:
    action: retry_or_rollback
    retry_with_feedback: true  # Pass Hook feedback to agent
    rollback_after: 3  # Roll back to previous step after 3 failures

  on_hook_failure:
    action: log_and_continue
    message: "Hook execution failed. Workflow continues."

  on_context_overflow:
    action: save_and_recover
    description: "Apply session recovery pattern with automatic save upon context exhaustion"

  # Agent Team Error Handling
  on_teammate_failure:
    action: escalating_retry
    protocol:
      attempt_1: "Pass feedback via SendMessage → same Teammate reworks"
      attempt_2: "Shutdown Teammate → spawn new Teammate (identical or higher model)"
      attempt_3: "Human escalation (AskUserQuestion)"
    sot_update:
      - "Record failure details in active_team.errors"
      - "Include retry_count and last_feedback"
    partial_output: "Preserve partial deliverables of failed Teammate (referenceable in next attempt)"
```

### Agent Team Error Handling Detailed Flow

```
Teammate failure detected
  ├── Method 1: TaskCompleted hook exit code 2 (quality below threshold)
  ├── Method 2: Error reported via SendMessage
  └── Method 3: Teammate transitions to idle (task incomplete)
      ↓
Team Lead response protocol:
  1. Record failure details in SOT active_team.errors immediately
  2. Attempt 1: Send feedback and rerun instructions to same Teammate via SendMessage
     → On success: Append to SOT active_team.tasks_completed
     → On failure: Proceed to Attempt 2
  3. Attempt 2: Shutdown failed Teammate → spawn new Teammate
     → Consider upgrading model (haiku→sonnet, sonnet→opus)
     → Pass partial deliverable to new Teammate (resume task, not full restart)
  4. Attempt 3: Human escalation (AskUserQuestion)
     → Change SOT status to "escalated"
```

---

## Data Pre/Post-Processing Patterns

Pattern of refining data at the code level before passing it to AI to increase analysis accuracy and deliverable quality.

### Workflow Step Pre-processing Specification

```markdown
### 2. Content Analysis
- **Pre-processing**: `scripts/extract_body.py` — Extract body text from HTML, remove ads and navigation
- **Agent**: `@insight-extractor`
- **Task**: Derive core insights from extracted body text
- **Output**: `insights-list.md`
- **Post-processing**: `scripts/dedup_insights.py` — Remove duplicate insights, merge items with similarity ≥ 0.9
```

### Pre-processing Script Design Criteria

| Criterion | Code-Level Processing | AI Agent Processing |
|---|---|---|
| Data filtering (dates, keywords) | O | X |
| Deduplication (hash, similarity) | O | X |
| Format conversion (HTML → Text) | O | X |
| Relationship computation (graph, statistics) | O | X |
| Semantic analysis, judgment, synthesis | X | O |
| Creative generation, writing | X | O |

### Hook-Based Automated Pre-processing

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/scripts/preprocess_input.py",
          "statusMessage": "Pre-processing data..."
        }]
      }
    ]
  }
}
```

---

## Component Comparison Summary

| Attribute | Sub-agent | Agent Team | Hook | Setup Hook | Slash Command | AskUserQuestion | Task System | Skill (inline) | Skill (forked) | MCP Server |
|---|---|---|---|---|---|---|---|---|---|---|
| **Role** | Expert delegation | Parallel collaboration | Automated verification | Infrastructure verification | User checkpoint | Dynamic inquiry | Task tracking | Knowledge injection | Isolated analysis/transformation | External integration |
| **Session** | Single (delegated) | Multi (independent) | N/A | Pre-session | N/A | N/A | N/A | N/A | Single (isolated) | N/A |
| **Context** | Split from parent | Fully independent | None | None (pre-session) | None | Current session | Shared by team | Injected into session | Split from parent | Injected into session |
| **SOT Relation** | Updated by Orchestrator | Updated by Team Lead only | Read-only | Non-access | Reflects user input | Reflects user input | Separate from SOT | Unrelated | Indirect (pre-processed injection) | Unrelated |
| **Quality Contribution** | Focused expertise | Multi-perspective parallel | Deterministic verification | Silent Failure prevention | Human judgment | Structured gathering | Dependency management | Proven patterns | Isolated analysis | External data |
| **Location** | `.claude/agents/*.md` | Task tool | `settings.json` | `settings.json` (Setup) | `.claude/commands/*.md` | In workflow step | Task tool | `.claude/skills/` | `.claude/skills/` | `.mcp.json` |

---

## Absolute Criteria Compliance Guide

**All Absolute Criteria apply** when implementing workflows.

### Absolute Criterion 1 (Quality): Component Selection Criteria
- Sub-agent vs Agent Team selection is judged **solely by quality**
- Choose paths that elevate quality over reducing step counts
- Allow repeated verification stages if deliverables improve through repetition

### Absolute Criterion 2 (SOT): State Management Principles
- All rules in §State Management (SOT Design) apply
- Task List is a task assignment tool, not the SOT

### Absolute Criterion 3 (CCP): Code Change Protocol
When implementing workflows, **Hook configuration changes, agent prompt updates, MCP configuration edits**, etc., constitute code changes.

| Change Target | CCP Application | Analysis Focus |
|---|---|---|
| Hook JSON addition/edit | Full 3 steps | Conflicts with existing Hooks, exit code impacts, interactions with other events |
| Agent .md edit | Full 3 steps | Ripple effects of tools changes, quality impact of model changes, call relationships |
| MCP configuration change | Full 3 steps | Environment variable dependencies, agent access permissions, security impact |
| Slash Command edit | Step 1 only (Minor) | Verify user interaction paths |
| SOT schema modification | Full 3 steps + User Approval | SOT read code across all agents, Hook verification logic, rollback impacts |

> **Reference**: Absolute Criterion 3 detailed protocol is defined in `AGENTS.md §2 Absolute Criteria 3`.
> All CCP steps are performed while internalizing the **Coding Anchor Points (CAP-1~4)** — Think Before Coding, Simplicity First, Goal-Based Execution, Surgical Changes.

---

## pACS Execution Pattern (predicted Agent Confidence Score)

Pattern where agents structurally self-evaluate the confidence of their deliverables during workflow execution.

> **Reference**: `AGENTS.md §5.4 pACS — predicted Agent Confidence Score`

### Step-by-Step pACS Execution Flow

```
┌─ Step N Execution ─────────────────────────────────────┐
│  @specialist-agent (performs work)                     │
│  → output: analysis/report.md                          │
│                                                        │
│  ── L0: Anti-Skip Guard ──                             │
│  File exists + ≥ 100 bytes ✓                           │
│                                                        │
│  ── L1: Verification Gate ──                           │
│  Self-verification against Verification criteria → PASS│
│  → verification-logs/step-N-verify.md                  │
│                                                        │
│  ── L1.5: pACS Self-Rating ──                          │
│  Pre-mortem Protocol:                                  │
│    Q1: Most uncertain component?                       │
│    Q2: Potential omissions?                            │
│    Q3: Weakest argumentation link?                     │
│  → F: 72, C: 85, L: 78                                 │
│  → pACS = min(72, 85, 78) = 72 → GREEN                 │
│  → pacs-logs/step-N-pacs.md                            │
│  → Update SOT pacs field                               │
│                                                        │
│  [L2: Calibration — Optional]                          │
│  Cross-verification by @verifier (high-risk steps only)│
├─ Proceed to Step N+1 ──────────────────────────────────┤
│  SOT: current_step += 1                                │
└────────────────────────────────────────────────────────┘
```

### Execution Patterns by pACS Action Trigger

```
pACS ≥ 70 (GREEN):
  → Auto-proceed
  → Record in SOT pacs.history.step-N

pACS 50-69 (YELLOW):
  → Proceed with weakness dimension flagged
  → Record weak_dimension in Decision Log
  → Record SOT pacs.pre_mortem_flag

pACS < 50 (RED):
  → Identify weakness dimension
  → Remediate affected component only (not full rework)
  → Re-score (up to 10 retries)
  → If still RED after 10 retries → User escalation
```

### Translation pACS Pattern

```
Upon completion of @translator translation:
  Pre-mortem (Translation Specific):
    Q1: Where is the risk of semantic distortion highest?
    Q2: Any sections potentially omitted?
    Q3: Any sentences with unnatural translationese?
  → Ft: 85, Ct: 90, Nt: 72
  → Translation pACS = min(85, 90, 72) = 72 → GREEN
  → pacs-logs/step-N-translation-pacs.md
```

### SOT pacs Field Schema

```yaml
workflow:
  pacs:
    current_step_score: 72
    dimensions: {F: 72, C: 85, L: 78}
    weak_dimension: "F"
    pre_mortem_flag: "2 unverified data sources"
    history:
      step-1: {score: 85, weak: "C"}
      step-2: {score: 72, weak: "F"}
```

- SOTs lacking the `pacs` field function normally (backward compatible)
- Automatically included in snapshots by Hook `capture_sot()`
- Ignored by `validate_step_output()` (preserving baseline behavior)

---

## Dual-Language Execution Pattern (English-First + Translation)

Pattern where all agents execute in English during workflow runs, and upon step completion, the `@translator` sub-agent generates target language translations.

> **Rationale**: AI achieves highest reasoning performance in English. English-first execution is a direct manifestation of Absolute Criterion 1 (Quality).
> **Reference**: `AGENTS.md §5.2 English-First Execution and Translation Protocol`

### Translation Sub-agent Definition

```markdown
# .claude/agents/translator.md
---
name: translator
description: English-to-target-language translation specialist with glossary-based terminology consistency
model: opus
tools: Read, Write, Glob, Grep
maxTurns: 20
---
```

**Model Selection Rationale**: Translation is a high-difficulty task requiring deep source comprehension, cultural adaptation, and terminology consistency. Classified under §Model Level Selection as a "Core task — directly impacts final quality," dictating the highest tier (opus).

**Sub-agent Selection Rationale**: Among the 5 factors in §Quality Judgment Matrix, "Context Depth" (accumulated terminology), "Deliverable Consistency" (unified tone), and "Information Transfer Loss" (preserving source nuance) favor specialized agents → Sub-agent rather than Agent Team.

### Glossary Management Pattern (Glossary — RLM External Persistent State)

```yaml
# translations/glossary.yaml — Persistent external memory for translation agent
terms:
  "Single Source of Truth": "Single Source of Truth"
  "Anti-Skip Guard": "Anti-Skip Guard"
  "Recursive Language Model": "Recursive Language Model"
  "sub-agent": "Sub-agent"
```

**Architectural Alignment**:
- Glossary is a **local working file** of the translation agent (not SOT)
- Local Memory tier in Hierarchical Memory: `per-agent task context`
- Not managed by Orchestrator — translation agent reads/writes autonomously
- Zero concurrent write risk — translation executes sequentially

### SOT Recording Pattern

```yaml
# state.yaml — Record English original + translated deliverable in outputs
workflow:
  outputs:
    step-1: "research/raw-contents.md"          # English original
    step-1-trans: "research/raw-contents.translated.md"    # Translated deliverable
    step-2: "data/processed.json"               # Translation not required
    step-3: "analysis/report.md"
    step-3-trans: "analysis/report.translated.md"
```

**Anti-Skip Guard Compatibility**: Non-numeric suffix keys (e.g. `step-N-trans`) are automatically skipped by the `.isdigit()` guard in the sorting lambda of `restore_context.py`. `validate_step_output()` validates the English original using `f"step-{step_number}"`. No Hook code modification required.

### Workflow Step Execution Flow

```
┌─ Step N Execution (English) ──────────────────────┐
│  @specialist-agent (English prompt)               │
│  → output: research/raw-contents.md               │
│  → SOT: outputs.step-N = "research/raw-..."       │
│  → Anti-Skip Guard: File exists + ≥100 bytes ✓    │
├─ Translation (Steps with Translation: @translator)┤
│  @translator (opus)                               │
│  ① Read translations/glossary.yaml                │
│  ② Read research/raw-contents.md (English)        │
│  ③ Translate — use established terms, no abbrev.  │
│  ④ Self-review — cross-check source, verify compl.│
│  ⑤ Write translations/glossary.yaml (update terms)│
│  ⑥ Write translated deliverable file              │
│  → SOT: record translation output path            │
│  → Verify translation: file exists + non-empty ✓  │
├─ Proceed to Step N+1 ─────────────────────────────┤
│  SOT: current_step += 1                           │
└───────────────────────────────────────────────────┘
```

### `(team)` Step Translation

```
Team Lead ──────────────────────────────────────────
  ├→ @teammate-a → output-a.md (English working file)
  ├→ @teammate-b → output-b.md (English working file)
  └→ Team Lead:
       1. Merge → merged-output.md (official deliverable)
       2. SOT outputs.step-N = "merged-output.md"
       3. Anti-Skip Guard ✓
       4. @translator → translated deliverable
       5. SOT outputs.step-N-trans = "[translated output path]"
       6. current_step += 1
```

> Individual teammate working files are intermediate outputs not recorded in SOT and therefore are not translated.

### Independent Translation Verification Pattern (Optional)

Selectively applied to steps where quality is especially critical, such as final deliverables:

```
@translator → translated output
  → @translation-verifier (separate sub-agent, model: opus)
    ① Read English original + translation simultaneously
    ② Verify accuracy, completeness, terminology consistency, naturalness
    ③ Pass/Fail + feedback
  → Fail: Feedback to @translator + retranslation request
  → Pass: Record in SOT and proceed
```

This pattern is applied by specifying `Verification: @translation-verifier` in the relevant workflow step during design.

---

## DNA Inheritance Pattern

Pattern where every generated workflow structurally embeds the genome of the parent (AgenticWorkflow).

> **Principle**: "Inheritance is structural, not optional." — Child workflows do not reference parent DNA; they embed it.

### Mandatory Inclusion Items

| Workflow Component | Embedded DNA Form | Verification Method |
|---|---|---|
| `workflow.md` | Contains `## Inherited DNA (Parent Genome)` section | Verify section exists |
| `state.yaml` | Contains `parent_genome` metadata | Verify field exists |
| Sub-agent definitions | Reflect parent quality standards in agent prompts | Quality principles included in Absolute Rules |
| Hook design | Apply P1 hallucination containment pattern to child Hooks | Exit code 2 blocking pattern present |

### Gene Expression by Domain

While expression intensity varies by domain, the genome itself is identical:

```
Research Automation → P1 (Data Refinement) strongly expressed, P2 (Expert Delegation) strongly expressed
SW Development      → CCP (Code Change Protocol) strongly expressed, Safety Hooks strongly expressed
Content Creation    → P2 (Expert Delegation) strongly expressed, Adversarial Review strongly expressed
Data Analysis       → P1 (Data Refinement) strongly expressed, SOT (State Management) strongly expressed
```

> **Reference**: `soul.md §0` — 12 genome components defined, `AGENTS.md §1` — Reason for existence and inheritance mechanism
