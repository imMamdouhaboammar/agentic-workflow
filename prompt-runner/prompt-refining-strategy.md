# Prompt Precision Redesign Strategy
> Purpose: Provide this document to Claude Code to precisely refine and sculpt all existing prompt blocks based on these standards.

---

## 1. Background Behind This Strategy

### Diagnosed Structural Problems

Full analysis results of all 112 prompts:

- **73% of all prompts are reflection/verification**. Direct execution instructions comprise only 15%.
- Core standards such as "preserve workflow philosophy", "maintain RLM pattern", and "absolute quality criteria" are **repeated across nearly 20 prompts**.
- Absolute criteria are attached in the **middle or bottom** of each prompt as cautions.
- Reflection does not build depth, but repeatedly cycles through the **same layer**.

### Core Root Cause

Because Claude loses direction from turn to turn, the prompt structure forces redirection on every single turn.
As a result, a vicious cycle is created where reflection is perpetually stacked on top of reflection.

### Why CLAUDE.md Alone Cannot Solve This

CLAUDE.md is processed by Claude as **background context**. It does not function as the "absolute criterion for this active turn".
In contrast, instructions placed directly inside the prompt reside within the **active context of this specific turn**. This functions as an absolute cognitive imprint.

### Conclusion: Both Are Required

- **CLAUDE.md**: Background standards for overall project philosophy and architecture
- **ABSOLUTE ANCHOR in Prompts**: Imprints the absolute criteria for that specific turn

---

## 2. ABSOLUTE ANCHOR — Core Design Principles

### Why the Current Approach Is Inefficient

The current approach repeats absolute criteria in **long descriptive prose**.

```
// Current approach example (~450 characters)
However, you must not forget the absolute criteria in all processes.
Completely ignore speed and token cost when this workflow operates.
The absolute criterion I desire is the quality and qualitative standard of the final deliverable.
I say again: quality and top-tier qualitative deliverables are the absolute criteria.
... (repetition of identical content below)
```

The issue is not length. The issue is that **the core message is buried within repetition**.
Furthermore, it lacks explanations of why these criteria are absolute and how to judge when conflicts occur.

### 3 Mandatory Elements of ABSOLUTE ANCHOR

Compressed keywords alone do not give Claude the **basis for decision-making in trade-off situations**.
All three elements below must be present for the imprint to work effectively:

1. **Keyword** — What is the criterion?
2. **Reason** — Why is this criterion absolute?
3. **Conflict Judgment** — How to decide in a trade-off situation?

### Standard ABSOLUTE ANCHOR Template

```
[ABSOLUTE ANCHOR]
① Quality Absolute Priority — Speed, cost, and convenience can never be justifications.
   In trade-off situations, everything other than quality is expendable.

② SOT + RLM Invariant — No improvement may compromise these two structures.
   If any possibility of compromise arises, you must notify me before implementation.

③ Implementation After Approval — Writing even a single line of code without my approval is strictly prohibited.
   Upon approval request: report implementation intent (1 sentence) + affected files + risk points only.
[/ABSOLUTE ANCHOR]
```

**Target Length**: ~150 characters/words. A 65% reduction compared to the legacy approach.

### Placement of ABSOLUTE ANCHOR

Must **always be placed at the very beginning of the prompt**.

Claude focuses its highest attention on the beginning of a prompt.
Placing it at the front equips Claude with evaluation criteria before it even begins reading the task instructions.

```
[ABSOLUTE ANCHOR]
... (criteria)
[/ABSOLUTE ANCHOR]

[Task Instructions]
... (actual work content)
```

---

## 3. 7 Criteria for Prompt Redesign

### Criterion 1. ABSOLUTE ANCHOR at the Top, Always

Every prompt starts with ABSOLUTE ANCHOR.
However, depending on project characteristics, the contents of ①②③ can be tuned.
The format and position are fixed.

### Criterion 2. Eliminate Repetitive Declarations and Organize by Hierarchy

Current: Identical criteria repeated in narrative form across every prompt.
Improvement: Unified into a single ABSOLUTE ANCHOR block with an internal hierarchical structure.

**Hierarchical Principles**
When a conflict occurs, higher-tier criteria take absolute precedence.
Once Claude understands the hierarchy, it can make autonomous judgments in ambiguous situations.

```
[ABSOLUTE ANCHOR]
Tier 1 (Absolute Invariant): Deliverable Quality
Tier 2 (Structural Invariant): SOT + RLM Pattern
Tier 3 (Process): Approval Prior to Implementation
→ Halt and report if lower-tier execution conflicts with a higher-tier criterion.
[/ABSOLUTE ANCHOR]
```

### Criterion 3. Structure Reflection to Ascend Through Layers

Current: Repetition of reflection at the same layer (12~13 reflections per session).
Improvement: Separated into 3 ascending layers where each layer serves as input to the next.

```
[Layer 1 — Fact Check]
Does the implementation match the design intent?
Evaluate only True/False. Do not provide explanations.
Output: Discrepancy list only.

[Layer 2 — Structure Analysis]
Using the Layer 1 discrepancies:
Set 2 feature addition scenarios for 6 months from now →
Analyze which part of the current structure collapses first.
Output: Vulnerability points and reasons.

[Layer 3 — Philosophy Alignment]
Using the Layer 2 vulnerabilities:
Does this actually compromise the Tier 1 criterion (Quality)?
Judge based on concrete evidence, not subjective feelings.
Output: Fix Required / Fix Not Required / Cannot Determine + Rationale.
```

**Effect**: Consolidates 5 legacy reflection prompts into 3, structuring each reflection so that it builds upon the concrete output of the previous reflection.

### Criterion 4. Specialize Attack Axes for Adversarial Agents

Current: Monolithic instruction: "Attack with critical thinking."
Improvement: Assign specialized attack axes to distinct agents.

```
[Adversarial Agent A — Operational Failure Specialist]
Attack weapons: Concurrency conflicts / Unresponsive agents / SOT data inconsistency /
                Network disconnection / Out of memory / Recursive infinite loops
Target flaws: "Parts that work normally but are unrecoverable upon failure"

[Adversarial Agent B — Simplicity Fundamentalist]
Attack weapons: Simpler alternatives / Over-engineered points /
                Components that yield identical quality when removed
Target flaws: "Complexity for the sake of complexity"

[Adversarial Agent C — 6-Month Maintainer]
Attack weapons: Incomprehensible structures / Undocumented assumptions /
                Areas where modification ripples unpredictably
Target flaws: "Traps that work now but create future liabilities"

[Defense Rules]
Honestly concede undefendable points.
An undefendable point = a core item that must be refactored.
Stubborn arguing without acknowledgment is prohibited.
```

### Criterion 5. Add a Reverse Layer to the Reading Protocol

Current: 3-pass reading.
Improvement: 4-pass reading — adds a 4th pass "reverse reading" to identify what is missing.

```
Pass 1: Essence focus (What/Why). Identify purpose, philosophy, and direction only.
Pass 2: Relational expansion. Identify system requirements, stages, and capabilities.
Pass 3: Midsection precision reinforcement.
Pass 4: [Reverse] What does this document NOT cover?
        Identify and list items necessary for achieving user goals that are absent from this document.
        This is not a check to confirm what exists, but an audit to discover what is missing.
```

### Criterion 6. Structure Approval Gates as Reporting Formats

Current: "Caution: Final implementation must begin only after my approval" — repeated across 19 prompts.
Improvement: Explicitly define reporting format within ABSOLUTE ANCHOR. Remove "caution" sentences from individual prompts.

```
Mandatory Approval Request Format (Writing even one line of code without this format is prohibited):
- [Implementation Intent] 1 sentence: What does this task do?
- [Affected Files] List of files to modify and reasons for each change
- [Risk Points] Areas with large blast radius upon failure
- [Assumptions] Ambiguities decided by the agent
- [Preservation Check] SOT/RLM maintenance status: Yes/No + Evidence
```

### Criterion 7. Standardize Session-Start Prompts into Header Format

Current: Narrating background anew in each session → First prompt reaches 1,000~2,500 characters.
Improvement: Standardize into SESSION HEADER format → Under 100 words.

```
[SESSION HEADER]
Previous Step: (Explicitly specify completed deliverables)
Current Step: (One-line goal for this session)
Key Reference Files: (List of paths)
[/SESSION HEADER]
```

Because ABSOLUTE ANCHOR encapsulates all operational criteria,
the session header only needs to state "where we currently are in the pipeline".

---

## 4. Prompt Redesign Before & After Comparison

### Pre-Improvement Structure (Based on actual 062.txt)

```
[Task Instructions — Reflection Request]
Let us conduct a Critical Reflection on Infrastructure Build.
Reflect from the perspective of a 30-year veteran Senior Software Engineer.

[Core Code Implementation Principles — 3 Detailed Descriptions]
1. Understand the intent of user instructions
   ...
2. Ripple effect analysis
   ...
3. Change design
   ...

[Communication Style with User]
...

[Repetitive Declaration of Absolute Criteria]
Completely ignore speed and token cost when this workflow operates.
Quality and top-tier qualitative deliverables are the absolute criteria.
SOT is mandatory. The RLM pattern must be strictly maintained.
The philosophy, purpose, and core of the existing workflow must be preserved intact.

[Approval Request]
Caution: Final implementation must begin only after my approval.

→ Approx. 1,300 characters
```

### Post-Improvement Structure

```
[ABSOLUTE ANCHOR]
① Quality Absolute Priority — Speed, cost, and convenience can never be justifications.
   In trade-off situations, everything other than quality is expendable.
② SOT + RLM Invariant — No improvement may compromise these two structures.
   If any possibility of compromise arises, you must notify me before implementation.
③ Implementation After Approval — Writing even a single line of code without my approval is strictly prohibited.
   Upon approval request: report implementation intent (1 sentence) + affected files + risk points only.
[/ABSOLUTE ANCHOR]

[Role]
30-year veteran Software Architect for large-scale codebases.
Evaluation criterion: Maintainability 10 years out; minimal blast radius of changes.

[Reflection Target]
Infrastructure Build — Reflect using the 3 principles below:
1. Understand user instruction intent: Can it be explained in 1-2 sentences?
2. Ripple effect analysis: Direct dependencies / call relationships / structural relationships / test code
3. Change design: Propose step-by-step plan per file

[Output Style]
Focus on code and concrete steps without theoretical lectures.
Even if ambiguous, declare assumptions explicitly and propose the optimal implementation.

→ Approx. 350 words (73% reduction)
```

---

## 5. Verification Criteria for Cognitive Imprint

Standards to verify whether redesigned prompts have successfully imprinted onto Claude:

**Verification Point 1 — Spontaneous Mention of SOT/RLM**
Claude independently detects potential SOT/RLM conflicts and flags them proactively.
If observed, the imprint succeeded. If not, reinforce explanation in ②.

**Verification Point 2 — Absence of Quality Compromises**
If statements such as "While this alternative is faster..." appear, the imprint of ① failed.

**Verification Point 3 — Autonomous Operation of Approval Gates**
If Claude naturally outputs "Requesting approval prior to implementation + structured report" without prompting, the imprint of ③ succeeded.

---

## 6. Instructions for Claude Code

Claude Code reading this document must redesign existing prompt blocks according to the criteria below:

### Operating Principles

1. **Identify the purpose of each prompt first.**
   Is it reflection? Direct execution? Brainstorming? Integration and synthesis?
   Different purposes shift the emphasis of ①②③ in ABSOLUTE ANCHOR.

2. **Replace repetitive prose of absolute criteria with ABSOLUTE ANCHOR.**
   Keyword + Reason + Conflict Judgment: all three elements must be present.
   Remove all other repetitive declarations.

3. **Explicitly specify layers for reflection prompts.**
   Layer 1 (Fact Check) → Layer 2 (Structure Analysis) → Layer 3 (Philosophy Alignment).
   If identical layers occur consecutively, evaluate whether they can be consolidated.

4. **Specialize attack axes for adversarial agent prompts.**
   Replace generic "attack critically" instructions with differentiated Agent A/B/C roles.

5. **Add Pass 4 reverse reading to prompts containing reading protocols.**

6. **Standardize session-start prompts into SESSION HEADER format.**

7. **Remove all occurrences of "Caution: Final implementation requires my approval".**
   This is already handled globally by ABSOLUTE ANCHOR ③.

8. **Verify whether the purpose of each redesigned prompt can be stated in a single sentence.**
   If it cannot be explained concisely, the prompt is not yet cleanly structured.

### Redesign Prohibitions

- Altering the core objective of a prompt.
- Truncating actual user task intent such that critical instructions are lost.
- Placing ABSOLUTE ANCHOR after task instructions.
- Leaving vague expressions like "seems good" or "looks fine".

---

## 7. Summary

| Aspect | Current | Improvement |
|---|---|---|
| Absolute Criteria Declaration | Descriptive repetition in every prompt (~450 chars) | Compact ABSOLUTE ANCHOR block (~150 words) |
| Position of Criteria | Caution at middle/bottom of prompt | Top of prompt, always |
| Reflection Structure | Monolithic repetition at the same layer | 3 distinct ascending layers |
| Adversarial Agents | Single monolithic attack instruction | Specialized A/B/C attack axes |
| Reading Protocol | 3 passes | 4 passes (includes reverse audit) |
| Approval Gate | "Caution" statement repeated 19 times | Standardized in ABSOLUTE ANCHOR ③ |
| Session-Start Prompts | Lengthy narrative context (1,000~2,500 chars) | Standardized SESSION HEADER (<100 words) |
| Imprint Reliability | Stochastic (key points buried in prose) | Structural (fixed format + fixed position) |
