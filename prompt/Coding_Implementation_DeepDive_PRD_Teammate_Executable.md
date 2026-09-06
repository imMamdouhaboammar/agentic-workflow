# Coding & Implementation Deep-Dive Framework
## Targeted In-Depth Research on Core Coding Technologies — Local Agentic Workflow Harness

---

> **Purpose of this Document**: Conduct an independent, in-depth investigation into **how to implement a local agentic workflow harness at the code level**. Alongside primary PRD research, technology deep dives, and other specialized investigations, this produces research deliverables to be integrated into the final PRD.

> **Implementation Direction**: Implement the workflow defined in `/prompt/workflow.md` by appropriately combining Claude Code's Task Management System, fork, agent-teams, Agent Swarm, orchestrator agent, sub agents, skills, hooks, commands, task verification, etc.

---

## Initial Setup (User Input)

**Research Target**: [e.g., "workflow.md-based agentic workflow implementation patterns"]
**Topic**: [e.g., "orchestrator-sub agent patterns and task verification implementation"]
**Core Coding Areas**: [e.g., "workflow scripts, agent orchestration, skill/hook implementation, verification logic, state management"]

### Reference Context (Attach results from other deep dives if available)

**Primary PRD Research Results** (if available): [Attach if available]
**Technology Deep Dive Results** (if available): [Attach if available]

> Even without reference context, this document can be executed independently. If other deep dive results exist, the research scope can be defined with greater precision.

---

## Fork-Based Sessions Branch Strategy

This framework leverages the `/fork` feature to **explore multiple coding implementation paths simultaneously**.

### Strategy Overview

```
Initial Setup
  ↓
[PHASE 1: Coding Deep Dive - 10 Branches in Parallel]
  ├─ /fork Branch 1.1: Workflow Script Architect (Declarative Workflow)
  ├─ /fork Branch 1.2: Workflow Script Architect (Procedural Workflow)
  ├─ /fork Branch 2.1: Agent Orchestration Coder (Centralized Orchestration)
  ├─ /fork Branch 2.2: Agent Orchestration Coder (Distributed Orchestration)
  ├─ /fork Branch 3.1: Skills & Hooks Developer (General-Purpose Skill Library)
  ├─ /fork Branch 3.2: Skills & Hooks Developer (Workflow-Specific Skills)
  ├─ /fork Branch 4.1: Verification & Quality Coder (Strict Verification)
  ├─ /fork Branch 4.2: Verification & Quality Coder (Selective Verification)
  ├─ /fork Branch 5.1: State & Recovery Coder (File-Based State Management)
  └─ /fork Branch 5.2: State & Recovery Coder (Structured State Machine)
  ↓
[PHASE 2: Coding Discussion]
  ├─ /fork Branch 2.A: Workflow Expressiveness Priority Discussion
  ├─ /fork Branch 2.B: Implementation Stability Priority Discussion
  ├─ /fork Branch 2.C: Implementation Speed Priority Discussion
  └─ /fork Branch 2.D: Maintainability/Extensibility Priority Discussion
  ↓
[PHASE 3: Implementation Scenarios]
  ├─ /fork Branch 3.A: Full-Defensive (Handle All Edge Cases)
  ├─ /fork Branch 3.B: Balanced (Defend Core Only)
  └─ /fork Branch 3.C: Rapid-Prototype (Minimal Implementation, Rapid Verification)
  ↓
[PHASE 4: Integration of Research Findings]
  → Coding Deep Dive Comprehensive Report
  → Implementation Pattern Reference
  → Findings Requiring Further Investigation
```

### Purpose of Using Branches

**Branches in Investigation Phase**
- Verify that even for the same component, complexity and stability vary significantly depending on the implementation approach
- Example: "Orchestrator controls all flow" vs "Agents collaborate autonomously" → identical functionality, yet vastly different code structures
- Concretely compare pros and cons of each approach using pseudocode or structural examples

**Branches in Discussion Phase**
- Verify how implementation patterns diverge based on which coding philosophy is prioritized
- Analyze code complexity vs stability vs maintainability trade-offs for each path

**Branches in Scenario Phase**
- Simultaneously evaluate 3 implementation paths based on defense levels
- Compare total code footprint, runtime stability, and maintenance overhead across scenarios

---

## Constraints

**Investigation Phase Constraints**
- Every implementation pattern **must include pseudocode or concrete structural examples**
- Must be grounded in Claude Code's actual capabilities — do not assume non-existent APIs or features
- **Parking Lot Rule**: Discoveries exceeding the current branch scope must be logged in the parking lot

**Discussion Phase Constraints**
- Focus discussions on **comparing implementation patterns** — "Is this pattern suitable for this component?"
- Explicitly detail **concrete code-level differences** in every comparison (abstract claims like "better" are prohibited)

**Scenario Phase Constraints**
- Each scenario must include **implementation configurations across all areas (scripts, orchestration, skills/hooks, verification, state management)** required for workflow execution
- Must output an **implementation complexity analysis** for each scenario

---

## Success Points

### Phase 1 (Coding Investigation) Success Points

✅ **Are implementation techniques concrete?**
- [ ] Does each implementation pattern include **pseudocode or structural examples**?
- [ ] Has the actual structure of workflow.md been designed?
- [ ] Is the orchestrator-sub agent role allocation concrete?

✅ **Is the implementation complexity analysis realistic?**
- [ ] Is the complexity of each implementation pattern analyzed in detail?
- [ ] Are items that are easier vs harder than expected clearly differentiated?

### Phase 2 (Discussion) Success Points

✅ **Are trade-offs between implementation patterns clear?**
- [ ] Captured at least 3 distinct conflicts between implementation approaches
- [ ] Explicit code-level differences articulated for each conflict

### Phase 3 (Scenarios) Success Points

✅ **Are the 3 implementation scenarios realistically differentiated?**
- [ ] Do scenarios differ in total implementation scope, stability, and maintenance burden?
- [ ] Are concrete implementation configurations specified for each scenario?

### Phase 4 (Integration) Success Points

✅ **Does the comprehensive report serve as a meaningful reference for drafting the final PRD?**
- [ ] Is the implementation pattern reference directly usable for actual development?
- [ ] Are technical limitations and possibilities discovered during implementation clearly organized?
- [ ] Are discoveries requiring further investigation documented?

---

## Final Review Checklist

```
Investigation Phase:
[ ] Does each Branch present concrete implementation techniques with pseudocode/structural examples?
[ ] Are pseudocode or structural examples included?
[ ] Has the actual structure of workflow.md been designed?

Discussion Phase:
[ ] Are trade-offs between at least 3 implementation patterns specified?
[ ] Are concrete code-level differences compared?

Scenario Phase:
[ ] Do the 3 scenarios present distinct implementation configurations?
[ ] Are total implementation scope, stability, and maintenance burden compared across scenarios?

Final:
[ ] Is the comprehensive report meaningful when read alongside other deep dive findings?
[ ] Is the implementation pattern reference directly usable for actual development?
[ ] Are new technical limitations and possibilities discovered during research organized?
```

---

## PHASE 1: Coding Deep Dive (Fork-Based Parallel Exploration)

### Parallel Execution of 2 Branches per Team

Each Teammate simultaneously explores **two conflicting implementation approaches** within their coding domain.
The subject of exploration is not abstract theory, but **how to concretely implement the workflow**.

---

#### **Workflow Script Architect - 2 Branches**

**Branch 1.1: Declarative Workflow**

```
You are an expert designing workflow.md by specifying only "what to do" and delegating "how" to the orchestrator.

Perspective: "The workflow declares intent; the agent determines execution method."

Analysis Target: [Research Topic]

Analysis Content:

1. workflow.md Structural Design
   - Task definition format: [How is each component expressed as a task?]
   - Task dependency representation: [How are precedence and parallelizability specified?]
   - Exit criteria representation: [How are success criteria for each task specified?]
   - Structural example: [Write an actual sample workflow.md spanning 3 tasks]

2. Orchestrator Agent Role Design
   - Judgments orchestrator must make by reading workflow.md: [Execution order, agent assignment, resource allocation]
   - Instructions needed by orchestrator: [What content is required in CLAUDE.md?]
   - Orchestrator autonomous judgment scope: [What is delegated and what is constrained?]

3. Implementation Complexity Analysis
   - Declarative workflow.md authoring difficulty: [Low / Medium / High]
   - Orchestrator configuration complexity: [Low / Medium / High]
   - Likelihood of unexpected behavior: [Low / Medium / High]
   - Debugging difficulty: [Low / Medium / High]

Conclusion:
- Strengths of declarative approach: [Concrete]
- Limitations of declarative approach: [Where is it insufficient?]
- Essential implementation elements in this approach: [Top 3]

🅿️ Parking Lot: [Discrepancies with technology deep dive conclusions, out-of-scope discoveries]
```

**Branch 1.2: Procedural Workflow**

```
You are an expert designing workflow.md by specifying not just "what" but "how, in what order, and using which agent".

Perspective: "The more explicit the workflow, the more predictable the execution."

Analysis Content:

1. workflow.md Structural Design
   - Task definition format: [Explicit execution steps, assigned agents, input/output formats]
   - Flow control between tasks: [How conditional branching, loops, wait conditions are expressed]
   - Agent assignment rules: [Which tasks assign to orchestrator / sub-agent / Agent Swarm?]
   - Structural example: [Write an actual sample workflow.md spanning 3 tasks]

2. Precision of Execution Control
   - Fork and merge points: [How specified in workflow.md?]
   - agent-teams configuration instructions: [How team structure, roles, deliverable formats are specified?]
   - Task verification criteria: [How verification methods for each task are included in workflow.md?]

3. Implementation Complexity Analysis
   - Procedural workflow.md authoring difficulty: [Low / Medium / High]
   - workflow.md maintenance overhead: [Change footprint when modifying workflow]
   - Execution predictability: [High]
   - Debugging difficulty: [Low / Medium / High]

Conclusion:
- Strengths of procedural approach: [Concrete]
- Limitations of procedural approach: [Does workflow.md become overly verbose? Maintenance issues?]
- Essential implementation elements in this approach: [Top 3]

🅿️ Parking Lot: [Discrepancies, out-of-scope discoveries]
```

**Final Synthesis (Branch 1.1 vs 1.2 Comparison)**

```
Implementation Differences:
- Declarative: [Short workflow.md, relies on orchestrator autonomous judgment, harder to predict]
- Procedural: [Long workflow.md, precise control, higher maintenance overhead]

Suitable Approach per Component:
- [Component A]: Which is more suitable, declarative or procedural? [Reason]
- [Component B]: ...
- Is a hybrid approach viable?: [Procedural for core tasks, declarative for auxiliary tasks, etc.]
```

---

#### **Agent Orchestration Coder - 2 Branches**

**Branch 2.1: Centralized Orchestration**

```
You are an expert in patterns where the orchestrator agent controls all flow and delegates individual tasks to sub-agents.

Perspective: "A single orchestrator oversees the big picture and directs execution."

Analysis Content:

1. Orchestrator-Sub Agent Pattern Design
   - Orchestrator role: [Interpret workflow.md, distribute tasks, collect results, judge quality]
   - Sub-agent role: [Execute single task, return results]
   - Delegation criteria: [Which tasks are delegated and which are handled directly?]

2. Task Management System Utilization
   - Task queue management: [How implemented?]
   - Task state tracking: [pending / running / completed / failed]
   - Task dependency resolution: [Verification method for preceding task completion]

3. Leveraging fork and agent-teams
   - When to use fork: [Tasks requiring parallel exploration]
   - When to configure agent-teams: [Tasks requiring multi-perspective analysis]
   - Result merge methodology: [How orchestrator synthesizes findings]

4. Implementation Complexity Analysis
   - Complexity of orchestrator setup itself: [__]
   - Management overhead as sub-agent count increases: [__]
   - Single point of failure (orchestrator failure) mitigation: [__]

Conclusion:
- Strengths of centralized approach: [Predictable, easy to debug]
- Limitations of centralized approach: [Orchestrator overload, single point of failure]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 2.2: Distributed Orchestration**

```
You are an expert in implementing autonomous agent collaboration via Agent Swarm patterns.

Perspective: "Agents understand their respective roles and collaborate autonomously."

Analysis Content:

1. Agent Swarm Pattern Design
   - Autonomous judgment scope for each agent: [To what extent?]
   - Inter-agent communication mechanism: [Files? Shared context? Messages?]
   - Consensus / conflict resolution mechanism: [Who makes the final call?]

2. Role-Based Agent Specialization
   - Specialized agent types: [Research agent, coding agent, verification agent, etc.]
   - Skill set for each agent: [Which skills are equipped?]
   - Inter-agent handoff: [Patterns]

3. Control of Autonomous Collaboration
   - Preventing divergence: [Constraints preventing agents from losing direction]
   - Progress monitoring: [How overall progress is tracked]
   - Intervention points: [When must the user intervene?]

4. Implementation Complexity Analysis
   - Complexity of Swarm setup itself: [__]
   - Communication complexity as agent count grows: [__]
   - Likelihood of unpredictable behavior: [__]

Conclusion:
- Strengths of distributed orchestration: [Scalability, flexibility]
- Limitations of distributed orchestration: [Hard to predict, complex debugging]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 2.1 vs 2.2 Comparison)**

```
Orchestration Pattern Selection:
- Centralized: [Simple workflows, emphasizes predictability]
- Distributed: [Complex workflows, emphasizes scalability]

Suitable Pattern per Component:
- [Component A]: Centralized vs Distributed? [Reason]
- Is a hybrid approach viable?: [Centralized for core flow, distributed for exploratory tasks, etc.]
```

---

#### **Skills & Hooks Developer - 2 Branches**

**Branch 3.1: General-Purpose Skills (General-purpose skill library)**

```
You are an expert designing reusable general-purpose skills and hooks applied across diverse workflows.

Perspective: "Build it well once, and reuse across multiple workflows."

Analysis Content:

1. Skill Design
   - General-purpose skills inventory: [Which skills are commonly needed across workflows?]
   - Interface of each skill: [Input, output, invocation method]
   - Skill composition patterns: [Output of skill A piped into input of skill B]
   - Implementation example: [Structure and usage examples for 2-3 general skills]

2. Hooks Design
   - General-purpose hooks inventory: [Which events should commonly trigger responses?]
   - Hook-to-skill linkage: [Patterns where hooks trigger skills]
   - Hook chaining: [Cases where one hook triggers another]

3. Custom Commands Design
   - Commands to simplify user interface: [Which commands?]
   - Relationship between commands and workflow.md: [Patterns where commands initiate workflows]

Conclusion:
- Strengths of general-purpose skill library: [Reusability, consistency]
- Limitations of general-purpose skills: [Not optimized for specific workflows]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 3.2: Workflow-Specific Skills**

```
You are an expert designing dedicated skills and hooks optimized for a specific workflow.

Perspective: "Dedicated builds per workflow maximize performance and accuracy."

Analysis Content:

1. Skill Design
   - Workflow-specific skills: [Specialized skills needed solely for this workflow]
   - Optimization points for each skill: [Where does it excel compared to general skills?]
   - Token efficiency: [Does the specialized skill save more tokens?]

2. Hooks Design
   - Workflow-specific hooks: [Respond exclusively to specific workflow stages]
   - Hook conditional branching: [Different responses to the same event based on workflow state]

3. Custom Commands Design
   - Dedicated workflow commands: [Dedicated interface for this workflow]

Conclusion:
- Strengths of specific skills: [Accuracy, token efficiency]
- Limitations of specific skills: [Zero reusability, maintenance burden]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 3.1 vs 3.2 Comparison)**

```
Skill Strategy Selection:
- General-purpose: [Fewer skills, broad reusability, slight inefficiency in specific workflows]
- Specific: [More skills, high accuracy, maintenance burden]

Suitable Strategy per Component:
- Components used across multiple workflows: General-purpose skills
- Components unique to this workflow: Specific skills
```

---

#### **Verification & Quality Coder - 2 Branches**

**Branch 4.1: Strict Verification**

```
You are a quality specialist applying automated verification logic to every task.

Perspective: "Unverified output cannot be trusted."

Analysis Content:

1. Task Verification Implementation
   - Completion criteria for each task: [Defined in automatically verifiable formats]
   - Deliverable format verification: [Method to compare expected format vs actual output]
   - Content quality verification: [LLM-based self-verification? Rule-based?]
   - Automated rerun loop on verification failure: [Retry count, modification instruction strategy]

2. Workflow-Level Verification
   - Overall workflow completion determination: [All tasks passed + final quality gate]
   - Intermediate deliverable verification: [Verifying intermediate results across task chains]
   - Regression verification: [Ensuring previously passed tasks remain unbroken]

3. Verification Cost Analysis
   - Verification logic code volume: [Additional code footprint per task]
   - Token consumption increase from verification: [__% increase]
   - Execution time increase from verification: [__% increase]

Conclusion:
- Benefits of strict verification: [High reliability]
- Costs of strict verification: [Increased implementation overhead, increased token consumption]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 4.2: Selective Verification**

```
You are a pragmatic quality specialist applying verification only to core tasks and trusting the rest.

Perspective: "Verifying everything is too expensive. Verify only the core."

Analysis Content:

1. Verification Target Selection Criteria
   - Mandatory verification tasks: [Criteria — failure impacts entire workflow?]
   - Tasks to trust and proceed: [Criteria — recoverable even if failed?]
   - Verification cost vs impact: [Task-by-task analysis]

2. Lightweight Verification Techniques
   - Format-only verification (skip content validation): [Pattern]
   - Sampling verification (verify a subset only): [Pattern]
   - User checkpoint (request user confirmation instead of automated check): [Pattern]

3. Verification Cost Analysis
   - Token savings from selective verification: [__% savings compared to strict]
   - Expected frequency of missed errors: [__]

Conclusion:
- Benefits of selective verification: [Rapid implementation, lower token consumption]
- Risks of selective verification: [Timing of discovering missed errors]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 4.1 vs 4.2 Comparison)**

```
Verification Strategy Selection:
- Strict: [High reliability, high implementation & token costs]
- Selective: [Rapid implementation, core guaranteed, accepts partial risk]

Suitable Strategy per Component:
- Failure impacts entire system: Strict verification
- Failure has localized impact: Selective verification or omitted verification
```

---

#### **State & Recovery Coder - 2 Branches**

**Branch 5.1: File-Based State (File-based state management)**

```
You are an expert designing straightforward state management via JSON/YAML files.

Perspective: "Files are transparent and easy to debug."

Analysis Content:

1. State File Schema Design
   - Workflow state file: [Structure, fields, update timing]
   - Task result files: [Structure, storage location, naming conventions]
   - Checkpoint files: [Structure, save frequency]

2. State Passing Between Agents
   - Orchestrator → sub-agent: [Which files and where?]
   - Sub-agent → orchestrator: [Result return format]
   - Inside Agent Swarm: [Shared state file access patterns]

3. Error Recovery Implementation
   - Resume upon session expiration: [How to resume from checkpoints?]
   - Context window exhaustion mitigation: [Load only necessary portions from state file]
   - Retry logic: [Method to rerun only failed tasks]

Conclusion:
- Strengths of file-based approach: [Transparency, ease of debugging, simple implementation]
- Limitations of file-based approach: [Concurrent access conflicts, file sprawl]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 5.2: Structured State Machine**

```
You are an expert precisely managing workflow state using formalized state machine patterns.

Perspective: "Explicit state transitions make complex workflows predictable."

Analysis Content:

1. State Machine Design
   - State definitions: [Inventory of states across entire workflow]
   - Transition conditions: [Conditions for State A → State B]
   - Disallowed transitions: [Transitions that must be explicitly blocked]

2. Implementation Methodology
   - Expressing state machines in files: [JSON schema]
   - Location of transition logic: [Orchestrator? Hook? Skill?]
   - State integrity verification: [How to verify current state validity?]

3. Error Recovery Implementation
   - State rollback: [Method to revert to previous state]
   - Partial failure handling: [When only a subset of tasks fail]
   - Idempotency guarantees: [Is it safe to rerun the same task?]

Conclusion:
- Strengths of state machine: [Precise control, high predictability]
- Limitations of state machine: [Implementation complexity, risk of over-engineering]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 5.1 vs 5.2 Comparison)**

```
State Management Selection:
- File-based: [Simple workflows, rapid implementation, easy debugging]
- State machine: [Complex workflows, precise control, complex implementation]

Suitable Strategy per Component:
- Sequential task chain: File-based is sufficient
- Complex branching/merging/retries: State machine required
```

---

### Synthesis of Branch Findings (Integrated Analysis of 10 Branches)

```
## Comprehensive Coding Research Report

### Step 1: Implementation Approach Spectrum per Domain

Workflow Script:
  Declarative ←─────────────→ Procedural
  [Our position: __]

Agent Orchestration:
  Centralized ←─────────────→ Distributed
  [Our position: __]

Skills & Hooks:
  General-Purpose ←─────────────→ Specific
  [Our position: __]

Verification:
  Strict ←─────────────→ Selective
  [Our position: __]

State Management:
  File-Based ←─────────────→ State Machine
  [Our position: __]

### Step 2: Synthesis of Technical Limits and Possibilities Discovered
- Easier than expected: [Concrete]
- Harder than expected: [Concrete]
- Currently impossible: [Concrete, reason]
- Unexpected possibilities: [Concrete]

### Step 4: Parking Lot Consolidation
- Findings requiring further investigation: [List, categorized]
```

---

## PHASE 2: Discussion by Coding Perspective (4 Discussion Branches)

### Branch 2.A: Workflow Expressiveness Priority Discussion

```
You are a discussion moderator prioritizing workflow.md expressiveness and precise execution control.

Question: "Can workflow.md express the workflow with sufficient precision?"

Receiving findings from 10 Branches in PHASE 1:
1. Implementation patterns that express each component most precisely
2. Structural limitations of workflow.md and workarounds
3. Optimal combination of orchestrator / sub-agent / Agent Swarm

Conclusion (Expressiveness-First PRD):
- Recommended implementation patterns: [Per component]
- Pros and cons of this combination: [Concrete]
```

### Branch 2.B: Implementation Stability Priority Discussion

```
Question: "Which implementation pattern operates most reliably?"

Conclusion (Stability-First PRD):
- Recommended implementation patterns: [Combination with lowest error rate]
- Proportion of verification/recovery code: [High]
- Pros and cons of this combination: [Concrete]
```

### Branch 2.C: Implementation Speed Priority Discussion

```
Question: "Which pattern allows the fastest working harness implementation?"

Conclusion (Speed-First PRD):
- Recommended implementation patterns: [Minimal code volume]
- Omitted verification/recovery code: [Concrete]
- Pros and cons of this combination: [Concrete]
```

### Branch 2.D: Maintainability/Extensibility Priority Discussion

```
Question: "Which pattern is easiest to modify or expand with new workflows in 6 months?"

Conclusion (Maintainability-First PRD):
- Recommended implementation patterns: [Modularized, maximum reuse]
- Change footprint when adding new workflows: [Minimal]
- Pros and cons of this combination: [Concrete]
```

### Synthesis of 4 Discussion Branches

```
| Implementation Pattern | Expressiveness PRD | Stability PRD | Speed PRD | Maintainability PRD | Consensus |
|------------------------|-------------------|---------------|-----------|---------------------|-----------|
| Pattern A | ✓ | ✓ | ✓ | ✓ | 4/4 ✅ |
| ... | | | | | |
```

---

## PHASE 3: Implementation Scenarios (3 Defense Levels)

### Branch 3.A: Full-Defensive (Handle All Edge Cases)

```
Philosophy: "Prepare for every possible failure mode."

Implementation Configuration:
- workflow.md: [Procedural, explicit branches and exceptions]
- Orchestration: [Orchestrator-centric, state checks at every transition]
- skills/hooks: [Hybrid general + specific, hooks on every event]
- Verification: [Automated verification + rerun loop on every task]
- State Management: [Structured state machine, checkpoints + rollback]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]
```

### Branch 3.B: Balanced (Defend Core Only)

```
Philosophy: "Defend the core critical path; handle the rest pragmatically."

Implementation Configuration:
- workflow.md: [Hybrid declarative + procedural]
- Orchestration: [Orchestrator-centric, checks at core transition points only]
- skills/hooks: [Primarily general skills, hooks on core events only]
- Verification: [Automated checks on core tasks only, lightweight checks on rest]
- State Management: [File-based, checkpoints at key branching points only]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]
```

### Branch 3.C: Rapid-Prototype (Minimal Implementation, Rapid Verification)

```
Philosophy: "Get it running first, strengthen incrementally."

Implementation Configuration:
- workflow.md: [Declarative, minimal instructions]
- Orchestration: [Simple orchestrator control, minimal sub-agents]
- skills/hooks: [Essential skills only, virtually no hooks]
- Verification: [Primarily manual user checks, minimal automated validation]
- State Management: [Simple file-based, no checkpoints]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]

## Incremental Hardening Roadmap
- Phase 1 (Immediate): [Verify operation with minimal implementation]
- Phase 2 (Stabilization): [Add core verification + error handling]
- Phase 3 (Completion): [Add comprehensive defensive code]
```

### Comparative Analysis of 3 Scenarios

```
| Criterion | Full-Defensive | Balanced | Rapid-Prototype |
|-----------|---------------|----------|-----------------|
| Total Implementation Scope | Very Large | Moderate | Small |
| Stability | Very High | High | Low (Manual backup) |
| Implementation Timeline | Long | Moderate | Short |
| Token Consumption (incl. verification) | High | Moderate | Low |
| Ease of Debugging | High (Rich logs) | Moderate | Low |
| Extension Cost | Low (Solid foundation) | Moderate | High (Added later) |

Selection Logic:
1. "Stability is paramount, implementation schedule is flexible" → Full-Defensive
2. "Guarantee the core first, harden the rest incrementally" → Balanced
3. "Execute first to validate, then harden" → Rapid-Prototype
```

---

## PHASE 4: Integration of Findings — Comprehensive Report

### Decision Process

```
You have received 3 implementation scenarios.

Current Mission:
1. Compare the essence of each scenario
2. Select the scenario suited to our situation
3. Finalize implementation complexity determination
4. Organize findings requiring further investigation
5. Compile implementation pattern references

---

## STEP 1: Synthesis of Comprehensive Research Findings

### Overall Technical Assessment for Workflow Implementation

Recommended approach across 5 domains:
- Workflow Script: [Declarative / Procedural / Hybrid — Reason]
- Agent Orchestration: [Centralized / Distributed / Hybrid — Reason]
- Skills & Hooks: [General-purpose / Specific / Hybrid — Reason]
- Verification: [Strict / Selective / Hybrid — Reason]
- State Management: [File / State Machine / Hybrid — Reason]

### Core Findings Discovered During Research

Easier than expected:
- [Concrete item] — Reason: [__]

Harder than expected:
- [Concrete item] — Reason: [__]

Currently impossible with Claude Code:
- [Concrete item] — Reason: [__]

Unexpected possibilities:
- [Concrete item] — Reason: [__]

---

## STEP 2: Implementation Pattern Reference

Based on selected scenario or hybrid model, organize patterns directly referenceable during actual development.

### Pattern 1: Basic Structure of workflow.md
- Task definition format: [Structural example]
- Dependency representation: [Structural example]
- Completion criteria representation: [Structural example]

### Pattern 2: Orchestrator-Sub Agent Configuration
- Orchestrator CLAUDE.md: [Structural example]
- Sub-agent role definitions: [Structural example]
- Delegation & result collection flow: [Structural example]

### Pattern 3: Leveraging fork and agent-teams
- Fork branching timing and method: [Structural example]
- agent-teams configuration: [Structural example]
- Merging results: [Structural example]

### Pattern 4: skill / hook / command Implementation
- Skill definition structure: [Structural example]
- Hook configuration structure: [Structural example]
- Custom command definition: [Structural example]

### Pattern 5: Task Verification Implementation
- Verification logic structure: [Structural example]
- Rerun loop: [Structural example]

### Pattern 6: State Management Implementation
- State file schema: [JSON example]
- Checkpoint / recovery flow: [Structural example]

---

## STEP 3: Component Implementation Reference

Based on the selected scenario, compile implementation patterns for each component.
This serves as a reference directly usable during development.

### Component [A] Implementation Pattern
- Relevant section of workflow.md: [Structural example]
- Agent assignment: [orchestrator / sub-agent / fork / agent-teams]
- Required skills: [List]
- Required hooks: [List]
- Verification method: [Concrete]
- State management: [File structure]

### Component [B] Implementation Pattern
- ...

---

## STEP 4: Team Sign-Off

To each Teammate:

"From your domain perspective, is this implementation pattern realistic?"

Final Signatures:
✅ Workflow Script Architect: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Agent Orchestration Coder: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Skills & Hooks Developer: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Verification & Quality Coder: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ State & Recovery Coder: [Thorough / Partial / Inadequate] Rationale: [Concrete]
```

---

## Final Deliverables (What You Receive)

1. **Coding Deep Dive Comprehensive Report** — Implementation approach analysis across 5 domains, discovered technical limits/possibilities, core determinations
2. **Implementation Pattern Reference** — Concrete examples for workflow.md structure, orchestrator setup, skill/hook/command implementations, verification logic, and state management patterns
3. **Comparison of 3 Implementation Scenarios** — Configurations, complexity, pros and cons of Full-Defensive / Balanced / Rapid-Prototype
4. **Findings Requiring Further Investigation** — Items not fully answered in this research
5. **Team Sign-Off Document**

→ These deliverables will be integrated into the final PRD alongside primary PRD research, technology deep dives, and other specialized investigations.

---

## How to Execute

### Claude Code Teammates - Fork-Based Parallel Execution (10 Branches)

```
In workflow.md:

## PHASE 1: Parallel Execution of 10 Coding Investigation Branches
/create_teammate "Workflow-Declarative" [Branch 1.1]
/create_teammate "Workflow-Procedural" [Branch 1.2]
/create_teammate "Orch-Centralized" [Branch 2.1]
/create_teammate "Orch-Distributed" [Branch 2.2]
/create_teammate "Skills-General" [Branch 3.1]
/create_teammate "Skills-Specific" [Branch 3.2]
/create_teammate "Verify-Strict" [Branch 4.1]
/create_teammate "Verify-Selective" [Branch 4.2]
/create_teammate "State-FileBased" [Branch 5.1]
/create_teammate "State-Machine" [Branch 5.2]

/run_parallel all

## PHASE 2: Parallel Execution of 4 Discussion Branches
/create_teammate "Discussion-Expression" [Branch 2.A]
/create_teammate "Discussion-Stability" [Branch 2.B]
/create_teammate "Discussion-Speed" [Branch 2.C]
/create_teammate "Discussion-Maintain" [Branch 2.D]

/run_parallel all

## PHASE 3: Parallel Execution of 3 Scenario Branches
/create_teammate "Impl-FullDefensive" [Branch 3.A]
/create_teammate "Impl-Balanced" [Branch 3.B]
/create_teammate "Impl-RapidPrototype" [Branch 3.C]

/run_parallel all

## PHASE 4: Final Integration
/run_moderator [Research findings integration + comprehensive report drafting prompt]
```

Or **Sequential Execution**:

```
1. PHASE 1 (10 Branches) → Organize findings → Consolidate parking lot
2. PHASE 2 (4 Branches) → Organize findings
3. PHASE 3 (3 Branches) → Compare scenarios
4. PHASE 4 (Final Integration) → Comprehensive report + Implementation pattern reference
```

---

## Tips & Best Practices

**PHASE 1 (Investigation Branches) Operational Tips**
- **Must include pseudocode or structural examples** — abstract assertions of "it's possible" are prohibited
- Design based on **actual operations** of Claude Code's Task Management System, fork, agent-teams, Agent Swarm, etc.

**PHASE 2 (Discussion Branches) Operational Tips**
- Discuss **differences when applied to concrete workflows**, rather than comparing abstract patterns
- Always specify concrete code-level differences

**PHASE 3 (Scenario Branches) Operational Tips**
- Quantitatively compare total implementation scope, implementation difficulty, token consumption, and maintenance burden for each scenario

**PHASE 4 (Final Integration) Operational Tips**
- Write **implementation pattern references at a quality level directly usable in actual development**
- Frankly document discovered technical limits and possibilities — critical reference material for final PRD authoring
- Clearly articulate areas requiring additional research
