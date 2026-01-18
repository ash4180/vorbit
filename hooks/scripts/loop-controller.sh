#!/bin/bash
# Loop controller for vorbit implement command (Ralph Wiggum pattern)
# This hook intercepts exit, checks completion, and re-feeds command if needed

set -euo pipefail

# Find project root (git root or current directory)
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Path to loop state file (absolute path)
STATE_FILE="$PROJECT_ROOT/.claude/.loop-state.json"

# If no state file exists, allow exit (normal mode)
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Read loop state
ACTIVE=$(jq -r '.active // false' "$STATE_FILE")

# If loop not active, allow exit
if [[ "$ACTIVE" != "true" ]]; then
  exit 0
fi

# Read loop configuration
COMMAND=$(jq -r '.command // ""' "$STATE_FILE")
COMPLETION_SIGNAL=$(jq -r '.completionSignal // ""' "$STATE_FILE")
MAX_ITERATIONS=$(jq -r '.maxIterations // 50' "$STATE_FILE")
CURRENT_ITERATION=$(jq -r '.iteration // 1' "$STATE_FILE")
ISSUE_ID=$(jq -r '.issueId // ""' "$STATE_FILE")

# Read Claude's last output (stdin contains the conversation)
CLAUDE_OUTPUT=$(cat)

# Check for completion signal in output
if [[ -n "$COMPLETION_SIGNAL" ]] && echo "$CLAUDE_OUTPUT" | grep -qF "$COMPLETION_SIGNAL"; then
  echo "✅ Completion signal detected: $COMPLETION_SIGNAL"
  rm -f "$STATE_FILE"
  exit 0
fi

# Check max iterations
if [[ $CURRENT_ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "⚠️  Max iterations ($MAX_ITERATIONS) reached. Stopping loop."
  rm -f "$STATE_FILE"
  exit 0
fi

# Increment iteration counter
NEXT_ITERATION=$((CURRENT_ITERATION + 1))
jq ".iteration = $NEXT_ITERATION" "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Log iteration
echo ""
echo "🔄 Loop iteration $CURRENT_ITERATION complete. Starting iteration $NEXT_ITERATION..."
echo ""

# Re-feed the command to continue loop
echo "$COMMAND"

# Block exit (non-zero exit code tells Claude to continue)
exit 1
