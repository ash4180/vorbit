# Learning Format Reference

## Classification Table

| Type | When to use | Default target |
|---|---|---|
| `pattern` | A reusable approach or convention | CLAUDE.md > Learned Patterns |
| `knowledge` | A fact about the codebase or domain | `.claude/rules/{topic}.md` |
| `workflow` | A multi-step process that should be repeatable | `.claude/rules/workflows.md` |
| `error` | A failure mode and its fix | CLAUDE.md > Error Patterns |
| `improvement` | Something that should be fixed/built | New Linear issue |
| `skill-fix` | A skill's SKILL.md had unclear, incomplete, or wrong instructions | Full absolute path (see `scopes.md`) |
| `script-fix` | A hook script had a bug, missing logic, or wrong behavior | Full absolute path (see `scopes.md`) |
| `review-rule` | A recurring code review finding that should become a standing rule | `.claude/review-rules.md` |

### Title Format

Concise imperative statement (like a commit message).
- Good: "Use WAL mode for SQLite to prevent BUSY errors"
- Bad: "I found a bug with SQLite"

## pending.md Format

```markdown
# Pending Learnings

<!-- META: ticket=NONE count=3 last_synced=7 Feb 2026, 12:00 -->

### 1. Use WAL mode for SQLite to prevent BUSY errors
- **Type:** error
- **Frequency:** 5
- **First seen:** 28 Jan 2026
- **Last seen:** 7 Feb 2026
- **Context:** Concurrent writes cause BUSY errors. WAL mode fixes it.
- **Target:** CLAUDE.md > Error Patterns

### 2. Soft deletes on events table — never call .delete()
- **Type:** knowledge
- **Frequency:** 3
- **First seen:** 1 Feb 2026
- **Last seen:** 6 Feb 2026
- **Context:** Events use soft deletes with deletedAt timestamp.
- **Target:** .claude/rules/database.md

### 3. Deploy requires running migrations before starting server
- **Type:** workflow
- **Frequency:** 1
- **First seen:** 7 Feb 2026
- **Last seen:** 7 Feb 2026
- **Context:** Server crashes on startup if new migrations haven't run.
- **Target:** .claude/rules/workflows.md
```

### Rules

- Items numbered sequentially (1, 2, 3...)
- META line: count = total items, last_synced = current timestamp
- Dates: `7 Feb 2026` (items), `7 Feb 2026, 12:00` (META)
- Sort by frequency (highest first)

## Examples

### Capture Example (session end)

Session: Implemented user authentication, hit a CORS error, discovered the project uses a custom middleware pattern.

```
### 1. CORS middleware must be registered before auth middleware
- **Type:** error
- **Frequency:** 1
- **First seen:** 7 Feb 2026
- **Last seen:** 7 Feb 2026
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
