# Technology & Development Deep-Dive Framework
## Targeted In-Depth Research on Related Technologies — Local Agentic Workflow Harness

---

> **Purpose of this Document**: Conduct an independent, in-depth investigation into **related technologies for a local agentic workflow harness**. Alongside primary PRD research, coding deep dives, and other specialized investigations, this produces research deliverables to be integrated into the final PRD.

## Initial Setup (User Input)

**Research Target**: [e.g., "Claude Code Max-based agentic workflow harness"]
**Topic**: [e.g., "CLAUDE.md configuration strategy and Hooks architecture design"]
**Core Technology Areas**: [e.g., "configuration architecture, context management, multi-agent orchestration"]

### Reference Context (Attach results from other deep dives if available)

**Primary PRD Research Results** (if available): [Attach if available]
**Other Deep Dive Results** (if available): [Attach if available]

> Even without reference context, this document can be executed independently. If other deep dive results exist, the research scope can be defined with greater precision.

---

## Fork-Based Sessions Branch Strategy (Extended Feature)

This framework leverages the `/fork` feature to **explore multiple paths of technology and implementation know-how simultaneously**.
This secures a deep and solid foundation for technical choices.

### Strategy Overview

```
Initial Setup
  ↓
[PHASE 1: Technology Deep Dive - 10 Branches in Parallel]
  ├─ /fork Branch 1.1: Platform Capability Researcher (Maximum Utilization Perspective)
  ├─ /fork Branch 1.2: Platform Capability Researcher (Limitation-Aware Perspective)
  ├─ /fork Branch 2.1: Configuration Architect (Minimal Configuration Design)
  ├─ /fork Branch 2.2: Configuration Architect (Precision Configuration Design)
  ├─ /fork Branch 3.1: Orchestration Engineer (Lightweight Orchestration)
  ├─ /fork Branch 3.2: Orchestration Engineer (Advanced Orchestration)
  ├─ /fork Branch 4.1: Integration Specialist (Minimal Integration)
  ├─ /fork Branch 4.2: Integration Specialist (Active Integration)
  ├─ /fork Branch 5.1: Theory Foundation Expert (Modern Agentic Theory Foundation)
  └─ /fork Branch 5.2: Theory Foundation Expert (Established Automation Principles Foundation)
  ↓
[PHASE 2: Technology Discussion]
  ├─ /fork Branch 2.A: Platform Capability Maximization Priority Discussion
  ├─ /fork Branch 2.B: Stability/Predictability Priority Discussion
  ├─ /fork Branch 2.C: Implementation Speed Priority Discussion
  └─ /fork Branch 2.D: Maintainability/Extensibility Priority Discussion
  ↓
[PHASE 3: Technology Implementation Scenarios]
  ├─ /fork Branch 3.A: Experimental (Cutting-Edge Techniques, High Potential, High Risk)
  ├─ /fork Branch 3.B: Pragmatic (Balance of Proven + Experimental)
  └─ /fork Branch 3.C: Established (Proven Patterns Only, Low Risk)
  ↓
[PHASE 4: Integration of Research Findings]
  → Technology Deep Dive Comprehensive Report
  → Technical Configuration Reference
  → Findings Requiring Further Investigation
```

### Purpose of Using Branches

**Branches in Investigation Phase**
- Acknowledge that multiple approaches are viable even within the same technological domain
- Example: "Maximize Claude Code Hooks utilization" vs "Recognize Hooks limitations and bypass them"
- Explicitly verify the advantages and trade-offs of each approach
- Capture out-of-scope discoveries during exploration in the parking lot

**Branches in Discussion Phase**
- Verify how conclusions diverge based on which technical philosophy is prioritized
- Trace pathways of "Platform Maximization" vs "Stability" vs "Implementation Speed" vs "Maintainability"
- Discern the technical cost-benefit balance for each path

**Branches in Scenario Phase**
- Simultaneously evaluate 3 implementation pathways: Experimental vs Balanced vs Proven techniques
- Concretely compare technical pros/cons, complexity, and stability across scenarios

---

## Constraints

Maintain the following constraints while running this research process:

**Investigation Phase Constraints**
- Each Teammate is **prohibited from making baseless technology recommendations** (hype alone is insufficient)
- Present **at least 3 actual working examples or official documentation citations** supporting each technology or technique
- Any conclusion stating "this technology is not viable" must specify **exact technical constraint points** (missing APIs, unsupported capabilities)
- Each Teammate must remain uninfluenced by other perspectives (maintain technical objectivity)
- **Theory Foundation Expert must explicitly cite theoretical foundations**:
  - Original authors / researchers, papers / presentations, publication year
  - Explicitly articulate the gap between theory and practical execution
- **Parking Lot Rule**: Discoveries made during investigation that exceed the current branch scope must be logged in the parking lot. Specify whether the item pertains to external integration, user behavior, or structural risk

**Discussion Phase Constraints**
- Discussions must focus strictly on the **rationale for technical selections**
- Claims of "it looks good" are prohibited → technical justification of "why it is superior" is mandatory
- If a specific technology is championed 3 consecutive times, explicitly provide an opportunity for alternative technologies to speak
- **All recommendations must be backed by actual execution tests, official documentation, or verified case studies**

**Scenario Phase Constraints**
- Experimental: **Focus on cutting-edge techniques** (emerged within last 1-2 years, active community)
- Pragmatic: **Balanced proven + experimental** (proven core foundation, experimental techniques applied only to key differentiators)
- Established: **Proven patterns only** (actively used by a broad base of practitioners)
- Explicitly detail the **implementation complexity, learning curve, and debugging difficulty** for each scenario
- Define the **concrete technical configuration** for each scenario

---

## Success Points

Criteria for determining whether this technical research process was **successful**:

### Phase 1 (Technical Investigation) Success Points

✅ **Is each Teammate's technical analysis deep and rigorous?**
- [ ] Rather than mere enumeration, are **concrete pros and cons** of each technology/technique specified?
- [ ] Is evidence clear? (Actual execution results, official documentation, verified case studies)
- [ ] Is there a **feasibility evaluation** tailored to our environment (local computer, Claude Code Max)?

✅ **Do the 10 Branches present technically meaningful alternatives?**
- [ ] Do conclusions between opposing branches **conflict** constructively? (Absence of conflict indicates superficial analysis)
- [ ] Are **multi-faceted evaluations** conducted covering learning curve, stability, scalability, token efficiency, etc.?

✅ **Is the theoretical foundation solid? (Theory Foundation Expert Evaluation)**
- [ ] **Agentic workflow design theory**: Are core principles clear?
- [ ] **Recent advancements**: What new concepts and techniques have emerged?
- [ ] **Gap between theory and practice**: Explanations such as "In theory X applies, but Claude Code reality requires Y"

✅ **Are technical limitations and possibilities clearly mapped?**
- [ ] Are elements that are easier vs harder than expected differentiated?
- [ ] Are currently impossible items cataloged with specific reasons?

### Phase 2 (Technical Discussion) Success Points

✅ **Are trade-offs between technologies clearly articulated?**
- [ ] Captured at least 3 distinct **technical conflicts**
- [ ] Concrete comparative evaluations performed for each conflict

✅ **Are areas of consensus clearly delineated?**
- [ ] Identified technologies and techniques that **all 4 perspectives agree upon**
- [ ] Can the combination of those consensus technologies form a **fully functional harness**?

### Phase 3 (Scenarios) Success Points

✅ **Are the 3 technical scenarios realistically differentiated?**
- [ ] Do scenarios differ in implementation complexity, learning curve, and debugging difficulty?
- [ ] Are technical pros and cons concretely compared across scenarios?

✅ **Does each scenario have a concrete technical configuration?**
- [ ] CLAUDE.md structure, Hooks design, context management strategies all defined
- [ ] Does each configuration appear **genuinely viable in practice**?

### Phase 4 (Integration) Success Points

✅ **Does the comprehensive report serve as a meaningful reference for drafting the final PRD?**
- [ ] Is the technical configuration reference directly usable for actual system design?
- [ ] Are discovered technical limitations and opportunities clearly synthesized?
- [ ] Are discoveries requiring further research documented?

---

## Final Review Checklist

Verify these criteria upon completion of the technical research:

```
Investigation Phase:
[ ] Does each Branch's technical analysis cite 3+ concrete sources (test results / docs / cases)?
[ ] Does each Branch advocate distinct technologies or techniques? (Confirm creative conflict)
[ ] Is execution feasibility evaluated in a local environment (Claude Code Max)?
[ ] Are evaluations grounded in Claude Code platform actual features and constraints?

Discussion Phase:
[ ] Are at least 3 technical trade-offs explicitly specified?
[ ] Are real-world use cases and failure modes included?
[ ] Are there technologies/techniques agreed upon by all 4 perspectives?

Scenario Phase:
[ ] Are technical configurations distinctly different across the 3 scenarios?
[ ] Are technical pros and cons concretely compared across scenarios?
[ ] Is the depth sufficient for an implementer to immediately make an architectural decision?

Final:
[ ] Is the comprehensive report meaningful when read alongside other deep dive findings?
[ ] Is the technical configuration reference directly usable in actual architecture design?
[ ] Are new technical limitations and possibilities discovered during research organized?
```

---

## PHASE 1: Technical Deep Dive (Fork-Based Parallel Exploration)

### Investigation Structure: Parallel Execution of 2 Branches per Team

Each Teammate simultaneously explores **two conflicting approaches** within their technical domain.

#### **Platform Capability Researcher - 2 Branches**

**Branch 1.1: Maximum Utilization (Maximize Platform Capabilities)**

```
You are a technical analyst operating from the perspective of maximizing Claude Code's built-in capabilities.

Perspective: "Deeply understanding built-in platform capabilities allows building a powerful harness without external dependencies."

Analysis Target: [Research Topic]

Analysis Content:

1. In-Depth Analysis of Current Claude Code Platform Features
   - Hooks system: [Event types, conditional branching, executable scope]
   - Teammate / Fork: [Parallel execution limits, context isolation levels, result integration methods]
   - CLAUDE.md: [Parsing rules, hierarchical support, file size limits]
   - .claude/ directory: [Configuration file types, version control, portability]
   - Session management: [Session persistence, context window management, state retention methods]

2. Verification of Actual Feature Operation
   - Stated official documentation features vs actual operational behavior: [Concrete]
   - Undocumented features / behaviors: [Are there any?]
   - Known bugs, limitations, and unstable areas: [Concrete]

3. Workflow Patterns Implementable Using Platform Features Alone
   - Simple pipeline: [Viable / Not viable]
   - Conditional branching pipeline: [Viable / Not viable]
   - Iterative / retry pipeline: [Viable / Not viable]
   - Multi-agent orchestration: [Viable / Not viable]
   - Implementation complexity of each pattern: [Low / Medium / High]

Conclusion:
- Scope coverable solely via platform: [Concrete]
- Strengths of maximum utilization: [3 concrete points]
- Limitations of maximum utilization: [Where does it hit a wall?]
- Essential technical components from this perspective: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries — specify relevant deep dive category]
```

**Branch 1.2: Limitation-Aware (Limitation-Aware Perspective)**

```
You are a technical analyst operating from the perspective of clearly identifying Claude Code limitations and engineering bypass strategies.

Perspective: "Accurately knowing platform limitations is essential for realistic architecture design."

Analysis Target: [Research Topic]

Analysis Content:

1. In-Depth Analysis of Structural Limitations of Claude Code Platform
   - Context window limits: [Size, consumption rate, recovery methods]
   - Token consumption limits: [Subscription quotas, consumption per workflow, optimization headroom]
   - Parallel execution limits: [Concurrent Teammate count, resource contention]
   - Hooks limits: [Unsupported events/conditions, execution environment constraints]
   - State management limits: [Cross-session state non-persistence, file dependency]

2. Real Impact of Each Limitation
   - In which workflow patterns does this become problematic?: [Concrete]
   - At what scale does this become problematic?: [Concrete]
   - Predictable limitations vs unpredictable limitations: [Classification]

3. Limitation Bypass Strategies
   - Context exhaustion bypass: [State file partitioning, summarization chains, etc.]
   - Token limit bypass: [Prompt optimization, batch processing, etc.]
   - Hooks limitation bypass: [External script integration, watchdog patterns, etc.]
   - Implementation complexity of each bypass strategy: [Low / Medium / High]

Conclusion:
- Most critical limitations Top 3: [Concrete]
- Bypassable limitations vs structurally insurmountable limitations: [Classification]
- Essential technical components from this perspective: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 1.1 vs 1.2 Comparison)**

```
Platform Capability Assessment:
- Maximum utilization perspective: [Feasible scope, benefits]
- Limitation-aware perspective: [Actual constraints, bypass overhead]

Realistic Questions:
- At our workflow complexity level, is the platform alone sufficient?
- Is the cost of bypassing limitations greater than the cost of integrating external tools?
- Matters to verify in follow-up research: [Concrete]
```

---

#### **Configuration Architect - 2 Branches**

**Branch 2.1: Minimal Configuration (Simple Configuration Design)**

```
You are a configuration architect designing minimal configuration for maximum impact.

Perspective: "Simpler configurations yield easier maintenance and fewer errors."

Analysis Target: [Research Topic]

Analysis Content:

1. CLAUDE.md Minimal Configuration Strategy
   - Single CLAUDE.md file structure: [Advantages, limitations]
   - Principles for including core instructions only: [What to include and what to omit?]
   - Relationship between configuration size and context consumption: [Concrete figures]

2. .claude/ Directory Minimal Design
   - Essential files only: [What is strictly required?]
   - Minimizing inter-file configuration dependencies: [Methodology]

3. Hooks Minimal Design
   - Attaching hooks to core events only: [Which events?]
   - Relationship between hook count and debugging difficulty: [Concrete]

4. Implementation Feasibility
   - Workflow scope coverable with this configuration: [Concrete]
   - Can new workflows be supported without additional configuration?: [Y/N]

Conclusion:
- Strengths of minimal configuration: [3 concrete points]
- Limitations of minimal configuration: [Where does it fall short?]
- Essential configuration components from this perspective: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 2.2: Precision Configuration (Precision Configuration Design)**

```
You are a configuration architect designing fine-tuned configurations for optimal performance.

Perspective: "Precise configuration maximizes workflow accuracy and execution efficiency."

Analysis Target: [Research Topic]

Analysis Content:

1. CLAUDE.md Hierarchical Configuration Strategy
   - Partitioning structure by project/workflow: [Design]
   - Common configuration vs workflow-specific configuration: [Separation criteria]
   - Configuration inheritance / override patterns: [Feasible? Method?]

2. .claude/ Directory Precision Design
   - Per-workflow configuration file separation: [Structure]
   - Environment-specific (dev/prod) configuration management: [Method]
   - Configuration version control: [Git integration?]

3. Hooks Precision Design
   - Multi-step conditional branching Hooks: [Feasible? Method?]
   - Hook chaining (one Hook triggering another): [Feasible?]
   - Hook execution logging and debugging: [Method]

4. Implementation Feasibility
   - Maintenance overhead of this configuration level: [Concrete]
   - Configuration workload when adding a new workflow: [Concrete]

Conclusion:
- Strengths of precision configuration: [3 concrete points]
- Risks of precision configuration: [Cost of over-configuration]
- Essential configuration components from this perspective: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 2.1 vs 2.2 Comparison)**

```
Differences in Configuration Philosophy:
- Minimal configuration: [Fast start, low maintenance, constrained precision]
- Precision configuration: [High precision, higher maintenance, longer initial setup]

Realistic Questions:
- How many workflow types are there? → 1-3 suggests minimal, 5+ suggests precision
- How frequent are configuration changes? → Frequent changes favor minimal
- Are there configuration conflicts between workflows? → Conflicts necessitate precision
```

---

#### **Orchestration Engineer - 2 Branches**

**Branch 3.1: Lightweight Orchestration (Lightweight Orchestration)**

```
You are an orchestration designer managing workflows with minimal complexity.

Perspective: "Simple pipelines are the most stable."

Analysis Content:

1. Execution Unit Design
   - Sequential execution within a single session: [Patterns, limitations]
   - Prompt chain management: [Methods, state propagation]
   - Manual restart upon failure: [Procedure]

2. State Management
   - File-based simple state storage: [JSON/YAML, structure]
   - Cross-session state passing: [Methods, limitations]
   - State file size management: [Growth rate, pruning strategy]

3. Error Handling
   - Failure detection: [How?]
   - Manual recovery vs automatic retry: [Criteria]
   - Error logging: [Method]

Conclusion:
- Scope coverable with lightweight orchestration: [Concrete]
- Limitations: [Where is manual intervention required?]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 3.2: Advanced Orchestration (Advanced Orchestration)**

```
You are an orchestration designer automatically managing complex multi-agent workflows.

Perspective: "Automated orchestration is the cornerstone of large-scale workflows."

Analysis Content:

1. Execution Unit Design
   - Multi-Teammate parallel execution: [Patterns, context isolation]
   - Fork-based branching and merging: [Methods, result synthesis]
   - Automated retry + fallback chains: [Implementation method]

2. State Management
   - Structured state machine: [Design]
   - Checkpointing / rollback: [Feasible? Method?]
   - Distributed state synchronization: [State sharing among Teammates]

3. Error Handling
   - Automated error taxonomy and response: [Patterns]
   - Automatic recovery from session expiration / context exhaustion: [Method]
   - Canary execution (small-scale probe before full execution): [Feasible?]

Conclusion:
- Benefits of advanced orchestration: [Concrete]
- Implementation complexity and maintenance overhead: [Concrete]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 3.1 vs 3.2 Comparison)**

```
Orchestration Level Selection:
- Lightweight: [Stable but requires manual intervention; ideal for simple workflows]
- Advanced: [High automation but complex to implement/debug; essential for complex workflows]

Realistic Questions:
- Is workflow failure frequency high? → High failure rate demands advanced orchestration
- Can the user handle error recovery directly? → If yes, lightweight is viable
- Is parallel execution strictly necessary? → If yes, advanced orchestration is required
```

---

#### **Integration Specialist - 2 Branches**

**Branch 4.1: Minimal Integration (Minimal Integration)**

```
You are an integration designer maximizing self-containment by minimizing external integration.

Perspective: "Fewer external dependencies produce greater operational stability."

Analysis Content:

1. External Capabilities Replaceable by Claude Code Standalone
   - Capabilities replaceable by file read/write: [Concrete]
   - Capabilities replaceable by shell scripts: [Concrete]
   - Capabilities replaceable by prompt chains: [Concrete]

2. Strictly Necessary External Integrations
   - Functions strictly requiring external tools: [Concrete, why?]
   - Reliability of each external integration: [High / Medium / Low]

3. Benefits and Limitations of Zero-Integration Setup
   - Installation and configuration simplification: [Degree]
   - Portability (migrating across environments): [Degree]
   - Functional limitations: [Where?]

Conclusion:
- Scope coverable via minimal integration: [Concrete]
- List of unavoidable external integrations: [Concrete]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 4.2: Active Integration (Active Integration)**

```
You are an integration designer expanding capabilities through proactive integration with external tools.

Perspective: "Strategic integration maximizes workflow power and capability."

Analysis Content:

1. MCP Server Integration Strategy
   - Available MCP server types: [Concrete]
   - Connection stability of each server: [High / Medium / Low]
   - Fallback strategy on connection failure: [Concrete]

2. Local Tool Integration Strategy
   - CLI tool invocation: [Which tools for what purpose?]
   - Shell script utilization: [Patterns, security considerations]
   - Data exchange via filesystem: [Patterns]

3. Integration Management Strategy
   - External dependency version management: [Method]
   - Integration failure detection + auto-recovery: [Method]
   - Integration testing: [How to verify?]

Conclusion:
- Benefits of active integration: [Concrete]
- Integration management overhead: [Concrete]
- Recommended integration architecture: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 4.1 vs 4.2 Comparison)**

```
Integration Level Selection:
- Minimal integration: [High self-containment, limited features, excellent portability]
- Active integration: [Broad capability scope, management overhead, environment dependencies]

Realistic Questions:
- Can the core workflow run without external tools?
- Does an integration failure halt the entire workflow?
- Is the MCP server stability at production level?
```

---

#### **Theory Foundation Expert - 2 Branches**

**Branch 5.1: Modern Agentic Theory (Modern Agentic Theory Foundation)**

```
You are an expert analyzing technologies grounded in modern agentic workflow theory and methodology.

Perspective: "Modern theory shapes the future of agentic workflow architecture."

Analysis Content:

1. Agentic Workflow Design Theory
   - ReAct (Reasoning + Acting) pattern: [Original authors, core principles, application methods]
   - Chain-of-Thought / Tree-of-Thought: [Principles, workflow applications]
   - Multi-agent collaboration theory: [Role differentiation, consensus mechanisms]

2. Modern Prompt Engineering Theory
   - Structured prompt design principles: [Core concepts]
   - Context window optimization theory: [Compression, summarization, selective inclusion]
   - Self-Verification patterns: [Principles, implementation]

3. Recent Advancements (Last 2 Years)
   - Novel agentic patterns: [Concrete]
   - Overcoming legacy limitations: [What has changed?]
   - Emerging limitation awareness: [What remains difficult?]

4. Theoretical Impact on Harness Design
   - Adhering to theory: [Design trajectory]
   - Neglecting theory: [Predicted pitfalls]

Conclusion:
- Robustness of theoretical foundation: [__/10]
- Implementation difficulty based on this theory: [Easy / Medium / Hard]
- Citations: [Papers / authors / publication year]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 5.2: Established Automation Theory (Established Automation Principles Foundation)**

```
You are an expert analyzing technologies grounded in decades of proven automation principles and software engineering theory.

Perspective: "Battle-tested principles provide the most reliable foundation."

Analysis Content:

1. Classical Principles of Automation Design
   - Unix philosophy: [Small tool composition, pipelines, text streams]
   - State machine design: [Finite state machines, transition conditions]
   - Idempotency principles: [Re-execution safety]
   - Failure isolation (Bulkhead) patterns: [Preventing cascade failures]

2. Classical Principles of Configuration Management
   - Infrastructure as Code: [Declarative configuration]
   - Separation of Concerns: [Configuration structuring]
   - DRY principle: [Configuration deduplication]

3. Empirical Validation of Classical Principles
   - How long have these principles been validated?
   - Do these principles translate effectively to agentic workflows?
   - Critical caveats when applying: [Concrete]

4. Relationship with Modern Agentic Techniques
   - Where classical principles remain fully valid: [Concrete]
   - Where classical principles do not map: [Concrete, why?]
   - Reconciliation approach: [Concrete]

Conclusion:
- Theoretical certainty: [__/10]
- Probability of these principles remaining valid long-term: [High]
- Citations: [Books / authors]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 5.1 vs 5.2 Comparison)**

```
Selection of Theoretical Foundations:

Modern Theory (Modern Agentic Theory):
- Benefits: [Innovative, agentic-specialized]
- Risks: [Less empirical longevity, rapid shifts]
- Suitable context: [Experimental leeway permitted, cutting-edge techniques required]

Established Theory (Battle-Tested Automation Principles):
- Benefits: [Proven, explicit principles, high stability]
- Risks: [May not address agentic-unique challenges]
- Suitable context: [Stability prioritized, predictable behavior required]

Gap Between Theory and Practice:
- "In theory X applies, but Claude Code reality requires Y"
- Compromise point: [How far to follow theory vs adapting to reality?]
```

---

### Synthesis of Branch Findings (Integrated Analysis of 10 Branches)

```
## Comprehensive Technology Research Report

### Step 1: Technology Selection Spectrum per Domain

Platform Capability:
  Maximum Utilization ←─────────────→ Limitation-Aware
  [Our position: __]
  
Configuration:
  Minimal Configuration ←─────────────→ Precision Configuration
  [Our position: __]
  
Orchestration:
  Lightweight ←─────────────→ Advanced
  [Our position: __]
  
Integration:
  Minimal Integration ←─────────────→ Active Integration
  [Our position: __]

Theory:
  Modern Agentic Theory ←─────────────→ Established Automation Principles
  [Our position: __]

### Step 2: Technologies and Techniques Agreed Upon by All Branches
- [Universally recommended]: [Concrete]
- [Universally mandatory]: [Concrete]
- [Universally agreed principles]: [Concrete]

### Step 3: Maximum Discrepancies Between Branches
- Discrepancy #1: [Between which branches, root cause, resolution approach]
- Discrepancy #2: ...

### Step 4: Parking Lot Consolidation
- Findings requiring further investigation: [List, categorized]
```

---

## PHASE 2: Discussion by Technical Perspective (Fork-Based Multi-Perspective)

### Branch 2.A: Platform Capability Maximization Priority Discussion

```
You are a discussion moderator prioritizing the maximum utilization of Claude Code platform capabilities.

Question: "How powerful a harness can we build using platform features alone?"

Receiving findings from 10 Branches in PHASE 1:

1. Maximum scope implementable via built-in platform features
2. Technical challenges solvable without external integration
3. Unavoidable external integrations caused by platform limits

Conclusion (Platform-Maximization PRD):
- Recommended technical configuration: [Maximum utilization of platform features]
- Implementation complexity: [__]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.B: Stability/Predictability Priority Discussion

```
You are a discussion moderator prioritizing stable, predictable operation.

Question: "Which technical configuration operates with the greatest stability?"

Conclusion (Stability-First PRD):
- Recommended technical configuration: [Stability first]
- Expected error rate: [Lowest]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.C: Implementation Speed Priority Discussion

```
You are a discussion moderator prioritizing the fastest path to a working harness.

Question: "Which technical configuration allows the fastest implementation?"

Conclusion (Speed-First PRD):
- Recommended technical configuration: [Implementation speed first]
- Implementation timeline: [Shortest]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.D: Maintainability/Extensibility Priority Discussion

```
You are a discussion moderator prioritizing long-term maintainability and extensibility.

Question: "Which technical configuration is easiest to maintain and expand in 6 months?"

Conclusion (Maintainability-First PRD):
- Recommended technical configuration: [Maintainability first]
- Maintenance burden in 6 months: [Lowest]
- Pros and cons of this configuration: [Concrete]
```

### Synthesis of 4 Discussion Branches

```
## Technology Selection Matrix Across 4 Perspectives

| Technology / Technique | Platform Maximization | Stability First | Speed First | Maintainability First | Consensus |
|------------------------|-----------------------|-----------------|-------------|-----------------------|-----------|
| Technique A | ✓ | ✓ | ✓ | ✓ | 4/4 ✅ |
| Technique B | ✓ | ✓ | △ | ✓ | 3.5/4 |
| ... | | | | | |

### Decision Rules:
1. 4 perspectives agree: → Top-priority inclusion
2. 3 perspectives agree: → Safe inclusion
3. 1-2 perspectives agree: → Requires rigorous review
```

---

## PHASE 3: Technical Implementation Scenarios (3 Pathways)

### Branch 3.A: Experimental (Cutting-Edge Techniques)

```
You are a technical leader proactively leveraging the latest agentic techniques.

Philosophy: "Modern techniques produce superior workflows."

Technical Configuration Design:
1. CLAUDE.md structure: [Apply latest patterns]
2. Hooks design: [Advanced conditional branching]
3. Context management: [Latest optimization techniques]
4. Orchestration: [Full multi-agent orchestration]
5. Integration: [Proactive MCP server utilization]

Conclusion:
- Implementation complexity: [High]
- Learning curve: [High]
- Potential performance: [Maximum]
- Stability risk: [High]
```

### Branch 3.B: Pragmatic (Practical Balance)

```
You are a technical leader balancing proven techniques with strategic experimentation.

Philosophy: "Experiment only on the core; rely on proven patterns for the rest."

Technical Configuration Design:
1. CLAUDE.md structure: [Proven patterns + core optimizations]
2. Hooks design: [Essential events only, stable structure]
3. Context management: [Proven methods + selective optimization]
4. Orchestration: [Selective automation]
5. Integration: [Essential integrations only]

Conclusion:
- Implementation complexity: [Moderate]
- Learning curve: [Moderate]
- Stability: [High]
- Expansion headroom: [Present]
```

### Branch 3.C: Established (Proven Patterns Only)

```
You are a technical leader relying strictly on proven patterns and principles.

Philosophy: "Begin with what is certain."

Technical Configuration Design:
1. CLAUDE.md structure: [Simple, proven structure]
2. Hooks design: [Minimal, core only]
3. Context management: [Baseline methods]
4. Orchestration: [Sequential execution-centric]
5. Integration: [Minimal or none]

Conclusion:
- Implementation complexity: [Low]
- Stability: [Very High]
- Functional scope: [Constrained]
- Expansion plan: [Phased]
```

### Comparative Analysis of 3 Scenarios

```
| Criterion | Experimental | Pragmatic | Established |
|-----------|-------------|-----------|-------------|
| Implementation Complexity | High | Moderate | Low |
| Learning Curve | High | Moderate | Low |
| Stability | Moderate | High | Very High |
| Functional Scope | Maximum | Core + α | Minimal |
| Maintenance Burden | High | Moderate | Low |
| Extension Headroom | Pre-extended | Extensible | Phased expansion needed |

Selection Logic:
1. "Benefits of latest techniques outweigh risks" → Experimental
2. "Experiment on core, keep remainder safe" → Pragmatic
3. "Start with what is proven" → Established
```

---

## PHASE 4: Integration of Findings — Comprehensive Report

### Decision Process

```
You have received 3 technical scenarios.

Current Mission:
1. Compare the core nature of each scenario
2. Synthesize comprehensive research findings
3. Author the technical configuration reference
4. Organize findings requiring further investigation

---

## STEP 1: Scenario Selection

Conditions for selecting Experimental:
- [ ] Workflow complexity is high enough to mandate advanced orchestration
- [ ] Users accept a steep learning curve
- [ ] Advantages of cutting-edge techniques outweigh associated risks

Conditions for selecting Pragmatic:
- [ ] High automation returns on core workflows
- [ ] Need a balance between stability and experimentation
- [ ] Phased expansion planned

Conditions for selecting Established:
- [ ] Stability is paramount
- [ ] Prioritize verifying basic operation first
- [ ] Must minimize maintenance overhead

---

## STEP 2: Technical Configuration Reference

Based on the selected scenario, compile technical configurations directly referenceable during actual design.

### Platform Utilization Configuration
- Scope of Claude Code built-in feature usage: [Concrete]
- Limitation bypass strategy: [Concrete]

### Configuration Architecture Setup
- CLAUDE.md structure: [Concrete]
- .claude/ directory design: [Concrete]
- Hooks configuration: [Concrete]

### Orchestration Setup
- Execution structure: [Concrete]
- Context management strategy: [Concrete]

### Integration Setup
- External integration scope: [Concrete]
- Integration reliability strategy: [Concrete]

### Theoretical Rationale Summary
- Theoretical foundation for this technical setup: [Concrete]
- Compromise points between theory and reality: [Concrete]

---

## STEP 3: Technical Decision Record (For Final PRD Integration)

Selected Scenario: [Experimental / Pragmatic / Established]

### Finalized Technical Configuration
- CLAUDE.md strategy: [Concrete]
- .claude/ directory structure: [Concrete]
- Hooks design: [Concrete]
- Context management strategy: [Concrete]
- Orchestration level: [Concrete]
- External integration configuration: [Concrete]

### Theoretical Rationale Summary
- Theoretical foundation of this technical setup: [Concrete]
- Compromise points between theory and reality: [Concrete]

### Findings Requiring Further Investigation

| Discovery Item | Discovered by Branch | Why Further Investigation Is Required |
|----------------|----------------------|---------------------------------------|
| [Item 1] | [Branch __] | [Reason] |
| [Item 2] | [Branch __] | [Reason] |
| ... | | |

---

## STEP 4: Team Sign-Off

To each Teammate:

"From your domain perspective, is this technical configuration realistic?"

Final Signatures:
✅ Platform Capability: [Realistic / Challenging / Unrealistic] Rationale: [Concrete]
✅ Configuration: [Realistic / Challenging / Unrealistic] Rationale: [Concrete]
✅ Orchestration: [Realistic / Challenging / Unrealistic] Rationale: [Concrete]
✅ Integration: [Realistic / Challenging / Unrealistic] Rationale: [Concrete]
✅ Theory Foundation: [Realistic / Challenging / Unrealistic] Rationale: [Concrete]
```

---

## Final Deliverables (What You Receive)

1. **Technical Deep Dive Comprehensive Report** — Technical analysis across 5 domains, discovered technical limits and possibilities, core determinations
2. **Technical Configuration Reference** — Concrete designs for platform utilization, configuration architecture, orchestration, and integration setups
3. **Technical Theory Deep Dive Report** — Comparison of modern agentic theory vs established automation principles, theory-practice gap analysis
4. **Comparison of 3 Technical Scenarios** — Configurations, complexity, pros and cons of Experimental / Pragmatic / Established
5. **Findings Requiring Further Investigation** — Matters not fully resolved in this research
6. **Team Sign-Off Document**

→ These deliverables will be integrated into the final PRD alongside primary PRD research, coding deep dives, and other specialized investigations.

---

## How to Execute

### Claude Code Teammates - Fork-Based Parallel Execution (10 Branches)

```
In workflow.md:

## PHASE 1: Parallel Execution of 10 Technology Investigation Branches
/create_teammate "Platform-MaxUtil" [Branch 1.1]
/create_teammate "Platform-LimitAware" [Branch 1.2]
/create_teammate "Config-Minimal" [Branch 2.1]
/create_teammate "Config-Precision" [Branch 2.2]
/create_teammate "Orch-Lightweight" [Branch 3.1]
/create_teammate "Orch-Advanced" [Branch 3.2]
/create_teammate "Integration-Minimal" [Branch 4.1]
/create_teammate "Integration-Active" [Branch 4.2]
/create_teammate "Theory-Modern" [Branch 5.1]
/create_teammate "Theory-Classical" [Branch 5.2]

/run_parallel all

## PHASE 2: Parallel Execution of 4 Discussion Branches
/create_teammate "Discussion-PlatformFirst" [Branch 2.A]
/create_teammate "Discussion-StabilityFirst" [Branch 2.B]
/create_teammate "Discussion-SpeedFirst" [Branch 2.C]
/create_teammate "Discussion-MaintainFirst" [Branch 2.D]

/run_parallel all

## PHASE 3: Parallel Execution of 3 Scenario Branches
/create_teammate "Scenario-Experimental" [Branch 3.A]
/create_teammate "Scenario-Pragmatic" [Branch 3.B]
/create_teammate "Scenario-Established" [Branch 3.C]

/run_parallel all

## PHASE 4: Final Integration
/run_moderator [Research findings integration + comprehensive report drafting prompt]
```

Or **Sequential Execution**:

```
1. PHASE 1 (10 Branches) → Organize findings → Consolidate parking lot
2. PHASE 2 (4 Branches) → Organize findings
3. PHASE 3 (3 Branches) → Organize findings → Compare scenarios
4. PHASE 4 (Final Integration) → Comprehensive report + Technical configuration reference
```

---

## Tips & Best Practices

### Operating the Branch Strategy Effectively

**PHASE 1 (Investigation Branches) Operational Tips**
- Each Branch must run **completely independently** (do not look at other branches)
- Technical analysis must include **concrete evidence (execution tests, official docs, verified cases)**
- Identify "technologies and techniques recommended by all branches" (truly essential technologies)
- **Actively utilize the parking lot** — log out-of-scope discoveries

**Theory Foundation Expert Branch Operational Tips**
- Theoretical analysis must present **principled rationale rather than simple exposition**
- Address both **agentic workflow-unique theories** and **battle-tested automation principles**
- Frankly acknowledge the **gap between theory and practical reality**
  - Example: "ReAct patterns are theoretically elegant, but how do they function under Claude Code's context limits?"
- **Specify citations**: Concretely list papers, authors, and publication years

**PHASE 2 (Discussion Branches) Operational Tips**
- Each Branch pushes a **specific value to its logical extreme**
- Tabulate **priority shifts per technology** when comparing 4 Branch results

**PHASE 3 (Scenario Branches) Operational Tips**
- Experimental, Pragmatic, Established represent a **choice of technical philosophy**
- Concretely compare implementation complexity, learning curve, and debugging difficulty

**PHASE 4 (Final Integration) Operational Tips**
- **The technical configuration reference is the most crucial deliverable** — it must be directly referenceable in actual system design
- Frankly articulate discovered technical limits and opportunities
- Clearly organize items requiring further investigation

### Technology Research Specific Tips

- **Prioritize actual execution tests**: Abstract claims of "it should work" are prohibited; prove with execution results
- **Ground evaluations in Claude Code official documentation**: Trust official documentation and real-world behavior over unofficial sources
- **Fit for our specific environment**: Ensure configurations fit "a single Claude Code Max subscriber operating locally", rather than enterprise team setups
- **Always factor in token efficiency**: Predict token consumption across any configuration and evaluate against subscription quotas
