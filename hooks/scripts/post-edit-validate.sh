#!/bin/bash
# Post-edit validate hook - validates files after Edit tool invocation
# Priority: TypeScript > Python > Go (based on file extension and config)
# BLOCKS on validation errors (exit non-zero)

set -euo pipefail

FILE_PATH=$(echo "${TOOL_INPUT:-}" | jq -r '.file_path // empty' 2>/dev/null || echo "")

[[ -z "$FILE_PATH" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

PROJECT_ROOT="$(cd "$(dirname "$FILE_PATH")" && (git rev-parse --show-toplevel 2>/dev/null || pwd))"
FILE_EXT="${FILE_PATH##*.}"

# TypeScript validation
if [[ -f "$PROJECT_ROOT/tsconfig.json" ]] && [[ "$FILE_EXT" == "ts" || "$FILE_EXT" == "tsx" ]]; then
  [[ "${DRY_RUN:-}" == "1" ]] && echo "[DRY_RUN] Would run: tsc --noEmit" && exit 0
  if command -v tsc &>/dev/null; then
    cd "$PROJECT_ROOT" && tsc --noEmit
    exit $?
  fi
  exit 0
fi

# Python validation (mypy or pyright)
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]] && [[ "$FILE_EXT" == "py" ]]; then
  if grep -q '\[tool.mypy\]' "$PROJECT_ROOT/pyproject.toml" 2>/dev/null || \
     grep -q '\[tool.pyright\]' "$PROJECT_ROOT/pyproject.toml" 2>/dev/null; then
    [[ "${DRY_RUN:-}" == "1" ]] && echo "[DRY_RUN] Would run: mypy or pyright $FILE_PATH" && exit 0
    if command -v mypy &>/dev/null; then
      mypy "$FILE_PATH"
      exit $?
    elif command -v pyright &>/dev/null; then
      pyright "$FILE_PATH"
      exit $?
    fi
  fi
  exit 0
fi

# Go validation
if [[ -f "$PROJECT_ROOT/go.mod" ]] && [[ "$FILE_EXT" == "go" ]]; then
  [[ "${DRY_RUN:-}" == "1" ]] && echo "[DRY_RUN] Would run: go build ./..." && exit 0
  if command -v go &>/dev/null; then
    cd "$PROJECT_ROOT" && go build ./...
    exit $?
  fi
  exit 0
fi

# No validator found - exit silently
