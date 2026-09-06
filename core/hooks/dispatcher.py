"""
Universal Agentic Hooks Framework (UAHF) — Dispatcher
=====================================================
Central orchestrator for receiving, routing, evaluating, and logging hook events.
Maintains event ledger append-only audit trail and workflow state synchronization.
"""

import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

from .types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
)
from .policy_engine import UniversalPolicyEngine
from .adapters.claude_adapter import ClaudeHookAdapter
from .adapters.gemini_adapter import GeminiHookAdapter
from .adapters.cursor_adapter import CursorHookAdapter
from .adapters.codex_adapter import CodexHookAdapter
from .adapters.shell_adapter import ShellHookAdapter
from .adapters.homebrew_adapter import HomebrewHookAdapter
from .adapters.mcp_proxy import McpHookProxy
from .adapters.cli_agent_adapter import CliAgentAdapter


class HookDispatcher:
    """Dispatches hook invocations to respective platform adapters and logs verdicts."""

    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.policy_engine = UniversalPolicyEngine(str(self.project_dir))

        # Register platform adapters
        self.claude_adapter = ClaudeHookAdapter(self.policy_engine)
        self.gemini_adapter = GeminiHookAdapter(self.policy_engine)
        self.cursor_adapter = CursorHookAdapter(self.policy_engine)
        self.codex_adapter = CodexHookAdapter(self.policy_engine)
        self.shell_adapter = ShellHookAdapter(self.policy_engine)
        self.homebrew_adapter = HomebrewHookAdapter(self.policy_engine)
        self.mcp_proxy = McpHookProxy(self.policy_engine)
        self.cli_adapter = CliAgentAdapter(self.policy_engine)

        self.ledger_file = self.project_dir / ".traces" / "hook_events.jsonl"
        self._ensure_ledger()

    def _ensure_ledger(self):
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.ledger_file.exists():
            self.ledger_file.touch()

    def log_event_ledger(self, event: HookEvent, result: HookResult):
        """Append hook execution to audit ledger for non-repudiation."""
        entry = {
            "timestamp": time.time(),
            "event_id": event.event_id,
            "source": event.source.value if isinstance(event.source, HookSource) else str(event.source),
            "hook_type": event.hook_type.value if isinstance(event.hook_type, HookType) else str(event.hook_type),
            "tool": event.tool_name,
            "command": (event.command[:120] + "...") if event.command and len(event.command) > 120 else event.command,
            "file": event.file_path,
            "verdict": result.verdict.value if isinstance(result.verdict, HookVerdict) else str(result.verdict),
            "rule_id": result.rule_id,
            "message": result.message,
        }
        try:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as log_err:
            logger.debug("Failed to write to audit ledger: %s", log_err)

    def dispatch(self, event: HookEvent) -> HookResult:
        """Route event through policy pipeline, record audit trail, and return verdict."""
        result = self.policy_engine.evaluate(event)
        self.log_event_ledger(event, result)
        return result

    def get_status(self) -> Dict[str, Any]:
        """Return runtime status of all hook adapters and policies."""
        total_events = 0
        blocked_events = 0
        if self.ledger_file.exists():
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    total_events += 1
                    if '"verdict": "block"' in line:
                        blocked_events += 1

        return {
            "framework": "Universal Agentic Hooks Framework (UAHF)",
            "version": "1.0.0",
            "active_policies": [r.rule_id for r in self.policy_engine.rules],
            "supported_adapters": [
                "claude (native JSON)",
                "cursor (MDC + MCP)",
                "antigravity (MCP + shell)",
                "codex (wrapper + shell)",
                "kimi (wrapper + shell)",
                "bash / zsh / terminal (preexec/trap)",
                "homebrew (package gatekeeper)",
                "mcp (JSON-RPC stdio proxy)",
            ],
            "ledger_path": str(self.ledger_file),
            "telemetry": {
                "total_events_intercepted": total_events,
                "blocked_events": blocked_events,
            },
        }
