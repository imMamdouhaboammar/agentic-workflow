"""
AgenticWorkflow Core Engine & Autonomous Toolchain
"""

from core.autopilot_engine import AutopilotEngine
from core.clean_code_guard import CleanCodeChecker, audit_directory, run_guard_report
from core.multi_agent_system import MultiAgentManager, CircuitBreaker, AgentRole, AgentSpan
from core.skills_indexer import AgenticSkillsMesh, SkillScanner, AgenticNode, NodeType
from core.hooks import HookDispatcher
from core.integrations import IntegrationInstaller, LifecycleDirector
from core.system import (
    AutoUpdater,
    AutoInstaller,
    Refresher,
    DoctorEngine,
    HealthEngine,
    DependenciesEngine,
    NotificationEngine,
    AnnouncementEngine,
    VersionTracker,
)

# Ergonomic aliases
SkillsIndexer = AgenticSkillsMesh

__all__ = [
    "AutopilotEngine",
    "CleanCodeChecker",
    "audit_directory",
    "run_guard_report",
    "MultiAgentManager",
    "CircuitBreaker",
    "AgentRole",
    "AgentSpan",
    "AgenticSkillsMesh",
    "SkillsIndexer",
    "SkillScanner",
    "AgenticNode",
    "NodeType",
    "HookDispatcher",
    "IntegrationInstaller",
    "LifecycleDirector",
    "AutoUpdater",
    "AutoInstaller",
    "Refresher",
    "DoctorEngine",
    "HealthEngine",
    "DependenciesEngine",
    "NotificationEngine",
    "AnnouncementEngine",
    "VersionTracker",
]
