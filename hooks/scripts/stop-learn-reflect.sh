#!/bin/bash
# Stop hook - extracts self-discovered learnings from session transcript.
# Agent writes labeled fields (ROOT_CAUSE, RULE, DESTINATION) in response.
# Script reads field names from vorbit-learning-rules.md — nothing hardcoded.
# Only triggers when labeled fields are found. Script controls output format.

set -euo pipefail

RULES_DIR="$HOME/.claude/rules"
RULES_FILE="$RULES_DIR/vorbit-learning.md"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")}"
RULES_SOURCE="$PLUGIN_ROOT/skills/learn/vorbit-learning-rules.md"
RULES_MARKER="vorbit-learning-rules"
OUTPUT_FILE="$RULES_DIR/unprocessed-corrections.md"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Consume stdin (stop hook protocol)
cat > /dev/null

# Can't function without the rules source
if [[ ! -f "$RULES_SOURCE" ]]; then
  exit 0
fi

# --- One-Time Setup: symlink rules file into ~/.claude/rules/ ---
if ! grep -q "$RULES_MARKER" "$RULES_FILE" 2>/dev/null; then
  mkdir -p "$RULES_DIR"
  ln -sf "$RULES_SOURCE" "$RULES_FILE"
fi

# --- Skip during active loop ---
LOOP_STATE="$PROJECT_ROOT/.claude/.loop-state.json"
if [[ -f "$LOOP_STATE" ]] && jq -e '.active == true' "$LOOP_STATE" > /dev/null 2>&1; then
  exit 0
fi

# --- Read field names from rules file (not hardcoded) ---
FIELDS_DEF=$(sed -n 's/.*<!-- learning-fields: \(.*\) -->.*/\1/p' "$RULES_SOURCE" | head -1)
if [[ -z "$FIELDS_DEF" ]]; then
  exit 0
fi

F1=$(echo "$FIELDS_DEF" | cut -d',' -f1)  # e.g. ROOT_CAUSE
F2=$(echo "$FIELDS_DEF" | cut -d',' -f2)  # e.g. RULE
F3=$(echo "$FIELDS_DEF" | cut -d',' -f3)  # e.g. DESTINATION

# --- Locate transcript ---
PROJECT_SLUG=$(echo "$PROJECT_ROOT" | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/$PROJECT_SLUG"

TRANSCRIPT=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1) || true
if [[ -z "$TRANSCRIPT" ]]; then
  exit 0
fi

SESSION_ID=$(basename "$TRANSCRIPT" .jsonl)
TIMESTAMP=$(date '+%d %b %Y')

# --- Quick check: any learning entries in this session? ---
HAS_LEARNING=$(jq -rs --arg f1 "${F1}: " \
  '[.[] | select(.type == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | map(select(contains($f1))) | length' \
  "$TRANSCRIPT" 2>/dev/null || echo "0")

if [[ "$HAS_LEARNING" == "0" ]]; then
  exit 0
fi

# --- Skip if session already recorded ---
if grep -qF "## Session: ${SESSION_ID}" "$OUTPUT_FILE" 2>/dev/null; then
  exit 0
fi

# --- Extract and format learning entries (script controls output format) ---
LEARNINGS=$(jq -rs \
  --arg f1 "${F1}: " \
  --arg f2 "${F2}: " \
  --arg f3 "${F3}: " '
  [.[] | select(.type == "assistant")] |
  [.[] | .message.content[]? | select(.type == "text") | .text] |
  map(select(contains($f1) and contains($f2) and contains($f3))) |
  map({
    root_cause: (split($f1)[1] | split("\n")[0]),
    rule:       (split($f2)[1] | split("\n")[0]),
    dest:       (split($f3)[1] | split("\n")[0])
  }) |
  map(
    "## " + (.root_cause | split(".")[0] | .[0:80]) + "\n" +
    "**Root cause:** " + .root_cause + "\n" +
    "**Rule:** " + .rule + "\n" +
    "**Destination:** " + .dest
  ) |
  join("\n\n")
' "$TRANSCRIPT" 2>/dev/null || echo "")

if [[ -z "$LEARNINGS" ]]; then
  exit 0
fi

# --- Write structured output ---
if [[ ! -f "$OUTPUT_FILE" ]]; then
  cat > "$OUTPUT_FILE" << 'HEADER_EOF'
# Unprocessed Session Corrections

**Action required:** Route each entry to its destination file.
Check existing rules files before writing — append to matching topic
files, never create duplicates. Use the absolute project path in each
block header for routing. Delete this file after processing.

---

HEADER_EOF
fi

cat >> "$OUTPUT_FILE" << SESSION_EOF
## Session: ${SESSION_ID} | Project: ${PROJECT_ROOT} | ${TIMESTAMP}

${LEARNINGS}

---

SESSION_EOF

exit 0
