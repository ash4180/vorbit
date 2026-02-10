# Routing Reference

## Routing Table

| Type | Destination | Section |
|---|---|---|
| `pattern` | `CLAUDE.md` | Learned Patterns |
| `error` | `CLAUDE.md` | Error Patterns |
| `knowledge` | `.claude/rules/{topic}.md` | By topic |
| `workflow` | `.claude/rules/workflows.md` | — |
| `review-rule` | `.claude/review-rules.md` | By severity (Critical / Important / Style) |
| `skill-fix` | `skills/{skill}/SKILL.md` | — |
| `script-fix` | `hooks/scripts/{script}` | — |
| `improvement` | Linear issue | — |

## Group A: CLAUDE.md (pattern, error)

1. Read CLAUDE.md
2. Find or create the target section (`## Learned Patterns` or `## Error Patterns`)
3. Append: `- **{title}:** {context}`

## Group B: Knowledge Files (knowledge, workflow)

1. Determine topic from context (e.g., "database", "auth", "api")
2. Read `consolidation.md` in this references directory before creating any new file
3. Read or create the target file
4. Append entry — 1-3 lines max per consolidation rules
5. **Cross-reference** in CLAUDE.md (see Cross-Reference Rule below)

## Group C: Review Rules (review-rule)

1. Read or create `.claude/review-rules.md`
2. Append under severity heading (`## Critical`, `## Important`, or `## Style`)
3. Format: `- **{title}:** {context}`
4. **Cross-reference** in CLAUDE.md (see Cross-Reference Rule below)

## Group D: Self-Improvement (skill-fix, script-fix)

1. Read `scopes.md` in this references directory to resolve the plugin path
2. Read the target file using the absolute path from the pending item's Target field
3. Apply minimum change needed — add/clarify the missing instruction or fix the bug
4. Do NOT rewrite surrounding content

## Group E: External (improvement)

1. Call `create_issue` with title and description
2. Report the issue URL

## Cross-Reference Rule

**After routing to any file in Group B or C**, ensure CLAUDE.md links to it:

1. Read CLAUDE.md
2. Find or create `## Knowledge Base` section
3. If the file is already listed → skip
4. If not listed → append: `- [{topic}]({path}) — {one-line description}`

```markdown
## Knowledge Base
- [Theme tokens](.claude/rules/theme.md) — Token mapping, ThemePreference values, hex opacity suffixes
- [Navigation](.claude/rules/navigation.md) — AuthStack/MainStack pattern, RootStackParamList type
- [UI conventions](.claude/rules/ui.md) — Tab bar constants, Settings layout, indicator sizing
- [Review rules](.claude/review-rules.md) — Standing code review rules from past reviews
```

Without this, knowledge files become orphaned and invisible to future sessions.
