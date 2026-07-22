<!-- GENERATED from skills/prd/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# PRD Skill

Create a Linear ticket that captures a product requirement. No fluff, just what needs building.

Read and follow `../references/execution-contract.md` before starting.

Before any Linear call, preflight required connectors: confirm each needed connector is configured in Gemini CLI and inspect its current operation/parameter schemas; never guess tool names. Verb names below describe intent; never substitute an operation name remembered from another runtime.

## Step 1: Gather Context (Draft First)

The goal is a drafted PRD before touching Linear. Connection problems must never block drafting.

**Source-of-truth rule:** Linear is the canonical PRD provider and the confirmed output is a Linear **spec ticket**. Pasted text and explicit local files are legacy import inputs, not competing sources of truth. Preserve their intent, record their provenance in the draft, and normalize them into the Linear ticket rather than continuing to maintain two PRDs.

Resolve context in this order:

**IF a Linear ticket URL or ID is provided (canonical PRD, existing draft, similar feature, etc.):**
1. Use `get_issue` to fetch the source ticket and read its description for context
2. Restructure: keep the source intent, normalize wording to the schema below, mark gaps as `TBD-###`

**ELSE IF the user pastes legacy content or gives an explicit local file path:**
1. Use the pasted text directly, or `Read` the user-specified local file
2. Record `Imported from: [pasted content | local path]` in the draft working notes
3. Ask for referenced content that is missing, then restructure as above

**ELSE IF a non-Linear URL is provided:** ask the user to paste/export its contents. Do not imply that the external document is canonical and do not guess its contents.

**IF conversation already covers the feature:** use that context as input.

**IF starting fresh:** proceed to Step 2. Do not require an existing Linear ticket to draft; Linear becomes canonical only after the approved creation step.

## Step 2: Clarify Requirements

**Rule: ask about every meaningful uncertainty. Do not silently guess.** Every factual requirement and numeric target must trace to user input, a cited source artifact, or a durable rule. Treat inferred privacy, persistence, retention, permissions, exclusions, and metric targets as questions, not facts.

Use plain-text chat questions and batch related unknowns together. A few rounds normally suffice; when unknowns remain after that, park them as TBDs (below) rather than continuing to interrogate. Focus on:
1. **Problem** — user pain and why this matters
2. **Users** — who is affected, primary vs secondary
3. **Scope** — what is in and what is out
4. **Constraints** — compliance, timing, platform, integration limits
5. **Edge cases** — failure paths and unusual but realistic usage
6. **Success metrics** — measurable outcomes

For anything still unknown:
1. Mark it inline as `TBD-001`, `TBD-002`, ... where it would appear in the PRD
2. Ask the user via plain-text chat questions (batched)
3. Replace the `TBD` with the answer before ticket confirmation
4. If the user can't or won't resolve it, leave the ID with a short label and classify it as `implementation-affecting` or `non-blocking`. Anything that can change observable behavior, AC wording, flow branches, API/data contracts, issue boundaries, dependencies, or test criteria is `implementation-affecting`; epic planning must block until it is resolved. Never invent a number or promote an inference into a constraint merely to remove a TBD

Every `TBD` must have a matching question attempt.

## Step 3: Generate Draft

Use the template below. Match VIB-2978's prose style — no big tables.

**Required content:**
- Feature name (3-8 words, no jargon) — this becomes the Linear ticket **title**
- Description: one short paragraph under the H1
- Problem: 1-2 short paragraphs, no tech detail
- User Stories: `US-001`, `US-002`, ... each representing one end-to-end user outcome with exactly one colocated user flow followed by acceptance-criteria checkboxes
- Constraints
- Success Criteria with confirmed, sourced numbers; use `TBD-###` when a target is unknown

Do not fill required sections by invention. Put unresolved assumptions in `## Open Questions` with their provenance and impact classification. A structurally complete review draft may contain permitted TBDs.

Before showing the draft, run the coverage gate: every acceptance criterion is satisfied by at least one step in its own story's flow. This is a check, not a section — verify it, state the result in chat, and keep the mapping out of the ticket body.

If the user requested a draft or review only, stop after showing it; do not ask to create or call Linear. Report `needs_input` when an implementation-affecting TBD remains, otherwise `completed`. For creation requests, ask after the draft: **"Does this look good? Ready to create the Linear ticket?"**

### Template

```markdown
# [Feature Name]

## Description

[1-2 sentences summarizing the feature]

## Problem

[1-2 short paragraphs explaining user pain and why this matters]

## User Stories

### US-001: [Title]

As a [user], I want [goal], so [benefit].

**User Flow:**

1. **Entry:** [which screen, and its starting state]. [User action and what they see]
2. [which screen or field]. [User action and what they see]
3. **Exit:** [observable end state]

**Acceptance Criteria:**

- [ ] [Specific testable criterion]
- [ ] [Another specific criterion]

### US-002: [Title]

As a [user], I want [goal], so [benefit].

**User Flow:**

1. **Entry:** [which screen, and its starting state]. [User action and what they see]
2. [which screen or field]. [User action and what they see]
3. **Exit:** [observable end state]

**Acceptance Criteria:**

- [ ] ...
- [ ] ...

## Constraints

* [Constraint with reason — what cannot change]
* [Constraint about backend, design, timeline, etc.]

## Success Criteria

* [Confirmed measurable target with a sourced number, or `TBD-###`]
* [Another confirmed target, or `TBD-###`]

## Open Questions

* `TBD-001` — [question] — Impact: [implementation-affecting | non-blocking]
```

### Flow rules

- Every user story represents one end-to-end user outcome and contains exactly one `**User Flow:**`
- Place the user flow after the story statement and before its acceptance criteria
- Number the flow steps `1.`, `2.`, `3.`
- Each step names three things: what the user did, which screen or field it happened on, and what they saw as a result
- Mark the first step `Entry` and an observable terminal step `Exit`; write a retry or loop in plain English when it is part of the same outcome
- Split materially different flows or outcomes into separate user stories instead of adding another flow to one story
- Keep the single flow readable without deleting branches, retries, loops, or requirements that belong to its outcome

### Identifier and coverage rules

- User story IDs are document-unique: `US-001`, `US-002`, ...
- Acceptance criteria carry no IDs. They are plain checkboxes under their story; the story heading already identifies them
- Flow steps carry no IDs. Reference them outside the document as `US-001, flow step 2`
- Coverage gate: every acceptance criterion is satisfied by at least one step in its own story's flow. Resolve any gap before confirmation. Run it as a check and report the result in chat; never write the mapping into the ticket

## Step 4: Confirm Draft

Only proceed after the user confirms the draft and any implementation-affecting TBDs are resolved. If they ask for changes, edit the draft in chat and re-confirm. A request for a draft, review, or analysis is not approval to create the ticket.

## Step 5: Create the Linear Ticket

1. Use the connector's verified lightweight identity/read operation to verify auth/session.
2. Use its verified team-list operation with a scoped limit (for example 10-20). If multiple teams exist, ask the user which one.
3. Use its verified project-list operation scoped to the selected team. If multiple projects exist, ask; if none exist, omit the project field.
4. Call the operation whose inspected schema explicitly **creates an issue**. Do not assume `save_issue` or `create_issue` across runtimes. Supply:
   - `title`: the feature name (the H1 line, without the `#`)
   - team: the selected team value in the exact field/type required by the inspected schema
   - project: the selected project value, if any, in the exact field/type required by the schema
   - `description`: the full PRD body in markdown, starting at `## Description` and including everything below

**Reliability rules:**
- Keep reads scoped by the selected team and a limit when the schema supports them. Don't run unfiltered workspace-wide listing
- On temporary MCP/API error, retry once with the same parameters
- If team listing fails but creation accepts a typed team, ask the user for the team value required by the schema
- Only block execution when auth fails

## Step 6: Report

- Linear ticket **URL**
- Team and project used
- Quick summary: X user stories, X colocated flows, Z success criteria
- Source note: Linear is now canonical; include legacy import provenance when applicable
- Suggested next step:
  - `$vorbit-epic <ticket-id>` to break the ticket into engineering sub-issues
  - `$vorbit-journey` to draw a flow diagram in FigJam

---

## Coverage Review Mode

When asked to review whether sub-issues fulfill a parent PRD ticket:

1. Read the PRD spec ticket (`get_issue`) and its `## Implementation Parents` index. The spec ticket is not an implementation parent. For a legacy ticket without the index, ask for the implementation-parent URLs; never treat the spec's direct children as the new topology by assumption.
2. Fetch every indexed implementation parent, then use `list_issues` with each implementation parent's `parentId` to fetch only its children.
3. Verify one indexed parent per `US-###`, and map every acceptance criterion to child issue(s) under that story's parent.
4. Flag missing/duplicate parents, cross-parent children, and work that **cannot be bundled** into an existing child as gaps; bundle-able housekeeping is not a gap.
5. Report: topology check, coverage matrix (story → parent → children), gaps, verdict (covered / has gaps).

---

# Schema & Validation

All sections below are required.

| Section | Rules |
|---------|-------|
| Title (H1) | 3-8 words, no jargon. Becomes the Linear ticket title |
| Description | 1-2 short sentences, plain English, no tech detail |
| Problem | 1-2 short paragraphs of user pain, not the technical fix |
| User Stories | `As a [user], I want [goal], so [benefit]`; one end-to-end outcome, exactly one colocated flow before at least one plain-checkbox criterion |
| Constraints | Limits the implementation must respect |
| Success Criteria | Sourced numbers (percentages, times, counts), or classified `TBD-###` placeholders |

- **AC coverage**: every acceptance criterion is satisfied by at least one step in its own story's flow. Verified before the draft is shown; reported in chat, never persisted as a section
- **TBD**: allowed in Constraints, Success Criteria numbers, and flow details that depend on later design decisions only — never in Problem, Users, or User Stories. Every `TBD-###` has a matching question attempt and impact classification

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| "We need JWT auth" | "Users cannot access personalized features without accounts" | Problem describes user pain, not the technical fix |
| "Users should be happy with login" | `TBD-001` — target completion rate and time threshold — Impact: non-blocking | Unknown targets stay explicit until the user supplies real numbers |
| "OAuth2 JWT Token Auth Implementation" | "User Login and Signup" | Title avoids jargon |
| Flow as one arrow chain (`Entry → Submit → Home`) | A numbered list: `1.` Entry, `2.` Submit, `3.` Exit | One step per line, each naming what the user did, which screen, and what they saw |
| A standalone `## User Flows` section | One `**User Flow:**` inside each user story | The outcome, flow, and acceptance criteria stay together |
| Multiple flows inside one user story | Split materially different flows into separate user stories | One story owns one end-to-end user outcome |
| Prefixing criteria or flow steps with IDs | `- [ ] Clicking Create shows an error` | The story heading and the list position already identify them. IDs only earn their keep when something *outside* the document points at them |
