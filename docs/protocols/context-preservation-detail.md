# Context Preservation System — Detailed Specification

> Internal mechanics and architectural details of the Context Preservation System.
> Consult when modifying, debugging, or extending Hook infrastructure.

## Operational Workflow for AI Agents

- When `[CONTEXT RECOVERY]` appears at session start, **you must read the indicated snapshot file** using the Read tool to restore prior working context.
- The latest snapshot is persisted at `.claude/context-snapshots/latest.md`.
- **Knowledge Archive**: `knowledge-index.jsonl` is a structured index accumulating across sessions. Both the Stop hook and SessionEnd/PreCompact write to it. Each entry captures `completion_summary` (tool success/failure), `git_summary` (repo diffs), `session_duration_entries`, `phase`, `phase_flow` (multi-stage transition flows, e.g., `research → implementation`), `primary_language` (dominant extension), `error_patterns` (Error Taxonomy 12 patterns + resolution matching), `success_patterns` (Edit/Write→Bash success sequences), `tool_sequence` (RLE compressed tool sequence), `final_status` (success/incomplete/error/unknown), and path-based search `tags`. Grep tool provides programmatic exploration (RLM pattern).
- **Resume Protocol**: The "Recovery Instructions" section in snapshots deterministically provides modified/referenced file paths and session details. `[CONTEXT RECOVERY]` displays tool success/failure counts and git status. **Dynamic RLM Query Hints**: Generates tailored Grep query patterns based on extracted file path tags (`extract_path_tags()`) and recorded error signatures.
- Hook scripts access the SOT (`state.yaml`) strictly in **read-only** mode (Absolute Criterion 2 compliant). SOT file paths are centrally managed via the `sot_paths()` helper, derived from `SOT_FILENAMES` (`state.yaml`, `state.yml`, `state.json`).

## Centralized Truncation Constants

10 truncation constants are centrally defined in `_context_lib.py`:
- `EDIT_PREVIEW_CHARS = 1000` — Preserves edit intent and surrounding context (5 lines x 1000 chars).
- `ERROR_RESULT_CHARS = 3000` — Preserves full stack traces.
- `MIN_OUTPUT_SIZE = 100` — Minimum deliverable file size.

## Multi-Stage Phase Transition Detection

The `detect_phase_transitions()` function uses a sliding window (20 tools, 50% overlap) to deterministically detect in-session workflow stage transitions (e.g. `research → planning → implementation`). Recorded in the Knowledge Archive `phase_flow` field.

## Decision Quality Tag Ordering

The "Key Design Decisions" section in snapshots (IMMORTAL priority) orders items by quality tags: `[explicit]` > `[decision]` > `[rationale]` > `[intent]`, filling 15 available slots so routine intent statements do not crowd out architectural decisions.

## IMMORTAL-Aware Compression

When a snapshot exceeds the context budget, Phase 7 hard truncation prioritizes IMMORTAL sections. Non-IMMORTAL sections are trimmed first, and even in extreme cases the head of IMMORTAL text is preserved.

**Compression Audit Trail**: Recorded at the end of snapshots as HTML comments (`<!-- compression-audit: ... -->`) documenting characters trimmed across Phases 1-7 and final size.

## Error Taxonomy

Categorizes tool execution failures across 12 distinct patterns:
`file_not_found`, `permission`, `syntax`, `timeout`, `dependency`, `edit_mismatch`, `type_error`, `value_error`, `connection`, `memory`, `git_error`, `command_not_found`.

Recorded in the Knowledge Archive `error_patterns` field, reducing "unknown" classifications to ~30%. Employs negative lookaheads and qualifying constraints to eliminate false positives.

**Error→Resolution Matching**: File-aware matching correlates tool errors with successful tool invocations within 5 subsequent entries, recording resolutions in the `resolution` field. Enables cross-session queries via `Grep "resolution" knowledge-index.jsonl`.

## Quality Gate State IMMORTAL Preservation

`_extract_quality_gate_state()` extracts the most recent quality gate evaluations from `pacs-logs/`, `review-logs/`, and `verification-logs/`, embedding them into snapshots under an IMMORTAL priority section.

## Phase Transition Snapshot Header

For sessions where multi-stage transitions are detected, the snapshot header indicates the flow (e.g. `Phase flow: research(12) → implementation(25)`).

## Error→Resolution Auto-Surfacing

`_extract_recent_error_resolutions()` in `restore_context.py` surfaces up to 3 recent error-resolution patterns from the Knowledge Archive directly in SessionStart output.

## Automated Runtime Directory Provisioning

`_check_runtime_dirs()` in `setup_init.py` automatically provisions 6 runtime directories when an SOT file exists: `verification-logs/`, `pacs-logs/`, `review-logs/`, `autopilot-logs/`, `translations/`, and `diagnosis-logs/`.

## System Command Filtering

Filters out system commands such as `/clear` and `/help` from the "Current Task" snapshot section, retaining only genuine user intent.

## Autopilot Runtime Enforcement

When Autopilot is enabled, SessionStart injects execution rules into context, the snapshot records Autopilot state (IMMORTAL priority), and the Stop hook detects and backfills missing Decision Logs.

## ULW Mode Detection & Inheritance

`detect_ulw_mode()` detects the `ulw` keyword in transcripts using word-boundary regexes. **Implicit Deactivation**: New sessions (`source=startup`) do not inherit ULW rules even if previous snapshots recorded ULW — only `clear`, `compact`, and `resume` sources inherit ULW.

## Predictive Debugging

`aggregate_risk_scores()` aggregates `error_patterns` by file with recency decay to generate risk scores. Executed once at SessionStart to populate `risk-scores.json`. `predictive_debug_guard.py` checks this cache before each Edit/Write, issuing warnings when thresholds are exceeded.

**Basename Merge**: Merges bare filenames and relative paths sharing the same basename, preventing risk score dilution.

---

## Hook Configuration Map

All hooks are unified in `.claude/settings.json`. Cloning the repository applies the hook infrastructure automatically.

- **Stop** → `context_guard.py --mode=stop` → `generate_context_summary.py`
- **PostToolUse** → `context_guard.py --mode=post-tool` → `update_work_log.py` (matcher: `Edit|Write|Bash|Task|NotebookEdit|TeamCreate|SendMessage|TaskCreate|TaskUpdate`)
- **PreCompact** → `context_guard.py --mode=pre-compact` → `save_context.py --trigger precompact`
- **SessionStart** → `context_guard.py --mode=restore` → `restore_context.py` (matcher: `clear|compact|resume`)
- **PreToolUse** → `block_destructive_commands.py` (matcher: `Bash`, standalone execution — preserves exit code 2)
- **PreToolUse** → `block_test_file_edit.py` (matcher: `Edit|Write`, standalone execution — `.tdd-guard` toggle)
- **PreToolUse** → `predictive_debug_guard.py` (matcher: `Edit|Write`, standalone execution — warning only)
- **PostToolUse** → `output_secret_filter.py` (matcher: `Bash|Read`, standalone execution — secret detection, exit 0 warning)
- **PostToolUse** → `security_sensitive_file_guard.py` (matcher: `Edit|Write`, standalone execution — warning, exit 0)
- **SessionEnd** → `save_context.py --trigger sessionend` (matcher: `clear`)
- **Setup (init)** → `setup_init.py` — Infrastructure health check (`claude --init`)
- **Setup (maintenance)** → `setup_maintenance.py` — Periodic health check (`claude --maintenance`)

### Hook Architectural Rationale

> **`if test -f; then; fi` Pattern**: All hook commands use the `if test -f; then; fi` pattern, replacing the legacy `|| true` idiom that previously swallowed exit code 2 blocking signals.
> **Independent PreToolUse Safety Hooks**: `block_destructive_commands.py` and `block_test_file_edit.py` execute independently of `context_guard.py` to ensure exit code 2 signals are cleanly delivered to Claude.
> **Independent PostToolUse Security Hooks (ADR-050)**: `output_secret_filter.py` and `security_sensitive_file_guard.py` operate on their own streams and data sources independently of `context_guard.py`.

### D-7 Intentional Duplication Registry

| # | Instance | Location A | Location B |
|---|---|---|---|
| 1 | `REQUIRED_SCRIPTS` (20 scripts) | `setup_init.py` | `setup_maintenance.py` |
| 2 | `RISK_THRESHOLD` / `MIN_SESSIONS` | `predictive_debug_guard.py` | `_context_lib.py` |
| 3 | `ERROR_TAXONOMY` Types (12 types) | `_classify_error_patterns()` | `_RISK_WEIGHTS` (13 weights) |
| 4 | ULW Detection Regex | `_gather_retry_history()` | `validate_retry_budget.py` + `restore_context.py` |
| 5 | Retry Limit Constants | `validate_retry_budget.py` | `_context_lib.py` + `restore_context.py` |
| 6 | `SOT_FILENAMES` Tuple | `_context_lib.py` | `setup_init.py` + `query_workflow.py` |

**Automated Synchronization Check**: `_check_doc_code_sync()` in `setup_maintenance.py` deterministically verifies synchronization across DC-1 through DC-5.
