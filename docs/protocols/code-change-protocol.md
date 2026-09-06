# Code Change Protocol (CCP) — Detailed Specification

> This document details the procedure for Absolute Criterion 3 (Code Change Protocol).
> Consult before making any code modifications.

## The 3-Step Protocol

Before writing, modifying, adding, or deleting code, you must internally perform the following 3 steps.
Skipping this protocol is a direct violation of the Absolute Criteria.
The protocol is always performed, with analysis depth scaling proportionally with the scope of the change.

### Step 1 — Understand Intent
- Define the purpose of the change (bug fix, feature addition, refactoring, performance) and constraints (compatibility, tech stack) in 1-2 sentences.
- For minor changes (typos, comments, formatting), confirm "no ripple effect" and execute immediately.

### Step 2 — Ripple Effect Analysis
- Direct dependencies + Call relationships (caller / callee)
- Structural relationships (inheritance, composition, reference)
- Data model / schema / type cascade changes
- Tests, configuration, documentation, and API specifications
- If tight coupling or shotgun surgery risks exist, **mandatory** prior notification and discussion with the user.

### Step 3 — Change Plan
- Step-by-step change sequence (which file/function first → dependency propagation → test/doc alignment).
- Propose refactoring opportunities that reduce coupling / increase cohesion (execute only after user approval).

## Proportionality Rule

| Change Scope | Applied Depth |
|---|---|
| Minor (typos, comments, formatting) | Step 1 only — confirm "no ripple effect" |
| Standard (functions, logic, files) | Full 3 steps |
| Large-scale (architecture, public API, cross-cutting) | Full 3 steps + mandatory prior user approval |

## Communication Rules
- Avoid unnecessarily verbose theoretical explanations; focus on actual code and concrete steps.
- Add concise rationale for important design decisions.
- If ambiguities exist, do not avoid work — explicitly state "reasonable assumptions" and propose the optimal design.

## Coding Anchor Points (CAP)

Every step of CCP must internalize the following 4 mindsets:

- **CAP-1: Think Before Coding** — Never modify code before reading it. Surface trade-offs. Ask when unclear.
- **CAP-2: Simplicity First** — Minimal code. No speculative features, premature abstractions, or unnecessary helpers.
- **CAP-3: Goal-Based Execution** — Define success criteria first, verify after implementation.
- **CAP-4: Surgical Changes** — Perform only requested changes. No unrelated "improvements".

> CAP is subordinate to CCP; when conflicting with Absolute Criterion 1 (Quality), Quality always wins. Details: `AGENTS.md §2`.
