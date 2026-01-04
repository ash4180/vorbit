---
name: explore
description: Structure for exploration documents. Use when creating explorations or validating explore output format. Supports Notion and Anytype.
---

# Explore Schema

Quick idea exploration before PRD creation. Supports saving to Notion or Anytype.

## Context Gathering (MANDATORY)

**CRITICAL: You MUST ask at least 10 questions before generating options.**

### Step 1: Generate Topic-Specific Questions

Generate exactly 10 questions specific to the topic. Present ALL 10 to the user in a single AskUserQuestion call.

Example for "notification system":
```
1. What triggers a notification? (user action, system event, schedule)
2. Which channels needed? (email, SMS, push, in-app)
3. Can users configure their preferences?
4. What's the expected volume? (10/day, 1000/hour)
5. Are notifications time-sensitive?
6. Should notifications be batched/digested?
7. What happens if delivery fails?
8. Are there compliance requirements? (GDPR opt-out)
9. Who can send notifications? (system only, other users)
10. What's the budget constraint for external services?
```

Questions should probe:
- Core functionality decisions
- Scale and performance needs
- User control and preferences
- Error handling and edge cases
- Constraints (budget, time, compliance)

### Step 2: Follow-up Questions

After the 10 questions, ask:
- **Competitors**: "Who are the main competitors or existing solutions?"
- **User scenarios**: "Describe 3 real scenarios users will face"
- **Constraints**: "Any budget, timeline, or technical limitations?"

**DO NOT proceed to analysis until you have answers to at least 10 questions.**

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | Key insights from ALL question answers |
| Problem Statement | Yes | One sentence, root cause focus |
| Options | Yes | 2-3 approaches with pros/cons |
| Recommendation | Yes | Which option and why |

## Options Format

Each option must have:
- **Name**: Short descriptive name
- **How**: One sentence approach
- **Pros**: 2-3 benefits
- **Cons**: 2-3 drawbacks
- **Effort**: Low / Medium / High
- **Risk**: Low / Medium / High

## Validation Rules

- Context includes answers to 10+ questions
- Problem identifies root cause, not symptoms
- Each option has concrete approach (not vague)
- Effort and risk honestly assessed
- No option obviously superior (otherwise why explore?)
- Recommendation addresses constraints from context

## Template

```markdown
# Explore: [TOPIC]

## Context Summary
Key insights from conversation:
- [Answer to Q1 insight]
- [Answer to Q2 insight]
- ...
- [Answer to Q10 insight]

Constraints: [budget, timeline, compliance from follow-up]
Competitors: [existing solutions mentioned]

## Problem Statement
[One sentence - what's the root cause?]

## Options

### Option 1: [Name]
**How**: [One sentence approach]
**Pros**:
- [Benefit 1]
- [Benefit 2]
**Cons**:
- [Drawback 1]
- [Drawback 2]
**Effort**: [Low/Medium/High]
**Risk**: [Low/Medium/High]

### Option 2: [Name]
...

### Option 3: [Name]
...

## Recommendation
[Which option and why, addressing constraints]
```

## Notion Mapping

| Notion Field | Explore Field | Notes |
|--------------|---------------|-------|
| Name | Topic | title property |
| Type | `["Exploration"]` | multi_select, if exists |

Content goes in page body as markdown.

## Anytype Mapping

| Anytype Field | Explore Field | Notes |
|---------------|---------------|-------|
| name | Topic | object name |
| body | Full exploration content | markdown format |
| type_key | "page" | or custom type if available |

Use `API-create-object` with:
- `space_id`: from `API-list-spaces`
- `type_key`: "page"
- `name`: topic
- `body`: full exploration markdown content
