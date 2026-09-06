"""
Universal Agentic Hooks Framework (UAHF) — Adapters
===================================================
Adapters for normalizing hooks across Claude, Cursor, Antigravity, Gemini CLI, Codex, Shell, Homebrew, MCP, and CLI.
"""

from .claude_adapter import ClaudeHookAdapter
from .gemini_adapter import GeminiHookAdapter
from .cursor_adapter import CursorHookAdapter
from .codex_adapter import CodexHookAdapter
from .shell_adapter import ShellHookAdapter
from .homebrew_adapter import HomebrewHookAdapter
from .mcp_proxy import McpHookProxy
from .cli_agent_adapter import CliAgentAdapter

__all__ = [
    "ClaudeHookAdapter",
    "GeminiHookAdapter",
    "CursorHookAdapter",
    "CodexHookAdapter",
    "ShellHookAdapter",
    "HomebrewHookAdapter",
    "McpHookProxy",
    "CliAgentAdapter",
]
