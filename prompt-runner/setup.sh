#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  setup.sh — Prompt Auto-Runner Setup Template
#
#  Usage:
#    1. Fill in the 2 variables below
#    2. Run bash setup.sh in terminal
#    3. Run python3 run.py
# ═══════════════════════════════════════════════════════════════

# ┌─────────────────────────────────────────────────────────────┐
# │  Fill in the 2 items below                                  │
# └─────────────────────────────────────────────────────────────┘

# ① What to build (Title / one-line description)
PROJECT_TITLE="ENTER_SERVICE_TITLE_HERE"

# ② Level and format of final deliverable (Goal)
PROJECT_GOAL="ENTER_FINAL_DELIVERABLE_STANDARD_AND_FORM_HERE"

# ┌─────────────────────────────────────────────────────────────┐
# │  Example                                                    │
# ├─────────────────────────────────────────────────────────────┤
# │                                                             │
# │  PROJECT_TITLE="Korean Church Future Forecast Simulation"   │
# │                                                             │
# │  PROJECT_GOAL="Analyze Korean church demographics, finance, │
# │  and pastoral trends for 2025-2045 using big data and AI     │
# │  agents, automatically generating an expert-grade future     │
# │  scenario report (Korean + English)."                       │
# │                                                             │
# └─────────────────────────────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════
#  Do not modify below this line
# ═══════════════════════════════════════════════════════════════

set -uo pipefail  # Removed -e: prevents exit code 1 when grep returns 0 matches

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"

# Input validation
if [[ "$PROJECT_TITLE" == *"SERVICE_TITLE_HERE"* ]] || [[ -z "$PROJECT_TITLE" ]]; then
    echo "❌ Error: Please fill in PROJECT_TITLE."
    echo "   Open setup.sh, fill in the 2 variables, and run again."
    exit 1
fi

if [[ "$PROJECT_GOAL" == *"STANDARD_AND_FORM_HERE"* ]] || [[ -z "$PROJECT_GOAL" ]]; then
    echo "❌ Error: Please fill in PROJECT_GOAL."
    echo "   Open setup.sh, fill in the 2 variables, and run again."
    exit 1
fi

echo "═══════════════════════════════════════════════════════"
echo "  Starting prompt placeholder substitution"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  ① Project: $PROJECT_TITLE"
echo "  ② Goal:    $PROJECT_GOAL"
echo ""

# OS detection (macOS vs Linux sed difference)
if [[ "$(uname)" == "Darwin" ]]; then
    SED_CMD="sed -i ''"
else
    SED_CMD="sed -i"
fi

# Check remaining counts before substitution
BEFORE_1=$(grep -rl "\[ Enter what you want to create here \]" "$PROMPTS_DIR"/*.txt 2>/dev/null | wc -l | tr -d " ")
BEFORE_2=$(grep -rl "Enter the most important purpose of creating this service" "$PROMPTS_DIR"/*.txt 2>/dev/null | wc -l | tr -d " ")

echo "  Before substitution:"
echo "    Placeholder ①: present in ${BEFORE_1} files"
echo "    Placeholder ②: present in ${BEFORE_2} files"
echo ""

# ── Execute substitution ──

# Substitute Placeholder ① and ②
cd "$PROMPTS_DIR"

# Escape special characters for sed
ESCAPED_TITLE=$(printf "%s" "$PROJECT_TITLE" | sed "s/[&/\]/\\&/g")
ESCAPED_GOAL=$(printf "%s" "$PROJECT_GOAL" | sed "s/[&/\]/\\&/g")

if [[ "$(uname)" == "Darwin" ]]; then
    sed -i "" "s/\[ Enter what you want to create here \]/${ESCAPED_TITLE}/g" *.txt
    sed -i "" "s/( Enter the most important purpose of creating this service here, or the shape and standard of the deliverables )/${ESCAPED_GOAL}/g" *.txt
else
    sed -i "s/\[ Enter what you want to create here \]/${ESCAPED_TITLE}/g" *.txt
    sed -i "s/( Enter the most important purpose of creating this service here, or the shape and standard of the deliverables )/${ESCAPED_GOAL}/g" *.txt
fi

# Check remaining counts after substitution (add || true since grep returns exit code 1 on 0 matches)
AFTER_1=$(grep -rl "\[ Enter what you want to create here \]" "$PROMPTS_DIR"/*.txt 2>/dev/null | wc -l || true)
AFTER_1=$(echo "$AFTER_1" | tr -d "[:space:]")
AFTER_2=$(grep -rl "Enter the most important purpose of creating this service" "$PROMPTS_DIR"/*.txt 2>/dev/null | wc -l || true)
AFTER_2=$(echo "$AFTER_2" | tr -d "[:space:]")

# Handle empty values
AFTER_1=${AFTER_1:-0}
AFTER_2=${AFTER_2:-0}

echo "  After substitution:"
echo "    Placeholder ①: ${AFTER_1} remaining"
echo "    Placeholder ②: ${AFTER_2} remaining"
echo ""

# Verification
if [[ "$AFTER_1" -eq 0 ]] && [[ "$AFTER_2" -eq 0 ]]; then
    echo "  ✅ All placeholders successfully substituted"
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  Next steps:"
    echo "    1. python3 ${SCRIPT_DIR}/run.py --verify"
    echo "    2. python3 ${SCRIPT_DIR}/run.py --dry-run"
    echo ""
    echo "  ★ Run (Ensure you specify the project root directory)"
    echo "    python3 ${SCRIPT_DIR}/run.py \\"
    echo "      --project-dir /path/to/your/project \\"
    echo "      --model claude-opus-4-5 \\"
    echo "      --skip-permissions \\"
    echo "      --max-turns 1000 \\"
    echo "      --timeout 7200"
    echo ""
    echo "  ※ --project-dir: Base path where Claude Code looks for .claude/ folder"
    echo "     hooks, commands, skills, CLAUDE.md are loaded relative to this path."
    echo "     Defaults to run.py execution location if omitted (usually the wrong path)"
    echo "  ※ --model: Opus model is strongly recommended for agent-swarm workflows"
    echo "     If omitted, Claude Code default (Sonnet) is used, which may degrade quality"
    echo "═══════════════════════════════════════════════════════"
else
    echo "  ❌ Substitution failed: Placeholders still remain."
    echo "    PROJECT_TITLE or PROJECT_GOAL may contain sed special characters (/, &, \\)."
    echo "    Please substitute manually."
    exit 1
fi
