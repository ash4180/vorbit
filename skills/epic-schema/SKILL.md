---
name: epic-schema
description: Structure for Linear issues. Use when creating epics + sub-issues in Linear from PRD user stories.
---

# Linear Issue Schema

Structure for creating issues in Linear from PRD user stories.

## Mapping

```
PRD User Story → Epic (Linear issue)
                     ↓
              Sub-issues (Linear)
```

**1 User Story = 1 Epic** with optional sub-issues for complex features.

## Issue Structure

| Field | Description | Required |
|-------|-------------|----------|
| `title` | Branch-friendly: kebab-case, action verb (e.g., `add-user-login`) | Yes |
| `description` | Details + link to PRD | Yes |
| `team` | Team name or ID | Yes |
| `parentId` | Parent issue ID (for sub-issues) | For sub-issues |
| `priority` | 1-4 (Urgent/High/Normal/Low) | Optional |
| `labels` | Team's existing labels | Optional |
| `project` | Team's existing project | Optional |

## Before Creating

1. Detect team's setup via Linear MCP tools
2. Use team's existing labels, states, projects
3. Link back to PRD user story in description

## Epic Description

```markdown
## User Story
US-XXX: As a [user], I want [goal], so that [benefit]

## Acceptance Criteria
[Copy from PRD]

## Test Criteria
[How to verify this works]

## PRD Reference
[Notion link]
```

## Sub-issue Description

```markdown
## Summary
[Technical task description]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
- Blocked by: [issues that must complete first, or "None"]

## Parent Story
[Link to parent issue]
```

## Priority Mapping

| Priority | Linear | Meaning |
|----------|--------|---------|
| P1 | 1 (Urgent) | Core functionality, blocks others |
| P2 | 2 (High) | Important, can start after P1 |
| P3 | 3 (Normal) | No dependencies, can run anytime |

## Parallel Execution

Mark sub-issues that can run in parallel with `[P]` prefix in title during planning.

**Execution Order:**
```
1. Run all P1 sub-issues first (sequential - they block others)
2. Run P2 sub-issues (can parallel if marked [P])
3. Run P3 sub-issues (can parallel if marked [P])
```

**Dependency Rules:**
- No `[P]` = Must complete before next
- `[P]` = Can run simultaneously with other `[P]` at same priority
- Dependencies field overrides `[P]` - if depends on X, wait for X

**Sub-issue Title Format (branch-friendly):**
```
[P] implement-auth-api        ← Can run in parallel
[P] create-login-form         ← Can run in parallel
setup-database-schema         ← Must complete first (no [P])
```

**Title Rules:**
- Use action verbs: add, implement, fix, update, remove
- Kebab-case: lowercase, hyphens, no special chars
- Max 50 chars

## References

- [linear-mapping.md](references/linear-mapping.md) - Field mapping details
