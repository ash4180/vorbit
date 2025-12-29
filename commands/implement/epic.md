---
description: Create parent issue + sub-issues in Linear from PRD
argument-hint: [feature name or Notion PRD URL]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*, mcp__plugin_linear_linear__*
---

Create issues for: $ARGUMENTS

Use the **epic** skill for issue format and validation rules.

## Step 1: Gather Context

1. IF Notion PRD URL, fetch the PRD
2. IF feature name, search Notion for PRD
3. IF no PRD exists, gather requirements via conversation

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
- PRD link
- SDD summary

Next: `/vorbit:implement:implement ABC-123`
