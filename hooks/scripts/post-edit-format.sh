#!/bin/bash
# Post-edit format hook - auto-formats files after Edit tool invocation
# Priority: biome > prettier (Deno removed - YAGNI)

set -euo pipefail

# Get file path from Edit tool input (TOOL_INPUT is JSON from Claude Code)
FILE_PATH=$(echo "${TOOL_INPUT:-}" | jq -r '.file_path // empty' 2>/dev/null || echo "")

# Exit silently if no file path or file doesn't exist
[[ -z "$FILE_PATH" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

# Find project root (git root or current directory of file)
PROJECT_ROOT="$(cd "$(dirname "$FILE_PATH")" && (git rev-parse --show-toplevel 2>/dev/null || pwd))"

# Check for Biome (highest priority)
if [[ -f "$PROJECT_ROOT/biome.json" ]] || [[ -f "$PROJECT_ROOT/biome.jsonc" ]]; then
  [[ "${DRY_RUN:-}" == "1" ]] && echo "[DRY_RUN] Would run: biome format --write $FILE_PATH" && exit 0
  if command -v biome &>/dev/null; then
    biome format --write "$FILE_PATH" 2>&1 || true
  fi
  exit 0
fi

# Check for Prettier (glob simplifies config detection)
if compgen -G "$PROJECT_ROOT/.prettierrc*" >/dev/null 2>&1 || \
   { [[ -f "$PROJECT_ROOT/package.json" ]] && jq -e '.prettier' "$PROJECT_ROOT/package.json" &>/dev/null; }; then
  [[ "${DRY_RUN:-}" == "1" ]] && echo "[DRY_RUN] Would run: prettier --write $FILE_PATH" && exit 0
  if command -v prettier &>/dev/null; then
    prettier --write "$FILE_PATH" 2>&1 || true
  fi
  exit 0
fi

# No formatter found - exit silently
