"""
core/system/dependencies.py — Python Dependencies & Multi-Ecosystem Auditor Engine
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class DependenciesEngine:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()

    def audit(self) -> Dict[str, Any]:
        deps = []

        # 1. Package.json dependencies
        pkg_file = self.project_dir / "package.json"
        if pkg_file.exists():
            try:
                with open(pkg_file, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                    all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    for name, ver in all_deps.items():
                        node_mod = self.project_dir / "node_modules" / name
                        deps.append({
                            "name": name,
                            "type": "bun-npm",
                            "status": "SATISFIED" if node_mod.exists() else "MISSING",
                            "version": ver
                        })
            except Exception:
                _pkg_read = False

        # 2. Python standard modules
        for mod in ["json", "pathlib", "unittest", "dataclasses", "asyncio"]:
            try:
                __import__(mod)
                deps.append({"name": f"python:{mod}", "type": "python", "status": "SATISFIED"})
            except ImportError:
                deps.append({"name": f"python:{mod}", "type": "python", "status": "MISSING"})

        # 3. Binaries
        for b in ["bun", "python3", "git"]:
            try:
                res = subprocess.run(f"{b} --version", shell=True, capture_output=True)
                deps.append({"name": f"bin:{b}", "type": "system-binary", "status": "SATISFIED" if res.returncode == 0 else "MISSING"})
            except Exception:
                deps.append({"name": f"bin:{b}", "type": "system-binary", "status": "MISSING"})

        satisfied = sum(1 for d in deps if d["status"] == "SATISFIED")
        missing = sum(1 for d in deps if d["status"] == "MISSING")

        return {
            "total": len(deps),
            "satisfied": satisfied,
            "missing": missing,
            "dependencies": deps,
            "all_satisfied": missing == 0
        }

    def install_missing(self) -> Dict[str, Any]:
        try:
            res = subprocess.run("bun install", shell=True, cwd=self.project_dir, capture_output=True, text=True)
            return {"success": res.returncode == 0, "message": "bun install executed"}
        except Exception as e:
            return {"success": False, "message": str(e)}
