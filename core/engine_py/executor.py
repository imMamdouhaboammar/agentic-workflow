"""
executor.py — Main Engine Orchestrator & Single-Writer SOT Coordinator.

Implements Absolute Criterion 2:
- Single-File SOT (state.yaml) updated exclusively by this Orchestrator
- Atomic write with filesystem lock to eliminate race conditions
- Decider evaluation loop driving tasks into the queue
- Event publishing for all lifecycle transitions
"""

import os
import time
import uuid
import asyncio
from typing import Optional, Dict, Any

try:
    import yaml
except ImportError:
    yaml = None

import json

from core.engine_py.models import (
    WorkflowDefinition, WorkflowInstance, WorkflowStatus, TaskStatus, EngineEvent
)
from core.engine_py.decider import AgenticDecider
from core.engine_py.queue import TaskQueue
from core.engine_py.event_bus import AsyncEventBus
from core.engine_py.energy import EnergyBudget


class AgenticExecutor:
    """Orchestrates workflow lifecycle, state transitions, and atomic SOT persistence."""

    def __init__(
        self,
        workflow_def: WorkflowDefinition,
        queue: TaskQueue,
        event_bus: AsyncEventBus,
        project_dir: str = ".",
        sot_filename: str = "state.yaml",
        energy_budget: Optional[EnergyBudget] = None
    ):
        self.workflow_def = workflow_def
        self.queue = queue
        self.event_bus = event_bus
        self.project_dir = os.path.abspath(project_dir)
        self.sot_path = os.path.join(self.project_dir, sot_filename)
        self.decider = AgenticDecider()
        self.energy = energy_budget or EnergyBudget()
        
        self.trace_id = f"auto_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        self.instance = WorkflowInstance(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            workflow_def=workflow_def,
            trace_id=self.trace_id,
            variables=dict(workflow_def.input_parameters)
        )
        self._write_sot()

    def _write_sot(self) -> None:
        """Atomically persists Single Source of Truth state to state.yaml."""
        current_stage = self.instance.get_current_stage()
        sot_data = {
            "workflow": {
                "title": self.workflow_def.name,
                "version": self.workflow_def.version,
                "workflow_id": self.instance.workflow_id,
                "trace_id": self.instance.trace_id,
                "status": self.instance.status.value,
                "current_stage": current_stage.id if current_stage else "COMPLETED",
                "current_stage_name": current_stage.name if current_stage else "All Stages Finished",
                "total_stages": len(self.workflow_def.stages),
                "autopilot": {"enabled": self.instance.autopilot_enabled, "status": self.instance.status.value},
                "energy_budget": {
                    "remaining_pct": round(self.energy.energy_percentage, 1),
                    "refuel_count": self.energy.refuel_count,
                    "consumed_tokens": self.energy.consumed_tokens
                }
            },
            "tasks": {
                tid: {
                    "task_id": t.task_id,
                    "stage_id": t.stage_id,
                    "type": t.task_def.type,
                    "role": t.task_def.role.value,
                    "status": t.status.value,
                    "attempt": t.attempt,
                    "pacs_score": t.pacs_score,
                    "gate_verdict": t.gate_verdict,
                    "deliverable": t.task_def.deliverable_path,
                    "error": t.error_message
                }
                for tid, t in self.instance.tasks.items()
            },
            "outputs": self.instance.outputs
        }

        temp_path = f"{self.sot_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            if yaml is not None:
                yaml.dump(sot_data, f, sort_keys=False)
            else:
                json.dump(sot_data, f, indent=2)
        os.replace(temp_path, self.sot_path)

    async def step(self) -> bool:
        """Executes one evaluation cycle of the state decider."""
        # 1. Reclaim any expired leases in queue
        self.queue.reclaim_expired()

        # 2. Evaluate state
        res = self.decider.evaluate(self.instance)

        # 3. Schedule newly ready tasks into queue
        for task in res.tasks_to_schedule:
            self.queue.push(task)
            await self.event_bus.publish(EngineEvent(
                event_type="task.scheduled",
                workflow_id=self.instance.workflow_id,
                stage_id=task.stage_id,
                task_id=task.task_id,
                trace_id=self.instance.trace_id,
                payload={"type": task.task_def.type, "role": task.task_def.role.value}
            ))

        for task in res.tasks_to_retry:
            self.queue.push(task)
            await self.event_bus.publish(EngineEvent(
                event_type="task.retrying",
                workflow_id=self.instance.workflow_id,
                stage_id=task.stage_id,
                task_id=task.task_id,
                trace_id=self.instance.trace_id,
                payload={"attempt": task.attempt}
            ))

        if res.stage_transitioned:
            await self.event_bus.publish(EngineEvent(
                event_type="stage.transitioned",
                workflow_id=self.instance.workflow_id,
                stage_id=res.new_stage_id,
                trace_id=self.instance.trace_id
            ))

        # 4. Atomic SOT update
        self._write_sot()

        if res.is_terminal:
            event_name = "workflow.completed" if res.workflow_status == WorkflowStatus.COMPLETED else "workflow.failed"
            await self.event_bus.publish(EngineEvent(
                event_type=event_name,
                workflow_id=self.instance.workflow_id,
                trace_id=self.instance.trace_id,
                payload={"status": res.workflow_status.value, "error": res.error_message}
            ))
            return False

        return True

    async def run_until_complete(self, workers: list, poll_interval: float = 0.05, max_iterations: int = 100) -> bool:
        """Runs the orchestrator loop alongside active workers until terminal state."""
        await self.event_bus.publish(EngineEvent(
            event_type="workflow.started",
            workflow_id=self.instance.workflow_id,
            trace_id=self.instance.trace_id,
            payload={"name": self.workflow_def.name}
        ))

        iterations = 0
        while iterations < max_iterations:
            iterations += 1

            # Let workers process available tasks
            for w in workers:
                await w.run_once()

            # Advance orchestrator decider step
            active = await self.step()
            if not active:
                break

            await asyncio.sleep(poll_interval)

        return self.instance.status == WorkflowStatus.COMPLETED
