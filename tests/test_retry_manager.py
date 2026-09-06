"""
test_retry_manager.py — Test suite for Sisyphus Persistence (retry_manager.py)

Covers:
  - FailureClassification enum values
  - RetryApproach enum values
  - FailureContext dataclass field presence
  - RetryBudget: slot allocation, budget exhaustion, history serialisation
  - ErrorClassifier: pattern-based classification for all three failure types
  - ApproachSelector: 3-attempt sequence per failure class + out-of-range guard
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "hooks", "scripts"))

from retry_manager import (
    FailureClassification,
    RetryApproach,
    FailureContext,
    RetryAttempt,
    RetryBudget,
    ErrorClassifier,
    ApproachSelector,
)


class TestFailureClassificationEnum(unittest.TestCase):
    def test_enum_members_exist(self):
        self.assertEqual(FailureClassification.TRANSIENT.value, "transient")
        self.assertEqual(FailureClassification.LOGIC.value, "logic")
        self.assertEqual(FailureClassification.RESOURCE.value, "resource")

    def test_enum_is_exhaustive(self):
        members = {m.value for m in FailureClassification}
        self.assertEqual(members, {"transient", "logic", "resource"})


class TestRetryApproachEnum(unittest.TestCase):
    def test_approach_values(self):
        self.assertEqual(RetryApproach.APPROACH_A.value, "approach-A")
        self.assertEqual(RetryApproach.APPROACH_B.value, "approach-B")
        self.assertEqual(RetryApproach.APPROACH_C.value, "approach-C")


class TestFailureContextDataclass(unittest.TestCase):
    def test_required_fields_present(self):
        ctx = FailureContext(
            step_id="step-research",
            stage_name="Research",
            error_message="timeout",
            failure_type=FailureClassification.TRANSIENT,
        )
        self.assertEqual(ctx.step_id, "step-research")
        self.assertEqual(ctx.stage_name, "Research")
        self.assertEqual(ctx.failure_type, FailureClassification.TRANSIENT)

    def test_optional_fields_default_to_none(self):
        ctx = FailureContext(
            step_id="step-plan",
            stage_name="Planning",
            error_message="logic error",
            failure_type=FailureClassification.LOGIC,
        )
        self.assertIsNone(ctx.deliverable_path)
        self.assertIsNone(ctx.pacs_score)

    def test_timestamp_is_utc(self):
        ctx = FailureContext(
            step_id="step-impl",
            stage_name="Implementation",
            error_message="rate limit",
            failure_type=FailureClassification.RESOURCE,
        )
        self.assertTrue(ctx.timestamp.endswith("Z"), f"Expected UTC 'Z' suffix, got: {ctx.timestamp}")


class TestRetryBudget(unittest.TestCase):
    def test_three_attempts_allocated_in_sequence(self):
        budget = RetryBudget("step-research", max_attempts=3)
        a1 = budget.next_attempt(RetryApproach.APPROACH_A)
        a2 = budget.next_attempt(RetryApproach.APPROACH_B)
        a3 = budget.next_attempt(RetryApproach.APPROACH_C)
        self.assertEqual(a1.attempt_number, 1)
        self.assertEqual(a2.attempt_number, 2)
        self.assertEqual(a3.attempt_number, 3)
        self.assertEqual(a1.approach, RetryApproach.APPROACH_A)
        self.assertEqual(a3.approach, RetryApproach.APPROACH_C)

    def test_budget_exhausted_after_max_attempts(self):
        budget = RetryBudget("step-research", max_attempts=3)
        for approach in [RetryApproach.APPROACH_A, RetryApproach.APPROACH_B, RetryApproach.APPROACH_C]:
            budget.next_attempt(approach)
        self.assertTrue(budget.is_budget_exhausted())
        self.assertIsNone(budget.next_attempt(RetryApproach.APPROACH_A))

    def test_budget_max_one_exhausted_immediately(self):
        budget = RetryBudget("step-quick", max_attempts=1)
        budget.next_attempt(RetryApproach.APPROACH_A)
        self.assertTrue(budget.is_budget_exhausted())

    def test_complete_attempt_records_status(self):
        budget = RetryBudget("step-research", max_attempts=3)
        budget.next_attempt(RetryApproach.APPROACH_A)
        budget.complete_attempt(verification_status="FAIL", pacs_score=42, failure_reason="shallow output")
        history = budget.get_retry_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["verification_status"], "FAIL")
        self.assertEqual(history[0]["pacs_score"], 42)
        self.assertEqual(history[0]["failure_reason"], "shallow output")

    def test_retry_history_serialisation_keys(self):
        budget = RetryBudget("step-plan", max_attempts=3)
        budget.next_attempt(RetryApproach.APPROACH_B)
        budget.complete_attempt(verification_status="PASS", pacs_score=88)
        entry = budget.get_retry_history()[0]
        required_keys = {"attempt", "approach", "timestamp_start", "timestamp_end",
                         "output_path", "verification_status", "pacs_score", "failure_reason"}
        self.assertEqual(required_keys, set(entry.keys()))


class TestErrorClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ErrorClassifier()

    def test_timeout_is_transient(self):
        self.assertEqual(self.classifier.classify("Request timeout after 30s"), FailureClassification.TRANSIENT)

    def test_connection_reset_is_transient(self):
        self.assertEqual(self.classifier.classify("connection reset by peer"), FailureClassification.TRANSIENT)

    def test_missing_section_is_logic(self):
        self.assertEqual(self.classifier.classify("missing section: References"), FailureClassification.LOGIC)

    def test_contradiction_is_logic(self):
        self.assertEqual(self.classifier.classify("contradiction detected in argument"), FailureClassification.LOGIC)

    def test_rate_limit_is_resource(self):
        self.assertEqual(self.classifier.classify("rate limit exceeded"), FailureClassification.RESOURCE)

    def test_unknown_error_returns_valid_classification(self):
        result = self.classifier.classify("something completely unrecognised xyz")
        self.assertIsInstance(result, FailureClassification)


class TestApproachSelector(unittest.TestCase):
    def setUp(self):
        self.selector = ApproachSelector()

    def test_all_three_failure_types_produce_approach_sequence(self):
        for fc in [FailureClassification.TRANSIENT, FailureClassification.LOGIC, FailureClassification.RESOURCE]:
            with self.subTest(fc=fc):
                self.assertEqual(self.selector.select_approach_for_attempt(fc, 1), RetryApproach.APPROACH_A)
                self.assertEqual(self.selector.select_approach_for_attempt(fc, 2), RetryApproach.APPROACH_B)
                self.assertEqual(self.selector.select_approach_for_attempt(fc, 3), RetryApproach.APPROACH_C)

    def test_attempt_zero_returns_none(self):
        self.assertIsNone(self.selector.select_approach_for_attempt(FailureClassification.TRANSIENT, 0))

    def test_attempt_four_returns_none(self):
        self.assertIsNone(self.selector.select_approach_for_attempt(FailureClassification.TRANSIENT, 4))

    def test_describe_approach_returns_non_empty_string(self):
        desc = self.selector.describe_approach(RetryApproach.APPROACH_A, FailureClassification.TRANSIENT)
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
