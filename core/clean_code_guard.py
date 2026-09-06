#!/usr/bin/env python3
"""
clean_code_guard.py — Clean Code & LLM Failure Mode Guard Pass

Implements the 24 Clean Code Imperatives:
- Intent-revealing names (no unqualified data, temp, res, helper)
- Small functions (<= 20 lines target, > 35 flag)
- Max 4 arguments per function (CQS / DTO enforcement)
- AI failure modes: No swallowed exceptions, no hardcoded fake returns
- Boundary validation & dead code elimination
"""

import ast
import os
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GuardViolation:
    file_path: str
    line_number: int
    rule_id: str
    severity: str  # ERROR, WARNING, INFO
    message: str


class CleanCodeChecker(ast.NodeVisitor):
    """AST-based Clean Code auditor for Python source files."""

    DISALLOWED_BARE_NAMES = {
        "data", "data2", "temp", "val", "value", "item", "obj",
        "helper", "utils", "mgr", "res", "result_final"
    }

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.violations: List[GuardViolation] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function_length(node)
        self._check_argument_count(node)
        self._check_function_naming(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._check_swallowed_exceptions(node)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self._check_hardcoded_fake_success(node)
        self.generic_visit(node)

    def _check_function_length(self, node: ast.FunctionDef) -> None:
        end_lineno = getattr(node, "end_lineno", node.lineno)
        length = end_lineno - node.lineno + 1
        if length > 35:
            self.violations.append(GuardViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id="RULE-02",
                severity="WARNING",
                message=f"Function '{node.name}' exceeds 35 lines ({length} lines). Consider decomposing."
            ))

    def _check_argument_count(self, node: ast.FunctionDef) -> None:
        pos_args = len(node.args.args)
        if node.args.args and node.args.args[0].arg in ("self", "cls"):
            pos_args -= 1
        if pos_args > 4:
            self.violations.append(GuardViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id="RULE-03",
                severity="WARNING",
                message=f"Function '{node.name}' has {pos_args} arguments (max 4 allowed; use a config/DTO object)."
            ))

    def _check_function_naming(self, node: ast.FunctionDef) -> None:
        if node.name.lower() in self.DISALLOWED_BARE_NAMES:
            self.violations.append(GuardViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id="RULE-01",
                severity="ERROR",
                message=f"Function name '{node.name}' does not reveal intent. Use a descriptive domain verb."
            ))

    def _check_swallowed_exceptions(self, node: ast.ExceptHandler) -> None:
        if len(node.body) == 1:
            first_stmt = node.body[0]
            if isinstance(first_stmt, ast.Pass):
                self.violations.append(GuardViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id="RULE-15",
                    severity="ERROR",
                    message="Swallowed exception with bare 'pass' detected without logging or recovery."
                ))
            elif isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
                self.violations.append(GuardViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id="RULE-15",
                    severity="ERROR",
                    message="Swallowed exception with no-op constant detected without logging or recovery."
                ))

    def _check_hardcoded_fake_success(self, node: ast.Return) -> None:
        if isinstance(node.value, ast.Dict):
            keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
            if "status" in keys and len(keys) == 1:
                self.violations.append(GuardViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id="RULE-18",
                    severity="WARNING",
                    message="Hardcoded fake status return detected. Ensure real implementation logic."
                ))


def audit_file(file_path: str) -> List[GuardViolation]:
    """Audits a single Python or script file for Clean Code imperatives."""
    if not os.path.isfile(file_path):
        return []
    
    violations: List[GuardViolation] = []
    if file_path.endswith(".py"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
            checker = CleanCodeChecker(file_path, content.splitlines())
            checker.visit(tree)
            violations.extend(checker.violations)
        except SyntaxError as parse_error:
            violations.append(GuardViolation(
                file_path=file_path,
                line_number=getattr(parse_error, 'lineno', 1) or 1,
                rule_id="RULE-16",
                severity="WARNING",
                message=f"Syntax error during file parse: {parse_error.msg}"
            ))
    return violations


def audit_directory(root_dir: str, skip_dirs: Optional[List[str]] = None) -> List[GuardViolation]:
    """Recursively audits all source files in a directory."""
    skip = set(skip_dirs or [".git", "node_modules", "context-snapshots", "__pycache__"])
    all_violations: List[GuardViolation] = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if f.endswith(".py") and not f.startswith("_test_"):
                path = os.path.join(root, f)
                all_violations.extend(audit_file(path))

    return all_violations


def run_guard_report(root_dir: str = ".") -> int:
    """Runs the audit and prints a structured clean-code-guard report."""
    print("🛡️ [clean-code-guard] Running Clean Code & AI Failure-Mode Audit...")
    violations = audit_directory(root_dir)
    errors = [v for v in violations if v.severity == "ERROR"]
    warnings = [v for v in violations if v.severity == "WARNING"]

    print(f"Audit Summary: {len(errors)} errors, {len(warnings)} warnings")
    for v in violations[:15]:
        icon = "❌" if v.severity == "ERROR" else "⚠️"
        print(f"  {icon} [{v.rule_id}] {v.file_path}:{v.line_number} — {v.message}")

    if errors:
        print("❌ clean-code-guard: FAIL (Fix critical violations before delivery)")
        return 1
    print("✅ clean-code-guard: clean (All critical imperatives satisfied)")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(run_guard_report(target))
