---
name: learn
version: 9.0.0
description: Capture agent corrections into Vorbit's canonical multi-agent learning store. Automatic capture writes pending review items; every durable rule requires human review before publication.
---

# Learn Skill

Vorbit now separates learning into two stages:

1. **Automatic capture** — Claude, Codex, and Gemini adapters write canonical captures and pending review items.
2. **Human review** — a pending item must be approved before it becomes a durable rule that any agent can load.

## Canonical store

Vorbit resolves its storage root in this order:

1. `VORBIT_HOME`
2. `~/.vorbit/config.toml` `storage.root`
3. `~/.vorbit`

Inside that root, the learning system uses:

- `captures/` — normalized raw capture records
- `pending/` — unified review inbox
- `rules/universal/` — shared global rules
- `rules/projects/<project-slug>/` — shared project rules
- `rules/agents/<agent>/projects/<project-slug>/` — agent-local project rules
- `rules/agents/<agent>/universal/` — agent-local global rules
- `state/` — dedupe/session state
- `exports/` — compatibility projections such as Claude bridge files or optional Obsidian mirrors

Pending items are not durable rules. Never treat `pending/*.json` as executable guidance.

## Automatic capture

Automatic capture is adapter-driven:

- **Claude** — stop hook writes canonical captures, then mirrors the legacy `~/.claude/rules/pending-capture.md` bridge and the optional Obsidian export.
- **Codex CLI** — `scripts/vorbit-codex-cli.py` captures transcript-driven learnings into the canonical queue.
- **Gemini CLI** — `scripts/vorbit-gemini-cli.py` does the same for Gemini transcripts.

Automatic means **capture only**. Promotion is always reviewed.

## Scopes

Each pending learning proposes one of these scopes:

- `agent-local` — only the source agent should load it
- `project-shared` — all agents should load it for this project
- `universal-shared` — all agents should load it globally

You may edit the proposed scope during review.

## Review flow

Use the canonical review CLI:

```bash
python3 scripts/vorbit-learning.py pending --project-root <project-root>
python3 scripts/vorbit-learning.py approve <review-id> --approved-by <name>
python3 scripts/vorbit-learning.py reject <review-id> --reason "<why>"
```

Optional overrides on approval:

```bash
python3 scripts/vorbit-learning.py approve <review-id> \
  --approved-by <name> \
  --scope project-shared \
  --rule-text "Use SQLite for local development." \
  --destination rules/projects/<project-slug>/<rule-id>.md
```

Approval publishes exactly one durable rule and refreshes projections for Claude, Codex, and Gemini.

## Mid-session interactive capture (Claude only)

This mode runs during sessions when Claude detects a correction and finds a fix. NOT invoked manually.

### References

Detailed specs live in `references/` within this skill's directory. Glob for `**/skills/learn/references/` to resolve the path.

| File | Contains |
|---|---|
| `references/format.md` | Scope classification table, type mapping, examples |
| `references/routing.md` | Routing table by scope, absolute path routing, Cross-Reference Rule |
| `references/consolidation.md` | Document consolidation rules for `.claude/rules/` files |

### Trigger

Any correction keyword from `vorbit-learning-rules.md` triggers this flow after the fix is confirmed.

### After finding the fix

**Step 1:** Use `AskUserQuestion`: "I just fixed an issue. Want me to analyze the root cause?"
- "Yes" → Step 2
- "No" → stop, resume primary task

**Step 2: Classify root cause**

Use this decision tree in order. Stop at the first match:

1. **Did a tool or MCP service behave unexpectedly?** → `tool-behavior`
2. **Is this a user workflow or communication preference?** → `user-preference`
3. **Did the agent make a reasoning error that would happen in ANY project?** → `agent-mistake`
4. **Is a skill's SKILL.md unclear or missing an instruction?** → `skill`
5. **Does a hook script have a bug or missing logic?** → `script`
6. **Is this a fact about the codebase that `.claude/rules/` should know?** → `knowledge`
7. **Would a rule in CLAUDE.md have prevented this error?** → `claude-md`
8. **Not enough context to classify?** → `unclear` — use `AskUserQuestion` to ask the user
9. **Agent reasoning error, no documentation fix needed** → `general` (nothing written)

**Step 3:** Use `AskUserQuestion` to present: what went wrong, root cause category, proposed scope, proposed rule text.
- "Approve" → write to canonical store via `vorbit_core`
- "Edit" → user adjusts scope/destination
- "Skip" → don't write anything

**Step 4:** Write the capture as a pending review item. It still requires human approval via the review CLI before becoming durable.

**Step 5:** Resume primary task.

## Claude compatibility

Claude still gets:

- `~/.claude/rules/vorbit-learning.md`
- `~/.claude/rules/pending-capture.md`
- `~/.claude/rules/.seen-correction-sessions`

Those are compatibility bridges. The canonical source of truth is the Vorbit store.

## Legacy import

To migrate the old Thinking-Labs + Claude layout into the canonical store:

```bash
python3 scripts/vorbit-learning.py import-legacy --project-root <project-root>
```

That imports:

- pending Obsidian-backed notes
- global Claude rules from `~/.claude/rules/`
- project Claude rules from `<project>/.claude/rules/`
