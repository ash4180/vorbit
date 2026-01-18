---
name: prd
version: 1.1.0
description: Use when user says "write PRD", "create requirements", "define feature", "document requirements", "product spec", or wants to create a Product Requirements Document. Outputs to Notion or Anytype.
---

# PRD Skill

Create Product Requirements Documents with proper structure. No fluff, just what needs building.

## Step 1: Detect Platform & Verify Connection

**Auto-detect platform from user input:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- User mentions "Notion" → use Notion
- Anytype URL or object ID → use Anytype
- User mentions "Anytype" → use Anytype
- Otherwise → ask at save time (Step 5)

**Only verify the detected platform (don't test both):**

### If Notion detected:
1. Run `notion-find` to search for "test"
2. **IF fails:** "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If no platform detected: proceed (ask later)

## Step 2: Gather Context

**IF Notion URL provided:**
1. Use `notion-find` with page title from URL
2. If content retrieval fails, ask user to paste relevant sections
3. Proceed to Step 4 (restructure mode)

**IF Anytype URL or object ID provided:**
1. Use `API-get-object` to retrieve content
2. If content retrieval fails, ask user to paste relevant sections
3. Proceed to Step 4 (restructure mode)

**IF existing context (explore doc, conversation):**
1. Use that context as input
2. Proceed to Step 3 for gaps

**IF starting fresh:**
1. Proceed to Step 3

## Step 3: Clarify Requirements

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Ask about:
1. **Problem** - "What problem does this solve?"
2. **Users** - "Who has this problem?" (options: Internal team, End users, Admins, etc.)
3. **Priority** - "How urgent?" (Critical, High, Medium, Low)
4. **Scope** - For ambiguous requirements, ask with options
5. **Constraints** - Budget, timeline, compliance

Keep asking until ALL requirements are clear. Don't guess.

## Step 4: Generate PRD

Use the template below. Include:
- Name (3-8 words, no jargon)
- Problem (max 3 sentences, no tech)
- Users
- User Stories with acceptance criteria
- User Flow: `[To be added via /vorbit:design:journey]`
- Constraints
- Out of Scope
- Success Criteria (with numbers)

**Show the complete PRD in chat for review:**

```markdown
# [Feature Name]

## Problem
[Max 3 sentences, no tech details]

## Users
[Who has this problem]

## User Stories

### US1: [Title]
As a [user], I want [goal], so that [benefit].

**Acceptance Criteria:**
- [ ] ...
- [ ] ...

### US2: [Title]
...

## User Flow
[To be added via /vorbit:design:journey]

## Constraints
- ...

## Out of Scope
- ...

## Success Criteria
- [Measurable metric with number]
- ...
```

**After showing draft, ask:** "Does this PRD look good? Ready to save?"

## Step 5: Save Document

**Only proceed after user confirms the draft.**

**If platform was detected in Step 1:** use that platform directly (don't ask again).

**If no platform detected:** Use AskUserQuestion: "Where should I save this PRD?"
- Options: Notion, Anytype, Other

### If Notion:
1. Ask for database name or page URL
2. Use `notion-find` to locate target database
3. Create with Name = feature name, full PRD in body
4. If database has `Type` property, set to `["PRD"]`

### If Anytype:
1. Use `API-list-spaces` to show available spaces
2. Ask user which space to save to
3. Use `API-create-object` with:
   - `type_key`: "page" (or appropriate type)
   - `name`: feature name
   - `body`: full PRD content as markdown

## Step 6: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Summary: X user stories, Y success criteria
- Next: `/vorbit:design:journey` or `/vorbit:implement:epic`

---

# PRD Schema & Validation

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Name | Yes | 3-8 words, no jargon |
| Description | Yes | Max 100 chars |
| Problem | Yes | Max 3 sentences, no tech details |
| Users | Yes | Who has the problem |
| User Stories | Yes | "As a [user]..." with acceptance criteria |
| User Flow | Placeholder | `[To be added via /vorbit:design:journey]` |
| Success Criteria | Yes | Measurable with numbers |
| Constraints | No | Budget, timeline, compliance |
| Out of Scope | No | What we're NOT building |

## Validation Rules

- **Name**: 3-8 words, no technical jargon
- **Problem**: Max 3 sentences, describes user pain not technical gap
- **User Stories**: Format "As a [user], I want [goal], so that [benefit]"
- **User Flow**: Placeholder text until journey command fills it
- **Success Criteria**: Contains measurable numbers (percentages, times, counts)
- **No placeholders**: No `[UNCLEAR]`, `[TBD]`, or empty sections (except User Flow)

## User Story Format

```
US-001: As a [user type], I want [goal], so that [benefit]
  Acceptance:
  - [Specific testable criterion]
  - [Another criterion]
```

Rules:
- One goal per story
- Each story has acceptance criteria
- Stories map to Linear issues (via /vorbit:implement:epic)

## Success Criteria Format

```
- 95% of signups complete successfully
- Page loads in under 2 seconds
- Error rate below 0.1%
```

Rules:
- Include numbers
- Must be verifiable (yes/no answer)
- Business outcomes, not tech metrics

## Notion Mapping

| Notion Field | PRD Field | Notes |
|--------------|-----------|-------|
| Name | Feature name | title property |
| Description | One-line summary | text, max 100 chars |
| Type | `["PRD"]` | multi_select, if exists |

Content goes in page body as markdown.

## Anytype Mapping

| Anytype Field | PRD Field | Notes |
|---------------|-----------|-------|
| name | Feature name | object name |
| body | Full PRD content | markdown format |
| type_key | "page" | or custom type if available |

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| "We need OAuth2 for authentication" | "Users cannot access personalized features without accounts" | Problem describes user pain, not technical solution |
| "Users should be happy with login" | "90% of users complete login in under 10 seconds" | Success criteria must have numbers |
| "OAuth2 JWT Token Auth Implementation" | "User Login and Signup" | Name avoids jargon |
