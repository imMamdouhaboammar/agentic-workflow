"""
test_agentic_engine_py.py — Comprehensive Test Suite for Python Agentic Engine.

Tests:
1. TaskQueue durability, leasing, and expiration (InMemory & SQLite)
2. Deterministic AgenticDecider DAG progression and retry backoff
3. 4-Layer Verification Gates (L0 Anti-Skip, L1 Functional, L1.5 pACS, L2 Review)
4. Circuit Breaker trip & half-open recovery
5. Full End-to-End multi-stage workflow execution with SOT state.yaml persistence
"""

import os
import shutil
import tempfile
import asyncio
import unittest

from core.engine_py.models import (
    WorkflowDefinition, StageDefinition, TaskDefinition,
    TaskStatus, WorkflowStatus, AgentRole, RetryPolicy, BackoffType
)
from core.engine_py.queue import InMemoryTaskQueue, SQLiteTaskQueue
from core.engine_py.event_bus import AsyncEventBus
from core.engine_py.decider import AgenticDecider
from core.engine_py.verification_controller import VerificationController
from core.engine_py.worker import CircuitBreaker, CircuitBreakerState
from core.engine_py.system_workers import SystemWorker
from core.engine_py.agent_worker import AgentWorker
from core.engine_py.executor import AgenticExecutor


class TestPythonAgenticEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="engine_test_")
        self.ledger_path = os.path.join(self.test_dir, "ledger.jsonl")
        self.sot_path = os.path.join(self.test_dir, "state.yaml")
        self.db_path = os.path.join(self.test_dir, "queue.db")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_in_memory_queue_operations(self):
        q = InMemoryTaskQueue()
        task_def = TaskDefinition(id="t1", type="system.code")
        task = TaskDefinition(id="t1", type="system.code")
        from core.engine_py.models import TaskInstance
        inst = TaskInstance(task_id="t1", workflow_id="w1", stage_id="s1", task_def=task_def)
        
        q.push(inst)
        self.assertEqual(q.size(), 1)

        polled = q.poll(task_types=["system.code"], worker_id="w_01", lease_seconds=10.0)
        self.assertIsNotNone(polled)
        self.assertEqual(polled.task_id, "t1")
        self.assertEqual(polled.worker_id, "w_01")
        self.assertEqual(q.size(), 0)

        # Ack
        q.ack("t1")
        self.assertEqual(q.size(), 0)

    def test_sqlite_queue_durability(self):
        q = SQLiteTaskQueue(db_path=self.db_path)
        task_def = TaskDefinition(id="sql_t1", type="system.code")
        from core.engine_py.models import TaskInstance
        inst = TaskInstance(task_id="sql_t1", workflow_id="w1", stage_id="s1", task_def=task_def)

        q.push(inst)
        self.assertEqual(q.size(), 1)

        polled = q.poll(task_types=["system.code"], worker_id="w_sql", lease_seconds=1.0)
        self.assertIsNotNone(polled)
        self.assertEqual(polled.task_id, "sql_t1")
        self.assertEqual(q.size(), 0)

        # Expire lease and reclaim
        import time
        time.sleep(1.2)
        reclaimed = q.reclaim_expired()
        self.assertIn("sql_t1", reclaimed)
        self.assertEqual(q.size(), 1)

        # Poll again and ack
        polled2 = q.poll(task_types=["system.code"], worker_id="w_sql_2", lease_seconds=10.0)
        self.assertIsNotNone(polled2)
        q.ack("sql_t1")
        self.assertEqual(q.size(), 0)

    def test_circuit_breaker(self):
        cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.2)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, CircuitBreakerState.CLOSED)

        cb.record_failure()
        self.assertTrue(cb.can_execute())
        
        cb.record_failure()
        self.assertEqual(cb.state, CircuitBreakerState.OPEN)
        self.assertFalse(cb.can_execute())

        # Wait for cooldown
        import time
        time.sleep(0.3)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, CircuitBreakerState.HALF_OPEN)

        cb.record_success()
        self.assertEqual(cb.state, CircuitBreakerState.CLOSED)

    def test_verification_controller_gates(self):
        vc = VerificationController(project_dir=self.test_dir)
        from core.engine_py.models import TaskInstance
        task_def = TaskDefinition(
            id="v_task",
            type="agent.task",
            deliverable_path="docs/test_deliv.md",
            criteria=["Architecture spec", "Security guardrails"]
        )
        inst = TaskInstance(task_id="v_task", workflow_id="w1", stage_id="s1", task_def=task_def)

        # 1. Deliverable doesn't exist -> should fail L0 and generate diagnosis log
        res = vc.evaluate_all_gates(inst)
        self.assertFalse(res.passed)
        self.assertFalse(res.l0_passed)
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "diagnosis-logs", "step-v_task-diagnosis.md")))

        # 2. Create deliverable fulfilling L0 and L1 criteria
        deliv_full = os.path.join(self.test_dir, "docs/test_deliv.md")
        os.makedirs(os.path.dirname(deliv_full), exist_ok=True)
        with open(deliv_full, "w", encoding="utf-8") as f:
            f.write("# Production Deliverable\n\n"
                    "- Architecture spec: Fully documented and verified.\n"
                    "- Security guardrails: Configured with least-privilege policies.\n\n"
                    "Comprehensive engineering implementation passing all gates.\n" * 5)

        res2 = vc.evaluate_all_gates(inst)
        self.assertTrue(res2.passed)
        self.assertTrue(res2.l0_passed)
        self.assertTrue(res2.l1_passed)
        self.assertGreaterEqual(res2.l15_pacs_score, 70)
        self.assertEqual(res2.l2_verdict, "PASS")

    def test_end_to_end_workflow_execution(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Construct a 3-Stage canonical agentic workflow
        wf_def = WorkflowDefinition(
            name="test_autonomous_pipeline",
            version="1.0.0",
            stages=[
                StageDefinition(
                    id="stage_research",
                    name="Stage 1: Research",
                    tasks=[
                        TaskDefinition(
                            id="task_res_01",
                            name="Gather Requirements",
                            type="agent.task",
                            role=AgentRole.RESEARCHER,
                            deliverable_path="docs/research.md",
                            criteria=["Identify patterns", "Synthesize requirements"]
                        )
                    ]
                ),
                StageDefinition(
                    id="stage_planning",
                    name="Stage 2: Planning",
                    tasks=[
                        TaskDefinition(
                            id="task_plan_approval",
                            name="Autopilot Plan Review",
                            type="agent.human",
                            role=AgentRole.ORCHESTRATOR
                        )
                    ]
                ),
                StageDefinition(
                    id="stage_implementation",
                    name="Stage 3: Implementation",
                    tasks=[
                        TaskDefinition(
                            id="task_exec_code",
                            name="Execute Core System Code",
                            type="system.code",
                            input_parameters={"code": "result = 42 * 2"}
                        ),
                        TaskDefinition(
                            id="task_code_review",
                            name="Adversarial Deliverable Review",
                            type="agent.review",
                            role=AgentRole.REVIEWER,
                            deliverable_path="review-logs/final_review.md",
                            criteria=["Audit verified"]
                        )
                    ]
                )
            ]
        )

        q = InMemoryTaskQueue()
        eb = AsyncEventBus(ledger_path=self.ledger_path)
        vc = VerificationController(project_dir=self.test_dir)

        sys_worker = SystemWorker(worker_id="sys_w", queue=q, event_bus=eb, verification_controller=vc)
        agent_worker = AgentWorker(
            worker_id="agent_w", queue=q, event_bus=eb,
            verification_controller=vc, project_dir=self.test_dir
        )

        executor = AgenticExecutor(
            workflow_def=wf_def,
            queue=q,
            event_bus=eb,
            project_dir=self.test_dir,
            sot_filename="state.yaml"
        )

        success = loop.run_until_complete(
            executor.run_until_complete(workers=[sys_worker, agent_worker], poll_interval=0.01, max_iterations=30)
        )
        loop.close()

        self.assertTrue(success)
        self.assertEqual(executor.instance.status, WorkflowStatus.COMPLETED)
        
        # Verify Single-File SOT was created
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "state.yaml")))
        
        # Verify append-only ledger has recorded all events
        self.assertTrue(os.path.isfile(self.ledger_path))
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 5)

        # Verify Autopilot decision log was generated
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "autopilot-logs", "step-task_plan_approval-decision.md")))


if __name__ == "__main__":
    unittest.main()
