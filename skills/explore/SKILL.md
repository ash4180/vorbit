---
name: explore
description: Use when the user asks to brainstorm, research options, or explore an early feature idea before committing to requirements. It asks targeted questions until the PRD-blocking unknowns are resolved, compares approaches, recommends one, and saves the approved exploration to Notion or Anytype when connected. Do not use for writing a final PRD, decomposing tickets, or implementing code.
---

# Explore Skill

Quick idea exploration before PRD creation. Supports saving to Notion or Anytype.

Read and follow `../_shared/execution-contract.md` before starting.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`) before any external call. Saving is optional: discover and verify Notion/Anytype when the user wants a saved artifact, but lack of a connection must not block questioning, analysis, or an approved chat draft.

## Step 2: Resolve the PRD-Blocking Unknowns

Ask questions via AskUserQuestion until every unknown that would block a PRD is either answered or explicitly parked as unresolved. Depth is set by the information need, not a count: a well-specified idea may need 4 targeted questions; a vague one may need 15. Size each batch to what the user can answer comfortably.

Cover these categories, skipping any the user's request already settles:
- Core functionality decisions
- Scale and performance needs
- User control and preferences
- Error handling and edge cases
- Constraints (budget, time, compliance)
- Existing solutions / competitors and real user scenarios

Before proceeding to Step 3, list each question asked with the user's answer (one line each), then list the unknowns that remain open. Open unknowns go to the PRD Handoff's unresolved decisions — never silently fill them with assumptions.

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

## PRD Handoff
- Confirmed decisions: [facts the user explicitly chose]
- Unresolved decisions: [questions to clarify in PRD; not requirements yet]
```

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 5: Save Document

**Only proceed after user confirms the draft.**

If a connected destination was selected, save using the "Save Content" section in `_shared/mcp-tool-routing.md` and pass the exploration content as markdown body. Otherwise keep the approved document in chat and report it as unsaved.

An exploration document is a decision input, not a PRD source of truth. Do not label it a PRD or create implementation issues from it directly. The PRD workflow imports the confirmed decisions and creates the canonical Linear spec ticket.

## Step 6: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Recommended approach summary
- Unresolved decisions to carry into PRD clarification (do not silently convert them into requirements)
- Next: `/vorbit:design:prd [pasted PRD Handoff or local export]` (include the exploration URL only as provenance)

---

# Explore Schema & Validation

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | Key insights from ALL question answers |
| Problem Statement | Yes | One sentence, root cause focus |
| Options | Yes | 2-3 approaches with pros/cons |
| Recommendation | Yes | Which option and why |
| PRD Handoff | Yes | Separate confirmed decisions from unresolved questions |

## Options Format

Each option must have:
- **Name**: Short descriptive name
- **How**: One sentence approach
- **Pros**: 2-3 benefits
- **Cons**: 2-3 drawbacks
- **Effort**: Low / Medium / High
- **Risk**: Low / Medium / High

## Validation Rules

- Context resolves every PRD-blocking unknown or lists it as an unresolved decision
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
- [One line per resolved unknown]

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

## PRD Handoff
**Confirmed decisions:**
- [Explicit user choice]

**Unresolved decisions:**
- [Question for PRD clarification — do not convert to a requirement]
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
