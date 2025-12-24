---
description: Create parent issue + sub-issues in Linear from PRD
argument-hint: [feature name or Notion PRD URL]
allowed-tools: Read, Grep, Glob, AskUserQuestion, Notion, Linear
---

Create issues for: $ARGUMENTS

## Step 1: Gather Context

1. IF Notion PRD URL provided, fetch the PRD
2. IF feature name provided, search Notion for PRD
3. IF no PRD exists, gather requirements via conversation

## Step 2: Detect Team's Linear Setup

**RULE: Adapt to team's existing patterns.**

Use Linear MCP tools:
- `list_teams` - Get team ID
- `list_issue_statuses` - Get actual state names
- `list_issue_labels` - Get existing labels
- `list_projects` - Get relevant project

Ask user if unclear: "Which team/project should I create this in?"

## Step 3: Learn Codebase Style

**Before any planning, study the existing codebase:**

1. **Code patterns** - Grep for similar features, note naming conventions
2. **File structure** - How are components/modules organized?
3. **Testing approach** - Jest/Vitest/pytest? What's the test file pattern?
4. **Existing code examples** - Find 2-3 files that represent team's style
5. **Check for mock data** - Find any `MOCK_`, `mock`, `.json` imports from prototype

Document findings for later use in implementation.

**If prototype exists with mock data:**
- List all mock data locations
- Include "Swap mock to real API" as sub-issue for each

## Step 4: Create SDD (Specification-Driven Development Document)

**RULE: If ANY requirement is unclear, MUST use AskUserQuestion tool.**

Create detailed technical plan:

```markdown
## Technical Overview
[High-level approach]

## Data Model Changes
[New tables/fields, migrations needed]

## API Changes
[New endpoints, request/response shapes]

## Component Breakdown
[UI components, services, utilities]

## Integration Points
[What existing code this touches]

## Dependencies
[External packages, internal modules]

## Testing Strategy
[Unit tests, integration tests, e2e if needed]

## Risks & Unknowns
[Technical debt, potential blockers]
```

## Step 5: User Review

**CRITICAL: Get approval before creating issues.**

Present the SDD and ask:
- "Does this technical approach make sense?"
- "Any concerns about the breakdown?"
- "Ready to create Linear issues?"

Do NOT proceed until user confirms.

## Step 6: Plan Epics from User Stories

**One User Story = One Epic (will become Linear issue)**

For each User Story from PRD, plan:

```
Epic Title: [verb]-[feature] (branch-friendly, e.g., "add-user-registration")
Description:
  - User Story: US-XXX
  - Full story: As a [user], I want [goal], so that [benefit]
  - Acceptance criteria from PRD
  - Test criteria
Priority: P1/P2/P3
```

**Sub-issues (only if epic is complex):**
```
[P] Sub-issue Title: [verb]-[component] (e.g., "implement-form-validation")
Description: What needs to be done
Parent: Epic ID
```

**Title Rules (for git branch compatibility):**
- Use action verbs: add, implement, fix, update, remove
- Kebab-case: no special chars, lowercase
- Short: max 50 chars

**Rules:**
- `[P]` prefix on sub-issues = Can run in parallel
- No `[P]` on sub-issues = Must run sequentially
- Simple epics don't need sub-issues
- Every epic/sub-issue MUST have test criteria

**Priority:**
- P1 (Urgent): Core functionality, blocks others
- P2 (High): Important, can start after P1
- P3 (Normal): No dependencies, can run anytime

## Step 7: Create in Linear

Using planned epics from Step 6 and SDD from Step 4:

1. **For each Epic planned in Step 6:**
   - Title: Epic title (branch-friendly)
   - Description: User story + acceptance criteria + test criteria
   - Team: Detected team (from Step 2)
   - Labels: Team's existing labels
   - Priority: As planned

2. **For each Sub-issue under Epic:**
   - Title: Sub-issue title (with [P] if parallel)
   - Description: Task details + test criteria
   - Parent: Epic ID
   - Priority: As planned

## Output

- Parent issue URL (e.g., `https://linear.app/team/ABC-123`)
- Sub-issue count: X total (P1: Y, P2: Z, P3: W)
- PRD link (if exists)
- SDD summary

Next: `/vorbit:implement:implement` (will auto-detect parent issue from this conversation) or `/vorbit:implement:implement ABC-123`
