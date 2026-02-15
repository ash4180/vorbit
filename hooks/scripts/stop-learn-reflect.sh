#!/bin/bash
# Stop hook - extracts corrections from session transcripts and installs learning rules.
# Fires at every session end when vorbit plugin is loaded.

set -euo pipefail

RULES_DIR="$HOME/.claude/rules"
RULES_FILE="$RULES_DIR/vorbit-learning.md"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")}"
RULES_SOURCE="$PLUGIN_ROOT/hooks/scripts/vorbit-learning-rules.md"
RULES_MARKER="vorbit-learning-rules"
OUTPUT_FILE="$RULES_DIR/unprocessed-corrections.md"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Consume stdin (stop hook protocol)
cat > /dev/null

# --- One-Time Setup: Install rules file as symlink ---
if ! grep -q "$RULES_MARKER" "$RULES_FILE" 2>/dev/null; then
  mkdir -p "$RULES_DIR"
  if [[ -f "$RULES_SOURCE" ]]; then
    ln -sf "$RULES_SOURCE" "$RULES_FILE"
  else
    cat > "$RULES_FILE" << 'RULES_EOF'
# Vorbit: Real-Time Learning Triggers

Watch for these patterns during every session. When detected, follow the learn skill's Correction Capture mode.

## When to Trigger

1. **User correction detected** — user says: "no", "wrong", "that's not right", "error", "still error", "not working", "broken", "nope", "roll back", "revert"
2. **Repeated failure** — you tried the same approach 2-3 times and it still fails
3. **Both conditions present** AND you then find a fix that works

## What to Do

After fixing the problem:
1. Use `AskUserQuestion` to ask if user wants root cause analysis
2. If yes: determine if the root cause is unclear CLAUDE.md, missing knowledge, skill gap, or script bug
3. Use `AskUserQuestion` to confirm the exact file path and content before writing
4. Write the learning to the confirmed location
5. Resume the primary task

Never skip user confirmation. Never write without asking. Always present the exact content you plan to write.

<!-- vorbit-learning-rules -->
RULES_EOF
  fi
fi

# --- Loop Mode Check ---
LOOP_STATE="$PROJECT_ROOT/.claude/.loop-state.json"
if [[ -f "$LOOP_STATE" ]] && jq -e '.active == true' "$LOOP_STATE" > /dev/null 2>&1; then
  exit 0
fi

# --- Transcript Extraction ---

# Determine project slug (replace / with -)
PROJECT_SLUG=$(echo "$PROJECT_ROOT" | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/$PROJECT_SLUG"

# Find most recent transcript
TRANSCRIPT=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1) || true
if [[ -z "$TRANSCRIPT" ]]; then
  exit 0
fi

# Extract session ID from filename
SESSION_ID=$(basename "$TRANSCRIPT" .jsonl)
TIMESTAMP=$(date '+%d %b %Y')

# Extract keyword-matched user messages with preceding assistant context.
# Uses jq -s (slurp) to load the full JSONL into an array for index-based lookback.
# Performance: jq handles 10MB files in well under 2 seconds.
MATCHES=$(jq -rs '
  # Keep only user and assistant messages
  [.[] | select(.type == "user" or .type == "assistant")] |

  # Extract text from each message
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

  # Find user message indices, pair with preceding assistant text
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

  # Filter for correction keywords (case-insensitive)
  map(select(
    (.user_text | ascii_downcase) as $t |
    ($t | test("wrong|not right|not working|broken|nope|revert|roll back|actually|that.s not")) or
    ($t | test("\\bno,")) or
    ($t | test("remember|always|never|don.t|we use|should be|must be"))
  )) |

  # Cap at 50
  .[:50] |

  # Format output
  map(
    (if .assistant_text == "" then "" else "A: [\(.assistant_text)]\n" end) +
    "USER: \(.user_text)"
  ) |
  join("\n\n")
' "$TRANSCRIPT" 2>/dev/null || echo "")

# If no matches, exit without creating/modifying the file
if [[ -z "$MATCHES" ]]; then
  exit 0
fi

# Create output file header if it doesn't exist
if [[ ! -f "$OUTPUT_FILE" ]]; then
  cat > "$OUTPUT_FILE" << 'HEADER_EOF'
# Unprocessed Session Corrections

**Action required:** Classify each learning by scope (project vs
universal) and destination (CLAUDE.md vs .claude/rules/). Check
existing rules files before writing — append to matching topic
files, never create duplicates. Route using the absolute project
path in each block header. Delete this file after processing.

---

HEADER_EOF
fi

# Append this session's matches
cat >> "$OUTPUT_FILE" << SESSION_EOF
## Session: ${SESSION_ID} | Project: ${PROJECT_ROOT} | ${TIMESTAMP}

${MATCHES}

---

SESSION_EOF

exit 0
