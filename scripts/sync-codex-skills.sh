#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

exec python3 "$REPO_ROOT/scripts/sync-agent-assets.py" \
  --agent codex \
  --agent-home "$CODEX_HOME" \
  --repo-root "$REPO_ROOT" \
  "$@"
