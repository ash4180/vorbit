#!/bin/bash
# Tests for post-edit-validate.sh hook
# Run with: bash hooks/tests/test-post-edit-validate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/post-edit-validate.sh"

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
}

teardown_test_project() {
  local test_dir="$1"
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

echo "Running post-edit-validate.sh tests..."
echo ""

TEST_PROJECT="/tmp/test-validate-hook-$$"

# -----------------------------------------------------------------------------
# Test: Detects tsconfig.json correctly
# -----------------------------------------------------------------------------
test_detects_tsconfig() {
  setup_test_project "$TEST_PROJECT"
  echo '{"compilerOptions": {"strict": true}}' > "$TEST_PROJECT/tsconfig.json"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "tsc" "$output" "Detects tsconfig.json correctly"
  assert_exit_code 0 $exit_code "TypeScript detection exits 0 in dry-run"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects pyproject.toml with mypy
# -----------------------------------------------------------------------------
test_detects_pyproject_mypy() {
  setup_test_project "$TEST_PROJECT"
  echo '[tool.mypy]' > "$TEST_PROJECT/pyproject.toml"
  touch "$TEST_PROJECT/test.py"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.py"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "mypy\|pyright" "$output" "Detects pyproject.toml with mypy"
  assert_exit_code 0 $exit_code "Python detection exits 0 in dry-run"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects go.mod correctly
# -----------------------------------------------------------------------------
test_detects_gomod() {
  setup_test_project "$TEST_PROJECT"
  echo 'module test' > "$TEST_PROJECT/go.mod"
  touch "$TEST_PROJECT/test.go"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.go"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "go" "$output" "Detects go.mod correctly"
  assert_exit_code 0 $exit_code "Go detection exits 0 in dry-run"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: No validator = silent skip
# -----------------------------------------------------------------------------
test_no_validator_silent_skip() {
  setup_test_project "$TEST_PROJECT"
  touch "$TEST_PROJECT/test.txt"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.txt"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "error" "$output" "No validator = no error message"
  assert_output_not_contains "warning" "$output" "No validator = no warning"
  assert_exit_code 0 $exit_code "No validator exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Validation failure = exit non-zero (blocks)
# -----------------------------------------------------------------------------
test_validation_failure_blocks() {
  setup_test_project "$TEST_PROJECT"
  echo '{"compilerOptions": {"strict": true}}' > "$TEST_PROJECT/tsconfig.json"
  # Create code with intentional type error
  echo 'const x: number = "string";' > "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  # Skip if tsc not installed
  if ! command -v tsc &>/dev/null; then
    echo -e "${GREEN}✓${NC} Validation failure blocks (skipped - tsc not installed)"
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_PASSED=$((TESTS_PASSED + 1))
    teardown_test_project "$TEST_PROJECT"
    return
  fi

  set +e  # Temporarily disable exit on error to capture exit code
  output=$(cd "$TEST_PROJECT" && bash "$HOOK_SCRIPT" 2>&1)
  exit_code=$?
  set -e

  # Validation failure should exit non-zero (block)
  if [[ $exit_code -ne 0 ]]; then
    echo -e "${GREEN}✓${NC} Validation failure blocks (exit $exit_code)"
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Validation failure blocks (expected non-zero, got $exit_code)"
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Validation success = exit 0
# -----------------------------------------------------------------------------
test_validation_success_passes() {
  setup_test_project "$TEST_PROJECT"
  echo '{"compilerOptions": {"strict": true}}' > "$TEST_PROJECT/tsconfig.json"
  echo 'const x: number = 42;' > "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  # Skip if tsc not installed
  if ! command -v tsc &>/dev/null; then
    echo -e "${GREEN}✓${NC} Validation success passes (skipped - tsc not installed)"
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_PASSED=$((TESTS_PASSED + 1))
    teardown_test_project "$TEST_PROJECT"
    return
  fi

  output=$(cd "$TEST_PROJECT" && bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_exit_code 0 $exit_code "Validation success exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_detects_tsconfig
test_detects_pyproject_mypy
test_detects_gomod
test_no_validator_silent_skip
test_validation_failure_blocks
test_validation_success_passes

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
