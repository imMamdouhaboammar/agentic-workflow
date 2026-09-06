/**
 * decider.ts — Deterministic State Machine Evaluator for TypeScript Engine.
 */

import { WorkflowInstance, WorkflowStatus, TaskInstance, TaskStatus, TaskDefinition } from "./types.js";

export interface DecisionResult {
  workflow_status: WorkflowStatus;
  tasks_to_schedule: TaskInstance[];
  tasks_to_retry: TaskInstance[];
  tasks_to_cancel: string[];
  stage_transitioned: boolean;
  new_stage_id?: string | null;
  is_terminal: boolean;
  failed_task?: TaskInstance | null;
  error_message?: string | null;
}

export class AgenticDecider {
  public evaluate(workflow: WorkflowInstance): DecisionResult {
    if (
      workflow.status === WorkflowStatus.COMPLETED ||
      workflow.status === WorkflowStatus.FAILED ||
      workflow.status === WorkflowStatus.CANCELLED
    ) {
      return {
        workflow_status: workflow.status,
        tasks_to_schedule: [],
        tasks_to_retry: [],
        tasks_to_cancel: [],
        stage_transitioned: false,
        is_terminal: true
      };
    }

    if (workflow.status === WorkflowStatus.PAUSED) {
      return {
        workflow_status: WorkflowStatus.PAUSED,
        tasks_to_schedule: [],
        tasks_to_retry: [],
        tasks_to_cancel: [],
        stage_transitioned: false,
        is_terminal: false
      };
    }

    const currentStage = workflow.workflow_def.stages[workflow.current_stage_index];
    if (!currentStage) {
      workflow.status = WorkflowStatus.COMPLETED;
      workflow.completed_at = Date.now();
      return {
        workflow_status: WorkflowStatus.COMPLETED,
        tasks_to_schedule: [],
        tasks_to_retry: [],
        tasks_to_cancel: [],
        stage_transitioned: false,
        is_terminal: true
      };
    }

    const scheduled: TaskInstance[] = [];
    const retries: TaskInstance[] = [];
    let allStageTasksDone = true;

    for (const taskDef of currentStage.tasks) {
      const taskInst = workflow.tasks[taskDef.id];

      if (!taskInst) {
        // Instantiate and schedule new task
        const newInst: TaskInstance = {
          task_id: taskDef.id,
          workflow_id: workflow.workflow_id,
          stage_id: currentStage.id,
          task_def: taskDef,
          status: TaskStatus.SCHEDULED,
          attempt: 1,
          input_data: { ...workflow.variables },
          output_data: {},
          worker_id: null,
          scheduled_at: Date.now(),
          trace_id: workflow.trace_id
        };
        workflow.tasks[taskDef.id] = newInst;
        scheduled.push(newInst);
        allStageTasksDone = false;
      } else if (
        taskInst.status === TaskStatus.SCHEDULED ||
        taskInst.status === TaskStatus.POLLED ||
        taskInst.status === TaskStatus.IN_PROGRESS ||
        taskInst.status === TaskStatus.GATE_EVALUATING ||
        taskInst.status === TaskStatus.DIAGNOSING
      ) {
        allStageTasksDone = false;
      } else if (taskInst.status === TaskStatus.FAILED) {
        const maxRetries = taskDef.retry_policy?.max_retries ?? 3;
        if (taskInst.attempt < maxRetries) {
          taskInst.attempt += 1;
          taskInst.status = TaskStatus.SCHEDULED;
          taskInst.worker_id = null;
          taskInst.lease_expires_at = null;
          retries.push(taskInst);
          allStageTasksDone = false;
        } else {
          // Check if Saga compensation is defined
          const compId = taskDef.compensation_task;
          if (compId && !workflow.tasks[compId]) {
            const compDef: TaskDefinition = {
              id: compId,
              type: "system.code",
              name: `Rollback compensation for ${taskInst.task_id}`,
              input_parameters: { code: "return { compensated: true };" }
            };
            const compInst: TaskInstance = {
              task_id: compId,
              workflow_id: workflow.workflow_id,
              stage_id: currentStage.id,
              task_def: compDef,
              status: TaskStatus.SCHEDULED,
              attempt: 1,
              input_data: { failed_task: taskInst.task_id, error: taskInst.error_message },
              output_data: {},
              scheduled_at: Date.now(),
              trace_id: workflow.trace_id
            };
            workflow.tasks[compId] = compInst;
            scheduled.push(compInst);
            allStageTasksDone = false;
          } else {
            // Terminal failure
            workflow.status = WorkflowStatus.FAILED;
            workflow.completed_at = Date.now();
            workflow.error_message = `Task ${taskInst.task_id} failed after ${taskInst.attempt} attempts: ${taskInst.error_message}`;
            return {
              workflow_status: WorkflowStatus.FAILED,
              tasks_to_schedule: [],
              tasks_to_retry: [],
              tasks_to_cancel: [],
              stage_transitioned: false,
              is_terminal: true,
              failed_task: taskInst,
              error_message: workflow.error_message
            };
          }
        }
      } else if (taskInst.status === TaskStatus.COMPLETED) {
        if (taskInst.output_data) {
          Object.assign(workflow.variables, taskInst.output_data);
          workflow.outputs[taskInst.task_id] = taskInst.output_data;
        }
      }
    }

    // Check if stage is complete
    if (allStageTasksDone && scheduled.length === 0 && retries.length === 0) {
      const nextStageIdx = workflow.current_stage_index + 1;
      if (nextStageIdx < workflow.workflow_def.stages.length) {
        workflow.current_stage_index = nextStageIdx;
        const nextStage = workflow.workflow_def.stages[nextStageIdx];
        const nextResult = this.evaluate(workflow);
        nextResult.stage_transitioned = true;
        nextResult.new_stage_id = nextStage.id;
        return nextResult;
      } else {
        workflow.status = WorkflowStatus.COMPLETED;
        workflow.completed_at = Date.now();
        return {
          workflow_status: WorkflowStatus.COMPLETED,
          tasks_to_schedule: [],
          tasks_to_retry: [],
          tasks_to_cancel: [],
          stage_transitioned: false,
          is_terminal: true
        };
      }
    }

    return {
      workflow_status: WorkflowStatus.RUNNING,
      tasks_to_schedule: scheduled,
      tasks_to_retry: retries,
      tasks_to_cancel: [],
      stage_transitioned: false,
      is_terminal: false
    };
  }
}
