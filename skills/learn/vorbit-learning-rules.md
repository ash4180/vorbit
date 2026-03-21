# Vorbit: Real-Time Learning Triggers

Watch for these patterns during every session. When detected, follow the learn skill's Correction Capture mode.

## When to Trigger

**Correction keywords** — any single word/phrase triggers Correction Capture:
"nope", "wrong", "that's not right", "still error", "not working", "broken", "roll back", "revert", "that's not how"

<!-- correction-keywords: nope,wrong,that's not right,still error,not working,broken,roll back,revert,that's not how -->

Repeated failure is NOT required. One correction = one trigger.

**Voluntary capture keywords** — triggers Voluntary Capture:
"remember this", "save this", "note this", "keep this", "don't forget this", "log this", "learn this"

<!-- voluntary-keywords: remember this,save this,note this,keep this,don't forget this,log this,learn this -->

## Stop-Hook Voluntary Capture Flow

When `~/.claude/rules/pending-capture.md` is in your context and contains a `[VORBIT:VOLUNTARY-CAPTURE]` block, the stop hook detected the user explicitly asking to save something during a previous session. Run this flow for each voluntary block:

**1. Read the Obsidian note**
- The block contains a path to the full Obsidian note (e.g., `~/Projects/Thinking-Labs/claude/projects/{project}/...`)
- Read the note for rich context — it has the full conversation segment, not a truncated snippet
- If context is still insufficient to understand what the user wanted to save → use `AskUserQuestion` to ask the user before classifying

**2. Analyze and fill in the Obsidian note**
Using the conversation context, the decision tree in SKILL.md Step 2, and `references/routing.md`:
- Fill `## Root Cause Analysis` — classify WHY this learning matters (e.g., "user-preference — project always uses sqlite3, never psycopg2")
- Fill `## Suggested Rule` — write a concise imperative rule ready to paste into the destination file (e.g., "Always use sqlite3 for database access in this project — never psycopg2 or other PostgreSQL drivers")
- Fill `## Destination` — the absolute path of the file to route to (e.g., `/Users/ash/Projects/myapp/.claude/rules/conventions.md`)
- Update YAML frontmatter: set `root_cause`, `rule`, `routed_to`

**3. Present via `AskUserQuestion`**
Show the filled analysis for confirmation:
- **Root cause** — the classification and explanation you wrote
- **Rule** — the imperative rule you wrote
- **Destination** — the file path you determined

**4. On approve:**
1. Write the rule to the destination file
2. Set `status: done` in the note's YAML frontmatter
3. Move the note based on `routed_to`:
   - Universal destination (`~/.claude/rules/...`) → move note to `~/Projects/Thinking-Labs/claude/universal/`
   - Project destination (`/path/to/project/...`) → move note to `~/Projects/Thinking-Labs/claude/projects/{destination-project}/`

**5. On reject** — set `status: cancelled` in the note's YAML frontmatter, do nothing else

Never skip `AskUserQuestion`. Never write without user confirmation. Always show the exact root cause, rule, and destination before writing.

## Stop-Hook Correction Flow

When `~/.claude/rules/pending-capture.md` is in your context and contains a `[VORBIT:CORRECTION-CAPTURE]` block, the stop hook detected correction keywords from the previous session. Run this flow:

**1. Read the Obsidian note**
- The block contains a path to the full Obsidian note
- Read the note for rich context — the `## Conversation Context` section has what happened
- If context is still insufficient to understand what happened → use `AskUserQuestion` to ask the user before classifying

**2. Consolidate**
- If multiple blocks point to notes about the **same underlying error**, treat them as ONE learning
- Derive a single root cause, rule, and destination covering all of them

**3. Analyze and fill in the Obsidian note**
Using the conversation context, the decision tree in SKILL.md Step 2, and `references/routing.md`:
- Fill `## Root Cause Analysis` — explain WHY this happened and classify (e.g., "tool-behavior — Pencil silently drops per-side padding properties")
- Fill `## Suggested Rule` — write a concise imperative rule ready to paste into the destination file (e.g., "Use padding: N or padding: [t,r,b,l] in Pencil — paddingTop/paddingLeft/paddingRight/paddingBottom are silently dropped")
- Fill `## Destination` — the absolute path of the file to route to (e.g., `~/.claude/rules/tool-quirks.md`)
- Update YAML frontmatter: set `root_cause`, `rule`, `routed_to`

**4. Present via `AskUserQuestion`**
Show the filled analysis for confirmation:
- **Root cause** — the classification and explanation you wrote
- **Rule** — the imperative rule you wrote
- **Destination** — the file path you determined

**5. On approve:**
1. Write the rule to the destination file
2. Set `status: done` in the note's YAML frontmatter
3. Move the note based on `routed_to`:
   - Universal destination (`~/.claude/rules/...`) → move note to `~/Projects/Thinking-Labs/claude/universal/`
   - Project destination (`/path/to/project/...`) → move note to `~/Projects/Thinking-Labs/claude/projects/{destination-project}/`

**6. On reject** — set `status: cancelled` in the note's YAML frontmatter, do nothing else

Never skip `AskUserQuestion`. Never write without user confirmation. Always show the exact root cause, rule, and destination before writing.

## After All Blocks Are Processed

Once every block in `pending-capture.md` has been handled (all CORRECTION and VOLUNTARY types) — delete the source file at `~/Projects/Thinking-Labs/claude/pending-capture.md`. The symlink at `~/.claude/rules/pending-capture.md` will be cleaned up automatically by the next stop hook run.

## Real-Time Correction Capture (mid-session)

After fixing the problem:
1. Use `AskUserQuestion` to ask if user wants root cause analysis
2. If yes: use the decision tree in SKILL.md Step 2 to classify. If context is unclear → ask the user.
3. Use `AskUserQuestion` to confirm the exact file path and content before writing
4. Write the learning to the confirmed location
5. Write/update the Obsidian note per SKILL.md Step 5
6. Resume the primary task

Never skip user confirmation. Never write without asking. Always present the exact content you plan to write.

<!-- vorbit-learning-rules -->
