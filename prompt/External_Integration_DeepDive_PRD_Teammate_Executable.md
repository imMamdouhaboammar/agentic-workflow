# External Integration Deep-Dive Framework
## Targeted In-Depth Research on External Integration Technologies — Local Agentic Workflow Harness

---

> **Purpose of this Document**: Conduct an independent, in-depth investigation into **how a local agentic workflow harness integrates with external systems, tools, and services**. Alongside primary PRD research, technology deep dives, coding deep dives, and other specialized investigations, this produces research deliverables to be integrated into the final PRD.

---

## Initial Setup (User Input)

**Research Target**: [e.g., "External integration architecture for Claude Code workflow harness"]
**Topic**: [e.g., "MCP server ecosystem utilization and local tool integration strategies"]
**Core Integration Areas**: [e.g., "MCP servers, local CLI tools, external APIs, data flow, integration reliability"]

### Reference Context (Attach results from other deep dives if available)

**Primary PRD Research Results** (if available): [Attach if available]
**Technology Deep Dive Results** (if available): [Attach if available]
**Coding Deep Dive Results** (if available): [Attach if available]

> Even without reference context, this document can be executed independently. If other deep dive results exist, the research scope can be defined with greater precision.

---

## Fork-Based Sessions Branch Strategy

This framework leverages the `/fork` feature to **explore multiple external integration pathways simultaneously**.

### Strategy Overview

```
Initial Setup
  ↓
[PHASE 1: External Integration Deep Dive - 10 Branches in Parallel]
  ├─ /fork Branch 1.1: MCP Server Specialist (Rich MCP Ecosystem Utilization)
  ├─ /fork Branch 1.2: MCP Server Specialist (Minimal MCP, Custom Server-Centric)
  ├─ /fork Branch 2.1: Local Tool Integration Expert (Heavy Local Tooling Utilization)
  ├─ /fork Branch 2.2: Local Tool Integration Expert (Light Local Tooling Dependency)
  ├─ /fork Branch 3.1: API & Service Connector (Cloud/External Service Integration)
  ├─ /fork Branch 3.2: API & Service Connector (Fully Local/Offline Operation)
  ├─ /fork Branch 4.1: Data Flow Architect (Real-Time Streaming Data Exchange)
  ├─ /fork Branch 4.2: Data Flow Architect (Batch File Exchange)
  ├─ /fork Branch 5.1: Reliability & Fallback Engineer (Fail-Fast Strategy)
  └─ /fork Branch 5.2: Reliability & Fallback Engineer (Graceful Degradation Strategy)
  ↓
[PHASE 2: Integration Discussion]
  ├─ /fork Branch 2.A: Functional Scope Maximization Priority Discussion
  ├─ /fork Branch 2.B: Integration Stability Priority Discussion
  ├─ /fork Branch 2.C: Configuration Simplicity Priority Discussion
  └─ /fork Branch 2.D: Self-Containment/Independence Priority Discussion
  ↓
[PHASE 3: Integration Scenarios]
  ├─ /fork Branch 3.A: Full Integration (Maximum Integration, Maximum Capability, Maximum Complexity)
  ├─ /fork Branch 3.B: Selective Integration (Core Integrations Only, Balanced)
  └─ /fork Branch 3.C: Self-Contained (Minimal External Dependencies, Maximum Independence)
  ↓
[PHASE 4: Integration of Research Findings]
  → External Integration Deep Dive Comprehensive Report
  → Integration Configuration Reference
  → Findings Requiring Further Investigation
```

### Purpose of Using Branches

**Branches in Investigation Phase**
- Verify that complexity, stability, and dependency profiles diverge completely depending on integration approach
- Example: "Utilize existing MCP servers" vs "Develop custom MCP servers" → identical objective, yet drastically different cost and flexibility curves
- Concretely compare pros and cons of each approach via specific configuration examples
- Capture out-of-scope discoveries during exploration in the parking lot

**Branches in Discussion Phase**
- Verify how configurations vary based on which integration philosophy is prioritized
- Trace pathways of "Maximizing Capability" vs "Stability" vs "Simplicity" vs "Self-Containment"
- Discern the cost-benefit balance of each path

**Branches in Scenario Phase**
- Simultaneously evaluate 3 architectural configurations based on integration depth
- Compare functional breadth, runtime reliability, and operational maintenance overhead across scenarios

---

## Constraints

**Investigation Phase Constraints**
- Each Teammate is **prohibited from making baseless integration recommendations** — real connection validation or official documentation citations are mandatory
- Explicitly evaluate **actual connectivity feasibility, stability, and configuration complexity** for each integration candidate
- Any conclusion stating "this integration is not viable" must specify **exact technical constraints** (unsupported protocol, authentication barriers, etc.)
- Each Teammate must remain uninfluenced by other perspectives (maintain analytical independence)
- **Parking Lot Rule**: Discoveries exceeding the current branch scope must be logged in the parking lot

**Discussion Phase Constraints**
- Focus discussions on **comparing integration configurations**
- Claims of "it looks good" are prohibited → concrete empirical data such as reliability metrics, setup step counts, and failure frequencies are required
- If a specific integration approach is championed 3 consecutive times, explicitly provide an opportunity for alternative approaches to speak

**Scenario Phase Constraints**
- Full Integration: Include all viable external integrations
- Selective Integration: Core integrations only, replacing remainder with Claude Code built-in features
- Self-Contained: Minimize external dependencies, operational offline
- Explicitly specify **external dependency count, configuration complexity, failure points, and recovery strategies** for each scenario

---

## Success Points

### Phase 1 (Integration Investigation) Success Points

✅ **Is each Teammate's integration analysis concrete?**
- [ ] Are step-by-step connection procedures detailed for each integration candidate?
- [ ] Are stability, setup complexity, and maintenance overhead evaluated?
- [ ] Is real-world operation verified in a local environment (Claude Code Max)?

✅ **Do the 10 Branches present meaningful integration alternatives?**
- [ ] Do conclusions between opposing branches conflict constructively? (Lack of conflict indicates superficial analysis)
- [ ] Are multi-dimensional evaluations conducted covering capability scope, stability, complexity, and independence?

✅ **Are integration failure scenarios analyzed?**
- [ ] Are failure modes identified for each integration point?
- [ ] Is the blast radius on the overall workflow analyzed if a failure occurs?
- [ ] Are recovery and fallback strategies concrete?

### Phase 2 (Discussion) Success Points

✅ **Are trade-offs between integration approaches clear?**
- [ ] Captured at least 3 distinct conflicts between integration methodologies
- [ ] Specific differences (configuration steps, failure rates, MTTR) articulated for each conflict

✅ **Are areas of consensus clearly delineated?**
- [ ] Identified integration configurations agreed upon by all 4 perspectives

### Phase 3 (Scenarios) Success Points

✅ **Are the 3 integration scenarios realistically differentiated?**
- [ ] Do scenarios differ in external dependency count, configuration complexity, and failure points?
- [ ] Are concrete integration configurations specified for each scenario?

### Phase 4 (Integration) Success Points

✅ **Does the comprehensive report serve as a meaningful reference for drafting the final PRD?**
- [ ] Is the integration configuration reference directly usable in actual system architecture?
- [ ] Are discovered integration limits and opportunities clearly organized?
- [ ] Are discoveries requiring further research documented?

---

## Final Review Checklist

```
Investigation Phase:
[ ] Does each Branch present step-by-step connection procedures for integration targets?
[ ] Are stability, configuration complexity, and maintenance overhead evaluated?
[ ] Are integration failure scenarios and recovery strategies analyzed?
[ ] Has real-world operation in Claude Code local environment been verified?

Discussion Phase:
[ ] Are at least 3 trade-offs between integration approaches explicitly specified?
[ ] Are concrete differences (configuration steps, failure frequency, recovery time) compared?

Scenario Phase:
[ ] Do the 3 scenarios present distinct integration configurations?
[ ] Are external dependency count, configuration complexity, and failure points compared across scenarios?

Final:
[ ] Is the comprehensive report meaningful when read alongside other deep dive findings?
[ ] Is the integration configuration reference directly usable in actual design?
[ ] Are new integration limits and possibilities discovered during research organized?
```

---

## PHASE 1: External Integration Deep Dive (Fork-Based Parallel Exploration)

### Parallel Execution of 2 Branches per Team

Each Teammate simultaneously explores **two conflicting approaches** within their integration domain.

---

#### **MCP Server Specialist - 2 Branches**

**Branch 1.1: Rich MCP Ecosystem (Rich MCP Ecosystem Utilization)**

```
You are an expert maximizing workflow capabilities by leveraging the existing MCP server ecosystem.

Perspective: "Composing pre-built MCP servers enables rapid construction of powerful integrations."

Analysis Content:

1. Survey of Current MCP Server Ecosystem
   - Currently available MCP server types: [Filesystem, database, web search, Git, browser, etc.]
   - Maturity of each server: [Stable / Experimental / Early-stage]
   - Claude Code compatibility for each server: [Full / Partial / Unverified]
   - Officially supported vs community-provided: [Classification]

2. Workflow-Specific MCP Server Architecture Design
   - Research workflow: [Which MCP server combination?]
   - Coding workflow: [Which MCP server combination?]
   - Document generation workflow: [Which MCP server combination?]
   - Setup procedures for each combination: [Concrete steps]

3. MCP Server Integration Reliability Evaluation
   - Connection stability: [Evaluation per server]
   - Response latency: [Evaluation per server]
   - Error handling: [How does each server return errors?]
   - Concurrent connection limit: [How many servers can run stably?]

4. Configuration and Management
   - MCP configuration file structure: [Where and in what format?]
   - Server version management: [Update strategy]
   - Inter-server conflicts: [Are there any? How to resolve?]

Conclusion:
- Recommended MCP server combinations: [Top 3 combinations]
- Strengths of rich MCP utilization: [3 concrete points]
- Risks of rich MCP utilization: [Quality variance, dependency management, configuration complexity]
- Verified working servers vs theoretically possible servers: [Classification]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 1.2: Minimal MCP, Custom Servers (Minimal MCP, Custom Server-Centric)**

```
You are an expert using essential MCP servers only and developing custom servers when needed.

Perspective: "Reducing external dependencies and building only what is needed maximizes control."

Analysis Content:

1. Identifying Irreplaceable MCP Servers
   - Integrations irreplaceable by Claude Code built-in features: [Concrete list]
   - Most stable MCP server for each: [Select 1 candidate per integration]
   - Minimal MCP footprint: [Total count?]

2. Custom MCP Server Development Analysis
   - Custom server development difficulty: [MCP SDK learning curve, implementation time]
   - Benefits of custom servers: [Tailored functionality, direct error control]
   - Costs of custom servers: [Development & maintenance burden]
   - Implementation example: [Minimal custom MCP server structure]

3. Bypass Patterns Without MCP
   - Integrations replaceable via shell scripts: [Concrete]
   - Integrations replaceable via Hooks: [Concrete]
   - Integrations replaceable via file-based data exchange: [Concrete]

Conclusion:
- Minimal essential MCP servers list: [Concrete]
- Cases where custom servers are required: [Concrete]
- Strengths of minimal MCP: [Low dependency footprint, high control]
- Limitations of minimal MCP: [Development overhead, functional constraints]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 1.1 vs 1.2 Comparison)**

```
MCP Strategy Selection:
- Rich ecosystem: [Rapid setup, broad capabilities, risk of quality variance]
- Minimal + custom: [High control, development burden, precise fit]

Suitable Strategy per Workflow Type:
- Workflows requiring diverse external data: [Which?]
- Workflows centered on internal file manipulation: [Which?]
- Is a hybrid approach viable?: [Custom servers for core, existing servers for auxiliary]

Technical Limits and Possibilities Discovered:
- [Concrete findings]
```

---

#### **Local Tool Integration Expert - 2 Branches**

**Branch 2.1: Heavy Local Tooling (Heavy Local Tooling Utilization)**

```
You are an expert augmenting workflows by proactively utilizing local CLI tools, scripts, and system utilities.

Perspective: "Local tools are fast, reliable, and integrate naturally with Claude Code."

Analysis Content:

1. Survey of Usable Local Tools
   - Development tools: [Git, linter, formatter, test runner, etc.]
   - File processing tools: [jq, yq, sed, awk, pandoc, etc.]
   - System tools: [cron, watchman, fswatch, etc.]
   - Data tools: [sqlite, csvkit, etc.]
   - Invocation method within Claude Code: [Bash tool? Hooks?]

2. Tool Composition Patterns
   - Pipeline pattern: [Output of tool A piped into input of tool B]
   - Watcher pattern: [File change detection → automated execution]
   - Verification pattern: [Validate deliverables via external tools]
   - Implementation examples: [Concrete commands / scripts for 2-3 patterns]

3. Tool Lifecycle Management
   - Installation dependencies: [Which tools require pre-installation?]
   - Version compatibility: [OS variations, version discrepancies]
   - Portability: [What breaks when migrating across environments?]

Conclusion:
- Strengths of heavy local tooling: [Speed, reliability, offline capability]
- Risks of heavy local tooling: [Environment dependency, installation burden, portability]
- Recommended tool combination: [Top 5]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 2.2: Light Local Tooling (Light Local Tooling Dependency)**

```
You are an expert minimizing local tool dependencies and relying on Claude Code built-in capabilities.

Perspective: "Fewer external tools mean simpler configuration and superior portability."

Analysis Content:

1. Capabilities Replaceable by Claude Code Built-in Features
   - File read/write: [Are built-in features sufficient?]
   - Code execution: [Is built-in Bash sufficient?]
   - Search / analysis: [Are built-in features sufficient?]

2. Minimal Essential Local Tools
   - Absolutely irreplaceable tools: [Concrete list, rationale]
   - Installation methods: [Is one-command installation feasible?]

3. Bypass Patterns Without External Tools
   - Direct handling by Claude Code: [Which tasks?]
   - Replacement via prompting: [Which tasks?]
   - Hard limits: [Tasks strictly impossible without tools]

Conclusion:
- Strengths of minimal tooling: [Simple setup, high portability]
- Limitations of minimal tooling: [Functional constraints, performance limits]
- Absolute essential tools list: [Concrete]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 2.1 vs 2.2 Comparison)**

```
Local Tool Strategy Selection:
- Heavy utilization: [Rich capabilities, environment dependencies, installation management required]
- Light dependency: [Simple setup, excellent portability, functional constraints]

Technical Limits and Possibilities Discovered:
- [Concrete findings]
```

---

#### **API & Service Connector - 2 Branches**

**Branch 3.1: Cloud/External Service (Cloud & External Service Integration)**

```
You are an expert expanding workflow capabilities by integrating external APIs and cloud services.

Perspective: "Leveraging external services unlocks capabilities impossible to execute purely locally."

Analysis Content:

1. Survey of Integrable External Services
   - Web search APIs: [Usable services, authentication methods, pricing]
   - Database services: [Cloud databases, connection methods]
   - Storage services: [S3, GCS, etc., connection methods]
   - AI/ML APIs: [Secondary LLMs, specialized AI services]
   - Productivity APIs: [Notion, Slack, Google Workspace, etc.]

2. External API Invocation Methods from Claude Code
   - Invocation via MCP server: [Patterns]
   - Invocation via shell scripts (curl / httpie): [Patterns]
   - Automated invocation via Hooks: [Patterns]
   - Pros and cons of each method: [Comparison]

3. Authentication & Security Management
   - API key storage: [Environment variables? .env? Secret managers?]
   - Key leakage prevention: [Security within Claude Code context]
   - Token renewal: [Is automated renewal viable for OAuth, etc.?]

4. Cost & Quota Management
   - API invocation cost tracking: [Methodology]
   - Rate limit mitigation: [Queuing, backoff, caching]
   - Estimated API cost per workflow run: [Projections]

Conclusion:
- Strengths of external service integration: [Enables capabilities impossible locally]
- Risks of external service integration: [Cost, network dependency, service outages]
- Recommended integration architecture: [Top 3]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 3.2: Fully Local/Offline (Fully Local / Offline Operation)**

```
You are an expert designing workflows operating entirely locally without external network dependencies.

Perspective: "Eliminating network dependencies guarantees robust operation anywhere."

Analysis Content:

1. Offline Operational Scope Analysis
   - Does Claude Code itself require network?: [API call structure analysis]
   - Capabilities operational offline: [Concrete]
   - Capabilities non-operational offline: [Concrete, reasons]

2. Local Substitution Strategies
   - Web search → Local document / SQLite search: [Method]
   - Cloud storage → Local filesystem: [Method]
   - External APIs → Local tools / scripts: [Method]

3. Pre-fetching & Caching Strategy
   - Pre-downloading required data: [What to pre-fetch? Where to store?]
   - Cache lifecycle: [Refresh intervals, storage limits]
   - Offline mode toggling: [Automatic detection? Manual switch?]

Conclusion:
- Strengths of fully local operation: [Network independence, airtight security, zero latency]
- Limitations of fully local operation: [Functional bounds, data staleness]
- Realistically achievable scope with local-only operation: [Concrete]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 3.1 vs 3.2 Comparison)**

```
Network Dependency Selection:
- Cloud integration: [Broad capability, network-dependent, recurring costs]
- Fully local: [High independence, functional constraints, zero costs]
- Hybrid: [Expands when online, falls back to core when offline]

Technical Limits and Possibilities Discovered:
- [Concrete findings]
```

---

#### **Data Flow Architect - 2 Branches**

**Branch 4.1: Real-Time Streaming (Real-Time Data Exchange)**

```
You are an expert designing real-time data flow between Claude Code and external systems.

Perspective: "Real-time data exchange maximizes workflow responsiveness."

Analysis Content:

1. Real-Time Data Exchange Patterns
   - Streaming via MCP servers: [Feasible? Method?]
   - File watching (watch/fswatch) real-time reaction: [Patterns, tooling]
   - Pipe (stdin/stdout) stream processing: [Feasible?]

2. Data Formats and Serialization
   - JSON streaming: [NDJSON, JSON Lines]
   - Structured logging: [Formats, parsing]
   - Binary data handling: [Images, PDFs, etc.]

3. Reliability of Real-Time Streams
   - Risk of data loss: [Present? Mitigation?]
   - Ordering guarantees: [Guaranteed? Method?]
   - Backpressure (load shedding): [Present? Method?]

Conclusion:
- Strengths of real-time exchange: [High responsiveness, fresh data]
- Risks of real-time exchange: [Complexity, instability, packet/data drop]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 4.2: Batch File Exchange (Batch File Exchange)**

```
You are an expert designing reliable integration through file-based batch data exchange.

Perspective: "File exchange is simple, transparent, easy to debug, and reproducible."

Analysis Content:

1. Batch File Exchange Patterns
   - Input directory → Processing → Output directory: [Pattern]
   - State files tracking operational progress: [Pattern]
   - Completion marker files (flag files): [Pattern]

2. Data Format Standardization
   - JSON files: [Schema definition, validation]
   - YAML files: [Use cases, pros and cons]
   - Markdown files: [Document deliverables]
   - Directory hierarchy rules: [Naming conventions, structure]

3. Reliability of Batch Exchange
   - Atomic writes: [Temp file write → atomic move pattern]
   - Idempotency / deduplication: [Execution completion markers]
   - File locking: [Necessary? Method?]

Conclusion:
- Strengths of batch exchange: [Simple, transparent, easily debugged, reproducible]
- Limitations of batch exchange: [Latency, filesystem growth, lack of real-time reactivity]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 4.1 vs 4.2 Comparison)**

```
Data Exchange Strategy Selection:
- Real-time: [Rapid response, high complexity, stability risks]
- Batch: [Simple, robust, higher latency]
- Hybrid: [Real-time for core signals, batch for data payloads]

Technical Limits and Possibilities Discovered:
- [Concrete findings]
```

---

#### **Reliability & Fallback Engineer - 2 Branches**

**Branch 5.1: Fail-Fast Strategy (Fail-Fast Strategy)**

```
You are an expert in strategies that halt immediately upon integration failure and notify the user.

Perspective: "Catching and resolving an error immediately is far superior to producing corrupt deliverables."

Analysis Content:

1. Failure Detection Mechanisms
   - MCP server connection failure detection: [Method, timeout settings]
   - API invocation failure detection: [HTTP status codes, response validation]
   - Local tool execution failure detection: [Exit codes, stderr]
   - Data integrity failure detection: [Schema validation, checksums]

2. Immediate Halt Patterns
   - Error logging: [What diagnostics are preserved?]
   - User notification: [How alerted?]
   - Workflow state preservation: [Checkpointing at halt point]
   - Implementation example: [Concrete fail-fast code structure]

3. Resume Strategy
   - Resuming from failure point: [Method]
   - Full re-run: [When required?]
   - Resuming post-human intervention: [Pattern]

Conclusion:
- Strengths of fail-fast: [Rapid issue detection, prevents data corruption]
- Limitations of fail-fast: [Frequent interruptions, higher human operational friction]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Branch 5.2: Graceful Degradation (Graceful Degradation Strategy)**

```
You are an expert in strategies that scale back features and keep workflows progressing when integrations fail.

Perspective: "Even if a component fails, the remaining workflow must continue executing."

Analysis Content:

1. Fallback Strategies per Integration
   - On MCP server failure: [Alternative method? Fallback to local CLI?]
   - On API call failure: [Use cached data? Skip non-essential step?]
   - On local tool failure: [Fallback to Claude Code built-in logic?]
   - Quality penalty per fallback: [Concrete evaluation]

2. Fallback Chain Design
   - Primary attempt → Secondary fallback → Tertiary minimal baseline: [Pattern]
   - Capability reduction scope per stage: [What is omitted?]
   - Notifying user of degraded state: [Method]
   - Implementation example: [Concrete fallback chain structure]

3. Recovery Strategy
   - Automated restoration when integration recovers: [Feasible? Method?]
   - Quality flagging on deliverables produced in degraded mode: [Method]
   - Retroactive completion of missing items: [Feasible? Pattern?]

Conclusion:
- Strengths of graceful degradation: [Continuous execution, partial deliverable generation]
- Limitations of graceful degradation: [Implementation complexity, quality control challenge]

🅿️ Parking Lot: [Out-of-scope discoveries]
```

**Final Synthesis (Branch 5.1 vs 5.2 Comparison)**

```
Failure Handling Selection:
- Fail-fast: [Prioritizes correctness, accepts frequent stops]
- Graceful degradation: [Prioritizes continuity, accepts partial quality degradation]
- Hybrid: [Fail-fast on core data integrations, graceful degradation on auxiliary services]

Technical Limits and Possibilities Discovered:
- [Concrete findings]
```

---

### Synthesis of Branch Findings (Integrated Analysis of 10 Branches)

```
## Comprehensive External Integration Research Report

### Step 1: Integration Approach Spectrum per Domain

MCP Server:       Rich Ecosystem ←────────→ Minimal + Custom   [Our position: __]
Local Tools:      Heavy Tooling  ←────────→ Light Dependency   [Our position: __]
API & Service:    Cloud Connect  ←────────→ Fully Local        [Our position: __]
Data Flow:        Real-Time      ←────────→ Batch              [Our position: __]
Reliability:      Fail-Fast      ←────────→ Graceful           [Our position: __]

### Step 2: Integration Configurations Agreed Upon by All Branches
- [Universally recommended integrations]: [Concrete]
- [Universally deemed essential]: [Concrete]
- [Universally advised to avoid]: [Concrete]

### Step 3: Maximum Discrepancies Between Branches
- Discrepancy #1: [Between which branches, root cause, resolution approach]
- Discrepancy #2: ...

### Step 4: Synthesis of Integration Limits and Opportunities Discovered
- Easier than expected: [Concrete]
- Harder than expected: [Concrete]
- Currently impossible: [Concrete, reasons]
- Unexpected possibilities: [Concrete]

### Step 5: Parking Lot Consolidation
- Findings requiring further investigation: [List, categorized]
```

---

## PHASE 2: Discussion by Integration Perspective (4 Discussion Branches)

### Branch 2.A: Functional Scope Maximization Priority Discussion

```
Question: "How powerful does the workflow become when leveraging all viable external integrations?"

Conclusion (Capability-First PRD):
- Recommended integration setup: [Include all high-value integrations]
- External dependency count: [Maximum]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.B: Integration Stability Priority Discussion

```
Question: "Which integration configuration operates with the highest stability?"

Conclusion (Stability-First PRD):
- Recommended integration setup: [Battle-tested integrations only]
- Failure point count: [Minimum]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.C: Configuration Simplicity Priority Discussion

```
Question: "Which integration setup is easiest to configure and maintain?"

Conclusion (Simplicity-First PRD):
- Recommended integration setup: [Minimum configuration steps]
- Operational maintenance burden: [Minimum]
- Pros and cons of this configuration: [Concrete]
```

### Branch 2.D: Self-Containment/Independence Priority Discussion

```
Question: "How powerful a workflow can we build without external dependencies?"

Conclusion (Independence-First PRD):
- Recommended integration setup: [Minimal external dependencies]
- Offline operational scope: [Concrete]
- Pros and cons of this configuration: [Concrete]
```

### Synthesis of 4 Discussion Branches

```
| Integration Target | Capability First | Stability First | Simplicity First | Independence First | Consensus |
|--------------------|------------------|-----------------|------------------|---------------------|-----------|
| Integration A | ✓ | ✓ | ✓ | ✓ | 4/4 ✅ |
| ... | | | | | |

Decision Points:
1. Integrations where capability conflicts with stability: [__]
2. Integrations where simplicity conflicts with capability: [__]
3. Integrations where independence conflicts with capability: [__]
```

---

## PHASE 3: Integration Scenarios (3 Integration Levels)

### Branch 3.A: Full Integration (Maximum Integration)

```
Philosophy: "Harness every viable external integration to achieve maximum capability."

Integration Configuration:
- MCP Servers: [Multiple, broad ecosystem utilization]
- Local Tools: [Heavy tooling, comprehensive tool chains]
- External APIs: [Proactive cloud service connections]
- Data Flow: [Hybrid real-time + batch]
- Failure Handling: [Graceful degradation + fail-fast on critical core]

Complexity Analysis:
- External dependency count: [High]
- Configuration complexity: [High]
- Failure points: [Many]
- Maintenance burden: [High]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]
```

### Branch 3.B: Selective Integration (Core Integrations Only)

```
Philosophy: "Include core high-leverage integrations only; handle remainder natively."

Integration Configuration:
- MCP Servers: [Core 2-3 servers only]
- Local Tools: [Essential utilities only]
- External APIs: [Strictly unavoidable services only]
- Data Flow: [Primarily batch file exchange]
- Failure Handling: [Fail-fast + clear recovery path]

Complexity Analysis:
- External dependency count: [Low]
- Configuration complexity: [Moderate]
- Failure points: [Few]
- Maintenance burden: [Moderate]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]
```

### Branch 3.C: Self-Contained (Minimal External Dependencies)

```
Philosophy: "Drastically reduce external dependencies to operate with extreme self-reliance."

Integration Configuration:
- MCP Servers: [None or 1 essential server]
- Local Tools: [Bare minimum essential tools]
- External APIs: [None]
- Data Flow: [File-based only]
- Failure Handling: [Fail-fast (virtually no external points to fail)]

Complexity Analysis:
- External dependency count: [Near zero]
- Configuration complexity: [Low]
- Failure points: [Near zero]
- Maintenance burden: [Low]

Advantages of this Scenario:
- [3 concrete points]

Risks of this Scenario:
- [3 concrete points]

Conditions for Selecting this Scenario:
- [Concrete conditions]

Functional Limitation Catalog:
- Tasks impossible without external integrations: [Concrete]
- Future expansion roadmap when adding integrations: [Concrete]
```

### Comparative Analysis of 3 Scenarios

```
| Criterion | Full Integration | Selective Integration | Self-Contained |
|-----------|------------------|-----------------------|----------------|
| External Dependencies | Many | Few | Near zero |
| Configuration Complexity | High | Moderate | Low |
| Functional Scope | Maximum | Core only | Minimal |
| Failure Points | Many | Few | Near zero |
| Maintenance Burden | High | Moderate | Low |
| Offline Operation | Restricted | Partially viable | Mostly viable |
| Portability | Low | Moderate | High |

Selection Logic:
1. "Maximum capability required, operational overhead acceptable" → Full Integration
2. "Lock down the core, solve remaining needs natively" → Selective Integration
3. "Minimize dependencies, prioritize self-reliant stability" → Self-Contained
```

---

## PHASE 4: Integration of Findings — Comprehensive Report

```
You have received 3 integration scenarios and 10 Branch analyses.

Current Mission:
1. Compare the core nature of each scenario
2. Synthesize comprehensive research findings
3. Compile integration configuration references
4. Organize findings requiring further investigation

---

## STEP 1: Synthesis of Comprehensive Research Findings

### Overall Technical Assessment for External Integration

Recommended approaches across 5 domains:
- MCP Server: [Rich ecosystem / Minimal + custom / Hybrid — Reason]
- Local Tools: [Heavy tooling / Light dependency / Hybrid — Reason]
- API & Service: [Cloud connect / Fully local / Hybrid — Reason]
- Data Flow: [Real-time / Batch / Hybrid — Reason]
- Reliability: [Fail-fast / Graceful degradation / Hybrid — Reason]

### Core Findings Discovered During Research

Easier than expected:
- [Concrete item] — Reason: [__]

Harder than expected:
- [Concrete item] — Reason: [__]

Currently impossible:
- [Concrete item] — Reason: [__]

Unexpected possibilities:
- [Concrete item] — Reason: [__]

---

## STEP 2: Integration Configuration Reference

Organize concrete integration configurations directly referenceable during actual design.

### Reference 1: MCP Server Configuration
- Recommended MCP server list: [Server name, purpose, reliability rating]
- Setup instructions: [Concrete steps]
- Custom server development guide: [If applicable]

### Reference 2: Local Tools Configuration
- Essential tools inventory: [Tool name, purpose, installation method]
- Tool composition patterns: [Concrete examples]

### Reference 3: External API Integration Configuration
- Integration targets: [Service name, purpose, authentication method]
- Invocation patterns: [Concrete examples]
- Cost and quota management strategies: [Concrete]

### Reference 4: Data Exchange Configuration
- Data format standards: [JSON schema, YAML conventions, etc.]
- Directory hierarchy conventions: [Concrete]
- Exchange patterns: [Concrete examples]

### Reference 5: Failure Handling Configuration
- Failure modes per integration: [Catalog]
- Fallback chains: [Concrete structure]
- Recovery procedures: [Step-by-step]

---

## STEP 3: Findings Requiring Further Investigation

| Discovery Item | Discovered by Branch | Why Further Investigation Is Required |
|----------------|----------------------|---------------------------------------|
| [Item 1] | [Branch __] | [Reason] |
| [Item 2] | [Branch __] | [Reason] |
| ... | | |

---

## STEP 4: Team Sign-Off

To each Teammate:

"From your domain perspective, are these research findings thorough, sound, and realistic?"

Final Signatures:
✅ MCP Server Specialist: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Local Tool Integration Expert: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ API & Service Connector: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Data Flow Architect: [Thorough / Partial / Inadequate] Rationale: [Concrete]
✅ Reliability & Fallback Engineer: [Thorough / Partial / Inadequate] Rationale: [Concrete]
```

---

## Final Deliverables (What You Receive)

1. **External Integration Deep Dive Comprehensive Report** — Integration analysis across 5 domains, discovered limits and opportunities, core determinations
2. **Integration Configuration Reference** — Concrete architectural specifications for MCP servers, local tools, external APIs, data exchange, and fallback chains
3. **Comparison of 3 Integration Scenarios** — Configurations, complexity, pros and cons of Full Integration / Selective Integration / Self-Contained
4. **Findings Requiring Further Investigation** — Matters not fully resolved in this research
5. **Team Sign-Off Document**

→ These deliverables will be integrated into the final PRD alongside primary PRD research, technology deep dives, coding deep dives, and other specialized investigations.

---

## How to Execute

### Claude Code Teammates - Fork-Based Parallel Execution (10 Branches)

```
In workflow.md:

## PHASE 1: Parallel Execution of 10 Integration Investigation Branches
/create_teammate "MCP-RichEcosystem" [Branch 1.1]
/create_teammate "MCP-MinimalCustom" [Branch 1.2]
/create_teammate "LocalTool-Heavy" [Branch 2.1]
/create_teammate "LocalTool-Light" [Branch 2.2]
/create_teammate "API-CloudService" [Branch 3.1]
/create_teammate "API-FullyLocal" [Branch 3.2]
/create_teammate "DataFlow-Realtime" [Branch 4.1]
/create_teammate "DataFlow-Batch" [Branch 4.2]
/create_teammate "Reliability-FailFast" [Branch 5.1]
/create_teammate "Reliability-Graceful" [Branch 5.2]

/run_parallel all

## PHASE 2: Parallel Execution of 4 Discussion Branches
/create_teammate "Discussion-MaxCapability" [Branch 2.A]
/create_teammate "Discussion-Stability" [Branch 2.B]
/create_teammate "Discussion-Simplicity" [Branch 2.C]
/create_teammate "Discussion-Independence" [Branch 2.D]

/run_parallel all

## PHASE 3: Parallel Execution of 3 Scenario Branches
/create_teammate "Integration-Full" [Branch 3.A]
/create_teammate "Integration-Selective" [Branch 3.B]
/create_teammate "Integration-SelfContained" [Branch 3.C]

/run_parallel all

## PHASE 4: Final Integration
/run_moderator [Research findings integration + comprehensive report drafting prompt]
```

Or **Sequential Execution**:

```
1. PHASE 1 (10 Branches) → Organize findings → Consolidate parking lot
2. PHASE 2 (4 Branches) → Organize findings
3. PHASE 3 (3 Branches) → Compare scenarios
4. PHASE 4 (Final Integration) → Comprehensive report + Integration configuration reference
```

---

## Tips & Best Practices

**PHASE 1 (Investigation Branches) Operational Tips**
- Each Branch must run **completely independently** (do not inspect other branches)
- Ground findings in **actual connectivity test results** — documentation claims often diverge from runtime behavior
- Clearly distinguish between **officially supported MCP servers and community implementations**
- **Security considerations**: Always define explicit management strategies for API keys, tokens, and sensitive credentials
- **Actively utilize the parking lot** — record out-of-scope discoveries

**PHASE 2 (Discussion Branches) Operational Tips**
- Quantitatively evaluate **external dependency count, setup steps, and failure point count** when comparing configurations
- Continually ask "Is this integration strictly necessary?" — unneeded integrations only inflate operational complexity

**PHASE 3 (Scenario Branches) Operational Tips**
- Full, Selective, and Self-Contained represent a **philosophical choice regarding external dependency**
- Always define the **offline operational scope** for each scenario — network reliability cannot be assumed
- The Self-Contained scenario must include a **future roadmap for incrementally adding integrations**

**PHASE 4 (Final Integration) Operational Tips**
- **The integration configuration reference is the most crucial deliverable** — MCP server lists, setup commands, and fallback chains must be immediately usable in actual design
- Frankly document discovered integration limits — clearly differentiate between "stated in documentation" vs "verified in actual execution"
- Clearly articulate areas requiring additional research
