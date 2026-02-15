#!/bin/bash
# Tests for stop-learn-reflect.sh hook (transcript extraction)
# Run with: bash hooks/tests/test-stop-learn-reflect.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/stop-learn-reflect.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helpers
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
  if [[ ! -f "$file" ]] && [[ ! -L "$file" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (file should not exist: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_file_contains() {
  local file="$1"
  local pattern="$2"
  local test_name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (pattern not found: $pattern)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_symlink() {
  local file="$1"
  local test_name="$2"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ -L "$file" ]]; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (not a symlink: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# Save originals and set up test environment
ORIG_RULES_DIR="$HOME/.claude/rules"
ORIG_RULES_FILE="$ORIG_RULES_DIR/vorbit-learning.md"
ORIG_OUTPUT_FILE="$ORIG_RULES_DIR/unprocessed-corrections.md"

# Backup existing files
BACKUP_DIR="/tmp/test-learn-reflect-backup-$$"
mkdir -p "$BACKUP_DIR"
[[ -f "$ORIG_RULES_FILE" ]] && cp -P "$ORIG_RULES_FILE" "$BACKUP_DIR/"
[[ -f "$ORIG_OUTPUT_FILE" ]] && cp "$ORIG_OUTPUT_FILE" "$BACKUP_DIR/"

cleanup() {
  # Restore backups
  if [[ -f "$BACKUP_DIR/vorbit-learning.md" ]]; then
    cp -P "$BACKUP_DIR/vorbit-learning.md" "$ORIG_RULES_FILE"
  fi
  if [[ -f "$BACKUP_DIR/unprocessed-corrections.md" ]]; then
    cp "$BACKUP_DIR/unprocessed-corrections.md" "$ORIG_OUTPUT_FILE"
  else
    rm -f "$ORIG_OUTPUT_FILE"
  fi
  rm -rf "$BACKUP_DIR"
  # Clean up test projects
  rm -rf /tmp/test-learn-reflect-*
}
trap cleanup EXIT

# Create a test project with git init and mock transcript.
# IMPORTANT: This function echoes the slug, so callers use $(setup_test_project ...).
# The $() creates a subshell, so `cd` inside doesn't persist — callers MUST
# cd to test_dir after calling this function.
setup_test_project() {
  local test_dir="$1"
  rm -rf "$test_dir"
  mkdir -p "$test_dir"
  cd "$test_dir"
  git init --quiet

  # Use git's resolved path (macOS: /tmp -> /private/tmp)
  local resolved_root
  resolved_root=$(git rev-parse --show-toplevel)
  local slug
  slug=$(echo "$resolved_root" | sed 's|/|-|g')
  mkdir -p "$HOME/.claude/projects/$slug"

  echo "$slug"
}

# Create a mock JSONL transcript with correction keywords
create_transcript_with_corrections() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-abc123}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll use useState for the login component shared state."}]},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"No, that's wrong. We always use Zustand, never useState."},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Good point, switching to Zustand store."}]},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:02:00Z"}
{"type":"user","message":{"role":"user","content":"Also remember the events table uses soft deletes."},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:03:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Got it, using soft deletes."}]},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:04:00Z"}
{"type":"user","message":{"role":"user","content":"Looks good, thanks."},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:05:00Z"}
JSONL_EOF

  echo "$transcript"
}

# Create a mock JSONL transcript with NO correction keywords
create_transcript_no_corrections() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-def456}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"user","message":{"role":"user","content":"Please fix the login page styling."},"sessionId":"test-session-def456","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll fix the login page styling now."}]},"sessionId":"test-session-def456","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Great, looks good."},"sessionId":"test-session-def456","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  echo "$transcript"
}

teardown_test_project() {
  local test_dir="$1"
  cd /
  # Clean up both raw and resolved paths (macOS: /tmp -> /private/tmp)
  local resolved
  resolved=$(realpath "$test_dir" 2>/dev/null || echo "$test_dir")
  rm -rf "$test_dir" "$resolved"
  # Clean sessions for both possible slugs
  local slug1 slug2
  slug1=$(echo "$test_dir" | sed 's|/|-|g')
  slug2=$(echo "$resolved" | sed 's|/|-|g')
  rm -rf "$HOME/.claude/projects/$slug1" "$HOME/.claude/projects/$slug2"
}

echo "Running stop-learn-reflect.sh tests..."
echo ""

TEST_BASE="/tmp/test-learn-reflect-$$"

# -----------------------------------------------------------------------------
# Test 1: Skips extraction when loop state is active
# -----------------------------------------------------------------------------
test_skips_during_loop() {
  local test_dir="$TEST_BASE/test1"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Create active loop state
  mkdir -p "$test_dir/.claude"
  echo '{"active":true,"command":"test","iteration":1}' > "$test_dir/.claude/.loop-state.json"

  # Create a transcript with corrections
  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null

  # Remove output file to ensure clean state
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "Loop active: exits 0"
  assert_file_not_exists "$ORIG_OUTPUT_FILE" "Loop active: no output file created"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 2: Extracts corrections when loop is inactive
# -----------------------------------------------------------------------------
test_extracts_with_corrections() {
  local test_dir="$TEST_BASE/test2"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "Corrections found: exits 0"
  assert_file_exists "$ORIG_OUTPUT_FILE" "Corrections found: output file created"
  assert_file_contains "$ORIG_OUTPUT_FILE" "Unprocessed Session Corrections" "Output has header"
  assert_file_contains "$ORIG_OUTPUT_FILE" "Session:" "Output has session block"
  assert_file_contains "$ORIG_OUTPUT_FILE" "Project:" "Output has project path"
  assert_file_contains "$ORIG_OUTPUT_FILE" "USER:" "Output has user messages"
  assert_file_contains "$ORIG_OUTPUT_FILE" "wrong" "Output contains correction keyword"
  assert_file_contains "$ORIG_OUTPUT_FILE" "remember" "Output contains teaching keyword"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 3: No output file when no corrections found
# -----------------------------------------------------------------------------
test_no_output_without_corrections() {
  local test_dir="$TEST_BASE/test3"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "No corrections: exits 0"
  assert_file_not_exists "$ORIG_OUTPUT_FILE" "No corrections: no output file created"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 4: Exits silently when no transcript found
# -----------------------------------------------------------------------------
test_exits_without_transcript() {
  local test_dir="$TEST_BASE/test4"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Don't create any transcript files
  rm -f "$HOME/.claude/projects/$slug"/*.jsonl 2>/dev/null

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "No transcript: exits 0"
  assert_file_not_exists "$ORIG_OUTPUT_FILE" "No transcript: no output file created"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 5: Preceding assistant text is included
# -----------------------------------------------------------------------------
test_assistant_context_included() {
  local test_dir="$TEST_BASE/test5"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null

  rm -f "$ORIG_OUTPUT_FILE"

  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  assert_file_contains "$ORIG_OUTPUT_FILE" "A: \[" "Output includes assistant context prefix"
  assert_file_contains "$ORIG_OUTPUT_FILE" "useState" "Assistant context includes relevant text"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 6: Multiple sessions append to same file
# -----------------------------------------------------------------------------
test_multiple_sessions_append() {
  local test_dir1="$TEST_BASE/test6a"
  local test_dir2="$TEST_BASE/test6b"

  local slug1
  slug1=$(setup_test_project "$test_dir1")
  create_transcript_with_corrections "$HOME/.claude/projects/$slug1" "session-aaa" > /dev/null

  rm -f "$ORIG_OUTPUT_FILE"

  cd "$test_dir1"
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  # Now a second project session
  local slug2
  slug2=$(setup_test_project "$test_dir2")
  create_transcript_with_corrections "$HOME/.claude/projects/$slug2" "session-bbb" > /dev/null

  cd "$test_dir2"
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  # Count session blocks
  local block_count
  block_count=$(grep -c "^## Session:" "$ORIG_OUTPUT_FILE" 2>/dev/null || echo "0")
  assert_eq "2" "$block_count" "Multiple sessions: 2 blocks appended"

  teardown_test_project "$test_dir1"
  teardown_test_project "$test_dir2"
}

# -----------------------------------------------------------------------------
# Test 7: Symlink setup works (fresh install)
# -----------------------------------------------------------------------------
test_symlink_setup() {
  local test_dir="$TEST_BASE/test7"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Remove existing rules file to test fresh install
  rm -f "$ORIG_RULES_FILE"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null

  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  assert_symlink "$ORIG_RULES_FILE" "Fresh install: rules file is a symlink"
  assert_file_contains "$ORIG_RULES_FILE" "vorbit-learning-rules" "Symlink target has marker"

  teardown_test_project "$test_dir"
}

# -----------------------------------------------------------------------------
# Test 8: Idempotent — skips setup when marker exists
# -----------------------------------------------------------------------------
test_idempotent_setup() {
  local test_dir="$TEST_BASE/test8"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Pre-create rules file with marker (simulating existing install)
  rm -f "$ORIG_RULES_FILE"
  echo "existing content" > "$ORIG_RULES_FILE"
  echo "<!-- vorbit-learning-rules -->" >> "$ORIG_RULES_FILE"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null

  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  # File should still be a regular file (not replaced with symlink)
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ ! -L "$ORIG_RULES_FILE" ]]; then
    echo -e "${GREEN}✓${NC} Idempotent: existing file not replaced"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Idempotent: should not replace existing file with marker"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  teardown_test_project "$test_dir"
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

test_skips_during_loop
test_extracts_with_corrections
test_no_output_without_corrections
test_exits_without_transcript
test_assistant_context_included
test_multiple_sessions_append
test_symlink_setup
test_idempotent_setup

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
