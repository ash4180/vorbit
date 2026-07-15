<!-- GENERATED from skills/explore/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Explore Skill

Quick idea exploration before PRD creation. Supports saving to Notion or Anytype.

Read and follow `../references/execution-contract.md` before starting.

## Step 1: Detect Platform & Verify Connection

Preflight required connectors: confirm each needed connector is configured in Codex and inspect its current operation/parameter schemas; never guess tool names before any external call. Saving is optional: discover and verify Notion/Anytype when the user wants a saved artifact, but lack of a connection must not block questioning, analysis, or an approved chat draft.

## Step 2: Resolve the PRD-Blocking Unknowns

Ask questions via plain-text chat questions until every unknown that would block a PRD is either answered or explicitly parked as unresolved. Depth is set by the information need, not a count: a well-specified idea may need 4 targeted questions; a vague one may need 15. Size each batch to what the user can answer comfortably.

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

**Show the complete exploration document in chat for review**, using the Template in the schema section below.

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 5: Save Document

**Only proceed after user confirms the draft.**

If a connected destination was selected, save via the connected platform's current content-creation tools (inspect schemas first) and pass the exploration content as markdown body. Otherwise keep the approved document in chat and report it as unsaved.

An exploration document is a decision input, not a PRD source of truth. Do not label it a PRD or create implementation issues from it directly. The PRD workflow imports the confirmed decisions and creates the canonical Linear spec ticket.

## Step 6: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Recommended approach summary
- Unresolved decisions to carry into PRD clarification (do not silently convert them into requirements)
- Next: `$vorbit-prd [pasted PRD Handoff or local export]` (include the exploration URL only as provenance)

---

# Explore Schema & Validation

## Validation Rules

- All Template sections present: Context Summary, Problem Statement, Options, Recommendation, PRD Handoff
- Context resolves every PRD-blocking unknown or lists it as an unresolved decision
- Problem identifies root cause, not symptoms
- 2-3 options, each with a concrete approach (not vague) and 2-3 pros/cons
- Effort and risk honestly assessed
- No option obviously superior (otherwise why explore?)
- Recommendation addresses constraints from context
- PRD Handoff separates confirmed decisions from unresolved questions

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
