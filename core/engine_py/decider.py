"""
decider.py — Deterministic State Machine & DAG Evaluator (The Decider).

Pure functional logic:
- Evaluates workflow DAG transitions without side effects
- Decides next tasks to schedule, retries to execute, or terminal statuses
- Enforces DNA inheritance: Stage 1 (Research) -> Stage 2 (Planning) -> Stage 3 (Implementation)
- Resolves parallel forks, join synchronization, and conditional switches
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from core.engine_py.models import (
    WorkflowInstance, WorkflowStatus, TaskInstance, TaskStatus, TaskDefinition
)


@dataclass
class DecisionResult:
    workflow_status: WorkflowStatus
    tasks_to_schedule: List[TaskInstance] = field(default_factory=list)
    tasks_to_retry: List[TaskInstance] = field(default_factory=list)
    tasks_to_cancel: List[str] = field(default_factory=list)
    stage_transitioned: bool = False
    new_stage_id: Optional[str] = None
    is_terminal: bool = False
    failed_task: Optional[TaskInstance] = None
    error_message: Optional[str] = None


class AgenticDecider:
    """State evaluator that calculates the next execution transitions for a workflow."""

    def evaluate(self, workflow: WorkflowInstance) -> DecisionResult:
        if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return DecisionResult(workflow_status=workflow.status, is_terminal=True)

        if workflow.status == WorkflowStatus.PAUSED:
            return DecisionResult(workflow_status=WorkflowStatus.PAUSED)

        current_stage = workflow.get_current_stage()
        if not current_stage:
            # All stages completed!
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = time.time()
            return DecisionResult(workflow_status=WorkflowStatus.COMPLETED, is_terminal=True)

        # 1. Inspect existing tasks in the current stage
        stage_task_defs = {t.id: t for t in current_stage.tasks}
        scheduled: List[TaskInstance] = []
        retries: List[TaskInstance] = []

        all_stage_tasks_done = True

        for task_def in current_stage.tasks:
            task_inst = workflow.tasks.get(task_def.id)

            if not task_inst:
                # Task not yet instantiated or scheduled
                new_inst = TaskInstance(
                    task_id=task_def.id,
                    workflow_id=workflow.workflow_id,
                    stage_id=current_stage.id,
                    task_def=task_def,
                    status=TaskStatus.SCHEDULED,
                    trace_id=workflow.trace_id,
                    input_data=dict(workflow.variables)
                )
                workflow.tasks[task_def.id] = new_inst
                scheduled.append(new_inst)
                all_stage_tasks_done = False

            elif task_inst.status in [TaskStatus.SCHEDULED, TaskStatus.POLLED, TaskStatus.IN_PROGRESS, TaskStatus.GATE_EVALUATING, TaskStatus.DIAGNOSING]:
                all_stage_tasks_done = False

            elif task_inst.status == TaskStatus.FAILED:
                # Check retry policy
                max_retries = task_def.retry_policy.max_retries
                if task_inst.attempt < max_retries:
                    task_inst.attempt += 1
                    task_inst.status = TaskStatus.SCHEDULED
                    task_inst.worker_id = None
                    task_inst.lease_expires_at = None
                    retries.append(task_inst)
                    all_stage_tasks_done = False
                else:
                    # Check if a Saga compensation task is defined
                    comp_id = task_def.compensation_task
                    if comp_id and comp_id not in workflow.tasks:
                        comp_def = TaskDefinition(
                            id=comp_id,
                            type="system.code",
                            name=f"Rollback compensation for {task_inst.task_id}",
                            input_parameters={"code": "result = 'COMPENSATED'"}
                        )
                        comp_inst = TaskInstance(
                            task_id=comp_id,
                            workflow_id=workflow.workflow_id,
                            stage_id=current_stage.id,
                            task_def=comp_def,
                            status=TaskStatus.SCHEDULED,
                            trace_id=workflow.trace_id,
                            input_data={"failed_task": task_inst.task_id, "error": task_inst.error_message}
                        )
                        workflow.tasks[comp_id] = comp_inst
                        scheduled.append(comp_inst)
                        all_stage_tasks_done = False
                    else:
                        # Irrecoverable task failure
                        workflow.status = WorkflowStatus.FAILED
                        workflow.completed_at = time.time()
                        workflow.error_message = f"Task {task_inst.task_id} failed after {task_inst.attempt} attempts: {task_inst.error_message}"
                        return DecisionResult(
                            workflow_status=WorkflowStatus.FAILED,
                            is_terminal=True,
                            failed_task=task_inst,
                            error_message=workflow.error_message
                        )

            elif task_inst.status == TaskStatus.COMPLETED:
                # Merge outputs into workflow variables
                if task_inst.output_data:
                    workflow.variables.update(task_inst.output_data)
                    workflow.outputs[task_inst.task_id] = task_inst.output_data

        # 2. Check if current stage has completed
        if all_stage_tasks_done and not scheduled and not retries:
            next_stage_idx = workflow.current_stage_index + 1
            if next_stage_idx < len(workflow.workflow_def.stages):
                workflow.current_stage_index = next_stage_idx
                next_stage = workflow.get_current_stage()
                # Recursively evaluate the new stage to schedule its initial tasks
                recurse_res = self.evaluate(workflow)
                recurse_res.stage_transitioned = True
                recurse_res.new_stage_id = next_stage.id if next_stage else None
                return recurse_res
            else:
                # All stages successfully finished!
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = time.time()
                return DecisionResult(workflow_status=WorkflowStatus.COMPLETED, is_terminal=True)

        return DecisionResult(
            workflow_status=WorkflowStatus.RUNNING,
            tasks_to_schedule=scheduled,
            tasks_to_retry=retries
        )
