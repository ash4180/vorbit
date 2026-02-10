---
name: learn
version: 6.0.0
description: Real-time and session-end learning capture. Correction capture triggers mid-session when the agent detects user corrections and finds a fix. Also supports session-end capture and manual review.
---

# Learn Skill

Three modes:
- **Correction capture** — always-on during sessions. Triggers when user corrects the agent and the agent finds a fix.
- **Capture mode** — triggered by stop hook at session end. Reflects, writes to pending file. Supports `--backfill N` to also mine past transcripts.
- **Review mode** — triggered by `/vorbit:learn:review`. Presents pending items, routes approved ones.

## References

Detailed specs live in `references/` within this skill's directory. Glob for `**/skills/learn/references/` to resolve the path. Read them when instructed at specific steps below.

| File | Contains |
|---|---|
| `references/format.md` | Classification table, pending.md format spec, examples |
| `references/routing.md` | Routing table, Groups A-E, Cross-Reference Rule |
| `references/consolidation.md` | Document consolidation rules for `.claude/rules/` files |
| `references/scopes.md` | File scope table, plugin root resolution |

---

## Mode Detection

- If your context contains "correction capture" from the rules file → run **Correction Capture**
- If your context contains "capture mode" from the stop hook output → run **Capture Mode**
- If invoked via `/vorbit:learn:review` → run **Review Mode**

---

## Correction Capture (Always-On)

This mode runs continuously during every session via the injected rules file. NOT invoked manually.

### Trigger Conditions

**Signal 1: User correction keywords**
User says: "no", "wrong", "that's not right", "error", "still error", "not working", "broken", "nope", "roll back", "revert", "that's broken", "why did you..."

**Signal 2: Repeated failure**
Same approach tried 2-3 times, still fails.

**When BOTH signals are present**, start tracking. Continue working on the fix.

### After Finding the Fix

Once the problem is resolved (build passes, test passes, user confirms):

**Step 1:** Use `AskUserQuestion`: "I just fixed an issue after some failed attempts. Want me to analyze the root cause?"
- "Yes, analyze it" → Step 2
- "No, move on" → stop, resume primary task

**Step 2: Analyze root cause**

| Root cause | Meaning |
|---|---|
| `claude-md` | CLAUDE.md is missing a rule that would have prevented the error |
| `knowledge` | `.claude/rules/` is missing a fact about the codebase |
| `skill` | A skill's SKILL.md has unclear or incomplete instructions |
| `script` | A hook script has a bug or missing logic |
| `general` | Agent reasoning error — no documentation fix needed |

**Step 3:** Use `AskUserQuestion` to present: what went wrong, root cause category, proposed file + content.
- "Approve" → write it
- "Edit path" → user specifies a different file
- "Skip" → don't write anything

**Step 4: Write the learning**

- **claude-md** → Read CLAUDE.md, find/create Learned Patterns or Error Patterns section, append
- **knowledge** → Read `references/consolidation.md` first. Determine topic, read/create rules file, append
- **skill** → Read `references/scopes.md` to resolve plugin path. Read skill file, add minimum needed
- **script** → Read `references/scopes.md` to resolve plugin path. Read script, fix the bug

**Step 5:** Resume primary task. Don't linger on the learning.

---

## Capture Mode

Fire-and-forget. Reflect on the session, write to pending, sync to Linear if threshold hit. Then stop.

### Step 1: Read Existing State

Read `$PROJECT_ROOT/.claude/learnings/pending.md` if it exists. Extract META: `ticket`, `count`, `last_synced`. Parse existing items. If file doesn't exist, start fresh.

### Step 2: Read Existing Rules

1. Read `CLAUDE.md` — scan for "Learned Patterns" and "Error Patterns" sections
2. Check `.claude/rules/` for any existing knowledge files
3. These are already-approved learnings — do NOT re-capture them

### Step 3: Reflect on This Session

Think about what happened:
- What **patterns** did you discover or follow?
- What **errors** did you hit and how were they solved?
- What **conventions** did you learn about the codebase?
- What **workflows** should be standardized?
- What **improvements** would help future sessions?
- What **skill/hook issues** did you hit? Did any skill instructions lead you astray, miss a case, or produce wrong behavior?
- What **corrections** did the user make? (see below)

**User corrections are high-priority learnings.** Scan the conversation for moments where the user:
- Said something was wrong ("that's not right", "no", "actually it should be...")
- Rejected an approach or suggestion
- Corrected a misunderstanding about the codebase, domain, or workflow
- Pushed back on a design decision

**Filter ruthlessly:**
- NOT general programming knowledge (everyone knows this)
- NOT already in CLAUDE.md, `.claude/rules/`, or pending.md
- IS specific to this project, codebase, or team
- WOULD help a future agent working on this project

If nothing worth capturing from the current session AND no `--backfill` flag → output "Nothing new to capture this session." and stop.

### Step 3b: Backfill Past Transcripts (optional)

**Only runs if `$ARGUMENTS` contains `--backfill`.**  If not present, skip to Step 4.

1. Determine project path slug: replace `/` with `-` in `$PROJECT_ROOT`
2. List transcripts in `~/.claude/projects/{slug}/*.jsonl`, sort by modification date (newest first)
3. If `$ARGUMENTS` contains a number N after `--backfill`, process last N sessions. Default: 10.
4. If `$PROJECT_ROOT/.claude/learnings/backfill-state.md` exists, read it and skip already-processed transcripts.
5. For each transcript, use the Task tool to dispatch a **general-purpose** agent that:
   - Reads the JSONL file using Bash: `jq -r 'select(.role == "user" or .role == "assistant") | select(.content != null) | if (.content | type) == "array" then (.content[] | select(.type == "text") | .text) else .content end' <file> 2>/dev/null | head -500`
   - If that fails, try: `jq -r '.message // empty' <file> 2>/dev/null | head -500`
   - Extracts project-specific learnings (errors, patterns, user corrections, domain knowledge, workflows)
   - Filters ruthlessly — only project-specific, not general knowledge
   - Returns findings formatted as:
     ```
     ### [Title]
     - **Type:** error | pattern | knowledge | workflow | review-rule
     - **Context:** [what happened and why it matters]
     ```
6. **Dispatch up to 4 agents in parallel.** Wait for all to complete.
7. Merge backfill findings with current-session findings. Continue to Step 4.

### Step 4: Classify Each Learning

Read `references/format.md` for the classification table and type definitions. Classify each learning.

### Step 5: Deduplicate

1. Compare title against existing pending items (fuzzy match — same concept counts)
2. If substantially similar → bump `Frequency` +1, update `Last seen` date
3. If genuinely new → add as new item

### Step 6: Enforce 20-Item Cap

- If count >= 20 → do NOT add new items
- Output: "Pending at capacity (20 items). Run /vorbit:learn:review to clear."

### Step 7: Write pending.md

Read `references/format.md` for the pending.md format spec. Write `$PROJECT_ROOT/.claude/learnings/pending.md`.

Rules: items numbered sequentially, META updated, dates human-readable (`7 Feb 2026`), sorted by frequency (highest first).

### Step 8: Sync to Linear

**If count >= 15 AND ticket is NONE:**

Use `AskUserQuestion`: "{count} learnings are pending review. Want me to create a Linear ticket to track this?"
- "Yes, assign to me" → create ticket assigned to current user
- "Yes, assign to someone else" → follow up asking for assignee name
- "No, I'll review later" → skip Linear

If approved:
1. `list_teams` → get team ID
2. `list_users` → find assignee
3. `create_issue`: title=`Review pending learnings ({count} items)`, description=full table, label=`learning-review`, assignee=selection
4. Update META with ticket ID

**If count >= 15 AND ticket exists:**
1. `create_comment` with this session's new/updated items
2. `update_issue` to update count in title

**If count < 15:** Skip. Pending file is sufficient.

**If Linear MCP tools fail:** Log error, continue. Pending file is the primary store.

### Step 9: Output Summary

```
Captured {N} learnings ({M} new, {K} updated). Total pending: {X}/20.
```

If `--backfill` was used, also include:
```
Backfill: processed {N} transcripts.
```

Then stop. The stop hook will fire again and exit cleanly (state file exists → exit 0).

---

## Review Mode

Interactive. Present pending items, user approves/rejects, route to correct files.

### Step 1: Load State

1. Read `$PROJECT_ROOT/.claude/learnings/pending.md`
2. If file doesn't exist or has no items → "Nothing to review." Stop.
3. Extract META: ticket ID, count

### Step 2: Check Linear for Approvals

If a ticket ID exists:
1. `list_comments` on the ticket
2. Parse comments: `approve #1`, `reject #3`, `approve all`, `reject all`, `route #2 to CLAUDE.md`
3. Pre-populate approval status for each item

### Step 3: Present Items

Display all pending items sorted by frequency (highest first):

```
{N} pending learnings to review:

1. [error] "Use WAL mode for SQLite" (x5 sessions) → CLAUDE.md > Error Patterns
2. [pattern] "Soft deletes on events table" (x3) → .claude/rules/database.md

Approve all? Or specify: approve 1,2,3 / reject 4
```

Use `AskUserQuestion` to get user's decision.

### Step 4: Route Approved Items

Read `references/routing.md` for the full routing table and group instructions. Follow them.

Also read `references/consolidation.md` before creating any new knowledge files.

If routing any `skill-fix` or `script-fix` items, read `references/scopes.md` to resolve the plugin path.

### Step 5: Clean Up

1. Remove all processed items (approved + rejected) from pending.md
2. Re-number remaining items sequentially
3. Update META: count, last_synced
4. If no items remain → delete pending.md. If Linear ticket exists → `update_issue` to mark Done.
5. If items remain → write updated pending.md. If Linear ticket exists → `create_comment` noting processed items.
6. **Mark processed transcripts:** If any items originated from backfill, append processed transcript filenames to `$PROJECT_ROOT/.claude/learnings/backfill-state.md`. Never delete Claude Code's session files — they're user-scope.

### Step 6: Report

```
Routed {N} learnings:
- {title} → CLAUDE.md (Learned Patterns)
- {title} → .claude/rules/database.md
Rejected {M} items.
{R} items remaining in pending.
```
