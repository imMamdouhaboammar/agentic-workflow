#!/usr/bin/env python3
"""
test_skills_indexer.py — Comprehensive Unit Tests for Agentic Skills Mesh & Indexer
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch

from core.skills_indexer import (
    NodeType, AgenticNode, FrontmatterParser, NodeClassifier,
    TriggerExtractor, EdgeResolver, ToonFormatter, SkillScanner,
    AgenticSkillsMesh
)
from core.autopilot_engine import AutopilotEngine, WorkflowStep
from core.multi_agent_system import AgentRole


class TestSkillsIndexer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agentic_skills_test_")
        # Ensure a mock skill exists in self.test_dir so skills_mesh has hermetic skills available
        skill_dir = os.path.join(self.test_dir, ".claude", "skills", "test-guard")
        os.makedirs(skill_dir, exist_ok=True)
        with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("""---
name: test-guard
description: Automated test execution and clean code auditor
tags: [guard, test, code]
---
# Test Guard
""")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_frontmatter_parser(self):
        content = """---
name: test-skill
description: A mock skill for automated testing
version: 2.1.0
tags: [unit-test, mock, agent]
---
# Test Skill Body
This is the markdown body of the skill.
"""
        fm, body = FrontmatterParser.parse_markdown(content)
        self.assertEqual(fm.get("name"), "test-skill")
        self.assertEqual(fm.get("version"), "2.1.0")
        self.assertIn("unit-test", fm.get("tags", []))
        self.assertIn("# Test Skill Body", body)

    def test_node_classifier(self):
        # Guard
        self.assertEqual(
            NodeClassifier.classify("clean-code-guard", "Clean Code Guard", "Audits code against SOLID", ""),
            NodeType.GUARD
        )
        # Agent
        self.assertEqual(
            NodeClassifier.classify("agency-api-tester", "API Tester", "Tests endpoints", ""),
            NodeType.AGENT
        )
        # Workflow
        self.assertEqual(
            NodeClassifier.classify("gsd-plan-phase", "Plan Phase", "Designs roadmap phases", ""),
            NodeType.WORKFLOW
        )
        # Playbook
        self.assertEqual(
            NodeClassifier.classify("api-design", "API Design", "API design guide", "Step 1: Define endpoints"),
            NodeType.PLAYBOOK
        )
        # Default Skill
        self.assertEqual(
            NodeClassifier.classify("simple-helper", "Simple Helper", "General helper utility", "Does things"),
            NodeType.SKILL
        )

    def test_trigger_and_tool_extractor(self):
        node_id = "test-worker"
        name = "Test Worker"
        desc = "Runs bash scripts and reviews files"
        body = """
Use the `run_command` and `view_file` tools to inspect code.
Trigger via /fable-run or /test-now.
"""
        triggers = TriggerExtractor.extract_triggers(node_id, name, desc, body, ["testing"])
        self.assertIn("/fable-run", triggers)
        self.assertIn("/test-now", triggers)
        self.assertIn("testing", triggers)

        tools = TriggerExtractor.extract_tools(body)
        self.assertIn("run_command", tools)
        self.assertIn("view_file", tools)

    def test_toon_serialization_and_deserialization(self):
        node = AgenticNode(
            id="mock-guard",
            name="Mock Guard",
            type=NodeType.GUARD,
            path="/path/to/mock/SKILL.md",
            description="Enforces mock invariants and test safety.",
            version="1.0.0",
            tags=["safety", "mock"],
            triggers=["mock", "safety", "/mock"],
            tools_required=["view_file", "run_command"],
            rules_and_guards=["enforce-mock-guard"],
            edges=["test-guard"]
        )

        toon_str = ToonFormatter.format_node(node)
        self.assertIn("@node:mock-guard [type:guard, name:\"Mock Guard\"", toon_str)
        self.assertIn("tools:run_command,view_file", toon_str)
        self.assertIn("summary:Enforces mock invariants and test safety.", toon_str)

        mesh_toon = ToonFormatter.serialize_mesh([node])
        parsed = ToonFormatter.parse_toon(mesh_toon)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], "mock-guard")
        self.assertEqual(parsed[0]["type"], "guard")
        self.assertEqual(parsed[0]["path"], "/path/to/mock/SKILL.md")
        self.assertIn("enforce-mock-guard", parsed[0]["rules_and_guards"])

    def test_scanner_and_indexer_in_temp_directory(self):
        # Create mock skill directory structure
        skill1_dir = os.path.join(self.test_dir, "skills", "mock-agent")
        os.makedirs(skill1_dir, exist_ok=True)
        with open(os.path.join(skill1_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("""---
name: mock-agent
description: Specialized mock engineer for integration testing
tags: [agent, mock]
---
# Mock Agent
Executes tasks using `run_command`.
""")

        skill2_dir = os.path.join(self.test_dir, "skills", "mock-guard")
        os.makedirs(skill2_dir, exist_ok=True)
        with open(os.path.join(skill2_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("""---
name: mock-guard
description: Security guard blocking unsafe operations
tags: [guard, safety]
---
# Mock Guard
Guards production code.
""")

        skills_dir = os.path.join(self.test_dir, "skills")
        mesh = AgenticSkillsMesh(project_dir=self.test_dir, candidate_dirs=[skills_dir])
        nodes = mesh.scan()
        self.assertIn("mock-agent", nodes)
        self.assertIn("mock-guard", nodes)
        self.assertEqual(nodes["mock-guard"].type, NodeType.GUARD)

        json_path, toon_path = mesh.build_index(output_dir=self.test_dir)
        self.assertTrue(os.path.isfile(json_path))
        self.assertTrue(os.path.isfile(toon_path))

        # Test search & resolve
        search_res = mesh.search("security")
        self.assertTrue(any(n.id == "mock-guard" for n in search_res))

        resolve_res = mesh.resolve_for_intent("run test and check security")
        self.assertTrue(len(resolve_res) > 0)

    def test_autopilot_engine_skills_mesh_binding(self):
        engine = AutopilotEngine(project_dir=self.test_dir, auto_approve=True)
        self.assertIsNotNone(engine.skills_mesh)

        step = WorkflowStep(
            step_id=1,
            name="Verify code cleanliness and unit tests",
            stage="implementation",
            deliverable_path="docs/summary.md",
            agent_role=AgentRole.ENGINEER,
            criteria=["Implement features", "Pass unit tests", "Audit clean code"]
        )

        engine.execute_step(step)
        self.assertTrue(len(step.skills) > 0)

        decision_file = os.path.join(self.test_dir, "autopilot-logs", "step-1-decision.md")
        self.assertTrue(os.path.isfile(decision_file))
        with open(decision_file, "r", encoding="utf-8") as f:
            log_content = f.read()
        self.assertIn("Bound Skills/Nodes:", log_content)


if __name__ == "__main__":
    unittest.main()
