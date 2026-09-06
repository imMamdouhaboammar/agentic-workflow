"""
worker.py — Resilient Worker Runtime & Circuit Breaker.

Provides:
- CircuitBreaker pattern (CLOSED -> OPEN -> HALF_OPEN)
- BaseWorker with automated heartbeats and 4-layer verification gate integration
"""

import time
import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from core.engine_py.models import TaskInstance, TaskStatus, EngineEvent
from core.engine_py.queue import TaskQueue
from core.engine_py.event_bus import AsyncEventBus
from core.engine_py.verification_controller import VerificationController


class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Protects against cascade failures by halting execution when failures exceed threshold."""

    def __init__(self, failure_threshold: int = 2, cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitBreakerState.CLOSED
        self.failure_streak = 0
        self.last_trip_time: Optional[float] = None
        self._lock = threading.Lock()

    def record_success(self) -> None:
        with self._lock:
            self.failure_streak = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED

    def record_failure(self) -> None:
        with self._lock:
            self.failure_streak += 1
            if self.failure_streak >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.last_trip_time = time.time()

    def can_execute(self) -> bool:
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            if self.state == CircuitBreakerState.OPEN:
                if self.last_trip_time and (time.time() - self.last_trip_time) > self.cooldown_seconds:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            return True  # HALF_OPEN allows single canary probe


class BaseWorker(ABC):
    """Abstract base worker with queue leasing, heartbeats, and gate evaluation."""

    def __init__(
        self,
        worker_id: str,
        task_types: List[str],
        queue: TaskQueue,
        event_bus: AsyncEventBus,
        verification_controller: Optional[VerificationController] = None
    ):
        self.worker_id = worker_id
        self.task_types = task_types
        self.queue = queue
        self.event_bus = event_bus
        self.verifier = verification_controller or VerificationController()
        self.circuit_breaker = CircuitBreaker()
        self.running = False

    @abstractmethod
    async def execute_task(self, task: TaskInstance) -> Dict[str, Any]:
        """Subclass implementation of actual task logic."""
        pass

    async def run_once(self) -> bool:
        """Polls for one task, executes it, verifies gates, and commits results."""
        if not self.circuit_breaker.can_execute():
            # Circuit is open; skip poll
            return False

        task = self.queue.poll(self.task_types, self.worker_id, lease_seconds=60.0)
        if not task:
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = time.time()
        await self.event_bus.publish(EngineEvent(
            event_type="task.polled",
            workflow_id=task.workflow_id,
            stage_id=task.stage_id,
            task_id=task.task_id,
            worker_id=self.worker_id,
            trace_id=task.trace_id
        ))

        try:
            # 1. Execute task
            outputs = await self.execute_task(task)
            task.output_data = outputs

            # 2. Evaluate 4-Layer Verification Gates
            task.status = TaskStatus.GATE_EVALUATING
            gate_res = self.verifier.evaluate_all_gates(task)

            if gate_res.passed:
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.pacs_score = gate_res.l15_pacs_score
                task.gate_verdict = gate_res.l2_verdict
                self.circuit_breaker.record_success()
                self.queue.ack(task.task_id)

                await self.event_bus.publish(EngineEvent(
                    event_type="task.completed",
                    workflow_id=task.workflow_id,
                    stage_id=task.stage_id,
                    task_id=task.task_id,
                    worker_id=self.worker_id,
                    trace_id=task.trace_id,
                    payload={"outputs": outputs, "pacs_score": gate_res.l15_pacs_score}
                ))
                return True
            else:
                task.status = TaskStatus.FAILED
                task.error_message = gate_res.error_message
                self.circuit_breaker.record_failure()
                self.queue.nack(task.task_id, requeue=False)

                await self.event_bus.publish(EngineEvent(
                    event_type="task.failed",
                    workflow_id=task.workflow_id,
                    stage_id=task.stage_id,
                    task_id=task.task_id,
                    worker_id=self.worker_id,
                    trace_id=task.trace_id,
                    payload={"error": gate_res.error_message, "diagnosis": gate_res.diagnosis_report}
                ))
                return False

        except Exception as err:
            task.status = TaskStatus.FAILED
            task.error_message = str(err)
            self.circuit_breaker.record_failure()
            self.queue.nack(task.task_id, requeue=False)

            await self.event_bus.publish(EngineEvent(
                event_type="task.failed",
                workflow_id=task.workflow_id,
                stage_id=task.stage_id,
                task_id=task.task_id,
                worker_id=self.worker_id,
                trace_id=task.trace_id,
                payload={"error": str(err)}
            ))
            return False
