---
name: learn
version: 7.0.0
description: Real-time correction capture and digest processing. Correction capture triggers mid-session on single keyword. Digest processing routes extracted corrections from stop hook to project rules files.
---

# Learn Skill

Two modes:
- **Correction Capture** — always-on during sessions. Triggers when user corrects the agent and the agent finds a fix.
- **Digest Processing** — processes `~/.claude/rules/unprocessed-corrections.md` when present in context. Routes learnings to correct files.

## References

Detailed specs live in `references/` within this skill's directory. Glob for `**/skills/learn/references/` to resolve the path. Read them when instructed at specific steps below.

| File | Contains |
|---|---|
| `references/format.md` | Scope classification table, unprocessed-corrections.md format, examples |
| `references/routing.md` | Routing table by scope, absolute path routing, Cross-Reference Rule |
| `references/consolidation.md` | Document consolidation rules for `.claude/rules/` files |
| `references/routing.md` | Routing table, step-by-step groups, plugin root resolution, Cross-Reference Rule |

---

## Mode Detection

Both `pending-capture.md` and `unprocessed-corrections.md` live in `~/.claude/rules/`, which Claude Code auto-loads into every session. That's why their content appears in your context without the user doing anything — the stop hook writes to these files and the next session picks them up automatically.

- If your context contains `pending-capture.md` content → run the **Stop-Hook Correction/Voluntary Flow** from `vorbit-learning-rules.md` for each block, then delete the file. On approve, write directly to the destination file (one review, no intermediate step).
- If your context contains `unprocessed-corrections.md` content → run **Digest Processing** (this only appears from Flow 2: self-discovered learnings that the stop hook wrote directly)
- If invoked via `/vorbit:learn:checkmemory` → run **Digest Processing**
- If user correction detected mid-session → run **Correction Capture**
- If user says "remember this", "save this", "note this", etc. → run **Voluntary Capture**

**Priority rule:** `pending-capture.md` processing runs first, before anything else. If digest is also in context, run Digest Processing after pending-capture.md is handled.

---

## Correction Capture (Always-On)

This mode runs continuously during every session via the injected rules file. NOT invoked manually.

### Trigger Conditions

Any **single** correction keyword from the user is enough:
"nope", "wrong", "that's not right", "still error", "not working", "broken", "roll back", "revert", "that's not how"

Repeated failure is NOT required. One correction = one trigger.

### After Finding the Fix

Once the problem is resolved (build passes, test passes, user confirms):

**Step 1:** Use `AskUserQuestion`: "I just fixed an issue. Want me to analyze the root cause?"
- "Yes, analyze it" → Step 2
- "No, move on" → stop, resume primary task

**Step 2: Analyze root cause**

First determine scope — does this learning apply only to this project, or to all projects?

**Project-specific** (codebase facts, project rules, skill/script bugs):

| Root cause | Meaning |
|---|---|
| `claude-md` | CLAUDE.md is missing a rule that would have prevented the error |
| `knowledge` | `.claude/rules/` is missing a fact about the codebase |
| `skill` | A skill's SKILL.md has unclear or incomplete instructions |
| `script` | A hook script has a bug or missing logic |
| `general` | Agent reasoning error — no documentation fix needed |

**Universal** (agent behavior that applies across all projects):

| Root cause | Meaning |
|---|---|
| `agent-mistake` | Agent made a reasoning error that would recur in any project |
| `user-preference` | User has a workflow or communication preference |
| `tool-behavior` | A tool or MCP service behaves unexpectedly |

**Step 3:** Use `AskUserQuestion` to present: what went wrong, root cause category, proposed file + content.
- "Approve" → write it
- "Edit path" → user specifies a different file
- "Skip" → don't write anything

**Step 4: Write the learning**

Project-specific:
- **claude-md** → Read CLAUDE.md, find/create Learned Patterns or Error Patterns section, append
- **knowledge** → Read `references/consolidation.md` first. Determine topic, read/create rules file, append. Then apply the Cross-Reference Rule from `references/routing.md` to add a link in the project's CLAUDE.md under `## Knowledge Base`.
- **skill** → Read `references/routing.md` Group D to resolve plugin path. Read skill file, add minimum needed
- **script** → Read `references/routing.md` Group D to resolve plugin path. Read script, fix the bug

Universal:
- **agent-mistake** → Read `references/consolidation.md` first. Read or create `~/.claude/rules/agent-behavior.md`, append
- **user-preference** → Read `references/consolidation.md` first. Read or create `~/.claude/rules/user-preferences.md`, append
- **tool-behavior** → Read `references/consolidation.md` first. Read or create `~/.claude/rules/tool-quirks.md`, append

**Step 5:** Resume primary task. Don't linger on the learning.

---

## Voluntary Capture (Always-On)

Triggers when the user explicitly asks to save something: "remember this", "save this", "note this", "keep this", "don't forget this", "log this".

**Step 1:** Use `AskUserQuestion` to confirm what to save and classify it:
- What is the learning? (summarize in one line if unclear)
- Is it project-specific or universal (applies across all projects)?
- Root cause category (same table as Correction Capture Step 2)

**Step 2:** Propose file + content using `AskUserQuestion`:
- "Approve" → write it
- "Edit path" → user specifies a different file
- "Skip" → don't write anything

**Step 3:** Write using the same routing as Correction Capture Step 4.

**Step 4:** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/learn/hooks/mark_voluntary_seen.py` to mark this session's voluntary keyword messages as seen. This prevents the stop hook from re-prompting at session end for the same capture you just handled. Then resume primary task.

---

## Digest Processing

Processes `~/.claude/rules/unprocessed-corrections.md` — the digest of corrections extracted by the stop hook at session end.

### Step 1: Read the Digest

The file is already in your context (loaded eagerly from `~/.claude/rules/`). Parse it:
- Each `## Session:` block contains one or more corrections from one session
- Block header has: session ID, absolute project path, timestamp
- Each entry is pre-structured with `**Root cause:**`, `**Rule:**`, and `**Destination:**` — already classified by the agent at capture time

If the file is not present or empty → "No corrections to process." Stop.

### Step 2: Check for Duplicates

For each unique project path in the digest:
1. Read `{project_path}/CLAUDE.md` — scan for "Learned Patterns" and "Error Patterns"
2. Glob `{project_path}/.claude/rules/*.md` — scan existing knowledge files
3. Glob `~/.claude/rules/*.md` — scan universal rules

Skip any entry whose rule is already captured in these files.

### Step 3: Present for Approval

Use `AskUserQuestion` to present all entries. Each entry already has its destination — show it directly:

```
Found {N} entries from {M} sessions:

1. "Always validate transcript parsing against a real JSONL sample"
   → /path/to/project/.claude/rules/bash-scripts.md
2. "Don't assume test failures mean code is wrong"
   → ~/.claude/rules/agent-behavior.md

Approve all? Or specify: approve 1 / reject 2
```

- "Approve all" → route all
- "Approve N,N" → route selected, discard rest
- "Reject all" → delete digest without routing

### Step 4: Route Approved Items

Read `references/consolidation.md` before writing to any file.

Write each approved entry to its `**Destination:**` path using the absolute path from the entry. If the path is relative, resolve it against the project path from the block header. If the destination is a `skill-fix` or `script-fix` path, read `references/routing.md` Group D to resolve the plugin root first.

### Step 5: Clean Up

Delete `~/.claude/rules/unprocessed-corrections.md` after processing all blocks.

### Step 6: Report

```
Routed {N} learnings:
- "Always validate transcript parsing..." → /path/to/project/.claude/rules/bash-scripts.md
- "Don't assume test failures..." → ~/.claude/rules/agent-behavior.md
Rejected {M} items.
Digest cleared.
```
