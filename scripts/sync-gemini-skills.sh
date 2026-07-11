#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEMINI_HOME="${GEMINI_HOME:-$HOME/.gemini}"

exec python3 "$REPO_ROOT/scripts/sync-agent-assets.py" \
  --agent gemini \
  --agent-home "$GEMINI_HOME" \
  --repo-root "$REPO_ROOT" \
  "$@"
