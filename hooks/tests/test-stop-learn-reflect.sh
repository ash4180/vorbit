#!/bin/bash
# Tests for stop-learn-reflect.sh hook
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

assert_output_contains() {
  local output="$1"
  local pattern="$2"
  local test_name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$output" | grep -q "$pattern" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (pattern not found in output: $pattern)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_output_not_contains() {
  local output="$1"
  local pattern="$2"
  local test_name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if ! echo "$output" | grep -q "$pattern" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $test_name (pattern should NOT be in output: $pattern)"
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
ORIG_SEEN_FILE="$ORIG_RULES_DIR/.seen-correction-sessions"

# Backup existing files
BACKUP_DIR="/tmp/test-learn-reflect-backup-$$"
mkdir -p "$BACKUP_DIR"
[[ -f "$ORIG_RULES_FILE" ]] && cp -P "$ORIG_RULES_FILE" "$BACKUP_DIR/"
[[ -f "$ORIG_OUTPUT_FILE" ]] && cp "$ORIG_OUTPUT_FILE" "$BACKUP_DIR/"
[[ -f "$ORIG_SEEN_FILE" ]] && cp "$ORIG_SEEN_FILE" "$BACKUP_DIR/"

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
  if [[ -f "$BACKUP_DIR/.seen-correction-sessions" ]]; then
    cp "$BACKUP_DIR/.seen-correction-sessions" "$ORIG_SEEN_FILE"
  else
    rm -f "$ORIG_SEEN_FILE"
  fi
  rm -rf "$BACKUP_DIR"
  # Clean up test projects
  rm -rf /tmp/test-learn-reflect-*
}
trap cleanup EXIT

# Create a test project with git init and mock transcript.
setup_test_project() {
  local test_dir="$1"
  rm -rf "$test_dir"
  mkdir -p "$test_dir"
  cd "$test_dir"
  git init --quiet

  local resolved_root
  resolved_root=$(git rev-parse --show-toplevel)
  local slug
  slug=$(echo "$resolved_root" | sed 's|/|-|g')
  mkdir -p "$HOME/.claude/projects/$slug"

  echo "$slug"
}

teardown_test_project() {
  local test_dir="$1"
  cd /
  local resolved
  resolved=$(realpath "$test_dir" 2>/dev/null || echo "$test_dir")
  rm -rf "$test_dir" "$resolved"
  local slug1 slug2
  slug1=$(echo "$test_dir" | sed 's|/|-|g')
  slug2=$(echo "$resolved" | sed 's|/|-|g')
  rm -rf "$HOME/.claude/projects/$slug1" "$HOME/.claude/projects/$slug2"
  # Clear seen file between tests to prevent session ID leakage
  rm -f "$ORIG_SEEN_FILE"
}

# --- Transcript builders ---

create_transcript_with_corrections() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-abc123}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"user","message":{"role":"user","content":"Add a PostgreSQL connection to config.py"},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll add psycopg2 for PostgreSQL connectivity."}]},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, this project uses SQLite not PostgreSQL"},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:02:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed, switching to sqlite3 module instead."}]},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:03:00Z"}
{"type":"user","message":{"role":"user","content":"Looks good, thanks."},"sessionId":"test-session-abc123","timestamp":"2026-02-15T10:04:00Z"}
JSONL_EOF

  echo "$transcript"
}

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

create_transcript_with_teammate_messages() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-team123}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"user","message":{"role":"user","content":"<teammate-message teammate_id=\"auditor\">## Audit Complete\n✓ No issues found. wrong broken error not working.</teammate-message>"},"sessionId":"test-session-team123","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Got the audit results."}]},"sessionId":"test-session-team123","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Thanks, looks good."},"sessionId":"test-session-team123","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  echo "$transcript"
}

create_transcript_with_long_message() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-long456}"
  local transcript="$sessions_dir/$session_id.jsonl"

  local long_text
  long_text="This session is being continued from a previous conversation. Previously the user said wrong and broken and we fixed it. The user also mentioned not working several times. This summary is very long and contains many correction keywords but should be excluded because it is a continuation summary that quotes past corrections rather than being a real correction itself. It goes on and on with more filler text to push it well past the five hundred character limit that we use to filter out these false positives from real corrections."

  cat > "$transcript" << JSONL_EOF
{"type":"user","message":{"role":"user","content":"${long_text}"},"sessionId":"test-session-long456","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Understood, continuing from before."}]},"sessionId":"test-session-long456","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Please continue with the task."},"sessionId":"test-session-long456","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  echo "$transcript"
}

create_transcript_multiple_corrections() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-multi789}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll use MySQL for the database."}]},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, we use PostgreSQL."},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"OK switching to PostgreSQL."}]},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:02:00Z"}
{"type":"user","message":{"role":"user","content":"Still not working, check the port."},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:03:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed the port to 5432."}]},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:04:00Z"}
{"type":"user","message":{"role":"user","content":"Nope, the issue is in the cookie parser."},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:05:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Found and fixed the cookie parser issue."}]},"sessionId":"test-session-multi789","timestamp":"2026-02-15T10:06:00Z"}
JSONL_EOF

  echo "$transcript"
}

create_transcript_with_nope() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-nope}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I added the feature to line 42."}]},"sessionId":"test-session-nope","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"Nope, line 12"},"sessionId":"test-session-nope","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed, moved to line 12."}]},"sessionId":"test-session-nope","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  echo "$transcript"
}

create_transcript_no_user_messages() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-nouser}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Starting task."}]},"sessionId":"test-session-nouser","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Task complete."}]},"sessionId":"test-session-nouser","timestamp":"2026-02-15T10:01:00Z"}
JSONL_EOF

  echo "$transcript"
}

create_transcript_with_self_discovery() {
  local sessions_dir="$1"
  local session_id="${2:-test-session-selfd}"
  local f1="${3:-ROOT_CAUSE}"
  local f2="${4:-RULE}"
  local f3="${5:-DESTINATION}"
  local transcript="$sessions_dir/$session_id.jsonl"

  cat > "$transcript" << JSONL_EOF
{"type":"user","message":{"role":"user","content":"Fix the login page."},"sessionId":"test-session-selfd","timestamp":"2026-02-15T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"${f1}: Session tokens expire too fast due to hardcoded TTL.\n${f2}: Always read TTL from config, never hardcode.\n${f3}: .claude/rules/auth.md"}]},"sessionId":"test-session-selfd","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Thanks, looks good."},"sessionId":"test-session-selfd","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  echo "$transcript"
}

echo "Running stop-learn-reflect.sh tests..."
echo ""

TEST_BASE="/tmp/test-learn-reflect-$$"

# =============================================================================
# Section 0: Exit Code Safety (MUST pass before anything else)
# =============================================================================
echo "--- Section 0: Exit Code Safety ---"

test_exit_code_on_jq_failure() {
  local test_dir="$TEST_BASE/test0a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Create a corrupt transcript (invalid JSON)
  mkdir -p "$HOME/.claude/projects/$slug"
  echo "NOT VALID JSON{{{" > "$HOME/.claude/projects/$slug/test-session-corrupt.jsonl"

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "0a: Corrupt transcript (jq failure) → exits 0"

  teardown_test_project "$test_dir"
}

test_exit_code_on_missing_rules() {
  local test_dir="$TEST_BASE/test0b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null

  # Override PLUGIN_ROOT to a nonexistent path so rules source is missing
  local exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="/nonexistent/path" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "0b: Missing rules file → exits 0"

  teardown_test_project "$test_dir"
}

test_exit_code_on_empty_transcript() {
  local test_dir="$TEST_BASE/test0c"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Create empty transcript
  mkdir -p "$HOME/.claude/projects/$slug"
  touch "$HOME/.claude/projects/$slug/test-session-empty.jsonl"

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "0c: Empty transcript → exits 0"

  teardown_test_project "$test_dir"
}

test_exit_code_only_0_or_2() {
  # Verify across multiple scenarios that we only ever get 0 or 2
  local test_dir="$TEST_BASE/test0d"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  rm -f "$ORIG_OUTPUT_FILE"
  local all_valid="yes"

  # Scenario: no transcript
  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  if [[ "$exit_code" != "0" && "$exit_code" != "2" ]]; then all_valid="no"; fi

  # Scenario: with corrections (should be 2)
  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  if [[ "$exit_code" != "0" && "$exit_code" != "2" ]]; then all_valid="no"; fi

  # Scenario: clean session (should be 0)
  rm -f "$HOME/.claude/projects/$slug"/*.jsonl
  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  if [[ "$exit_code" != "0" && "$exit_code" != "2" ]]; then all_valid="no"; fi

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$all_valid" == "yes" ]]; then
    echo -e "${GREEN}✓${NC} 0d: Script NEVER exits with code other than 0 or 2"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} 0d: Script exited with unexpected code"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  teardown_test_project "$test_dir"
}

test_exit_code_on_jq_failure
test_exit_code_on_missing_rules
test_exit_code_on_empty_transcript
test_exit_code_only_0_or_2

echo ""
echo "--- Section 1: Correction Keyword Detection ---"

# =============================================================================
# Section 1: Correction Keyword Detection
# =============================================================================

test_correction_keyword_wrong() {
  local test_dir="$TEST_BASE/test1a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "1a: User says 'Wrong' → exits 2"
  assert_output_contains "$output" "VORBIT:CORRECTION-CAPTURE" "1a: Output starts with directive"
  assert_output_contains "$output" "Wrong, this project uses SQLite" "1a: Output contains correction message"
  assert_output_contains "$output" "A: \[" "1a: Output includes assistant context"
  assert_output_not_contains "$output" "Add a PostgreSQL connection" "1a: Output excludes unrelated messages"

  teardown_test_project "$test_dir"
}

test_clean_session_exits_0() {
  local test_dir="$TEST_BASE/test1b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "0" "$exit_code" "1b: Clean session → exits 0"
  assert_eq "" "$output" "1b: No stdout on clean session"

  teardown_test_project "$test_dir"
}

test_no_user_messages_exits_0() {
  local test_dir="$TEST_BASE/test1c"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_no_user_messages "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "1c: No user messages → exits 0"

  teardown_test_project "$test_dir"
}

test_nope_keyword() {
  local test_dir="$TEST_BASE/test1d"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_nope "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "1d: User says 'Nope' → exits 2"
  assert_output_contains "$output" "VORBIT:CORRECTION-CAPTURE" "1d: Directive present"
  assert_output_contains "$output" "Nope, line 12" "1d: Correction message present"

  teardown_test_project "$test_dir"
}

test_multiple_corrections() {
  local test_dir="$TEST_BASE/test1e"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_multiple_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "1e: Multiple corrections → exits 2"
  assert_output_contains "$output" "Wrong, we use PostgreSQL" "1e: First correction captured"
  assert_output_contains "$output" "Still not working" "1e: Second correction captured"
  assert_output_contains "$output" "Nope, the issue is in the cookie parser" "1e: Third correction captured"

  teardown_test_project "$test_dir"
}

test_correction_keyword_wrong
test_clean_session_exits_0
test_no_user_messages_exits_0
test_nope_keyword
test_multiple_corrections

echo ""
echo "--- Section 2: False Positive Filtering ---"

# =============================================================================
# Section 2: False Positive Filtering
# =============================================================================

test_long_message_filtered() {
  local test_dir="$TEST_BASE/test2a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_long_message "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "2a: Long message (>500 chars) with keywords → exits 0 (filtered)"

  teardown_test_project "$test_dir"
}

test_teammate_message_filtered() {
  local test_dir="$TEST_BASE/test2b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_teammate_messages "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "2b: Teammate message with keywords → exits 0 (filtered)"

  teardown_test_project "$test_dir"
}

test_real_short_correction_passes() {
  local test_dir="$TEST_BASE/test2c"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Short real user correction: "wrong" in a short message
  local transcript="$HOME/.claude/projects/$slug/test-session-short.jsonl"
  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Using var for variable declarations."}]},"sessionId":"test-session-short","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"wrong, use const"},"sessionId":"test-session-short","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed, using const instead."}]},"sessionId":"test-session-short","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "2" "$exit_code" "2c: Short real correction 'wrong' → exits 2 (not filtered)"

  teardown_test_project "$test_dir"
}

test_no_word_boundary() {
  local test_dir="$TEST_BASE/test2d"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Messages with "not", "know", "cannot" must NOT trigger via "no" substring
  local transcript="$HOME/.claude/projects/$slug/test-session-nosub.jsonl"
  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Setting up the config."}]},"sessionId":"test-session-nosub","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"the script is not ready yet"},"sessionId":"test-session-nosub","timestamp":"2026-02-15T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"I know there is another approach"},"sessionId":"test-session-nosub","timestamp":"2026-02-15T10:02:00Z"}
{"type":"user","message":{"role":"user","content":"we cannot use that library"},"sessionId":"test-session-nosub","timestamp":"2026-02-15T10:03:00Z"}
JSONL_EOF

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "2d: 'not'/'know'/'cannot' do not trigger via 'no' substring → exits 0"
  assert_file_not_exists "$ORIG_SEEN_FILE" "2d: .seen-correction-sessions not written (no real corrections)"

  teardown_test_project "$test_dir"
}

test_long_message_filtered
test_teammate_message_filtered
test_real_short_correction_passes
test_no_word_boundary

echo ""
echo "--- Section 3: Keyword Source ---"

# =============================================================================
# Section 3: Keyword Source (reads from rules file, not hardcoded)
# =============================================================================

test_custom_keywords_from_rules() {
  local test_dir="$TEST_BASE/test3a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Create a custom rules file with ONLY "oops" as keyword
  local custom_rules_dir="$test_dir/skills/learn"
  mkdir -p "$custom_rules_dir"
  cat > "$custom_rules_dir/vorbit-learning-rules.md" << 'EOF'
# Test Rules
<!-- correction-keywords: oops -->
<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->
<!-- vorbit-learning-rules -->
EOF

  # Transcript with "oops" (should match custom keyword)
  local transcript="$HOME/.claude/projects/$slug/test-session-custom.jsonl"
  cat > "$transcript" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Deployed to staging."}]},"sessionId":"test-session-custom","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"oops, that was the wrong branch"},"sessionId":"test-session-custom","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Rolling back."}]},"sessionId":"test-session-custom","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="$test_dir" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "2" "$exit_code" "3a: Custom keyword 'oops' in rules → exits 2"

  # Now swap to "broken" only — same transcript should NOT match
  cat > "$custom_rules_dir/vorbit-learning-rules.md" << 'EOF'
# Test Rules
<!-- correction-keywords: broken -->
<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->
<!-- vorbit-learning-rules -->
EOF

  rm -f "$ORIG_OUTPUT_FILE"
  # Remove session dedup by using different session id
  rm -f "$HOME/.claude/projects/$slug"/*.jsonl
  local transcript2="$HOME/.claude/projects/$slug/test-session-custom2.jsonl"
  cat > "$transcript2" << 'JSONL_EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Deployed to staging."}]},"sessionId":"test-session-custom2","timestamp":"2026-02-15T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"oops, that was the wrong branch"},"sessionId":"test-session-custom2","timestamp":"2026-02-15T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Rolling back."}]},"sessionId":"test-session-custom2","timestamp":"2026-02-15T10:02:00Z"}
JSONL_EOF

  exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="$test_dir" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "3a: Keyword swapped to 'broken', 'oops' no longer matches → exits 0"

  teardown_test_project "$test_dir"
}

test_missing_keywords_comment_exits_0() {
  local test_dir="$TEST_BASE/test3b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  # Rules file without correction-keywords comment
  local custom_rules_dir="$test_dir/skills/learn"
  mkdir -p "$custom_rules_dir"
  cat > "$custom_rules_dir/vorbit-learning-rules.md" << 'EOF'
# Test Rules (no keywords comment)
<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->
<!-- vorbit-learning-rules -->
EOF

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="$test_dir" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "3b: No correction-keywords comment → exits 0 (no crash)"

  teardown_test_project "$test_dir"
}

test_custom_keywords_from_rules
test_missing_keywords_comment_exits_0

echo ""
echo "--- Section 4: Loop & Dedup Guards ---"

# =============================================================================
# Section 4: Loop & Dedup Guards
# =============================================================================

test_skips_during_loop() {
  local test_dir="$TEST_BASE/test4a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  mkdir -p "$test_dir/.claude"
  echo '{"active":true,"command":"test","iteration":1}' > "$test_dir/.claude/.loop-state.json"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "4a: Loop active → exits 0"

  teardown_test_project "$test_dir"
}

test_session_dedup() {
  local test_dir="$TEST_BASE/test4b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null

  # Pre-populate seen file with this session ID (dedup now uses .seen-correction-sessions)
  mkdir -p "$ORIG_RULES_DIR"
  echo "test-session-abc123" > "$ORIG_SEEN_FILE"
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "4b: Session in seen file → exits 0 (dedup)"
  assert_file_not_exists "$ORIG_OUTPUT_FILE" "4b: unprocessed-corrections.md not written (no real content)"

  teardown_test_project "$test_dir"
}

test_correction_retrigger_dedup() {
  local test_dir="$TEST_BASE/test4c"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  # First run: keywords found → exits 2, writes session ID to SEEN_FILE (not OUTPUT_FILE)
  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "2" "$exit_code" "4c: First run with correction keywords → exits 2"
  assert_file_not_exists "$ORIG_OUTPUT_FILE" "4c: unprocessed-corrections.md not written on first run"
  assert_file_exists "$ORIG_SEEN_FILE" "4c: .seen-correction-sessions written"

  # Second run: same session — seen file dedup catches it
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "4c: Second run same session → exits 0 (no re-trigger loop)"

  teardown_test_project "$test_dir"
}

test_skips_during_loop
test_session_dedup
test_correction_retrigger_dedup

echo ""
echo "--- Section 5: Self-Discovery Fallback ---"

# =============================================================================
# Section 5: Self-Discovery Fallback (no keywords, but labeled fields present)
# =============================================================================

test_self_discovery_fallback() {
  local test_dir="$TEST_BASE/test5a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_self_discovery "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "5a: Self-discovery path → exits 0 (writes to file)"
  assert_file_exists "$ORIG_OUTPUT_FILE" "5a: Output file created"
  assert_file_contains "$ORIG_OUTPUT_FILE" "Session:" "5a: Session block present"
  assert_file_contains "$ORIG_OUTPUT_FILE" "Root cause" "5a: Root cause captured"
  assert_file_contains "$ORIG_OUTPUT_FILE" "hardcoded TTL" "5a: Learning content present"

  teardown_test_project "$test_dir"
}

test_self_discovery_fallback

echo ""
echo "--- Section 6: Symlink & Setup ---"

# =============================================================================
# Section 6: Symlink Setup
# =============================================================================

test_symlink_setup() {
  local test_dir="$TEST_BASE/test6a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  rm -f "$ORIG_RULES_FILE"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null

  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  assert_symlink "$ORIG_RULES_FILE" "6a: Fresh install → rules file is a symlink"
  assert_file_contains "$ORIG_RULES_FILE" "vorbit-learning-rules" "6a: Symlink target has marker"

  teardown_test_project "$test_dir"
}

test_idempotent_setup() {
  local test_dir="$TEST_BASE/test6b"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  rm -f "$ORIG_RULES_FILE"
  echo "existing content" > "$ORIG_RULES_FILE"
  echo "<!-- vorbit-learning-rules -->" >> "$ORIG_RULES_FILE"

  create_transcript_no_corrections "$HOME/.claude/projects/$slug" > /dev/null

  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ ! -L "$ORIG_RULES_FILE" ]]; then
    echo -e "${GREEN}✓${NC} 6b: Existing file with marker → not replaced"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} 6b: Should not replace existing file with marker"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  teardown_test_project "$test_dir"
}

test_exits_without_transcript() {
  local test_dir="$TEST_BASE/test6c"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  rm -f "$HOME/.claude/projects/$slug"/*.jsonl 2>/dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "6c: No transcript → exits 0"

  teardown_test_project "$test_dir"
}

test_symlink_setup
test_idempotent_setup
test_exits_without_transcript

echo ""
echo "--- Section 7: Output Format ---"

# =============================================================================
# Section 7: Output Format Verification
# =============================================================================

test_output_format_directive() {
  local test_dir="$TEST_BASE/test7a"
  local slug
  slug=$(setup_test_project "$test_dir")
  cd "$test_dir"

  create_transcript_with_corrections "$HOME/.claude/projects/$slug" > /dev/null
  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  # First line must be the directive
  local first_line
  first_line=$(echo "$output" | head -1)

  assert_eq "[VORBIT:CORRECTION-CAPTURE] Stop hook found correction keywords. Run the Stop-Hook Correction Flow from vorbit-learning-rules.md." "$first_line" "7a: First line is exact directive"

  # Context includes assistant messages
  assert_output_contains "$output" "A: \[" "7a: Assistant context prefix present"
  assert_output_contains "$output" "psycopg2" "7a: Preceding assistant text in context"
  assert_output_contains "$output" "sqlite3" "7a: Following assistant text in context"

  teardown_test_project "$test_dir"
}

test_output_format_directive

# =============================================================================
# RUN SUMMARY
# =============================================================================

echo ""
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
