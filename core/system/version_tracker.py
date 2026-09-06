"""
core/system/version_tracker.py — Python Version Tracker & Matrix Engine
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class VersionTracker:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()

    def _run_git(self, cmd: str) -> str:
        try:
            res = subprocess.run(f"git {cmd}", shell=True, cwd=self.project_dir, capture_output=True, text=True)
            return res.stdout.strip()
        except Exception:
            return ""

    def get_version_matrix(self) -> Dict[str, Any]:
        pkg = self.project_dir / "package.json"
        ver = "1.2.2"
        if pkg.exists():
            try:
                with open(pkg, "r", encoding="utf-8") as f:
                    ver = json.load(f).get("version", "1.2.2")
            except Exception:
                ver = "1.2.2"

        commit = self._run_git("rev-parse HEAD") or "unknown"
        branch = self._run_git("rev-parse --abbrev-ref HEAD") or "main"
        dirty = bool(self._run_git("status --porcelain"))

        components = [
            {"name": "AgenticWorkflow CLI", "version": ver, "channel": "stable"},
            {"name": "TypeScript Async Engine", "version": ver, "channel": "stable"},
            {"name": "Python AsyncIO Engine", "version": ver, "channel": "stable"},
            {"name": "TOON Protocol Adapter", "version": "4.1.1", "channel": "standard"},
            {"name": "Universal Agentic Hooks", "version": "1.2.0", "channel": "governed"},
            {"name": "Skills Mesh Indexer", "version": "2.0.0", "channel": "dynamic"},
            {"name": "Supportive Tools Director", "version": "1.1.0", "channel": "continuous"}
        ]

        return {
            "cli_version": ver,
            "git_commit": commit,
            "git_branch": branch,
            "git_clean": not dirty,
            "components": components
        }

    def compare_versions(self, v1: str, v2: str) -> int:
        c1 = [int(x) for x in v1.replace("v", "").split(".") if x.isdigit()]
        c2 = [int(x) for x in v2.replace("v", "").split(".") if x.isdigit()]

        for i in range(max(len(c1), len(c2))):
            n1 = c1[i] if i < len(c1) else 0
            n2 = c2[i] if i < len(c2) else 0
            if n1 > n2:
                return 1
            if n1 < n2:
                return -1
        return 0
