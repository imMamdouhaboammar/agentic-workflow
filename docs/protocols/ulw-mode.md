# ULW (Ultrawork) Mode

> Detailed specification for Ultrawork (ULW) Mode.
> Reference when ULW is active.

## Overview

Including `ulw` anywhere in your prompt activates **Ultrawork Mode**. ULW is a **thoroughness intensity overlay orthogonal to Autopilot**.

- **Autopilot** = Automation axis (HOW) — skips `(human)` approvals
- **ULW** = Thoroughness axis (HOW THOROUGHLY) — exhaustive execution, relentless resolution of all errors

These two axes are completely independent, enabling any combination:

| | **ULW OFF** (Standard) | **ULW ON** (Maximum Rigor) |
|---|---|---|
| **Autopilot OFF** | Standard interactive | Interactive + Sisyphus Persistence (3 retries) + Mandatory Task Decomposition |
| **Autopilot ON** | Standard automated workflow | Automated workflow + Sisyphus reinforcement (3 retries) + Team-wide rigor |

## 2-Axis Comparison

| Axis | Focus | Activation | Deactivation | Scope |
|---|---|---|---|---|
| **Autopilot** | Automation (HOW) | SOT `autopilot.enabled: true` | SOT modification | Workflow steps |
| **ULW** | Thoroughness (HOW THOROUGHLY) | `ulw` keyword in prompt | Implicit (new session without `ulw`) | All tasks (interactive + workflows) |

## Activation Patterns

| User Command | Behavior |
|---|---|
| "ulw do this", "ulw refactor this" | `ulw` detected in transcript regex → ULW mode activated |
| New session without `ulw` | ULW inactive (implicit deactivation — no explicit toggle needed) |

## 3 Intensifier Rules

When ULW is active, three intensifier rules are **overlaid onto the current context**:

| Intensifier | Description | Interactive Effect | Autopilot Combined Effect |
|---|---|---|---|
| **I-1. Sisyphus Persistence** | Up to 3 retries, each using a fundamentally different approach. 100% completion or explicit blocker report. | Try up to 3 alternatives on failure | Quality Gate (Verification/pACS) retry ceiling raised from 10 to 15 |
| **I-2. Mandatory Task Decomposition** | TaskCreate → TaskUpdate → TaskList mandatory | Enforces task decomposition for all non-trivial tasks | Preserved (Autopilot already tracks via SOT) |
| **I-3. Bounded Retry Escalation** | No more than 3 consecutive retries on the same target (Quality Gates retain separate budget) — escalate to user when exceeded | Prevents infinite loops | Safety Hook blocks are always strictly respected |

## Runtime Enforcement Mechanisms

| Layer | Mechanism | Enforcement Details |
|---|---|---|
| **Hook** (Deterministic) | `_context_lib.py` — `detect_ulw_mode()` | Detects `ulw` via regex over transcript |
| **Hook** (Deterministic) | `generate_snapshot_md()` — Snapshot | Preserves ULW state in IMMORTAL priority section |
| **Hook** (Deterministic) | `extract_session_facts()` — Knowledge Archive | Tags `ulw_active: true` → queryable via RLM |
| **Hook** (Deterministic) | `restore_context.py` — SessionStart | Injects the 3 intensifier rules into context on startup |
| **Hook** (Deterministic) | `_context_lib.py` — `check_ulw_compliance()` | Deterministically validates compliance → injects warnings into IMMORTAL snapshot |
| **Hook** (Deterministic) | `generate_context_summary.py` — Stop | ULW Compliance safety net — surfaces stderr warnings on violation |

## NEVER DO
- Never retry more than 3 consecutive times on the same target without alternative hypothesis (I-3 violation; escalate to user).
- Never override a Safety Hook block (`(hook)` exit code 2) in the name of ULW.
- Never leave tasks "partially complete" and halt while ULW is active (I-1 violation).
- Never give up on errors without attempting viable alternative approaches (I-1 violation).
- Never proceed with non-trivial work implicitly without TaskCreate decomposition (I-2 violation).
