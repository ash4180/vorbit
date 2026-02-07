---
name: learn
version: 2.0.0
description: Auto-captures session learnings and routes them after review. Triggered automatically at session end (capture mode) or manually via /vorbit:learn:review (review mode). Never blocks your primary task.
---

# Learn Skill

Two modes:
- **Capture mode** — triggered by stop hook at session end. Reflects, writes to pending file.
- **Review mode** — triggered by `/vorbit:learn:review`. Presents pending items, routes approved ones.

---

## Mode Detection

- If your context contains "capture mode" from the stop hook output → run **Capture Mode**
- If invoked via `/vorbit:learn:review` → run **Review Mode**

---

## Capture Mode

Fire-and-forget. Reflect on the session, write to pending, sync to Linear if threshold hit. Then stop.

### Step 1: Read Existing State

Read `$PROJECT_ROOT/.claude/learnings/pending.md` if it exists.

Extract from the META comment line:
- `ticket` — Linear issue ID (or NONE)
- `count` — current item count
- `last_synced` — last sync timestamp

Parse existing items: titles, types, frequencies.

If the file doesn't exist, start fresh.

### Step 2: Read Existing Rules

Before reflecting, read what's already documented:
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

**Filter ruthlessly:**
- NOT general programming knowledge (everyone knows this)
- NOT already in CLAUDE.md, `.claude/rules/`, or pending.md
- IS specific to this project, codebase, or team
- WOULD help a future agent working on this project

If nothing worth capturing → output "Nothing new to capture this session." and stop.

### Step 4: Classify Each Learning

| Type | When to use | Default target |
|---|---|---|
| `pattern` | A reusable approach or convention | CLAUDE.md > Learned Patterns |
| `knowledge` | A fact about the codebase or domain | `.claude/rules/{topic}.md` |
| `workflow` | A multi-step process that should be repeatable | `.claude/rules/workflows.md` |
| `error` | A failure mode and its fix | CLAUDE.md > Error Patterns |
| `improvement` | Something that should be fixed/built | New Linear issue |
| `insight` | A general observation | `.claude/rules/insights.md` |

**Title format:** Concise imperative statement (like a commit message).
- Good: "Use WAL mode for SQLite to prevent BUSY errors"
- Bad: "I found a bug with SQLite"

### Step 5: Deduplicate

For each candidate learning:
1. Compare title against existing pending items (fuzzy match — same concept counts)
2. If substantially similar → bump `Frequency` +1, update `Last seen` date
3. If genuinely new → add as new item

### Step 6: Enforce 20-Item Cap

- Count total items after dedup
- If count >= 20 → do NOT add new items
- Output warning: "Pending at capacity (20 items). Run /vorbit:learn:review to clear."

### Step 7: Write pending.md

Write `$PROJECT_ROOT/.claude/learnings/pending.md` using this format:

```markdown
# Pending Learnings

<!-- META: ticket=NONE count=3 last_synced=2026-02-07T12:00:00Z -->

### 1. Use WAL mode for SQLite to prevent BUSY errors
- **Type:** error
- **Frequency:** 5
- **First seen:** 2026-01-28
- **Last seen:** 2026-02-07
- **Context:** Concurrent writes cause BUSY errors. WAL mode fixes it.
- **Target:** CLAUDE.md > Error Patterns

### 2. Soft deletes on events table — never call .delete()
- **Type:** knowledge
- **Frequency:** 3
- **First seen:** 2026-02-01
- **Last seen:** 2026-02-06
- **Context:** Events use soft deletes with deletedAt timestamp.
- **Target:** .claude/rules/database.md

### 3. Deploy requires running migrations before starting server
- **Type:** workflow
- **Frequency:** 1
- **First seen:** 2026-02-07
- **Last seen:** 2026-02-07
- **Context:** Server crashes on startup if new migrations haven't run.
- **Target:** .claude/rules/workflows.md
```

Rules:
- Items are numbered sequentially (1, 2, 3...)
- META line must be updated: count reflects total items, last_synced is current timestamp
- Keep items sorted by frequency (highest first)

### Step 8: Sync to Linear

**If count >= 5 AND ticket is NONE:**
1. Call `list_teams` to get team ID
2. Call `create_issue` with:
   - Title: `Review pending learnings ({count} items)`
   - Description: Full table of all pending items
   - Label: `learning-review` (create via `create_issue_label` if it doesn't exist)
3. Update META in pending.md with the new ticket ID

**If count >= 5 AND ticket exists:**
1. Call `create_comment` on the existing ticket with this session's new/updated items
2. Call `update_issue` to update the description item count in the title

**If count < 5:**
- Skip Linear. Not enough signal yet.

**If Linear MCP tools fail:**
- Log the error in output. Continue without Linear. The pending file is the primary store. Never fail because of Linear.

### Step 9: Output Summary

```
Captured {N} learnings ({M} new, {K} updated). Total pending: {X}/20.
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
1. Call `list_comments` on the ticket
2. Parse comments for approval/rejection markers:
   - `approve #1` or `approve 1` → approve item 1
   - `reject #3` or `reject 3` → reject item 3
   - `approve all` → approve everything
   - `reject all` → reject everything
   - `route #2 to CLAUDE.md` → override default target for item 2
3. Pre-populate approval status for each item

### Step 3: Present Items

Display all pending items sorted by frequency (highest first):

```
{N} pending learnings to review:

1. [error] "Use WAL mode for SQLite" (x5 sessions) → CLAUDE.md > Error Patterns
2. [pattern] "Soft deletes on events table" (x3) → .claude/rules/database.md
3. [workflow] "Deploy requires migrations" (x2) → .claude/rules/workflows.md
4. [improvement] "Review skill needs cross-file check" (x1) → New Linear issue

Approve all? Or specify: approve 1,2,3 / reject 4
```

Use `AskUserQuestion` to get user's decision.

### Step 4: Route Approved Items

For each approved item, based on type and target:

**pattern → CLAUDE.md**
- Read CLAUDE.md
- Find or create "## Learned Patterns" section
- Append: `- {title}: {context}`

**knowledge → `.claude/rules/{topic}.md`**
- Determine topic from context (e.g., "database", "auth", "api")
- Read or create `.claude/rules/{topic}.md`
- Append the learning under a clear heading

**workflow → `.claude/rules/workflows.md`**
- Read or create `.claude/rules/workflows.md`
- Append the workflow steps

**error → CLAUDE.md**
- Read CLAUDE.md
- Find or create "## Error Patterns" section
- Append: `- {title}: {context}`

**improvement → Linear issue**
- Call `create_issue` with title and description from the learning
- Report the issue URL

**insight → `.claude/rules/insights.md`**
- Read or create `.claude/rules/insights.md`
- Append the insight

### Step 5: Clean Up

1. Remove all processed items (approved + rejected) from pending.md
2. Re-number remaining items sequentially
3. Update META: count, last_synced
4. If no items remain:
   - Delete pending.md
   - If Linear ticket exists: call `update_issue` to mark Done
5. If items remain:
   - Write updated pending.md
   - If Linear ticket exists: call `create_comment` noting what was processed

### Step 6: Report

```
Routed {N} learnings:
- {title} → CLAUDE.md (Learned Patterns)
- {title} → .claude/rules/database.md
Rejected {M} items.
{R} items remaining in pending.
```

---

## Examples

### Capture Example (session end)

Session: Implemented user authentication, hit a CORS error, discovered the project uses a custom middleware pattern.

Learnings captured:
```
### 1. CORS middleware must be registered before auth middleware
- **Type:** error
- **Frequency:** 1
- **First seen:** 2026-02-07
- **Last seen:** 2026-02-07
- **Context:** Auth middleware returns 401 before CORS headers are set, causing opaque browser errors. Order matters in middleware chain.
- **Target:** CLAUDE.md > Error Patterns
```

### Review Example

```
3 pending learnings to review:

1. [error] "CORS middleware before auth middleware" (x3) → CLAUDE.md > Error Patterns
2. [pattern] "Use /api/v2 prefix for all new endpoints" (x2) → .claude/rules/api.md
3. [improvement] "Add API versioning to prototype skill" (x1) → New Linear issue

> User: approve 1,2 / reject 3

Routed 2 learnings:
- "CORS middleware before auth middleware" → CLAUDE.md (Error Patterns)
- "Use /api/v2 prefix for all new endpoints" → .claude/rules/api.md
Rejected 1 item.
0 items remaining. Pending cleared. Linear ticket marked Done.
```
