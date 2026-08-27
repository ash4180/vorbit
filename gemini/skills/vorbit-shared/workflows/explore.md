<!-- GENERATED from skills/explore/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-explore` skill directory (a sibling of `vorbit-shared`).

# Explore Skill

Quick idea exploration before PRD creation. Supports saving to Notion or Anytype.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/glossary.md`: use the project's `CONTEXT.md` glossary terms when it exists, and record newly agreed terms there.

## Step 1: Detect Platform & Verify Connection

Preflight required connectors: confirm each needed connector is configured in Gemini CLI and inspect its current operation/parameter schemas; never guess tool names before any external call. Saving is optional: discover and verify Notion/Anytype when the user wants a saved artifact, but lack of a connection must not block questioning, analysis, or an approved chat draft.

## Step 2: Resolve the PRD-Blocking Unknowns

Ask questions via plain-text chat questions until every unknown that would block a PRD is either answered or explicitly parked as unresolved. Depth is set by the information need, not a count: a well-specified idea may need 4 targeted questions; a vague one may need 15. Size each batch to what the user can answer comfortably.

Work in rounds. Each round asks every question that is answerable now; a question whose answer depends on another question still open in the same round waits for a later round. Mark a recommended option on every question. Facts are your job, never the user's: anything discoverable from the codebase, connected tools, or the web gets looked up between rounds — ask the user only for decisions. After each round of answers, recompute what became askable.

**UI/UX asks:** when the request is about screens, flows, visual design, or interactions, the FIRST question batch must ask: "Is this for existing code or a fresh idea?" Existing code: read the relevant screens and components before analyzing, and ground every proposal in them. Fresh idea: skip the codebase and ground proposals in reference research only.

Cover these categories, skipping any the user's request already settles:
- Core functionality decisions
- Scale and performance needs
- User control and preferences
- Error handling and edge cases
- Constraints (budget, time, compliance)
- Existing solutions / competitors and real user scenarios

Before proceeding to Step 3, list each question asked with the user's answer (one line each), then list the unknowns that remain open. Open unknowns go to the PRD Handoff's unresolved decisions — never silently fill them with assumptions.

## Step 3: Research References (UI/UX asks)

For UI/UX explorations, gather real-product evidence before analyzing:
1. Mobbin first, when connected: search screens, flows, and sections for the pattern. Flows also show transitions and motion worth borrowing.
2. Web search as fallback, or to add named products Mobbin lacks.
3. For "existing code" asks, also read the current screens and components so proposals reuse what exists.

Collect per candidate pattern: app name, what it does well, and any motion worth borrowing. Skip this step for non-UI explorations.

## Step 4: Analyze

After gathering context:
1. Summarize insights from all question answers
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros/cons/effort/risk
4. Make recommendation addressing constraints
5. UI/UX asks: define the key animations and micro-interactions of the recommended approach, following `references/motion-principles.md` (from this skill's installed directory)

## Step 5: Publish the Solution Artifact (UI/UX asks, automatic)

After analysis, build one self-contained HTML page presenting the recommended solution. Publish it as an artifact when the platform supports artifacts; otherwise save the file outside the repo and give the user the path. Do not ask permission first; this page is part of the exploration deliverable.

The page contains:
- The user flow of the recommended approach, step by step.
- The reference patterns from research, with app names.
- One micro-interaction card per key interaction, with a live CSS demo, using the card shape in `references/motion-principles.md` (from this skill's installed directory). Follow its role models and hard limits, including `prefers-reduced-motion`.

The page presents the solution. It is not a pixel-perfect mockup and not a PRD.

## Step 6: Draft in Chat

**Show the complete exploration document in chat for review**, using the Template in the schema section below.

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 7: Save Document

**Only proceed after user confirms the draft.**

If a connected destination was selected, save via the connected platform's current content-creation tools (inspect schemas first) and pass the exploration content as markdown body. Otherwise keep the approved document in chat and report it as unsaved.

An exploration document is a decision input, not a PRD source of truth. Do not label it a PRD or create implementation issues from it directly. The PRD workflow imports the confirmed decisions and creates the canonical Linear spec ticket.

## Step 8: Report

- URL or object ID (if saved)
- Solution artifact link (UI/UX asks)
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
- UI/UX asks only: Reference Patterns present with at least 2 real products, and the solution artifact is published and linked in the report

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

## Reference Patterns (UI/UX asks only)
- [App name]: [what it does well] ([Mobbin/web])
- [App name]: [motion worth borrowing] ([Mobbin/web])

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
