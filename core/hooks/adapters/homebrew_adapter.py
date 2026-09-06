"""
Homebrew Package Manager Hook Adapter
=====================================
Dedicated gatekeeper for Homebrew command interception and package hygiene.
Enforces prohibitions against heavy or banned packages (e.g. Colima) and unsafe flags.
"""

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


class HomebrewHookAdapter:
    """Intercepts and verifies brew operations before execution."""

    def __init__(self, policy_engine: Optional[UniversalPolicyEngine] = None):
        self.engine = policy_engine or UniversalPolicyEngine()

    def evaluate_brew_args(self, args: List[str]) -> HookResult:
        full_command = f"brew {' '.join(args)}".strip()
        package_target = None
        for i, arg in enumerate(args):
            if arg in ["install", "reinstall", "cask"] and i + 1 < len(args):
                package_target = args[i + 1]
                break

        event = HookEvent(
            source=HookSource.HOMEBREW,
            hook_type=HookType.PRE_COMMAND,
            command=full_command,
            tool_name="homebrew",
            args={"raw_args": args, "package": package_target},
        )
        return self.engine.evaluate(event)

    def run_shim(self, brew_args: List[str]) -> int:
        result = self.evaluate_brew_args(brew_args)
        if result.verdict == HookVerdict.BLOCK:
            print(f"\033[1;31m🛑 [Homebrew Hook Guard] OPERATION BLOCKED:\033[0m\n  {result.message}", file=sys.stderr)
            return 2
        elif result.verdict == HookVerdict.WARN:
            print(f"\033[1;33m⚠️ [Homebrew Hook Guard] ADVISORY:\033[0m {result.message}", file=sys.stderr)

        # Locate real brew binary
        real_brew = None
        for candidate in ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]:
            if shutil.which(candidate):
                real_brew = candidate
                break
        if not real_brew:
            real_brew = shutil.which("brew")

        if not real_brew:
            print("❌ [Homebrew Hook Guard] Homebrew executable not found on system PATH.", file=sys.stderr)
            return 127

        # Pass through to real brew
        res = subprocess.run([real_brew] + brew_args)
        return res.returncode
