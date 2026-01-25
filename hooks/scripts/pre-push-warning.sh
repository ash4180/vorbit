#!/bin/bash
# PreToolUse hook - warns before git push commands (but never blocks)

set -euo pipefail

COMMAND=$(echo "${TOOL_INPUT:-}" | jq -r '.command // empty' 2>/dev/null || echo "")

[[ -z "$COMMAND" ]] && exit 0

# Check if command is a git push
if echo "$COMMAND" | grep -qE '^git\s+push'; then
  echo "⚠️  About to push to remote repository"
  echo "   Command: $COMMAND"
  echo "   Make sure you've reviewed your changes!"
fi

# Always exit 0 - this is a reminder, not a blocker
exit 0
