---
description: Create parent issue + sub-issues in Linear from PRD
argument-hint: [feature name or PRD reference]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*, mcp__anytype__*, mcp__plugin_linear_linear__*
---

Create issues for: $ARGUMENTS

Use the **epic** skill for issue format and validation rules.

## Step 0: Detect Platform & Verify Connection

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
3. **IF succeeds:** proceed to Step 1

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed to Step 1

### If no platform detected: proceed to Step 1

## Step 1: Gather Context

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

## Step 2: Detect Team's Linear Setup

**Adapt to team's existing patterns.**

Use Linear MCP:
- `list_teams` - Get team ID
- `list_issue_statuses` - Get actual state names
- `list_issue_labels` - Get existing labels
- `list_projects` - Get relevant project

Ask user if unclear: "Which team/project?"

## Step 3: Learn Codebase Style

Before planning:
1. Grep for similar features, note naming conventions
2. Check file structure
3. Find test patterns
4. Check for mock data from prototype (`mocks/` folders)

If prototype exists with mock data:
- List all mock locations
- Include "Swap mock to real API" as sub-issue

## Step 4: Create Technical Plan

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Create SDD (Specification-Driven Development) document:
- Technical Overview
- Data Model Changes
- API Changes
- Component Breakdown
- Testing Strategy
- Risks & Unknowns

## Step 5: User Review

**CRITICAL: Get approval before creating issues.**

Present plan and ask:
- "Does this approach make sense?"
- "Any concerns?"
- "Ready to create Linear issues?"

**DO NOT proceed until user confirms.**

## Step 6: Plan Epics from User Stories

**1 User Story = 1 Epic**

For each User Story, create:
- **Title**: Transform user story goal → kebab-case (e.g., "I want to login" → `add-user-login`)
- **Description**: User story + acceptance criteria + test criteria
- **Sub-issues** (if complex): With `[P]` prefix for parallel tasks

Title must be branch-friendly: `git checkout -b add-user-login`

## Step 7: Create in Linear

Using plan from Step 6:
1. Create parent issue (epic) first
2. Create sub-issues with `parentId` = epic ID
3. Use team's existing labels/states

**Hook auto-validates before create. Fix issues if prompted.**

## Report

- Parent issue URL
- Sub-issue count: X total (P1: Y, P2: Z, P3: W)
- PRD link (URL or object ID)
- Platform used (Notion/Anytype)
- SDD summary

Next: `/vorbit:implement:implement ABC-123`
