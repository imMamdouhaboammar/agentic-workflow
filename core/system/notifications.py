"""
core/system/notifications.py — Python Terminal & Desktop Notification Engine
"""

import os
import platform
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class NotificationEngine:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.history_file = self.project_dir / ".notifications.json"

    def render_banner(self, title: str, message: str, level: str = "INFO") -> str:
        icons = {
            "SUCCESS": "✅",
            "WARN": "⚠️",
            "ERROR": "🛑",
            "CRITICAL": "🛑",
            "ANNOUNCEMENT": "📢",
            "INFO": "ℹ️"
        }
        icon = icons.get(level, "ℹ️")
        lines = message.split("\n")
        width = min(80, max(50, len(title) + 20, max((len(l) for l in lines), default=40) + 6))
        border = "═" * width

        banner = [
            f"╔{border}╗",
            f"  {icon} [{level}]: {title}",
            f"╟{border}╢"
        ]
        for l in lines:
            banner.append(f"  {l}")
        banner.append(f"╚{border}╝")
        return "\n".join(banner)

    def send_desktop(self, title: str, message: str, sound: bool = True) -> bool:
        if os.environ.get("CI") or not os.isatty(1):
            return False

        sys_platform = platform.system().lower()
        clean_t = title.replace('"', '\\"')
        clean_m = message.replace('"', '\\"')

        try:
            if sys_platform == "darwin":
                sound_cmd = 'sound name "Glass"' if sound else ''
                script = f'display notification "{clean_m}" with title "{clean_t}" {sound_cmd}'
                subprocess.run(f"osascript -e '{script}'", shell=True, capture_output=True)
                return True
            elif sys_platform == "linux":
                subprocess.run(f'notify-send "{clean_t}" "{clean_m}"', shell=True, capture_output=True)
                return True
        except Exception:
            pass
        return False

    def send(self, title: str, message: str, level: str = "INFO", sound: bool = True, desktop: bool = True) -> Dict[str, Any]:
        banner = self.render_banner(title, message, level)
        print(banner)

        if desktop:
            self.send_desktop(title, message, sound)

        record = {
            "id": f"notif_{int(time.time()*1000)}",
            "title": title,
            "message": message,
            "level": level,
            "timestamp": time.time()
        }
        self._save_record(record)
        return record

    def get_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_record(self, record: Dict[str, Any]):
        h = self.get_history()
        h.insert(0, record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(h[:50], f, indent=2)
        except Exception:
            pass
