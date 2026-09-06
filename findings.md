# Conductor OSS Research & Custom Agentic Engine Findings

## 1. Conductor OSS (Netflix / Orkes) Architectural Breakdown

### Core Subsystems
- **DeciderService (The Brain):**
  - Pure state evaluator. Given the current workflow execution history (DAG of tasks) and workflow definition, evaluates what tasks are ready to schedule, what tasks have timed out, whether the workflow has completed, failed, or needs compensation.
  - Decoupled from execution: Decider never executes task code directly. It simply transitions task states (`SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCELED`, `SKIPPED`).
- **WorkflowExecutor (Lifecycle Coordinator):**
  - Handles external commands: `startWorkflow`, `terminateWorkflow`, `pauseWorkflow`, `resumeWorkflow`, `retryWorkflow`, `restartWorkflow`.
  - Orchestrates interactions between `ExecutionDAO`, `QueueDAO`, `MetadataDAO`, and `DeciderService`.
- **QueueDAO & Pluggable Queuing:**
  - Decoupled worker-task queue interface.
  - Supports polling with long-polling (`poll(taskType, workerId, domain, count, timeout)`), `ack`, `nack`, and lease renewal.
  - Implementations: In-memory, Redis, PostgreSQL (using `FOR UPDATE SKIP LOCKED`), MySQL, SQS, AMQP.
- **ExecutionDAO & Persistence:**
  - Persists workflow execution records, task execution records, input/output JSON payloads, and execution history.
  - Backends: Redis, PostgreSQL, MySQL, Cassandra.
- **Sweeper (Background Re-evaluator):**
  - Periodic background sweeper loop that sweeps active workflows to detect stalled tasks, expired timers, missed queue messages, or workflows needing re-evaluation.
- **Task Types:**
  - **System Tasks:** Handled internally without external worker polling:
    - `HTTP`: Makes external HTTP calls.
    - `JSON_JQ_TRANSFORM`: Evaluates jq / JSONPath transforms.
    - `SWITCH` / `DECISION`: Conditional branching.
    - `DO_WHILE`: Looping construct until condition is met.
    - `DYNAMIC_FORK`: Spawns sub-tasks dynamically based on runtime array inputs.
    - `FORK_JOIN` & `JOIN`: Parallel task fan-out and barrier synchronization.
    - `SUB_WORKFLOW`: Invokes a child workflow and waits for completion.
    - `WAIT`: Pauses execution for a duration or until external event/signal.
    - `EVENT`: Emits event to external message bus.
    - `HUMAN`: Durable pause for human review and input.
    - `LLM_CHAT_COMPLETE`, `LLM_GENERATE_EMBEDDINGS`, `LLM_SEARCH_INDEX`: Native AI system tasks.
  - **Worker Tasks (Simple Tasks):**
    - Executed by distributed external workers polling queues.

### Resilience & Durability Patterns in Conductor
- **Idempotency:** Task scheduling and execution uses unique `referenceTaskName` + iteration counts.
- **Retries & Backoff:** Tasks define `retryCount`, `retryDelaySeconds`, and `retryLogic` (`FIXED`, `LINEAR`, `EXPONENTIAL_BACKOFF`).
- **Timeouts:** 
  - `pollTimeoutSeconds`: Max time task can wait in queue before being marked timed out.
  - `responseTimeoutSeconds`: Max time worker has to update status before task is rescheduled.
  - `workflowTimeoutSeconds`: Max overall workflow duration.
- **Circuit Breaking & Rate Limiting:**
  - `rateLimitPerFrequency` & `rateLimitFrequencyInSeconds` per task definition.
  - Concurrent execution limits per task definition.
- **Compensations (Saga Pattern):**
  - Workflows can define a `failureWorkflow` that executes compensations and rollback tasks if the main workflow fails.

---

## 2. Gap Analysis: Conductor OSS vs Agentic AI Frameworks

| Capability | Conductor OSS | Modern Agentic AI Engine (Our Goal) |
|---|---|---|
| **Runtime Footprint** | Heavyweight Java/JVM backend, requires Redis + Elasticsearch / DB | Lightweight, zero-JVM, pure Python & TypeScript/Bun native, embeddable or standalone |
| **State Management** | Distributed database tables, relational or document schemas | **Single-File SOT (`state.yaml` / `state.json`)** + Event Log / Time-Travel |
| **Agent Reasoning** | Rudimentary LLM task calls, simple prompt interpolation | Full Agentic Loops (ReAct, Planning, Tool Use, Sandboxed Capabilities, Context Compression) |
| **Quality Verification** | Binary Task Success/Failure (exception based) | **4-Layer Epistemic Verification (L0 Anti-Skip, L1 Functional, L1.5 pACS, L2 Adversarial Review)** |
| **Energy & Token Budget** | Not token-aware | **Energy & Token Budgeting, RLM Context Compaction, Auto-Refueling** |
| **Failure Recovery** | Blind retries or Saga rollback | **Abductive Diagnosis (pre-evidence collection, hypothesis formation, targeted healing)** |
| **Autopilot Execution** | Human task blocks until external API call | **Zero-touch Autopilot mode with Decision Logs and Auto-Approval** |
| **Polyglot Engines** | Java server + client SDKs | **First-class dual engines: Native Python engine + Native TypeScript/Bun engine** sharing the identical SOT schema and event protocol |

---
 
 ## 3. Triple-Guard Remediation & Multi-Engine Parity Findings
 
 ### Audit Findings & Resolutions
 - **SOT Schema Divergence (Resolved):**
   - TypeScript executor originally used a minimal YAML serializer emitting only status, role, and pacs_score.
   - Now updated to full parity: emits `current_stage_name`, `total_stages`, structured `autopilot`, `energy_budget`, granular task metrics (`task_id`, `stage_id`, `type`, `attempt`, `gate_verdict`, `deliverable`, `error`), and `outputs`.
   - `_context_lib.py` S3 validator updated to accept engine runtime `task_*` keys alongside generator `step-N` keys without warning.
 - **Exception Transparency (Resolved):**
   - Eliminated swallowed `except: pass` in production codebase (`verification_controller.py`, `skills_indexer.py`, `toon_adapter.py`, `prompt-runner/run.py`).
   - Replaced with structured logging and failure signaling to preserve epistemic integrity of L0-L2 verification gates.
 - **Infrastructure Hardening (Resolved):**
   - `setup_init.py` & `setup_maintenance.py` updated: registered `retry_manager.py`, filtered `_test_` files, whitelisted `query_workflow.py` in `SOT_AWARE_SCRIPTS`.
   - `setup_init.py --init` passes 30/30 checks (100% clean, 0 warnings).
 - **CLI Usability (Resolved):**
   - `bin/cli.js status` now passes `--project-dir "${rootDir}" --dashboard` correctly.
   - `bin/cli.js init` pipes stdin safely (`< /dev/null`) preventing blocking.
   - Test suite 12 added for `tests/test_retry_manager.py` (21 tests).

## 4. Architecture Blueprint for Our Custom Event-Driven Agentic Engine

### Core Components
1. **AgenticDecider (Deterministic State Machine):**
   - Evaluates workflow DAGs with stages: Research -> Planning -> Implementation.
   - Handles DAG branching (Parallel, Conditional, Loop, Dynamic Fan-out).
   - Enforces 4-Layer Verification gates before marking any task as complete.
2. **EventBus & Queue (Event-Driven Backbone):**
   - Async pub/sub event bus supporting `WorkflowStarted`, `TaskScheduled`, `TaskPolled`, `TaskProgress`, `TaskVerificationRequested`, `TaskCompleted`, `TaskFailed`, `WorkflowPaused`, `WorkflowResumed`, `WorkflowCompleted`.
   - Pluggable backends: `MemoryQueue`, `FileQueue` (SOT-native), `SQLiteQueue`, and `RedisQueue`.
3. **SOT State Storage & Event Log:**
   - Single-file SOT (`state.yaml` / `state.json`) updated exclusively by the Engine Orchestrator.
   - Append-only event ledger (`ledger.jsonl` / `traces.jsonl`) for replayability and time-travel debugging.
4. **Resilient Task Worker Runtime:**
   - Worker pool with concurrency limits, exponential backoff retries, lease renewal / heartbeats.
   - System Workers: `CodeExecWorker`, `WaitWorker`, `WebhookWorker`, `TransformWorker`.
   - Agent Workers: Role-based AI agents (`researcher`, `architect`, `engineer`, `reviewer`, `fact_checker`) with least-privilege tool isolation.
5. **Autopilot & Gate Controller:**
   - Evaluates L0 (physical file existence/size), L1 (functional acceptance criteria), L1.5 (pACS 3D calibration + pre-mortem), L2 (Adversarial reviewer/fact-checker).
   - Automated Decision Log generation in `autopilot-logs/`.
6. **Self-Healing & Abductive Diagnosis Layer:**
   - On gate failure: does not blindly retry. Pauses, triggers `diagnose_context`, generates multi-hypothesis root cause analysis (`AD1-AD10`), adjusts context/plan, and retries with informed correction.
7. **Fuel & Context Preservation (RLM):**
   - Tracks token consumption, monitors context headroom, triggers compaction and snapshotting before context exhaustion.
