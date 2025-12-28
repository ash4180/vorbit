---
name: epic
description: Linear issue schema. Use when creating epics + sub-issues from PRD user stories.
---

# Epic Schema

Structure for creating Linear issues from PRD user stories.

## Core Mapping

```
PRD User Story → Epic (Linear parent issue)
                      ↓
               Sub-issues (Linear children)
```

**1 User Story = 1 Epic** with optional sub-issues for complex features.

## Title: User Story → Branch-Friendly

**Transform the user story goal into a kebab-case title for GitHub branches.**

| User Story | Epic Title |
|------------|------------|
| "As a user, I want to **login**..." | `add-user-login` |
| "As an admin, I want to **manage users**..." | `add-admin-user-management` |
| "As a customer, I want to **reset my password**..." | `add-password-reset` |
| "As a seller, I want to **list products**..." | `add-product-listing` |

Rules:
- Extract the **goal** from user story
- Prefix with action verb: `add-`, `implement-`, `fix-`, `update-`, `remove-`
- kebab-case: lowercase, hyphens, no special chars
- Max 50 chars
- Must work as Git branch name: `git checkout -b add-user-login`

## Issue Fields

| Field | Required | Rules |
|-------|----------|-------|
| `title` | Yes | Branch-friendly from user story goal |
| `description` | Yes | Has Summary + Acceptance Criteria sections |
| `team` | Yes | Team name or ID |
| `parentId` | Sub-issues | Parent issue ID |
| `priority` | No | 1=Urgent, 2=High, 3=Normal, 4=Low |
| `labels` | No | Use team's existing labels |
| `project` | No | Use team's existing project |

## Validation Rules

- **Title**: Derived from user story, kebab-case, max 50 chars, branch-friendly
- **Description**: Contains `## User Story`, `## Acceptance Criteria` sections
- **Sub-issues**: Must have `parentId` and acceptance criteria
- **Testable**: Every issue has clear pass/fail criteria

## Epic Description Template

```markdown
## User Story
US-XXX: As a [user], I want [goal], so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1 (from PRD)
- [ ] Criterion 2
- [ ] Criterion 3

## Test Criteria
- [ ] Unit tests for [component]
- [ ] Integration test for [flow]

## PRD Reference
[Notion link]
```

## Sub-issue Description Template

```markdown
## Summary
[Technical task description]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
- Blocked by: [issues or "None"]
```

## Sub-issue Title Format

```
[P] implement-auth-api        ← Can run in parallel
[P] create-login-form         ← Can run in parallel
setup-database-schema         ← Must complete first (no [P])
```

- `[P]` prefix = can run in parallel with other `[P]` at same priority
- No `[P]` = sequential, must complete before next

## Priority Mapping

| Priority | Linear Value | Meaning |
|----------|--------------|---------|
| P1 | 1 (Urgent) | Core functionality, blocks others |
| P2 | 2 (High) | Important, can start after P1 |
| P3 | 3 (Normal) | No dependencies, can run anytime |

## Execution Order

```
1. Run P1 sub-issues first (sequential - they block others)
2. Run P2 sub-issues (parallel if marked [P])
3. Run P3 sub-issues (parallel if marked [P])
```

## Before Creating Issues

Detect team's existing patterns:
1. `list_teams` - Get team ID
2. `list_issue_statuses` - Get actual state names
3. `list_issue_labels` - Get existing labels
4. `list_projects` - Get project structure

Adapt to team's conventions. Don't impose new patterns.
