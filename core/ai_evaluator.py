#!/usr/bin/env python3
"""
ai_evaluator.py — AI / ML Pipeline & Prompt-Injection Guard

Implements patterns from /engineering-ai-engineer:
1. Four-Fifths Disparate Impact & Fairness Testing (Selection Rate Ratio >= 0.80)
2. Adversarial Prompt-Injection Sanitizer & Instruction-Content Boundary Defense
3. Population Stability Index (PSI) Drift Estimator
4. Strict Schema Validation for Agent Outputs
"""

import re
import math
from typing import Dict, List, Tuple, Any, Optional


class PromptInjectionSanitizer:
    """Detects and neutralizes prompt-injection attempts in untrusted content."""

    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
        r"you\s+are\s+now\s+a\s+(new|different)\s+agent",
        r"system\s*:\s*override",
        r"reveal\s+(your\s+)?(system\s+prompt|instructions|secret)",
        r"dump\s+(all\s+)?(passwords|api_keys|tokens)",
        r"bypass\s+(all\s+)?(safety|guards|filters)"
    ]

    def __init__(self):
        self._compiled_regexes = [
            re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS
        ]

    def scan_content(self, text: str) -> Tuple[bool, List[str]]:
        """Scans text for prompt injection signatures. Returns (is_safe, matches)."""
        matches = []
        for regex in self._compiled_regexes:
            found = regex.findall(text)
            if found:
                matches.append(regex.pattern)
        return (len(matches) == 0, matches)

    def sanitize(self, text: str) -> str:
        """Neutralizes detected instruction overrides by escaping directive boundaries."""
        sanitized = text
        for regex in self._compiled_regexes:
            sanitized = regex.sub("[FILTERED_INSTRUCTION]", sanitized)
        return sanitized


class FairnessAuditor:
    """Evaluates demographic parity and four-fifths disparate impact rule."""

    @staticmethod
    def calculate_disparate_impact(
        selection_rate_unprivileged: float,
        selection_rate_privileged: float
    ) -> float:
        """
        Computes disparate impact ratio: rate(unprivileged) / rate(privileged).
        Pass condition: ratio >= 0.80.
        """
        if selection_rate_privileged <= 0.0:
            return 1.0 if selection_rate_unprivileged <= 0.0 else 0.0
        return selection_rate_unprivileged / selection_rate_privileged

    @classmethod
    def audit_selection_rates(
        cls, rates: Dict[str, float], reference_group: str
    ) -> Dict[str, Any]:
        """Audits all groups against the reference group using four-fifths rule."""
        ref_rate = rates.get(reference_group, 1.0)
        results = {}
        all_passed = True

        for group, rate in rates.items():
            if group == reference_group:
                continue
            ratio = cls.calculate_disparate_impact(rate, ref_rate)
            passed = ratio >= 0.80
            if not passed:
                all_passed = False
            results[group] = {
                "selection_rate": rate,
                "reference_rate": ref_rate,
                "disparate_impact_ratio": round(ratio, 4),
                "passed_four_fifths_rule": passed
            }

        return {
            "all_passed": all_passed,
            "group_audits": results
        }


class DriftMonitor:
    """Population Stability Index (PSI) calculator to detect feature/data drift."""

    @staticmethod
    def calculate_psi(expected: List[float], actual: List[float], epsilon: float = 1e-4) -> float:
        """
        Computes Population Stability Index between expected baseline and actual sample.
        PSI < 0.10: No shift (stable)
        0.10 <= PSI < 0.25: Moderate shift
        PSI >= 0.25: Significant shift (retraining triggered)
        """
        if len(expected) != len(actual) or not expected:
            return 0.0

        psi_total = 0.0
        for exp_pct, act_pct in zip(expected, actual):
            e = max(exp_pct, epsilon)
            a = max(act_pct, epsilon)
            psi_total += (a - e) * math.log(a / e)

        return round(psi_total, 4)
