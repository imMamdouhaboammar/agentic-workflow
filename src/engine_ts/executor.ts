/**
 * executor.ts — Main TypeScript Engine Orchestrator & SOT Coordinator.
 * 
 * Enforces Absolute Criterion 2: Single-File SOT (state.yaml) atomic updates.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import {
  WorkflowDefinition,
  WorkflowInstance,
  WorkflowStatus,
  EngineEvent
} from "./types.js";
import { AgenticDecider } from "./decider.js";
import { TaskQueue } from "./queue.js";
import { AsyncEventBus } from "./event-bus.js";
import { BaseWorker } from "./worker.js";

export class AgenticExecutor {
  public workflowDef: WorkflowDefinition;
  public queue: TaskQueue;
  public eventBus: AsyncEventBus;
  public projectDir: string;
  public sotPath: string;
  public decider: AgenticDecider;
  public instance: WorkflowInstance;

  constructor(
    workflowDef: WorkflowDefinition,
    queue: TaskQueue,
    eventBus: AsyncEventBus,
    projectDir: string = ".",
    sotFilename: string = "state.yaml"
  ) {
    this.workflowDef = workflowDef;
    this.queue = queue;
    this.eventBus = eventBus;
    this.projectDir = path.resolve(projectDir);
    this.sotPath = path.join(this.projectDir, sotFilename);
    this.decider = new AgenticDecider();

    const traceId = `ts_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    this.instance = {
      workflow_id: `wf_${Math.random().toString(36).slice(2, 10)}`,
      workflow_def: workflowDef,
      trace_id: traceId,
      status: WorkflowStatus.RUNNING,
      current_stage_index: 0,
      tasks: {},
      variables: { ...(workflowDef.input_parameters || {}) },
      outputs: {},
      started_at: Date.now(),
      autopilot_enabled: true
    };

    this.writeSot();
  }

  public writeSot(): void {
    const currentStage = this.workflowDef.stages[this.instance.current_stage_index];
    const totalStages = this.workflowDef.stages.length;

    // Build structured SOT — mirrors Python engine's _write_sot() field set exactly
    const sotData: Record<string, any> = {
      workflow: {
        title: this.workflowDef.name,
        version: this.workflowDef.version,
        workflow_id: this.instance.workflow_id,
        trace_id: this.instance.trace_id,
        status: this.instance.status,
        current_stage: currentStage ? currentStage.id : "COMPLETED",
        current_stage_name: currentStage ? currentStage.name : "All Stages Finished",
        total_stages: totalStages,
        autopilot: {
          enabled: this.instance.autopilot_enabled,
          mode: this.instance.autopilot_enabled ? "auto" : "manual",
          current_step: this.instance.current_stage_index
        },
        energy_budget: {
          initial: 100,
          remaining: 100,
          consumed: 0
        },
        runtime: "typescript_bun"
      },
      tasks: {} as Record<string, any>,
      outputs: this.instance.outputs ?? {}
    };

    for (const [tid, t] of Object.entries(this.instance.tasks)) {
      sotData.tasks[tid] = {
        task_id: t.task_id,
        stage_id: t.stage_id,
        type: t.task_def.type,
        role: t.task_def.role,
        status: t.status,
        attempt: t.attempt,
        pacs_score: t.pacs_score ?? 0,
        gate_verdict: t.gate_verdict ?? "PENDING",
        deliverable: t.task_def.deliverable_path ?? "",
        error: t.error_message ?? null
      };
    }

    // ── YAML serialiser ────────────────────────────────────────────────────
    const ind = (n: number) => "  ".repeat(n);
    const yamlStr = (v: any): string => {
      if (v === null || v === undefined) return "null";
      if (typeof v === "boolean") return v ? "true" : "false";
      if (typeof v === "number") return String(v);
      if (typeof v === "string") {
        if (v === "" || /[:#\[\]{},|>&*!%@`]/.test(v) || v.includes('"')) {
          return `"${v.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
        }
        return v;
      }
      return `"${String(v)}"`;
    };

    const lines: string[] = [];
    const wf = sotData.workflow;

    lines.push("workflow:");
    lines.push(`${ind(1)}title: ${yamlStr(wf.title)}`);
    lines.push(`${ind(1)}version: ${yamlStr(wf.version)}`);
    lines.push(`${ind(1)}workflow_id: ${yamlStr(wf.workflow_id)}`);
    lines.push(`${ind(1)}trace_id: ${yamlStr(wf.trace_id)}`);
    lines.push(`${ind(1)}status: ${yamlStr(wf.status)}`);
    lines.push(`${ind(1)}current_stage: ${yamlStr(wf.current_stage)}`);
    lines.push(`${ind(1)}current_stage_name: ${yamlStr(wf.current_stage_name)}`);
    lines.push(`${ind(1)}total_stages: ${wf.total_stages}`);
    lines.push(`${ind(1)}autopilot:`);
    lines.push(`${ind(2)}enabled: ${wf.autopilot.enabled}`);
    lines.push(`${ind(2)}mode: ${yamlStr(wf.autopilot.mode)}`);
    lines.push(`${ind(2)}current_step: ${wf.autopilot.current_step}`);
    lines.push(`${ind(1)}energy_budget:`);
    lines.push(`${ind(2)}initial: ${wf.energy_budget.initial}`);
    lines.push(`${ind(2)}remaining: ${wf.energy_budget.remaining}`);
    lines.push(`${ind(2)}consumed: ${wf.energy_budget.consumed}`);
    lines.push(`${ind(1)}runtime: ${yamlStr(wf.runtime)}`);

    lines.push("tasks:");
    for (const [tid, t] of Object.entries(sotData.tasks)) {
      const task = t as Record<string, any>;
      lines.push(`${ind(1)}${tid}:`);
      lines.push(`${ind(2)}task_id: ${yamlStr(task.task_id)}`);
      lines.push(`${ind(2)}stage_id: ${yamlStr(task.stage_id)}`);
      lines.push(`${ind(2)}type: ${yamlStr(task.type)}`);
      lines.push(`${ind(2)}role: ${yamlStr(task.role)}`);
      lines.push(`${ind(2)}status: ${yamlStr(task.status)}`);
      lines.push(`${ind(2)}attempt: ${task.attempt}`);
      lines.push(`${ind(2)}pacs_score: ${task.pacs_score}`);
      lines.push(`${ind(2)}gate_verdict: ${yamlStr(task.gate_verdict)}`);
      lines.push(`${ind(2)}deliverable: ${yamlStr(task.deliverable)}`);
      lines.push(`${ind(2)}error: ${yamlStr(task.error)}`);
    }

    lines.push("outputs:");
    for (const [key, val] of Object.entries(sotData.outputs)) {
      lines.push(`${ind(1)}${key}: ${yamlStr(String(val))}`);
    }

    // Atomic write: .tmp → rename (mirrors Python's os.replace)
    const tempPath = `${this.sotPath}.tmp`;
    fs.writeFileSync(tempPath, lines.join("\n") + "\n", "utf-8");
    fs.renameSync(tempPath, this.sotPath);
  }

  public async step(): Promise<boolean> {
    this.queue.reclaimExpired();
    const res = this.decider.evaluate(this.instance);

    for (const task of res.tasks_to_schedule) {
      this.queue.push(task);
      await this.eventBus.publish({
        event_id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        event_type: "task.scheduled",
        timestamp: Date.now(),
        trace_id: this.instance.trace_id,
        workflow_id: this.instance.workflow_id,
        stage_id: task.stage_id,
        task_id: task.task_id,
        payload: { type: task.task_def.type, role: task.task_def.role }
      });
    }

    for (const task of res.tasks_to_retry) {
      this.queue.push(task);
      await this.eventBus.publish({
        event_id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        event_type: "task.retrying",
        timestamp: Date.now(),
        trace_id: this.instance.trace_id,
        workflow_id: this.instance.workflow_id,
        stage_id: task.stage_id,
        task_id: task.task_id,
        payload: { attempt: task.attempt }
      });
    }

    if (res.stage_transitioned) {
      await this.eventBus.publish({
        event_id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        event_type: "stage.transitioned",
        timestamp: Date.now(),
        trace_id: this.instance.trace_id,
        workflow_id: this.instance.workflow_id,
        stage_id: res.new_stage_id
      });
    }

    this.writeSot();

    if (res.is_terminal) {
      const eventType =
        res.workflow_status === WorkflowStatus.COMPLETED ? "workflow.completed" : "workflow.failed";
      await this.eventBus.publish({
        event_id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        event_type: eventType,
        timestamp: Date.now(),
        trace_id: this.instance.trace_id,
        workflow_id: this.instance.workflow_id,
        payload: { status: res.workflow_status, error: res.error_message }
      });
      return false;
    }

    return true;
  }

  public async runUntilComplete(
    workers: BaseWorker[],
    pollIntervalMs: number = 20,
    maxIterations: number = 100
  ): Promise<boolean> {
    await this.eventBus.publish({
      event_id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      event_type: "workflow.started",
      timestamp: Date.now(),
      trace_id: this.instance.trace_id,
      workflow_id: this.instance.workflow_id,
      payload: { name: this.workflowDef.name }
    });

    let iterations = 0;
    while (iterations < maxIterations) {
      iterations++;

      for (const w of workers) {
        await w.runOnce();
      }

      const active = await this.step();
      if (!active) break;

      await new Promise(r => setTimeout(r, pollIntervalMs));
    }

    return this.instance.status === WorkflowStatus.COMPLETED;
  }
}
