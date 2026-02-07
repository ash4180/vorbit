#!/bin/bash
# Tests for stop-learn-reflect.sh hook
# Run with: bash hooks/tests/test-stop-learn-reflect.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/stop-learn-reflect.sh"

# Runs hook script piping input, captures exit code without set -e interference
run_hook() {
  local input="$1"
  local exit_code=0
  LAST_OUTPUT=$(echo "$input" | bash "$HOOK_SCRIPT" 2>&1) || exit_code=$?
  return $exit_code
}

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
  mkdir -p .claude
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

assert_dir_exists() {
  local dir="$1"
  local test_name="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ -d "$dir" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (directory not found: $dir)"
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

echo "Running stop-learn-reflect.sh tests..."
echo ""

TEST_PROJECT="/tmp/test-learn-reflect-hook-$$"

# -----------------------------------------------------------------------------
# Test 1: First invocation exits 1 (blocks stop for reflection)
# -----------------------------------------------------------------------------
test_first_invocation_blocks() {
  setup_test_project "$TEST_PROJECT"

  exit_code=0
  run_hook "some session output" || exit_code=$?
  output="$LAST_OUTPUT"

  assert_exit_code 1 $exit_code "First invocation exits 1 (blocks stop)"
  assert_file_exists "$TEST_PROJECT/.claude/.learn-reflect-state.json" "State file created"
  assert_dir_exists "$TEST_PROJECT/.claude/learnings" "Learnings directory created"
  assert_output_contains "learn" "$output" "Output mentions learn skill"
  assert_output_contains "capture mode" "$output" "Output mentions capture mode"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test 2: Second invocation exits 0 (allows stop)
# -----------------------------------------------------------------------------
test_second_invocation_allows_stop() {
  setup_test_project "$TEST_PROJECT"

  # First invocation — creates state file
  exit_code=0
  run_hook "session output" || exit_code=$?

  # Second invocation — should clean up and exit 0
  exit_code=0
  run_hook "reflection output" || exit_code=$?

  assert_exit_code 0 $exit_code "Second invocation exits 0 (allows stop)"
  assert_file_not_exists "$TEST_PROJECT/.claude/.learn-reflect-state.json" "State file deleted"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test 3: Skips when loop is active
# -----------------------------------------------------------------------------
test_skips_during_loop() {
  setup_test_project "$TEST_PROJECT"

  # Create active loop state
  echo '{"active":true,"command":"test","iteration":1}' > "$TEST_PROJECT/.claude/.loop-state.json"

  exit_code=0
  run_hook "session output" || exit_code=$?

  assert_exit_code 0 $exit_code "Exits 0 when loop is active (skip reflection)"
  assert_file_not_exists "$TEST_PROJECT/.claude/.learn-reflect-state.json" "No state file created during loop"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test 4: Does NOT skip when loop state exists but inactive
# -----------------------------------------------------------------------------
test_reflects_when_loop_inactive() {
  setup_test_project "$TEST_PROJECT"

  # Loop state exists but not active
  echo '{"active":false}' > "$TEST_PROJECT/.claude/.loop-state.json"

  exit_code=0
  run_hook "session output" || exit_code=$?

  assert_exit_code 1 $exit_code "Exits 1 when loop exists but inactive (reflects)"
  assert_file_exists "$TEST_PROJECT/.claude/.learn-reflect-state.json" "State file created"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test 5: Stale state file from crashed session gets cleaned up
# -----------------------------------------------------------------------------
test_stale_state_cleanup() {
  setup_test_project "$TEST_PROJECT"

  # Simulate stale state from crashed session
  mkdir -p "$TEST_PROJECT/.claude"
  echo '{"reflectRequested":true,"timestamp":"2026-02-06T12:00:00Z"}' > "$TEST_PROJECT/.claude/.learn-reflect-state.json"

  exit_code=0
  run_hook "new session output" || exit_code=$?

  assert_exit_code 0 $exit_code "Stale state file: exits 0 (cleans up)"
  assert_file_not_exists "$TEST_PROJECT/.claude/.learn-reflect-state.json" "Stale state file deleted"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test 6: No loop state file — proceeds normally
# -----------------------------------------------------------------------------
test_no_loop_state() {
  setup_test_project "$TEST_PROJECT"

  # No .loop-state.json at all
  exit_code=0
  run_hook "session output" || exit_code=$?

  assert_exit_code 1 $exit_code "No loop state: exits 1 (reflects)"

  teardown_test_project "$TEST_PROJECT"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_first_invocation_blocks
test_second_invocation_allows_stop
test_skips_during_loop
test_reflects_when_loop_inactive
test_stale_state_cleanup
test_no_loop_state

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
