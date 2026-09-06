"""
Universal Agentic Hooks Framework (UAHF) — Types & Data Models
==============================================================
Canonical data models for normalized hook events, verdicts, and policies.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid


class HookSource(str, Enum):
    CLAUDE = "claude"
    CURSOR = "cursor"
    ANTIGRAVITY = "antigravity"
    CODEX = "codex"
    KIMI = "kimi"
    BASH = "bash"
    TERMINAL = "terminal"
    HOMEBREW = "homebrew"
    MCP = "mcp"
    CLI = "cli"


class HookType(str, Enum):
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    PRE_COMMAND = "pre_command"
    POST_COMMAND = "post_command"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ERROR_TRAP = "error_trap"


class HookVerdict(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    MUTATE = "mutate"
    WARN = "warn"
    ASK_USER = "ask_user"


@dataclass
class HookEvent:
    event_id: str = field(default_factory=lambda: f"hook_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}")
    source: HookSource = HookSource.CLI
    hook_type: HookType = HookType.PRE_COMMAND
    timestamp: float = field(default_factory=time.time)
    tool_name: Optional[str] = None
    command: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Any] = None
    file_path: Optional[str] = None
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source": self.source.value if isinstance(self.source, HookSource) else str(self.source),
            "hook_type": self.hook_type.value if isinstance(self.hook_type, HookType) else str(self.hook_type),
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "command": self.command,
            "args": self.args,
            "output": self.output,
            "file_path": self.file_path,
            "cwd": self.cwd,
            "env": self.env,
            "agent_id": self.agent_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HookEvent":
        source_val = data.get("source", "cli")
        try:
            source = HookSource(source_val)
        except ValueError:
            source = HookSource.CLI

        type_val = data.get("hook_type", "pre_command")
        try:
            hook_type = HookType(type_val)
        except ValueError:
            hook_type = HookType.PRE_COMMAND

        return cls(
            event_id=data.get("event_id", f"hook_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"),
            source=source,
            hook_type=hook_type,
            timestamp=data.get("timestamp", time.time()),
            tool_name=data.get("tool_name"),
            command=data.get("command"),
            args=data.get("args") or {},
            output=data.get("output"),
            file_path=data.get("file_path"),
            cwd=data.get("cwd"),
            env=data.get("env") or {},
            agent_id=data.get("agent_id"),
            metadata=data.get("metadata") or {},
        )


@dataclass
class HookResult:
    event_id: str
    verdict: HookVerdict = HookVerdict.ALLOW
    message: str = "Allowed by policy"
    exit_code: int = 0
    mutated_input: Optional[Dict[str, Any]] = None
    mutated_command: Optional[str] = None
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_blocked(self) -> bool:
        return self.verdict == HookVerdict.BLOCK

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "verdict": self.verdict.value if isinstance(self.verdict, HookVerdict) else str(self.verdict),
            "message": self.message,
            "exit_code": self.exit_code,
            "mutated_input": self.mutated_input,
            "mutated_command": self.mutated_command,
            "rule_id": self.rule_id,
            "metadata": self.metadata,
        }


class PolicyRule:
    """Base interface for all security and governance rules."""
    rule_id: str = "base_rule"
    description: str = "Base policy rule"

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        """
        Evaluate an event against this rule.
        Return None if the rule does not apply or passes cleanly.
        Return HookResult (BLOCK, WARN, MUTATE) if triggered.
        """
        raise NotImplementedError
