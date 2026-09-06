"""
tests/test_system_engines_py.py — Python Parity Tests for 9 System Engines
"""

import unittest
import os
import shutil
import tempfile
from pathlib import Path

from core.system.updater import AutoUpdater
from core.system.installer import AutoInstaller
from core.system.refresher import Refresher
from core.system.doctor import DoctorEngine
from core.system.health import HealthEngine
from core.system.dependencies import DependenciesEngine
from core.system.notifications import NotificationEngine
from core.system.announcements import AnnouncementEngine
from core.system.version_tracker import VersionTracker

ROOT_DIR = Path(__file__).parent.parent.resolve()


class TestSystemEnginesPython(unittest.TestCase):

    def test_auto_updater(self):
        updater = AutoUpdater(str(ROOT_DIR))
        ver = updater.get_local_version()
        self.assertTrue(len(ver) > 0)

        check = updater.check_for_updates()
        self.assertIn("has_update", check)
        self.assertEqual(check["current_version"], ver)
        self.assertIn(check["channel"], ["stable", "nightly"])

    def test_auto_installer(self):
        installer = AutoInstaller(str(ROOT_DIR))
        targets = installer.get_host_targets()
        self.assertEqual(len(targets), 5)
        platforms = [t["platform"] for t in targets]
        self.assertIn("claude", platforms)
        self.assertIn("gemini", platforms)
        self.assertIn("cursor", platforms)
        self.assertIn("agents", platforms)

        status = installer.check_status()
        self.assertTrue(status["success"])
        self.assertGreaterEqual(len(status["system_deps"]), 3)

    def test_refresher(self):
        refresher = Refresher(str(ROOT_DIR))
        res = refresher.refresh(clear_bytecode=True, rebuild_index=False, sync_integrations=False)
        self.assertTrue(res["success"])
        self.assertIsInstance(res["freed_bytes"], int)
        self.assertIsInstance(res["messages"], list)

    def test_doctor_engine(self):
        doctor = DoctorEngine(str(ROOT_DIR))
        report = doctor.diagnose()
        self.assertGreaterEqual(report["total"], 8)
        self.assertGreater(report["passed"], 0)

        check_ids = [c["id"] for c in report["checks"]]
        self.assertIn("runtime-bun", check_ids)
        self.assertIn("runtime-python", check_ids)
        self.assertIn("cli-permission", check_ids)
        self.assertIn("hooks-uahf", check_ids)

    def test_health_engine(self):
        health = HealthEngine(str(ROOT_DIR))
        report = health.get_report()
        self.assertIn(report["grade"], ["A+", "A", "B", "C", "F"])
        self.assertGreater(report["score"], 0)
        self.assertIn("TS_ENGINE", report["services"])

        toon = health.format_toon(report)
        self.assertIn("health_telemetry{", toon)

    def test_dependencies_engine(self):
        deps = DependenciesEngine(str(ROOT_DIR))
        audit = deps.audit()
        self.assertGreater(audit["total"], 0)
        self.assertGreater(audit["satisfied"], 0)
        dep_names = [d["name"] for d in audit["dependencies"]]
        self.assertIn("python:asyncio", dep_names)

    def test_notifications_engine(self):
        notifier = NotificationEngine(str(ROOT_DIR))
        banner = notifier.render_banner("Test Title", "Test Message\nLine 2", "SUCCESS")
        self.assertIn("SUCCESS", banner)
        self.assertIn("Test Title", banner)

        record = notifier.send("Py Test", "Alert details", "INFO", sound=False, desktop=False)
        self.assertEqual(record["title"], "Py Test")
        hist = notifier.get_history()
        self.assertGreater(len(hist), 0)

    def test_announcement_engine(self):
        announcer = AnnouncementEngine(str(ROOT_DIR))
        anns = announcer.list_all()
        self.assertGreaterEqual(len(anns), 2)
        unread = announcer.get_unread()
        self.assertIsInstance(unread, list)

        first_id = anns[0]["id"]
        announcer.mark_as_read(first_id)
        announcer.mark_all_as_read()
        self.assertEqual(len(announcer.get_unread()), 0)

    def test_version_tracker(self):
        tracker = VersionTracker(str(ROOT_DIR))
        matrix = tracker.get_version_matrix()
        self.assertTrue(len(matrix["cli_version"]) > 0)
        self.assertEqual(len(matrix["components"]), 7)

        self.assertEqual(tracker.compare_versions("1.1.0", "1.0.5"), 1)
        self.assertEqual(tracker.compare_versions("1.0.5", "1.1.0"), -1)
        self.assertEqual(tracker.compare_versions("1.1.0", "1.1.0"), 0)


if __name__ == "__main__":
    unittest.main()
