---
name: epic
version: 1.1.0
description: Use when user says "create issues", "break down PRD", "set up epic", "create Linear tasks", "plan sprint", "convert to issues", or wants to transform PRD user stories into Linear epics and sub-issues.
---

# Epic Planning Skill

Transform User Stories (from PRD) into executable Engineering Tasks (Epics/Issues) in Linear.

## Step 1: Detect Platform & Verify Connection

**Auto-detect platform from user input:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- User mentions "Notion" → use Notion
- Anytype URL or object ID → use Anytype
- User mentions "Anytype" → use Anytype
- Otherwise → skip platform, gather requirements via conversation

**Only verify the detected platform (don't test both):**

### If Notion detected:
1. Run `notion-find` to search for "test"
2. **IF fails:** "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If no platform detected: proceed to next step

## Step 2: Gather Context

**IF Notion PRD URL provided:**
1. Use `notion-find` to fetch the PRD
2. Extract user stories and acceptance criteria

**IF Anytype PRD URL or object ID provided:**
1. Use `API-get-object` to fetch the PRD
2. Extract user stories and acceptance criteria

**IF feature name provided:**
1. Search detected platform for existing PRD
2. Extract user stories and acceptance criteria

**IF no PRD exists:**
1. Gather requirements via conversation

## Step 3: Detect Team's Linear Setup

**Adapt to team's existing patterns.**

Use Linear MCP:
- `list_teams` - Get team ID
- `list_issue_statuses` - Get actual state names
- `list_issue_labels` - Get existing labels
- `list_projects` - Get relevant project

Ask user if unclear: "Which team/project?"

## Step 4: Learn Codebase Style

Before planning:
1. Grep for similar features, note naming conventions
2. Check file structure
3. Find test patterns
4. Check for mock data from prototype (`mocks/` folders)

If prototype exists with mock data:
- List all mock locations
- Include "Swap mock to real API" as sub-issue

## Step 5: Create Technical Plan (SDD)

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Create SDD (Specification-Driven Development) document:
- Technical Overview
- Data Model Changes
- API Changes
- Component Breakdown
- Testing Strategy
- Risks & Unknowns

## Step 6: User Review

**CRITICAL: Get approval before creating issues.**

Present plan and ask:
- "Does this approach make sense?"
- "Any concerns?"
- "Ready to create Linear issues?"

**DO NOT proceed until user confirms.**

## Step 7: Plan Epics from User Stories

**1 User Story = 1 Epic**

For each User Story, create:
- **Title**: Transform user story goal → kebab-case (e.g., "I want to login" → `add-user-login`)
- **Description**: User story + acceptance criteria + **test criteria (REQUIRED for TDD)**
- **Sub-issues** (if complex): Apply **Parallel** label only when truly independent

**TDD rule:** Every issue MUST include `## Test Criteria` section. Tests are written FIRST before implementation.

## Step 8: Create in Linear

Using plan from Step 7:
1. Create parent issue (epic) first
2. Create sub-issues with `parentId` = epic ID
3. Use team's existing labels/states

## Step 9: Report

- Parent issue URL
- Sub-issue count: X total (P1: Y, P2: Z, P3: W)
- PRD link (URL or object ID)
- Platform used (Notion/Anytype)
- SDD summary

Next: `/vorbit:implement:implement ABC-123`

---

# Epic Schema & Standards

## Title Format

**Transform the User Story Goal into a kebab-case title.**

| User Story | Epic Title |
| :--- | :--- |
| "As a user, I want to **login**..." | `add-user-login` |
| "As an admin, I want to **manage users**..." | `add-admin-user-management` |

**Rules**:
- Action verbs: `add-`, `implement-`, `fix-`, `update-`
- Lowercase, hyphens, no special chars
- Match Git branch conventions: `git checkout -b add-user-login`

## Issue Structure

### Epic (Parent)

**Description template:**
```markdown
## User Story
US-XXX: As a [user], I want [goal]...

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [component behavior]
- [ ] Integration test: [user flow]

## PRD Reference
[Link]
```

### Sub-issue (Child)

**Title**: `component-name` or `step-name` (use **Parallel** label, not prefix)

**Description template:**
```markdown
## Summary
[Technical task description]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [specific behavior]
- [ ] Unit test: [edge case]
```

**Priority Mapping**:
- P1 (Urgent): Core / Blocker
- P2 (High): Important
- P3 (Normal): Standard

---

## TDD Requirement

**CRITICAL: All implementation follows Test-Driven Development.**

Every issue (epic and sub-issue) MUST include `## Test Criteria` section:
- Tests are written FIRST before implementation code
- Implementation is only "done" when all tests pass
- No issue is complete without corresponding tests

---

## Parallel Label Criteria

**Apply Parallel label ONLY when ALL are true:**
1. Sub-issue has NO dependencies on other sub-issues
2. Sub-issue does NOT block other sub-issues
3. Works on separate files/components (no merge conflicts)

**Default: Sequential.** When in doubt, don't add Parallel label.
