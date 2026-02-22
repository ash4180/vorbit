#!/bin/bash
# E2E tests for stop-learn-reflect.sh — covers TL-153 E2E scenarios
# Run with: bash hooks/tests/test-e2e-stop-learn-reflect.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/../scripts/stop-learn-reflect.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_eq() {
  local expected="$1" actual="$2" name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$actual" == "$expected" ]]; then
    echo -e "${GREEN}✓${NC} $name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $name"
    echo "    expected: $expected"
    echo "    actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_output_contains() {
  local output="$1" pattern="$2" name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$output" | grep -q "$pattern" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $name (pattern not found: $pattern)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_output_not_contains() {
  local output="$1" pattern="$2" name="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if ! echo "$output" | grep -q "$pattern" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} $name (pattern should NOT be in output: $pattern)"
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

# --- Shared E2E project setup ---
# Creates a realistic project with files, a git repo, and a sessions dir.
E2E_BASE="/tmp/test-e2e-stop-learn-$$"
ORIG_RULES_DIR="$HOME/.claude/rules"
ORIG_OUTPUT_FILE="$ORIG_RULES_DIR/unprocessed-corrections.md"
ORIG_SEEN_FILE="$ORIG_RULES_DIR/.seen-correction-sessions"
BACKUP_DIR="/tmp/test-e2e-backup-$$"

mkdir -p "$BACKUP_DIR"
[[ -f "$ORIG_OUTPUT_FILE" ]] && cp "$ORIG_OUTPUT_FILE" "$BACKUP_DIR/"
[[ -f "$ORIG_SEEN_FILE" ]] && cp "$ORIG_SEEN_FILE" "$BACKUP_DIR/"

cleanup() {
  [[ -f "$BACKUP_DIR/unprocessed-corrections.md" ]] \
    && cp "$BACKUP_DIR/unprocessed-corrections.md" "$ORIG_OUTPUT_FILE" \
    || rm -f "$ORIG_OUTPUT_FILE"
  [[ -f "$BACKUP_DIR/.seen-correction-sessions" ]] \
    && cp "$BACKUP_DIR/.seen-correction-sessions" "$ORIG_SEEN_FILE" \
    || rm -f "$ORIG_SEEN_FILE"
  rm -rf "$BACKUP_DIR" "$E2E_BASE"
}
trap cleanup EXIT

setup_e2e_project() {
  local test_dir="$1"
  rm -rf "$test_dir"
  mkdir -p "$test_dir"
  cd "$test_dir"
  git init --quiet

  # Project files described in TL-153
  echo "This project uses SQLite" > README.md
  echo "# config.py" > config.py

  local resolved_root
  resolved_root=$(git rev-parse --show-toplevel)
  local slug
  slug=$(echo "$resolved_root" | sed 's|/|-|g')
  local sessions_dir="$HOME/.claude/projects/$slug"
  mkdir -p "$sessions_dir"

  echo "$slug"
}

teardown_e2e_project() {
  local test_dir="$1"
  cd /
  local resolved
  resolved=$(realpath "$test_dir" 2>/dev/null || echo "$test_dir")
  local slug1 slug2
  slug1=$(echo "$test_dir" | sed 's|/|-|g')
  slug2=$(echo "$resolved" | sed 's|/|-|g')
  rm -rf "$test_dir" "$resolved" \
    "$HOME/.claude/projects/$slug1" \
    "$HOME/.claude/projects/$slug2"
}

run_hook() {
  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?
  echo "$exit_code|$output"
}

echo "Running E2E tests for stop-learn-reflect.sh..."
echo ""

# =============================================================================
# E2E-1: Wrong tech assumption → exit 2 with plain text directive
# =============================================================================
echo "--- E2E-1: Wrong tech assumption ---"

e2e_1() {
  local test_dir="$E2E_BASE/e2e1"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e1-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Add a PostgreSQL connection to config.py"},"sessionId":"e2e1-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll add psycopg2 for PostgreSQL connectivity."}]},"sessionId":"e2e1-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, this project uses SQLite not PostgreSQL"},"sessionId":"e2e1-session","timestamp":"2026-02-21T10:02:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed, switching to sqlite3 module instead."}]},"sessionId":"e2e1-session","timestamp":"2026-02-21T10:03:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "E2E-1: exits 2"

  local first_line
  first_line=$(echo "$output" | head -1)
  assert_eq "[VORBIT:CORRECTION-CAPTURE] Stop hook found correction keywords. Run the Stop-Hook Correction Flow from vorbit-learning-rules.md." \
    "$first_line" "E2E-1: first line is exact directive"

  assert_output_contains "$output" "Wrong, this project uses SQLite not PostgreSQL" "E2E-1: correction message in output"
  assert_output_contains "$output" "psycopg2" "E2E-1: preceding assistant context included"
  assert_output_contains "$output" "sqlite3" "E2E-1: following assistant context included"
  assert_output_not_contains "$output" "Add a PostgreSQL connection" "E2E-1: unrelated first message excluded"

  # unprocessed-corrections.md must stay clean — dedup goes to .seen-correction-sessions
  assert_output_not_contains "$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)" "Session:" \
    "E2E-1: unprocessed-corrections.md not written (stays clean)"

  teardown_e2e_project "$test_dir"
}

e2e_1
echo ""

# =============================================================================
# E2E-2: Wrong line target → exit 2
# =============================================================================
echo "--- E2E-2: Wrong line target ---"

e2e_2() {
  local test_dir="$E2E_BASE/e2e2"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e2-session.jsonl" << 'JSONL'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I added the feature to line 42."}]},"sessionId":"e2e2-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"Nope, line 12"},"sessionId":"e2e2-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed, moved to line 12."}]},"sessionId":"e2e2-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "E2E-2: exits 2"
  local first_line
  first_line=$(echo "$output" | head -1)
  assert_eq "[VORBIT:CORRECTION-CAPTURE] Stop hook found correction keywords. Run the Stop-Hook Correction Flow from vorbit-learning-rules.md." \
    "$first_line" "E2E-2: directive present"

  teardown_e2e_project "$test_dir"
}

e2e_2
echo ""

# =============================================================================
# E2E-3: Multiple corrections → all captured
# =============================================================================
echo "--- E2E-3: Multiple corrections ---"

e2e_3() {
  local test_dir="$E2E_BASE/e2e3"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e3-session.jsonl" << 'JSONL'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll use MySQL for the database."}]},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, we use PostgreSQL."},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Switching to PostgreSQL."}]},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:02:00Z"}
{"type":"user","message":{"role":"user","content":"Still not working, check the port."},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:03:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed the port to 5432."}]},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:04:00Z"}
{"type":"user","message":{"role":"user","content":"Nope, the issue is in the cookie parser."},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:05:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Found and fixed the cookie parser."}]},"sessionId":"e2e3-session","timestamp":"2026-02-21T10:06:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "2" "$exit_code" "E2E-3: exits 2"
  assert_output_contains "$output" "Wrong, we use PostgreSQL" "E2E-3: first correction captured"
  assert_output_contains "$output" "Still not working" "E2E-3: second correction captured"
  assert_output_contains "$output" "Nope, the issue is in the cookie parser" "E2E-3: third correction captured"

  assert_output_not_contains "$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)" "Session:" \
    "E2E-3: unprocessed-corrections.md not written (stays clean)"

  teardown_e2e_project "$test_dir"
}

e2e_3
echo ""

# =============================================================================
# E2E-4: Clean session → exit 0, no stdout
# =============================================================================
echo "--- E2E-4: Clean session ---"

e2e_4() {
  local test_dir="$E2E_BASE/e2e4"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e4-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Please fix the login page styling."},"sessionId":"e2e4-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll fix the login page styling now."}]},"sessionId":"e2e4-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Great, looks good."},"sessionId":"e2e4-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?

  assert_eq "0" "$exit_code" "E2E-4: exits 0"
  assert_eq "" "$output" "E2E-4: no stdout"

  teardown_e2e_project "$test_dir"
}

e2e_4
echo ""

# =============================================================================
# E2E-5: False positive — continuation summary (>500 chars) → exit 0
# =============================================================================
echo "--- E2E-5: False positive — continuation summary ---"

e2e_5() {
  local test_dir="$E2E_BASE/e2e5"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local long_text="This session is being continued from a previous conversation. Previously the user said wrong and broken and we fixed it. The user also mentioned not working several times. This summary is very long and contains many correction keywords but should be excluded because it is a continuation summary that quotes past corrections rather than being a real correction itself. It goes on and on with more filler text to push it well past the five hundred character limit used to filter out these false positives."

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e5-session.jsonl" << JSONL
{"type":"user","message":{"role":"user","content":"${long_text}"},"sessionId":"e2e5-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Continuing from before."}]},"sessionId":"e2e5-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Please continue."},"sessionId":"e2e5-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "E2E-5: continuation summary with keywords → exits 0 (filtered)"

  teardown_e2e_project "$test_dir"
}

e2e_5
echo ""

# =============================================================================
# E2E-6: False positive — teammate message → exit 0
# =============================================================================
echo "--- E2E-6: False positive — teammate message ---"

e2e_6() {
  local test_dir="$E2E_BASE/e2e6"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e6-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"<teammate-message teammate_id=\"auditor\">## Audit Complete\n✓ No issues found. wrong broken error not working.</teammate-message>"},"sessionId":"e2e6-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Got the audit results."}]},"sessionId":"e2e6-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Looks good, thanks."},"sessionId":"e2e6-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "E2E-6: teammate message with keywords → exits 0 (filtered)"

  teardown_e2e_project "$test_dir"
}

e2e_6
echo ""

# =============================================================================
# E2E-7: Custom keywords from rules file
# =============================================================================
echo "--- E2E-7: Custom keywords ---"

e2e_7() {
  local test_dir="$E2E_BASE/e2e7"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  # Custom rules with only "oops"
  local custom_rules_dir="$test_dir/skills/learn"
  mkdir -p "$custom_rules_dir"
  cat > "$custom_rules_dir/vorbit-learning-rules.md" << 'EOF'
# Test Rules
<!-- correction-keywords: oops -->
<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->
<!-- vorbit-learning-rules -->
EOF

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e7a-session.jsonl" << 'JSONL'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Deployed to production."}]},"sessionId":"e2e7a-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"oops, that was the wrong branch"},"sessionId":"e2e7a-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Rolling back."}]},"sessionId":"e2e7a-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="$test_dir" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-7: custom keyword 'oops' → exits 2"

  # Swap to "broken" — same transcript should NOT match
  cat > "$custom_rules_dir/vorbit-learning-rules.md" << 'EOF'
# Test Rules
<!-- correction-keywords: broken -->
<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->
<!-- vorbit-learning-rules -->
EOF

  rm -f "$HOME/.claude/projects/$slug"/e2e7a-session.jsonl "$ORIG_OUTPUT_FILE"
  cat > "$sessions_dir/e2e7b-session.jsonl" << 'JSONL'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Deployed to production."}]},"sessionId":"e2e7b-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"user","message":{"role":"user","content":"oops, that was the wrong branch"},"sessionId":"e2e7b-session","timestamp":"2026-02-21T10:01:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Rolling back."}]},"sessionId":"e2e7b-session","timestamp":"2026-02-21T10:02:00Z"}
JSONL

  exit_code=0
  echo "" | CLAUDE_PLUGIN_ROOT="$test_dir" bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-7: keyword swapped to 'broken', 'oops' no longer matches → exits 0"

  teardown_e2e_project "$test_dir"
}

e2e_7
echo ""

# =============================================================================
# E2E-8: Loop mode active → exit 0
# =============================================================================
echo "--- E2E-8: Loop mode active ---"

e2e_8() {
  local test_dir="$E2E_BASE/e2e8"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  mkdir -p "$test_dir/.claude"
  echo '{"active":true,"command":"implement","iteration":2}' > "$test_dir/.claude/.loop-state.json"

  local sessions_dir="$HOME/.claude/projects/$slug"
  cat > "$sessions_dir/e2e8-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Wrong, use const not var."},"sessionId":"e2e8-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed."}]},"sessionId":"e2e8-session","timestamp":"2026-02-21T10:01:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?

  assert_eq "0" "$exit_code" "E2E-8: loop active with correction keywords → exits 0 (skipped)"

  teardown_e2e_project "$test_dir"
}

e2e_8
echo ""

# =============================================================================
# E2E-9: Session dedup → exit 0 on re-run
# =============================================================================
echo "--- E2E-9: Session dedup ---"

e2e_9() {
  local test_dir="$E2E_BASE/e2e9"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  # Correction "Wrong" is at index 0
  cat > "$sessions_dir/e2e9-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Wrong, use SQLite not PostgreSQL."},"sessionId":"e2e9-session","timestamp":"2026-02-21T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Switching to SQLite."}]},"sessionId":"e2e9-session","timestamp":"2026-02-21T10:01:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  # First run: exits 2, writes per-learning ID to seen file (not to output file)
  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-9: first run → exits 2"
  assert_output_not_contains "$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)" "Session:" \
    "E2E-9: unprocessed-corrections.md not written on first run"

  # Second run: same message index already in SEEN_FILE → exits 0
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-9: second run same session → exits 0 (per-learning dedup)"

  teardown_e2e_project "$test_dir"
}

e2e_9
echo ""

# =============================================================================
# E2E-10: Multi-capture — new correction after first captured → exits 2 again
# =============================================================================
echo "--- E2E-10: Multi-capture ---"

e2e_10() {
  local test_dir="$E2E_BASE/e2e10"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  local transcript="$sessions_dir/e2e10-session.jsonl"

  # Transcript with one correction at index 2
  cat > "$transcript" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Set up the database."},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Using MySQL."}]},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, we use PostgreSQL."},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:02:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Switching to PostgreSQL."}]},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:03:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  # First run: captures correction at index 2 → exits 2
  local exit_code=0
  local output
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-10: first run → exits 2"
  assert_output_contains "$output" "Wrong, we use PostgreSQL" "E2E-10: first correction in output"

  # Append new correction at index 4 (simulates continued session after compaction or new turn)
  cat >> "$transcript" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Nope, check the connection string."},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:04:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed the connection string."}]},"sessionId":"e2e10-session","timestamp":"2026-02-22T10:05:00Z"}
JSONL

  # Second run: index 2 already captured, index 4 is new → exits 2
  exit_code=0
  output=$(echo "" | bash "$HOOK_SCRIPT" 2>/dev/null) || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-10: second run with new correction → exits 2 (multi-capture)"
  assert_output_contains "$output" "Nope, check the connection string" "E2E-10: new correction captured"
  assert_output_not_contains "$output" "Wrong, we use PostgreSQL" "E2E-10: first correction not re-captured"

  # Third run: all corrections captured → exits 0
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-10: third run after all captured → exits 0"

  teardown_e2e_project "$test_dir"
}

e2e_10
echo ""

# =============================================================================
# E2E-11: SEEN_FILE tab-separated format verification
# =============================================================================
echo "--- E2E-11: SEEN_FILE format ---"

e2e_11() {
  local test_dir="$E2E_BASE/e2e11"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  # Correction at index 0
  cat > "$sessions_dir/e2e11-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Wrong, use const not var."},"sessionId":"e2e11-session","timestamp":"2026-02-22T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Fixed."}]},"sessionId":"e2e11-session","timestamp":"2026-02-22T10:01:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-11: exits 2 on correction"

  # SEEN_FILE must have tab-separated format: session_id TAB f1 TAB msg_index
  local seen_line
  seen_line=$(cat "$ORIG_SEEN_FILE" 2>/dev/null | head -1)
  assert_eq $'e2e11-session\tf1\t0' "$seen_line" "E2E-11: SEEN_FILE has tab-separated per-learning ID"

  teardown_e2e_project "$test_dir"
}

e2e_11
echo ""

# =============================================================================
# E2E-12: Self-learning flows independently after correction capture
# =============================================================================
echo "--- E2E-12: Self-learning after correction ---"

e2e_12() {
  local test_dir="$E2E_BASE/e2e12"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  # Transcript: correction at index 2, self-learning at index 5
  cat > "$sessions_dir/e2e12-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Set up auth."},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Using JWT tokens."}]},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Wrong, we use sessions not JWT."},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:02:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Switching to session-based auth."}]},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:03:00Z"}
{"type":"user","message":{"role":"user","content":"Looks good."},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:04:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"ROOT_CAUSE: Assumed JWT when project uses sessions.\nRULE: Always check existing auth strategy before implementing.\nDESTINATION: /Users/ash/Projects/vorbit/.claude/rules/bash-scripts.md"}]},"sessionId":"e2e12-session","timestamp":"2026-02-22T10:05:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  # First run: correction at index 2 → exits 2, SEEN_FILE gets f1:2
  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "2" "$exit_code" "E2E-12: first run → exits 2 (correction captured)"

  # Second run: correction at index 2 already seen → Flow 1 passes through
  # Flow 2: self-learning at index 5 is new → captures it → writes to output
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-12: second run → exits 0 (self-learning captured by Flow 2)"
  assert_file_exists "$ORIG_OUTPUT_FILE" "E2E-12: output file created by Flow 2"

  local has_output
  has_output=$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)
  assert_output_contains "$has_output" "Always check existing auth strategy" "E2E-12: self-learning rule captured in output"
  assert_output_contains "$has_output" "msg:5" "E2E-12: message index 5 referenced in output"

  # Third run: both already captured → exits 0, no new output
  local output_before
  output_before=$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)
  exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-12: third run → exits 0 (all captured)"
  local output_after
  output_after=$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)
  assert_eq "$output_before" "$output_after" "E2E-12: no new entries written on third run"

  teardown_e2e_project "$test_dir"
}

e2e_12
echo ""

# =============================================================================
# E2E-13: unprocessed-corrections.md includes [msg:N] reference
# =============================================================================
echo "--- E2E-13: [msg:N] traceability in output ---"

e2e_13() {
  local test_dir="$E2E_BASE/e2e13"
  local slug
  slug=$(setup_e2e_project "$test_dir")
  cd "$test_dir"

  local sessions_dir="$HOME/.claude/projects/$slug"
  # Transcript with self-learning only (no correction keywords) at index 1
  cat > "$sessions_dir/e2e13-session.jsonl" << 'JSONL'
{"type":"user","message":{"role":"user","content":"Fix the login page."},"sessionId":"e2e13-session","timestamp":"2026-02-22T10:00:00Z"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"ROOT_CAUSE: Session tokens expire too fast due to hardcoded TTL.\nRULE: Always read TTL from config, never hardcode.\nDESTINATION: .claude/rules/auth.md"}]},"sessionId":"e2e13-session","timestamp":"2026-02-22T10:01:00Z"}
{"type":"user","message":{"role":"user","content":"Thanks."},"sessionId":"e2e13-session","timestamp":"2026-02-22T10:02:00Z"}
JSONL

  rm -f "$ORIG_OUTPUT_FILE" "$ORIG_SEEN_FILE"

  local exit_code=0
  echo "" | bash "$HOOK_SCRIPT" 2>/dev/null || exit_code=$?
  assert_eq "0" "$exit_code" "E2E-13: self-learning only → exits 0"

  local content
  content=$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null)
  assert_output_contains "$content" "Session:" "E2E-13: session block written"
  assert_output_contains "$content" "[msg:1]" "E2E-13: message index 1 referenced in learning header"
  assert_output_contains "$content" "hardcoded TTL" "E2E-13: learning content present"

  teardown_e2e_project "$test_dir"
}

e2e_13
echo ""

# =============================================================================
# RUN SUMMARY
# =============================================================================
echo "================================"
echo "Tests: $TESTS_RUN | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED"
echo "================================"

[[ $TESTS_FAILED -gt 0 ]] && exit 1 || exit 0
