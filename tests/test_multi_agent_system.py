import unittest
import os
import shutil
from core.multi_agent_system import (
    MultiAgentManager,
    AgentRole,
    CircuitBreaker,
    CircuitBreakerState
)


class TestMultiAgentSystem(unittest.TestCase):
    def setUp(self):
        self.test_trace_dir = ".test_traces"
        self.manager = MultiAgentManager(trace_dir=self.test_trace_dir)

    def tearDown(self):
        if os.path.exists(self.test_trace_dir):
            shutil.rmtree(self.test_trace_dir)

    def test_least_privilege_tool_authorization(self):
        # Reviewer cannot write files
        self.assertFalse(self.manager.authorize_tool(AgentRole.REVIEWER, "write_file"))
        # Reviewer can rate pacs
        self.assertTrue(self.manager.authorize_tool(AgentRole.REVIEWER, "rate_pacs"))
        # Engineer can write files
        self.assertTrue(self.manager.authorize_tool(AgentRole.ENGINEER, "write_file"))

    def test_circuit_breaker_trips_on_streak(self):
        cb = CircuitBreaker(failure_threshold=2)
        self.assertEqual(cb.state, CircuitBreakerState.CLOSED)
        self.assertTrue(cb.can_execute())

        cb.record_failure()
        self.assertEqual(cb.state, CircuitBreakerState.CLOSED)

        cb.record_failure()
        self.assertEqual(cb.state, CircuitBreakerState.OPEN)
        self.assertFalse(cb.can_execute())

        cb.record_success()
        self.assertEqual(cb.failure_streak, 0)

    def test_trace_span_recording(self):
        span = self.manager.start_span("trace-123", "agent-1", AgentRole.RESEARCHER, 1)
        span.finish(status="success")
        self.manager.record_span(span)

        trace_file = os.path.join(self.test_trace_dir, "trace_trace-123.jsonl")
        self.assertTrue(os.path.exists(trace_file))
        with open(trace_file, "r", encoding="utf-8") as f:
            line = f.readline()
            self.assertIn("trace-123", line)
            self.assertIn("researcher", line)

    def test_contradiction_detection(self):
        outputs = {
            "reviewer_a": "L1 verification: PASS",
            "reviewer_b": "L1 verification: FAIL"
        }
        contradictions = self.manager.detect_contradictions(outputs)
        self.assertEqual(len(contradictions), 1)


if __name__ == "__main__":
    unittest.main()
