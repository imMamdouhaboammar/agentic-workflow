#!/usr/bin/env python3
"""
registry.py — Integrations Registry & Manifest Manager

Maintains declarative metadata for supportive tools, frameworks, and agentic skills
such as Ponytail, TOON, Fable, and Caveman, supporting native dynamic expansion.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class IntegrationDefinition:
    id: str
    name: str
    repo: str
    description: str
    category: str  # simplicity_governor, notation_protocol, lifecycle_harness, terse_comm, etc.
    lifecycle_phases: List[str] = field(default_factory=list)
    install: Dict[str, Any] = field(default_factory=dict)
    detection: Dict[str, Any] = field(default_factory=dict)
    directives: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntegrationDefinition":
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            repo=data.get("repo", ""),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            lifecycle_phases=data.get("lifecycle_phases", []),
            install=data.get("install", {}),
            detection=data.get("detection", {}),
            directives=data.get("directives", {})
        )


class IntegrationsRegistry:
    """Manages the full catalog of supportive integrations."""

    def __init__(self, manifest_path: Optional[str] = None):
        self.manifest_path = manifest_path
        self._integrations: Dict[str, IntegrationDefinition] = {}
        if manifest_path and os.path.exists(manifest_path):
            self.load_from_file(manifest_path)

    def load_from_file(self, path: str) -> None:
        """Loads integrations manifest from JSON."""
        self.manifest_path = os.path.abspath(path)
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._integrations.clear()
        for item in data.get("integrations", []):
            defn = IntegrationDefinition.from_dict(item)
            self._integrations[defn.id] = defn

    def save_to_file(self, path: Optional[str] = None) -> None:
        """Persists integrations manifest to JSON."""
        target = path or self.manifest_path
        if not target:
            raise ValueError("No target path specified for saving integrations manifest.")
        data = {
            "version": "1.0.0",
            "description": "Declarative registry of supportive tools, frameworks, and agentic skills for AgenticWorkflow",
            "integrations": [i.to_dict() for i in self._integrations.values()]
        }
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register(self, definition: IntegrationDefinition) -> None:
        """Registers or updates an integration definition."""
        self._integrations[definition.id] = definition

    def get(self, integration_id: str) -> Optional[IntegrationDefinition]:
        return self._integrations.get(integration_id)

    def list_all(self) -> List[IntegrationDefinition]:
        return list(self._integrations.values())

    def get_for_phase(self, phase: str) -> List[IntegrationDefinition]:
        """Returns all integrations bound to a specific workflow phase or continuous."""
        phase_clean = phase.lower().strip()
        matched = []
        for item in self._integrations.values():
            if "continuous" in item.lifecycle_phases or phase_clean in item.lifecycle_phases:
                matched.append(item)
        return matched


def get_default_registry(project_dir: str = ".") -> IntegrationsRegistry:
    """Instantiates registry from project root integrations.json with repo fallback."""
    manifest_path = os.path.join(os.path.abspath(project_dir), "integrations.json")
    if not os.path.exists(manifest_path):
        repo_fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "integrations.json"))
        if os.path.exists(repo_fallback):
            manifest_path = repo_fallback
    return IntegrationsRegistry(manifest_path=manifest_path)

