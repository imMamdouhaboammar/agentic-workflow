"""
Universal Agentic Hooks Framework (UAHF) — Python Core
======================================================
Multi-platform hook consumption, normalization, and policy enforcement layer.
"""

from .types import (
    HookSource,
    HookType,
    HookVerdict,
    HookEvent,
    HookResult,
    PolicyRule,
)
from .policy_engine import UniversalPolicyEngine
from .dispatcher import HookDispatcher
from .session_end import SessionEndManager

__all__ = [
    "HookSource",
    "HookType",
    "HookVerdict",
    "HookEvent",
    "HookResult",
    "PolicyRule",
    "UniversalPolicyEngine",
    "HookDispatcher",
    "SessionEndManager",
]
