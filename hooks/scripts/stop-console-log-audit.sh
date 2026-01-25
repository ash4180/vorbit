#!/bin/bash
# Stop hook - scans for debug statements and warns (but never blocks)
# Checks staged/tracked files for console.log, print, etc.

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

# Only check tracked files (avoid node_modules, etc.)
TRACKED_FILES=$(git ls-files 2>/dev/null || find . -type f -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" -o -name "*.go" 2>/dev/null)

[[ -z "$TRACKED_FILES" ]] && exit 0

FOUND_ISSUES=0

# JavaScript/TypeScript: console.log, console.debug, console.warn
JS_MATCHES=$(echo "$TRACKED_FILES" | grep -E '\.(ts|tsx|js|jsx)$' | xargs grep -Hn 'console\.\(log\|debug\|warn\)' 2>/dev/null || true)
if [[ -n "$JS_MATCHES" ]]; then
  if [[ $FOUND_ISSUES -eq 0 ]]; then
    echo "⚠️  Debug statements found:"
    FOUND_ISSUES=1
  fi
  echo "$JS_MATCHES" | while read -r line; do
    echo "  $line"
  done
fi

# Python: print(, breakpoint(), pdb.set_trace()
PY_MATCHES=$(echo "$TRACKED_FILES" | grep -E '\.py$' | xargs grep -Hn -E 'print\(|breakpoint\(\)|pdb\.set_trace\(\)' 2>/dev/null || true)
if [[ -n "$PY_MATCHES" ]]; then
  if [[ $FOUND_ISSUES -eq 0 ]]; then
    echo "⚠️  Debug statements found:"
    FOUND_ISSUES=1
  fi
  echo "$PY_MATCHES" | while read -r line; do
    echo "  $line"
  done
fi

# Go: fmt.Print, log.Print
GO_MATCHES=$(echo "$TRACKED_FILES" | grep -E '\.go$' | xargs grep -Hn -E 'fmt\.Print|log\.Print' 2>/dev/null || true)
if [[ -n "$GO_MATCHES" ]]; then
  if [[ $FOUND_ISSUES -eq 0 ]]; then
    echo "⚠️  Debug statements found:"
    FOUND_ISSUES=1
  fi
  echo "$GO_MATCHES" | while read -r line; do
    echo "  $line"
  done
fi

# Rust: println!, dbg!
RS_MATCHES=$(echo "$TRACKED_FILES" | grep -E '\.rs$' | xargs grep -Hn -E 'println!|dbg!' 2>/dev/null || true)
if [[ -n "$RS_MATCHES" ]]; then
  if [[ $FOUND_ISSUES -eq 0 ]]; then
    echo "⚠️  Debug statements found:"
    FOUND_ISSUES=1
  fi
  echo "$RS_MATCHES" | while read -r line; do
    echo "  $line"
  done
fi

# Always exit 0 - this is a warning, not a blocker
exit 0
