/**
 * runner.ts — CLI entry point for TypeScript Agentic Engine.
 */

import * as path from "node:path";
import * as fs from "node:fs";
import { WorkflowDefinition, AgentRole } from "./types.js";
import { InMemoryTaskQueue } from "./queue.js";
import { AsyncEventBus } from "./event-bus.js";
import { VerificationController } from "./verification-controller.js";
import { SystemWorker, AgentWorker } from "./worker.js";
import { AgenticExecutor } from "./executor.js";
import { LifecycleDirector } from "../integrations/index.ts";

async function main() {
  const projectDir = process.cwd();
  console.log(`🚀 [engine-ts] Starting Event-Driven Agentic Engine (TypeScript / Bun)...`);

  const defaultWorkflow: WorkflowDefinition = {
    name: "autonomous_agentic_pipeline",
    version: "1.0.0",
    stages: [
      {
        id: "stage_01_research",
        name: "Stage 1: Research",
        tasks: [
          {
            id: "task_research_01",
            name: "Analyze System Architecture and Dependencies",
            type: "agent.task",
            role: AgentRole.RESEARCHER,
            deliverable_path: "docs/research_findings.md",
            criteria: ["Analyze architecture patterns", "Establish baseline"]
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
            id: "task_code_impl",
            name: "Implement Core Production Logic",
            type: "agent.task",
            role: AgentRole.ENGINEER,
            deliverable_path: "docs/implementation_summary.md",
            criteria: ["Pass unit tests", "Generate comprehensive documentation"]
          },
          {
            id: "task_review_01",
            name: "Adversarial Code & Fact-Check Review",
            type: "agent.review",
            role: AgentRole.REVIEWER,
            deliverable_path: "review-logs/step-3-review.md",
            criteria: ["Zero critical vulnerabilities"]
          }
        ]
      }
    ]
  };

  const queue = new InMemoryTaskQueue();
  const ledgerPath = path.join(projectDir, "ledger.jsonl");
  const eventBus = new AsyncEventBus(ledgerPath);
  const verifier = new VerificationController(projectDir);

  const sysWorker = new SystemWorker("sys_worker_1", queue, eventBus, verifier);
  const agentWorker = new AgentWorker("agent_worker_1", queue, eventBus, verifier, projectDir);

  const executor = new AgenticExecutor(defaultWorkflow, queue, eventBus, projectDir, "state.yaml");

  const lifecycleDirector = new LifecycleDirector(projectDir);
  console.log(`🧭 [lifecycle-director] Lifecycle Director active (Ponytail, TOON, Fable, Caveman).`);
  console.log(`⚡ Trace ID: ${executor.instance.trace_id}`);
  console.log(`⚡ Workflow ID: ${executor.instance.workflow_id}`);
  console.log(`⚡ SOT Path: ${executor.sotPath}`);

  const success = await executor.runUntilComplete([sysWorker, agentWorker], 20, 50);

  if (success) {
    lifecycleDirector.executePostPhaseActions("handoff", {
      trace_id: executor.instance.trace_id,
      next_action: "TypeScript Event-Driven Engine Workflow execution completed successfully."
    });
    console.log(`\n🎉 [engine-ts] Workflow Completed Successfully with All Gates Verified!`);
    process.exit(0);
  } else {
    console.error(`\n❌ [engine-ts] Workflow execution halted or failed gates.`);
    process.exit(1);
  }
}

main().catch(err => {
  console.error("Fatal error in engine runner:", err);
  process.exit(1);
});
