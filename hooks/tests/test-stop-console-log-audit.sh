#!/bin/bash
# Tests for stop-console-log-audit.sh hook
# Run with: bash hooks/tests/test-stop-console-log-audit.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/stop-console-log-audit.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

setup_test_project() {
  local test_dir="$1"
  rm -rf "$test_dir"
  mkdir -p "$test_dir"
  cd "$test_dir"
  git init --quiet
}

teardown_test_project() {
  local test_dir="$1"
  cd /
  rm -rf "$test_dir"
}

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
  if echo "$actual" | grep -q "$expected"; then
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
  if ! echo "$actual" | grep -q "$unexpected"; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (output should not contain: $unexpected)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

echo "Running stop-console-log-audit.sh tests..."
echo ""

TEST_PROJECT="/tmp/test-console-log-hook-$$"

# -----------------------------------------------------------------------------
# Test: Detects console.log in JS/TS files
# -----------------------------------------------------------------------------
test_detects_console_log() {
  setup_test_project "$TEST_PROJECT"
  echo 'console.log("debug");' > "$TEST_PROJECT/test.ts"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "console.log" "$output" "Detects console.log in JS/TS files"
  assert_output_contains "test.ts" "$output" "Output includes filename"
  assert_exit_code 0 $exit_code "Console.log detection exits 0 (doesn't block)"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects print() in Python files
# -----------------------------------------------------------------------------
test_detects_python_print() {
  setup_test_project "$TEST_PROJECT"
  echo 'print("debug")' > "$TEST_PROJECT/test.py"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "print" "$output" "Detects print() in Python files"
  assert_exit_code 0 $exit_code "Python print detection exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects fmt.Print in Go files
# -----------------------------------------------------------------------------
test_detects_go_print() {
  setup_test_project "$TEST_PROJECT"
  echo 'fmt.Println("debug")' > "$TEST_PROJECT/test.go"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "fmt.Print" "$output" "Detects fmt.Print in Go files"
  assert_exit_code 0 $exit_code "Go print detection exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Output includes file:line format
# -----------------------------------------------------------------------------
test_output_includes_file_line() {
  setup_test_project "$TEST_PROJECT"
  echo 'const x = 1;' > "$TEST_PROJECT/test.ts"
  echo 'console.log("debug");' >> "$TEST_PROJECT/test.ts"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true

  # Should contain something like test.ts:2
  assert_output_contains "test.ts:" "$output" "Output includes file:line format"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Always exits 0 (never blocks)
# -----------------------------------------------------------------------------
test_always_exits_zero() {
  setup_test_project "$TEST_PROJECT"
  # Many debug statements
  echo 'console.log("1");' > "$TEST_PROJECT/a.ts"
  echo 'console.log("2");' >> "$TEST_PROJECT/a.ts"
  echo 'print("3")' > "$TEST_PROJECT/b.py"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_exit_code 0 $exit_code "Always exits 0 even with many debug statements"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: No debug statements = no warning
# -----------------------------------------------------------------------------
test_no_debug_no_warning() {
  setup_test_project "$TEST_PROJECT"
  echo 'const x = 42;' > "$TEST_PROJECT/test.ts"
  git add .

  output=$(bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "console" "$output" "No debug = no console warning"
  assert_output_not_contains "print" "$output" "No debug = no print warning"
  assert_exit_code 0 $exit_code "No debug exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_detects_console_log
test_detects_python_print
test_detects_go_print
test_output_includes_file_line
test_always_exits_zero
test_no_debug_no_warning

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
