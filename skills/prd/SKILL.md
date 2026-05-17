---
name: prd
version: 2.0.0
description: Use when user says "write PRD", "create requirements", "define feature", "document requirements", "product spec", "create ticket", or wants to capture a feature spec as a single Linear ticket. Creates a Linear ticket directly with user stories, acceptance criteria, user flows, constraints, and success criteria.
---

# PRD Skill

Create a Linear ticket that captures a product requirement. No fluff, just what needs building.

> **Linear MCP namespace**: All Linear calls in this skill use `mcp__plugin_linear_linear__*` (the namespace shipped with the vorbit plugin). Bare verb names below (`get_user`, `list_teams`, `save_issue`, etc.) refer to the corresponding `mcp__plugin_linear_linear__<verb>` tool.

## Step 1: Gather Context (Draft First)

The goal is a drafted PRD before touching Linear. Connection problems must never block drafting.

**IF a Linear ticket URL or ID is provided (existing draft, similar feature, etc.):**
1. Use `get_issue` to fetch the source ticket and read its description for context
2. Restructure: keep the source intent, normalize wording to the schema below, mark gaps as `TBD`

**IF the user pastes content from elsewhere (Notion, a doc, an old spec):**
1. Use the pasted text directly as input — the skill's Linear-only `allowed-tools` cannot fetch external docs
2. Ask the user for any sections they referenced but did not paste, then restructure as above

**IF conversation already covers the feature:** use that context as input.

**IF starting fresh:** proceed to Step 2.

## Step 2: Clarify Requirements

**Rule: ask about every meaningful uncertainty. Do not silently guess.**

Use `AskUserQuestion`, batch related unknowns together, max 3 rounds. Focus on:
1. **Problem** — user pain and why this matters
2. **Users** — who is affected, primary vs secondary
3. **Scope** — what is in and what is out
4. **Constraints** — compliance, timing, platform, integration limits
5. **Edge cases** — failure paths and unusual but realistic usage
6. **Success metrics** — measurable outcomes

For anything still unknown:
1. Mark it `TBD` inline where it would appear in the PRD
2. Ask the user via `AskUserQuestion` (batched, max 3 rounds)
3. Replace the `TBD` with the answer before the final draft
4. If still unresolved after 3 rounds, leave the `TBD` with a short label

Every `TBD` must have a matching question attempt. No silent guessing.

## Step 3: Generate Draft

Use the template below. Match VIB-2978's prose style — no big tables.

**Required content:**
- Feature name (3-8 words, no jargon) — this becomes the Linear ticket **title**
- Description: one short paragraph under the H1
- Problem: 1-2 short paragraphs, no tech detail
- User Stories: `US-001`, `US-002`, ... each with `AC-N` items
- User Flows: at least one happy flow in prose Entry/Exit form
- Constraints
- Success Criteria with numbers

After showing the draft, ask: **"Does this look good? Ready to create the Linear ticket?"**

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

**Acceptance Criteria:**

- [ ] AC-1 [Specific testable criterion]
- [ ] AC-2 [Another specific criterion]

### US-002: [Title]

As a [user], I want [goal], so [benefit].

**Acceptance Criteria:**

- [ ] AC-3 ...
- [ ] AC-4 ...

## User Flows

### Flow 1: [Name] (Happy flow)

**Entry:** [Start screen] → [Step] → [Step] → [Step] → **Exit:** [End state]

### Flow 2: [Name] (Happy flow, second main path)

**Entry:** [Start] → [Step] → [Step] → **Exit:** [End]

### Flow 3: [Name] (alternate / error)

Entry: [Start] → [Step] → Server returns error → Error toast, values preserved → Exit: [State]

## Constraints

* [Constraint with reason — what cannot change]
* [Constraint about backend, design, timeline, etc.]

## Success Criteria

* [Measurable target with a number]
* [Another measurable target]
```

### Flow rules

- Every PRD needs at least one happy flow
- Flow steps use prose `Entry: X → step → step → **Exit:** Y` form
- Each step names what the user does, the surface they touch, and the visible result
- Add a separate flow for any materially different path (second happy path, alternate, error)
- Every user story should be covered by at least one flow step
- Keep flows ticket-sized: typically 3-8 arrows per flow

### TBD rules

- `TBD` is fine in Constraints, Success Criteria numbers, and flow details that depend on later design decisions
- `TBD` is **not** allowed in Problem, Users, or User Stories — those must be concrete before the ticket is created
- Every `TBD` must have a matching `AskUserQuestion` attempt

## Step 4: Confirm Draft

Only proceed after the user confirms the draft. If they ask for changes, edit the draft in chat and re-confirm.

## Step 5: Create the Linear Ticket

1. `get_user` with `query: "me"` to verify Linear auth/session
2. `list_teams` (scoped `limit`, e.g. 10-20). If multiple teams, ask the user which one
3. `list_projects` with the selected team (scoped `limit`). If multiple, ask the user which one. If the team has no projects, skip the project field
4. `save_issue` to create the ticket:
   - `title`: the feature name (the H1 line, without the `#`)
   - `team`: selected team name (string, name-based — not `teamId`)
   - `project`: selected project name if any (string, name-based — not `projectId`)
   - `description`: the full PRD body in markdown, starting at `## Description` and including everything below

**Reliability rules:**
- Keep calls scoped with `team` and `limit`. Don't run unfiltered workspace-wide listing
- On temporary MCP/API error, retry once with the same parameters
- If `list_teams` fails, ask the user to type the team name directly
- Only block execution when auth fails

## Step 6: Report

- Linear ticket **URL**
- Team and project used
- Quick summary: X user stories, Y flows, Z success criteria
- Suggested next step:
  - `/vorbit:implement:epic <ticket-id>` to break the ticket into engineering sub-issues
  - `/vorbit:design:journey` to draw a flow diagram in FigJam

---

## Coverage Review Mode

When asked to review whether sub-issues fulfill a parent PRD ticket:

1. Read the parent ticket (`get_issue`) and all sub-issues (`list_issues` with the parent's `parentId`)
2. Map each User Story and `AC-N` to the sub-issue(s) covering it
3. Flag work that **cannot be bundled** into an existing sub-issue as a gap; bundle-able housekeeping is not a gap
4. Report: coverage matrix (story → sub-issues), gaps, verdict (covered / has gaps)

---

# Schema & Validation

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Title (H1) | Yes | 3-8 words, no jargon. Becomes Linear ticket title. |
| Description | Yes | 1-2 short sentences, no tech detail |
| Problem | Yes | 1-2 short paragraphs, user pain not tech gap |
| User Stories | Yes | `As a [user], I want ..., so ...` plus `AC-N` items |
| User Flows | Yes | At least one happy flow in Entry/Exit prose form |
| Constraints | Yes | Limits the implementation must respect |
| Success Criteria | Yes | Measurable with numbers |

## Validation Rules

- **Title**: 3-8 words, no jargon
- **Description**: short, plain English, no tech detail
- **Problem**: describes user pain, not the technical fix
- **User Stories**: `As a [user], I want [goal], so [benefit]`. Each story has at least one `AC-N`
- **User Flows**: at least one. Use Entry/Exit anchors. 3-8 arrows per flow is the sweet spot
- **AC coverage**: every `AC-N` should be reflected in at least one flow step
- **Success Criteria**: contain real numbers (percentages, times, counts)
- **TBD**: allowed in Constraints, Success Criteria numbers, and flow details only — never in Problem, Users, or User Stories. Every `TBD` must have a matching `AskUserQuestion` attempt

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| "We need JWT auth" | "Users cannot access personalized features without accounts" | Problem describes user pain, not the technical fix |
| "Users should be happy with login" | "90% of users complete login in under 10 seconds" | Success criteria need real numbers |
| "OAuth2 JWT Token Auth Implementation" | "User Login and Signup" | Title avoids jargon |
| Flow as steps only (`User → API → DB → API → User`) | `Entry: Login → Click Submit → Loading → Token returned → Exit: Home` | Flows describe what the user sees, with Entry/Exit anchors |
