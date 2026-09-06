"""
core/system/doctor.py — Python Doctor Diagnostic & Auto-Fix Engine
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class DoctorEngine:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.home_dir = Path.home()

    def _run_cmd(self, cmd: str) -> Dict[str, Any]:
        try:
            res = subprocess.run(cmd, shell=True, cwd=self.project_dir, capture_output=True, text=True)
            return {"ok": res.returncode == 0, "stdout": res.stdout.strip()}
        except Exception:
            return {"ok": False, "stdout": ""}

    def diagnose(self) -> Dict[str, Any]:
        checks = []

        # 1. Bun Runtime
        bun = self._run_cmd("bun --version")
        checks.append({
            "id": "runtime-bun",
            "title": "Bun Runtime",
            "status": "PASS" if bun["ok"] else "FAIL",
            "details": f"Bun v{bun['stdout']}" if bun["ok"] else "Bun not found.",
            "fixable": False
        })

        # 2. Python 3 Runtime
        py = self._run_cmd("python3 --version")
        checks.append({
            "id": "runtime-python",
            "title": "Python 3 Runtime",
            "status": "PASS" if py["ok"] else "FAIL",
            "details": py["stdout"] if py["ok"] else "Python 3 not found.",
            "fixable": False
        })

        # 3. CLI Permission
        cli_js = self.project_dir / "bin" / "cli.js"
        if cli_js.exists():
            is_exec = os.access(cli_js, os.X_OK)
            checks.append({
                "id": "cli-permission",
                "title": "CLI Permission (bin/cli.js)",
                "status": "PASS" if is_exec else "WARN",
                "details": "Executable" if is_exec else "Not executable",
                "fixable": not is_exec
            })
        else:
            checks.append({
                "id": "cli-permission",
                "title": "CLI Permission (bin/cli.js)",
                "status": "FAIL",
                "details": "bin/cli.js missing",
                "fixable": False
            })

        # 4. CLI Symlink
        local_bin = self.home_dir / ".local" / "bin" / "agentic-workflow"
        usr_bin = Path("/usr/local/bin/agentic-workflow")
        linked = local_bin.exists() or usr_bin.exists()
        checks.append({
            "id": "cli-symlink",
            "title": "Global CLI Symlink",
            "status": "PASS" if linked else "WARN",
            "details": f"Linked at {local_bin if local_bin.exists() else usr_bin}" if linked else "Not linked in user PATH",
            "fixable": not linked
        })

        # 5. Dependencies
        node_modules = self.project_dir / "node_modules"
        toon_pkg = node_modules / "@toon-format" / "toon"
        has_deps = node_modules.exists() and toon_pkg.exists()
        checks.append({
            "id": "dependencies-npm",
            "title": "Dependencies (@toon-format/toon)",
            "status": "PASS" if has_deps else "WARN",
            "details": "Installed" if has_deps else "node_modules missing or incomplete",
            "fixable": not has_deps
        })

        # 6. SOT State
        sot = self.project_dir / "state.yaml"
        checks.append({
            "id": "state-sot",
            "title": "Single Source of Truth (state.yaml)",
            "status": "PASS" if sot.exists() else "WARN",
            "details": "state.yaml present" if sot.exists() else "Workflow state idle",
            "fixable": False
        })

        # 7. UAHF Hooks
        hooks = self.project_dir / ".claude" / "hooks" / "scripts" / "context_guard.py"
        checks.append({
            "id": "hooks-uahf",
            "title": "UAHF Safety & Verification Scripts",
            "status": "PASS" if hooks.exists() else "FAIL",
            "details": "UAHF hooks online" if hooks.exists() else "Hooks missing",
            "fixable": False
        })

        # 8. Skills Index
        skills_toon = self.project_dir / "skills-index.toon"
        checks.append({
            "id": "skills-mesh",
            "title": "Skills Mesh Index (skills-index.toon)",
            "status": "PASS" if skills_toon.exists() else "WARN",
            "details": "skills-index.toon present" if skills_toon.exists() else "Missing index",
            "fixable": not skills_toon.exists()
        })

        passed = sum(1 for c in checks if c["status"] == "PASS")
        warned = sum(1 for c in checks if c["status"] == "WARN")
        failed = sum(1 for c in checks if c["status"] == "FAIL")

        return {
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "total": len(checks),
            "checks": checks,
            "overall_healthy": failed == 0
        }

    def fix_all(self) -> List[Dict[str, Any]]:
        diag = self.diagnose()
        fixable = [c for c in diag["checks"] if c["fixable"] and c["status"] != "PASS"]
        results = []

        for c in fixable:
            cid = c["id"]
            if cid == "cli-permission":
                cli_js = self.project_dir / "bin" / "cli.js"
                try:
                    os.chmod(cli_js, 0o755)
                    results.append({"check_id": cid, "remediated": True, "message": "Chmod 0755 bin/cli.js"})
                except Exception as e:
                    results.append({"check_id": cid, "remediated": False, "message": str(e)})
            elif cid == "cli-symlink":
                local_bin = self.home_dir / ".local" / "bin"
                local_bin.mkdir(parents=True, exist_ok=True)
                target = local_bin / "agentic-workflow"
                src = self.project_dir / "bin" / "cli.js"
                try:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                    target.symlink_to(src)
                    results.append({"check_id": cid, "remediated": True, "message": f"Symlinked {target}"})
                except Exception as e:
                    results.append({"check_id": cid, "remediated": False, "message": str(e)})
            elif cid == "dependencies-npm":
                try:
                    subprocess.run("bun install", shell=True, cwd=self.project_dir, capture_output=True)
                    results.append({"check_id": cid, "remediated": True, "message": "Ran bun install"})
                except Exception as e:
                    results.append({"check_id": cid, "remediated": False, "message": str(e)})
            elif cid == "skills-mesh":
                try:
                    subprocess.run("python3 core/skills_indexer.py index", shell=True, cwd=self.project_dir, capture_output=True)
                    results.append({"check_id": cid, "remediated": True, "message": "Rebuilt skills index"})
                except Exception as e:
                    results.append({"check_id": cid, "remediated": False, "message": str(e)})
        return results
