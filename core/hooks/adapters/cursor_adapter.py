"""
Cursor IDE & Windsurf Hook Driver Adapter
=========================================
Consumes tool execution and terminal command events from Cursor IDE rules (.cursor/rules)
and Windsurf cascades. Normalizes events to HookEvent(source=HookSource.CURSOR) and applies
governance policies.
"""

import json
from typing import Any, Dict, Optional

from ..types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
)
from ..policy_engine import UniversalPolicyEngine


class CursorHookAdapter:
    """Consumes and mediates Cursor IDE & Windsurf lifecycle events."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def parse_payload(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> Optional[HookEvent]:
        """Parses Cursor / Windsurf command or tool invocation payload."""
        try:
            data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        tool_name = data.get("tool") or data.get("tool_name") or data.get("action")
        command = data.get("command") or data.get("cmd")
        file_path = data.get("file_path") or data.get("path") or data.get("target_file")
        tool_args = data.get("args") or data.get("parameters") or {}
        output = data.get("output") or data.get("result")

        if isinstance(tool_args, dict):
            if not command:
                command = tool_args.get("command") or tool_args.get("cmd")
            if not file_path:
                file_path = tool_args.get("file_path") or tool_args.get("path") or tool_args.get("target_file")

        return HookEvent(
            source=HookSource.CURSOR,
            hook_type=hook_type,
            tool_name=tool_name or ("terminal" if command else "file_op"),
            command=command,
            file_path=file_path,
            args=tool_args if isinstance(tool_args, dict) else {"raw": tool_args},
            output=output,
            metadata={"raw_cursor_payload": data},
        )

    def handle(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> HookResult:
        """Evaluates Cursor event against universal policies."""
        event = self.parse_payload(raw_input, hook_type)
        if not event:
            return HookResult(event_id="cursor_empty", verdict=HookVerdict.ALLOW, exit_code=0)

        return self.engine.evaluate(event)

    def evaluate_command(self, command_line: str, is_pre: bool = True, output: Optional[str] = None) -> HookResult:
        """Convenience method for evaluating Cursor terminal commands."""
        hook_type = HookType.PRE_COMMAND if is_pre else HookType.POST_COMMAND
        payload = {"command": command_line, "output": output}
        return self.handle(payload, hook_type)
