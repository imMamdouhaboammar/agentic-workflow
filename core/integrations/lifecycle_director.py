#!/usr/bin/env python3
"""
lifecycle_director.py — Sequential Operational Lifecycle Director

Directs the entire autonomous workflow sequentially across 5 core phases:
1. Continuous Protocol Layer (TOON v4.1 & Caveman Brevity)
2. Research & Intelligence (Skills Mesh & Fable Discover)
3. Architecture & Planning (Ponytail YAGNI Ladder Rung 1-3 & Fable Plan)
4. Production Implementation (Ponytail Rung 4-7 Surgical Diff & Fable Circuit Breaker)
5. Multi-Pass Verification & Quality Gates (Clean Code Guard, Ponytail Audit & L0-L2)
6. Handoff & Continuation State (Fable Handoff & TOON Ledger)

Ensures supportive tools are automatically employed in the correct place without
requiring manual user decision.
"""

import os
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from core.integrations.registry import IntegrationsRegistry, get_default_registry


@dataclass
class PhaseDirectives:
    phase: str
    active_integrations: List[str]
    system_prompt_overlay: str
    rules: List[str]
    tools_engaged: List[str]


class LifecycleDirector:
    """Orchestrates supportive tools sequentially throughout the workflow lifecycle."""

    def __init__(self, project_dir: str = ".", registry: Optional[IntegrationsRegistry] = None):
        self.project_dir = os.path.abspath(project_dir)
        self.registry = registry or get_default_registry(self.project_dir)

    def get_phase_directives(self, phase: str) -> PhaseDirectives:
        """Synthesizes unified operational directives for the specified workflow phase."""
        phase_norm = phase.lower().strip()
        matched = self.registry.get_for_phase(phase_norm)

        active_names = [m.name for m in matched]
        tools_engaged = [m.id for m in matched]
        rules = []
        directive_sections = []

        # 1. Continuous protocols (TOON & Caveman)
        toon_item = self.registry.get("toon")
        if toon_item and "continuous" in toon_item.directives:
            directive_sections.append(f"### [Continuous Protocol] TOON v4.1 Serialization\n{toon_item.directives['continuous']}")
            rules.append("Format all structured datasets, task tables, and trace logs in TOON syntax to conserve 30-60% tokens.")

        caveman_item = self.registry.get("caveman")
        if caveman_item and "continuous" in caveman_item.directives:
            directive_sections.append(f"### [Communication Protocol] Caveman Terse Mode\n{caveman_item.directives['continuous']}")
            rules.append("Eliminate pleasantries and conversational filler in logs and thoughts; preserve exact code, paths, and errors.")

        # 2. Phase-specific directives
        for item in matched:
            if phase_norm in item.directives:
                directive_sections.append(f"### [{item.name}] Phase Directives ({phase_norm.capitalize()})\n{item.directives[phase_norm]}")
                rules.append(f"[{item.name}] {item.directives[phase_norm]}")

        # Phase-specific synthesized overview
        if phase_norm == "planning":
            overview = (
                "## 🧭 Sequential Lifecycle Directive: Phase 2 — Architecture & Planning\n"
                "Before approving or implementing any architectural design, you MUST enforce the Ponytail YAGNI ladder:\n"
                "1. Does this speculative requirement need to exist at all? If not, skip it.\n"
                "2. Is a helper or pattern already present in this codebase? Reuse it.\n"
                "3. Does the standard library or runtime platform cover it? Use it.\n"
                "4. Structure deliverables as verifiable Fable contracts with explicit success criteria.\n"
                "5. Compile and validate OmniSkill SkillSpec contracts and dynamic DAG execution paths."
            )
        elif phase_norm == "implementation":
            overview = (
                "## 🔨 Sequential Lifecycle Directive: Phase 3 — Production Implementation\n"
                "Enforce surgical code changes:\n"
                "1. Shortest working diff wins. Minimum code needed to fulfill requirements.\n"
                "2. Fix root causes at callers/callees, not symptoms.\n"
                "3. Fable Circuit Breaker is active: if failure streak >= 2, halt speculative modifications.\n"
                "4. Follow OmniSkill progressive disclosure: frontmatter <=1024 chars, core SKILL.md, references/, scripts/."
            )
        elif phase_norm == "verification":
            overview = (
                "## 🛡️ Sequential Lifecycle Directive: Phase 4 — Verification & Quality Gates\n"
                "1. Run Clean Code Guard (SOLID, 24 Imperatives).\n"
                "2. Conduct Ponytail Anti-Debt audit: inspect for unnecessary scaffolding, dead config, or bloat.\n"
                "3. Execute L0 Anti-Skip, L1 Verification, L1.5 pACS (min score >= 70), and L2 Review.\n"
                "4. Enforce OmniSkill 4-Layer Validation (Artifact, Discovery, Behavior, Portability)."
            )
        elif phase_norm == "handoff":
            overview = (
                "## 🏁 Sequential Lifecycle Directive: Phase 5 — Handoff & Continuation\n"
                "1. Compact session learnings into durable continuation state (.fable/state.json and .fable/PROGRESS.md).\n"
                "2. Archive telemetry and audit logs using high-density TOON format."
            )
        else:
            overview = f"## ⚡ Sequential Lifecycle Directive: {phase_norm.capitalize()} Phase"

        system_prompt = f"{overview}\n\n" + "\n\n".join(directive_sections)

        return PhaseDirectives(
            phase=phase_norm,
            active_integrations=active_names,
            system_prompt_overlay=system_prompt,
            rules=rules,
            tools_engaged=tools_engaged
        )

    def execute_pre_phase_guards(self, phase: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs automated pre-phase safety gates and policy evaluations."""
        ctx = context or {}
        phase_norm = phase.lower().strip()
        result = {
            "phase": phase_norm,
            "allowed": True,
            "warnings": [],
            "actions_taken": []
        }

        # Check circuit breaker if in implementation
        if phase_norm == "implementation":
            failure_streak = ctx.get("failure_streak", 0)
            if failure_streak >= 2:
                result["allowed"] = False
                result["warnings"].append(
                    f"Fable Circuit Breaker TRIPPED: Consecutive failures ({failure_streak}) >= 2. "
                    "Halting speculative execution to prevent thrashing."
                )
                result["actions_taken"].append("trip_circuit_breaker")

        # Check planning simplicity gate
        if phase_norm == "planning":
            result["actions_taken"].append("enforce_ponytail_yagni_gate")

        return result

    def execute_post_phase_actions(self, phase: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes automated post-phase validations and handoffs."""
        ctx = context or {}
        phase_norm = phase.lower().strip()
        result = {
            "phase": phase_norm,
            "success": True,
            "artifacts_generated": []
        }

        # If handoff phase, ensure .fable continuation state
        if phase_norm == "handoff":
            fable_dir = os.path.join(self.project_dir, ".fable")
            os.makedirs(fable_dir, exist_ok=True)
            state_file = os.path.join(fable_dir, "state.json")
            progress_file = os.path.join(fable_dir, "PROGRESS.md")

            state_payload = {
                "trace_id": ctx.get("trace_id", f"trace_{int(time.time())}"),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "COMPLETED",
                "next_action": ctx.get("next_action", "All workflow stages verified cleanly.")
            }
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_payload, f, indent=2)

            with open(progress_file, "w", encoding="utf-8") as f:
                f.write(f"# Fable Continuation Progress\n\n- Timestamp: {state_payload['timestamp']}\n- Trace: `{state_payload['trace_id']}`\n- Next Action: {state_payload['next_action']}\n")

            result["artifacts_generated"].extend([state_file, progress_file])

        return result
