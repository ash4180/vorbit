---
description: Create a Product Requirements Document. No fluff, just what needs building.
argument-hint: [feature description]
allowed-tools: Read, AskUserQuestion, Notion
---

Create a PRD for: $ARGUMENTS

## Step 1: Gather Context

1. IF existing context (explore.md, Notion doc, conversation), use it
2. IF starting fresh, proceed to Step 2

## Step 2: Clarify Requirements via Conversation

**RULE: If ANY requirement is unclear, MUST use AskUserQuestion tool.**

Use conversational questions with options (checkbox/radio) when possible:

1. **Problem** - "What problem does this solve?"
   - Let user describe freely

2. **Users** - "Who has this problem?"
   - Options: Internal team, End users, Admins, API consumers, Other

3. **Priority** - "How urgent is this?"
   - Options: Critical (blocking), High (needed soon), Medium (planned), Low (nice-to-have)

4. **Scope decisions** - For each ambiguous requirement, ask:
   - "Should [feature] support X or Y?" with clear options
   - "Do you need [capability]?" with Yes/No
   - "Which approach: A, B, or C?" with trade-off descriptions

5. **Constraints** - "Any limitations I should know?"
   - Budget, timeline, compliance, technical

Keep asking until ALL requirements are clear. Don't guess.

## Step 3: Create PRD

Use the **prd-schema** skill for exact output format.

Generate PRD with confirmed details:
- **Name**: Feature name (3-8 words, no jargon)
- **Description**: One-line summary (max 100 chars)
- **Problem**: What's broken (max 3 sentences, no tech)
- **Users**: Who has this problem
- **User Stories**: US-001, US-002... As a [user], I want [goal], so that [benefit]
- **Acceptance Criteria**: Clear conditions per user story
- **User Flow**: `[To be added via /vorbit:design:journey]`
- **Constraints**: Budget, timeline, compliance limits
- **Out of Scope**: What we're NOT building
- **Success Criteria**: Measurable outcomes (numbers, percentages)

## Step 4: Save to Notion

Ask user: "Where should I save this PRD? (Notion database name, page URL, or 'skip')"

If user provides a location:
1. Use `notion-search` or `notion-fetch` to find target
2. Create PRD document:
   - `Name` = feature name
   - `Description` = one-line summary
   - Full PRD in body
3. If database has `Type` property, set to `["PRD"]`

## Validation

Before saving, use **output-validator** agent to check PRD matches schema.

## Report

- Notion page URL (if saved)
- Summary: X requirements, Y success criteria
- Next: `/vorbit:design:journey` or `/vorbit:implement:epic`
