"""
core/system/health.py — Python Health Telemetry & Scoring Engine
"""

import os
import platform
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any, List


class HealthEngine:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()

    def collect_vitals(self) -> Dict[str, Any]:
        bun_v = None
        try:
            res = subprocess.run("bun --version", shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                bun_v = res.stdout.strip()
        except Exception:
            pass

        py_v = platform.python_version()

        # Workflow vitals
        sot = self.project_dir / "state.yaml"
        has_wf = False
        step = "idle"
        if sot.exists():
            try:
                txt = sot.read_text(encoding="utf-8")
                has_wf = "status: in_progress" in txt or "status: planning" in txt
                for line in txt.splitlines():
                    if line.strip().startswith("current_step:"):
                        step = line.split(":", 1)[1].strip().strip('"\'')
            except Exception:
                pass

        # Circuit breaker
        cb = "CLOSED"
        streak = 0
        fable_state = self.project_dir / ".fable" / "state.json"
        if fable_state.exists():
            try:
                with open(fable_state, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("circuit_breaker_tripped"):
                        cb = "OPEN"
                    streak = data.get("failure_streak", 0)
            except Exception:
                pass

        # Traces count
        traces = 0
        trace_dir = self.project_dir / ".traces"
        if trace_dir.exists():
            for f in trace_dir.glob("*.jsonl"):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        traces += sum(1 for _ in fp)
                except Exception:
                    pass

        return {
            "platform": platform.system().lower(),
            "arch": platform.machine(),
            "bun_version": bun_v,
            "python_version": py_v,
            "has_workflow": has_wf,
            "current_step": step,
            "circuit_breaker": cb,
            "failure_streak": streak,
            "traces_count": traces
        }

    def evaluate_score(self, vitals: Dict[str, Any]) -> Dict[str, Any]:
        score = 100
        warnings = []

        if not vitals.get("bun_version"):
            score -= 10
            warnings.append("Bun runtime missing")
        if vitals.get("circuit_breaker") == "OPEN":
            score -= 25
            warnings.append("Circuit breaker OPEN")
        elif vitals.get("failure_streak", 0) > 0:
            score -= min(15, vitals["failure_streak"] * 5)
            warnings.append(f"Active failure streak: {vitals['failure_streak']}")

        if not (self.project_dir / "node_modules").exists():
            score -= 10
            warnings.append("node_modules missing")

        if not (self.project_dir / "skills-index.toon").exists():
            score -= 10
            warnings.append("skills-index.toon missing")

        score = max(0, min(100, score))
        grade = "F"
        if score >= 95:
            grade = "A+"
        elif score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"

        return {
            "score": score,
            "grade": grade,
            "warnings": warnings
        }

    def get_report(self) -> Dict[str, Any]:
        vitals = self.collect_vitals()
        eval_res = self.evaluate_score(vitals)
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "score": eval_res["score"],
            "grade": eval_res["grade"],
            "warnings": eval_res["warnings"],
            "vitals": vitals,
            "services": {
                "TS_ENGINE": "HEALTHY" if vitals["bun_version"] else "DEGRADED",
                "PY_ENGINE": "HEALTHY",
                "UAHF_HOOKS": "HEALTHY" if (self.project_dir / ".claude" / "hooks" / "scripts").exists() else "DOWN",
                "SKILLS_MESH": "HEALTHY" if (self.project_dir / "skills-index.toon").exists() else "DEGRADED"
            }
        }

    def format_toon(self, report: Dict[str, Any]) -> str:
        v = report["vitals"]
        return f"""health_telemetry{{timestamp:"{report['timestamp']}",score:{report['score']},grade:"{report['grade']}"}}:
  runtime[1]{{os,arch,bun_v,py_v}}:
    {v['platform']},{v['arch']},{v.get('bun_version') or 'none'},{v['python_version']}
  workflow[1]{{active,step,circuit_breaker,streak,spans}}:
    {v['has_workflow']},{v['current_step']},{v['circuit_breaker']},{v['failure_streak']},{v['traces_count']}
  warnings[{len(report['warnings'])}]:
""" + "\n".join(f"    - \"{w}\"" for w in report["warnings"])
