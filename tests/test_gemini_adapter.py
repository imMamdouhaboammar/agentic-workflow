"""
Unit tests for Google Antigravity & Gemini CLI Hook Driver Adapter (Python).
"""

import unittest
from core.hooks.types import HookSource, HookType, HookVerdict
from core.hooks.policy_engine import UniversalPolicyEngine
from core.hooks.adapters.gemini_adapter import GeminiHookAdapter


class TestGeminiHookAdapter(unittest.TestCase):

    def setUp(self):
        self.engine = UniversalPolicyEngine()
        self.adapter = GeminiHookAdapter(self.engine)

    def test_parse_run_command_payload(self):
        payload = {
            "tool_name": "run_command",
            "args": {
                "CommandLine": "echo 'hello world'",
                "Cwd": "/tmp"
            }
        }
        event = self.adapter.parse_payload(payload, HookType.PRE_TOOL)
        self.assertIsNotNone(event)
        self.assertEqual(event.source, HookSource.ANTIGRAVITY)
        self.assertEqual(event.tool_name, "run_command")
        self.assertEqual(event.command, "echo 'hello world'")

    def test_blocks_destructive_command_on_gemini(self):
        payload = {
            "tool_name": "run_command",
            "args": {
                "CommandLine": "rm -rf / --no-preserve-root"
            }
        }
        result = self.adapter.handle(payload, HookType.PRE_TOOL)
        self.assertEqual(result.verdict, HookVerdict.BLOCK)
        self.assertIn("DESTRUCTIVE COMMAND BLOCKED", result.message)

    def test_evaluates_tool_call_helper(self):
        # Benign command
        res = self.adapter.evaluate_tool_call("run_command", {"CommandLine": "git status"})
        self.assertEqual(res.verdict, HookVerdict.ALLOW)

        # Destructive command
        res_block = self.adapter.evaluate_tool_call("run_command", {"CommandLine": "git reset --hard HEAD~10"})
        self.assertEqual(res_block.verdict, HookVerdict.BLOCK)

    def test_file_write_path_extraction(self):
        payload = {
            "tool_name": "write_to_file",
            "args": {
                "TargetFile": "/path/to/source.py",
                "CodeContent": "print(1)"
            }
        }
        event = self.adapter.parse_payload(payload, HookType.PRE_TOOL)
        self.assertIsNotNone(event)
        self.assertEqual(event.file_path, "/path/to/source.py")


if __name__ == "__main__":
    unittest.main()
