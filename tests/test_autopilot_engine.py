import unittest
import os
import shutil
from core.autopilot_engine import AutopilotEngine, EnergyBudget


class TestAutopilotEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = ".test_autopilot_workspace"
        os.makedirs(self.test_dir, exist_ok=True)
        self.engine = AutopilotEngine(project_dir=self.test_dir, auto_approve=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_energy_budget_and_refueling(self):
        budget = EnergyBudget(max_energy_tokens=1000)
        self.assertEqual(budget.remaining_energy, 1000)
        self.assertEqual(budget.energy_percentage, 100.0)

        # Consume 850 tokens (leaving 15% -> needs refuel)
        budget.consume(850)
        self.assertTrue(budget.needs_refuel())

        budget.refuel("snap-1")
        self.assertEqual(budget.refuel_count, 1)
        self.assertFalse(budget.needs_refuel())

    def test_full_autopilot_run(self):
        self.engine.plan_default_workflow(
            title="Test Workflow",
            goal="Validate autonomous execution"
        )
        self.assertEqual(len(self.engine.steps), 3)
        success = self.engine.run_all()
        self.assertTrue(success)

        # Check that deliverables and logs were created
        sot_path = os.path.join(self.test_dir, "state.yaml")
        self.assertTrue(os.path.exists(sot_path))

        decision_file = os.path.join(self.test_dir, "autopilot-logs", "step-1-decision.md")
        self.assertTrue(os.path.exists(decision_file))


if __name__ == "__main__":
    unittest.main()
