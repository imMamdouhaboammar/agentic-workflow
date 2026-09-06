Resume a halted prompt runner execution. Resumes from the last recorded position in state.json.

!python3 "$CLAUDE_PROJECT_DIR/prompt-runner/run.py" \
  --resume \
  --project-dir "$CLAUDE_PROJECT_DIR" \
  --max-turns 0 \
  --timeout 0 \
  --idle-timeout 0 \
  --delay 60
