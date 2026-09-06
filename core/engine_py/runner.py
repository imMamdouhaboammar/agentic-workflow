#!/usr/bin/env python3
"""
runner.py — CLI entry point for Python Agentic Engine.
"""

import os
import sys
import asyncio

# Ensure project root is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.engine_py.models import (
    WorkflowDefinition, StageDefinition, TaskDefinition, AgentRole
)
from core.engine_py.queue import InMemoryTaskQueue
from core.engine_py.event_bus import AsyncEventBus
from core.engine_py.verification_controller import VerificationController
from core.engine_py.system_workers import SystemWorker
from core.engine_py.agent_worker import AgentWorker
from core.engine_py.executor import AgenticExecutor


async def main():
    project_dir = os.getcwd()
    print("🚀 [engine-py] Starting Event-Driven Agentic Engine (Python AsyncIO)...")

    wf_def = WorkflowDefinition(
        name="autonomous_agentic_pipeline",
        version="1.0.0",
        stages=[
            StageDefinition(
                id="stage_01_research",
                name="Stage 1: Research",
                tasks=[
                    TaskDefinition(
                        id="task_research_01",
                        name="Analyze System Architecture and Dependencies",
                        type="agent.task",
                        role=AgentRole.RESEARCHER,
                        deliverable_path="docs/research_findings.md",
                        criteria=["Analyze architecture patterns", "Establish baseline"]
                    )
                ]
            ),
            StageDefinition(
                id="stage_02_planning",
                name="Stage 2: Planning",
                tasks=[
                    TaskDefinition(
                        id="task_plan_approval",
                        name="Autopilot Plan Approval",
                        type="agent.human",
                        role=AgentRole.ORCHESTRATOR
                    )
                ]
            ),
            StageDefinition(
                id="stage_03_implementation",
                name="Stage 3: Implementation",
                tasks=[
                    TaskDefinition(
                        id="task_code_impl",
                        name="Implement Core Production Logic",
                        type="agent.task",
                        role=AgentRole.ENGINEER,
                        deliverable_path="docs/implementation_summary.md",
                        criteria=["Pass unit tests", "Generate comprehensive documentation"]
                    ),
                    TaskDefinition(
                        id="task_review_01",
                        name="Adversarial Code & Fact-Check Review",
                        type="agent.review",
                        role=AgentRole.REVIEWER,
                        deliverable_path="review-logs/step-3-review.md",
                        criteria=["Zero critical vulnerabilities"]
                    )
                ]
            )
        ]
    )

    queue = InMemoryTaskQueue()
    ledger_path = os.path.join(project_dir, "ledger.jsonl")
    event_bus = AsyncEventBus(ledger_path=ledger_path)
    verifier = VerificationController(project_dir=project_dir)

    sys_worker = SystemWorker(worker_id="sys_worker_py", queue=queue, event_bus=event_bus, verification_controller=verifier)
    agent_worker = AgentWorker(worker_id="agent_worker_py", queue=queue, event_bus=event_bus, verification_controller=verifier, project_dir=project_dir)

    executor = AgenticExecutor(
        workflow_def=wf_def,
        queue=queue,
        event_bus=event_bus,
        project_dir=project_dir,
        sot_filename="state.yaml"
    )

    print(f"⚡ Trace ID: {executor.instance.trace_id}")
    print(f"⚡ Workflow ID: {executor.instance.workflow_id}")
    print(f"⚡ SOT Path: {executor.sot_path}")

    success = await executor.run_until_complete(workers=[sys_worker, agent_worker], poll_interval=0.02, max_iterations=50)

    if success:
        print("\n🎉 [engine-py] Workflow Completed Successfully with All Gates Verified!")
        sys.exit(0)
    else:
        print("\n❌ [engine-py] Workflow execution halted or failed gates.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
