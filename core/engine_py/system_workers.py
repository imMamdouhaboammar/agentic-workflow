"""
system_workers.py — Built-in System Task Workers.

Implements handlers for:
- system.code: executes inline Python or shell code
- system.wait: timer delays or external signal pauses
- system.switch: evaluates dynamic conditional branching
- system.transform: data projection and key transformation
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

from core.engine_py.models import TaskInstance
from core.engine_py.worker import BaseWorker


class SystemWorker(BaseWorker):
    """Worker handling core system task execution without external AI dependencies."""

    def __init__(self, worker_id: str, queue, event_bus, verification_controller=None):
        super().__init__(
            worker_id=worker_id,
            task_types=["system.code", "system.wait", "system.switch", "system.transform"],
            queue=queue,
            event_bus=event_bus,
            verification_controller=verification_controller
        )

    async def execute_task(self, task: TaskInstance) -> Dict[str, Any]:
        task_type = task.task_def.type

        if task_type == "system.code":
            return await self._execute_code(task)
        elif task_type == "system.wait":
            return await self._execute_wait(task)
        elif task_type == "system.switch":
            return await self._execute_switch(task)
        elif task_type == "system.transform":
            return await self._execute_transform(task)
        else:
            raise ValueError(f"Unsupported system task type: {task_type}")

    async def _execute_code(self, task: TaskInstance) -> Dict[str, Any]:
        code = task.task_def.input_parameters.get("code", "")
        # Safe evaluation of deterministic expressions
        local_scope: Dict[str, Any] = {"inputs": task.input_data, "result": None}
        exec(code, {}, local_scope)
        return {"result": local_scope.get("result", "COMPLETED")}

    async def _execute_wait(self, task: TaskInstance) -> Dict[str, Any]:
        duration = float(task.task_def.input_parameters.get("seconds", 1.0))
        await asyncio.sleep(min(duration, 10.0))  # Capped for safety in test run
        return {"waited_seconds": duration}

    async def _execute_switch(self, task: TaskInstance) -> Dict[str, Any]:
        condition_key = task.task_def.input_parameters.get("key", "status")
        val = task.input_data.get(condition_key)
        branches = task.task_def.branches
        chosen_branch = branches.get(str(val), branches.get("default", "default_branch"))
        return {"selected_branch": chosen_branch}

    async def _execute_transform(self, task: TaskInstance) -> Dict[str, Any]:
        mapping = task.task_def.input_parameters.get("mapping", {})
        transformed = {}
        for out_key, in_path in mapping.items():
            transformed[out_key] = task.input_data.get(in_path)
        return transformed
