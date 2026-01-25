#!/bin/bash
# Tests for post-edit-format.sh hook
# Run with: bash hooks/tests/test-post-edit-format.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/post-edit-format.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
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

# =============================================================================
# TEST CASES
# =============================================================================

echo "Running post-edit-format.sh tests..."
echo ""

TEST_PROJECT="/tmp/test-format-hook-$$"

# -----------------------------------------------------------------------------
# Test: Detects biome.json correctly
# -----------------------------------------------------------------------------
test_detects_biome_json() {
  setup_test_project "$TEST_PROJECT"
  echo '{"formatter": {"enabled": true}}' > "$TEST_PROJECT/biome.json"
  touch "$TEST_PROJECT/test.ts"

  # Set up environment like Claude Code would
  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  # Run hook in dry-run mode
  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "biome" "$output" "Detects biome.json correctly"
  assert_exit_code 0 $exit_code "Biome detection exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects .prettierrc correctly
# -----------------------------------------------------------------------------
test_detects_prettierrc() {
  setup_test_project "$TEST_PROJECT"
  echo '{}' > "$TEST_PROJECT/.prettierrc"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "prettier" "$output" "Detects .prettierrc correctly"
  assert_exit_code 0 $exit_code "Prettier detection exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects prettier key in package.json
# -----------------------------------------------------------------------------
test_detects_prettier_in_package_json() {
  setup_test_project "$TEST_PROJECT"
  echo '{"prettier": {"semi": true}}' > "$TEST_PROJECT/package.json"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "prettier" "$output" "Detects prettier key in package.json"
  assert_exit_code 0 $exit_code "Prettier in package.json exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Detects deno.json with fmt config
# -----------------------------------------------------------------------------
test_detects_deno_json() {
  setup_test_project "$TEST_PROJECT"
  echo '{"fmt": {"indentWidth": 2}}' > "$TEST_PROJECT/deno.json"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_contains "deno" "$output" "Detects deno.json with fmt config"
  assert_exit_code 0 $exit_code "Deno detection exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Priority order (biome > prettier > deno)
# -----------------------------------------------------------------------------
test_priority_biome_over_prettier() {
  setup_test_project "$TEST_PROJECT"
  echo '{}' > "$TEST_PROJECT/biome.json"
  echo '{}' > "$TEST_PROJECT/.prettierrc"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true

  assert_output_contains "biome" "$output" "Priority: biome over prettier"
  assert_output_not_contains "prettier" "$output" "Priority: prettier not used when biome exists"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: No formatter = silent skip
# -----------------------------------------------------------------------------
test_no_formatter_silent_skip() {
  setup_test_project "$TEST_PROJECT"
  touch "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  output=$(cd "$TEST_PROJECT" && DRY_RUN=1 bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_output_not_contains "error" "$output" "No formatter = no error message"
  assert_output_not_contains "warning" "$output" "No formatter = no warning"
  assert_exit_code 0 $exit_code "No formatter exits 0"

  teardown_test_project "$TEST_PROJECT"
}

# -----------------------------------------------------------------------------
# Test: Formatter failure = show error, exit 0
# -----------------------------------------------------------------------------
test_formatter_failure_exits_zero() {
  setup_test_project "$TEST_PROJECT"
  echo '{}' > "$TEST_PROJECT/biome.json"
  # Create invalid syntax that would fail formatting
  echo 'const x =' > "$TEST_PROJECT/test.ts"

  export TOOL_INPUT='{"file_path": "'"$TEST_PROJECT/test.ts"'"}'

  # Even if formatter fails, hook should exit 0 (not block)
  output=$(cd "$TEST_PROJECT" && bash "$HOOK_SCRIPT" 2>&1) || true
  exit_code=$?

  assert_exit_code 0 $exit_code "Formatter failure still exits 0 (doesn't block)"

  teardown_test_project "$TEST_PROJECT"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_detects_biome_json
test_detects_prettierrc
test_detects_prettier_in_package_json
test_detects_deno_json
test_priority_biome_over_prettier
test_no_formatter_silent_skip
test_formatter_failure_exits_zero

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
