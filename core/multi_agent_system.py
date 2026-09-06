#!/usr/bin/env python3
"""
multi_agent_system.py — Multi-Agent System Architecture & Governance Engine

Implements patterns from /agency-multi-agent-systems-architect:
1. Hierarchical Orchestrator-Subagent Topology with Task Ledger
2. Least-Privilege Agent Permissions & Sandboxing
3. Circuit Breaker Pattern (CLOSED -> OPEN -> HALF_OPEN)
4. Trace-Based Observability (trace_id, span_id, latency, cost)
5. Contradiction Detection & Multi-Agent Arbitration
"""

import os
import sys
import json
import time
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"      # Healthy: calls proceed normally
    OPEN = "OPEN"          # Tripped: failures exceeded threshold (recovers via diagnosis)
    HALF_OPEN = "HALF_OPEN"  # Testing recovery with single canary request


class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    REVIEWER = "reviewer"
    FACT_CHECKER = "fact_checker"
    CLEAN_CODE_GUARD = "clean_code_guard"
    RECOVERY = "fable_recovery"


# Least-Privilege Tool Permissions Matrix
TOOL_PERMISSIONS: Dict[AgentRole, List[str]] = {
    AgentRole.ORCHESTRATOR: ["read_file", "write_sot", "dispatch_agent", "log_trace"],
    AgentRole.RESEARCHER: ["read_file", "search_web", "read_url", "extract_data"],
    AgentRole.ARCHITECT: ["read_file", "propose_plan", "diagram_topology"],
    AgentRole.ENGINEER: ["read_file", "write_file", "run_tests", "execute_code"],
    AgentRole.REVIEWER: ["read_file", "rate_pacs", "lint_code"],  # Strictly read-only
    AgentRole.FACT_CHECKER: ["read_file", "search_web", "verify_claim"],
    AgentRole.CLEAN_CODE_GUARD: ["read_file", "ast_check", "report_violations"],
    AgentRole.RECOVERY: ["read_file", "diagnose_context", "rollback_checkpoint", "repair_state"]
}


@dataclass
class AgentSpan:
    trace_id: str
    span_id: str
    agent_id: str
    role: str
    step: int
    started_at: float
    completed_at: Optional[float] = None
    latency_ms: Optional[float] = None
    input_tokens: int = 0
    output_tokens: int = 0
    confidence: float = 1.0
    tools_called: List[str] = field(default_factory=list)
    status: str = "running"  # success, failure, partial, escalated
    error_message: Optional[str] = None
    output_summary: Optional[str] = None

    def finish(self, status: str = "success", error: Optional[str] = None) -> None:
        self.completed_at = time.time()
        self.latency_ms = (self.completed_at - self.started_at) * 1000.0
        self.status = status
        self.error_message = error


class CircuitBreaker:
    """Fable & Distributed Systems Circuit Breaker for agent actions."""

    def __init__(self, failure_threshold: int = 2, cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitBreakerState.CLOSED
        self.failure_streak = 0
        self.last_trip_time: Optional[float] = None

    def record_success(self) -> None:
        self.failure_streak = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED

    def record_failure(self) -> None:
        self.failure_streak += 1
        if self.failure_streak >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_trip_time = time.time()

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if self.last_trip_time and (time.time() - self.last_trip_time) > self.cooldown_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN allows single test execution


class MultiAgentManager:
    """Coordinates agent role scoping, trace logging, and fault containment."""

    def __init__(self, trace_dir: str = ".traces"):
        self.trace_dir = trace_dir
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        os.makedirs(self.trace_dir, exist_ok=True)

    def get_circuit_breaker(self, agent_role: str) -> CircuitBreaker:
        if agent_role not in self.circuit_breakers:
            self.circuit_breakers[agent_role] = CircuitBreaker(failure_threshold=2)
        return self.circuit_breakers[agent_role]

    def authorize_tool(self, role: AgentRole, tool_name: str) -> bool:
        """Enforces least-privilege boundary. Returns True if tool is permitted."""
        allowed = TOOL_PERMISSIONS.get(role, [])
        return tool_name in allowed

    def start_span(self, trace_id: str, agent_id: str, role: AgentRole, step: int) -> AgentSpan:
        """Initiates an observable trace span for an agent execution step."""
        return AgentSpan(
            trace_id=trace_id,
            span_id=str(uuid.uuid4())[:8],
            agent_id=agent_id,
            role=role.value,
            step=step,
            started_at=time.time()
        )

    def record_span(self, span: AgentSpan) -> None:
        """Persists the trace span to disk for full observability."""
        trace_file = os.path.join(self.trace_dir, f"trace_{span.trace_id}.jsonl")
        record = asdict(span)
        try:
            with open(trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as log_err:
            # Telemetry error handling without silent swallowing
            sys.stderr.write(f"Trace telemetry notice: {log_err}\n")

    def detect_contradictions(self, outputs: Dict[str, str]) -> List[str]:
        """Detects conflicting claims or opposing verdicts between peer agents."""
        contradictions = []
        verdicts = {}
        for agent_name, text in outputs.items():
            if "FAIL" in text:
                verdicts[agent_name] = "FAIL"
            elif "PASS" in text:
                verdicts[agent_name] = "PASS"

        if "FAIL" in verdicts.values() and "PASS" in verdicts.values():
            contradictions.append(
                f"Verdict contradiction detected between agents: {verdicts}"
            )
        return contradictions
