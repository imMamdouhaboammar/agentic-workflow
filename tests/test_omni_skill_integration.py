"""
Unit tests for OmniSkill integration, dynamic DAG generation, and lifecycle directives.
"""

import unittest
import os
from core.integrations.registry import get_default_registry
from core.integrations.installer import IntegrationInstaller
from core.integrations.lifecycle_director import LifecycleDirector
from core.autopilot_engine import AutopilotEngine


class TestOmniSkillIntegration(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.abspath(".")
        self.registry = get_default_registry(self.project_dir)
        self.installer = IntegrationInstaller(self.project_dir)
        self.lifecycle_director = LifecycleDirector(self.project_dir, self.registry)

    def test_omni_skill_registered_in_registry(self):
        omni = self.registry.get("omni-skill")
        self.assertIsNotNone(omni)
        self.assertEqual(omni.name, "OmniSkill")
        self.assertEqual(omni.category, "skill_engine")
        self.assertIn("planning", omni.lifecycle_phases)
        self.assertIn("verification", omni.lifecycle_phases)

    def test_omni_skill_detection_by_installer(self):
        omni = self.registry.get("omni-skill")
        self.assertIsNotNone(omni)
        status = self.installer.check_status(omni)
        self.assertTrue(status.installed)
        self.assertEqual(status.status, "INSTALLED")
        self.assertTrue(len(status.locations) > 0)

    def test_planning_directives_include_omni_skill(self):
        directives = self.lifecycle_director.get_phase_directives("planning")
        self.assertIn("OmniSkill", directives.active_integrations)
        self.assertIn("OmniSkill Dynamic Router", directives.system_prompt_overlay)

    def test_verification_directives_include_omni_skill(self):
        directives = self.lifecycle_director.get_phase_directives("verification")
        self.assertIn("OmniSkill", directives.active_integrations)
        self.assertIn("OmniSkill 4-Layer Validation", directives.system_prompt_overlay)

    def test_autopilot_plan_from_dag(self):
        engine = AutopilotEngine(project_dir=self.project_dir, auto_approve=True)
        custom_dag = [
            {
                "name": "Custom Intelligence Step",
                "stage": "research",
                "role": "researcher",
                "deliverable_path": "docs/custom_research.md",
                "criteria": ["Baseline verified"]
            },
            {
                "name": "Custom Execution Step",
                "stage": "implementation",
                "role": "engineer",
                "deliverable_path": "docs/custom_impl.md",
                "criteria": ["Code implemented"]
            }
        ]
        engine.plan_from_dag(custom_dag, title="DAG Test", goal="Verify OmniSkill DAG Planning")
        self.assertEqual(len(engine.steps), 2)
        self.assertEqual(engine.steps[0].name, "Custom Intelligence Step")
        self.assertEqual(engine.steps[1].name, "Custom Execution Step")


if __name__ == "__main__":
    unittest.main()
