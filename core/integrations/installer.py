#!/usr/bin/env python3
"""
installer.py — Autonomous Supportive Tools Provisioner

Discovers, verifies, and installs external supportive tools and frameworks
(Ponytail, TOON, Fable, Caveman, and dynamic extensions) across AI agent environments:
- ~/.gemini/config/skills
- ~/.claude/skills
- ~/.agents/skills
- ~/.codex/skills
"""

import os
import sys
import shutil
import subprocess
import importlib.util
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
from typing import Dict, List, Optional, Any, Tuple

from core.integrations.registry import IntegrationDefinition, IntegrationsRegistry, get_default_registry


@dataclass
class InstallationStatus:
    id: str
    name: str
    installed: bool
    status: str  # "INSTALLED", "MISSING", "ERROR", "PROVISIONED"
    details: str
    locations: List[str]


class IntegrationInstaller:
    """Provisions and verifies external supportive tools across agent environments."""

    def __init__(self, project_dir: str = "."):
        self.project_dir = os.path.abspath(project_dir)
        self.home_dir = os.path.expanduser("~")
        self.target_skill_dirs = [
            os.path.join(self.home_dir, ".gemini", "config", "skills"),
            os.path.join(self.home_dir, ".claude", "skills"),
            os.path.join(self.home_dir, ".agents", "skills"),
            os.path.join(self.home_dir, ".codex", "skills"),
        ]

    def _find_existing_skill_dir(self, skill_name: str) -> Optional[str]:
        """Searches user environments and agent-kernel plugins for an existing skill folder."""
        search_locations = [
            *self.target_skill_dirs,
            os.path.join(self.home_dir, ".agent-kernel", "plugins", skill_name, "skills", skill_name),
            os.path.join(self.home_dir, ".agent-kernel", "plugins", skill_name, "skills"),
            os.path.join(self.home_dir, ".claude", "plugins", "marketplaces", skill_name),
        ]
        for loc in search_locations:
            if os.path.isdir(loc):
                skill_file = os.path.join(loc, "SKILL.md")
                if os.path.isfile(skill_file):
                    return loc
                child_loc = os.path.join(loc, skill_name)
                if os.path.isdir(child_loc) and os.path.isfile(os.path.join(child_loc, "SKILL.md")):
                    return child_loc
        return None

    def check_status(self, item: IntegrationDefinition) -> InstallationStatus:
        """Determines if an integration is installed and healthy."""
        detected_locations = []

        # 1. Check skill directories
        skill_names = item.install.get("skill_names", [item.id])
        for sname in skill_names:
            for base_dir in self.target_skill_dirs:
                candidate = os.path.join(base_dir, sname)
                if os.path.exists(candidate):
                    detected_locations.append(candidate)

        # 2. Check npm / bun package
        npm_pkg = item.detection.get("npm_package")
        if npm_pkg:
            pkg_path = os.path.join(self.project_dir, "node_modules", npm_pkg)
            if os.path.exists(pkg_path):
                detected_locations.append(f"node_modules/{npm_pkg}")

        # 3. Check python module
        py_mod = item.detection.get("python_module")
        if py_mod:
            try:
                spec = importlib.util.find_spec(py_mod)
                if spec is not None:
                    detected_locations.append(f"python:{py_mod}")
            except Exception as detection_err:
                logger.debug("Python module detection failed for %s: %s", py_mod, detection_err)

        # 4. Check state dir
        state_dir = item.detection.get("state_dir")
        if state_dir:
            full_state = os.path.join(self.project_dir, state_dir)
            if os.path.isdir(full_state):
                detected_locations.append(state_dir)

        is_installed = len(detected_locations) > 0
        status_str = "INSTALLED" if is_installed else "MISSING"
        details = f"Active at {len(detected_locations)} location(s)" if is_installed else "Not found in active agent skill paths or project dependencies"

        return InstallationStatus(
            id=item.id,
            name=item.name,
            installed=is_installed,
            status=status_str,
            details=details,
            locations=detected_locations
        )

    def provision(self, item: IntegrationDefinition, synchronize_all: bool = True) -> InstallationStatus:
        """Installs or provisions an integration, syncing across all agent environments."""
        current = self.check_status(item)
        strategy = item.install.get("strategy", "skill")
        created_locations = []

        try:
            if strategy in ["skill", "hybrid"]:
                skill_names = item.install.get("skill_names", [item.id])
                for sname in skill_names:
                    existing = self._find_existing_skill_dir(sname)
                    if existing:
                        for target_dir in self.target_skill_dirs:
                            dest = os.path.join(target_dir, sname)
                            if not os.path.exists(dest):
                                os.makedirs(target_dir, exist_ok=True)
                                try:
                                    os.symlink(existing, dest)
                                    created_locations.append(dest)
                                except OSError:
                                    shutil.copytree(existing, dest, dirs_exist_ok=True)
                                    created_locations.append(dest)
                    else:
                        # Fallback clone
                        fallback_git = item.install.get("fallback_git")
                        if fallback_git:
                            primary_target = os.path.join(self.home_dir, ".agents", "skills", sname)
                            os.makedirs(os.path.dirname(primary_target), exist_ok=True)
                            try:
                                subprocess.run(
                                    ["git", "clone", "--depth", "1", fallback_git, primary_target],
                                    check=True,
                                    capture_output=True,
                                    timeout=30
                                )
                                created_locations.append(primary_target)
                                for target_dir in self.target_skill_dirs:
                                    dest = os.path.join(target_dir, sname)
                                    if not os.path.exists(dest):
                                        os.makedirs(target_dir, exist_ok=True)
                                        try:
                                            os.symlink(primary_target, dest)
                                            created_locations.append(dest)
                                        except OSError:
                                            shutil.copytree(primary_target, dest, dirs_exist_ok=True)
                                            created_locations.append(dest)
                            except Exception as copy_err:
                                logger.debug("Skill target copy fallback failed: %s", copy_err)

            if strategy in ["package", "hybrid"]:
                bun_pkg = item.install.get("bun_package")
                if bun_pkg and shutil.which("bun"):
                    pkg_name = item.detection.get("npm_package")
                    if not pkg_name or not os.path.exists(os.path.join(self.project_dir, "node_modules", pkg_name)):
                        try:
                            subprocess.run(
                                ["bun", "add", bun_pkg],
                                cwd=self.project_dir,
                                check=True,
                                capture_output=True,
                                timeout=30
                            )
                            created_locations.append(f"bun:{bun_pkg}")
                        except Exception as bun_err:
                            logger.debug("Bun package install failed: %s", bun_err)

            post_status = self.check_status(item)
            if post_status.installed or created_locations:
                status_label = "PROVISIONED" if created_locations else post_status.status
                return InstallationStatus(
                    id=item.id,
                    name=item.name,
                    installed=True,
                    status=status_label,
                    details=f"Active at {len(post_status.locations)} location(s)" + (f" ({len(created_locations)} newly synced)" if created_locations else ""),
                    locations=post_status.locations
                )
            else:
                return InstallationStatus(
                    id=item.id,
                    name=item.name,
                    installed=False,
                    status="ERROR",
                    details="Provisioning completed with no active targets confirmed",
                    locations=[]
                )
        except Exception as e:
            return InstallationStatus(
                id=item.id,
                name=item.name,
                installed=False,
                status="ERROR",
                details=f"Provisioning error: {str(e)}",
                locations=[]
            )

    def provision_all(self, registry: Optional[IntegrationsRegistry] = None) -> List[InstallationStatus]:
        """Ensures all registered supportive integrations are provisioned and synchronized."""
        reg = registry or get_default_registry(self.project_dir)
        results = []
        for item in reg.list_all():
            res = self.provision(item, synchronize_all=True)
            results.append(res)
        return results

    def check_all(self, registry: Optional[IntegrationsRegistry] = None) -> List[InstallationStatus]:
        """Checks installation status for all registered integrations."""
        reg = registry or get_default_registry(self.project_dir)
        return [self.check_status(item) for item in reg.list_all()]
