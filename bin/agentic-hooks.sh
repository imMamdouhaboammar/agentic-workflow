#!/usr/bin/env bash
# ==============================================================================
# Universal Agentic Hooks Framework (UAHF) — Shell & Terminal Hooks
# ==============================================================================
# Ingests, normalizes, and governs all shell commands executed by interactive users,
# terminal sessions, or agent subprocesses (Claude, Codex, Antigravity, Cursor, Kimi).
# Handles pre-execution security and post-session Fable handoff compaction.
# ==============================================================================

export AGENTIC_HOOKS_ACTIVE=1
PROJECT_DIR="${AGENTIC_PROJECT_DIR:-$(pwd)}"

# 1. Intercepted Homebrew Wrapper
brew() {
  if [ -x "$PROJECT_DIR/bin/cli.js" ]; then
    bun "$PROJECT_DIR/bin/cli.js" hooks brew-shim "$@"
    return $?
  elif command -v python3 >/dev/null 2>&1 && [ -f "$PROJECT_DIR/core/hooks/dispatcher.py" ]; then
    python3 -c "from core.hooks.adapters.homebrew_adapter import HomebrewHookAdapter; import sys; sys.exit(HomebrewHookAdapter().run_shim(sys.argv[1:]))" "$@"
    return $?
  fi
  # Fallback to standard brew if framework not reachable
  command brew "$@"
}

# 2. Shell Command Interceptor (Zsh preexec / Bash DEBUG trap)
__agentic_preexec_hook() {
  local cmd="$1"
  [ -z "$cmd" ] && return 0

  # Fast-path: Skip evaluation for trivial builtins to maintain instant prompt speed
  case "$cmd" in
    cd*|pwd|echo*|printf*|true|false|test*|export*|unset*) return 0 ;;
  esac

  if command -v bun >/dev/null 2>&1 && [ -f "$PROJECT_DIR/bin/cli.js" ]; then
    bun "$PROJECT_DIR/bin/cli.js" hooks dispatch --command "$cmd" --source terminal
    local verdict=$?
    if [ $verdict -ne 0 ]; then
      return 1
    fi
  elif command -v python3 >/dev/null 2>&1 && [ -f "$PROJECT_DIR/core/hooks/dispatcher.py" ]; then
    python3 -c "from core.hooks.adapters.shell_adapter import ShellHookAdapter; import sys; sys.exit(ShellHookAdapter().run_cli_preexec(sys.argv[1]))" "$cmd"
    local verdict=$?
    if [ $verdict -ne 0 ]; then
      return 1
    fi
  fi
  return 0
}

# 3. End of Session Hook & Fable Continuation State Compaction
__agentic_session_end_hook() {
  if [ -n "$AGENTIC_SESSION_FINALIZED" ]; then
    return 0
  fi
  export AGENTIC_SESSION_FINALIZED=1

  if command -v bun >/dev/null 2>&1 && [ -f "$PROJECT_DIR/bin/cli.js" ]; then
    bun "$PROJECT_DIR/bin/cli.js" hooks session-end --agent terminal --reason shell_exit >/dev/null 2>&1
  elif command -v python3 >/dev/null 2>&1 && [ -f "$PROJECT_DIR/core/hooks/session_end.py" ]; then
    python3 -c "from core.hooks.session_end import SessionEndManager; SessionEndManager('${PROJECT_DIR}').handle_session_end(agent_id='terminal', reason='shell_exit')" >/dev/null 2>&1
  fi
}

# 4. Zsh / Bash Bindings & Exit Trap
trap __agentic_session_end_hook EXIT

if [ -n "$ZSH_VERSION" ]; then
  autoload -Uz add-zsh-hook 2>/dev/null
  if command -v add-zsh-hook >/dev/null 2>&1; then
    __agentic_zsh_preexec() {
      __agentic_preexec_hook "$1"
    }
    add-zsh-hook preexec __agentic_zsh_preexec
  fi
fi

echo "⚡ [UAHF] Agentic Shell & End-of-Session Hooks Activated (Project: $PROJECT_DIR)"
