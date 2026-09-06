"""
Universal Agentic Hooks Framework (UAHF) — Policy Engine
========================================================
Centralized, deterministic policy evaluation pipeline for governing agent behavior.
Integrates safety hooks, secret sanitizers, package policy, and TDD guards.
"""

from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set

from .types import (
    HookEvent,
    HookResult,
    HookSource,
    HookType,
    HookVerdict,
    PolicyRule,
)


class DestructiveCommandRule(PolicyRule):
    """Blocks catastrophic commands (rm -rf /, dd if=, mkfs, git -f, curl | sh)."""
    rule_id = "SEC-001-DESTRUCTIVE-COMMAND"
    description = "Blocks destructive system, git, and exfiltration commands"

    NETWORK_PATTERNS = [
        (re.compile(r"\bcurl\b.*\|\s*(ba)?sh\b"), "curl piped to shell is blocked. Download, inspect, and execute manually."),
        (re.compile(r"\bwget\b.*\|\s*(ba)?sh\b"), "wget piped to shell is blocked. Download, inspect, and execute manually."),
    ]

    SYSTEM_PATTERNS = [
        (re.compile(r"\bdd\b\s+if="), "dd command with raw input file is blocked. Irreversible disk write risk."),
        (re.compile(r"\bmkfs\b"), "mkfs command is blocked. Filesystem formatting destroys all data."),
    ]

    GIT_PATTERNS = [
        (
            re.compile(r"\bgit\s+push\b.*(?<![-\w])--force(?![-\w])"),
            "git push --force is blocked. Use --force-with-lease to protect remote history.",
        ),
        (
            re.compile(r"\bgit\s+push\b.*\s-[a-zA-Z]*f"),
            "git push -f is blocked. Use --force-with-lease to protect remote history.",
        ),
        (re.compile(r"\bgit\s+reset\b.*\s--hard\b"), "git reset --hard is blocked. Discards uncommitted work permanently."),
        (re.compile(r"\bgit\s+checkout\b\s+(?:--\s+)?\."), "git checkout . is blocked. Discards unstaged modifications."),
        (re.compile(r"\bgit\s+restore\b\s+\."), "git restore . is blocked. Discards unstaged modifications."),
        (re.compile(r"\bgit\s+clean\b.*\s-[a-zA-Z]*f"), "git clean -f is blocked. Permanently deletes untracked files."),
        (re.compile(r"\bgit\s+branch\b.*\s-D\b"), "git branch -D is blocked. Use git branch -d for safe deletion."),
        (
            re.compile(r"\bgit\s+branch\b.*\s--delete\b.*\s--force\b"),
            "git branch --delete --force is blocked. Use git branch -d for safe deletion.",
        ),
    ]

    DANGEROUS_TARGETS = {"/", "/*", "~", "~/", "$HOME", "$HOME/", "$HOME/*"}

    def _check_dangerous_rm(self, sub_command: str) -> Optional[str]:
        tokens = sub_command.split()
        if not tokens or tokens[0] != "rm":
            return None

        flags = ""
        targets = []
        for token in tokens[1:]:
            if token.startswith("-") and not token.startswith("--"):
                flags += token[1:]
            elif not token.startswith("-"):
                targets.append(token.strip("\"'"))

        has_recursive = "r" in flags or "R" in flags
        has_force = "f" in flags

        if not (has_recursive and has_force):
            return None

        for target in targets:
            if target in self.DANGEROUS_TARGETS:
                return f"rm -rf targeting {target} is blocked. Catastrophic, irreversible file deletion."
        return None

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        command = event.command or (event.args.get("command") if isinstance(event.args, dict) else None)
        if not command or not isinstance(command, str):
            return None

        for pattern, msg in self.NETWORK_PATTERNS:
            if pattern.search(command):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.BLOCK,
                    message=f"DESTRUCTIVE COMMAND BLOCKED: {msg}",
                    exit_code=2,
                    rule_id=self.rule_id,
                )

        for pattern, msg in self.SYSTEM_PATTERNS:
            if pattern.search(command):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.BLOCK,
                    message=f"DESTRUCTIVE COMMAND BLOCKED: {msg}",
                    exit_code=2,
                    rule_id=self.rule_id,
                )

        for pattern, msg in self.GIT_PATTERNS:
            if pattern.search(command):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.BLOCK,
                    message=f"DESTRUCTIVE COMMAND BLOCKED: {msg}",
                    exit_code=2,
                    rule_id=self.rule_id,
                )

        for sub_cmd in re.split(r"\s*(?:&&|\|\||;)\s*", command):
            for segment in sub_cmd.split("|"):
                rm_err = self._check_dangerous_rm(segment.strip())
                if rm_err:
                    return HookResult(
                        event_id=event.event_id,
                        verdict=HookVerdict.BLOCK,
                        message=f"DESTRUCTIVE COMMAND BLOCKED: {rm_err}",
                        exit_code=2,
                        rule_id=self.rule_id,
                    )

        return None


class PackagePolicyRule(PolicyRule):
    """Enforces package manager hygiene: bans Colima, restricts sudo brew, verifies safe installs."""
    rule_id = "PKG-002-PACKAGE-HYGIENE"
    description = "Enforces container and package manager governance policies"

    FORBIDDEN_PACKAGES = {
        "colima": "Colima is prohibited per project constitution due to large footprint. Use lightweight alternatives.",
    }

    BREW_INSTALL_REGEX = re.compile(r"\bbrew\s+(?:install|reinstall|cask)\s+([^\s;]+)", re.IGNORECASE)
    SUDO_BREW_REGEX = re.compile(r"\bsudo\s+brew\b", re.IGNORECASE)

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        command = event.command or (event.args.get("command") if isinstance(event.args, dict) else None)
        args_target = event.args.get("target") or event.args.get("package")

        if command and isinstance(command, str):
            if self.SUDO_BREW_REGEX.search(command):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.BLOCK,
                    message="PACKAGE POLICY VIOLATION: 'sudo brew' is prohibited. Homebrew must not run as root.",
                    exit_code=2,
                    rule_id=self.rule_id,
                )

            match = self.BREW_INSTALL_REGEX.search(command)
            if match:
                pkg_candidate = match.group(1).lower().strip("\"'")
                for forbidden_pkg, reason in self.FORBIDDEN_PACKAGES.items():
                    if forbidden_pkg in pkg_candidate:
                        return HookResult(
                            event_id=event.event_id,
                            verdict=HookVerdict.BLOCK,
                            message=f"PACKAGE POLICY VIOLATION: Package '{forbidden_pkg}' is blocked. {reason}",
                            exit_code=2,
                            rule_id=self.rule_id,
                        )

        if args_target and isinstance(args_target, str):
            tgt = args_target.lower()
            for forbidden_pkg, reason in self.FORBIDDEN_PACKAGES.items():
                if forbidden_pkg == tgt or forbidden_pkg in tgt:
                    return HookResult(
                        event_id=event.event_id,
                        verdict=HookVerdict.BLOCK,
                        message=f"PACKAGE POLICY VIOLATION: Package '{forbidden_pkg}' is blocked. {reason}",
                        exit_code=2,
                        rule_id=self.rule_id,
                    )

        return None


class SensitiveFileRule(PolicyRule):
    """Prevents overwriting or exposing security-sensitive files (.env, keys, certs)."""
    rule_id = "SEC-003-SENSITIVE-FILES"
    description = "Prevents tampering with credentials, environment secrets, and private keys"

    SENSITIVE_PATTERNS = [
        (re.compile(r"(^|[/\\])\.env(\.[a-zA-Z0-9_-]+)?$"), "Environment secret file (.env)"),
        (re.compile(r"\.(pem|key|p12|pfx)$", re.IGNORECASE), "Private key or certificate"),
        (re.compile(r"(^|[/\\])id_(rsa|ed25519|ecdsa|dsa)$"), "SSH private key"),
        (re.compile(r"(^|[/\\])(credentials|secrets|passwords)\.(json|ya?ml|toml)$", re.IGNORECASE), "Secrets store"),
        (re.compile(r"(^|[/\\])(service[-_]?account|token)\.json$", re.IGNORECASE), "Service account / Token file"),
        (re.compile(r"\.(tfstate|tfvars)$", re.IGNORECASE), "Terraform state / variable secrets"),
    ]

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        file_path = event.file_path or event.args.get("file_path") or event.args.get("path")
        if not file_path or not isinstance(file_path, str):
            return None

        for pattern, label in self.SENSITIVE_PATTERNS:
            if pattern.search(file_path):
                # If tool attempts write/edit on sensitive file, block or warn
                tool_name = (event.tool_name or "").lower()
                is_write = (
                    "write" in tool_name
                    or "edit" in tool_name
                    or event.hook_type in [HookType.PRE_TOOL, HookType.PRE_COMMAND]
                )
                if is_write:
                    return HookResult(
                        event_id=event.event_id,
                        verdict=HookVerdict.WARN,
                        message=f"SECURITY ADVISORY: Access/modification to sensitive file '{file_path}' ({label}).",
                        exit_code=0,
                        rule_id=self.rule_id,
                    )
        return None


class TddIntegrityRule(PolicyRule):
    """Enforces TDD discipline by blocking test file edits when .tdd-guard is active."""
    rule_id = "GOV-004-TDD-INTEGRITY"
    description = "Protects test files from modification during implementation phases"

    TEST_FILE_PATTERNS = [
        re.compile(r"(^|[/\\])test_[^/\\]+\.py$"),
        re.compile(r"[._]test\.[jt]sx?$"),
        re.compile(r"[._]spec\.[jt]sx?$"),
    ]

    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()

    def is_guard_active(self) -> bool:
        return (self.project_dir / ".tdd-guard").exists() or Path(".tdd-guard").exists()

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        if not self.is_guard_active():
            return None

        file_path = event.file_path or event.args.get("file_path") or event.args.get("path")
        if not file_path or not isinstance(file_path, str):
            return None

        tool_name = (event.tool_name or "").lower()
        if not ("edit" in tool_name or "write" in tool_name):
            return None

        for pattern in self.TEST_FILE_PATTERNS:
            if pattern.search(file_path):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.BLOCK,
                    message=(
                        f"TDD GUARD ACTIVE: Modification of test file '{file_path}' is blocked. "
                        "Modify implementation code to make tests pass."
                    ),
                    exit_code=2,
                    rule_id=self.rule_id,
                )
        return None


class SecretLeakRule(PolicyRule):
    """Scans tool outputs and command responses for accidental credential exfiltration."""
    rule_id = "SEC-005-SECRET-LEAK-FILTER"
    description = "Detects and blocks leakage of API keys and authentication tokens in telemetry"

    PATTERNS = [
        (re.compile(r"sk-(?:proj|ant|live)-[a-zA-Z0-9_\-]{20,}"), "OpenAI / Anthropic API Key"),
        (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID"),
        (re.compile(r"gh[pousr][_-][A-Za-z0-9_]{36,255}"), "GitHub Personal Access Token"),
        (re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}"), "Slack Token"),
        (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"), "Private Cryptographic Key"),
    ]

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        output = event.output
        if output is None:
            return None

        text = str(output)
        for pattern, label in self.PATTERNS:
            if pattern.search(text):
                return HookResult(
                    event_id=event.event_id,
                    verdict=HookVerdict.WARN,
                    message=f"SECRET LEAK DETECTED: {label} found in output stream. Redacting.",
                    exit_code=0,
                    rule_id=self.rule_id,
                    metadata={"leak_type": label},
                )
        return None


class CircuitBreakerRule(PolicyRule):
    """Trips and halts runaway agent loops when consecutive failure streaks >= 2."""
    rule_id = "RES-006-CIRCUIT-BREAKER"
    description = "Halts speculative retry loops when failure threshold is exceeded"

    def __init__(self, failure_threshold: int = 2):
        self.failure_threshold = failure_threshold
        self.streak_counters: Dict[str, int] = {}

    def record_failure(self, agent_id: str):
        self.streak_counters[agent_id] = self.streak_counters.get(agent_id, 0) + 1

    def record_success(self, agent_id: str):
        self.streak_counters[agent_id] = 0

    def evaluate(self, event: HookEvent) -> Optional[HookResult]:
        agent_id = event.agent_id or "default_agent"
        streak = self.streak_counters.get(agent_id, 0)
        if streak >= self.failure_threshold:
            return HookResult(
                event_id=event.event_id,
                verdict=HookVerdict.BLOCK,
                message=(
                    f"CIRCUIT BREAKER TRIPPED: Agent '{agent_id}' has {streak} consecutive failures. "
                    "Halting speculative edits. Run Abductive Diagnosis before retrying."
                ),
                exit_code=2,
                rule_id=self.rule_id,
            )
        return None


class UniversalPolicyEngine:
    """Orchestrates all policy rules and computes conclusive hook verdicts."""

    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = project_dir or str(Path.cwd())
        self.rules: List[PolicyRule] = [
            DestructiveCommandRule(),
            PackagePolicyRule(),
            SensitiveFileRule(),
            TddIntegrityRule(self.project_dir),
            SecretLeakRule(),
            CircuitBreakerRule(),
        ]

    def add_rule(self, rule: PolicyRule):
        self.rules.append(rule)

    def evaluate(self, event: HookEvent) -> HookResult:
        warnings = []
        for rule in self.rules:
            result = rule.evaluate(event)
            if result:
                if result.verdict == HookVerdict.BLOCK:
                    return result
                elif result.verdict == HookVerdict.WARN:
                    warnings.append(result.message)

        if warnings:
            return HookResult(
                event_id=event.event_id,
                verdict=HookVerdict.WARN,
                message="; ".join(warnings),
                exit_code=0,
            )

        return HookResult(
            event_id=event.event_id,
            verdict=HookVerdict.ALLOW,
            message="Operation allowed by policy",
            exit_code=0,
        )
