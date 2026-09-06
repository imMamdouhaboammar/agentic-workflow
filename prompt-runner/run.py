#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  run.py — Claude Code Sequential Prompt Auto-Runner (Final Version)

  Method: pipe mode (-p) + session ID capture (--resume)

  Operating Principles:
    1. First prompt of a session: claude -p --output-format stream-json --verbose < prompt.txt
       → Extract and save session_id from JSON response
    2. Subsequent prompts in the same session: claude -p --resume $session_id < prompt.txt
       → Exactly resumes that session
    3. When encountering /clear: discard session_id
       → Next prompt starts a new session and captures a new session_id
    4. Process termination = task completion (100% deterministic)

  Usage:
    python3 run.py                    # Full execution (from #1)
    python3 run.py --resume           # Resume from breakpoint
    python3 run.py --from 34          # Start from #34 (new session)
    python3 run.py --dry-run          # Preview execution order without running
    python3 run.py --verify           # Verify prompt file integrity

  Environment variables:
    MAX_TURNS=0           Max agent turns (0 = unlimited)
    TIMEOUT=0             Max execution time per prompt (0 = unlimited)
    SKIP_PERMISSIONS=1    Skip permission checks

  ════════════════════════════════════════════════════════════════
  🔄 Rate-Limit Automatic Retry Policy (Operations Guide)

  Situation: API rate limit occurs → automatically wait and retry

  Settings:
    · Up to 60 retries (5-minute intervals)
    · Max total wait time: 300 minutes (5 hours)
    · Detection keywords: "rate limit", "quota exceeded", "429", etc.

  User Experience:
    Rate-limit detected during Step 35 execution
      → Automatic retry after 5-minute wait
      → Repeated up to 60 times
      → Exits with code 0 (normal exit) if exceeded

  --resume Recovery (Automatic Wait):
    python3 run.py --resume
      → Detects rate_limit_state in state.json
      → Automatically sleeps for remaining wait time
      → Resumes at recovery time

  Monitoring:
    logs/{step}.rate-limit.log  — Wait history
    rate_limit_state in state.json — Last state (step, attempt_count, next_retry_at)

  Operations Team Response (if needed):
    1. Check status: inspect rate_limit_state in state.json
    2. Manual recovery: python3 run.py --resume
       (Run after waiting the required delay)
    3. Force proceed: set rate_limit_state to null in state.json and resume
       (Not recommended — may hit rate-limit error again)
  ════════════════════════════════════════════════════════════════
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone

from state_manager import StateManager, StateCorruptError


# ═══════════════════════════════════════════════════════════════
# Constants Definition — Immutable
# ═══════════════════════════════════════════════════════════════

TOTAL_PROMPTS = 110

# /clear positions: session ends at this step, new session starts at next step
CLEAR_POSITIONS = frozenset({3, 6, 9, 12, 14, 17, 20, 23, 26, 29, 33, 36, 39, 42, 47, 50, 53, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85, 88, 91, 95, 98, 101, 104, 107, 110})

# Step immediately following each /clear = new session start point
# Includes #1 (initial start)
NEW_SESSION_STARTS = frozenset({1, 4, 7, 10, 13, 15, 18, 21, 24, 27, 30, 34, 37, 40, 43, 48, 51, 54, 59, 62, 65, 68, 71, 74, 77, 80, 83, 86, 89, 92, 96, 99, 102, 105, 108})

# ═══════════════════════════════════════════════════════════════
# P2 Phase 2: Rate-Limit Policy Classes (P1-P5 Substitutions)
# ═══════════════════════════════════════════════════════════════

# P1: Custom RateLimitError
class RateLimitError(Exception):
    """Rate-limit exceeded or unrecoverable state"""
    pass


# P3: RateLimitPolicy — Encapsulate all constants into a class
class RateLimitPolicy:
    """Rate-limit policy configuration (DRY principle)"""
    MAX_NORMAL_RETRIES = 3          # Normal error: 3 retries
    MAX_RATE_LIMIT_RETRIES = 60     # Rate-limit: 60 retries (5 hours)
    RATE_LIMIT_WAIT = 300           # 5-minute wait

    # Normal retry wait times (exponential backoff)
    NORMAL_RETRY_WAITS = [15, 30, 60]  # 15s, 30s, 60s


# P4: Expose policy as module-level constants (backward compatibility)
MAX_RATE_LIMIT_RETRIES = RateLimitPolicy.MAX_RATE_LIMIT_RETRIES
RATE_LIMIT_WAIT = RateLimitPolicy.RATE_LIMIT_WAIT


# ═══════════════════════════════════════════════════════════════
# Automatic Selection of Highest-Performance Model
# ═══════════════════════════════════════════════════════════════

# Model priority: higher number = newer and higher performance
# Adding to this list upon new model release will enable auto-selection
_MODEL_PRIORITY: list[tuple[int, str]] = [
    (1100, "claude-opus-4-7"),          # Highest priority: opus 4.7 (default)
    (1000, "claude-opus-4-6"),          # opus 4.6
    (990,  "claude-opus-4-5"),          # opus 4.5
    (980,  "claude-opus-4-0"),          # opus 4.0
    (970,  "claude-opus-4"),            # opus 4 (alias)
    (500,  "claude-sonnet-4-6"),        # sonnet 4.6 (fallback)
    (490,  "claude-sonnet-4-5"),        # sonnet 4.5 (fallback)
]

# Extended thinking (max effort) token budget — fixed to maximum value
THINKING_BUDGET_TOKENS = 16000   # Max extended thinking for Claude Opus


# ═══════════════════════════════════════════════════════════════
# Rate-Limit Handling (P2 Complete: RateLimitHandler + RateLimitPolicy)
# ═══════════════════════════════════════════════════════════════

class RateLimitHandler:
    """Rate-limit detection, retry, and state management class (P2)"""

    # Rate-limit dedicated keywords (false positives eliminated)
    KEYWORDS = [
        "rate limit",
        "rate_limit",
        "hit your limit",
        "hitting the rate limit",
        "you have exceeded",
        "quota exceeded",
        "too many requests",  # HTTP 429
    ]

    MAX_RETRIES = RateLimitPolicy.MAX_RATE_LIMIT_RETRIES  # P3: Reference policy class
    WAIT_SECONDS = RateLimitPolicy.RATE_LIMIT_WAIT        # P3: Reference policy class

    @staticmethod
    def detect(err_file: Path, stdout_file: Path, stream_file: Path) -> bool:
        """Detect rate-limit (inspect 3 files)"""
        for check_file in [err_file, stdout_file, stream_file]:
            if check_file.exists():
                content = check_file.read_text(encoding='utf-8').lower()
                if any(kw in content for kw in RateLimitHandler.KEYWORDS):
                    return True
        return False

    @staticmethod
    def record_state(state: dict, step: int, attempt_count: int):
        """Record rate-limit state in state dict (saved in main)"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        next_retry_at = (now + timedelta(seconds=RateLimitHandler.WAIT_SECONDS)).isoformat()

        state["rate_limit_state"] = {
            "step": step,
            "attempt_count": attempt_count,
            "max_attempts": RateLimitHandler.MAX_RETRIES,
            "last_wait_time": now.isoformat(),
            "next_retry_at": next_retry_at,
        }


def _resolve_best_model() -> str:
    """
    Queries available models from Anthropic API and
    returns the highest priority model based on _MODEL_PRIORITY.

    Falls back to top model in _MODEL_PRIORITY if API query fails.
    """
    import urllib.request
    import urllib.error

    fallback = _MODEL_PRIORITY[0][1]  # Top of list

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.warning("ANTHROPIC_API_KEY not set — cannot query models automatically, fallback: " + fallback)
        return fallback

    try:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        available = {m["id"] for m in data.get("data", [])}
    except Exception as e:
        log.warning(f"Failed to query model list ({e}) — fallback: {fallback}")
        return fallback

    # Return first available model in priority order
    for _, model_id in sorted(_MODEL_PRIORITY, key=lambda x: x[0], reverse=True):
        if model_id in available:
            return model_id

    log.warning(f"No available model found in priority list — fallback: {fallback}")
    return fallback


# Query once at process startup (same model used across all 110 steps)
_BEST_MODEL: str | None = None


def get_best_model() -> str:
    """Returns the cached highest-performance model ID."""
    global _BEST_MODEL
    if _BEST_MODEL is None:
        _BEST_MODEL = _resolve_best_model()
        log.info(f"✦ Selected model: {_BEST_MODEL} (thinking: {THINKING_BUDGET_TOKENS:,} tokens)")
    return _BEST_MODEL

# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent.resolve()
PROMPTS_DIR = SCRIPT_DIR / "prompts"
LOGS_DIR = SCRIPT_DIR / "logs"
STATE_FILE = SCRIPT_DIR / "state.json"

# StateManager (Flaw #2, #3 — Atomic Write + Corrupt Recovery + audit_log integration)
state_manager = StateManager(STATE_FILE)


# ═══════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('runner')

# Also add file logging
file_handler = logging.FileHandler(SCRIPT_DIR / "execution.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s │ %(levelname)s │ %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
log.addHandler(file_handler)


# ═══════════════════════════════════════════════════════════════
# State Management (state.json)
# ═══════════════════════════════════════════════════════════════

def state_init() -> dict:
    """Initialize new state"""
    s = {
        "total": TOTAL_PROMPTS,
        "current_step": 1,
        "current_session_id": None,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed": [],
        "clears": [],
        "failed": [],
        "sessions": {},  # {session_id: [step1, step2, ...]}
        "rate_limit_state": None,  # (Fix #4) Record rate-limit state
    }
    _state_save(s)
    return s


def state_load() -> dict:
    """Load existing state with automatic corruption recovery

    Uses StateManager which:
    1. Tries primary state.json
    2. Auto-recovers from backups if corrupt
    3. Restores backup to primary if needed

    Returns:
        State dict

    Raises:
        StateCorruptError: If all backups are corrupt
        SystemExit: Exits with code 1 if unrecoverable
    """
    try:
        return state_manager.load()
    except StateCorruptError as e:
        log.error(f"[STATE] CORRUPTION UNRECOVERABLE: {e}")
        sys.exit(1)


def _state_save(s: dict):
    """Save state with atomic write + backup rotation

    Uses StateManager which:
    1. Rotates backups (backup.1 → backup.2 → backup.3)
    2. Writes to temporary file
    3. Validates schema (Pydantic)
    4. Atomically renames (tmp → primary)

    Args:
        s: State dict to save

    Raises:
        SystemExit: Exits with code 1 if save fails
    """
    try:
        state_manager.save(s)
    except Exception as e:
        log.error(f"[STATE] SAVE FAILED: {e}")
        sys.exit(1)


def state_record_complete(s: dict, step: int):
    s["completed"].append(step)
    s["current_step"] = step + 1
    # Session recording
    sid = s.get("current_session_id")
    if sid:
        s["sessions"].setdefault(sid, []).append(step)

    # P1: Audit logging (merged into state.json)
    state_manager.record_audit(s, step, "run_prompt", {
        "status": "completed",
        "session_id": sid
    })

    _state_save(s)


def state_record_clear(s: dict, step: int):
    old_session_id = s.get("current_session_id")
    s["clears"].append(step)
    s["current_session_id"] = None  # Clear session ID
    s["current_step"] = step + 1

    # P1: Audit logging
    state_manager.record_audit(s, step, "clear", {
        "cleared_session": old_session_id
    })

    _state_save(s)


def state_update_session_id(s: dict, session_id: str):
    step = s.get("current_step", 0)
    s["current_session_id"] = session_id

    # P1: Audit logging
    state_manager.record_audit(s, step, "session_change", {
        "new_session_id": session_id
    })

    _state_save(s)


def state_record_fail(s: dict, step: int):
    s["failed"].append(step)

    # P1: Audit logging
    state_manager.record_audit(s, step, "run_prompt", {
        "status": "failed"
    })

    _state_save(s)


def state_record_rate_limit_exceeded(s: dict, step: int, attempt_count: int, max_attempts: int):
    """Record rate-limit exceeded state in state dict (saved in main)"""
    from datetime import timezone

    now = datetime.now(timezone.utc)
    next_retry_at = (now + timedelta(seconds=RATE_LIMIT_WAIT)).isoformat()

    s["rate_limit_state"] = {
        "step": step,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "last_wait_time": now.isoformat(),
        "next_retry_at": next_retry_at,
    }

    # P1: Audit logging
    state_manager.record_audit(s, step, "rate_limit", {
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "next_retry_at": next_retry_at
    })


def state_finish(s: dict):
    step = s.get("current_step", 0)
    s["status"] = "done"
    s["finished_at"] = datetime.now().isoformat()

    # P1: Audit logging
    state_manager.record_audit(s, step, "run_prompt", {
        "status": "workflow_completed"
    })

    _state_save(s)



# ═══════════════════════════════════════════════════════════════
# 3-Layer Verification System
# ═══════════════════════════════════════════════════════════════

# ─── Layer 1: Silent Failure Keywords ───
# Note: Rate limit keywords are not placed here (automatically retried in run_with_retry)
SILENT_FAILURE_KEYWORDS = [
    # Context window exceeded
    "context window",
    "context_window_overflow",
    "token limit",
    "conversation is too long",
    "too many tokens",
    # Claude Code actual error patterns
    "error_during_tool",
    "i was interrupted",
    "i'm sorry, i can't",
    "i cannot continue",
    "task was interrupted",
    "aborted",
    "failed to complete",
    "could not complete",
    "unable to complete",
]

# ─── Session Expired Detection Keywords ───
# Error patterns output by Claude Code when a session is expired/deleted with --resume $session_id
# When this pattern is detected, run_with_retry falls back to session_id=None and starts a new session
SESSION_EXPIRED_KEYWORDS = [
    "session not found",
    "no such session",
    "session does not exist",
    "invalid session",
    "session expired",
    "session.*not.*exist",
    "unknown session",
    "cannot resume",
    "resume failed",
]

# ─── Interactive Prompt Auto-Response Patterns ───
# When these patterns are detected in output, automatically sends "1\n" to stdin (auto-select option 1 / Yes)
AUTO_RESPOND_PATTERNS = [
    # ── English patterns ──
    "do you want to proceed",
    "would you like to proceed",
    "proceed? (y/n)",
    "proceed (y/n)",
    "1. yes",
    "1) yes",
    "1: yes",
    "enter your choice",
    "select an option",
    "select option",
    "would you like to",
    "press enter to continue",
    "type 'yes' to confirm",
    "confirm? (y/n)",
    "(y/n):",
    "[y/n]",
    "continue? [y",
    # ── Additional interactive patterns ──
    "do you wish to proceed",
    "would you like to proceed",
    "would you like to continue",
    "do you want to continue",
    "do you want to execute",
    "do you approve",
    "shall we proceed",
    "shall we continue",
    "1. yes",
    "1) yes",
    "yes (y)",
    "yes(y)",
]


# ─── Layer 2: File Change Detection ───
def snapshot_project_files(project_dir: Path = None) -> dict:
    """
    Snapshots the file state of the project directory.
    
    Returns: {filepath: (size, mtime)} dictionary
    """
    if project_dir is None:
        project_dir = Path.cwd()
    
    snapshot = {}
    skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__', 'prompt-runner'}
    
    try:
        for item in project_dir.rglob('*'):
            # Directories to skip
            if any(skip in item.parts for skip in skip_dirs):
                continue
            if item.is_file():
                try:
                    stat = item.stat()
                    snapshot[str(item.relative_to(project_dir))] = (stat.st_size, stat.st_mtime)
                except (OSError, ValueError) as e:
                    log.debug(f"Snapshot stat error on {item}: {e}")
    except Exception as e:
        log.debug(f"Snapshot directory traversal error: {e}")
    
    return snapshot


def diff_snapshots(before: dict, after: dict) -> dict:
    """
    Compares two snapshots and returns the changes.
    
    Returns: {
        "created": [newly created files],
        "modified": [modified files],
        "deleted": [deleted files],
        "total_changes": total number of changes
    }
    """
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    
    created = sorted(after_keys - before_keys)
    deleted = sorted(before_keys - after_keys)
    
    modified = []
    for f in before_keys & after_keys:
        if before[f] != after[f]:
            modified.append(f)
    modified.sort()
    
    return {
        "created": created,
        "modified": modified,
        "deleted": deleted,
        "total_changes": len(created) + len(modified) + len(deleted),
    }


# ═══════════════════════════════════════════════════════════════
# Mandatory Completion Report Template Injection
# ═══════════════════════════════════════════════════════════════

COMPLETION_REPORT_TEMPLATE = """

---
[MANDATORY COMPLETION REPORT - DO NOT SKIP - THIS IS REQUIRED]

Before finishing this step, you MUST write a completion report using EXACTLY this format.
This report is used to monitor quality, detect hallucination, and improve the automation pipeline.
Be brutally honest. Do not inflate or soften results.

## 📋 STEP COMPLETION REPORT

### 1. INSTRUCTIONS RECEIVED
(Summarize the key instructions from this prompt in 3-5 bullet points)
- 
- 
- 

### 2. FEATURES / TOOLS USED
(List every Claude Code feature you actually invoked. If you did NOT use something, write ✗)
- agent-teams / teammate: [✓ used N teammates / ✗ not used — reason: ]
- Agent Swarm / orchestrator: [✓ / ✗ — reason: ]
- Sub-agents: [✓ N sub-agents spawned / ✗]
- Task Management System: [✓ / ✗]
- fork: [✓ / ✗]
- hooks: [✓ / ✗]
- commands: [✓ / ✗]
- skills: [✓ / ✗]
- Task verification / TDD: [✓ / ✗]
- Web search / fetch: [✓ / ✗]
- Source of Truth (SOT): [✓ implemented / ✗ not implemented]
- SOT read BEFORE any write/decision this turn (RLM): [✓ / ✗ — reason: ]
- RLM pattern preserved (recursive reads, no memorized substitution): [✓ / ✗ — reason: ]
- SOT writes routed through orchestrator/team-lead only: [✓ / ✗ / N/A — reason: ]
- Sub-agent invocations recorded in state["steps"][...]["invocations"]: [✓ / ✗ / N/A]

### 3. DELIVERABLES PRODUCED
(List every file created, modified, or deleted with their paths)
CREATED:
- 
MODIFIED:
- 
DELETED:
- 

### 4. OBJECTIVE COMPLETION ASSESSMENT
(Rate each instruction from section 1 as: ✅ DONE / ⚠ PARTIAL / ❌ NOT DONE)
Rate the overall completion: ___% complete

Explain what was NOT completed and why (be specific, not vague):


### 5. HONESTY FLAGS
(Answer yes/no + explanation for each)
- Did you skip any instruction because it was too complex? [YES/NO]:
- Did you make assumptions without explicit confirmation? [YES/NO]:
- Did you produce placeholder/stub code instead of real implementation? [YES/NO]:
- Did you hallucinate file contents you did not actually verify? [YES/NO]:
- Did you run out of turns before completing the task? [YES/NO]:
- Is there anything the next step needs to know about the current state? [YES/NO]:
- Did you bypass SOT to write directly to a shared file/field? [YES/NO]:
- Did you skip the RLM recursive read in favor of memorized context? [YES/NO]:
- Did multiple agents (parallel teammates/sub-agents) write to the same SOT field? [YES/NO]:
- Did you invoke a sub-agent without recording the invocation in state["steps"]? [YES/NO]:

### 6. NEXT STEP RISK
(What could go wrong in the next prompt if this step's output is incomplete?)


---
[END OF MANDATORY COMPLETION REPORT]
"""


MAX_EFFORT_INSTRUCTION = """[MANDATORY SYSTEM RULES - ALWAYS FOLLOW THESE BEFORE ANYTHING ELSE]

## Rule 1: Maximum Thinking
Use maximum extended thinking. Think deeply, exhaustively, and step-by-step before every action and response. Do not take shortcuts. Do not skip steps. Pursue the highest possible quality.

## Rule 2: WebFetch / Network Hang Prevention (CRITICAL)
WebFetch and external HTTP requests can silently hang forever, blocking you and all parent agents.
You MUST follow these rules for every WebFetch or web request:

1. **30-second mental timeout**: If a WebFetch has not returned within what feels like 30 seconds, assume it has hung. Do NOT wait longer.
2. **Never block on a single URL**: If WebFetch on one URL hangs or fails, immediately move on. Use WebSearch results you already have, or try a different source.
3. **Prefer these sources** (more reliable, less likely to hang):
   - Official documentation sites (docs.*, *.readthedocs.io, developer.*)
   - GitHub (github.com, raw.githubusercontent.com)
   - Wikipedia, MDN, Stack Overflow
   - Avoid: personal blogs, unknown CDNs, self-hosted sites
4. **Parallel tool calls**: If you call WebFetch and WebSearch in parallel and WebSearch returns first, DO NOT wait for WebFetch. Proceed with WebSearch results immediately. A partial result is better than a deadlock.
5. **On any network failure**: Log the failure, record the URL as unreachable, and continue with available information. Never retry a hanging URL more than once.
6. **If you are a sub-agent**: Treat any unresponsive tool call as a timeout after one attempt. Return your partial results to the parent agent immediately rather than waiting indefinitely.

## Rule 3: Anti-Deadlock
If you spawn sub-agents (teammates/Task), each sub-agent MUST return a result within a reasonable time even if some of their tool calls fail. Sub-agents should never block the parent indefinitely.

## Rule 4: SOT + RLM Pre-Action Verification (CRITICAL — workflow philosophy)
This workflow operates under TWO ABSOLUTE INVARIANTS that override convenience:
  - Single-file SOT (Source of Truth): all shared state lives in ONE file; only the
    orchestrator/team-lead writes to it; parallel agents NEVER modify the same SOT field.
  - RLM (Recursive Language Model) pattern: agents recursively READ the SOT before
    deciding; they do not act from memorized context alone.

Before ANY data write, file modification, or sub-agent invocation, verify:
(a) You have READ the current SOT file (state.json or the designated SOT) for THIS turn —
    not relying on what you remember from earlier turns.
(b) ALL writes to SOT are routed through the orchestrator/team-lead. No parallel agent
    writes to SOT directly.
(c) RLM is preserved — recursive reads of SOT happen at each decision boundary; cached
    or memorized state does NOT replace a fresh read.
(d) Sub-agent invocations are recorded in state["steps"][step_name]["invocations"]
    via the orchestrator's record_subagent_invocation() (or equivalent).

If ANY of (a)-(d) is unclear or cannot be guaranteed, STOP and report before acting.
Quality and workflow integrity are absolute; tokens, speed, and convenience are not
acceptable reasons to bypass these invariants.

---
"""


def build_augmented_prompt(prompt_file: Path) -> str:
    """
    Appends mandatory completion report template to end of original prompt.
    Does not inject into /clear prompts.
    """
    content = prompt_file.read_text(encoding='utf-8')
    if content.strip() == "/clear":
        return content
    return MAX_EFFORT_INSTRUCTION + content + COMPLETION_REPORT_TEMPLATE


def _save_completion_report(step: int, logs_dir: Path) -> None:
    """
    Concatenates content_block_delta text from {step:03d}.stream.jsonl
    to reconstruct complete text, then extracts the STEP COMPLETION REPORT section.

    Key issue: .log files store display_text chunks with appended '\n',
    so searching fails if marker strings are split across chunk boundaries.
    → Concatenating content_block_delta text without \n from .stream.jsonl
    restores the complete original text verbatim.
    """
    report_file = logs_dir / f"{step:03d}.report.md"
    stream_file = logs_dir / f"{step:03d}.stream.jsonl"

    combined = ""

    # Concatenate all text deltas from stream.jsonl without \n → eliminate fragmentation
    if stream_file.exists():
        parts: list[str] = []
        try:
            for raw in stream_file.read_text(encoding='utf-8').splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                    msg_type = obj.get("type", "")

                    if msg_type == "content_block_delta":
                        # Streaming text chunk — append as-is without \n
                        delta = obj.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            parts.append(text)

                    elif msg_type == "assistant":
                        # Non-streaming full message
                        msg = obj.get("message", {})
                        if isinstance(msg, dict):
                            text = msg.get("text", "")
                        elif isinstance(msg, str):
                            text = msg
                        else:
                            text = ""
                        if text:
                            parts.append(text)

                    elif msg_type == "result":
                        # Final summary — include newline for demarcation
                        t = obj.get("result", "")
                        if t:
                            parts.append("\n" + t)

                except json.JSONDecodeError:
                    continue
        except Exception as e:
            log.debug(f"Stream parsing error: {e}")
        combined = "".join(parts)

    # Fallback to .log file if stream.jsonl is missing or empty
    if not combined:
        log_file = logs_dir / f"{step:03d}.log"
        if log_file.exists():
            try:
                combined = log_file.read_text(encoding='utf-8')
            except Exception:
                combined = ""

    report_marker = "## 📋 STEP COMPLETION REPORT"
    end_marker    = "[END OF MANDATORY COMPLETION REPORT]"

    if report_marker not in combined:
        report_file.write_text(
            f"# Step {step:03d} — No completion report\n\n"
            f"> ⚠ Claude ignored the MANDATORY COMPLETION REPORT instruction.\n\n"
            f"## Raw output (partial)\n```\n{combined[:1000]}\n```\n",
            encoding='utf-8',
        )
        return

    start = combined.index(report_marker)
    end   = combined.find(end_marker)
    body  = combined[start:end].strip() if end > 0 else combined[start:].strip()

    report_file.write_text(
        f"# Step {step:03d} — COMPLETION REPORT\n\n{body}\n",
        encoding='utf-8',
    )
    log.info(f"[{step:03d}] Saved completion report: {report_file.name}")


# ═══════════════════════════════════════════════════════════════
# Core: Single Prompt Execution
# ═══════════════════════════════════════════════════════════════

def run_single_prompt(
    step: int,
    prompt_file: Path,
    session_id: str = None,
    max_turns: int = 0,
    timeout: int = 0,
    skip_permissions: bool = False,
    project_dir: Path = None,
    model: str = None,
    idle_timeout: int = 0,
) -> tuple:  # (verdict: str, session_id: str, duration: int)
    """
    Executes a single prompt.
    Streams in real-time with --output-format stream-json.
    
    stream-json outputs line-by-line JSON in real-time:
      {"type":"assistant","message":{"type":"text","text":"..."}}
      {"type":"result","session_id":"...","cost_usd":...}
    """
    
    import threading
    
    # ─── stdin write lock — prevent concurrent access between write_stdin and process_stream threads ───
    stdin_lock = threading.Lock()
    
    # ─── Command Construction ───
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose"]
    
    if session_id:
        # Resume with specific session ID — bare --continue prohibited
        # (bare --continue resumes system latest session and may enter an unrelated session)
        cmd.extend(["--resume", session_id])
    
    # ── max-turns: 0 means unlimited (run until done) ──
    if max_turns > 0:
        cmd.extend(["--max-turns", str(max_turns)])
    
    # ── Model enforcement: always use auto-selected highest-performance model ──
    effective_model = get_best_model()
    if model and model != effective_model:
        log.warning(f"[{step:03d}] Ignored --model '{model}' → enforcing auto-selected model '{effective_model}'")
    cmd.extend(["--model", effective_model])
    
    # ── Extended thinking (max effort): enabled via environment variable ──
    # CLI flag not supported → passed via environment variable (CLAUDE_CODE_MAX_THINKING_TOKENS)
    
    # Always enabled since pipe mode cannot respond to permission confirmation popups
    cmd.append("--dangerously-skip-permissions")
    
    # ─── Environment Variables (enable agent-teams + max effort) ───
    env = os.environ.copy()
    env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
    # Extended thinking (max effort) — environment variable recognized by Claude Code
    env["CLAUDE_CODE_MAX_THINKING_TOKENS"] = str(THINKING_BUDGET_TOKENS)
    env["ANTHROPIC_THINKING_BUDGET_TOKENS"] = str(THINKING_BUDGET_TOKENS)
    
    # ─── Log Files ───
    log_file = LOGS_DIR / f"{step:03d}.log"
    log_raw_file = LOGS_DIR / f"{step:03d}.stream.jsonl"
    log_err_file = LOGS_DIR / f"{step:03d}.error.log"
    log_meta_file = LOGS_DIR / f"{step:03d}.meta.json"
    
    # ─── State ───
    is_new = (session_id is None)
    mode_str = "new session" if is_new else "continue"
    start_time = time.time()
    is_running = True
    has_output = False
    result_session_id = None
    detected_failure_keyword = None  # Layer 1 verification: silent failure keyword
    last_output_time = time.time()   # Watchdog: timestamp of last output
    stagnation_killed = False        # Whether watchdog killed the process
    
    # idle_timeout: applied in order of parameter → environment variable → default 1200s (20m)
    STAGNATION_LIMIT = idle_timeout if idle_timeout > 0 else int(os.environ.get("IDLE_TIMEOUT", "7200"))
    
    # ─── Elapsed Time Timer + Stagnation Watchdog ───
    def timer_loop():
        nonlocal stagnation_killed
        while is_running:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            silent = int(time.time() - last_output_time)
            
            if has_output:
                status = f"📝 Outputting... (stagnant: {silent}s)"
            else:
                status = "⏳ Working..."
            
            print(f"\r  ⏱ [{step:03d}/{TOTAL_PROMPTS}] {mode_str} │ {mins:02d}:{secs:02d} │ {status}   ",
                  end='', flush=True)
            
            # Stagnation detection: output occurred at least once, but no output for STAGNATION_LIMIT seconds
            if has_output and silent >= STAGNATION_LIMIT and not stagnation_killed:
                stagnation_killed = True
                log.warning(f"\n[{step:03d}] ⏰ Stagnation detected — no output for {STAGNATION_LIMIT//60} minutes (possible WebFetch hang)")
                log.warning(f"[{step:03d}]   → Terminating process forcibly and retrying")
                try:
                    proc.kill()
                except Exception as e:
                    log.debug(f"Process termination error: {e}")
                break
            
            time.sleep(1)
    
    # ─── stream-json Parsing + Real-time Display ───
    def process_stream(pipe, raw_f, text_f):
        nonlocal has_output, result_session_id, detected_failure_keyword, last_output_time
        
        for raw_bytes in pipe:
            # UTF-8 decode lines read from binary pipe
            if isinstance(raw_bytes, bytes):
                raw_line = raw_bytes.decode('utf-8', errors='replace')
            else:
                raw_line = raw_bytes
            line = raw_line.strip()
            if not line:
                continue
            
            # Save raw JSONL
            raw_f.write(line + '\n')
            raw_f.flush()
            
            # ─── Layer 1 verification: real-time keyword detection ───
            line_lower = line.lower()
            for kw in SILENT_FAILURE_KEYWORDS:
                if kw in line_lower:
                    detected_failure_keyword = kw
                    break
            
            # ─── Interactive prompt auto-response (pre-detection on raw line) ───
            # Detect patterns in raw text before JSON parsing (handles non-JSON output)
            # auto_responded: True if already responded on this line → prevent duplicate transmission
            auto_responded = False
            if any(pat in line_lower for pat in AUTO_RESPOND_PATTERNS):
                try:
                    with stdin_lock:
                        if not proc.stdin.closed:
                            proc.stdin.write(b"1\n")
                            proc.stdin.flush()
                    auto_responded = True
                    auto_msg = "🤖 [Auto-response] 1 (Yes) — Interactive prompt detected"
                    print(f"\r{' ' * 80}\r  {auto_msg}", flush=True)
                    text_f.write(auto_msg + '\n')
                    text_f.flush()
                    last_output_time = time.time()
                    log.info(f"[{step:03d}] Sent auto-response: 1 (Yes) ← \"{line[:80]}\"")
                except Exception as e:
                    log.warning(f"[{step:03d}] Failed to send auto-response: {e}")
            
            # JSON parsing
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            msg_type = obj.get("type", "")
            
            # ─── Extract text output ───
            display_text = None
            
            if msg_type == "assistant":
                # Claude response text
                msg = obj.get("message", {})
                if isinstance(msg, dict):
                    display_text = msg.get("text", "")
                elif isinstance(msg, str):
                    display_text = msg
            
            elif msg_type == "content_block_delta":
                # Streaming text chunk — output immediately in real-time (erase timer line and print immediately)
                delta = obj.get("delta", {})
                chunk = delta.get("text", "")
                if chunk:
                    has_output = True
                    last_output_time = time.time()
                    # If timer line exists, erase and print chunk directly (inline without newline)
                    print('\r' + ' ' * 80 + '\r', end='', flush=True)
                    print(chunk, end='', flush=True)
                    text_f.write(chunk)
                    text_f.flush()
                display_text = None  # Already printed, skip lower print block
            
            elif msg_type == "result":
                # Final result — session_id capture + subtype error detection
                result_session_id = obj.get("session_id")
                result_text = obj.get("result", "")
                subtype = obj.get("subtype", "")
                
                if subtype in ("error", "error_during_tool", "interrupted"):
                    # result-level error: mark as silent failure
                    if not detected_failure_keyword:
                        detected_failure_keyword = f"result.subtype={subtype}"
                    display_text = f"\n⚠ Result error ({subtype}): {result_text[:200]}\n"
                elif result_text:
                    # result field is a short summary automatically generated by Claude Code
                    # Report body is in streaming chunks (content_block_delta)
                    # Report extraction is performed by _save_completion_report() from .stream.jsonl
                    display_text = f"\n{'─'*40}\n📋 Result Summary:\n{result_text[:300]}\n{'─'*40}\n"
            
            elif msg_type == "tool_use":
                # Tool usage — display name and key input
                tool_name = obj.get("name", obj.get("tool", ""))
                tool_input = obj.get("input", {})
                if tool_name:
                    if tool_name in ("Task", "task"):
                        # agent-teams Task invocation: display instructions
                        task_desc = str(tool_input.get("description", tool_input.get("prompt", "")))[:80]
                        display_text = f"🤖 [Task → {task_desc}]"
                    else:
                        display_text = f"🔧 [{tool_name}]"
            
            elif msg_type == "tool_result":
                # Tool result — full error for failures, first-line summary for success
                is_error = obj.get("is_error", False)
                result_content = obj.get("content", "")
                if isinstance(result_content, list):
                    result_content = " ".join(c.get("text", "") for c in result_content if isinstance(c, dict))
                result_content = str(result_content).strip()
                if is_error:
                    display_text = f"❌ Tool error: {result_content[:200]}"
                elif result_content:
                    # Normal result — display first-line summary only (truncate if too long)
                    first_line = result_content.split("\n")[0][:120]
                    display_text = f"  ↳ {first_line}" if first_line else None
            
            elif msg_type == "system":
                # System initialization message — display model name
                sys_subtype = obj.get("subtype", "")
                if sys_subtype == "init":
                    model_name = obj.get("model", "")
                    tools = obj.get("tools", [])
                    tool_names = [t.get("name", "") for t in tools if isinstance(t, dict)]
                    display_text = f"🚀 Model: {model_name} | Tools: {', '.join(tool_names[:5])}"
            
            elif msg_type in ("agent_start", "subagent_start"):
                # Sub-agent started
                agent_id = obj.get("agent_id", obj.get("id", ""))
                display_text = f"👾 Sub-agent started: {agent_id}"
            
            elif msg_type in ("agent_end", "subagent_end", "subagent_result"):
                # Sub-agent completed
                agent_id = obj.get("agent_id", obj.get("id", ""))
                display_text = f"✔ Sub-agent completed: {agent_id}"
            
            # ─── Screen Output ───
            if display_text and display_text.strip():
                has_output = True
                last_output_time = time.time()   # Reset watchdog timer
                
                # ── Interactive prompt auto-response (secondary detection on display_text) ──
                # Handles questions nested inside JSON if missed in raw line
                # Skip if auto_responded=True to prevent duplicate transmission
                if not auto_responded:
                    dt_lower = display_text.lower()
                    if any(pat in dt_lower for pat in AUTO_RESPOND_PATTERNS):
                        try:
                            with stdin_lock:
                                if not proc.stdin.closed:
                                    proc.stdin.write(b"1\n")
                                    proc.stdin.flush()
                            auto_msg = "🤖 [Auto-response] 1 (Yes) — Interactive prompt detected"
                            log.info(f"[{step:03d}] Sent auto-response (2nd pass): 1 (Yes)")
                            text_f.write(auto_msg + '\n')
                            text_f.flush()
                        except Exception as e:
                            log.debug(f"Auto-response write error: {e}")
                
                # Clear timer line
                print(f"\r{' ' * 80}\r", end='', flush=True)
                print(f"  {display_text}", flush=True)
                # Also save to text log
                text_f.write(display_text + '\n')
                text_f.flush()
    
    # ─── Start ───
    print(f"\n{'─' * 60}")
    log.info(f"[{step:03d}/{TOTAL_PROMPTS}] Starting execution ({mode_str})")
    print(f"{'─' * 60}")
    
    # ─── Combine prompt + mandatory report template ───
    augmented_prompt = build_augmented_prompt(prompt_file)
    augmented_bytes = augmented_prompt.encode('utf-8')
    
    timer_thread = threading.Thread(target=timer_loop, daemon=True)
    timer_thread.start()
    
    try:
        with open(log_raw_file, 'w', encoding='utf-8') as raw_f, \
             open(log_file, 'w', encoding='utf-8') as text_f, \
             open(log_err_file, 'w', encoding='utf-8') as err_f:
            
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(project_dir) if project_dir else None,
            )
            
            # Write augmented prompt to stdin (separate thread — prevent deadlock)
            # ※ Do not close stdin — keep open for interactive prompt auto-response
            # ※ Protect concurrent access with process_stream thread using stdin_lock
            def write_stdin():
                try:
                    with stdin_lock:
                        proc.stdin.write(augmented_bytes)
                        proc.stdin.flush()
                        proc.stdin.close()  # Send EOF — if not closed, Claude Code deadlocks waiting for EOF
                except BrokenPipeError:
                    log.debug("Stdin pipe closed prematurely")
                except Exception as e:
                    log.debug(f"Stdin write error: {e}")
            
            t_stdin = threading.Thread(target=write_stdin, daemon=True)
            
            stderr_chunks = []
            
            def read_stderr():
                for raw_bytes in proc.stderr:
                    line = raw_bytes.decode('utf-8', errors='replace') if isinstance(raw_bytes, bytes) else raw_bytes
                    err_f.write(line)
                    err_f.flush()
                    stderr_chunks.append(line)
            
            t_out = threading.Thread(
                target=process_stream,
                args=(proc.stdout, raw_f, text_f)
            )
            t_err = threading.Thread(target=read_stderr)
            
            t_stdin.start()
            t_out.start()
            t_err.start()
            
            try:
                proc.wait()  # No timeout — wait until completion
            except KeyboardInterrupt:
                proc.kill()
                is_running = False
                t_out.join(timeout=5)
                t_err.join(timeout=5)
                raise
            
            is_running = False
            t_out.join()
            t_err.join()
            
            returncode = proc.returncode
            stderr_text = ''.join(stderr_chunks)
            
    except Exception as e:
        is_running = False
        duration = int(time.time() - start_time)
        log.error(f"[{step:03d}] Execution error: {e}")
        return ("failed", session_id, duration)
    
    is_running = False
    duration = int(time.time() - start_time)
    mins, secs = divmod(duration, 60)
    
    # ─── Result Evaluation (including 3-layer verification) ───
    print()
    
    # If killed by idle watchdog → treat as suspicious (auto-skip)
    if stagnation_killed:
        log.warning(f"[{step:03d}] 💀 idle_killed — forcibly terminated due to no output for {STAGNATION_LIMIT//60} minutes ({mins}m {secs}s elapsed)")
        meta = {
            "step": step,
            "exit_code": "idle_killed",
            "verdict": "suspicious",
            "failure_keyword": f"idle_timeout_{STAGNATION_LIMIT}s",
            "duration_sec": duration,
            "new_session": is_new,
            "session_id": result_session_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_md5": hashlib.md5(prompt_file.read_bytes()).hexdigest(),
        }
        log_meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
        _save_completion_report(step, logs_dir=LOGS_DIR)
        return ("suspicious", result_session_id, duration)
    
    if returncode == 0:
        # Silent failure possible even with exit_code=0 → Layer 1 verification
        if detected_failure_keyword:
            log.warning(f"[{step:03d}] ⚠ Silent failure detected: '{detected_failure_keyword}'")
            log.warning(f"[{step:03d}] exit_code=0, but task may not have completed.")
            
            meta = {
                "step": step,
                "exit_code": 0,
                "verdict": "suspicious",
                "failure_keyword": detected_failure_keyword,
                "duration_sec": duration,
                "new_session": is_new,
                "session_id": result_session_id,
                "timestamp": datetime.now().isoformat(),
                "prompt_md5": hashlib.md5(prompt_file.read_bytes()).hexdigest(),
            }
            log_meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
            
            _save_completion_report(step, logs_dir=LOGS_DIR)
            return ("suspicious", result_session_id, duration)
        
        log.info(f"[{step:03d}] ✅ Completed — {mins}m {secs}s elapsed")
        
        meta = {
            "step": step,
            "exit_code": 0,
            "verdict": "success",
            "duration_sec": duration,
            "new_session": is_new,
            "session_id": result_session_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_md5": hashlib.md5(prompt_file.read_bytes()).hexdigest(),
        }
        log_meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # ── Save completion report to separate file ──
        _save_completion_report(step, logs_dir=LOGS_DIR)
        
        # Always return actual session_id — do not use "CONTINUE" sentinel
        return ("success", result_session_id, duration)
    else:
        log.error(f"[{step:03d}] ❌ Failed — exit code: {returncode}, {mins}m {secs}s elapsed")
        if stderr_text:
            log.error(f"[{step:03d}] {stderr_text[:200]}")
        
        return ("failed", None, duration)


# ═══════════════════════════════════════════════════════════════
# Retry Logic
# ═══════════════════════════════════════════════════════════════

def _detect_session_expired(err_file: Path, stdout_file: Path, stream_file: Path) -> bool:
    """Detect session expired/deleted (inspect 3 files)."""
    for check_file in [err_file, stdout_file, stream_file]:
        if check_file.exists():
            content = check_file.read_text(encoding='utf-8').lower()
            if any(kw in content for kw in SESSION_EXPIRED_KEYWORDS):
                return True
    return False


def run_with_retry(
    step: int,
    prompt_file: Path,
    session_id: str = None,
    max_retries: int = None,  # P3: Use RateLimitPolicy
    project_dir: Path = None,
    model: str = None,
    idle_timeout: int = 0,
    state: dict = None,
    **kwargs,
) -> tuple:  # (verdict, session_id, total_duration)
    """
    Executes prompt with retry logic (Fix #3: explicit state machine).

    Normal error: MAX_NORMAL_RETRIES retries (exponential backoff 15s, 30s, 60s)
    Rate limit: MAX_RATE_LIMIT_RETRIES retries (5m × 60 = 5 hours)
    Session expired: fallback to session_id=None and immediately retry with new session

    State machine:
        initial          — analyze execution result → decide next state
        normal_retry     — wait for normal error backoff → return to initial
        rate_limit_wait  — wait 5-minute rate-limit countdown → return to initial
        session_recovery — discard session_id → immediately return to initial

    Counters for each state (`normal_attempts`, `rate_limit_retries`) are independent.
    Session recovery resets all counters (new session gets fair retry opportunity).
    """

    if max_retries is None:
        max_retries = RateLimitPolicy.MAX_NORMAL_RETRIES

    total_duration = 0
    normal_attempts = 0
    rate_limit_retries = 0
    state_name = "initial"

    err_file = LOGS_DIR / f"{step:03d}.error.log"
    stdout_file = LOGS_DIR / f"{step:03d}.log"
    stream_file = LOGS_DIR / f"{step:03d}.stream.jsonl"

    while True:
        # ─── initial: Execute prompt + classify results ───
        if state_name == "initial":
            verdict, sid, dur = run_single_prompt(
                step, prompt_file, session_id,
                project_dir=project_dir, model=model, idle_timeout=idle_timeout, **kwargs
            )
            total_duration += dur

            if verdict == "success":
                return ("success", sid, total_duration)
            if verdict == "suspicious":
                # Silent failure returns immediately without retry (evaluated in main loop)
                return ("suspicious", sid, total_duration)

            # Error occurred — determine transition via root cause analysis
            # Priority: session expired > rate-limit > normal error
            if _detect_session_expired(err_file, stdout_file, stream_file) and session_id is not None:
                state_name = "session_recovery"
                continue
            if RateLimitHandler.detect(err_file, stdout_file, stream_file):
                state_name = "rate_limit_wait"
                continue
            state_name = "normal_retry"
            continue

        # ─── normal_retry: Re-execute after exponential backoff ───
        if state_name == "normal_retry":
            normal_attempts += 1
            if normal_attempts > max_retries:
                return ("failed", session_id, total_duration)

            wait = RateLimitPolicy.NORMAL_RETRY_WAITS[
                min(normal_attempts - 1, len(RateLimitPolicy.NORMAL_RETRY_WAITS) - 1)
            ]
            log.warning(f"[{step:03d}] Retry {normal_attempts}/{max_retries} — waiting {wait}s")
            time.sleep(wait)
            state_name = "initial"
            continue

        # ─── rate_limit_wait: Re-execute after 5-minute countdown ───
        if state_name == "rate_limit_wait":
            rate_limit_retries += 1
            if rate_limit_retries > MAX_RATE_LIMIT_RETRIES:
                log.error(f"[{step:03d}] Rate limit wait exceeded {MAX_RATE_LIMIT_RETRIES} attempts. Halting.")
                if state is not None:
                    state_record_rate_limit_exceeded(
                        state, step, rate_limit_retries, MAX_RATE_LIMIT_RETRIES
                    )
                return ("rate_limit_exceeded", session_id, total_duration)

            mins_waited = rate_limit_retries * RATE_LIMIT_WAIT // 60
            log.warning("")
            log.warning(f"[{step:03d}] ⏸ Rate Limit detected!")
            log.warning(
                f"[{step:03d}] Automatic retry in {RATE_LIMIT_WAIT // 60} minutes "
                f"({rate_limit_retries}/{MAX_RATE_LIMIT_RETRIES})"
            )
            log.warning(f"[{step:03d}] Total time waited so far: {mins_waited} minutes")
            log.warning("")

            for remaining in range(RATE_LIMIT_WAIT, 0, -1):
                mins, secs = divmod(remaining, 60)
                print(f"\r  ⏸ Waiting for Rate Limit... {mins:02d}:{secs:02d} ", end='', flush=True)
                time.sleep(1)
            print(f"\r  ▶ Starting retry                              ")

            state_name = "initial"
            continue

        # ─── session_recovery: Discard session → new session + reset counters ───
        if state_name == "session_recovery":
            log.warning(f"[{step:03d}] ⚠ Session expired/deleted detected (session_id: {session_id[:16]}...)")
            log.warning(f"[{step:03d}]   → Falling back to session_id=None, retrying with new session")
            session_id = None
            normal_attempts = 0     # Fair retry opportunity for new session
            rate_limit_retries = 0  # New session = reset rate-limit counter
            state_name = "initial"
            continue

        # Unreachable — defensive guard
        log.error(f"[{step:03d}] Unknown state: {state_name!r}. Marking as failed.")
        return ("failed", session_id, total_duration)


# ═══════════════════════════════════════════════════════════════
# Prompt File Integrity Verification
# ═══════════════════════════════════════════════════════════════

def verify_prompts() -> bool:
    """Verify existence and integrity of all prompt files"""
    
    log.info("Starting prompt file validation...")
    errors = 0
    
    for i in range(1, TOTAL_PROMPTS + 1):
        f = PROMPTS_DIR / f"{i:03d}.txt"
        
        if not f.exists():
            log.error(f"  ❌ File not found: {f}")
            errors += 1
            continue
        
        content = f.read_text(encoding='utf-8')
        
        # Verify /clear files
        if i in CLEAR_POSITIONS:
            if content.strip() != "/clear":
                log.error(f"  ❌ #{i:03d}: /clear file but contents differ: {repr(content[:50])}")
                errors += 1
        else:
            if len(content.strip()) == 0:
                log.error(f"  ❌ #{i:03d}: Empty file")
                errors += 1
    
    # Verify NEW_SESSION_STARTS
    for ns in NEW_SESSION_STARTS:
        if ns > 1:
            prev = ns - 1
            if prev not in CLEAR_POSITIONS:
                log.error(f"  ❌ Logic error: #{ns} is new session, but #{prev} is not /clear")
                errors += 1
    
    if errors == 0:
        log.info(f"  ✅ {TOTAL_PROMPTS} files validated — intact")
        return True
    else:
        log.error(f"  ❌ {errors} errors found")
        return False


# ═══════════════════════════════════════════════════════════════
# Progress Display
# ═══════════════════════════════════════════════════════════════

def show_progress(step: int, state: dict):
    completed = len(state["completed"])
    clears = len(state["clears"])
    failed = len(state["failed"])
    done = completed + clears
    pct = done * 100 // TOTAL_PROMPTS
    
    bar_len = 30
    filled = pct * bar_len // 100
    bar = "█" * filled + "░" * (bar_len - filled)
    
    print(f"\n{'═' * 56}")
    print(f"  Prompt Runner │ Step {step}/{TOTAL_PROMPTS}")
    print(f"  [{bar}] {pct}%")
    print(f"  Completed: {completed}  /clear: {clears}  Failed: {failed}")
    sid = state.get("current_session_id", "")
    if sid:
        print(f"  Session: {sid[:20]}...")
    print(f"{'═' * 56}\n")


# ═══════════════════════════════════════════════════════════════
# Dry Run
# ═══════════════════════════════════════════════════════════════

def dry_run(start_from: int = 1):
    """Preview execution sequence"""
    
    print(f"\n{'═' * 70}")
    print(f"  Dry run — execution sequence preview (Step {start_from}~{TOTAL_PROMPTS})")
    print(f"{'═' * 70}\n")
    
    session_num = 0
    session_id = "(none)"
    exec_count = 0
    
    for step in range(start_from, TOTAL_PROMPTS + 1):
        f = PROMPTS_DIR / f"{step:03d}.txt"
        size = f.stat().st_size if f.exists() else 0
        
        if step in CLEAR_POSITIONS:
            print(f"  #{step:03d}  ── /clear ── Session ended, session_id cleared")
            session_id = "(none)"
        
        elif step in NEW_SESSION_STARTS:
            session_num += 1
            session_id = f"(captured in session {session_num})"
            print(f"  #{step:03d}  ▶ Starting new session {session_num}  "
                  f"claude -p --output-format stream-json --verbose < {step:03d}.txt  ({size}B)")
            exec_count += 1
        
        else:
            print(f"  #{step:03d}    Continue       "
                  f"claude -p --output-format stream-json --verbose --resume $sid < {step:03d}.txt  ({size}B)")
            exec_count += 1
    
    print(f"\n{'─' * 70}")
    print(f"  Execution prompts: {exec_count}")
    print(f"  /clear:            {len(CLEAR_POSITIONS)}")
    print(f"  Total sessions:    {session_num}")
    print(f"{'─' * 70}\n")


# ═══════════════════════════════════════════════════════════════
# Automated Placeholder Substitution
# ═══════════════════════════════════════════════════════════════

PLACEHOLDER_TITLE = "[ Enter what you want to create here ]"
PLACEHOLDER_GOAL = "( Enter the most important purpose of creating this service here, or the shape and standard of the deliverables )"


def setup_prompts(title: str, goal: str) -> bool:
    """
    Substitutes placeholders across all 110 prompt files.
    
    ① "[ Enter what you want to create here ]" → title
    ② "( Enter the most important purpose of creating this service... )" → goal
    
    Returns: Success status
    """
    
    log.info(f"{'═' * 56}")
    log.info(f"  Placeholder substitution")
    log.info(f"  ① Project: {title}")
    log.info(f"  ② Goal: {goal}")
    log.info(f"{'═' * 56}")
    
    replaced_title = 0
    replaced_goal = 0
    
    for i in range(1, TOTAL_PROMPTS + 1):
        filepath = PROMPTS_DIR / f"{i:03d}.txt"
        content = filepath.read_text(encoding='utf-8')
        
        new_content = content
        
        if PLACEHOLDER_TITLE in new_content:
            new_content = new_content.replace(PLACEHOLDER_TITLE, title)
            replaced_title += 1
        
        if PLACEHOLDER_GOAL in new_content:
            new_content = new_content.replace(PLACEHOLDER_GOAL, goal)
            replaced_goal += 1
        
        if new_content != content:
            filepath.write_text(new_content, encoding='utf-8')
    
    log.info(f"  Substitution complete: ①={replaced_title}, ②={replaced_goal}")
    
    # Verification: check remaining placeholders
    remaining = 0
    for i in range(1, TOTAL_PROMPTS + 1):
        content = (PROMPTS_DIR / f"{i:03d}.txt").read_text(encoding='utf-8')
        if PLACEHOLDER_TITLE in content or PLACEHOLDER_GOAL in content:
            remaining += 1
    
    if remaining > 0:
        log.error(f"  ❌ Substitution failed: placeholders remain in {remaining} files")
        return False
    
    log.info(f"  ✅ 0 remaining placeholders — substitution perfect")
    return True


def check_needs_setup() -> bool:
    """Check if placeholders still remain"""
    for i in range(1, TOTAL_PROMPTS + 1):
        content = (PROMPTS_DIR / f"{i:03d}.txt").read_text(encoding='utf-8')
        if PLACEHOLDER_TITLE in content or PLACEHOLDER_GOAL in content:
            return True
    return False


def _print_report_summary(logs_dir: Path, completed_steps: list) -> None:
    """
    Summarizes completion report status after full execution.
    Aggregates partial completions, honesty flags, etc.
    """
    partial_completions = []
    honesty_flags = []
    report_count = 0
    
    for step in completed_steps:
        report_file = logs_dir / f"{step:03d}.report.md"
        if not report_file.exists():
            continue
        
        content = report_file.read_text(encoding='utf-8')
        
        if "No completion report" in content:
            continue
        
        report_count += 1
        
        # Detect partial completion (% achieved)
        import re
        pct_match = re.search(r'(\d+)%\s*complete', content, re.IGNORECASE)
        if pct_match:
            pct = int(pct_match.group(1))
            if pct < 80:
                partial_completions.append((step, pct))
        
        # Detect honesty flags (YES answers)
        yes_flags = re.findall(r'-\s.*?:\s*\[YES\]', content, re.IGNORECASE)
        if yes_flags:
            honesty_flags.append((step, len(yes_flags)))
    
    print(f"\n{'═' * 60}")
    print(f"  📊 Completion Report Analysis")
    print(f"{'═' * 60}")
    print(f"  Reports received: {report_count}/{len(completed_steps)}")
    
    if partial_completions:
        print(f"\n  ⚠ Partial completion (<80%): {len(partial_completions)}")
        for step, pct in partial_completions:
            print(f"    Step {step:03d}: {pct}%")
    
    if honesty_flags:
        print(f"\n  🚩 Honesty flags present: {len(honesty_flags)} steps")
        for step, cnt in honesty_flags:
            print(f"    Step {step:03d}: {cnt} YES flags")
    
    if not partial_completions and not honesty_flags:
        print(f"\n  ✅ No anomalies detected")
    
    print(f"\n  Report location: {logs_dir}/{{step:03d}}.report.md")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════════
# Tests (P0: Pre-production validation)
# ═══════════════════════════════════════════════════════════════

def test_rate_limit_keywords():
    """Fix#1 validation: rate-limit keywords precision (false positive removal)"""
    print("\n[TEST] Verifying rate-limit keywords precision...")

    # RATE_LIMIT_KEYWORDS is defined inside run_with_retry, so difficult to test directly
    # Instead, verify removed keywords are absent
    with open(__file__, 'r', encoding='utf-8') as f:
        content = f.read()

    # Keywords that should be removed
    removed_keywords = ["try again", "too many", "overloaded"]
    for kw in removed_keywords:
        if f'"{kw}"' in content:
            # Verify only present in comments
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if f'"{kw}"' in line and 'RATE_LIMIT_KEYWORDS' in lines[max(0, i-5):i]:
                    print(f"  ❌ '{kw}' still present in RATE_LIMIT_KEYWORDS (Line {i+1})")
                    return False

    # Keywords that should be retained
    required_keywords = ["rate limit", "hit your limit", "quota exceeded", "too many requests"]
    for kw in required_keywords:
        if f'"{kw}"' not in content:
            print(f"  ❌ '{kw}' missing")
            return False

    print("  ✅ Keyword precision passed (false positives eliminated)")
    return True


def test_constants():
    """Fix#2 validation: module-level constants (comments match code)"""
    print("\n[TEST] Verifying module-level constants...")

    # Verify constant definitions
    if MAX_RATE_LIMIT_RETRIES != 60:
        print(f"  ❌ MAX_RATE_LIMIT_RETRIES = {MAX_RATE_LIMIT_RETRIES} (expected 60)")
        return False

    if RATE_LIMIT_WAIT != 300:
        print(f"  ❌ RATE_LIMIT_WAIT = {RATE_LIMIT_WAIT} (expected 300)")
        return False

    # Verify 5-hour calculation
    max_wait_minutes = (MAX_RATE_LIMIT_RETRIES * RATE_LIMIT_WAIT) // 60
    if max_wait_minutes != 300:
        print(f"  ❌ Max wait time = {max_wait_minutes}m (expected 300m)")
        return False

    print(f"  ✅ Constant verification passed ({MAX_RATE_LIMIT_RETRIES} × {RATE_LIMIT_WAIT}s = {max_wait_minutes}m)")
    return True


def test_state_schema():
    """Fix#3 validation: state.json schema (rate_limit_state field)"""
    print("\n[TEST] Verifying state schema...")

    # Initialize new state
    test_state = state_init()

    if "rate_limit_state" not in test_state:
        print("  ❌ Missing rate_limit_state field")
        return False

    if test_state["rate_limit_state"] is not None:
        print(f"  ❌ Initial value is not None: {test_state['rate_limit_state']}")
        return False

    print("  ✅ State schema verification passed")
    return True


def test_state_record_rate_limit():
    """Fix#4 validation: state_record_rate_limit_exceeded() function"""
    print("\n[TEST] Verifying rate-limit state recording function...")

    test_state = state_init()
    state_record_rate_limit_exceeded(test_state, step=35, attempt_count=61, max_attempts=60)

    rls = test_state.get("rate_limit_state")
    if not rls:
        print("  ❌ Failed to record rate_limit_state")
        return False

    required_fields = ["step", "attempt_count", "max_attempts", "last_wait_time", "next_retry_at"]
    for field in required_fields:
        if field not in rls:
            print(f"  ❌ Missing field: {field}")
            return False

    if rls["step"] != 35 or rls["attempt_count"] != 61:
        print(f"  ❌ Incorrect value: {rls}")
        return False

    print("  ✅ Rate-limit state recording passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "═" * 60)
    print("  🧪 Rate-Limit Fix Validation Tests")
    print("═" * 60)

    results = [
        test_rate_limit_keywords(),
        test_constants(),
        test_state_schema(),
        test_state_record_rate_limit(),
    ]

    passed = sum(results)
    total = len(results)

    print("\n" + "═" * 60)
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("═" * 60)
        return True
    else:
        print(f"❌ Tests failed ({passed}/{total})")
        print("═" * 60)
        return False


# ═══════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Claude Code Sequential Prompt Auto-Runner (pipe + session ID)'
    )
    parser.add_argument('--resume', action='store_true',
                        help='Resume from breakpoint')
    parser.add_argument('--from', dest='start_from', type=int, default=0,
                        help='Start from specific number (new session)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview sequence without execution')
    parser.add_argument('--verify', action='store_true',
                        help='Verify prompt file integrity')
    parser.add_argument('--skip-permissions', action='store_true',
                        help='(deprecated) --dangerously-skip-permissions is always applied in pipe mode.')
    parser.add_argument('--input', type=str, default=None,
                        help='Input JSON file (pass title and goal via file)')
    parser.add_argument('--title', type=str, default=None,
                        help='Project title (what to build)')
    parser.add_argument('--goal', type=str, default=None,
                        help='Final goal (standard and format of deliverable)')
    parser.add_argument('--max-turns', type=int, default=0,
                        help='Max agent turns (default: 0 = unlimited, runs until done)')
    parser.add_argument('--timeout', type=int, default=0,
                        help='Max execution time in seconds per prompt (default: 0 = unlimited, runs until done)')
    parser.add_argument('--delay', type=int, default=60,
                        help='Wait time in seconds between prompts (default: 60, 0 = no wait)')
    parser.add_argument('--project-dir', type=str, default=None,
                        help='Working directory for Claude Code (where hooks/commands/skills are loaded). '
                             'Defaults to run.py execution directory if omitted.')
    parser.add_argument('--idle-timeout', type=int, default=7200,
                        help='Idle timeout in seconds before considering process hung (default: 7200=2 hours, 0=use IDLE_TIMEOUT env)')
    parser.add_argument('--model', type=str, default=None,
                        help='Claude model to use (auto-selected, usually not needed)')
    
    args = parser.parse_args()
    
    # ─── Load title/goal from --input JSON file ───
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            log.error(f"Input file not found: {args.input}")
            sys.exit(1)
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        if 'title' not in input_data or 'goal' not in input_data:
            log.error("Input JSON requires 'title' and 'goal' keys.")
            sys.exit(1)
        args.title = input_data['title']
        args.goal = input_data['goal']
        log.info(f"Loaded input file: {args.input}")
    
    # ─── Prompt directly if title/goal not provided ───
    if not args.title and not args.goal and not args.resume and not args.verify:
        if check_needs_setup():
            print()
            print("═" * 56)
            print("  Enter project information")
            print("═" * 56)
            print()
            print("① What to build? (Title)")
            args.title = input("   → ").strip()
            print()
            print("② What is the standard and format of final deliverables? (Goal)")
            args.goal = input("   → ").strip()
            print()
            
            if not args.title or not args.goal:
                log.error("Both title and goal must be entered.")
                sys.exit(1)
    
    # Environment variable overrides
    max_turns = int(os.environ.get("MAX_TURNS", args.max_turns))
    timeout = int(os.environ.get("TIMEOUT", args.timeout))
    delay = int(os.environ.get("DELAY", args.delay))
    skip_perms = os.environ.get("SKIP_PERMISSIONS", "0") == "1" or args.skip_permissions
    
    # ─── Resolve project directory ───
    if args.project_dir:
        project_dir = Path(args.project_dir).resolve()
        if not project_dir.is_dir():
            log.error(f"--project-dir path does not exist: {project_dir}")
            sys.exit(1)
    else:
        project_dir = Path.cwd()
    log.info(f"Project directory: {project_dir}")
    claude_dir = project_dir / ".claude"
    if claude_dir.is_dir():
        log.info(f"  .claude/ directory detected — hooks/commands/skills enabled")
    else:
        log.warning(f"  ⚠ No .claude/ directory ({project_dir}) — hooks/commands/skills disabled")
    
    # ─── 1. Placeholder substitution (highest priority) ───
    if args.title and args.goal:
        if not setup_prompts(args.title, args.goal):
            log.error("Placeholder substitution failed. Halting.")
            sys.exit(1)
    elif args.title or args.goal:
        log.error("--title and --goal must be used together.")
        sys.exit(1)
    
    # ─── 2. Verification mode ───
    if args.verify:
        ok = verify_prompts()
        sys.exit(0 if ok else 1)
    
    # ─── 3. Dry-run mode ───
    if args.dry_run:
        start = args.start_from if args.start_from > 0 else 1
        if args.resume and STATE_FILE.exists():
            start = state_load()["current_step"]
        dry_run(start)
        sys.exit(0)
    
    # ─── 4. Check remaining placeholders (execution mode only) ───
    if check_needs_setup():
        log.error("Placeholders still remain in prompts.")
        log.error("Specify --title and --goal:")
        log.error('  python3 run.py --title "Project Title" --goal "Final Goal"')
        sys.exit(1)
    
    # ─── 5. Determine starting point ───
    if args.resume and STATE_FILE.exists():
        state = state_load()

        # P1: Step Mismatch Recovery (Design Requirement: P1.1)
        expected_step = max(state["completed"]) + 1 if state["completed"] else 1
        actual_step = state["current_step"]

        if actual_step != expected_step:
            log.warning(f"[RESUME] Step consistency check failed")
            log.warning(f"  Expected: {expected_step} (based on completed array)")
            log.warning(f"  Actual: {actual_step} (from state.json)")
            log.warning(f"  Auto-correcting to {expected_step}")
            state["current_step"] = expected_step

            # P1: Audit logging for step mismatch correction
            state_manager.record_audit(state, expected_step, "run_prompt", {
                "event": "step_mismatch_auto_corrected",
                "expected_step": expected_step,
                "actual_step": actual_step
            })

            _state_save(state)

        start_from = state["current_step"]
        log.info(f"Resuming from previous state: Step {start_from}")

        # (P1) Rate-limit state recovery: wait until next_retry_at
        rate_limit_state = state.get("rate_limit_state")
        if rate_limit_state and rate_limit_state["step"] == start_from:
            from datetime import timezone
            next_retry_at = datetime.fromisoformat(rate_limit_state["next_retry_at"])
            now = datetime.now(timezone.utc)

            if now < next_retry_at:
                wait_secs = (next_retry_at - now).total_seconds()
                log.warning(f"[{start_from:03d}] ⏸ Rate-limit state recovery detected")
                log.warning(f"[{start_from:03d}]   Attempt: {rate_limit_state['attempt_count']}/{rate_limit_state['max_attempts']}")
                log.warning(f"[{start_from:03d}]   Waiting {int(wait_secs)}s until next retry...")

                # Countdown display
                for remaining in range(int(wait_secs), 0, -1):
                    mins, secs = divmod(remaining, 60)
                    print(f"\r  ⏸ {mins:02d}:{secs:02d} ", end='', flush=True)
                    time.sleep(1)
                print(f"\r  ▶ Starting retry              ")
                log.info(f"[{start_from:03d}] Wait complete, resuming execution")
            else:
                log.info(f"[{start_from:03d}] Wait time expired, resuming immediately")
                state["rate_limit_state"] = None  # Recovery complete, clear state

                # P1: Audit logging for rate-limit wait completion
                state_manager.record_audit(state, start_from, "rate_limit", {
                    "event": "rate_limit_wait_completed",
                    "recovered_from_step": rate_limit_state["step"]
                })

                _state_save(state)

        if start_from > TOTAL_PROMPTS:
            log.info(f"  ※ current_step({start_from}) > TOTAL_PROMPTS({TOTAL_PROMPTS}) — already completed.")
            sys.exit(0)
    elif args.start_from > 0:
        if args.start_from > TOTAL_PROMPTS:
            log.error(f"--from {args.start_from} exceeds TOTAL_PROMPTS({TOTAL_PROMPTS}).")
            sys.exit(1)
        state = state_init()
        start_from = args.start_from
        state["current_step"] = start_from
        _state_save(state)
        log.info(f"Starting from Step {start_from} (new session)")
    else:
        state = state_init()
        start_from = 1
    
    # ─── 6. Pre-flight verification ───
    LOGS_DIR.mkdir(exist_ok=True)
    
    if not verify_prompts():
        log.error("Prompt file validation failed. Halting.")
        sys.exit(1)
    
    # ─── Start execution ───
    log.info(f"{'═' * 56}")
    log.info(f"  Starting Claude Code prompt auto-execution")
    log.info(f"  Range: Step {start_from} ~ {TOTAL_PROMPTS}")
    log.info(f"  Model: {get_best_model()} (auto-selected) | thinking: {THINKING_BUDGET_TOKENS:,} tokens")
    log.info(f"  max_turns: {'unlimited' if max_turns == 0 else max_turns}, timeout: {'unlimited' if timeout == 0 else f'{timeout}s'}")
    log.info(f"  idle_timeout: {args.idle_timeout}s ({args.idle_timeout//60}m) — declared hung if no output")
    log.info(f"  Inter-prompt delay: {delay}s (adaptive)")
    log.info(f"  Project: {project_dir}")
    log.info(f"{'═' * 56}")
    
    main_start = time.time()
    use_continue = False   # Default: new session
    current_session_id = None  # Actual ID of currently active session (used for --resume)

    # ─── Restore previous session on --resume ───
    if args.resume and STATE_FILE.exists():
        saved_sid = state.get("current_session_id")
        if start_from not in NEW_SESSION_STARTS:
            # Resume mid-session block: continue with --resume using saved session_id
            use_continue = True
            current_session_id = saved_sid  # None is acceptable (handled below)
            if saved_sid:
                log.info(f"  Restoring previous session: {saved_sid[:24]}...")
                log.info(f"  Resuming Step {start_from} with --resume {saved_sid[:8]}...")
            else:
                log.warning(f"  ⚠ No saved session_id — starting fallback new session")
                use_continue = False
        else:
            log.info(f"  Step {start_from} is new session start point → starting new session")
    
    for step in range(start_from, TOTAL_PROMPTS + 1):
        
        # ─── Handle /clear ───
        if step in CLEAR_POSITIONS:
            log.info(f"[{step:03d}] /clear → session ended")
            use_continue = False       # Next prompt is a new session
            current_session_id = None  # Clear session ID
            state_record_clear(state, step)
            continue
        
        # ─── Progress Display ───
        show_progress(step, state)
        
        # ─── Session Evaluation ───
        prompt_file = PROMPTS_DIR / f"{step:03d}.txt"
        
        if step in NEW_SESSION_STARTS:
            use_continue = False       # New session
            current_session_id = None  # Reset session ID

        # session_arg: actual session_id if continue, None if new session
        # Complete removal of "CONTINUE" string sentinel — use actual ID only
        session_arg = current_session_id if use_continue else None
        
        # ─── Layer 2 verification: pre-execution snapshot ───
        snapshot_before = snapshot_project_files(project_dir)
        
        # ─── Execution ───
        verdict, sid, duration = run_with_retry(
            step=step,
            prompt_file=prompt_file,
            session_id=session_arg,
            max_retries=RateLimitPolicy.MAX_NORMAL_RETRIES,  # P3: Use policy class
            max_turns=max_turns,
            timeout=timeout,
            skip_permissions=skip_perms,
            project_dir=project_dir,
            model=args.model,
            idle_timeout=args.idle_timeout,
            state=state,
        )
        
        # ─── Update session ID — track latest session_id after every step ───
        # (Claude always returns session_id in result, whether new session or resume)
        if sid:
            current_session_id = sid
            state_update_session_id(state, sid)
            if not use_continue:
                log.info(f"[{step:03d}] New session ID: {sid[:24]}...")
            else:
                log.debug(f"[{step:03d}] Verified session ID: {sid[:24]}...")
        
        # ─── Layer 2 verification: compare post-execution snapshot ───
        snapshot_after = snapshot_project_files(project_dir)
        changes = diff_snapshots(snapshot_before, snapshot_after)
        
        # ─── Evaluation ───
        if verdict == "success":
            # exit_code=0 + no keyword
            if changes["total_changes"] == 0:
                # No file changes — normal for analysis/reflection prompts
                log.info(f"[{step:03d}] 0 file changes (normal for analysis/reflection prompt)")
            else:
                log.info(f"[{step:03d}] File changes: +{len(changes['created'])} ~{len(changes['modified'])} -{len(changes['deleted'])}")
            
            use_continue = True
            state_record_complete(state, step)
        
        elif verdict == "suspicious":
            # Layer 1 detection: silent failure keyword found → always auto-skip
            if changes["total_changes"] == 0:
                log.warning(f"[{step:03d}] ⚠ Silent failure keyword detected + 0 file changes → auto-skipping")
            else:
                log.warning(
                    f"[{step:03d}] ⚠ Silent failure keyword detected + {changes['total_changes']} file changes → auto-skipping"
                )
                log.warning(f"[{step:03d}]   Changed files: "
                            f"+{len(changes['created'])} ~{len(changes['modified'])} -{len(changes['deleted'])}")
            
            # If stagnation kill (sid=None), session state is ambiguous → safely switch to new session
            # If keyword detected (sid exists), session is valid so preserve continuation
            if sid is None:
                log.warning(f"[{step:03d}]   stagnation kill — session state ambiguous → next step will be new session")
                use_continue = False
                current_session_id = None
            else:
                use_continue = True
            state_record_complete(state, step)

        elif verdict == "rate_limit_exceeded":
            # Rate-limit is transient error — timeout, not permanent failure
            log.warning(f"[{step:03d}] ⏸ Rate-limit exceeded (waited max {MAX_RATE_LIMIT_RETRIES} times)")
            log.warning(f"[{step:03d}]   State saved in rate_limit_state")
            log.warning(f"[{step:03d}]   Resume command: python3 run.py --resume")
            _state_save(state)
            sys.exit(0)  # Normal exit (not error)

        else:  # "failed"
            state_record_fail(state, step)
            log.error(f"[{step:03d}] Final failure. Halting.")
            log.error(f"  Resume command: python3 run.py --resume")
            sys.exit(1)
        
        # ─── Inter-prompt delay (rate limit prevention) ───
        # Reached here = proceed to next step via success or skip
        if delay > 0 and step < TOTAL_PROMPTS:
            next_step = step + 1
            if next_step not in CLEAR_POSITIONS:
                # ── Adaptive delay: based on prompt size + execution duration ──
                prompt_size = prompt_file.stat().st_size
                if prompt_size < 150:
                    # Very short prompt (approval/relay): minimum delay
                    actual_delay = min(delay, 10)
                elif prompt_size < 500:
                    # Short prompt: half delay
                    actual_delay = min(delay, max(10, delay // 2))
                else:
                    # Long prompt (agent work): configured full delay
                    actual_delay = delay
                
                for remaining in range(actual_delay, 0, -1):
                    print(f"\r  ⏸ Waiting {remaining}s until next prompt... ({prompt_size}B)   ", end='', flush=True)
                    time.sleep(1)
                print(f"\r{' ' * 60}\r", end='', flush=True)
    
    # ─── Completion ───
    state_finish(state)
    
    total_sec = int(time.time() - main_start)
    hours = total_sec // 3600
    mins = (total_sec % 3600) // 60
    
    log.info(f"{'═' * 56}")
    log.info(f"  ✅ All executions completed!")
    log.info(f"  Duration: {hours}h {mins}m")
    log.info(f"  Completed: {len(state['completed'])}")
    log.info(f"  /clear: {len(state['clears'])}")
    log.info(f"{'═' * 56}")
    
    # ─── Summary of completion report status ───
    _print_report_summary(LOGS_DIR, state["completed"])


# ═══════════════════════════════════════════════════════════════
# Signal Handler
# ═══════════════════════════════════════════════════════════════

def signal_handler(signum, frame):
    print()
    log.warning("User interrupted (Ctrl+C)")
    log.info("Current state saved in state.json.")
    log.info("Resume: python3 run.py --resume")
    sys.exit(130)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    main()
