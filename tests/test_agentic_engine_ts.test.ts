/**
 * test_agentic_engine_ts.test.ts — Bun Test Suite for TypeScript Agentic Engine.
 */

import { test, expect, describe, beforeEach, afterEach } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";

import {
  WorkflowDefinition,
  WorkflowStatus,
  TaskStatus,
  AgentRole
} from "../src/engine_ts/types.js";
import { InMemoryTaskQueue } from "../src/engine_ts/queue.js";
import { AsyncEventBus } from "../src/engine_ts/event-bus.js";
import { CircuitBreaker, CircuitBreakerState, SystemWorker, AgentWorker } from "../src/engine_ts/worker.js";
import { VerificationController } from "../src/engine_ts/verification-controller.js";
import { AgenticExecutor } from "../src/engine_ts/executor.js";

describe("TypeScript Agentic Engine", () => {
  let tmpDir: string;
  let ledgerPath: string;
  let sotPath: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "engine_ts_test_"));
    ledgerPath = path.join(tmpDir, "ledger.jsonl");
    sotPath = path.join(tmpDir, "state.yaml");
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("InMemoryTaskQueue push, poll, lease and ack", () => {
    const q = new InMemoryTaskQueue();
    q.push({
      task_id: "ts_t1",
      workflow_id: "w1",
      stage_id: "s1",
      task_def: { id: "ts_t1", type: "system.code" },
      status: TaskStatus.SCHEDULED,
      attempt: 1,
      input_data: {},
      output_data: {},
      scheduled_at: Date.now(),
      trace_id: "tr_1"
    });

    expect(q.size()).toBe(1);

    const polled = q.poll(["system.code"], "w_ts", 10);
    expect(polled).not.toBeNull();
    expect(polled?.task_id).toBe("ts_t1");
    expect(polled?.worker_id).toBe("w_ts");
    expect(q.size()).toBe(0);

    q.ack("ts_t1");
    expect(q.size()).toBe(0);
  });

  test("CircuitBreaker transitions on failures and recovers", async () => {
    const cb = new CircuitBreaker(2, 0.1);
    expect(cb.canExecute()).toBe(true);
    expect(cb.state).toBe(CircuitBreakerState.CLOSED);

    cb.recordFailure();
    expect(cb.canExecute()).toBe(true);

    cb.recordFailure();
    expect(cb.state).toBe(CircuitBreakerState.OPEN);
    expect(cb.canExecute()).toBe(false);

    await new Promise(r => setTimeout(r, 120));
    expect(cb.canExecute()).toBe(true);
    expect(cb.state).toBe(CircuitBreakerState.HALF_OPEN);

    cb.recordSuccess();
    expect(cb.state).toBe(CircuitBreakerState.CLOSED);
  });

  test("VerificationController evaluates L0-L2 gates and diagnosis", () => {
    const vc = new VerificationController(tmpDir);
    const task = {
      task_id: "deliv_task",
      workflow_id: "w1",
      stage_id: "s1",
      task_def: {
        id: "deliv_task",
        type: "agent.task",
        deliverable_path: "docs/output.md",
        criteria: ["Architecture verified", "Quality standards met"]
      },
      status: TaskStatus.SCHEDULED,
      attempt: 1,
      input_data: {},
      output_data: {},
      scheduled_at: Date.now(),
      trace_id: "tr_diag"
    };

    // 1. Deliverable doesn't exist -> fails L0, writes diagnosis log
    const failRes = vc.evaluateAllGates(task);
    expect(failRes.passed).toBe(false);
    expect(failRes.l0_passed).toBe(false);
    expect(fs.existsSync(path.join(tmpDir, "diagnosis-logs", "step-deliv_task-diagnosis.md"))).toBe(true);

    // 2. Create deliverable
    const fullPath = path.join(tmpDir, "docs/output.md");
    fs.mkdirSync(path.dirname(fullPath), { recursive: true });
    fs.writeFileSync(
      fullPath,
      "# Architecture Deliverable\n\n" +
      "- Architecture verified: Confirmed by design review.\n" +
      "- Quality standards met: Complete and thorough implementation.\n\n" +
      "Production-ready specifications with full criteria coverage.\n".repeat(6)
    );

    const passRes = vc.evaluateAllGates(task);
    expect(passRes.passed).toBe(true);
    expect(passRes.l0_passed).toBe(true);
    expect(passRes.l1_passed).toBe(true);
    expect(passRes.l15_pacs_score).toBeGreaterThanOrEqual(70);
    expect(passRes.l2_verdict).toBe("PASS");
  });

  test("End-to-End multi-stage workflow execution in TypeScript", async () => {
    const wfDef: WorkflowDefinition = {
      name: "ts_canonical_workflow",
      version: "1.0.0",
      stages: [
        {
          id: "stage_01_research",
          name: "Stage 1: Research",
          tasks: [
            {
              id: "task_research",
              name: "Research System Architecture",
              type: "agent.task",
              role: AgentRole.RESEARCHER,
              deliverable_path: "docs/research_findings.md",
              criteria: ["System requirements analyzed", "Dependencies resolved"]
            }
          ]
        },
        {
          id: "stage_02_planning",
          name: "Stage 2: Planning",
          tasks: [
            {
              id: "task_plan_approval",
              name: "Autopilot Plan Approval",
              type: "agent.human",
              role: AgentRole.ORCHESTRATOR
            }
          ]
        },
        {
          id: "stage_03_implementation",
          name: "Stage 3: Implementation",
          tasks: [
            {
              id: "task_code_exec",
              name: "Run Calculation",
              type: "system.code",
              input_parameters: { code: "return { calculated: 42 * 2 };" }
            },
            {
              id: "task_review",
              name: "Adversarial Review",
              type: "agent.review",
              role: AgentRole.REVIEWER,
              deliverable_path: "review-logs/final_review.md",
              criteria: ["Verified clean"]
            }
          ]
        }
      ]
    };

    const q = new InMemoryTaskQueue();
    const eb = new AsyncEventBus(ledgerPath);
    const vc = new VerificationController(tmpDir);

    const sysWorker = new SystemWorker("sys_w_ts", q, eb, vc);
    const agentWorker = new AgentWorker("agent_w_ts", q, eb, vc, tmpDir);

    const executor = new AgenticExecutor(wfDef, q, eb, tmpDir, "state.yaml");
    const success = await executor.runUntilComplete([sysWorker, agentWorker], 10, 30);

    expect(success).toBe(true);
    expect(executor.instance.status).toBe(WorkflowStatus.COMPLETED);

    // Verify SOT state.yaml created with full schema parity
    expect(fs.existsSync(sotPath)).toBe(true);
    const sotContent = fs.readFileSync(sotPath, "utf-8");
    expect(sotContent).toContain("runtime: typescript_bun");
    expect(sotContent).toContain("status: COMPLETED");
    // Verify new parity fields present (F1 fix)
    expect(sotContent).toContain("total_stages:");
    expect(sotContent).toContain("autopilot:");
    expect(sotContent).toContain("energy_budget:");
    expect(sotContent).toContain("outputs:");

    // Verify durable ledger created
    expect(fs.existsSync(ledgerPath)).toBe(true);
    const lines = fs.readFileSync(ledgerPath, "utf-8").trim().split("\n");
    expect(lines.length).toBeGreaterThan(5);

    // Verify Autopilot decision log created
    expect(fs.existsSync(path.join(tmpDir, "autopilot-logs", "step-task_plan_approval-decision.md"))).toBe(true);
  });
});
