---
name: prd
version: 1.4.0
description: Use when user says "write PRD", "create requirements", "define feature", "document requirements", "product spec", or wants to create a Product Requirements Document. Outputs to Notion or Anytype.
---

# PRD Skill

Create Product Requirements Documents with proper structure. No fluff, just what needs building.

## Step 1: Gather Context (Draft First)

Goal: produce a PRD draft first. Platform connection must not block drafting.

**IF URL or ID provided:**
1. Try to fetch content using `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`)
2. If MCP connection is missing or retrieval fails, ask user to paste relevant sections and continue
3. Use restructure mode, then proceed to Step 2

**Restructure mode definition:**
- Transform existing source content into the PRD schema while preserving intent
- Keep strong source details as-is; normalize structure and wording
- Mark missing required fields as `TBD` and resolve through Step 2 questions

**IF existing context (explore doc, conversation):**
1. Use that context as input
2. Proceed to Step 2 for gaps

**IF starting fresh:**
1. Proceed to Step 2

## Step 2: Clarify Requirements

**RULE: Ask on every meaningful uncertainty. Do not silently assume unclear requirements.**

Ask a MAXIMUM of 3 rounds of questions using `AskUserQuestion` (batch related unknowns together). Focus on:
1. **Problem** - user pain and why this matters
2. **Users** - who is affected, primary vs secondary users
3. **Scope** - what is explicitly in and out
4. **Constraints** - compliance, timeline, platform, integration limits
5. **Edge cases** - failure paths and unusual but realistic usage
6. **Success metrics** - measurable target outcomes

**For anything uncertain:**
1. Mark the requirement as `TBD` inline where it appears in the PRD
2. Ask the user to clarify using `AskUserQuestion` (batched, max 3 rounds)
3. Update `TBD` markers with the user's answers before showing the final draft
4. If still unanswered after 3 rounds, keep `TBD` and label it

Every `TBD` MUST have a corresponding question asked. No silent guessing.

## Step 3: Generate PRD Draft

Use the template below. Include:
- Name (3-8 words, no jargon)
- Description (one line, max 100 chars)
- Problem (max 3 sentences, no tech)
- Users
- User Stories with plain language acceptance criteria (ID each as `AC-*`)
- Assumptions (only explicit defaults accepted by the user, or explicit deferrals)
- User Flows (Actor/Surface/Action/Result + Story/AC refs across Pages/Components/Services)
- Constraints
- Success Criteria (with numbers)

**User Flow Rules:**
- Every PRD needs at least ONE flow
- Each step has: Actor (who), Surface (where), Action (what), Result (outcome)
- The primary flow MUST include User, UI, and System actors
- Use `Agent` as an actor only when a model/agent performs a distinct journey step (for example: generates content, makes a recommendation/decision, classifies input, or executes tools)
- Do NOT label normal backend/API processing as `Agent`; use `System` for standard deterministic service behavior
- Add additional flows only for materially different paths (error, edge, alternate)
- Every user story MUST map to at least one flow (or be explicitly marked `No user flow required` with a reason)
- No strict 1:1 is required: one flow can cover multiple user stories

**Core Flow Building Rules (Flow 1):**
- Flow 1 is REQUIRED and represents the primary end-to-end happy path
- Start at the user's first trigger and end at the user-visible completion state
- Use stable step IDs: `F1-S1`, `F1-S2`, ...
- Keep one state transition per step (no hidden jumps)
- Each step MUST specify:
  - Actor
  - Surface (page/component/service)
  - Action
  - Result
  - Story refs (`US-*`)
  - AC refs (`AC-*`)
- If a step calls an API/service, show the endpoint/service name in `Surface` or `Result`
- If a step can fail, point to alternate flow coverage in `Result` (for example: `On failure -> Flow 2`)
- Keep Flow 1 detailed enough for ticket derivation (typically 4-12 steps)
- Every `AC-*` should map to at least one flow step, unless explicitly marked `Non-journey AC` with reason

**Acceptance Criteria format:** Plain language descriptions of what "done" looks like. Each AC is a short statement — what the user can do, what the system does, or what constraint is met. No formal structure (MUST/SHOULD, GIVEN/WHEN/THEN) — the `/vorbit:epic` skill formalizes these into testable specs later.

**Show the complete PRD in chat for review:**

```markdown
# [Feature Name]

## Description
[One-line summary, max 100 chars]

## Problem
[Max 3 sentences, no tech details]

## Users
[Who has this problem]

## User Stories

### US-1: [Title]
As a [user], I want [goal], so that [benefit].

**Acceptance Criteria:**
- AC-1: [What the user can do or what the system does when done]
- AC-2: [Another observable outcome or constraint]

### US-2: [Title]
...

## Assumptions
- [Explicit default accepted by user]
- [Explicitly deferred decision with owner]

## User Flows

### Flow 1: [Primary Flow Name]
**Entry:** [Page/Screen] → **Exit:** [Page/Screen]

| Step ID | Actor | Surface | Action | Result | Story Refs | AC Refs |
|---------|-------|---------|--------|--------|------------|---------|
| F1-S1 | User | [Page] | [What user does] | [What happens] | US-1 | AC-1 |
| F1-S2 | UI | [Component] | [UI response] | [What user sees] | US-1 | AC-1 |
| F1-S3 | System | [Service/API] | [Processes request] | [Data/state updated] | US-1 | AC-2 |
| F1-S4 | UI | [Page] | [Shows result] | [End state] | US-1 | AC-2 |

### Flow 2: [Alternative/Error Flow] (optional)
...

> Add `Agent` rows only when the agent performs a distinct journey step; otherwise keep those steps as `System`.
> Detailed journey diagram: `/vorbit:design:journey`

## Story-to-Flow Mapping
| User Story | Flow Coverage | AC Coverage | Notes |
|------------|---------------|-------------|-------|
| US-1 | Flow 1 (F1-S1 to F1-S4) | AC-1, AC-2 | Primary journey |
| US-2 | Flow 2 (F2-S1 to F2-S3) | AC-3 | Error/alternate path |
| US-3 | No user flow required | AC-4 | Internal technical migration only |

## Constraints
- ...

## Success Criteria
- [Measurable metric with number]
- ...
```

**After showing draft, ask:** "Does this PRD look good? Ready to save?"

## Step 4: Confirm Draft

**Only proceed after user confirms the draft.**

## Step 5: Save Document (Optional)

If user confirms saving:
1. If a platform was already identified earlier, reuse it unless user asks to switch
2. Otherwise follow `_shared/mcp-tool-routing.md` to discover connected platforms, ask user which one to use, and verify connection
3. Save with the selected platform's MCP tools:
   - `type`: `"PRD"`
   - `name`: feature name
   - `body`: full PRD markdown

If user does not want to save, skip Step 5 and continue to Step 6.

## Step 6: Report

- Draft status: confirmed (and whether it was saved)
- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Summary: X user stories, Y success criteria
- Next: `/vorbit:design:journey` or `/vorbit:implement:epic`

## Coverage Review Mode

When asked to review if tickets/issues fulfill a PRD:

### Step 1: Fetch Both Sides
- Read the PRD (from Notion, Anytype, or provided content)
- Read all referenced tickets (from Linear or provided list)

### Step 2: Map User Stories to Tickets
For each user story + acceptance criteria in the PRD, find the ticket(s) that cover it. Present as a coverage matrix.

### Step 3: Identify Gaps

Only flag work as a gap if it **cannot be naturally bundled into an existing ticket**. If it's a side effect of implementing an existing ticket, it's not a gap — it's housekeeping that happens during implementation.

### Step 4: Report
- Coverage matrix: user story → ticket(s)
- Gaps: work that cannot be bundled into existing tickets
- Verdict: fully covered / has gaps

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
| Assumptions | Yes | Explicit defaults accepted by user, or explicit deferrals |
| User Flows | Yes | Actor/Surface/Action/Result + Story/AC refs; primary flow includes User/UI/System, Agent when applicable |
| Story-to-Flow Mapping | Yes | Every story maps to flow(s) and AC coverage, or marked "No user flow required" with reason |
| Success Criteria | Yes | Measurable with numbers |
| Constraints | No | Budget, timeline, compliance |

## Validation Rules

- **Name**: 3-8 words, no technical jargon
- **Description**: one line, max 100 chars
- **Problem**: Max 3 sentences, describes user pain not technical gap
- **User Stories**: Format "As a [user], I want [goal], so that [benefit]"; each criterion IDed as `AC-*`
- **AC format**: Plain language bullet — `AC-{n}: [what is true when done]`. Describes observable outcomes (what user sees, what system does). No formal structure needed — `/vorbit:epic` formalizes later
- **AC observability**: Criteria describe what the user or caller observes — not internal state
- **Assumptions**: Only explicit defaults accepted by user, or explicit deferrals
- **User Flows**: At least one flow with Actor/Surface/Action/Result/Story refs/AC refs. Primary flow must include User, UI, and System. Use `Agent` only for explicit agent/model steps; keep normal service/API logic under `System`
- **Flow 1 quality bar**: includes start/end, stable step IDs, explicit API/service touchpoints, and 4-12 state-transition steps
- **Story-to-Flow Mapping**: every user story must map to at least one flow, or be explicitly marked `No user flow required` with reason
- **AC-to-Flow coverage**: every `AC-*` maps to one or more flow steps, or is marked `Non-journey AC` with reason
- **Success Criteria**: Contains measurable numbers (percentages, times, counts)
- **TBD allowed selectively**: `TBD` is fine in Constraints, Success Criteria numbers, and User Flow steps that depend on design decisions. NOT allowed in Problem, Users, or User Stories — those must be concrete
- **TBD question rule**: every `TBD` must have a corresponding `AskUserQuestion` attempt

## User Story Format

```markdown
### US-1: [Title]
As a [user type], I want [goal], so that [benefit].

**Acceptance Criteria:**
- AC-1: [What the user can do or what the system does when done]
- AC-2: [Another observable outcome or constraint]
```

Rules:
- One goal per story
- Each AC is a plain language statement of what "done" looks like
- Describes what user/caller **observes** — not internal state
- Stories map to Linear issues (via /vorbit:implement:epic)
- `/vorbit:epic` formalizes these into MUST/SHOULD + GIVEN/WHEN/THEN specs

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
| `- [ ] AC-1 Form validates email` | `AC-1: User sees error when email is invalid` | ACs describe observable outcomes in plain language |
| `AC-1: isLoading state is set to true` | `AC-1: Loading spinner appears during submission` | Describe what user sees, not internal state |
| `AC-1: Uses MUST/SHOULD + GIVEN/WHEN/THEN` | `AC-1: Preview updates when form changes` | PRD uses plain language — epic formalizes later |
