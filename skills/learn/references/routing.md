# Routing Reference

## Routing Table

| Type | Scope | Destination | Section |
|---|---|---|---|
| `error` | project | `{origin}/CLAUDE.md` | Error Patterns |
| `pattern` | project | `{origin}/CLAUDE.md` | Learned Patterns |
| `knowledge` | project | `{origin}/.claude/rules/{topic}.md` | By topic |
| `workflow` | project | `{origin}/.claude/rules/{topic}.md` | — |
| `review-rule` | project | `{origin}/.claude/review-rules.md` | By severity |
| `skill-fix` | project | `{plugin_root}/skills/{skill}/SKILL.md` | — |
| `script-fix` | project | `{plugin_root}/hooks/scripts/{script}` | — |
| `agent-mistake` | universal | `~/.claude/rules/{topic}.md` | — |
| `user-preference` | universal | `~/.claude/rules/{topic}.md` | — |
| `tool-behavior` | universal | `~/.claude/rules/{topic}.md` | — |

`{origin}` = the absolute project path from the digest block header.

## Absolute Path Routing

When processing learnings (from pending-capture approval or unprocessed-corrections digest), each block header contains the full project path:

```
## Session: abc123 | Project: /Users/ash/Desktop/myproject | 15 Feb 2026
```

Use `/Users/ash/Desktop/myproject` as the `{origin}` for all project-scoped learnings from that block. This ensures learnings route to the correct project even when the current session is in a different project.

## Group A: CLAUDE.md (error, pattern)

1. Read `{origin}/CLAUDE.md`
2. Find or create the target section (`## Learned Patterns` or `## Error Patterns`)
3. Append: `- **{title}:** {context}`

## Group B: Knowledge Files (knowledge, workflow)

1. Determine topic from context (e.g., "database", "auth", "api", "state-management")
2. Read `consolidation.md` in this references directory before creating any new file
3. Read or create the target file at `{origin}/.claude/rules/{topic}.md`
4. Append entry — 1-3 lines max per consolidation rules
5. **Cross-reference** in CLAUDE.md (see Cross-Reference Rule below)

## Group C: Review Rules (review-rule)

1. Read or create `{origin}/.claude/review-rules.md`
2. Append under severity heading (`## Critical`, `## Important`, or `## Style`)
3. Format: `- **{title}:** {context}`
4. **Cross-reference** in CLAUDE.md (see Cross-Reference Rule below)

## Group D: Self-Improvement (skill-fix, script-fix)

1. Resolve the plugin root — search for the vorbit plugin manifest:
   ```bash
   find ~ -path "*/.claude-plugin/plugin.json" -maxdepth 6 2>/dev/null | head -5
   ```
   Pick the result containing `vorbit`. The parent of `.claude-plugin/` is the plugin root.
2. Read the target file using the absolute path
3. Apply minimum change needed — add/clarify the missing instruction or fix the bug
4. Do NOT rewrite surrounding content

## Group E: Universal Learnings (agent-mistake, user-preference, tool-behavior)

1. Determine topic from context (e.g., "agent-behavior", "tool-quirks", "user-preferences")
2. Read `consolidation.md` before creating any new file
3. Read or create the target file at `~/.claude/rules/{topic}.md`
4. Append entry — 1-3 lines max per consolidation rules

## Cross-Reference Rule

**After routing to any file in Group B or C**, ensure the project's CLAUDE.md links to it:

1. Read `{origin}/CLAUDE.md`
2. Find or create `## Knowledge Base` section
3. If the file is already listed → skip
4. If not listed → append: `- [{topic}]({relative_path}) — {one-line description}`

Without this, knowledge files become orphaned and invisible to future sessions.
