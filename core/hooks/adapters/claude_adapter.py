"""
Claude Code Hook Adapter
========================
Consumes native Claude Code PreToolUse, PostToolUse, and Session lifecycle hooks.
Interprets stdin JSON, normalizes to HookEvent, and controls Claude via exit codes (0 vs 2).
"""

import json
import sys
from typing import Any, Dict, Optional

from ..types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
)
from ..policy_engine import UniversalPolicyEngine


class ClaudeHookAdapter:
    """Consumes and mediates Claude Code lifecycle hooks."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def parse_payload(self, raw_input: str, hook_type: HookType = HookType.PRE_TOOL) -> Optional[HookEvent]:
        try:
            data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        tool_name = data.get("tool_name") or data.get("name")
        tool_input = data.get("tool_input") or data.get("input") or {}
        tool_response = data.get("tool_response") or data.get("output")

        command = None
        file_path = None

        if isinstance(tool_input, dict):
            command = tool_input.get("command")
            file_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("target")

        return HookEvent(
            source=HookSource.CLAUDE,
            hook_type=hook_type,
            tool_name=tool_name,
            command=command,
            file_path=file_path,
            args=tool_input if isinstance(tool_input, dict) else {"raw": tool_input},
            output=tool_response,
            metadata={"raw_claude_payload": data},
        )

    def handle(self, raw_input: str, hook_type: HookType = HookType.PRE_TOOL) -> HookResult:
        event = self.parse_payload(raw_input, hook_type)
        if not event:
            return HookResult(event_id="claude_empty", verdict=HookVerdict.ALLOW, exit_code=0)

        result = self.engine.evaluate(event)
        return result

    def run_cli(self, hook_type_str: str = "pre_tool"):
        """CLI runner for direct pipe execution in .claude/settings.json."""
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        htype = HookType.POST_TOOL if "post" in hook_type_str.lower() else HookType.PRE_TOOL
        result = self.handle(raw, htype)

        if result.verdict == HookVerdict.BLOCK:
            print(f"🛑 [UAHF Claude Hook] {result.message}", file=sys.stderr)
            sys.exit(result.exit_code or 2)
        elif result.verdict == HookVerdict.WARN:
            print(f"⚠️ [UAHF Claude Hook] {result.message}", file=sys.stderr)
            sys.exit(0)

        sys.exit(0)
