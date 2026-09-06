---
name: workflow-generator
description: Automated workflow (workflow.md) generator skill for Claude Code. Use when the user requests "create a workflow", "generate workflow", "design automation pipeline", "define work stream", etc. Clarifies user intent through dialogue and generates workflow.md with a 3-phase structure: Research → Planning → Implementation. Includes implementation design leveraging Claude Code sub-agents, agent teams (swarm), hooks, skills, slash commands, and MCP servers.
---

# Workflow Generator

Skill for designing and generating workflow definition files (workflow.md) for Claude Code.

## Case Identification

**First, identify the user's situation:**

| Condition | Case | Approach |
|---|---|---|
| PDF/Document attached | Case 2 | Document analysis first → confirmation dialogue |
| Idea only mentioned | Case 1 | Requirements gathering via interactive questions |

---

## Case 1: Idea Only

When the user has only a high-level idea.

### Step 1: Identify Purpose

Derive workflow purpose with the following questions:

1. "What deliverable (output) do you want to create?"
2. "What problem does this workflow need to solve?"
3. "What are the primary input sources?"

### Step 2: Define Steps

Derive concrete steps for each Phase:

1. "What information needs to be collected in the Research phase?"
2. "What review/approval is needed in the Planning phase?"
3. "What are the format and quality criteria for the final deliverable?"

### Step 3: Identify Human-in-the-Loop

1. "At which steps is human review/approval required?"
2. "Please distinguish between steps that can be automated and steps that require mandatory human verification."

### Step 4: Implementation Design → Generation

Generate workflow.md upon completing requirements gathering.

---

## Case 2: Document Provided

When the user attaches a concrete explanatory document such as a PDF.

### Step 1: In-Depth Document Analysis

**Always read the document thoroughly first and extract the following:**

```
1. Core purpose: The ultimate goal this workflow aims to achieve
2. Key steps: Processes/steps mentioned in the document
3. I/O definitions: Input/output for each step
4. Technical requirements: Necessary tools, APIs, data sources
5. Constraints: Quality criteria, time limits, dependencies
6. Human-in-the-loop: Points requiring human intervention
```

### Step 2: Share Analysis Results

Present a summary of understood details to the user following document analysis:

```markdown
## Document Analysis Results

**Workflow Purpose**: [Extracted purpose]

**Identified Key Steps**:
1. [Step 1]: [Description]
2. [Step 2]: [Description]
...

**Identified Human-in-the-Loop Checkpoints**:
- [Point 1]: [Reason]

**Technical Implementation Strategy**:
- Sub-agents: [Agent list — delegation within a single session]
- Agent Team: [Team configuration — when parallel collaboration across independent sessions is required]
- Hooks: [Automation triggers — quality gates, formatting, validation]
- Required Tools: [Tool/MCP list]

**Items Requiring Confirmation**:
1. [Question 1]
2. [Question 2]
```

### Step 3: Confirmation Dialogue

Short confirmation questions based on analysis results:

- "Is my understanding accurate?"
- "Is there anything you would like to add or modify?"
- "Could you explain more about [Ambiguous Area]?"

### Step 4: Generation

Generate workflow.md upon completing confirmation.

---

## Absolute Criteria

### Absolute Criterion 1: Quality of the Final Deliverable

> **Speed and token cost are completely ignored.**
> The absolute criterion for all design decisions is the **'quality' of the final deliverable and 'highest-standard qualitative outcomes'**.
> Rather than making things faster by reducing steps, choose the direction that elevates quality even if it means adding steps.
> Even if adding steps for quality improvement increases SOT state complexity, accept it (Absolute Criterion 1 > Absolute Criterion 2).

### Absolute Criterion 2: Single-File SOT + Hierarchical Memory Structure

> **Under the design of a single-file SOT (Single Source of Truth) + hierarchical memory structure, no data inconsistency occurs even when dozens of agents operate simultaneously.**

Design implications of this rule:
- **State Management**: Concentrate all shared state of the workflow in a **single file** (e.g., `state.json`). Do not scatter state across multiple files.
- **Memory Hierarchy**: Clearly separate agent-local memory (task context) from global memory (shared state).
- **Write Permissions**: Only the Orchestrator or a single designated agent has write permission to the SOT file. Other agents access it read-only or pass results to the Orchestrator to merge.
- **Conflict Prevention**: Never design structures where parallel agents (Agent Team/Swarm) modify the same data concurrently.

```
Bad:  Agent A → directly modifies state.json
      Agent B → directly modifies state.json  → data conflict/inconsistency
Good: Agent A → reports results to Orchestrator
      Agent B → reports results to Orchestrator
      Orchestrator → merges and writes to state.json  → single write point, no inconsistency
```

### Absolute Criterion 3: Code Change Protocol (CCP)

> **When writing or modifying code during workflow implementation (Phase 2), you must execute the 3 steps: Understand Intent → Ripple Effect Analysis → Change Plan.**

Workflow components (Sub-agent, Hook, SOT, Slash Command, MCP) depend on each other. Because changes to one component can create ripple effects on other components, always analyze impact scope before modifying code.

- **Step 1 — Understand Intent**: Accurately grasp the purpose of the change and constraints.
- **Step 2 — Ripple Effect Analysis**: Inspect directly dependent modules, call relationships, SOT files, configuration/environment, test code, and documentation.
- **Step 3 — Change Plan**: Design change order, establish modification plans for all affected files, and execute.

> Proportionality Rule: Document revisions during workflow design (Phase 1) are classified as minor changes (Step 1 only); code modifications during implementation (Phase 2) are classified as standard/large-scale changes (full 3 steps).

### Priority Among Absolute Criteria

> **Absolute Criterion 1 (Quality) is highest. Absolute Criterion 2 (SOT) and Absolute Criterion 3 (CCP) are co-equal means to guarantee quality.**
> Designs where final deliverable quality degrades to preserve SOT structure are prohibited.
> Designs where final deliverable quality degrades to comply with CCP are prohibited.

All Absolute Criteria sit above the design principles below. When design principles conflict, Absolute Criteria always take precedence; when Absolute Criteria conflict, follow the order **Absolute Criterion 1 > (Absolute Criterion 2, Absolute Criterion 3)**.

---

## Genome Inheritance Protocol

> **When birthing a child, structurally inherit the parent's entire genome. Birthing a child without inheritance is prohibited.**

AgenticWorkflow is a parent organism that generates child workflows. `workflow-generator` is the production line, and every child born from this line embeds the parent's entire genome as an `Inherited DNA` section.

### Inheritance Mechanism

| Parent Genome (DNA) | Form Embedded in Child |
|---|---|
| 3 Absolute Criteria | `Inherited DNA` section — contextualized per domain |
| SOT Pattern | Configuration's `state.yaml` + single write point |
| 3-Phase Structure | Research → Planning → Implementation workflow structure |
| 4-Layer QA | `Verification` + `pACS` fields |
| P1 Containment | Hook-based deterministic validation |
| Safety Hook | PreToolUse blocking pattern |
| Adversarial Review | `Review:` field — `@reviewer` / `@fact-checker` |
| Decision Log | `autopilot-logs/` pattern |
| Context Preservation | Cross-session memory preservation pattern |

### Expression vs Inheritance

Just as cells sharing identical genomes perform different functions, child systems express differently based on their domain on top of the same DNA. For example, in a research automation system, Research phase genes are strongly expressed; in software development automation, CCP (Code Change Protocol) genes are strongly expressed. Even though purposes differ, the genome is identical.

### Obligations upon Generation

1. Include the `Inherited DNA (Parent Genome)` section in every workflow.md (see template)
2. Include `parent_genome` metadata in every state.yaml (see SOT template)
3. Child agent definitions reflect parent quality standards (Absolute Criterion 1)

Details: `soul.md §0`, `AGENTS.md §1 Reason for Existence`.

---

## Design Principles (Mandatory Compliance)

Principles that must be applied when designing workflows. However, all principles are subordinate to **all Absolute Criteria (1. Quality First, 2. Single-File SOT, 3. Code Change Protocol)**.

### P1. Data Refinement for Accuracy

Passing large data directly to AI introduces noise and **degrades accuracy**. Refine data so agents can focus on the core.

- Specify **data pre-processing** at each step: Remove noise via Python scripts before handing off to AI → **improve analysis accuracy**
- Specify **post-processing** at each step: Refine deliverables before passing to the next step → **improve next-step quality**
- Pre-compute data relationships at the **code level** where possible → **AI focuses on judgment and analysis**

```
Bad:  "Pass entire collected webpage HTML to agent" → analysis quality drops from noise
Good: "Extract body text with Python script → pass only essential text to agent" → analysis accuracy increases
```

### P2. Expertise-Based Delegation Structure

Maximize quality by delegating each task to the **specialized agent best suited to perform it**. The Orchestrator coordinates overall quality, and specialized agents focus deeply on their respective domains.

```
Orchestrator (quality coordination and overall flow management)
  ├→ Sub-agent A: Specialized research (optimized for the domain)
  ├→ Sub-agent B: In-depth analysis (focused only on analysis)
  └→ Skill C: Proven pattern application (quality-guaranteed reusable logic)
```

### P3. Image/Resource Accuracy

In steps requiring image resources, specify **accurate download paths**. Placeholders must also be fully extracted; omissions are prohibited.

### P4. Question Design Rules

When asking the user questions:
- Maximum 4 questions
- Offer **about 3 options** per question (sub-agent/skill/recommended options)
- Proceed without questions if there are no ambiguities

---

## Basic Workflow Structure

Every workflow consists of 3 phases:

1. **Research**: Information gathering and analysis
2. **Planning**: Plan formulation and structuring
3. **Implementation**: Actual execution and deliverable generation

**Mandatory items to include in each step:**
- Task to perform (Task)
- Responsible agent (@agent)
- Data pre-processing (Pre-processing) — noise removal for improved accuracy (P1)
- Deliverable (Output)
- Adversarial Review (Review) — `@reviewer`, `@fact-checker`, or `none` (AGENTS.md §5.5)
- Translation (Translation) — `@translator` or `none` (applicable to text deliverables only)
- Post-processing (Post-processing) — refinement to ensure next step quality (P1)

## Claude Code Component Mapping

| Workflow Element | Claude Code Implementation | Selection Criteria |
|---|---|---|
| Single task delegation | Sub-agent (`.claude/agents/*.md`) | Focus deeply on specialty, maximize quality |
| Large-scale parallel collaboration | Agent Team/Swarm (`TeamCreate`) | Perform independent tasks across multiple sessions concurrently |
| Human intervention step | Slash command (`.claude/commands/`) | Review/approval/selection user interactions |
| Automation validation/trigger | Hooks (`settings.json`) | Formatting, quality gates, security validation |
| Reusable logic | Skill (`.claude/skills/`) | Domain knowledge, recurring patterns |
| External integration | MCP Server | API, DB, external service integration |

### Sub-agent vs Agent Team Selection Criteria

> **The sole criterion for selection is 'which structure achieves the highest final deliverable quality.'**
> Do not choose Agent Team simply because parallel processing is fast.
> Do not choose Sub-agent simply because it uses fewer tokens.

| Situation | Selection | Quality Rationale |
|---|---|---|
| Highest quality achieved by a single specialist maintaining deep context | **Sub-agent** | Maintains consistent depth within a single context |
| Highest quality achieved by multiple specialists addressing distinct domains | **Agent Team** | Each specialist focuses 100% on their respective domain in independent contexts |
| Multi-perspective analysis/cross-validation improves quality | **Agent Team** | Combining independent perspectives produces richer results than a single agent |
| Accurate context transfer across sequential steps is core to quality | **Sub-agent sequential calls** | Accurately forwards step deliverables to subsequent steps |

> **Absolute Criterion 2 Mandatory Companion**: When selecting Agent Team, always define SOT design together — SOT file path, single write permission for Team Lead, and teammate deliverable creation rules. Agent Teams without SOT design are strictly prohibited in principle. Details: `references/claude-code-patterns.md` state management section.
>
> **Absolute Criterion 1 Priority Exception**: Only in cases of completely independent parallel work (where agents have no shared state and do not reference each other's deliverables) and where it is explicitly demonstrated that SOT design does not contribute to quality, lightweight SOT may be permitted. This determination must be documented during workflow design.

## Reference Documents

- Workflow template: `references/workflow-template.md`
- Claude Code implementation patterns (Sub-agents, Teams, Hooks): `references/claude-code-patterns.md`
  - Anti-Skip Guard Protocol: §Anti-Skip Execution Protocol (Deliverable verification — 100 bytes minimum size)
  - Autopilot Execution Checklist: §Autopilot + Agent Team Integration Checklist
  - SOT State Management: §SOT State Management Protocol
- Document analysis guide (Case 2): `references/document-analysis-guide.md`
- Context injection patterns (Sub-agent/Team input transfer): `references/context-injection-patterns.md`
- SOT template (state.yaml bootstrap): `references/state.yaml.example`
- Autopilot Decision Log template: `references/autopilot-decision-template.md`

## Final Generation Procedure

1. Identify case (document presence)
2. Case 1: Gather requirements via dialogue / Case 2: Analyze document → confirmation dialogue
3. **Genome Inheritance**: Include the `Inherited DNA (Parent Genome)` section in workflow.md (Inheritance Protocol — see `references/workflow-template.md`). Use the date of workflow generation (YYYY-MM-DD) for `parent_genome.version`. When contextualizing CCP, include Coding Anchor Points (CAP-1~4).
4. Define tasks in 3-phase structure applying Design Principles P1~P4
   - Evaluate Domain Knowledge Structure (DKS) necessity: Workflows requiring domain-specific reasoning such as medical, legal, or competitive analysis include a DKS construction step in the Research phase. Workflows using DKS include `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir . --check-output --step N` in Post-processing of relevant steps. Details: `AGENTS.md §5.3 DKS`
5. Specify data pre-processing/post-processing for each step (P1)
6. Mark Human-in-the-Loop checkpoints
7. **Define `Verification` field for each step** (AGENTS.md §5.3 — Mandatory):
   - Place `Verification` field **before** `Task` field (agents recognize it first)
   - **`Verification` is mandatory for every agent execution step** — no distinction between Research/Planning/Implementation (Research steps also require "completeness" verification: e.g. "All 5 competitors analyzed")
   - `(human)` steps are the only exception — human is the verifier, so no `Verification` field needed
   - Write each criterion as a **concrete statement verifiable as true/false by a third party**
   - Include a combination of the 5 criteria types:
     - **Structural completeness**: Internal deliverable structure → "All 5 sections included", "Minimum 3 sub-items per item"
     - **Functional goals**: Task objective achievement → "Pricing data from 3+ competitors", "All API endpoints implemented"
     - **Data integrity**: Data accuracy → "All URLs valid, no placeholders", "Sources specified for numerical data"
     - **Pipeline connectivity**: Next-step input compatibility → "Includes fields required by Step N", "Output format matches Step N+1 input"
     - **Cross-step traceability**: Logical derivation from previous steps → "80%+ of analytical claims traceable to sources with [trace:step-N] markers"
   - **Tip**: When describing criteria, utilizing `(source: Step N)` annotations enables Verification criteria themselves to explicitly reference previous steps, automating upstream impact analysis during diagnosis. E.g.: "Competitor analysis data reflects Step 2 research findings (source: Step 2)"
8. Set **Review field** for each step (AGENTS.md §5.5 — Optional):
   - Research/analysis deliverables (requiring fact checking) → `@fact-checker`
   - Code/technical deliverables (requiring logic/completeness verification) → `@reviewer`
   - High-risk steps (both required) → `@reviewer + @fact-checker`
   - Low-risk or intermediate steps → `none` (up to L1.5 only)
   - **Execution order**: Review PASS → Translation (prohibit translation in Review FAIL state)
9. Set **Translation field** for each step — `@translator` for text deliverables (`.md`, `.txt`), `none` for code/data/configuration
10. Add Claude Code implementation design (Sub-agents, Teams, Hooks, Commands, Skills, MCP)
   - **Select Context Injection pattern** (for each agent step):
     - Input < 50KB → Pattern A (Full Delegation — pass file path)
     - Input 50-200KB + partially relevant → Pattern B (Filtered — refine via pre-processing script before passing)
     - Input > 200KB or partitioning required → Pattern C (Recursive Decomposition — chunk parallel processing)
     - Absolute Criterion 1 priority: Select Pattern B if filtering improves quality, regardless of size
     - Details: `references/context-injection-patterns.md`
   - **SOT design mandatory when using Agent Team** (Absolute Criterion 2):
     - SOT file location (`.claude/state.yaml`), single write permission for Team Lead, teammate deliverable rules
     - `active_team` schema: name, status, tasks_completed/pending, completed_summaries
     - 4 SOT update timings: Immediately after TeamCreate → upon teammate completion → upon overall completion → immediately after TeamDelete
     - Details: `references/workflow-template.md §SOT Schema when using Agent Team`
   - **Checkpoint Pattern**: Evaluate expected turns for each Task and select `standard` (≤ 10 turns) or `dense` (> 10 turns). Details: `references/claude-code-patterns.md §DCP`
11. **Apply English-First Execution Principle** (AGENTS.md §5.2):
   - Write all agent Task descriptions and prompts in **English** (maximize AI performance — Absolute Criterion 1)
   - User dialogue (workflow design) in user's language, agent execution in English
   - `@translator` sub-agent handles translation into target language (specified via Translation field)
12. Generate workflow.md file
13. **(Optional) Distill Verification**: Inspection for maximizing quality of generated workflow
   - "Does this step contribute to final quality?" — Remove only steps unrelated to quality
   - "Is quality more stable if this step is automated?" — Discover automation opportunities
   - "Are there steps that need to be added to elevate quality?" — Add verification/enhancement steps
   - "Does each `Verification` criterion include **pipeline connectivity**?" — Verify data flow between steps
   - **DNA Inheritance P1 Verification**: Run `python3 .claude/hooks/scripts/validate_workflow.py --workflow-path ./workflow.md` → verify W1-W8 pass
   - Reference: `prompt/distill-partner.md`

## Autopilot Mode Support

Include the Autopilot Mode field in the generated workflow.md.

- Add `- **Autopilot**: [disabled|enabled]` in Overview section (default: disabled)
- Set to `enabled` if user requests "run automatically", "uninterrupted execution", etc.
- Do not alter the design of `(human)` steps themselves — Autopilot is an execution mode, not a design change
- Optional: Specify default action on auto-approval via `Autopilot Default` field in each `(human)` step

## pACS Support

Include the pACS (self-confidence evaluation) field in the generated workflow.md.

- Add `- **pACS**: [enabled|disabled]` in Overview section (default: enabled, AGENTS.md §5.4)
- pACS operates independently of Autopilot mode — applies in manual execution as well
- `(human)` steps do not require pACS as human is the evaluator (same principle as Verification)
- Set to `disabled` if user explicitly requests "without pACS", etc.
