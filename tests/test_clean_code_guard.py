import unittest
from core.clean_code_guard import audit_file, CleanCodeChecker
import ast


class TestCleanCodeGuard(unittest.TestCase):
    def test_detect_swallowed_exception(self):
        code = """
def sample_func():
    try:
        x = 1 / 0
    except ZeroDivisionError:
        pass
"""
        tree = ast.parse(code)
        checker = CleanCodeChecker("dummy.py", code.splitlines())
        checker.visit(tree)
        self.assertTrue(any(v.rule_id == "RULE-15" for v in checker.violations))

    def test_detect_long_function(self):
        lines = ["def huge_function():"] + ["    x = 1" for _ in range(40)]
        code = "\n".join(lines)
        tree = ast.parse(code)
        checker = CleanCodeChecker("dummy.py", lines)
        checker.visit(tree)
        self.assertTrue(any(v.rule_id == "RULE-02" for v in checker.violations))

    def test_detect_excessive_arguments(self):
        code = "def too_many_args(a, b, c, d, e):\n    return a + b\n"
        tree = ast.parse(code)
        checker = CleanCodeChecker("dummy.py", code.splitlines())
        checker.visit(tree)
        self.assertTrue(any(v.rule_id == "RULE-03" for v in checker.violations))

    def test_clean_function_passes(self):
        code = """
def calculate_metric(alpha: float, beta: float) -> float:
    \"\"\"Calculate weighted score.\"\"\"
    return alpha * 0.7 + beta * 0.3
"""
        tree = ast.parse(code)
        checker = CleanCodeChecker("dummy.py", code.splitlines())
        checker.visit(tree)
        errors = [v for v in checker.violations if v.severity == "ERROR"]
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
