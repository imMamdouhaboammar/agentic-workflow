# Document Analysis Guide

Guide for analyzing workflow description documents (PDF, etc.) provided by the user.

## Analysis Checklist

Systematically extract the following items while reading the document:

### 1. Purpose

```
- What is the ultimate goal of this workflow?
- What problem is it attempting to solve?
- What are the success criteria?
```

### 2. Process Steps

```
- Explicitly mentioned steps in the document
- Order and dependencies between steps
- Purpose and deliverable of each step
```

**Step Extraction Patterns:**
- Numbered lists (1, 2, 3...)
- Sequence keywords ("First", "Next", "After that")
- Section headings
- Flowcharts/diagrams

### 3. I/O Definitions (Input/Output)

```
- Entire workflow input: What is the trigger?
- Entire workflow output: What is the final deliverable?
- Inputs/outputs per step: Intermediate deliverables
```

### 4. Technical Requirements

```
- Required tools/software
- External API/service integrations
- Data sources (RSS, DB, API, etc.)
- File format requirements
- Data volume estimation (throughput influences pattern selection)
- Need for parallel processing (rationale for Agent Team)
```

**Data Volume → Pattern Selection Guide:**

| Data Scale | Recommended Pattern | Rationale |
|---|---|---|
| Small scale (single doc/API) | Sub-agent sequential | Maintaining context with a single specialist is efficient |
| Medium scale (multiple sources, independent) | Agent Team parallel | Specialized agents per independent source improve quality |
| Large scale (100+ items) | Pre-processing + Agent | P1 principle: Code refines, AI judges |

> **Quality Criterion (Absolute Criterion 1)**: Do not use Agent Team simply because "there is a lot of data"; determine whether "having independent specialists deeply process each source increases quality."

### 5. Constraints & Quality Criteria

```
- Quality criteria/standards
- Time limits/SLAs
- Dependencies/prerequisites
- Exception handling rules
```

**Quality Criteria Extraction Guide:**

Systematically extract quality-related mentions from the document. The extracted criteria serve as the judgment basis for Hook-based automated verification or (human) review steps.

| Quality Type | Target to Extract | Claude Code Mapping |
|---|---|---|
| Quantitative criteria | "Accuracy 95% or higher", "Minimum 10 sources" | Hook (command type) — verifiable via code |
| Qualitative criteria | "Professional tone", "Logical flow" | Hook (prompt/agent type) — evaluated by AI |
| Format criteria | "Markdown format", "Within 3,000 words" | Hook (command type) — deterministic verification |
| Domain criteria | "Compliance with academic citation rules" | Skill injection + Hook verification |

> **Application of Absolute Criterion 1**: If quality criteria are not explicitly stated, use "highest quality standard" as default. Never interpret in a direction that lowers quality standards.

### 6. Human Checkpoints (Human-in-the-Loop)

```
- Explicit approval/review steps
- Decision-making points
- Quality inspection steps
- Exception handling
```

**Identification Keywords:**
- "review", "approval", "verification", "selection"
- "review", "approve", "verify", "select"
- "manager", "admin", "human"

**Claude Code Feature Mapping:**

| Intervention Type | Claude Code Feature | Workflow Notation |
|---|---|---|
| Deliverable review/approval | Slash Command (`/review-*`) | `(human) Review and approval` |
| Option selection (predefined list) | Slash Command (`/select-*`) | `(human) Option selection` |
| Requirements gathering (dynamic questions) | AskUserQuestion | Invoked within workflow step |
| Automated quality verification (no human intervention needed) | Hook (TaskCompleted, exit 2) | `(hook) Automated quality verification` |
| Escalation (after automated failure) | AskUserQuestion | Orchestrator escalation |

> **Judgment Criteria**: "Can this intervention be predefined?" → Slash Command. "Must questions be asked dynamically?" → AskUserQuestion. "Is deterministic verification possible?" → Hook.

## 3-Stage Structure Mapping

Place document content across Research → Planning → Implementation:

| Phase | Applicable Activity Type |
|---|---|
| **Research** | Information gathering, data collection, source exploration, current state assessment |
| **Planning** | Analysis, structuring, design, drafting, plan formulation |
| **Implementation** | Execution, generation, deployment, final deliverable production |

## Handling Ambiguous Areas

Record unclear sections from the document:

```markdown
**Items Requiring Clarification:**
1. Concrete execution method for [Step X] is unclear
2. Source/format for [Input Y] is undecided
3. Quality criteria for [Deliverable Z] are unspecified
4. Whether additional Human-in-the-Loop points are required
```

## Analysis Output Format

```markdown
## 📋 Document Analysis Results

### Workflow Overview
- **Purpose**: [One-line summary]
- **Input**: [Trigger/Source]
- **Output**: [Final deliverable]

### Identified Steps (Total N)

**Research Phase**
1. [Step Name]: [Description] → Deliverable: [Filename]
2. ...

**Planning Phase**
3. [Step Name]: [Description] → Deliverable: [Filename]
4. ...

**Implementation Phase**
5. [Step Name]: [Description] → Deliverable: [Filename]

### Human-in-the-Loop Checkpoints
- After Step [N]: [Review details]
- After Step [M]: [Approval details]

### Technical Implementation Strategy

| Component | Details | Selection Rationale |
|---|---|---|
| Sub-agents | [Agent list + role, model, tools of each agent] | [Why Sub-agent is suitable for this task] |
| Agent Team | [Team structure + parallel configuration + join conditions] | [Why parallel processing increases quality] |
| Hooks | [Event + type + verification criteria] | [Why automated verification is required] |
| Slash Commands | [Command + purpose + parameters] | [What user judgment is needed] |
| AskUserQuestion | [Steps requiring dynamic questions] | [Why predefined commands are insufficient] |
| Task Management | [Task structure + dependencies] | [Mandatory when using Agent Team] |
| Skills | [Required skill list] | [What domain knowledge is required] |
| MCP Servers | [External integrated services] | [What external data/capabilities are needed] |
| Pre/Post-processing | [Preprocessing/postprocessing scripts] | [P1 Principle: Code refines, AI judges] |
| Translation | [Text deliverable: `@translator` / Code and data: `none`] | [English-First execution — AGENTS.md §5.2] |

> **Reference**: Refer to `references/claude-code-patterns.md` for detailed implementation patterns of each component.

### ❓ Items Requiring Confirmation
1. [Question 1]
2. [Question 2]

---
Please review the details above. Let me know if anything needs correction or addition.
```

## Confirmation Dialogue Guide

Brief, essential questions after sharing analysis results:

**Mandatory Confirmation:**
- "Is my understanding of the step breakdown accurate?"
- "Are these Human-in-the-Loop checkpoints sufficient?"

**Optional Confirmation (only when ambiguous areas exist):**
- "Could you clarify the specific method for [Specific Step]?"
- "Where should [Specific Input] be retrieved from?"

**Avoid Excessive Questions:**
- Do not re-verify details already clear in the document
- Do not ask more than 3 questions at once

> **P4 Rule (SKILL.md §Design Principle P4)**: Maximum 4 questions, ~3 options per question. The same rule applies when using the AskUserQuestion tool.

## Absolute Criteria Compliance Checklist

After completing document analysis, verify the following:

- [ ] **Absolute Criterion 1 (Quality)**: Are workflow steps sufficient to maximize quality? Are there any unnecessary shortcuts?
- [ ] **Absolute Criterion 2 (SOT)**: Is shared state managed in a single file? Is write permission held by a single point?
- [ ] **Absolute Criterion 3 (CCP)**: Did you analyze ripple effects of Hook/Agent/MCP changes during implementation?

> **Reference**: Details of Absolute Criteria are defined in `AGENTS.md §2 Absolute Criteria`.
