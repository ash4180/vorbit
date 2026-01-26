#!/bin/bash
# Stop hook - scans for debug statements and warns (but never blocks)

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

TRACKED_FILES=$(git ls-files 2>/dev/null || true)
[[ -z "$TRACKED_FILES" ]] && exit 0

FOUND_ISSUES=0

scan_files() {
  local ext_pattern="$1"
  local debug_pattern="$2"
  local matches
  matches=$(echo "$TRACKED_FILES" | grep -E "$ext_pattern" | xargs grep -Hn -E "$debug_pattern" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    if [[ $FOUND_ISSUES -eq 0 ]]; then
      echo "⚠️  Debug statements found:"
      FOUND_ISSUES=1
    fi
    echo "$matches" | sed 's/^/  /'
  fi
}

scan_files '\.(ts|tsx|js|jsx)$' 'console\.(log|debug|warn)'
scan_files '\.py$' 'print\(|breakpoint\(\)|pdb\.set_trace\(\)'
scan_files '\.go$' 'fmt\.Print|log\.Print'
scan_files '\.rs$' 'println!|dbg!'

exit 0
