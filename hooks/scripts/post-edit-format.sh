#!/bin/bash
# Post-edit format hook - auto-formats files after Edit tool invocation
# Detects formatter from project config and runs it on the edited file

set -euo pipefail

# Get file path from Edit tool input (TOOL_INPUT is JSON from Claude Code)
FILE_PATH=$(echo "${TOOL_INPUT:-}" | jq -r '.file_path // empty' 2>/dev/null || echo "")

# Exit silently if no file path
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Find project root (git root or directory containing the file)
PROJECT_ROOT="$(cd "$(dirname "$FILE_PATH")" && git rev-parse --show-toplevel 2>/dev/null || dirname "$FILE_PATH")"

# Detect formatter and format file
# Priority: biome > prettier > deno

detect_and_format() {
  local file="$1"
  local project_root="$2"

  # Check for Biome (highest priority)
  if [[ -f "$project_root/biome.json" ]] || [[ -f "$project_root/biome.jsonc" ]]; then
    if [[ "${DRY_RUN:-}" == "1" ]]; then
      echo "[DRY_RUN] Would run: biome format --write $file"
      return 0
    fi
    if command -v biome &>/dev/null; then
      echo "🎨 Formatting with biome..."
      biome format --write "$file" 2>&1 || true
    else
      echo "⚠️  biome.json found but biome not installed"
    fi
    return 0
  fi

  # Check for Prettier
  if [[ -f "$project_root/.prettierrc" ]] || \
     [[ -f "$project_root/.prettierrc.json" ]] || \
     [[ -f "$project_root/.prettierrc.js" ]] || \
     [[ -f "$project_root/.prettierrc.yaml" ]] || \
     [[ -f "$project_root/.prettierrc.yml" ]] || \
     (jq -e '.prettier' "$project_root/package.json" &>/dev/null 2>&1); then
    if [[ "${DRY_RUN:-}" == "1" ]]; then
      echo "[DRY_RUN] Would run: prettier --write $file"
      return 0
    fi
    if command -v prettier &>/dev/null; then
      echo "🎨 Formatting with prettier..."
      prettier --write "$file" 2>&1 || true
    elif command -v npx &>/dev/null; then
      echo "🎨 Formatting with prettier (via npx)..."
      npx prettier --write "$file" 2>&1 || true
    else
      echo "⚠️  .prettierrc found but prettier not installed"
    fi
    return 0
  fi

  # Check for Deno
  if [[ -f "$project_root/deno.json" ]] && jq -e '.fmt' "$project_root/deno.json" &>/dev/null 2>&1; then
    if [[ "${DRY_RUN:-}" == "1" ]]; then
      echo "[DRY_RUN] Would run: deno fmt $file"
      return 0
    fi
    if command -v deno &>/dev/null; then
      echo "🎨 Formatting with deno..."
      deno fmt "$file" 2>&1 || true
    else
      echo "⚠️  deno.json found but deno not installed"
    fi
    return 0
  fi

  # No formatter found - exit silently (per spec: no warning)
  return 0
}

# Run formatter detection and execution
detect_and_format "$FILE_PATH" "$PROJECT_ROOT"

# Always exit 0 - formatting errors should not block edits
exit 0
