"""
models.py — Data structures and state definitions for AgenticWorkflow Engine.

Defines:
- Workflow & Task definitions
- Workflow & Task execution instances
- State enumerations (TaskStatus, WorkflowStatus, BackoffType)
- Standard EngineEvent envelope
"""

import time
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union


class TaskStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    POLLED = "POLLED"
    IN_PROGRESS = "IN_PROGRESS"
    GATE_EVALUATING = "GATE_EVALUATING"
    DIAGNOSING = "DIAGNOSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class WorkflowStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BackoffType(str, Enum):
    FIXED = "FIXED"
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    REVIEWER = "reviewer"
    FACT_CHECKER = "fact_checker"
    CLEAN_CODE_GUARD = "clean_code_guard"
    RECOVERY = "recovery"


@dataclass
class RetryPolicy:
    max_retries: int = 3
    delay_seconds: float = 2.0
    backoff_rate: BackoffType = BackoffType.EXPONENTIAL

    def calculate_delay(self, attempt: int) -> float:
        if self.backoff_rate == BackoffType.FIXED:
            return self.delay_seconds
        elif self.backoff_rate == BackoffType.LINEAR:
            return self.delay_seconds * attempt
        else:  # EXPONENTIAL
            return self.delay_seconds * (2 ** (attempt - 1))


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 2
    cooldown_seconds: float = 30.0


@dataclass
class TaskDefinition:
    id: str
    type: str  # system.code, system.wait, agent.task, agent.human, agent.review, etc.
    name: str = ""
    description: str = ""
    role: AgentRole = AgentRole.ENGINEER
    deliverable_path: Optional[str] = None
    criteria: List[str] = field(default_factory=list)
    input_parameters: Dict[str, Any] = field(default_factory=dict)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: int = 300
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    compensation_task: Optional[str] = None
    branches: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StageDefinition:
    id: str
    name: str
    stage_type: str = "custom"  # research, planning, implementation, verification
    tasks: List[TaskDefinition] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    name: str
    version: str = "1.0.0"
    description: str = ""
    stages: List[StageDefinition] = field(default_factory=list)
    input_parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    failure_workflow: Optional[str] = None


@dataclass
class TaskInstance:
    task_id: str
    workflow_id: str
    stage_id: str
    task_def: TaskDefinition
    status: TaskStatus = TaskStatus.SCHEDULED
    attempt: int = 1
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    worker_id: Optional[str] = None
    scheduled_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    lease_expires_at: Optional[float] = None
    pacs_score: Optional[int] = None
    gate_verdict: Optional[str] = None
    error_message: Optional[str] = None
    trace_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["task_def"]["role"] = self.task_def.role.value
        d["task_def"]["retry_policy"]["backoff_rate"] = self.task_def.retry_policy.backoff_rate.value
        return d


@dataclass
class WorkflowInstance:
    workflow_id: str
    workflow_def: WorkflowDefinition
    trace_id: str
    status: WorkflowStatus = WorkflowStatus.RUNNING
    current_stage_index: int = 0
    tasks: Dict[str, TaskInstance] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    autopilot_enabled: bool = True
    error_message: Optional[str] = None

    def get_current_stage(self) -> Optional[StageDefinition]:
        if 0 <= self.current_stage_index < len(self.workflow_def.stages):
            return self.workflow_def.stages[self.current_stage_index]
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.workflow_def.name,
            "version": self.workflow_def.version,
            "trace_id": self.trace_id,
            "status": self.status.value,
            "current_stage_index": self.current_stage_index,
            "current_stage_id": self.get_current_stage().id if self.get_current_stage() else None,
            "autopilot_enabled": self.autopilot_enabled,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "variables": self.variables,
            "outputs": self.outputs,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message
        }


@dataclass
class EngineEvent:
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str = "workflow.started"
    timestamp: float = field(default_factory=lambda: time.time() * 1000)
    trace_id: str = ""
    workflow_id: str = ""
    stage_id: Optional[str] = None
    task_id: Optional[str] = None
    worker_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
