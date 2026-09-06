"""
AgenticWorkflow: Universal Autonomous Agentic Toolchain & Pluripotent Stem-Cell Framework
"""

__version__ = "1.2.0"
__author__ = "Mamdouh Aboammar"

from core.autopilot_engine import AutopilotEngine
from core.clean_code_guard import CleanCodeChecker, audit_directory, run_guard_report
from core.multi_agent_system import MultiAgentManager, CircuitBreaker, AgentRole, AgentSpan
from core.skills_indexer import AgenticSkillsMesh, SkillScanner, AgenticNode, NodeType
from core.hooks import HookDispatcher
from core.integrations import IntegrationInstaller, LifecycleDirector

# Ergonomic aliases
SkillsIndexer = AgenticSkillsMesh

__all__ = [
    "__version__",
    "__author__",
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
]
