#!/bin/bash
# Stop hook - triggers one reflection turn at session end for learning capture
# Pattern: same as loop-controller.sh (state file prevents infinite loops)
# - First stop: create state file, output reflection prompt, exit 1 (one more turn)
# - Second stop: delete state file, exit 0 (allow exit)
# - Loop active: exit 0 immediately (skip mid-loop)

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE_FILE="$PROJECT_ROOT/.claude/.learn-reflect-state.json"
LOOP_STATE="$PROJECT_ROOT/.claude/.loop-state.json"

# If loop-controller is active, skip reflection (mid-loop, not session end)
if [[ -f "$LOOP_STATE" ]]; then
  LOOP_ACTIVE=$(jq -r '.active // false' "$LOOP_STATE" 2>/dev/null || echo "false")
  if [[ "$LOOP_ACTIVE" == "true" ]]; then
    exit 0
  fi
fi

# Second invocation: reflection already happened, allow stop
if [[ -f "$STATE_FILE" ]]; then
  rm -f "$STATE_FILE"
  exit 0
fi

# First invocation: request one reflection turn
CLAUDE_OUTPUT=$(cat)

# Create state file
mkdir -p "$(dirname "$STATE_FILE")"
echo '{"reflectRequested":true,"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' > "$STATE_FILE"

# Ensure learnings directory exists
mkdir -p "$PROJECT_ROOT/.claude/learnings"

# Output instruction for the agent
echo ""
echo "Use the **learn** skill in capture mode."
echo "Reflect on this session and capture any learnings worth remembering."
echo ""

# Block stop to give agent one reflection turn
exit 1
