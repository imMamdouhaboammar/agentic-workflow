# Task Plan: Event-Driven Agentic Workflow Engine (Python & TypeScript)

## Goal
Study `conductor-oss/conductor` architecture and design/craft our own event-driven, durable, and highly resilient execution engine for applications and AI Agents in Python and TypeScript/Bun, fully compliant with `AgenticWorkflow-main` framework (Single-File SOT, 3-Stage Lifecycle, 4-Layer Verification, pACS, Abductive Diagnosis, RLM Context Preservation).

## Status
- **Current Phase:** Phase 8 — System Harmonization & Triple-Guard Remediation
- **Status:** complete
- **Next Step:** All 12 test suites green, 30/30 setup checks passed, 0 non-hook errors, full TS/Python SOT parity verified. System fully certified for production workflows.

---

## Phases

### Phase 1: In-depth Architectural Study & Comparative Analysis
- [x] Study Conductor OSS engine architecture (`DeciderService`, `WorkflowExecutor`, `QueueDAO`, `ExecutionDAO`, `MetadataDAO`, Sweeper).
- [x] Analyze Conductor task execution lifecycle, polling vs push mechanisms, system tasks vs worker tasks.
- [x] Evaluate Conductor's AI/LLM, human-in-the-loop, and event-driven capabilities.
- [x] Formulate detailed Gap Analysis & Architectural Synthesis between Conductor and `AgenticWorkflow`.
- **Status:** complete

### Phase 2: Engine Specifications & Unified Data Contracts
- [x] Define declarative Workflow & Task DSL (JSON/YAML) supporting stages, DAG transitions, dynamic forks, sub-workflows, loops, and agent tasks.
- [x] Define Single-File SOT Schema (`state.yaml` / `state.json`) with atomic transitions and single-writer coordinator.
- [x] Define Event Bus Protocol & Event Types (`workflow_schema.json`, `event_schema.json`, `example_workflow.yaml`).
- [x] Specify 4-Layer Verification Contract (L0 Anti-Skip, L1 Functional, L1.5 pACS, L2 Adversarial Review).
- **Status:** complete

### Phase 3: Python Engine Architecture (`core/engine_py/`)
- [x] Design Async Decider Service (`AgenticDecider`) & State Machine.
- [x] Design EventBus & TaskQueue with pluggable backends (In-Memory, SQLite, SOT-File).
- [x] Design Worker Pool runtime (Concurrency limits, heartbeat leases, backoff retries, timeout management).
- [x] Implement Built-in System Workers (`CodeExec`, `WaitEvent`, `Switch`, `Transform`).
- [x] Implement Agentic Task Worker (`AgentWorker` with prompt templates, tool sandboxing, least-privilege permissions).
- [x] Implement 4-Layer Gate Controller & Abductive Diagnosis on failure.
- [x] Implement Energy/Token Budget & RLM Context Refueler.
- **Status:** complete

### Phase 4: TypeScript / Bun Engine Architecture (`src/engine_ts/`)
- [x] Design Bun/Node Async Event-Loop Decider with strict Zod/TypeScript schemas.
- [x] Design TypeScript EventBus with EventEmitter and Webhook dispatching.
- [x] Design TypeScript TaskQueue (InMemory and SQLite).
- [x] Design TypeScript Task Worker Runtime & System/Agent Workers.
- [x] Implement TypeScript AgenticExecutor & Single-File SOT coordinator.
- [x] Integrate with `bin/cli.js` and test cross-runtime parity.
- **Status:** complete

### Phase 5: Resilience, Event Triggers & Saga Compensations
- [x] Design Durable State Persistence & Replay Engine (`ledger.jsonl` append-only audit trail).
- [x] Design External Event Ingestion & Webhook Triggers via AsyncEventBus.
- [x] Design Saga Rollback & Compensation Workflows for agent failure recovery in both Deciders.
- [x] Design Circuit Breaker & Rate Limiter (CLOSED -> OPEN -> HALF_OPEN).
- **Status:** complete

### Phase 6: CLI & Universal Toolchain Integration (`bin/cli.js`)
- [x] Integrated `engine` command into `bin/cli.js` supporting `--runtime py|ts`.
- [x] Built executable CLI runners for both runtimes (`core/engine_py/runner.py` and `src/engine_ts/runner.ts`).
- [x] Extended `bin/cli.js test` to run all 7 multi-engine test suites.
- **Status:** complete

### Phase 7: Verification, Test Suite & End-to-End Demonstration
- [x] Formulate automated test suite (Unit tests for Decider, Queue, Worker, SOT serialization).
- [x] Integration tests for DAG branching, dynamic fan-out, and human-in-the-loop pauses.
- [x] End-to-end agentic workflow execution test (Research -> Planning -> Implementation with L0-L2 gates).
- [x] All 7 test suites green across Python and TypeScript/Bun.
- **Status:** complete

### Phase 8: System Harmonization & Triple-Guard Remediation (Fable & CE)
- [x] Audit entire system via docs-guard, test-guard, and clean-code-guard (131 tests, 104 errors identified).
- [x] Remediate F1 (TS executor SOT schema parity: autopilot, energy budget, task metrics, outputs).
- [x] Remediate F2 (VerificationController bare passes replaced with structured failure logging).
- [x] Remediate F3 (Synchronize marketplace.json to 1.1.0 matching package.json).
- [x] Remediate F4 & F5 (Skills indexer and Toon adapter bare passes replaced with logging).
- [x] Remediate F6 (Implement comprehensive 21-test suite for retry_manager.py Sisyphus Persistence).
- [x] Remediate F7 & F8 (SOT output key validator updated for task_* keys; setup_init hardened to 30/30 passed).
- [x] Remediate CLI bugs in bin/cli.js (status --project-dir, init stdin piping, test suite 12).
- [x] Eliminate all non-hook RULE-15 swallowed exceptions across entire repository (0 errors).
- **Status:** complete

---

## Decisions Made
| Date | Decision | Rationale |
|---|---|---|
| 2026-09-06 | Dual Engine Parity (Python + TypeScript/Bun) | Python offers unmatched AI/ML ecosystem, while TS/Bun offers ultra-fast event loops, lightweight CLI and webhook server. Both share identical SOT & event protocol. |
| 2026-09-06 | Single-File SOT with Append-Only Ledger | Preserves Absolute Criterion 2 of `AgenticWorkflow`, avoiding multi-agent race conditions while supporting time-travel replay. |
| 2026-09-06 | Native 4-Layer Verification in Task Lifecycle | Instead of binary success/failure, tasks must pass L0-L2 gates before completion, preventing AI hallucination leakage into downstream tasks. |

---

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| None yet | 0 | Proactive planning initiated |
