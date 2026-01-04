---
name: prd
description: PRD output schema for Notion and Anytype. Use when creating PRDs, validating structure, or saving to documentation platforms.
---

# PRD Schema

Product Requirements Document structure for Notion and Anytype integration.

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

## Template

```markdown
# PRD: [FEATURE_NAME]

## Problem
[What's broken? Max 3 sentences, no tech details]

## Target Users
[Who has this problem?]

## User Stories

**US-001**: As a [user], I want [goal], so that [benefit]
  Acceptance:
  - [Criterion 1]
  - [Criterion 2]

**US-002**: As a [user], I want [goal], so that [benefit]
  Acceptance:
  - [Criterion 1]

## User Flow
[To be added via /vorbit:design:journey]

## Constraints
[Budget, timeline, compliance]

## Out of Scope
- [What we're NOT building]

## Success Criteria
- [Measurable outcome with number]
- [Another measurable outcome]
```

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

Use `API-create-object` with:
- `space_id`: from `API-list-spaces`
- `type_key`: "page"
- `name`: feature name
- `body`: full PRD markdown content

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| "We need OAuth2 for authentication" | "Users cannot access personalized features without accounts" | Problem describes user pain, not technical solution |
| "Users should be happy with login" | "90% of users complete login in under 10 seconds" | Success criteria must have numbers |
| "OAuth2 JWT Token Auth Implementation" | "User Login and Signup" | Name avoids jargon |
