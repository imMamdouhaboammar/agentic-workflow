"""
Shell & Terminal Hook Adapter
=============================
Intercepts commands in Bash, Zsh, and interactive/scripted terminal sessions.
Integrates with shell hooks (preexec/precmd, DEBUG trap) and shell wrapper shims.
"""

import os
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


class ShellHookAdapter:
    """Intercepts and governs raw shell / terminal command execution."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def create_event(
        self,
        command: str,
        hook_type: HookType = HookType.PRE_COMMAND,
        source: HookSource = HookSource.BASH,
        cwd: Optional[str] = None,
    ) -> HookEvent:
        return HookEvent(
            source=source,
            hook_type=hook_type,
            command=command.strip(),
            tool_name="bash",
            cwd=cwd or os.getcwd(),
            env=dict(os.environ),
        )

    def evaluate_command(
        self,
        command: str,
        hook_type: HookType = HookType.PRE_COMMAND,
        source: HookSource = HookSource.BASH,
    ) -> HookResult:
        if not command or not command.strip():
            return HookResult(event_id="empty_cmd", verdict=HookVerdict.ALLOW, exit_code=0)

        event = self.create_event(command, hook_type, source)
        return self.engine.evaluate(event)

    def run_cli_preexec(self, command: str) -> int:
        result = self.evaluate_command(command, hook_type=HookType.PRE_COMMAND, source=HookSource.TERMINAL)
        if result.verdict == HookVerdict.BLOCK:
            print(f"\033[1;31m🛑 [Agentic Shell Hook] EXECUTION BLOCKED:\033[0m\n  {result.message}", file=sys.stderr)
            print(f"  Command: {command[:200]}\033[0m", file=sys.stderr)
            return 2
        elif result.verdict == HookVerdict.WARN:
            print(f"\033[1;33m⚠️ [Agentic Shell Hook] ADVISORY:\033[0m {result.message}", file=sys.stderr)
            return 0
        return 0
