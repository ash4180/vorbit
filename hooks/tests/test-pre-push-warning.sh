#!/bin/bash
# Tests for pre-push-warning.sh hook
# Run with: bash hooks/tests/test-pre-push-warning.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/pre-push-warning.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_exit_code() {
  local expected="$1"
  local actual="$2"
  local test_name="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$actual" -eq "$expected" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (expected exit $expected, got $actual)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_output_contains() {
  local expected="$1"
  local actual="$2"
  local test_name="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$actual" | grep -qi "$expected"; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (output did not contain: $expected)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_output_not_contains() {
  local unexpected="$1"
  local actual="$2"
  local test_name="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if ! echo "$actual" | grep -qi "$unexpected"; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (output should not contain: $unexpected)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

echo "Running pre-push-warning.sh tests..."
echo ""

# -----------------------------------------------------------------------------
# Test: Detects 'git push' command
# -----------------------------------------------------------------------------
test_detects_git_push() {
  export TOOL_INPUT='{"command": "git push"}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "push" "$output" "Detects 'git push' command"
  assert_exit_code 0 $exit_code "Git push detection exits 0"
}

# -----------------------------------------------------------------------------
# Test: Detects 'git push origin main'
# -----------------------------------------------------------------------------
test_detects_git_push_origin_main() {
  export TOOL_INPUT='{"command": "git push origin main"}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "push" "$output" "Detects 'git push origin main'"
  assert_exit_code 0 $exit_code "Git push origin main exits 0"
}

# -----------------------------------------------------------------------------
# Test: Ignores 'git status'
# -----------------------------------------------------------------------------
test_ignores_git_status() {
  export TOOL_INPUT='{"command": "git status"}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "warning" "$output" "Ignores 'git status'"
  assert_exit_code 0 $exit_code "Git status exits 0"
}

# -----------------------------------------------------------------------------
# Test: Ignores 'git commit'
# -----------------------------------------------------------------------------
test_ignores_git_commit() {
  export TOOL_INPUT='{"command": "git commit -m \"test\""}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "warning" "$output" "Ignores 'git commit'"
  assert_exit_code 0 $exit_code "Git commit exits 0"
}

# -----------------------------------------------------------------------------
# Test: Always exits 0 (never blocks)
# -----------------------------------------------------------------------------
test_always_exits_zero() {
  export TOOL_INPUT='{"command": "git push --force origin main"}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_exit_code 0 $exit_code "Always exits 0 (never blocks)"
}

# -----------------------------------------------------------------------------
# Test: Ignores non-git commands
# -----------------------------------------------------------------------------
test_ignores_non_git() {
  export TOOL_INPUT='{"command": "npm install"}'

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "push" "$output" "Ignores non-git commands"
  assert_exit_code 0 $exit_code "Non-git command exits 0"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_detects_git_push
test_detects_git_push_origin_main
test_ignores_git_status
test_ignores_git_commit
test_always_exits_zero
test_ignores_non_git

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
