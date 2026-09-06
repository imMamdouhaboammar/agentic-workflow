"""
CLI Agent Wrapper & Interceptor Adapter
=======================================
Supervises external CLI agents (OpenAI Codex, Moonshot Kimi, Aider, etc.).
Intercepts agent execution, enforces pre-flight governance, and injects protective hooks.
"""

import os
import shutil
import subprocess
import sys
from typing import List, Optional

from ..types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
)
from ..policy_engine import UniversalPolicyEngine


class CliAgentAdapter:
    """Wraps and mediates execution of autonomous CLI agents."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def identify_agent_source(self, binary_name: str) -> HookSource:
        name = os.path.basename(binary_name).lower()
        if "codex" in name:
            return HookSource.CODEX
        elif "kimi" in name:
            return HookSource.KIMI
        elif "cursor" in name:
            return HookSource.CURSOR
        elif "antigravity" in name:
            return HookSource.ANTIGRAVITY
        elif "claude" in name:
            return HookSource.CLAUDE
        return HookSource.CLI

    def run_supervised(self, command_args: List[str]) -> int:
        if not command_args:
            print("❌ No command provided to CLI Agent supervisor.", file=sys.stderr)
            return 1

        binary = command_args[0]
        source = self.identify_agent_source(binary)

        # Pre-execution policy check on the agent invocation itself
        full_command = " ".join(command_args)
        event = HookEvent(
            source=source,
            hook_type=HookType.SESSION_START,
            command=full_command,
            tool_name=binary,
            args={"raw_args": command_args[1:]},
            agent_id=f"agent_{source.value}",
        )

        result = self.engine.evaluate(event)
        if result.verdict == HookVerdict.BLOCK:
            print(f"\033[1;31m🛑 [CLI Agent Guard] INVOCATION BLOCKED:\033[0m\n  {result.message}", file=sys.stderr)
            return 2

        # Inject environment hook overrides so subshells spawned by the agent hit our hooks
        env = os.environ.copy()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        hook_bin = os.path.join(repo_root, "bin")

        current_path = env.get("PATH", "")
        if hook_bin not in current_path:
            env["PATH"] = f"{hook_bin}:{current_path}"

        env["AGENTIC_HOOKS_ACTIVE"] = "1"
        env["AGENTIC_AGENT_NAME"] = source.value

        # Execute target agent
        proc = subprocess.run(command_args, env=env)
        return proc.returncode
