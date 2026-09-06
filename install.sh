#!/usr/bin/env bash
# AgenticWorkflow Universal Cross-Platform Multi-Agent & Host Installer
# Supports local execution or piped curl execution:
#   curl -fsSL https://raw.githubusercontent.com/imMamdouhaboammar/agentic-workflow/main/install.sh | bash

set -e

TARGET_NAME="agentic-workflow"
REPO_URL="https://github.com/imMamdouhaboammar/agentic-workflow.git"

# Detect if executing via pipe or local script file
if [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  # Remote curl execution: Clone into ~/.agentic-workflow
  INSTALL_BASE="$HOME/.agentic-workflow"
  echo "📥 Fetching latest AgenticWorkflow from ${REPO_URL}..."
  if [ -d "$INSTALL_BASE/.git" ]; then
    git -C "$INSTALL_BASE" pull --quiet
  else
    rm -rf "$INSTALL_BASE"
    git clone --depth 1 "$REPO_URL" "$INSTALL_BASE" --quiet
  fi
  SCRIPT_DIR="$INSTALL_BASE"
fi

echo "================================================================="
echo "⚡ Installing AgenticWorkflow across AI Agent Frameworks & Hosts"
echo "================================================================="

# 1. Claude Code
if [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; then
  mkdir -p "$HOME/.claude/skills"
  rm -rf "$HOME/.claude/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.claude/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Claude Code -> $HOME/.claude/skills/${TARGET_NAME}"
fi

# 2. Antigravity / Gemini CLI
if [ -d "$HOME/.gemini" ]; then
  mkdir -p "$HOME/.gemini/config/skills"
  rm -rf "$HOME/.gemini/config/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.gemini/config/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Antigravity / Gemini CLI -> $HOME/.gemini/config/skills/${TARGET_NAME}"
fi

# 3. Cursor IDE
if [ -d "$HOME/.cursor" ] || [ -d "$HOME/Library/Application Support/Cursor" ]; then
  mkdir -p "$HOME/.cursor/skills"
  rm -rf "$HOME/.cursor/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.cursor/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Cursor -> $HOME/.cursor/skills/${TARGET_NAME}"
fi

# 4. Codex / OpenCode
if [ -d "$HOME/.codex" ]; then
  mkdir -p "$HOME/.codex/skills"
  rm -rf "$HOME/.codex/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.codex/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Codex / OpenCode -> $HOME/.codex/skills/${TARGET_NAME}"
fi

# 5. Universal Agent Kernel (~/.agents/skills)
mkdir -p "$HOME/.agents/skills"
rm -rf "$HOME/.agents/skills/${TARGET_NAME}"
cp -r "$SCRIPT_DIR" "$HOME/.agents/skills/${TARGET_NAME}"
echo "  ✅ Installed for Universal Agent Kernel -> $HOME/.agents/skills/${TARGET_NAME}"

# 6. Global CLI Binary Symlink
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
CLI_TARGET="$SCRIPT_DIR/bin/cli.js"
chmod +x "$CLI_TARGET"

ln -sf "$CLI_TARGET" "$BIN_DIR/${TARGET_NAME}"
echo "  ✅ Linked CLI executable -> $BIN_DIR/${TARGET_NAME}"

# Also attempt /usr/local/bin if writable without sudo
if [ -w "/usr/local/bin" ]; then
  ln -sf "$CLI_TARGET" "/usr/local/bin/${TARGET_NAME}"
  echo "  ✅ Linked CLI executable -> /usr/local/bin/${TARGET_NAME}"
fi

# 7. Provision Supportive Tools & Verify System Health
echo ""
echo "⚡ Provisioning supportive tools & frameworks (Ponytail, TOON, Fable, Caveman)..."
if command -v python3 >/dev/null 2>&1; then
  python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
try:
    from core.integrations import IntegrationInstaller
    IntegrationInstaller('${SCRIPT_DIR}').provision_all()
except Exception as e:
    print(f'Note: Supportive tools sync notice: {e}')
" || true
fi

# 8. Run Doctor Diagnostic Check
if command -v bun >/dev/null 2>&1; then
  echo ""
  echo "🩺 Verifying system health and toolchain invariants..."
  bun "$CLI_TARGET" doctor || true
fi

echo ""
echo "================================================================="
echo "🎉 AgenticWorkflow successfully installed and ready everywhere!"
echo "   Run 'agentic-workflow doctor' or 'agentic-workflow health'"
echo "================================================================="

