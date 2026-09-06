"""
core/system/installer.py — Python Auto-Installer Engine for AgenticWorkflow
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class AutoInstaller:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.home_dir = Path.home()

    def _check_binary(self, cmd: str) -> Dict[str, Any]:
        try:
            res = subprocess.run(f"{cmd} --version", shell=True, capture_output=True, text=True)
            return {"available": res.returncode == 0, "version": res.stdout.strip().split("\n")[0]}
        except Exception:
            return {"available": False}

    def get_host_targets(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Claude Code Skills",
                "platform": "claude",
                "path": str(self.home_dir / ".claude" / "skills" / "agentic-workflow"),
                "installed": (self.home_dir / ".claude" / "skills" / "agentic-workflow").exists()
            },
            {
                "name": "Gemini CLI / Antigravity Skills",
                "platform": "gemini",
                "path": str(self.home_dir / ".gemini" / "config" / "skills" / "agentic-workflow"),
                "installed": (self.home_dir / ".gemini" / "config" / "skills" / "agentic-workflow").exists()
            },
            {
                "name": "Cursor IDE Skills",
                "platform": "cursor",
                "path": str(self.home_dir / ".cursor" / "skills" / "agentic-workflow"),
                "installed": (self.home_dir / ".cursor" / "skills" / "agentic-workflow").exists()
            },
            {
                "name": "Codex / OpenCode Skills",
                "platform": "codex",
                "path": str(self.home_dir / ".codex" / "skills" / "agentic-workflow"),
                "installed": (self.home_dir / ".codex" / "skills" / "agentic-workflow").exists()
            },
            {
                "name": "Universal Agent Kernel",
                "platform": "agents",
                "path": str(self.home_dir / ".agents" / "skills" / "agentic-workflow"),
                "installed": (self.home_dir / ".agents" / "skills" / "agentic-workflow").exists()
            }
        ]

    def check_status(self) -> Dict[str, Any]:
        targets = self.get_host_targets()
        installed = [t for t in targets if t["installed"]]
        skipped = [t for t in targets if not t["installed"]]

        bin_paths = [
            str(self.home_dir / ".local" / "bin" / "agentic-workflow"),
            "/usr/local/bin/agentic-workflow"
        ]
        linked = [p for p in bin_paths if os.path.exists(p)]

        deps = [
            {"name": "bun", **self._check_binary("bun")},
            {"name": "node", **self._check_binary("node")},
            {"name": "python3", **self._check_binary("python3")},
            {"name": "git", **self._check_binary("git")}
        ]

        return {
            "success": True,
            "installed_targets": installed,
            "skipped_targets": skipped,
            "bin_linked": linked,
            "system_deps": deps
        }

    def install(self, platforms: Optional[List[str]] = None, global_bin: bool = True) -> Dict[str, Any]:
        requested = platforms or ["claude", "gemini", "cursor", "codex", "agents"]
        messages = []
        installed_targets = []
        bin_linked = []

        targets = self.get_host_targets()
        for t in targets:
            if t["platform"] not in requested:
                continue

            target_path = Path(t["path"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)

            try:
                shutil.copytree(
                    self.project_dir,
                    target_path,
                    ignore=shutil.ignore_patterns("node_modules", ".git", "__pycache__", ".pytest_cache")
                )
                t["installed"] = True
                installed_targets.append(t)
                messages.append(f"✓ Installed skill to {t['name']}")
            except Exception as e:
                messages.append(f"! Failed installing to {t['name']}: {e}")

        # CLI symlink
        cli_src = self.project_dir / "bin" / "cli.js"
        if cli_src.exists():
            try:
                os.chmod(cli_src, 0o755)
            except Exception:
                _chmod_ok = False

            local_bin = self.home_dir / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            link_target = local_bin / "agentic-workflow"
            try:
                if link_target.exists() or link_target.is_symlink():
                    link_target.unlink()
                link_target.symlink_to(cli_src)
                bin_linked.append(str(link_target))
                messages.append(f"✓ Linked executable to {link_target}")
            except Exception as e:
                messages.append(f"! Failed linking CLI: {e}")

        return {
            "success": len(installed_targets) > 0 or len(bin_linked) > 0,
            "installed_targets": installed_targets,
            "bin_linked": bin_linked,
            "messages": messages
        }
