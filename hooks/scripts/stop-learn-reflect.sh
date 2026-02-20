#!/bin/bash
# Stop hook - dumps recent session messages for agent-driven learning classification.
# Agent applies vorbit-learning-rules.md criteria to identify corrections.
# Fires at every session end when vorbit plugin is loaded.

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

# --- Locate transcript ---
PROJECT_SLUG=$(echo "$PROJECT_ROOT" | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/$PROJECT_SLUG"

TRANSCRIPT=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1) || true
if [[ -z "$TRANSCRIPT" ]]; then
  exit 0
fi

SESSION_ID=$(basename "$TRANSCRIPT" .jsonl)
TIMESTAMP=$(date '+%d %b %Y')

# --- Extract last 30 user messages with assistant context ---
# No keyword filtering — agent applies learn skill criteria to decide what matters.
# Structural noise removed: teammate messages and continuation summaries (>500 chars).
MESSAGES=$(jq -rs '
  [.[] | select(.type == "user" or .type == "assistant")] |

  [.[] | {
    type: .type,
    text: (
      if .type == "user" then
        (.message.content |
          if type == "string" then .
          elif type == "array" then
            [.[] | select(.type == "text") | .text] | join(" ")
          else "" end)
      else
        ([.message.content[]? | select(.type == "text") | .text] | join(" ") | .[:200])
      end
    )
  }] |

  . as $msgs |
  [range(length)] |
  map(select($msgs[.].type == "user")) |
  map(. as $i | {
    user_text: $msgs[$i].text,
    assistant_text: (
      if $i > 0 and $msgs[$i-1].type == "assistant" then $msgs[$i-1].text
      else "" end
    )
  }) |

  # Remove structural noise (not user corrections)
  map(select(.user_text | test("<teammate-message") | not)) |
  map(select(.user_text | length < 500)) |

  # Last 30 messages — agent decides which are corrections
  .[-30:] |

  map(
    (if .assistant_text == "" then "" else "A: [\(.assistant_text)]\n" end) +
    "USER: \(.user_text)"
  ) |
  join("\n\n")
' "$TRANSCRIPT" 2>/dev/null || echo "")

if [[ -z "$MESSAGES" ]]; then
  exit 0
fi

# --- Write output for agent ---
if [[ ! -f "$OUTPUT_FILE" ]]; then
  cat > "$OUTPUT_FILE" << 'HEADER_EOF'
# Unprocessed Session Corrections

**Action required:** Read each session block. Apply vorbit-learning-rules.md criteria
to identify corrections and learnings. Classify by scope and route to the correct file.
Delete this file after processing.

---

HEADER_EOF
fi

cat >> "$OUTPUT_FILE" << SESSION_EOF
## Session: ${SESSION_ID} | Project: ${PROJECT_ROOT} | ${TIMESTAMP}

${MESSAGES}

---

SESSION_EOF

exit 0
