# Linear Field Mapping

## Structure

**Issue** (parent) → **Sub-issues** (children)

Use Linear's native parent/child relationship via `parentId` field.

## Before Creating Issues

Detect team's existing patterns:
1. `list_teams` - Get team ID
2. `list_issue_statuses` - Get actual state names
3. `list_issue_labels` - Get existing labels
4. `list_projects` - Get project structure

Adapt to team's conventions. Don't impose new patterns.

## Issue Fields

| Field | Description | Required |
|-------|-------------|----------|
| `title` | Branch-friendly: kebab-case, action verb (e.g., `add-user-login`) | Yes |
| `description` | Markdown content | Yes |
| `team` | Team name or ID | Yes |
| `state` | Team's actual state name | Optional |
| `priority` | 1=Urgent, 2=High, 3=Normal, 4=Low | Optional |
| `labels` | Team's existing labels | Optional |
| `project` | Team's existing project | Optional |
| `assignee` | User ID or "me" | Optional |
| `parentId` | Parent issue ID (for sub-issues) | For sub-issues |

## Creating Parent + Sub-issues

```
1. Create parent issue first → get issue ID
2. Create sub-issues with parentId = parent issue ID
```

## Description Template (adapt as needed)

```markdown
## Summary
[What needs to be done]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Context
- PRD: [Notion link if exists]
```

Keep it simple. Match team's existing style.
