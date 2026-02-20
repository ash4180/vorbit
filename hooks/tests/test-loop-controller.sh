#!/bin/bash
# Tests for loop-controller.sh hook
# Run with: bash hooks/tests/test-loop-controller.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/loop-controller.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_eq() {
  local expected="$1"
  local actual="$2"
  local test_name="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$actual" == "$expected" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name"
    echo "    expected: $expected"
    echo "    actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_file_exists() {
  local file="$1"
  local test_name="$2"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ -f "$file" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (file not found: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_file_not_exists() {
  local file="$1"
  local test_name="$2"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ ! -f "$file" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (file should not exist: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

TEST_BASE="/tmp/test-loop-controller-$$"

cleanup() {
  rm -rf "$TEST_BASE"
}
trap cleanup EXIT

# Set up a temp git repo and return its path
setup_test_dir() {
  local test_dir="$1"
  rm -rf "$test_dir"
  mkdir -p "$test_dir/.claude"
  cd "$test_dir"
  git init --quiet
}

# Write a loop state file
write_state() {
  local dir="$1"
  local json="$2"
  echo "$json" > "$dir/.claude/.loop-state.json"
}

echo "Running loop-controller.sh tests..."
echo ""

# -----------------------------------------------------------------------------
# Test 1: No state file → exits 0, does nothing
# -----------------------------------------------------------------------------
test_no_state_file() {
  local test_dir="$TEST_BASE/test1"
  setup_test_dir "$test_dir"

  # No state file created
  local exit_code=0
  echo "some claude output" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "No state file: exits 0"
  assert_file_not_exists "$test_dir/.claude/.loop-state.json" "No state file: no file created"

  cd /
}

# -----------------------------------------------------------------------------
# Test 2: active: false → exits 0, state file untouched
# -----------------------------------------------------------------------------
test_inactive_loop() {
  local test_dir="$TEST_BASE/test2"
  setup_test_dir "$test_dir"
  write_state "$test_dir" '{"active":false,"iteration":1,"maxIterations":50}'

  local exit_code=0
  echo "some claude output" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "Inactive loop: exits 0"
  assert_file_exists "$test_dir/.claude/.loop-state.json" "Inactive loop: state file untouched"

  cd /
}

# -----------------------------------------------------------------------------
# Test 3: Active loop, no signal, under max → iteration incremented, exit 2, command echoed
# -----------------------------------------------------------------------------
test_increments_iteration() {
  local test_dir="$TEST_BASE/test3"
  setup_test_dir "$test_dir"
  local cmd="test-command-$RANDOM"
  write_state "$test_dir" "{\"active\":true,\"command\":\"$cmd\",\"completionSignal\":\"LOOP_DONE\",\"maxIterations\":50,\"iteration\":3}"

  local exit_code=0
  local stdout
  stdout=$(echo "some output without the signal" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  local next_iteration
  next_iteration=$(jq -r '.iteration' "$test_dir/.claude/.loop-state.json")

  assert_eq "2" "$exit_code" "Active loop: exits 2 (continue signal)"
  assert_eq "4" "$next_iteration" "Active loop: iteration incremented from 3 to 4"
  assert_eq "$cmd" "$stdout" "Active loop: command echoed to stdout"
  assert_file_exists "$test_dir/.claude/.loop-state.json" "Active loop: state file kept"

  cd /
}

# -----------------------------------------------------------------------------
# Test 4: Completion signal in output → state file deleted
# -----------------------------------------------------------------------------
test_completion_signal_stops_loop() {
  local test_dir="$TEST_BASE/test4"
  setup_test_dir "$test_dir"
  write_state "$test_dir" '{"active":true,"completionSignal":"ALL_DONE","maxIterations":50,"iteration":2}'

  local exit_code=0
  echo "Work complete. ALL_DONE" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "Completion signal: exits 0"
  assert_file_not_exists "$test_dir/.claude/.loop-state.json" "Completion signal: state file deleted"

  cd /
}

# -----------------------------------------------------------------------------
# Test 5: Max iterations reached → state file deleted
# -----------------------------------------------------------------------------
test_max_iterations_stops_loop() {
  local test_dir="$TEST_BASE/test5"
  setup_test_dir "$test_dir"
  write_state "$test_dir" '{"active":true,"completionSignal":"DONE","maxIterations":10,"iteration":10}'

  local exit_code=0
  echo "still going" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "Max iterations: exits 0"
  assert_file_not_exists "$test_dir/.claude/.loop-state.json" "Max iterations: state file deleted"

  cd /
}

# -----------------------------------------------------------------------------
# Test 6: Completion signal not present → exits 2, command echoed
# -----------------------------------------------------------------------------
test_no_signal_continues_loop() {
  local test_dir="$TEST_BASE/test6"
  setup_test_dir "$test_dir"
  local cmd="test-command-$RANDOM"
  write_state "$test_dir" "{\"active\":true,\"command\":\"$cmd\",\"completionSignal\":\"LOOP_COMPLETE\",\"maxIterations\":50,\"iteration\":1}"

  local exit_code=0
  local stdout
  stdout=$(echo "output with no signal here" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "No signal: exits 2 (continue signal)"
  assert_eq "$cmd" "$stdout" "No signal: command echoed to stdout"
  assert_file_exists "$test_dir/.claude/.loop-state.json" "No signal: state file kept"

  cd /
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_no_state_file
test_inactive_loop
test_increments_iteration
test_completion_signal_stops_loop
test_max_iterations_stops_loop
test_no_signal_continues_loop

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
