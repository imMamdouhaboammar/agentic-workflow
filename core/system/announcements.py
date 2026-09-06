"""
core/system/announcements.py — Python Announcement & Bulletin Engine
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class AnnouncementEngine:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.state_file = self.project_dir / ".announcements_seen.json"

    def get_default_announcements(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "ann_v110_engines",
                "title": "Universal System Engines Suite Online",
                "body": "AgenticWorkflow now features 9 core toolchain engines with dual-runtime parity.",
                "category": "FEATURE",
                "date": "2026-09-06",
                "version": "1.1.0",
                "priority": "high"
            },
            {
                "id": "ann_toon_v41",
                "title": "TOON Protocol v4.1 Released",
                "body": "Token-Oriented Object Notation (v4.1) delivers 30-60% token compression.",
                "category": "UPDATE",
                "date": "2026-09-01",
                "version": "1.0.5",
                "priority": "normal"
            }
        ]

    def get_seen_ids(self) -> List[str]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("seen_ids", [])
            except Exception:
                return []
        return []

    def list_all(self) -> List[Dict[str, Any]]:
        seen = set(self.get_seen_ids())
        anns = self.get_default_announcements()
        for a in anns:
            a["seen"] = a["id"] in seen
        return anns

    def get_unread(self) -> List[Dict[str, Any]]:
        return [a for a in self.list_all() if not a.get("seen")]

    def mark_as_read(self, ann_id: str):
        seen = self.get_seen_ids()
        if ann_id not in seen:
            seen.append(ann_id)
            try:
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump({"seen_ids": seen}, f, indent=2)
            except Exception:
                _saved = False

    def mark_all_as_read(self):
        all_ids = [a["id"] for a in self.list_all()]
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({"seen_ids": all_ids}, f, indent=2)
        except Exception:
            _saved = False
