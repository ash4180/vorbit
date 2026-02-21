#!/bin/bash
# Stop hook - detects correction keywords in user messages and continues session.
# Falls back to self-discovered learning extraction when no keywords found.
# Reads all config from vorbit-learning-rules.md — nothing hardcoded.

set -uo pipefail
trap 'exit 0' ERR

RULES_DIR="$HOME/.claude/rules"
RULES_FILE="$RULES_DIR/vorbit-learning.md"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")}"
RULES_SOURCE="$PLUGIN_ROOT/skills/learn/vorbit-learning-rules.md"
RULES_MARKER="vorbit-learning-rules"
OUTPUT_FILE="$RULES_DIR/unprocessed-corrections.md"
SEEN_FILE="$RULES_DIR/.seen-correction-sessions"
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

# --- Locate transcript ---
PROJECT_SLUG=$(echo "$PROJECT_ROOT" | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/$PROJECT_SLUG"

TRANSCRIPT=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1) || true
if [[ -z "$TRANSCRIPT" ]]; then
  exit 0
fi

SESSION_ID=$(basename "$TRANSCRIPT" .jsonl)

# --- FLOW 1: Correction keyword detection ---
# Skip if already processed this session (prevents exit-2 loop)
KEYWORDS_CSV=$(sed -n 's/.*<!-- correction-keywords: \(.*\) -->.*/\1/p' "$RULES_SOURCE" | head -1)

if [[ -n "$KEYWORDS_CSV" ]] && ! grep -qF "$SESSION_ID" "$SEEN_FILE" 2>/dev/null; then
  # Build regex: CSV to pipe-separated with word boundaries, case-insensitive
  # \b ensures "no" matches standalone word only, not inside "not", "know", "cannot"
  KEYWORD_REGEX=$(echo "$KEYWORDS_CSV" | sed 's/,/\\b|\\b/g')
  KEYWORD_REGEX="\\b${KEYWORD_REGEX}\\b"

  # Extract user messages, filter false positives, scan for keywords
  # content may be a plain string or an array of {type,text} blocks — handle both
  MATCHING_INDICES=$(jq -rs --arg regex "$KEYWORD_REGEX" '
    def extract_text:
      if type == "string" then .
      elif type == "array" then [.[] | select(.type == "text") | .text] | join("\n")
      else "" end;
    [range(length)] as $indices |
    [., $indices] | transpose |
    map(
      . as [$msg, $idx] |
      ($msg.message.content | extract_text) as $text |
      select(
        $msg.type == "user" and
        ($text | length) > 0 and
        ($text | length) <= 500 and
        ($text | test("<teammate-message") | not) and
        ($text | test($regex; "i"))
      ) |
      $idx
    )
  ' "$TRANSCRIPT" 2>/dev/null || echo "[]")

  MATCH_COUNT=$(echo "$MATCHING_INDICES" | jq 'length' 2>/dev/null || echo "0")

  if [[ "$MATCH_COUNT" -gt 0 ]]; then
    # Build context: preceding assistant + user correction + following assistant
    # Assistant messages are identified by message.role == "assistant" (not entry.type)
    CONTEXT=$(jq -rs --argjson indices "$MATCHING_INDICES" '
      def extract_text:
        if type == "string" then .
        elif type == "array" then [.[] | select(.type == "text") | .text] | join("\n")
        else "" end;
      . as $messages |
      [$indices[] |
        . as $idx |
        (if $idx > 0 and $messages[$idx - 1].message.role == "assistant" then
          "A: [" + ($messages[$idx - 1].message.content | extract_text | .[0:200]) + "]"
        else empty end),
        "USER: " + ($messages[$idx].message.content | extract_text),
        (if $idx + 1 < ($messages | length) and $messages[$idx + 1].message.role == "assistant" then
          "A: [" + ($messages[$idx + 1].message.content | extract_text | .[0:200]) + "]"
        else empty end),
        ""
      ] | join("\n")
    ' "$TRANSCRIPT" 2>/dev/null || echo "")

    # Mark session as seen — separate file keeps unprocessed-corrections.md clean
    mkdir -p "$RULES_DIR"
    echo "$SESSION_ID" >> "$SEEN_FILE"

    printf '[VORBIT:CORRECTION-CAPTURE] Stop hook found correction keywords. Run the Stop-Hook Correction Flow from vorbit-learning-rules.md.\n\n%s' "$CONTEXT"
    exit 2
  fi
fi

# --- FLOW 2: Self-discovered learning extraction (no correction keywords found) ---
# Skip if session already recorded
if grep -qF "## Session: ${SESSION_ID}" "$OUTPUT_FILE" 2>/dev/null; then
  exit 0
fi

# Read field names from rules file
FIELDS_DEF=$(sed -n 's/.*<!-- learning-fields: \(.*\) -->.*/\1/p' "$RULES_SOURCE" | head -1)
if [[ -z "$FIELDS_DEF" ]]; then
  exit 0
fi

F1=$(echo "$FIELDS_DEF" | cut -d',' -f1)
F2=$(echo "$FIELDS_DEF" | cut -d',' -f2)
F3=$(echo "$FIELDS_DEF" | cut -d',' -f3)

TIMESTAMP=$(date '+%d %b %Y')

# Quick check: any learning entries in this session?
HAS_LEARNING=$(jq -rs --arg f1 "${F1}: " \
  '[.[] | select(.type == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | map(select(contains($f1))) | length' \
  "$TRANSCRIPT" 2>/dev/null || echo "0")

if [[ "$HAS_LEARNING" == "0" ]]; then
  exit 0
fi

# Extract and format learning entries
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

# Write structured output — only real content reaches this point
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
