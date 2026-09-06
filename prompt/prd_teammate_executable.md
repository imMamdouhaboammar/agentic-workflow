# PRD Primary Research - Teammate Execution Framework

> **Purpose of this Document**: The broad-net primary research phase. The deliverable of this document is not the final PRD, but rather the "Primary PRD Draft + Follow-up Deep Dive Execution Plan". Following specialized deep dives into technology, external integrations, coding implementation, etc., all findings will be synthesized into the final PRD.

## Initial Setup (User Input)

**Product Name**: [Enter here]
**Primary Use Scenarios**: [Enter core task types this harness will automate]
**Workflow Problem to Solve**: [Enter current manual or inefficient workflows]

---

## Fork-Based Sessions Branch Strategy (Extended Feature)

This framework leverages the `/fork` feature to **explore multiple paths simultaneously in each Phase**.
This achieves deeper research, rigorous debate, and robust convergence.

### Strategy Overview

```
Initial Setup
  ↓
[PHASE 1: Investigation]
  ├─ /fork Branch 1.1: Workflow Architect (Assumption A)
  ├─ /fork Branch 1.2: Workflow Architect (Assumption B)
  ├─ /fork Branch 2.1: Scenario Explorer (Assumption A)
  ├─ /fork Branch 2.2: Scenario Explorer (Assumption B)
  ├─ /fork Branch 3.1: Operator Analyst (Assumption A)
  ├─ /fork Branch 3.2: Operator Analyst (Assumption B)
  ├─ /fork Branch 4.1: Sustainability Strategist (Assumption A)
  └─ /fork Branch 4.2: Sustainability Strategist (Assumption B)
  ↓
[PHASE 2: Discussion]
  ├─ /fork Branch 2.A: Workflow Architecture Priority Discussion
  ├─ /fork Branch 2.B: Scenario Coverage Priority Discussion
  ├─ /fork Branch 2.C: Operator Experience Priority Discussion
  └─ /fork Branch 2.D: Sustainability/Efficiency Priority Discussion
  ↓
[PHASE 3: Convergence]
  ├─ /fork Branch 3.A: Deep Automation (High Automation)
  ├─ /fork Branch 3.B: Selective Automation (Selective Automation)
  └─ /fork Branch 3.C: Minimal Automation (Minimal Automation)
  ↓
[PHASE 4: Integration]
  → Compare 3 Scenarios
  → Finalize Primary PRD Draft
  → Output Follow-up Deep Dive Execution Plan
```

### Purpose of Using Branches

**Branches in Investigation Phase**
- Acknowledge that multiple assumptions are viable even within the same perspective
- Validate that each assumption carries legitimate justification
- Capture out-of-scope discoveries in the parking lot during exploration

**Guideline for Setting Assumption Axes**: At project kickoff, choose the single most meaningful axis among the following candidates:
- "Claude Code Standalone Completion vs External Tool Integration Premise"
- "Single-User Exclusive vs Team-Shareable Architecture"
- "Single-Project Focus vs Multi-Project Simultaneous Management"
- "Minimal Automation (Heavy User Intervention) vs Maximum Automation (Fully Autonomous Execution)"

Regardless of which axis is chosen, forcing the exploration of two opposing assumptions guarantees broad coverage.

**Branches in Discussion Phase**
- Validate how conclusions diverge based on which perspective is prioritized
- Trace how pathways of "Workflow Structure First" vs "Scenario Coverage First" vs "Operability First" vs "Sustainability First" create distinct PRDs
- Understand the pros and cons of each path

**Branches in Convergence Phase**
- Simultaneously evaluate 3 scenarios based on automation scope and structural complexity
- Concurrently evaluate "What if we automated more aggressively?" vs "What if we started minimally?"
- Each scenario outputs follow-up research items across 4 categories to link directly to subsequent deep dive phases

---

## Constraints

Maintain the following constraints while running this process:

**Investigation Phase Constraints**
- Each Teammate is **prohibited from making baseless assertions** (intuition or conjecture alone is insufficient)
- When evaluating alternative workflow tools or methodologies, **verify real-world execution feasibility** in a local environment
- **Must explicitly state Claude Code actual execution limits** (context window size, token burn rate, concurrent Teammate limits, Hooks conditional branching support)
- When concluding that something is "impossible", specify **exact technical constraint points** (missing APIs, unsupported capabilities)
- Each Teammate must maintain independence without being influenced by other perspectives
- **Parking Lot Rule**: Discoveries made during investigation that exceed the current Branch's scope must be recorded in the parking lot. Specify the discovery details, source Branch, and corresponding follow-up research category (Technical / External Integration / User Behavior / Structural Risk)

**Discussion Phase Constraints**
- The Moderator must maintain strict neutrality (no favoritism toward any specific perspective)
- If one perspective is emphasized 3 consecutive times, explicitly grant speaking turns to opposing perspectives
- Mere agreement ("I agree") is unacceptable → substantive justification ("why I agree") is mandatory
- Conflicts are required (unanimous agreement across all 4 perspectives indicates a lack of discussion depth)
- **Parking Lot Rule**: Out-of-scope items identified during discussion must likewise be logged in the parking lot

**Convergence Phase Constraints**
- Green Zone: **All 4 perspectives must agree** (3 perspectives agreeing places it in the Yellow Zone)
- Yellow Zone: Must define **explicit trigger conditions** ("Under what exact conditions will this be included?")
- Red Zone: Must define **explicit re-evaluation milestones** ("Review after 6 months" or "Review when condition X is met")
- Consolidate components to at most 15 (avoid fragmentation)
- **Each scenario must output follow-up research items across all 4 categories**

---

## Success Points

Criteria for determining whether this research process was **successful**:

### Phase 1 (Investigation) Success Points
✅ **Are each Teammate's conclusions concrete?**
- [ ] Are workflow components (Hooks, Teammates, Pipelines, Triggers, etc.) concrete? (e.g., "Automation" ❌ → "Commit Hook executing automated linting + test suite" ✅)
- [ ] Are supporting grounds explicitly stated? (e.g., "Per Claude Code Hooks official documentation...", "Based on empirical execution results...")
- [ ] Are priorities clear? (Top 3 explicitly derived)

✅ **Did the 4 perspectives analyze from distinctly different angles?**
- [ ] Are there components emphasized exclusively by the Workflow Architect? (Focusing on pipeline structure)
- [ ] Are there scenarios emphasized exclusively by the Scenario Explorer? (Focusing on functional coverage)
- [ ] Are there friction points cautioned against exclusively by the Operator Analyst? (Focusing on usability)
- [ ] Are there structural bottlenecks flagged exclusively by the Sustainability Strategist? (Focusing on long-term sustainability)
- → If all are present, ✅ multi-faceted analysis succeeded

### Phase 2 (Discussion) Success Points
✅ **Were conflicts explicitly surfaced?**
- [ ] At least 3 points of substantive disagreement captured
- [ ] Clear rationale ("why perspectives diverge") documented for each disagreement
- [ ] Represents **logical conflict**, rather than mere stylistic preference

✅ **Are consensus boundaries clearly defined?**
- [ ] At least 5 components where **all 4 perspectives agree**
- [ ] Do those components **genuinely resolve** the core workflow problem?
- [ ] Can the question "Can a functional harness operate on Green Zone components alone?" be answered with "YES"?

✅ **Were high-risk assumptions captured?**
- [ ] Top 5 riskiest assumptions explicitly listed
- [ ] Concrete "verification methods" defined for each assumption (e.g., "Empirical execution test", "Claude Code API documentation verification")
- [ ] Assumptions represent threats capable of collapsing the entire workflow

### Phase 3 (Convergence) Success Points
✅ **Is the Primary PRD Draft actionable?**
- [ ] Is the cumulative implementation complexity of Green Zone components realistic and explicitly stated?
- [ ] Is the priority sequence of each component clear?
- [ ] Are deferred components genuinely safe to defer?

✅ **Can all teams sign off?**
- [ ] Workflow Architect: "The workflow can execute reliably under this architecture" → Agrees?
- [ ] Scenario Explorer: "Core use scenarios are covered by this configuration" → Agrees?
- [ ] Operator Analyst: "Users can accept this configuration complexity" → Agrees?
- [ ] Sustainability Strategist: "This architecture is sustainable to operate and expand long-term" → Agrees?
- → All must agree for ✅

✅ **Are links to follow-up deep dives established?**
- [ ] Follow-up research items across 4 categories (Technical / External Integration / User Behavior / Structural Risk) output for each scenario
- [ ] Parking lot items consolidated into follow-up research categories
- [ ] Explicitly specified: "Which PRD decision will be destabilized if this item is not verified?"

---

## Final Review Checklist

Verify these criteria upon completion of research:

```
Investigation Phase:
[ ] Are Workflow Architect conclusions concrete? (At the level of CLAUDE.md, .claude/, Hooks, etc.)
[ ] Is the Scenario Explorer landscape sufficiently comprehensive?
[ ] Is the Operator Analyst user taxonomy realistic?
[ ] Did the Sustainability Strategist pinpoint structural limits?

Discussion Phase:
[ ] Are at least 3 substantive disagreements recorded?
[ ] Are resolutions or priority decisions determined for each disagreement?
[ ] Are Top 5 risky assumptions and verification plans specified?

Convergence Phase:
[ ] Are Green Zone components consolidated to 5-7 items?
[ ] Are reasons for "absolute necessity" stated for each Green Zone component?
[ ] Are inclusion conditions stated for Yellow Zone components?
[ ] Are re-evaluation milestones stated for Red Zone components?

Follow-up Linkage:
[ ] Were 4-category follow-up research items produced across all 3 scenarios?
[ ] Were parking lot items merged into the follow-up research inventory?
[ ] Is the follow-up deep dive execution plan organized with clear priorities?

Final:
[ ] Would all 4 Teammates endorse this Primary PRD Draft?
[ ] Has the follow-up deep dive execution plan been comprehensively produced without omissions?
```

---

## PHASE 1 Execution: Fork-Based Parallel Investigation Structure

### Step 1: Independent Execution of 2 Branches per Teammate

In this step, **each Teammate explores two opposing assumptions** within their perspective simultaneously.
The assumption axis selected during Initial Setup is used. Below uses "Claude Code Standalone Completion vs External Tool Integration Premise" as the reference axis.

#### **Workflow Architect Branch A: Self-Contained (Claude Code Standalone Completion)**

```
You are designing the workflow architecture to be fully self-contained within the Claude Code ecosystem.

Core Assumption: "Without external tools, all workflows can be implemented using Claude Code built-in features alone (Hooks, Teammates, /fork, CLAUDE.md, .claude/, etc.)."

Analysis Content:
1. Workflow Execution Structure
   - Basic execution unit of pipeline: [Task? Session? Prompt chain?]
   - Branching, loops, and failure recovery: [How implemented via Claude Code built-ins?]
   - State persistence: [File-based? Memory? Leveraging .claude/ directory?]

2. Configuration Architecture
   - CLAUDE.md strategy: [Single file? Hierarchical partitioning?]
   - .claude/ directory design: [Which configurations go where?]
   - Hooks utilization: [Which automations trigger on which events?]

3. Multi-Agent Execution
   - Context isolation strategy across Teammates: [How is independence guaranteed?]
   - Preventing state collisions during parallel execution: [Concrete methodology]
   - Result synthesis mechanism: [How are deliverables merged across Teammates?]

Conclusion:
- Scope of workflows implementable via Claude Code standalone: [Concrete]
- Strengths of self-contained design: [3 concrete points]
- Limitations of self-contained design: [Where does it hit a ceiling?]
- Essential components in this architecture: [Top 3]

🅿️ Parking Lot: [Log discoveries outside this Branch's scope requiring follow-up investigation]
```

#### **Workflow Architect Branch B: Integrated (External Tool Integration Premise)**

```
You are designing the workflow architecture under the premise of integrating with external tools.

Core Assumption: "Claude Code alone has limits; it must integrate with MCP servers, external APIs, and local scripts to achieve a complete workflow."

Analysis Content:
1. Workflow Execution Structure
   - Basic execution unit of pipeline: [Composite units incorporating external tool calls]
   - External integration points: [At which stages do external tools intervene?]
   - Error handling: [Fallback strategies upon external tool failure]

2. Integration Architecture
   - MCP server utilization strategy: [Which MCP servers for what purposes?]
   - Local script / CLI tool integration: [Which tools invoked and how?]
   - Data flow: [Data transfer mechanisms between Claude Code ↔ external tools]

3. Complexity Management
   - External dependency management: [Versioning, compatibility, installation]
   - Debugging strategy: [Root cause analysis upon integration failure]
   - Configuration portability: [What breaks when migrating across environments?]

Conclusion:
- Workflow types strictly requiring external integration: [Concrete]
- Strengths of integration: [3 concrete points]
- Risks of integration: [Complexity explosion, dependency overhead, etc.]
- Essential components in this architecture: [Top 3]

🅿️ Parking Lot: [Log discoveries outside this Branch's scope requiring follow-up investigation]
```

#### **Final Synthesis (Branch A vs B Comparison)**
```
Qualitative Rationale:
- Scenarios where Self-Contained is warranted: [Concrete scenarios]
- Scenarios where Integrated is warranted: [Concrete scenarios]

Data-Driven Assessment:
- To what degree do Claude Code current built-in features provide coverage?
- Which specific capabilities strictly require external integration?
- Matters to verify in follow-up research: [Concrete]
```

---

#### **Scenario Explorer Branch A: Assumption A Perspective**

```
You are scanning the landscape of use scenarios this harness must cover from the perspective of Assumption A.

Analysis Content:
1. Scenario Landscape
   - Full spectrum of task types automatable by this harness: [Enumerate broadly]
   - Complexity spectrum per task type: [Simple → Complex]
   - Alternative tools/methods currently used by practitioners: [Concrete]

2. Survey of Alternative Tools & Methodologies
   - At least 3 alternative tools: [Strengths, weaknesses, local execution feasibility]
   - Areas this harness can replace or augment: [Concrete]
   - Areas this harness cannot replace: [Why?]

3. Scenario Prioritization
   - Highest-frequency scenarios: [Top 3]
   - Highest-value automation scenarios: [Top 3]
   - Most difficult scenarios to implement: [Top 3]

Conclusion:
- Scenarios to prioritize under this assumption: [Top 3]
- Core components demanded by each scenario: [Concrete]
- Scenarios to defer: [Concrete]

🅿️ Parking Lot: [Log out-of-scope discoveries requiring follow-up investigation]
```

#### **Scenario Explorer Branch B: Assumption B Perspective**

```
You are scanning the landscape of use scenarios this harness must cover from the perspective of Assumption B.

(Follow identical analytical structure as Branch A, starting from the opposing assumption to reach distinct conclusions)

Analysis Content:
1. Scenario Landscape
   - [Automatable scope viewed through Assumption B]
   - [Complexity spectrum shifts under Assumption B]
   - [Alternative tools more relevant under Assumption B]

2. Survey of Alternative Tools & Methodologies
   - [3+ alternative tools in the context of Assumption B]

3. Scenario Prioritization
   - [How priorities shift under Assumption B]

Conclusion:
- Scenarios to prioritize under this assumption: [Top 3]
- Differences compared to Branch A: [Concrete]

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

#### **Final Synthesis (Branch A vs B Comparison)**
```
Implications of Scenario Selection:
- Prioritizing Assumption A: [Coverage scope, implementation direction]
- Prioritizing Assumption B: [Coverage scope, implementation direction]

Realistic Questions:
- Can both be supported simultaneously?
- If not, which scenario must be supported first?
- When should deferred scenarios be addressed?
```

---

#### **Operator Analyst Branch A: Power User (Complex Multi-Agent Designer)**

```
You are analyzing from the viewpoint of advanced power users who will operate this harness.

Persona: "A Claude Code Max subscriber who designs, optimizes, and debugs multi-agent workflows directly."

Analysis Content:
1. Persona Deep Dive
   - Background: [Development experience, automation proficiency, operating environment]
   - Current workflow: [Tasks performed manually vs tasks already automated]
   - Core friction points: [Concrete pain points in current workflows]

2. Components Required by this User
   - Mandatory components: [Top 3, without which there is no reason to use this harness]
   - Specific problems resolved by each component: [Explicit]

3. Acceptable Complexity Limits
   - Time willing to invest in configuration: [Concrete]
   - Receptivity to direct manual editing of CLAUDE.md: [Acceptable / Unacceptable]
   - Willingness to debug and fine-tune: [High / Low]

Conclusion:
- 3 core components for this persona: [Concrete]
- If these components are missing: [User defaults to alternative tools]

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

#### **Operator Analyst Branch B: General User (Simple Automation User)**

```
You are analyzing from the viewpoint of general Claude Code users who will operate this harness.

Persona: "A Claude Code Max subscriber who wants out-of-the-box automation rather than complex configuration."

Analysis Content:
1. Persona Deep Dive
   - Background: [Development experience level, attitude toward automation]
   - Current workflow: [Predominantly manual, limited automation experience]
   - Core friction points: [Repetitive, tedious tasks]

2. Components Required by this User
   - Mandatory components: [Top 3, delivering immediate visible value]
   - Learning curve of each component: [How fast can value be realized?]

3. Acceptable Complexity Limits
   - Time willing to invest in setup: [Very short]
   - Requirement for pre-configured templates: [Mandatory / Optional]
   - Autonomous error resolution ability: [Present / Absent]

Conclusion:
- 3 core components for this persona: [Concrete]
- Even if these components are missing: [Can tolerate manual workarounds]

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

#### **Final Synthesis (Branch A vs B Comparison)**
```
Implications of User Persona Selection:
- Prioritizing Power Users: [Design trajectory, baseline complexity]
- Prioritizing General Users: [Design trajectory, baseline complexity]

Realistic Questions:
- Can both user types be satisfied?
- If not, who must be built for first?
- Will supporting the other type later require architectural overhauls?
```

---

#### **Sustainability Strategist Branch A: Assumption A Perspective**

```
You are analyzing the sustainable operation and scalability of this harness from the perspective of Assumption A.

Analysis Content:
1. Token Consumption Efficiency
   - Estimated token consumption per workflow type: [Concrete]
   - Headroom relative to Claude Code Max subscription quotas: [Ample / Tight / Exceeded]
   - Token optimization strategies: [Concrete methods]

2. Maintenance Overhead
   - Impact of Claude Code platform updates on the harness: [What breaks?]
   - Configuration file complexity growth over time: [How complex over time?]
   - Debugging difficulty: [How easily can root causes be traced upon failure?]

3. Scalability Limits
   - As workflow count expands: [Where do bottlenecks occur?]
   - As project size scales up: [Context window exhaustion, state management sprawl]
   - As team usage expands: [Configuration sharing, conflict management]

Conclusion:
- Essential components for sustainability: [Top 3]
- Greatest structural bottleneck: [Concrete]
- Projected maintenance burden in 6 months: [High / Medium / Low]

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

#### **Sustainability Strategist Branch B: Assumption B Perspective**

```
You are analyzing the sustainable operation and scalability of this harness from the perspective of Assumption B.

(Follow identical analytical structure as Branch A, starting from the opposing assumption to reach distinct conclusions)

Analysis Content:
1. Token Consumption Efficiency: [Consumption patterns shifting under Assumption B]
2. Maintenance Overhead: [Maintenance burden shifting under Assumption B]
3. Scalability Limits: [Bottlenecks shifting under Assumption B]

Conclusion:
- Sustainability evaluation under this assumption: [Concrete]
- Key differences compared to Branch A: [Concrete]

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

#### **Final Synthesis (Branch A vs B Comparison)**
```
Sustainability Assessment:
- Under Assumption A: [Operational health in 6 months]
- Under Assumption B: [Operational health in 6 months]

Realistic Questions:
- Likelihood of token consumption exceeding subscription quotas: [Present / Absent]
- Likelihood of maintenance burden offsetting automation gains: [Present / Absent]
- Items to verify in follow-up research to confirm this judgment: [Concrete]
```

---

### Step 2: Synthesis of Branch Findings (Consolidation of 8 Branches)

After executing all 8 Branches (2 per Teammate):

```
## Comprehensive Investigation Report

### Step 1: Spectrum Mapping per Perspective
- Workflow Architect: Self-Contained ←─────────→ External Integration
  [A Score: __/10] [Our position: __]
  
- Scenario Explorer: Assumption A ←─────────→ Assumption B
  [A Score: __/10] [Our position: __]
  
- Operator Analyst: Power User ←─────────→ General User
  [A Score: __/10] [Our position: __]
  
- Sustainability Strategist: Assumption A ←─────────→ Assumption B
  [A Score: __/10] [Our position: __]

### Step 2: Intersection Across Branches (Agreed by all)
```
Absolute Essential Components:
[Components deemed "Mandatory" by both Branch A and B]

Items to Strictly Avoid:
[Items deemed "Risky" across all perspectives]
```

### Step 3: Maximum Discrepancies Across Branches
```
Greatest Divergence of Opinion:
- Branches: [e.g., Workflow Architect A vs B]
- Root cause of divergence: [Which assumptions differ?]
- Resolution path: [What follow-up research is required?]

Next Priority Verification Items:
1. [Method to verify Branch A]
2. [Method to verify Branch B]
3. [Criteria to determine which assumption is correct]
```

### Step 4: Parking Lot Consolidation
```
Consolidated Parking Lot Inventory:
- Technical Verification Required: [Item list]
- External Integration Verification Required: [Item list]
- User Behavior Hypothesis Verification Required: [Item list]
- Structural Risk Exploration Required: [Item list]
```

---

## PHASE 1: Independent Agent Investigation Prompts

### Teammate 1: Workflow Architect

```
You are the workflow architecture design specialist for this harness.

Execute the following for [Product Name]:

1. Workflow Structure Investigation
   - Define the basic execution unit of the pipeline
   - Design branching, iteration, and failure recovery mechanisms
   - CLAUDE.md strategy (single file vs hierarchical partitioning)
   - .claude/ directory architecture design
   - Claude Code Hooks utilization patterns

2. Context Management Strategy
   - Context isolation methods across multi-Teammate executions
   - Local state persistence strategies (file-based vs memory)
   - Context window exhaustion prevention strategies

3. Final Structured Conclusions
   - Core design principles: [3 points]
   - Mandatory components: [Top 5]
   - Implementation complexity per component: [Low / Medium / High]
   - Anti-patterns to strictly avoid structurally: [Concrete]

**Ground all conclusions in Claude Code actual features and limitations. Never assume non-existent features.**

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

### Teammate 2: Scenario Explorer

```
You are the specialist scanning the entire landscape of use scenarios this harness will cover.

Deeply analyze use scenarios for [Product Name]:

1. Map Scenario Landscape
   - Enumerate all automatable task types for this harness
   - Classify complexity per type (Simple / Medium / Complex)
   - Highest-frequency scenarios vs highest-value scenarios

2. Alternative Tools & Methodology Survey
   - At least 3 alternative tools (strengths, weaknesses, local execution feasibility)
   - Areas this harness can replace
   - Areas this harness cannot replace

3. Workflow Requirements per Scenario
   - Components demanded by each scenario: [Concrete]
   - Common requirements across scenarios: [Overlaps]
   - Conflicting requirements across scenarios: [Collisions]

4. Final Conclusions
   - Scenarios to prioritize: [Top 3, why?]
   - Core components required for prioritized scenarios: [Concrete]
   - Deferred scenarios: [Concrete, when to support?]

**Evaluate strictly based on whether they operate in an actual local environment.**

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

### Teammate 3: Operator Analyst

```
You are the specialist analyzing user behavior patterns and operational friction points for this harness.

Deeply analyze users for [Product Name]:

1. User Taxonomy Classification
   - Type 1: Power User (Multi-agent designer) — Background, workflow, expectations
   - Type 2: General User (Simple automation user) — Background, workflow, expectations
   - Complexity tolerance limits for each type

2. User Journey Mapping
   - "Install → Setup → First Run → Repeated Usage → Scaling" journey
   - Friction points at each stage: [Concrete]
   - Stage with highest churn risk: [Where? Why?]

3. Essential Component Prioritization
   - Deemed "Mandatory" by each user type: [Top 3]
   - Deemed "Nice to have, but optional": [Top 3]
   - Dependency relationships among components

4. Final Conclusions
   - User type to prioritize: [Who? Why?]
   - Core components for prioritized user type: [Top 3]
   - Is the harness unusable without these components?: [Y/N]

**Judge based on: "Will users genuinely perform this setup directly?"**

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

### Teammate 4: Sustainability Strategist

```
You are the specialist analyzing long-term operational sustainability and scaling requirements for this harness.

Analyze sustainability for [Product Name]:

1. Token Consumption Efficiency
   - Projected token consumption per workflow type
   - Buffer relative to Claude Code Max subscription limits
   - Token conservation strategies (prompt optimization, context hygiene)

2. Maintenance Burden
   - Impact of Claude Code platform updates on the harness
   - Rate of configuration file complexity growth over time
   - Debugging difficulty (tracing failure causes across workflows)

3. Extensibility & Scaling
   - Bottlenecks as workflow count increases
   - Structural limits as project scale expands
   - Versioning and configuration migration strategies

4. Final Conclusions
   - Essential components for sustainability: [Top 3]
   - Greatest structural bottleneck: [Concrete]
   - Projected maintenance overhead in 6 months: [High / Medium / Low]
   - Anti-patterns to structurally avoid: [Concrete]

**Judge based on: "Will users still be happily using this harness in 6 months?"**

🅿️ Parking Lot: [Log out-of-scope discoveries]
```

---

## PHASE 2: Fork-Based Multi-Perspective Discussion (4 Discussion Branches)

### Overview: Conducting Parallel Discussions Prioritizing Distinct Perspectives

Following PHASE 1's 8 investigation branches, explore how conclusions diverge based on which perspective is held paramount:

```
[8 Investigation Branch Findings]
       ↓
[PHASE 2: Discussion]
  ├─ /fork Branch 2.A: Workflow Architecture Priority
  ├─ /fork Branch 2.B: Scenario Coverage Priority
  ├─ /fork Branch 2.C: Operator Experience Priority
  └─ /fork Branch 2.D: Sustainability Priority
       ↓
[Conclusions per Branch]
  ├─ PRD generated by Branch 2.A
  ├─ PRD generated by Branch 2.B
  ├─ PRD generated by Branch 2.C
  └─ PRD generated by Branch 2.D
       ↓
[Comparative Analysis: Discrepancies across 4 PRDs]
```

### Branch 2.A: Workflow Architecture Priority Discussion

```
You are the Moderator prioritizing the structural robustness of the workflow above all else.

Guidelines:
- Drive discussion centered on Workflow Architect findings
- Core question: "Does this component guarantee reliable execution of the workflow?"

PHASE 1 Input:
[Attach conclusions from 8 Branches here]

Discussion Sequence:
1. Self-Contained vs Integrated: Which architecture is correct?
   - Claude Code standalone vs external integration
   - What are the real operational limits of Claude Code currently?

2. Essential Components for Workflow Stability
   - Among items recommended by Scenario/Operator/Sustainability, which are structurally essential?
   - If the pipeline breaks, everything else is meaningless.

3. Components Retained Despite Structural Constraints
   - Items that must never be omitted for workflow stability

Conclusion (Architecture-First PRD):
- Mandatory components (structural stability conditions): [Top 5]
- Conditional components: [Top 5]
- Items that must never be omitted: [Concrete]
- Items safe to defer: [Concrete]
```

### Branch 2.B: Scenario Coverage Priority Discussion

```
You are the Moderator prioritizing use scenario coverage above all else.

Guidelines:
- Drive discussion centered on Scenario Explorer findings
- Core question: "Does this configuration cover the core use scenarios?"

PHASE 1 Input:
[Attach conclusions from 8 Branches here]

Discussion Sequence:
1. Which scenarios must be supported first?
   - High-frequency scenarios vs high-value scenarios
   - Is it feasible to cover all scenarios?

2. Essential Components for Scenario Coverage
   - Among items recommended by Workflow/Operator/Sustainability, which are essential for coverage?
   - If core scenarios cannot run, the harness is useless.

3. Components Retained Despite Structural Constraints
   - Items that must never be omitted for scenario coverage

Conclusion (Coverage-First PRD):
- Mandatory components (coverage conditions): [Top 5]
- Conditional components: [Top 5]
- Items that must never be omitted: [Concrete]
- Items safe to defer: [Concrete]
```

### Branch 2.C: Operator Experience Priority Discussion

```
You are the Moderator prioritizing the human operator's experience above all else.

Guidelines:
- Drive discussion centered on Operator Analyst findings
- Core question: "Can the user realistically configure and operate this?"

PHASE 1 Input:
[Attach conclusions from 8 Branches here]

Discussion Sequence:
1. Power Users vs General Users: Who comes first?
   - Users accepting complex setups vs users demanding instant operation
   - Can both be satisfied?

2. Essential Components for Operability
   - Among items recommended by Workflow/Scenario/Sustainability, which can users actually operate?
   - If configuration is too difficult, nobody will adopt it.

3. Components Retained Despite Structural Constraints
   - Items that must never be omitted for user experience

Conclusion (Operability-First PRD):
- Mandatory components (operability conditions): [Top 5]
- Conditional components: [Top 5]
- Items that must never be omitted: [Concrete]
- Items safe to defer: [Concrete]
```

### Branch 2.D: Sustainability Priority Discussion

```
You are the Moderator prioritizing long-term sustainability and operational efficiency above all else.

Guidelines:
- Drive discussion centered on Sustainability Strategist findings
- Core question: "Is this architecture sustainable to operate 6 months from now?"

PHASE 1 Input:
[Attach conclusions from 8 Branches here]

Discussion Sequence:
1. Token Efficiency vs Capability Scope: What is the correct balance?
   - Feature richness vs token burn
   - What is realistic within subscription quotas?

2. Essential Components for Sustainability
   - Among items recommended by Workflow/Scenario/Operator, which are sustainable?
   - If maintenance burden cancels out automation benefits, the project fails.

3. Components Retained Despite Structural Constraints
   - Items that must never be omitted for long-term viability

Conclusion (Sustainability-First PRD):
- Mandatory components (sustainability conditions): [Top 5]
- Conditional components: [Top 5]
- Items that must never be omitted: [Concrete]
- Items safe to defer: [Concrete]
```

### Comparative Analysis of Branches

Once all 4 Branch discussions conclude:

```
## PRD Comparison Matrix Across 4 Perspectives

| Component | Workflow PRD | Scenario PRD | Operator PRD | Sustainability PRD | Consensus |
|-----------|-------------|-------------|-------------|-------------------|-----------|
| Component A | ✓ (Mandatory) | ✓ (Mandatory) | ✓ (Viable) | ✓ (Required) | 4/4 ✅ |
| Component B | ✓ (Mandatory) | ✓ (Mandatory) | △ (Complex) | ✓ (Required) | 3.5/4 |
| Component C | ✓ (Mandatory) | △ (Optional) | ✗ (Too complex) | ✓ (Required) | 2.5/4 |
| Component D | △ (Optional) | ✓ (Mandatory) | ✓ (Viable) | △ (Optional) | 2.5/4 |
| Component E | ✗ (Unnecessary) | △ (Optional) | ✓ (Viable) | △ (Optional) | 1.5/4 |

### Pattern Analysis:
- 4/4 Agreement: [Components] → Green Zone (Absolute Must-Have)
- 3/4 Agreement: [Components] → Yellow Zone (Conditional Inclusion)
- ≤ 2 Agreement: [Components] → Red Zone (Deferred)

### Decision Points:
1. Emphasized by Workflow but opposed by Operator: [__]
   → Which takes precedence: structural stability or user accessibility?
2. Emphasized by Scenario but opposed by Sustainability: [__]
   → Which takes precedence: scenario coverage or token efficiency?
3. Opposed exclusively by Operator: [__]
   → Can configuration complexity be reduced?
4. Opposed exclusively by Sustainability: [__]
   → Can token burn be optimized?
```

---

## PHASE 2: Automated Discussion Execution (Claude Code Moderator)

### Moderator Prompt (Automated Execution)

```
You are an AI moderator conducting a structured automated debate across the findings of 4 domain experts.

## Research Findings to Date

### Workflow Architect Conclusion:
[Attach Teammate 1 final conclusion here]

### Scenario Explorer Conclusion:
[Attach Teammate 2 final conclusion here]

### Operator Analyst Conclusion:
[Attach Teammate 3 final conclusion here]

### Sustainability Strategist Conclusion:
[Attach Teammate 4 final conclusion here]

---

## Your Mission: Drive Structured Debate

### STEP 1: Overlap Analysis

Question: "Which components and priorities are championed by all 4 perspectives?"

Analyze along these lines:
- Components placed in TOP 3 by all teams?
- Capabilities agreed to be currently impossible via Claude Code?
- Success metrics agreed upon by all?

**Format:**
```
✅ Full Consensus Items:
1. [Component]: Workflow [Agree], Scenario [Agree], Operator [Agree], Sustainability [Agree]
2. [Component]: ...

⚠️ Partial Consensus (3 Agree):
1. [Component]: Workflow [Agree], Scenario [Agree], Operator [Disagree], Sustainability [Agree]
   → Operator Concern: [Concrete]
```

### STEP 2: Conflict Mapping

Question: "Where do perspectives collide?"

Examine the following 4 conflict archetypes:

**Pattern 1: "Structurally Necessary" vs "Humanly Tolerable"**
- Components emphasized by Workflow where Operator fears complexity?
- Rationale: [Operator perspective]
- Resolution: [Compromise proposal]

**Pattern 2: "Necessary for Coverage" vs "Sustainable"**
- Components emphasized by Scenario where Sustainability fears token/maintenance drag?
- Rationale: [Sustainability perspective]
- Resolution: [Optimization options?]

**Pattern 3: "Ideal Workflow Structure" vs "Practical Operability"**
- Workflow's ideal architecture vs Operator's realistic execution limits
- Can we simplify or abstract it away?
- Action: [Concrete next steps]

**Pattern 4: "Feature Scope" vs "Efficiency"**
- Covering more scenarios vs conserving tokens and maintenance overhead
- Priority: [Which comes first?]

### STEP 3: Prioritization ("What Must We Omit?")

To each team:
- "What are your Top 3 absolute MUST-HAVEs?"
- "What are your Top 3 items that CAN WAIT?"

**Format:**
```
MUST HAVE (Harness cannot function without these):
- Workflow: [1. __ 2. __ 3. __]
- Scenario: [1. __ 2. __ 3. __]
- Operator: [1. __ 2. __ 3. __]
- Sustainability: [1. __ 2. __ 3. __]

CAN WAIT (Safe to defer):
- Workflow: [1. __ 2. __ 3. __]
- Scenario: [1. __ 2. __ 3. __]
- Operator: [1. __ 2. __ 3. __]
- Sustainability: [1. __ 2. __ 3. __]
```

### STEP 4: Riskiest Assumptions TOP 5

Question: "What are the 5 most dangerous assumptions underlying our plan?"

From each angle:
- Workflow: "If this assumption fails, the pipeline itself collapses"
- Scenario: "If this assumption fails, core scenarios cannot execute"
- Operator: "If this assumption fails, users will abandon setup"
- Sustainability: "If this assumption fails, token budgets burn out within a month"

**Format:**
```
Riskiest Assumptions TOP 5:

1️⃣ [Assumption]: "What if [X] is false?"
   Impact: [High / Medium / Low]
   Probability: [High / Medium / Low]
   Verification Method: [How to confirm empirically?]
   Contingency Plan: [Action if assumption is invalidated]
   Risk Owner: [Which perspective monitors this?]

2️⃣ ...
```

### STEP 5: Final Convergence

**Moderator Final Synthesis:**

```
Consensus PRD Direction:

## GREEN ZONE (All Agree, Core Components)
- Component A: [Rationale] Workflow✓ Scenario✓ Operator✓ Sustainability✓
- Component B: [Rationale] Workflow✓ Scenario✓ Operator✓ Sustainability✓
- Component C: [Rationale] Workflow✓ Scenario✓ Operator✓ Sustainability✓

## YELLOW ZONE (Conditional Inclusion)
- Component D: [Condition: Included if __]
  Workflow: [View] / Scenario: [View] / Operator: [View] / Sustainability: [View]

## RED ZONE (Deferred)
- Component E: [Reason for deferral]
  Re-evaluation Criteria: [When? Triggered by what signal?]

## Top-Priority Verifications (In Follow-up Deep Dives)
1. Verify [Risky Assumption 1]: [Method]
2. Verify [Risky Assumption 2]: [Method]
3. Verify [Risky Assumption 3]: [Method]
```

---

## PHASE 3: Fork-Based Scenario Convergence (3 Automation Levels)

### Overview: Preparing for Final Architectural Decisions

Equipped with PHASE 2's debate findings, evaluate 3 distinct automation levels simultaneously:

```
[4 Perspective PRDs + Branch Comparison]
       ↓
[PHASE 3: Convergence]
  ├─ /fork Branch 3.A: Deep Automation
  │   (High automation, higher complexity, maximum automated scope)
  │
  ├─ /fork Branch 3.B: Selective Automation
  │   (Core automated, balanced, intentional manual intervention gates)
  │
  └─ /fork Branch 3.C: Minimal Automation
      (Minimal automation, maximum stability, lowest maintenance)
       ↓
[Primary PRD Draft per Scenario + Follow-up Research Items]
```

### Branch 3.A: Deep Automation (High Automation)

```
You are a decision-maker expanding automation scope to the fullest extent.

Philosophy: "Automate everything automatable. Minimize human intervention."

Guidelines:
- Construct the most comprehensive automated PRD from PHASE 2 findings
- Incorporate full multi-agent orchestration
- Accept high design complexity and maintenance overhead
- Continually ask: "What happens if this becomes unmaintainable?"

PRD Composition:
1. Core Components (Universally agreed upon)
   - [Top 5 components]

2. Advanced Automation Components (Complex but high ROI)
   - [Top 2-3 components]
   - Implementation complexity: [High]
   - Failure scenario: [Manual fallback plan]

3. Acknowledged Structural Complexity
   - Components causing setup complexity: [Concrete]
   - Anticipated maintenance drag: [Very High]
   - "How long will this hold?": [Concrete assessment]

4. Risk Mitigations
   - Top 3 dangerous assumptions: [Concrete]
   - Countermeasures for each: [Concrete]

Conclusion (Deep Automation PRD):
- Total components: [Top 8-10]
- Expected stability: [Moderate]
- Maintenance overhead: [Very High]
- When to select this path:
  [Workflows execute at extreme frequency]
  [Users readily tolerate high setup complexity]
  [Automation benefits overwhelmingly surpass maintenance costs]

## Follow-up Research Items (4 Categories)

### Technical Verification Required
- [Unverified technical assumptions underpinning this scenario]
- e.g., "Do Claude Code Hooks reliably support this degree of complex branching?"
- PRD decision jeopardized if unverified: [Concrete]

### External Integration Verification Required
- [Integration feasibility and bounds with external systems/APIs]
- e.g., "Is real-time bi-directional communication with MCP servers stable locally?"
- PRD decision jeopardized if unverified: [Concrete]

### User Behavior Hypothesis Verification Required
- [Assumed user behavior patterns]
- e.g., "Will users genuinely manage 10+ Hooks directly?"
- PRD decision jeopardized if unverified: [Concrete]

### Structural Risk Exploration Required
- [Failure modes, bottlenecks, and scaling ceilings unique to this scenario]
- e.g., "Does context window consumption rate remain practical during multi-Teammate runs?"
- PRD decision jeopardized if unverified: [Concrete]
```

### Branch 3.B: Selective Automation (Selective Automation)

```
You are a decision-maker automating the core while retaining human checkpoints.

Philosophy: "Automate high-value, repetitive tasks; leave judgment calls to humans."

Guidelines:
- Construct a PRD where all 4 perspectives find solid consensus
- Balance design complexity against stability
- Selectively incorporate vetted Yellow Zone items
- Continually ask: "Can a user easily recover manually if this fails?"

PRD Composition:
1. Core Components (All 4 perspectives agree)
   - [Top 5 components]
   - Implementation certainty: [Very High]

2. Conditional Components (3 agree, 1 cautions)
   - [Top 2-3 components]
   - Inclusion criteria: [Concrete: "Include once X is verified"]
   - Implementation complexity: [Moderate]

3. Manual Intervention Gate Design
   - Deliberately unautomated stages: [Concrete, why left manual?]
   - Benefits of manual gates: [Quality control, flexibility]
   - Promotion criteria: [Conditions required to automate later]

4. Realistic Risk Mitigation
   - Top 3 dangerous assumptions: [Concrete]
   - Countermeasures for each: [Concrete]

Conclusion (Selective Automation PRD):
- Total components: [Top 6-8]
- Expected stability: [High]
- Maintenance overhead: [Moderate]
- When to select this path:
  [Seeking balance between automation ROI and maintenance burden]
  [Planning incremental expansion]
  [Requiring quality control through human checkpoints]

## Follow-up Research Items (4 Categories)

### Technical Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### External Integration Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### User Behavior Hypothesis Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### Structural Risk Exploration Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]
```

### Branch 3.C: Minimal Automation (Minimal Automation)

```
You are a decision-maker prioritizing stability and simplicity above all.

Philosophy: "Start with single-task automation. Expand incrementally after validation."

Guidelines:
- Construct a PRD containing only what is absolutely certain
- Minimize maintenance overhead; maximize operational reliability
- Launch with Green Zone items only
- Continually ask: "Once this works, what should be added next?"

PRD Composition:
1. Absolute Essential Components (Green Zone only)
   - [Top 3-4 components]
   - Implementation certainty: [Near 100%]
   - Does this constitute a functional minimal harness?: YES

2. Deferred Components
   - Confirmed future additions: [Top 5]
   - Promotion timeline: [Post-validation, concrete criteria]

3. Simple Architecture
   - Configuration design: [Minimal CLAUDE.md + core Hooks only]
   - Complexity: [Low]
   - Debugging ease: [High]

4. Minimal Risk Exposure
   - Critical risks to avoid: [Concrete]
   - Mitigation: [Verification-first]

Conclusion (Minimal Automation PRD):
- Total components: [Top 3-4]
- Expected stability: [Very High]
- Maintenance overhead: [Low]
- When to select this path:
  [Workflow uncertainties are high]
  [Need to confirm basic operation first]
  [Want to minimize maintenance overhead]
  [Prefer phased complexity escalation]

## Follow-up Research Items (4 Categories)

### Technical Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### External Integration Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### User Behavior Hypothesis Verification Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]

### Structural Risk Exploration Required
- [Concrete item]
- PRD decision jeopardized if unverified: [Concrete]
```

### Comparative Analysis of 3 Scenarios

```
## Decision Evaluation Matrix

| Criterion | Deep Automation | Selective Automation | Minimal Automation |
|-----------|----------------|---------------------|-------------------|
| Component Count | 8-10 | 6-8 | 3-4 |
| Design Complexity | Very High | Moderate | Low |
| Maintenance Overhead | Very High | Moderate | Low |
| Stability | Moderate | High | Very High |
| Automation Scope | Maximum | Core only | Minimal |
| User Intervention | Minimal | Core checkpoints only | Frequent |
| Expansion Plan | Maintain & optimize | Incremental additions | Phased scaling |

## Selection Logic:

What is your situation?
1. "Repetitive tasks are extreme and automation benefits dominate?" → Deep Automation
2. "Automate the core, preserve flexibility elsewhere?" → Selective Automation
3. "Start small, validate, then scale?" → Minimal Automation

## Cross-Analysis of Follow-up Research Items:

Items appearing across all 3 scenarios:
- [Common items — must be verified regardless of chosen path]

Scenario-specific items:
- Deep Automation only: [Items]
- Selective Automation only: [Items]
- Minimal Automation only: [Items]
```

---

## PHASE 4: Integration — Primary PRD Draft + Follow-up Deep Dive Execution Plan

### Decision Process

```
You have received 3 Scenarios.

Current Mission:
1. Grasp the core nature of each Scenario
2. Select the Scenario fitting our context
3. Document rationale for selection
4. Finalize Primary PRD Draft
5. Produce Follow-up Deep Dive Execution Plan

---

## STEP 1: Review 3 Scenarios

Conditions for selecting Deep Automation:
- [ ] Workflow repetition frequency is exceptionally high
- [ ] Users readily accept high setup complexity
- [ ] Automation gains overwhelmingly surpass maintenance overhead
- [ ] Ample initial time budget is secured

→ Check 3 or more: Choose Deep Automation

Conditions for selecting Selective Automation:
- [ ] Core task automation delivers high value
- [ ] Specific points genuinely require human judgment
- [ ] Want to maintain maintenance overhead at a balanced level
- [ ] Planning phased expansion

→ Check 3 or more: Choose Selective Automation

Conditions for selecting Minimal Automation:
- [ ] High workflow uncertainty
- [ ] Prioritize verifying basic operation first
- [ ] Must minimize maintenance burden
- [ ] Prefer step-by-step expansion

→ Check 3 or more: Choose Minimal Automation

---

## STEP 2: Finalize Primary PRD Draft for Selected Scenario

Selected Scenario: [Deep / Selective / Minimal Automation]

Verification Checklist:
- [ ] Does this PRD draft sufficiently represent all 4 perspectives?
- [ ] Does this PRD draft match our operational reality?
- [ ] Is it understood that this is subject to revision following deep dives?

Primary PRD Draft:
```
# [Product Name] PRD - Primary Draft (Pre-Deep Dive)

## 1. Executive Summary
- Selected Scenario: [Deep / Selective / Minimal Automation]
- Selection Rationale: [Concrete]
- Note: This is an initial draft prior to specialized deep dives, subject to revision based on research findings.

## 2. Green Zone (Absolute Must-Have)
- Component A: [Why essential?]
- Component B: [Why essential?]
- Component C: [Why essential?]

## 3. Yellow Zone (Conditional Inclusion)
- Component D: [Inclusion condition]
- Component E: [Inclusion condition]

## 4. Red Zone (Deferred)
- Component F: [Promotion criteria & timeline]
- Component G: [Promotion criteria & timeline]

## 5. Riskiest Assumptions TOP 5
1. [Assumption]: Verification [Concrete], Mitigation [Concrete]
2. ...

## 6. Team Sign-Off
- Workflow Architect: [Agreed / Concerns]
- Scenario Explorer: [Agreed / Concerns]
- Operator Analyst: [Agreed / Concerns]
- Sustainability Strategist: [Agreed / Concerns]
```

---

## STEP 3: Final Verification (Signatures of 4 Teammates)

To each Teammate:

```
"From your domain perspective, do you endorse this Primary PRD Draft?"

Standards:
- "Agreed" = Core perspective is fully incorporated
- "Accepted" = Not flawless, but realistic and workable
- "Concerned" = Perspective is insufficiently reflected

Detail your evaluation and rationale.
```

Final Signatures:
```
✅ Workflow Architect: [Agreed / Accepted / Concerned] Rationale: [Concrete]
✅ Scenario Explorer: [Agreed / Accepted / Concerned] Rationale: [Concrete]
✅ Operator Analyst: [Agreed / Accepted / Concerned] Rationale: [Concrete]
✅ Sustainability Strategist: [Agreed / Accepted / Concerned] Rationale: [Concrete]

Result Assessment:
- 4 Agreed: Ideal (Extremely robust primary draft)
- 4 Accepted: Realistic (Actionable primary draft)
- ≥ 1 Concerned: Caution (Verify that concerns are captured in follow-up research agenda)
```

---

## STEP 4: Produce Follow-up Deep Dive Execution Plan

This is the primary deliverable of this framework. By consolidating Phase 3's 4-category items and the parking lot inventory, generate a comprehensive, deduplicated roadmap for subsequent deep dives.

```
## Follow-up Deep Dive Execution Plan

### 1. Technical Verification Deep Dive

| Rank | Verification Item | PRD Decision Jeopardized if Unverified | Verification Method | Source |
|------|-------------------|---------------------------------------|---------------------|--------|
| 1 | [Item] | [Decision impacted?] | [Method] | Phase 3 / Parking Lot |
| 2 | [Item] | [Decision impacted?] | [Method] | |
| ... | | | | |

### 2. External Integration Verification Deep Dive

| Rank | Verification Item | PRD Decision Jeopardized if Unverified | Verification Method | Source |
|------|-------------------|---------------------------------------|---------------------|--------|
| 1 | [Item] | [Decision impacted?] | [Method] | |
| ... | | | | |

### 3. User Behavior Hypothesis Verification Deep Dive

| Rank | Verification Item | PRD Decision Jeopardized if Unverified | Verification Method | Source |
|------|-------------------|---------------------------------------|---------------------|--------|
| 1 | [Item] | [Decision impacted?] | [Method] | |
| ... | | | | |

### 4. Structural Risk Exploration Deep Dive

| Rank | Verification Item | PRD Decision Jeopardized if Unverified | Verification Method | Source |
|------|-------------------|---------------------------------------|---------------------|--------|
| 1 | [Item] | [Decision impacted?] | [Method] | |
| ... | | | | |

### 5. Execution Sequence for Deep Dives

Recommended sequence and rationale:
1. [First category to execute] — Rationale: [Why first?]
2. [Second] — Rationale: [Why second?]
3. [Third] — Rationale: [Why third?]
4. [Fourth] — Rationale: [Why fourth?]

### 6. Integration Criteria for Final PRD Post-Deep Dives

Following deep dives, the following elements of the Primary PRD Draft may be modified:
- Conditions for adding/removing Green Zone components: [Concrete]
- Criteria for promoting Yellow Zone → Green Zone: [Concrete]
- Criteria for demoting Yellow Zone → Red Zone: [Concrete]
- Scenario alteration triggers: [Which research results would necessitate switching scenarios?]
```

---

## Final Deliverables (What You Receive)

1. **Primary PRD Draft** (Green + Yellow + Red Zones specified, explicitly marked "Pre-Deep Dive Draft")
2. **Follow-up Deep Dive Execution Plan** (4 categories × prioritized inventories)
3. **Conflict Log** (Why components were selected vs omitted)
4. **Risk Register** (Top 5 riskiest assumptions and empirical verification plans)
5. **Team Alignment Document** (Signatures across all Teammates)
6. **Consolidated Parking Lot Inventory** (Out-of-scope discoveries classified into research categories)

---

## How to Execute

### Claude Code Teammates - Fork-Based Parallel Execution

```
In workflow.md:

## PHASE 1: Parallel Execution of 8 Investigation Branches
/create_teammate "Workflow-AssumptionA" [Workflow Architect Branch A]
/create_teammate "Workflow-AssumptionB" [Workflow Architect Branch B]
/create_teammate "Scenario-AssumptionA" [Scenario Explorer Branch A]
/create_teammate "Scenario-AssumptionB" [Scenario Explorer Branch B]
/create_teammate "Operator-PowerUser" [Operator Analyst Branch A]
/create_teammate "Operator-GeneralUser" [Operator Analyst Branch B]
/create_teammate "Sustain-AssumptionA" [Sustainability Strategist Branch A]
/create_teammate "Sustain-AssumptionB" [Sustainability Strategist Branch B]

/run_parallel all

## PHASE 2: Parallel Execution of 4 Discussion Branches
/create_teammate "Discussion-Workflow" [Branch 2.A: Workflow Architecture Priority]
/create_teammate "Discussion-Scenario" [Branch 2.B: Scenario Coverage Priority]
/create_teammate "Discussion-Operator" [Branch 2.C: Operator Experience Priority]
/create_teammate "Discussion-Sustain" [Branch 2.D: Sustainability Priority]

/run_parallel all

## PHASE 3: Parallel Execution of 3 Scenario Branches
/create_teammate "Scenario-Deep" [Branch 3.A: Deep Automation]
/create_teammate "Scenario-Selective" [Branch 3.B: Selective Automation]
/create_teammate "Scenario-Minimal" [Branch 3.C: Minimal Automation]

/run_parallel all

## PHASE 4: Final Integration
/run_moderator [Final Integration & Decision Prompt]
  → Comparative Analysis of 3 Scenarios
  → Finalize Primary PRD Draft
  → Produce Follow-up Deep Dive Execution Plan
```

Or **Sequential Execution (Under Resource Constraints)**:

```
1. Run PHASE 1 (8 Branches) → Synthesize findings → Consolidate parking lot
2. Run PHASE 2 (4 Branches) → Synthesize findings → Consolidate parking lot
3. Run PHASE 3 (3 Branches) → Synthesize findings → Output follow-up research items
4. Run PHASE 4 (Final Integration) → Primary PRD Draft + Follow-up Deep Dive Execution Plan
```

---

## Tips & Best Practices

### Operating the Branch Strategy Effectively

**PHASE 1 (Investigation Branches) Operational Tips**
- Each Branch must be **completely independent** (never inspect findings of other branches)
- Keep the **two opposing assumptions** on the chosen axis explicitly defined
- Attach **concrete evidence** (Claude Code official docs, execution tests, real cases) to all conclusions
- Identify "components agreed upon by all branches" (those represent true essentials)
- **Actively utilize the parking lot** — capture out-of-scope discoveries rather than discarding them

**PHASE 2 (Discussion Branches) Operational Tips**
- Each Branch pushes a **specific perspective to its extreme** (architecture-first focuses purely on structure)
- This surfaces what happens when a given value is crowned as the top priority
- Tabulate "priority shifts per component" when comparing the 4 Branch outputs
- Discover optimal perspective blends

**PHASE 3 (Scenario Branches) Operational Tips**
- Deep, Selective, Minimal represent **philosophical choices regarding automation**, not merely scale
- Clearly demonstrate where each path leads 6 months down the road
- **Mandatorily output 4-category follow-up research items** — these form the input to subsequent phases
- Clarify selection criteria (execution frequency, user skill, token budget, expansion roadmaps)

**PHASE 4 (Final Integration) Operational Tips**
- Do not pick a "winner" among the 3 scenarios; select the one **matching our operational reality**
- Document the rationale: "Why was this scenario chosen over alternatives?"
- **The follow-up deep dive execution plan is the primary deliverable** — without it, the final PRD cannot be reached
- Explicitly designate the Primary PRD Draft as "Pre-Deep Dive Draft" — it represents a hypothesis, not a final verdict

### General Operational Tips

During Investigation
- Demand concrete evidence from every Teammate
- For abstract claims, re-prompt: "Provide 3 concrete examples"
- Welcoming conflicting views is healthy and encouraged

During Discussion
- The Moderator must remain neutral
- If one perspective dominates, rebalance: "What does the counter-perspective say?"
- "I agree" is weak → probe deeper: "Why do you agree?"

During Convergence
- Green Zone must be **conservative** (unanimous agreement only)
- Yellow Zone must have **explicit trigger conditions** (when does it enter?)
- Red Zone must state **re-evaluation milestones** (when is it reconsidered?)
