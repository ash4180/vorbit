---
name: prd
version: 1.1.0
description: Use when user says "write PRD", "create requirements", "define feature", "document requirements", "product spec", or wants to create a Product Requirements Document. Outputs to Notion or Anytype.
---

# PRD Skill

Create Product Requirements Documents with proper structure. No fluff, just what needs building.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`). Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Gather Context

**IF URL or ID provided:**
1. Use the platform's MCP tools (discovered in Step 1) to fetch content
2. If retrieval fails, ask user to paste relevant sections
3. Proceed to Step 4 (restructure mode)

**IF existing context (explore doc, conversation):**
1. Use that context as input
2. Proceed to Step 3 for gaps

**IF starting fresh:**
1. Proceed to Step 3

## Step 3: Clarify Requirements

**RULE: Be opinionated. Assume standard patterns. Only ask when wrong assumptions waste real effort.**

Ask a MAXIMUM of 3 rounds of questions. Focus on:
1. **Problem** - "What problem does this solve?" (only if not obvious from context)
2. **Users** - "Who has this problem?" (only if ambiguous — don't ask if context makes it clear)
3. **Scope** - Only ask if the feature could reasonably be 2x or 0.5x what they described

**Do NOT ask about:**
- Priority (user will tell you if it matters)
- Constraints (assume standard unless stated)
- Edge cases (capture those as assumptions, not questions)

**For anything uncertain:**
1. Mark the requirement as `TBD` inline where it appears in the PRD
2. Use `AskUserQuestion` to ask the user to clarify — batch unclear items together (max 3 rounds)
3. Update the `TBD` markers with user's answers before showing the final draft

Every `TBD` MUST have a corresponding question asked. No silent guessing.

## Step 4: Generate PRD

Use the template below. Include:
- Name (3-8 words, no jargon)
- Problem (max 3 sentences, no tech)
- Users
- User Stories with acceptance criteria
- Assumptions (from Step 3 — things you assumed instead of asking)
- User Flows (multi-actor: User, UI, Agent, System across Pages/Components/Services)
- Constraints
- Out of Scope
- Success Criteria (with numbers)

**User Flow Rules:**
- Every PRD needs at least ONE flow
- Flows must show interactions between actors (User, UI, Agent, System)
- Each step has: Actor (who), Surface (where), Action (what), Result (outcome)
- If the feature has AI/agent involvement, the agent MUST appear as an actor in the flow
- Multiple flows for different paths (happy path, error path, edge cases)

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

## Assumptions
- [Reasonable assumption made during PRD creation]
- [Another assumption — user corrects during review]

## User Flows

### Flow 1: [Primary Flow Name]
**Entry:** [Page/Screen] → **Exit:** [Page/Screen]

| Step | Actor | Surface | Action | Result |
|------|-------|---------|--------|--------|
| 1 | User | [Page] | [What user does] | [What happens] |
| 2 | UI | [Component] | [UI response] | [What user sees] |
| 3 | Agent | [Service] | [Processing] | [Output] |
| 4 | UI | [Page] | [Shows result] | [End state] |

### Flow 2: [Secondary Flow Name]
...

> Detailed journey diagram: `/vorbit:design:journey`

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

Save using the platform selected in Step 1. Follow the "Save Content" section in `_shared/mcp-tool-routing.md`. Pass the PRD content as markdown body.

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
| Assumptions | Yes | Stated assumptions, user corrects during review |
| User Flows | Yes | Multi-actor flows with Actor/Surface/Action/Result |
| Success Criteria | Yes | Measurable with numbers |
| Constraints | No | Budget, timeline, compliance |
| Out of Scope | No | What we're NOT building |

## Validation Rules

- **Name**: 3-8 words, no technical jargon
- **Problem**: Max 3 sentences, describes user pain not technical gap
- **User Stories**: Format "As a [user], I want [goal], so that [benefit]"
- **Assumptions**: Reasonable defaults stated explicitly — user corrects during review
- **User Flows**: At least one flow with Actor (User/UI/Agent/System), Surface (Page/Component/Service), Action, Result
- **Success Criteria**: Contains measurable numbers (percentages, times, counts)
- **TBD allowed selectively**: `TBD` is fine in Constraints, Success Criteria numbers, and User Flow steps that depend on design decisions. NOT allowed in Problem, Users, or User Stories — those must be concrete

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
