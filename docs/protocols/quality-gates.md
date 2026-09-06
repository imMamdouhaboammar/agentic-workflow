# Quality Gates & P1 Validation

> This document provides the detailed specification for the 4-layer quality assurance architecture and P1 hallucination containment.
> Consult when designing, debugging, or extending quality gates.

## 4-Layer Quality Assurance Architecture (L0 → L1 → L1.5 → L2)

The Orchestrator increments `current_step` strictly sequentially. Each step completion must pass up to 4 verification layers before proceeding:

1. **L0 Anti-Skip Guard** (Deterministic) — Deliverable file existence + minimum size (100 bytes). Executed by `validate_step_output()` at the hook layer.
2. **L1 Verification Gate** (Semantic) — Agent self-verification ensuring the deliverable achieves 100% of the declared `Verification` criteria. On failure, rerun only the failing section (up to 10 retries). Recorded in `verification-logs/step-N-verify.md`.
3. **L1.5 pACS Self-Rating** (Confidence) — Evaluates Faithfulness / Completeness / Logic (F/C/L) after executing the Pre-mortem Protocol. Recorded in `pacs-logs/step-N-pacs.md`. RED (< 50) mandates rework.
4. **[L2 Adversarial Review / Calibration]** (Optional / Enhanced) — Independent review by `@reviewer` and `@fact-checker` cross-checking deliverables, claims, and pACS scores for high-risk steps.

> Steps without a declared `Verification` field proceed with Anti-Skip Guard only (backward compatibility). Details: `AGENTS.md §5.3`, `§5.4`.

---

## P1 Hallucination Containment

Repetitive tasks requiring 100% accuracy are deterministically enforced via Python code.

### (1) Knowledge Index (KI) Schema Validation
`_validate_session_facts()` guarantees that required RLM keys (session_id, tags, final_status, diagnosis_patterns, etc., 11 items total) exist before writing to `knowledge-index.jsonl` — filling safe defaults if omitted.

### (2) Partial Failure Isolation
In `archive_and_index_session()`, failure to write an archive snapshot never blocks updating `knowledge-index.jsonl`, safeguarding core RLM assets.

### (3) SOT Write Pattern Validation
`_check_sot_write_safety()` in `setup_init.py` scans hook scripts using AST boundary analysis to detect accidental writes to SOT files (Tier 1: blocks non-SOT scripts from referencing SOT paths; Tier 2: verifies function-level write safety in SOT-aware scripts).

### (4) SOT Schema Validation
`validate_sot_schema()` validates structural integrity of workflow `state.yaml` across 8 items:
- **S1-S6**: `current_step` type & range, `outputs` dict & key format, future step deliverable detection, valid `workflow_status` values, `auto_approved_steps` consistency.
- **S7**: 5 fields for pACS validation (S7a: dimensions F/C/L 0-100, S7b: `current_step_score` 0-100, S7c: `weak_dimension`, S7d: `history` dictionary, S7e: `pre_mortem_flag` string).
- **S8**: 5 fields for `active_team` validation (S8a: `name` string, S8b: `status` partial|all_completed, S8c: `tasks_completed` list, S8d: `tasks_pending` list, S8e: `completed_summaries` dict).

Runs during both SessionStart and Stop hooks.

### (5) Adversarial Review P1 Validation
`validate_review_output()` validates structural integrity of review reports:
- R1: File existence
- R2: Minimum size
- R3: 4 mandatory sections
- R4: Explicit PASS / FAIL verdict extraction
- R5: Issue table has >= 1 row

`parse_review_verdict()` — regex extraction of issue severity counts.
`calculate_pacs_delta()` — Generator vs Reviewer pACS difference (Delta >= 15 triggers recalibration).
`validate_review_sequence()` — Enforces Review PASS preceding Translation via file timestamps.
Standalone script: `validate_review.py`.

### (6) Terminology & Translation P1 Validation
`validate_translation_output()` validates translation deliverables across 7 criteria:
- T1: File existence, T2: Minimum size, T3: English source existence, T4: Deliverable file naming, T5: Non-empty, T6: Heading count matching (+-20%), T7: Code block count equality.

`check_glossary_freshness()` — Validates glossary timestamp freshness (T8).
`verify_pacs_arithmetic()` — Generic min() arithmetic validation across all pACS logs (T9).
`validate_verification_log()` — Verification log integrity (V1a-V1c).
Standalone script: `validate_translation.py`.

### (7) pACS P1 Validation
`validate_pacs_output()` validates pACS logs across 6 items:
- PA1: File existence, PA2: Minimum size (50 bytes), PA3: Dimension scores >= 3 (range 0-100), PA4: Pre-mortem section present, PA5: min() arithmetic accuracy, PA7: RED zone blockage (pACS < 50 triggers FAIL).
- PA6 (Optional): Score-to-color-zone alignment.

Standalone script: `validate_pacs.py`.

### (8) L0 Anti-Skip Guard Code Implementation
`validate_step_output()` — 3 deterministic L0 criteria:
- L0a: SOT `outputs.step-N` file path exists on disk.
- L0b: File size >= `MIN_OUTPUT_SIZE` (100 bytes).
- L0c: Non-whitespace content confirmed.

Run pACS + L0 concurrently via `validate_pacs.py --check-l0`.

### (9) Predictive Debugging P1 Validation
`validate_risk_scores()` — Validates `risk-scores.json` across 6 items:
- RS1: Mandatory keys, RS2: `data_sessions` integer, RS3: `risk_score` range, RS4: `error_count` arithmetic integrity, RS5: `resolution_rate` range, RS6: `top_risk_files` sorted and existent.

### (10) Retry Budget P1 Validation
`validate_retry_budget.py` — Deterministic retry budget evaluation:
- RB1: Reads counter file, RB2: Detects active ULW mode, RB3: Budget comparison (`retries_used < max_retries`).
- `max_retries`: 3 when ULW is active, 2 when inactive.
- Atomic counter increment with `--increment` flag.

### (11) Abductive Diagnosis P1 Validation
`validate_diagnosis_log()` — Validates diagnosis logs across 10 items:
- AD1: File existence, AD2: Minimum size 100 bytes, AD3: Quality gate field match, AD4: Selected hypothesis present, AD5: Evidence count >= 1, AD6: Action plan present, AD7: No forward references, AD8: Hypotheses count >= 2, AD9: Selected hypothesis consistency, AD10: Prior diagnosis reference on retry > 0.

`diagnose_failure_context()` — Pre-evidence collection (retry history, upstream evidence, hypothesis priority, fast-path, raw evidence). Deterministic fast-path shortcuts (FP1-FP3).
Standalone scripts: `diagnose_context.py` (pre-analysis) and `validate_diagnosis.py` (post-validation).

### (12) Cross-Step Traceability P1 Validation
`validate_cross_step_traceability()` — 5 items:
- CT1: Trace markers present, CT2: Referenced step deliverables exist, CT3: Section ID resolution (warning), CT4: Minimum density >= 3, CT5: No forward references.

Standalone script: `validate_traceability.py`.

### (13) Domain Knowledge Structure (DKS) P1 Validation
`validate_domain_knowledge()` — 7 items:
- DK1: File existence + valid YAML, DK2: Mandatory metadata keys, DK3: Entities structure, DK4: Referential relation integrity, DK5: Constraints structure, DK6: Deliverable DKS reference resolution, DK7: Constraint non-violation.

Standalone script: `validate_domain_knowledge.py`.

### (14) Workflow.md DNA Inheritance P1 Validation
`validate_workflow_md()` — 8 items:
- W1: File existence, W2: Minimum size 500 bytes, W3: `## Inherited DNA` header, W4: Inherited Patterns table >= 3 rows, W5: Constitutional Principles section, W6: CAP reference, W7: Cross-Step Traceability alignment, W8: DKS validation alignment.

Standalone script: `validate_workflow.py`. Invoked after `workflow-generator` completes.
