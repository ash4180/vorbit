#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
HELPER="$CODEX_HOME/bin/vorbit-github-mcp"

PATH_CODEX="$(command -v codex 2>/dev/null || true)"
if [ -n "$PATH_CODEX" ] && "$PATH_CODEX" --version >/dev/null 2>&1; then
  CODEX_BIN="$PATH_CODEX"
elif [ -x "/Applications/ChatGPT.app/Contents/Resources/codex" ]; then
  CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"
else
  echo "error: Codex is not installed" >&2
  exit 2
fi

for command_name in git gh; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "error: required command is not installed: $command_name" >&2
    exit 2
  fi
done

current_github="$(CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" mcp get github --json 2>/dev/null || true)"
if [ -n "$current_github" ] \
  && ! grep -Fq '"url": "https://api.githubcopilot.com/mcp/"' <<<"$current_github" \
  && ! grep -Fq "\"command\": \"$HELPER\"" <<<"$current_github"; then
  echo "error: refusing to replace a custom GitHub MCP server" >&2
  exit 2
fi

account="$("$REPO_ROOT/scripts/vorbit-github-mcp" --project-root "$REPO_ROOT" --print-account)"

if ! command -v github-mcp-server >/dev/null 2>&1; then
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    echo "Installing GitHub MCP server..."
    brew install github-mcp-server
  else
    echo "error: install github-mcp-server before running this setup" >&2
    exit 2
  fi
fi

CODEX_HOME="$CODEX_HOME" bash "$REPO_ROOT/scripts/sync-codex-skills.sh"
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" mcp add github -- "$HELPER"

echo "Codex setup complete. GitHub account for this repo: $account"
echo "Restart Codex to load the GitHub connection."
