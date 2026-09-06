"""
Universal MCP (Model Context Protocol) Hook Proxy
=================================================
Transparent JSON-RPC proxy sitting between any MCP client (Cursor, Antigravity, Claude,
Codex, Kimi) and downstream MCP servers.
Intercepts 'tools/call' requests for policy gating and inspects tool responses for leaks.
"""

import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from ..types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
)
from ..policy_engine import UniversalPolicyEngine


class McpHookProxy:
    """Proxies and governs Model Context Protocol tool invocations."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def inspect_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Inspect an MCP client JSON-RPC request.
        If it's a tools/call and policy triggers a BLOCK, return a synthetic JSON-RPC error.
        Otherwise return None (allow pass-through).
        """
        if message.get("method") != "tools/call":
            return None

        params = message.get("params") or {}
        tool_name = params.get("name")
        tool_args = params.get("arguments") or {}

        event = HookEvent(
            source=HookSource.MCP,
            hook_type=HookType.PRE_TOOL,
            tool_name=tool_name,
            command=tool_args.get("command") or tool_args.get("cmd"),
            file_path=tool_args.get("path") or tool_args.get("file_path"),
            args=tool_args,
        )

        result = self.engine.evaluate(event)
        if result.verdict == HookVerdict.BLOCK:
            msg_id = message.get("id")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32000,
                    "message": f"MCP Tool Execution Blocked by Policy: {result.message}",
                    "data": {"rule_id": result.rule_id, "verdict": "blocked"},
                },
            }
        return None

    def inspect_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspect MCP server JSON-RPC response before delivering back to the client.
        Checks for secret leakage in tool output.
        """
        result_payload = response.get("result")
        if not result_payload:
            return response

        event = HookEvent(
            source=HookSource.MCP,
            hook_type=HookType.POST_TOOL,
            output=json.dumps(result_payload),
        )

        res = self.engine.evaluate(event)
        if res.verdict == HookVerdict.WARN and "SECRET LEAK DETECTED" in res.message:
            # Mask or annotate leak advisory
            if isinstance(result_payload, dict) and "content" in result_payload:
                result_payload["_security_advisory"] = res.message
        return response

    def run_proxy(self, server_command: List[str]):
        """Run downstream MCP server as subprocess, proxying stdin/stdout."""
        proc = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1,
        )

        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                    blocked_resp = self.inspect_request(msg)
                    if blocked_resp:
                        print(json.dumps(blocked_resp), flush=True)
                        continue
                except Exception as parse_err:
                    logger.debug("MCP JSON parse error: %s", parse_err)

                # Forward to server
                if proc.stdin:
                    proc.stdin.write(line + "\n")
                    proc.stdin.flush()

                # Read response from server
                if proc.stdout:
                    resp_line = proc.stdout.readline()
                    if resp_line:
                        try:
                            resp_json = json.loads(resp_line.strip())
                            sanitized = self.inspect_response(resp_json)
                            print(json.dumps(sanitized), flush=True)
                        except Exception:
                            print(resp_line.strip(), flush=True)
        finally:
            proc.terminate()
