"""
OpenAI Codex & ChatGPT Plugin Hook Driver Adapter
=================================================
Consumes execution events from OpenAI Codex and ChatGPT plugin environments.
Normalizes events to HookEvent(source=HookSource.CODEX) and applies sandbox security
and governance policies.
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


class CodexHookAdapter:
    """Consumes and mediates OpenAI Codex & ChatGPT plugin lifecycle events."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def parse_payload(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> Optional[HookEvent]:
        """Parses a Codex / ChatGPT tool call payload into a normalized HookEvent."""
        try:
            data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        tool_name = data.get("name") or data.get("tool_name") or data.get("function")
        tool_args = data.get("arguments") or data.get("args") or data.get("input") or {}
        output = data.get("output") or data.get("response")

        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
            except Exception:
                tool_args = {"raw": tool_args}

        command = None
        file_path = None

        if isinstance(tool_args, dict):
            command = tool_args.get("command") or tool_args.get("cmd") or tool_args.get("code")
            file_path = tool_args.get("path") or tool_args.get("file_path") or tool_args.get("filename")

        return HookEvent(
            source=HookSource.CODEX,
            hook_type=hook_type,
            tool_name=tool_name or ("exec" if command else "plugin_call"),
            command=command,
            file_path=file_path,
            args=tool_args if isinstance(tool_args, dict) else {"raw": tool_args},
            output=output,
            metadata={"raw_codex_payload": data},
        )

    def handle(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> HookResult:
        """Evaluates Codex event against universal policies."""
        event = self.parse_payload(raw_input, hook_type)
        if not event:
            return HookResult(event_id="codex_empty", verdict=HookVerdict.ALLOW, exit_code=0)

        return self.engine.evaluate(event)

    def evaluate_tool(self, name: str, arguments: Dict[str, Any], is_pre: bool = True, output: Optional[Any] = None) -> HookResult:
        """Convenience method for programmatic Codex tool call evaluation."""
        hook_type = HookType.PRE_TOOL if is_pre else HookType.POST_TOOL
        payload = {"name": name, "arguments": arguments, "output": output}
        return self.handle(payload, hook_type)
