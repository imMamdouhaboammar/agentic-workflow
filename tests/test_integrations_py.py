#!/usr/bin/env python3
"""
test_integrations_py.py — Unit & Integration Tests for Supportive Tools Subsystem

Tests:
1. IntegrationsRegistry loading, querying, phase filtering, and dynamic extension.
2. IntegrationInstaller status checking, detection, and provisioning synchronization.
3. LifecycleDirector phase directives synthesis (Ponytail, TOON, Fable, Caveman).
4. LifecycleDirector pre-phase guards (Fable circuit breaker) and post-phase actions (Fable handoff).
"""

import os
import sys
import json
import unittest
import tempfile
import shutil

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.integrations.registry import (
    IntegrationDefinition,
    IntegrationsRegistry,
    get_default_registry
)
from core.integrations.installer import (
    IntegrationInstaller,
    InstallationStatus
)
from core.integrations.lifecycle_director import (
    LifecycleDirector,
    PhaseDirectives
)


class TestIntegrationsRegistry(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.registry = get_default_registry(self.project_dir)

    def test_default_registry_contains_foundation_tools(self):
        """Verify Ponytail, TOON, Fable, and Caveman are defined in default registry."""
        tools = [item.id for item in self.registry.list_all()]
        self.assertIn("ponytail", tools)
        self.assertIn("toon", tools)
        self.assertIn("fable", tools)
        self.assertIn("caveman", tools)

    def test_phase_filtering(self):
        """Verify get_for_phase returns matching tools plus continuous protocol tools."""
        planning_tools = [i.id for i in self.registry.get_for_phase("planning")]
        self.assertIn("ponytail", planning_tools)
        self.assertIn("fable", planning_tools)
        self.assertIn("toon", planning_tools)
        self.assertIn("caveman", planning_tools)

        impl_tools = [i.id for i in self.registry.get_for_phase("implementation")]
        self.assertIn("ponytail", impl_tools)
        self.assertIn("fable", impl_tools)

        handoff_tools = [i.id for i in self.registry.get_for_phase("handoff")]
        self.assertIn("fable", handoff_tools)
        self.assertIn("toon", handoff_tools)

    def test_dynamic_registration_and_persistence(self):
        """Verify adding new external sibling integrations dynamically."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_manifest = os.path.join(tmp_dir, "integrations.json")
            reg = IntegrationsRegistry()
            custom = IntegrationDefinition(
                id="custom-linter",
                name="Custom Linter",
                repo="https://github.com/example/custom-linter",
                description="Specialized code hygiene linter",
                category="code_quality",
                lifecycle_phases=["implementation", "verification"],
                install={"strategy": "skill"},
                directives={"verification": "Execute strict type check."}
            )
            reg.register(custom)
            reg.save_to_file(test_manifest)

            # Reload and verify
            reloaded = IntegrationsRegistry(manifest_path=test_manifest)
            item = reloaded.get("custom-linter")
            self.assertIsNotNone(item)
            self.assertEqual(item.name, "Custom Linter")
            self.assertIn("verification", item.lifecycle_phases)


class TestIntegrationInstaller(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.installer = IntegrationInstaller(self.project_dir)
        self.registry = get_default_registry(self.project_dir)

    def test_detection_across_agent_environments(self):
        """Verify installer accurately identifies installed supportive tools."""
        statuses = self.installer.check_all(self.registry)
        self.assertEqual(len(statuses), 5)

        status_map = {s.id: s for s in statuses}
        self.assertTrue(status_map["ponytail"].installed)
        self.assertTrue(status_map["toon"].installed)
        self.assertTrue(status_map["fable"].installed)
        self.assertTrue(status_map["caveman"].installed)
        self.assertTrue(status_map["omni-skill"].installed)

    def test_provision_all_idempotent(self):
        """Verify running provision_all executes cleanly and keeps statuses healthy."""
        statuses = self.installer.provision_all(self.registry)
        for s in statuses:
            self.assertTrue(s.installed, f"Integration {s.id} failed provisioning")


class TestLifecycleDirector(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.director = LifecycleDirector(self.project_dir)

    def test_planning_directives_synthesize_yagni_and_fable(self):
        """Verify Planning phase injects Ponytail YAGNI ladder and Fable contracts."""
        directives = self.director.get_phase_directives("planning")
        self.assertIn("Ponytail", directives.active_integrations)
        self.assertIn("Fable (get-fable)", directives.active_integrations)
        self.assertIn("TOON (Token-Oriented Object Notation)", directives.active_integrations)
        self.assertIn("Caveman", directives.active_integrations)

        # Check prompt content
        prompt = directives.system_prompt_overlay
        self.assertIn("YAGNI", prompt)
        self.assertIn("Ponytail Ladder", prompt)
        self.assertIn("TOON v4.1", prompt)
        self.assertIn("Caveman", prompt)

    def test_implementation_directives_synthesize_surgical_diff(self):
        """Verify Implementation phase injects Ponytail surgical diff and Fable circuit breaker."""
        directives = self.director.get_phase_directives("implementation")
        prompt = directives.system_prompt_overlay
        self.assertIn("Shortest working diff wins", prompt)
        self.assertIn("Circuit Breaker", prompt)

    def test_fable_circuit_breaker_guard(self):
        """Verify pre-phase guard halts execution when consecutive failure streak >= 2."""
        # Normal execution
        ok_res = self.director.execute_pre_phase_guards("implementation", {"failure_streak": 0})
        self.assertTrue(ok_res["allowed"])

        # Tripped circuit breaker
        tripped_res = self.director.execute_pre_phase_guards("implementation", {"failure_streak": 2})
        self.assertFalse(tripped_res["allowed"])
        self.assertIn("trip_circuit_breaker", tripped_res["actions_taken"])

    def test_handoff_post_phase_action(self):
        """Verify handoff post-phase action creates durable .fable continuation state."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            director = LifecycleDirector(project_dir=tmp_dir)
            post_res = director.execute_post_phase_actions("handoff", {
                "trace_id": "test_trace_123",
                "next_action": "Run regression test suite."
            })
            self.assertTrue(post_res["success"])
            fable_state = os.path.join(tmp_dir, ".fable", "state.json")
            fable_progress = os.path.join(tmp_dir, ".fable", "PROGRESS.md")
            self.assertTrue(os.path.isfile(fable_state))
            self.assertTrue(os.path.isfile(fable_progress))

            with open(fable_state, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            self.assertEqual(state_data["trace_id"], "test_trace_123")
            self.assertEqual(state_data["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
