---
name: learn
version: 8.0.0
description: Real-time correction capture with Obsidian-backed context storage. Correction capture triggers mid-session on single keyword. Corrections stored as structured Obsidian notes for accurate root cause analysis.
---

# Learn Skill

Two modes:
- **Correction Capture** — always-on during sessions. Triggers when user corrects the agent and the agent finds a fix.
- **Voluntary Capture** — triggers when user explicitly asks to save a learning.

## References

Detailed specs live in `references/` within this skill's directory. Glob for `**/skills/learn/references/` to resolve the path. Read them when instructed at specific steps below.

| File | Contains |
|---|---|
| `references/format.md` | Scope classification table, examples |
| `references/routing.md` | Routing table by scope, absolute path routing, Cross-Reference Rule |
| `references/consolidation.md` | Document consolidation rules for `.claude/rules/` files |

## Obsidian Vault

Corrections are stored as structured notes in the Obsidian vault at:
```
~/Projects/Thinking-Labs/claude/
  projects/{project-name}/    ← per-project corrections
  universal/                  ← cross-project corrections
  _corrections-index.md       ← Dataview query (live, not static)
```

The index uses a Dataview query that reads YAML frontmatter from all notes — no manual rows to maintain.

---

## Session-Start Scanning

At the start of every session, if `pending-capture.md` is in your context (symlinked from Obsidian vault):

1. Process each block — read the linked Obsidian note, analyze, classify, route
2. Check for **recurring patterns** — if the correction context resembles a previous correction for the same project, the learning wasn't effective. Flag to user.

---

## Mode Detection

`pending-capture.md` lives in the Obsidian vault (`~/Projects/Thinking-Labs/claude/`) and is symlinked into `~/.claude/rules/` for auto-loading. The stop hook writes to the Obsidian source; the symlink makes it appear in your context automatically.

- If your context contains `pending-capture.md` content → run the **Stop-Hook Correction/Voluntary Flow** from `vorbit-learning-rules.md` for each block, then delete the file
- If user correction detected mid-session → run **Correction Capture**
- If user says "remember this", "save this", "note this", etc. → run **Voluntary Capture**

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

**Step 2: Classify root cause**

First check the Obsidian notes in `~/Projects/Thinking-Labs/claude/projects/{project}/` — has this project had similar corrections before? If so, reference the past note when classifying.

Use this decision tree in order. Stop at the first match:

1. **Did a tool or MCP service behave unexpectedly?** (e.g., Pencil dropped a property, Figma MCP returned stale data)
   → `tool-behavior` (universal)

2. **Is this a user workflow or communication preference?** (e.g., "always run tests first", "don't auto-commit")
   → `user-preference` (universal)

3. **Did the agent make a reasoning error that would happen in ANY project?** (e.g., assumed a typo, didn't check console)
   → `agent-mistake` (universal)

4. **Is a skill's SKILL.md unclear or missing an instruction?**
   → `skill` (project)

5. **Does a hook script have a bug or missing logic?**
   → `script` (project)

6. **Is this a fact about the codebase that `.claude/rules/` should know?** (e.g., "events table uses soft deletes", "deploy requires migrations first")
   → `knowledge` (project)

7. **Would a rule in CLAUDE.md have prevented this error?** (e.g., "CORS middleware must be before auth")
   → `claude-md` (project)

8. **Not enough context to classify confidently?**
   → `unclear` — use `AskUserQuestion` to ask the user: "I can't determine the root cause with confidence. What went wrong?" Then reclassify with their answer.

9. **Agent reasoning error, no documentation fix needed**
   → `general` (nothing written)

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

**Step 5: Update Obsidian note**

If a pending Obsidian note exists for this correction (linked from `pending-capture.md`):
1. Read the note at its full path
2. Fill `## Root Cause Analysis` — explain WHY this happened and classify
3. Fill `## Suggested Rule` — write a concise imperative rule ready to paste into the destination file
4. Fill `## Destination` — the absolute path of the file to route to
5. Update YAML frontmatter: set `root_cause`, `rule`, `routed_to`, `status: done`
6. Move the note based on `routed_to`:
   - Universal destination (`~/.claude/rules/...`) → move to `~/Projects/Thinking-Labs/claude/universal/`
   - Project destination (`/path/to/project/...`) → move to `~/Projects/Thinking-Labs/claude/projects/{destination-project}/`

If this is a mid-session correction (no Obsidian note yet):
1. Determine scope from the destination path
2. Write note to the correct Obsidian directory:
   - Universal → `~/Projects/Thinking-Labs/claude/universal/`
   - Project → `~/Projects/Thinking-Labs/claude/projects/{destination-project}/`
3. Include all sections: Conversation Context (filled), Root Cause Analysis (filled), Suggested Rule (filled), Destination (filled)
4. Use the same YAML format with all fields filled

**Step 6:** Resume primary task. Don't linger on the learning.

---

## Voluntary Capture (Always-On)

Triggers when the user explicitly asks to save something: "remember this", "save this", "note this", "keep this", "don't forget this", "log this".

**Step 1:** Use `AskUserQuestion` to confirm what to save and classify it:
- What is the learning? (summarize in one line if unclear)
- Is it project-specific or universal (applies across all projects)?
- Root cause category (same decision tree as Correction Capture Step 2)

**Step 2:** Propose file + content using `AskUserQuestion`:
- "Approve" → write it
- "Edit path" → user specifies a different file
- "Skip" → don't write anything

**Step 3:** Write using the same routing as Correction Capture Step 4. Then update/create Obsidian note per Step 5.

**Step 4:** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/learn/hooks/mark_voluntary_seen.py` to mark this session's voluntary keyword messages as seen. This prevents the stop hook from re-prompting at session end for the same capture you just handled. Then resume primary task.
