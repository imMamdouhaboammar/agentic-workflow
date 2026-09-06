"""
Google Antigravity & Gemini CLI Hook Driver Adapter
===================================================
Consumes tool execution events from Google Antigravity and Gemini CLI environments.
Normalizes tool calls (run_command, write_to_file, replace_file_content, view_file, invoke_subagent)
into canonical HookEvent instances and applies UAHF policy engine gates.
"""

import json
import os
import re
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


class GeminiHookAdapter:
    """Consumes and mediates Gemini CLI & Google Antigravity lifecycle tool events."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def parse_payload(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> Optional[HookEvent]:
        """Parses a Gemini CLI / Antigravity tool call payload into a normalized HookEvent."""
        try:
            data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        tool_name = data.get("tool_name") or data.get("name") or data.get("tool")
        tool_args = data.get("args") or data.get("arguments") or data.get("parameters") or {}
        tool_response = data.get("response") or data.get("output") or data.get("result")

        command = None
        file_path = None

        if isinstance(tool_args, dict):
            # Antigravity run_command convention
            command = tool_args.get("CommandLine") or tool_args.get("command") or tool_args.get("cmd")
            # Antigravity file tools (view_file, write_to_file, replace_file_content)
            file_path = (
                tool_args.get("AbsolutePath")
                or tool_args.get("TargetFile")
                or tool_args.get("file_path")
                or tool_args.get("path")
            )

        return HookEvent(
            source=HookSource.ANTIGRAVITY,
            hook_type=hook_type,
            tool_name=tool_name,
            command=command,
            file_path=file_path,
            args=tool_args if isinstance(tool_args, dict) else {"raw": tool_args},
            output=tool_response,
            metadata={"raw_gemini_payload": data},
        )

    def handle(self, raw_input: Any, hook_type: HookType = HookType.PRE_TOOL) -> HookResult:
        """Evaluates payload against universal policies."""
        event = self.parse_payload(raw_input, hook_type)
        if not event:
            return HookResult(event_id="gemini_empty", verdict=HookVerdict.ALLOW, exit_code=0)

        result = self.engine.evaluate(event)
        return result

    def evaluate_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        is_pre: bool = True,
        output: Optional[Any] = None
    ) -> HookResult:
        """Programmatic evaluation entry point for Python-driven Gemini / Antigravity agents."""
        hook_type = HookType.PRE_TOOL if is_pre else HookType.POST_TOOL
        payload = {
            "tool_name": tool_name,
            "args": arguments,
            "output": output
        }
        return self.handle(payload, hook_type)
