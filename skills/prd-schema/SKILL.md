---
name: PRD Schema
description: This skill provides the strict output schema for Product Requirements Documents. Use when creating PRDs, validating PRD structure, or mapping PRDs to Notion databases.
---

## Purpose

Define consistent PRD structure for Notion integration. Every PRD follows the same format for team readability and agent validation.

## PRD Structure

| Section | Required | Validation |
|---------|----------|------------|
| Name | Yes | 3-8 words, no jargon |
| Description | Yes | Max 100 chars |
| Problem | Yes | Max 3 sentences, no tech |
| Users | Yes | Who has the problem |
| User Stories | Yes | "As a [user]..." format with acceptance criteria |
| Constraints | No | Budget, timeline, compliance |
| Out of Scope | No | What we're NOT building |
| Success Criteria | Yes | Measurable with numbers |

## User Stories Format

```
US-001: As a [user type], I want [goal], so that [benefit]
US-002: As a [user type], I want [goal], so that [benefit]
```

**Rules:**
- Each story = one user goal
- Include acceptance criteria per story
- Stories map to parent issues in Linear (via epic command)

**Example:**
```
US-001: As a new user, I want to create an account, so that I can access personalized features
  Acceptance:
  - Can enter email and password
  - Receives confirmation email
  - Account is created and active
```

## Story Prioritization (RICE)

User stories can include RICE scores for prioritization:

| Field | Values | Description |
|-------|--------|-------------|
| reach | 1-1000+ | Users affected per quarter |
| impact | 3/2/1/0.5/0.25 | massive/high/medium/low/minimal |
| confidence | 1.0/0.8/0.5 | high/medium/low |
| effort | 1-10 | Person-weeks |

**Score = (Reach × Impact × Confidence) / Effort**

Higher score = higher priority for Linear issues.

## Success Criteria Format

```
- 95% of signups complete successfully
- Login errors provide actionable guidance
- Page loads in under 2 seconds
```

**Rules:**
- Include numbers or percentages
- Must be verifiable (yes/no answer possible)
- Business outcomes, not technical metrics

## References

- `references/notion-mapping.md` - Database field mapping and schema
- `references/content-schema.json` - JSON schema for validation

## Examples

- `examples/valid-prd.json` - Complete PRD meeting all criteria
- `examples/invalid-examples.md` - Common mistakes and fixes

## Validation Checklist

Before saving to Notion:
- [ ] Name: 3-8 words, no technical jargon
- [ ] Description: Under 100 characters
- [ ] Problem: Max 3 sentences, no implementation details
- [ ] User stories follow "As a [user]..." format
- [ ] Each story has acceptance criteria
- [ ] Success criteria have measurable numbers
- [ ] No [UNCLEAR] markers remain
