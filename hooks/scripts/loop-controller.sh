#!/bin/bash
# Loop controller for vorbit implement command
# Manages loop state: tracks iterations, checks completion signals.

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE_FILE="$PROJECT_ROOT/.claude/.loop-state.json"

# If no state file exists, allow exit (normal mode)
if [[ ! -f "$STATE_FILE" ]]; then
  cat > /dev/null
  exit 0
fi

# Read loop state
ACTIVE=$(jq -r '.active // false' "$STATE_FILE")

if [[ "$ACTIVE" != "true" ]]; then
  cat > /dev/null
  exit 0
fi

# Read loop configuration
COMPLETION_SIGNAL=$(jq -r '.completionSignal // ""' "$STATE_FILE")
MAX_ITERATIONS=$(jq -r '.maxIterations // 50' "$STATE_FILE")
CURRENT_ITERATION=$(jq -r '.iteration // 1' "$STATE_FILE")

# Read Claude's last output
CLAUDE_OUTPUT=$(cat)

# Check for completion signal
if [[ -n "$COMPLETION_SIGNAL" ]] && echo "$CLAUDE_OUTPUT" | grep -qF "$COMPLETION_SIGNAL"; then
  rm -f "$STATE_FILE"
  exit 0
fi

# Check max iterations
if [[ $CURRENT_ITERATION -ge $MAX_ITERATIONS ]]; then
  rm -f "$STATE_FILE"
  exit 0
fi

# Increment iteration counter and re-feed command to continue loop
COMMAND=$(jq -r '.command // ""' "$STATE_FILE")
NEXT_ITERATION=$((CURRENT_ITERATION + 1))
jq ".iteration = $NEXT_ITERATION" "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

echo "$COMMAND"
exit 2
