"""
core/system/refresher.py — Python Refresher & Cache Invalidation Engine
"""

import os
import shutil
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class Refresher:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.home_dir = Path.home()

    def clear_bytecode(self) -> Dict[str, Any]:
        cleared = []
        freed = 0

        for p in self.project_dir.rglob("__pycache__"):
            if "node_modules" in str(p) or ".git" in str(p):
                continue
            try:
                for f in p.rglob("*"):
                    if f.is_file():
                        freed += f.stat().st_size
                shutil.rmtree(p, ignore_errors=True)
                cleared.append(str(p.relative_to(self.project_dir)))
            except Exception:
                _cleared = False

        for p in self.project_dir.rglob(".pytest_cache"):
            if "node_modules" in str(p):
                continue
            try:
                shutil.rmtree(p, ignore_errors=True)
                cleared.append(str(p.relative_to(self.project_dir)))
            except Exception:
                _cleared = False

        return {"cleared": cleared, "freed_bytes": freed}

    def clean_stale_locks(self) -> List[str]:
        cleared = []
        now = time.time()
        for lock_name in [".lock", ".git/index.lock"]:
            lf = self.project_dir / lock_name
            if lf.exists():
                try:
                    if now - lf.stat().st_mtime > 300:
                        lf.unlink()
                        cleared.append(lock_name)
                except Exception:
                    _unlinked = False
        return cleared

    def refresh(self, clear_bytecode: bool = True, rebuild_index: bool = True, sync_integrations: bool = True) -> Dict[str, Any]:
        start = time.time()
        messages = []
        cleared_items = []
        freed_bytes = 0

        if clear_bytecode:
            bc = self.clear_bytecode()
            cleared_items.extend(bc["cleared"])
            freed_bytes += bc["freed_bytes"]
            if bc["cleared"]:
                messages.append(f"✓ Cleared {len(bc['cleared'])} bytecode directory(ies)")

        locks = self.clean_stale_locks()
        cleared_items.extend(locks)
        if locks:
            messages.append(f"✓ Removed {len(locks)} stale lockfile(s)")

        skills_reindexed = False
        if rebuild_index:
            try:
                subprocess.run(
                    "python3 core/skills_indexer.py index",
                    shell=True,
                    cwd=self.project_dir,
                    capture_output=True
                )
                skills_reindexed = True
                messages.append("✓ Rebuilt skills mesh index")
            except Exception as e:
                messages.append(f"! Skills re-indexing notice: {e}")

        integrations_synced = False
        if sync_integrations:
            try:
                from core.integrations import IntegrationInstaller
                IntegrationInstaller(str(self.project_dir)).provision_all()
                integrations_synced = True
                messages.append("✓ Synchronized supportive integrations")
            except Exception as e:
                messages.append(f"! Integrations sync notice: {e}")

        duration_ms = int((time.time() - start) * 1000)
        return {
            "success": True,
            "cleared_items": cleared_items,
            "freed_bytes": freed_bytes,
            "skills_reindexed": skills_reindexed,
            "integrations_synced": integrations_synced,
            "duration_ms": duration_ms,
            "messages": messages
        }
