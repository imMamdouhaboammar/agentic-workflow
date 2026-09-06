"""
core/system/updater.py — Python Auto-Updater Engine for AgenticWorkflow
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class AutoUpdater:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.history_file = self.project_dir / ".update_history.json"

    def _run_git(self, cmd: str) -> str:
        try:
            res = subprocess.run(
                f"git {cmd}",
                shell=True,
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def get_local_version(self) -> str:
        pkg = self.project_dir / "package.json"
        if pkg.exists():
            try:
                with open(pkg, "r", encoding="utf-8") as f:
                    return json.load(f).get("version", "1.0.0")
            except Exception:
                return "1.0.0"
        return "1.0.0"

    def check_for_updates(self) -> Dict[str, Any]:
        curr = self._run_git("rev-parse HEAD") or "unknown"
        branch = self._run_git("rev-parse --abbrev-ref HEAD") or "main"
        ver = self.get_local_version()

        remote = curr
        behind = 0
        commits: List[Dict[str, str]] = []

        try:
            remote_head = self._run_git(f"ls-remote origin refs/heads/{branch}")
            if remote_head:
                remote = remote_head.split()[0]
            if remote and remote != curr and remote != "unknown":
                behind = 1
                commits.append({
                    "hash": remote[:7],
                    "message": f"Upstream update available on origin/{branch}",
                    "date": "recent"
                })
        except Exception:
            remote = curr

        return {
            "has_update": remote != curr and remote != "unknown",
            "current_commit": curr,
            "current_version": ver,
            "remote_commit": remote,
            "branch": branch,
            "behind_count": behind,
            "commits": commits,
            "channel": "stable" if branch == "main" else "nightly"
        }

    def update(self, strategy: str = "stash-and-pull", force: bool = False, auto_reinstall: bool = False) -> Dict[str, Any]:
        branch = self._run_git("rev-parse --abbrev-ref HEAD") or "main"
        prev_commit = self._run_git("rev-parse HEAD")
        dirty = bool(self._run_git("status --porcelain"))
        stashed = False

        if dirty:
            if strategy == "stash-and-pull":
                self._run_git(f"stash push -m 'py-auto-update'")
                stashed = True
            elif not force:
                return {
                    "success": False,
                    "previous_commit": prev_commit,
                    "new_commit": prev_commit,
                    "message": "Working directory dirty. Use force or stash first.",
                    "stashed": False
                }

        try:
            self._run_git(f"pull origin {branch}")
            new_commit = self._run_git("rev-parse HEAD")

            reinstalled = False
            if auto_reinstall:
                try:
                    subprocess.run("bun install", shell=True, cwd=self.project_dir, capture_output=True)
                    reinstalled = True
                except Exception:
                    reinstalled = False

            self._save_history({
                "previous_commit": prev_commit,
                "new_commit": new_commit,
                "branch": branch,
                "stashed": stashed
            })

            return {
                "success": True,
                "previous_commit": prev_commit,
                "new_commit": new_commit,
                "message": f"Updated from {prev_commit[:7]} to {new_commit[:7]}",
                "stashed": stashed,
                "reinstalled": reinstalled
            }
        except Exception as e:
            if stashed:
                self._run_git("stash pop")
            return {
                "success": False,
                "previous_commit": prev_commit,
                "new_commit": prev_commit,
                "message": f"Update failed: {e}",
                "stashed": False
            }

    def rollback(self) -> Dict[str, Any]:
        history = self.get_history()
        if not history:
            return {"success": False, "message": "No update history found to rollback."}

        last = history.pop()
        target = last.get("previous_commit")
        try:
            self._run_git(f"reset --hard {target}")
            if last.get("stashed"):
                try:
                    self._run_git("stash pop")
                except Exception:
                    _popped = False
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            return {"success": True, "rolled_back_to": target, "message": f"Rolled back to {target[:7]}"}
        except Exception as e:
            return {"success": False, "message": f"Rollback failed: {e}"}

    def get_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self, record: Dict[str, Any]):
        h = self.get_history()
        h.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(h, f, indent=2)
        except Exception:
            _saved = False
