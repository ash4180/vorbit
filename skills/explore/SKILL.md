---
name: explore
version: 1.1.0
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", "research options", or wants to do lightweight idea exploration before creating a full PRD. Saves to Notion or Anytype.
---

# Explore Skill

Quick idea exploration before PRD creation. Supports saving to Notion or Anytype.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`). Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Ask 10+ Questions

**MANDATORY: Ask at least 10 questions before generating options.**

Generate 10 questions specific to the topic. Ask in batches of 3-4 using AskUserQuestion - wait for responses before asking the next batch:

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

Then ask follow-ups:
- **Competitors**: "Who are existing solutions?"
- **User scenarios**: "Describe 3 real scenarios"
- **Constraints**: "Budget, timeline, or technical limitations?"
- **Confirm**: "Which are most important? What's missing?"

**DO NOT proceed until you have answers to 10+ questions.**

## Step 3: Analyze

After gathering context:
1. Summarize insights from all question answers
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros/cons/effort/risk
4. Make recommendation addressing constraints

## Step 4: Draft in Chat

**Show the complete exploration document in chat for review:**

```markdown
# [Topic] - Exploration

## Problem Statement
[One sentence identifying root cause]

## Context
[Summary of insights from questions]

## Options

### Option 1: [Name]
- **Description**: ...
- **Pros**: ...
- **Cons**: ...
- **Effort**: Low/Medium/High
- **Risk**: Low/Medium/High

### Option 2: [Name]
...

## Recommendation
[Which option and why, addressing constraints]
```

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 5: Save Document

**Only proceed after user confirms the draft.**

Save using the platform selected in Step 1. Follow the "Save Content" section in `_shared/mcp-tool-routing.md`. Pass the exploration content as markdown body.

## Step 6: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Recommended approach summary
- Next: `/vorbit:design:prd`

---

# Explore Schema & Validation

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
