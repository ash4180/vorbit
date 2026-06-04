---
name: prd
version: 2.1.0
description: Use when user says "write PRD", "create requirements", "define feature", "document requirements", "product spec", "create ticket", or wants to capture a feature spec as a single Linear ticket. Creates a Linear ticket carrying numbered AC-* acceptance criteria, ordered flow steps with F*-S* IDs + AC tags (Notion-doc format), component mapping intent (kind-of-component per block, NOT concrete DS names — that's /figma's job), state list (empty/loading/error/etc. as TEXT, not mockups), constraints, and success criteria. Treats PRD as agent contract first, engineering spec second.

# PRD Skill

Create a Linear ticket that captures a product requirement. **PRD is the agent contract** — Figma is the visual contract, annotations are the bridge. Per the three-artifact convention (see `[[reference_three_artifact_convention]]`), PRD owns *intent + requirements*: numbered `AC-*`, ordered flow steps, state list, component mapping intent. Figma owns *the look*. Don't put visuals here; don't put rules in Figma.

> **Linear MCP namespace**: All Linear calls in this skill use `mcp__plugin_linear_linear__*` (the namespace shipped with the vorbit plugin). Bare verb names below (`get_user`, `list_teams`, `save_issue`, etc.) refer to the corresponding `mcp__plugin_linear_linear__<verb>` tool.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

> **UX patterns reference**: Senior UX product designer knowledge lives in `_shared/ux-knowledge/`. When building Step 2 clarifying questions, consult `question-matrix.md` (14 categories). When checking AC + state completeness in Step 3, consult `edge-case-catalog.md`. When phrasing ACs (verbatim user-words rule), consult `ux-philosophy.md`. Read directly — no need to invoke `/vorbit:design:ux` unless requirements are deeply vague.

## Step 1: Gather Context (Draft First)

The goal is a drafted PRD before touching Linear. Connection problems must never block drafting.

**IF a Linear ticket URL or ID is provided (existing draft, similar feature, etc.):**
1. Use `get_issue` to fetch the source ticket and read its description for context
2. Restructure: keep the source intent, normalize wording to the schema below, mark gaps as `TBD`

**IF the user pastes content from elsewhere (Notion, a doc, an old spec):**
1. Use the pasted text directly as input — the skill's Linear-only `allowed-tools` cannot fetch external docs
2. Ask the user for any sections they referenced but did not paste, then restructure as above

**IF the source is an `/explore` exploration document** (visual moodboard with `blocks_mined[]`, `flow_steps[]`, `references[]`, `recommended_direction` from `/vorbit:design:explore`):
1. **Consume the structured fields directly** — don't re-ask what /explore already captured:
   - `flow_steps[]` → seeds the User Flows section. /explore writes plain-English ordered steps; /prd assigns `F*-S*` IDs (Flow-N, Step-M) and adds `[AC-X]` tags as ACs get written in Step 3.
   - `blocks_mined[]` (grain-tagged, with embedded screenshots) → seeds the **Component Mapping Intent** section. Each block becomes one row; PRD records the *intent* ("what kind of component this block needs"), NOT a concrete DS name. /figma's Phase 2 resolves intent → DS later.
   - `recommended_direction` → seeds the Description and first User Story.
   - `references[]` → kept as a link or short attribution block; not restated in the PRD body. PRD is implementation spec, not research artifact.
2. **No `lo_fi_figma_url` is expected.** Earlier /explore versions produced lo-fi mockups — that's been dropped in the 2026-05 redesign because lo-fi adds no value when a complete linked DS is available. If a lo-fi URL appears in an older /explore output, ignore it.

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
6. **Design source** — for UI work, exact Figma/file/mockup nodes and which node is source of truth
7. **Success metrics** — measurable outcomes

### Design-source rules

If the feature changes UI, layout, visual hierarchy, component composition, or user-visible states:
- Ask for the exact Figma URL and node ID for each affected surface. Do not accept "like the mockup" as sufficient.
- Identify whether the node is a page, frame, component, variant, or nested card/block.
- Ask for the parent frame/user-flow context when a node is only a nested block and the surrounding flow is unclear.
- Ask which node wins when written ticket text conflicts with the mockup.
- Capture responsive behavior, states/variants, empty/error/loading states, and explicitly out-of-scope design pieces.
- If no mockup exists, ask whether the agent should use existing product patterns or wait for design. Mark unresolved design as `TBD-design`.

For API/backend-only work:
- Do not require a Figma node unless the API response directly controls user-visible fields, state, copy, or layout.
- If the API supports a designed UI, capture the design-derived contract: fields, states, ordering, error cases, and copy the UI needs.

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
- **User Stories**: `US-001`, `US-002`, ... each with `AC-N` items (numbered globally across the PRD so /figma annotations can reference them as `implements: AC-X`)
- **User Flows**: at least one flow with **`F*-S*` step IDs** and `[AC-X]` tags per step (Notion-doc format — see template). Entry/Exit anchors kept for human scanning.
- **State List**: ordered list of every UI state the feature touches (default / loading / empty / error / permission-denied / etc.) tagged with the AC each state is governed by. **Text only — no mockups.** Figma stays happy-path.
- **Component Mapping Intent**: per block from `/explore`, declare the *kind* of component needed (intent), NOT the concrete DS name. /figma's Phase 2 resolves intent → DS.
- Design Source of Truth: lighter than before — for UI work, the *target surface* and *conflict rule*, but not "what to design" prose (the lo-fi flow / blocks_mined already describes it).
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

## Design Source of Truth

Required only when UI, layout, component composition, or visual states are in scope.

* **Primary Figma node:** [URL with exact `node-id`, or `N/A` for non-UI work]
* **Parent flow/frame:** [Figma parent frame/page/user flow that explains where this node lives]
* **Implementation target:** [screen/pane/component/block the node applies to]
* **States/variants required:** [default, empty, loading, error, selected, responsive breakpoints]
* **Interaction flow:** [entry point, user action, visible result, exit state]
* **Design conflicts:** [which source wins if ticket text and Figma disagree]
* **Out of scope:** [nearby mockup parts that should not be implemented]

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

Use the Notion-doc format: each step has an `F*-S*` ID and `[AC-X]` tags. Keep Entry/Exit anchors at the flow level for human scanning, but make the per-step format machine-parseable so `/vorbit:design:figma` (Flow Page generation) and `/vorbit:implement:epic` (Related Flow Steps) can consume it without inference.

### Flow F1: [Name] (Happy flow)

**Entry:** [Start screen]
**Exit:** [End state]

- **F1-S1**: [Surface] → [User action] → [Visible result] [AC-1, AC-2]
- **F1-S2**: [Surface] → [User action] → [Visible result] [AC-3]
- **F1-S3**: [Surface] → [User action] → [Visible result] [AC-4]

### Flow F2: [Name] (Second main path or alternate)

**Entry:** [Start]
**Exit:** [End]

- **F2-S1**: [Surface] → [User action] → [Visible result] [AC-5]
- **F2-S2**: Server returns error → Error toast, values preserved [AC-6]

## State List

Every UI state the feature touches, tagged by the AC governing it. **Text only — Figma stays happy-path; /implement renders each state per AC.**

| State | Triggers | Governing AC |
|-------|----------|--------------|
| Default (happy) | First load, data present | AC-1 |
| Empty | User has no items yet | AC-7 |
| Loading | API in flight (>200ms) | AC-8 |
| Error | API returns 5xx or network fails | AC-9 |
| Permission denied | User lacks `read:foo` scope | AC-10 |

## Component Mapping Intent

For each block surfaced by `/explore`'s `blocks_mined[]`, declare the *kind of component* the block needs. **No concrete DS names** — `/vorbit:design:figma`'s Phase 2 resolves intent → DS using the linked library inventory.

| Block (from /explore) | Intent (what kind of component) | Governing AC |
|-----------------------|----------------------------------|--------------|
| `search-with-filters` (Linear inbox pattern) | Search input with inline filter chips, multi-select | AC-1, AC-2 |
| `empty-state-onboarding` (Notion onboarding pattern) | Empty hero + illustration + primary CTA | AC-7 |
| `activity-timeline` (custom) | Vertical activity feed with timestamps; no DS match anticipated — /figma may propose new DS component | AC-11 |

## Constraints

* [Constraint with reason — what cannot change]
* [Constraint about backend, design, timeline, etc.]

## Success Criteria

* [Measurable target with a number]
* [Another measurable target]
```

Flow rules, TBD rules, and per-section validation live in the **Schema & Validation** section below — read it before drafting.

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
  - `/vorbit:design:journey` to draw a flow diagram in Excalidraw

---

## Coverage Review Mode

When asked to review whether sub-issues fulfill a parent PRD ticket:

1. Read the parent ticket (`get_issue`) and all sub-issues (`list_issues` with the parent's `parentId`)
2. Map each User Story and `AC-N` to the sub-issue(s) covering it
3. Flag work that **cannot be bundled** into an existing sub-issue as a gap; bundle-able housekeeping is not a gap
4. Report: coverage matrix (story → sub-issues), gaps, verdict (covered / has gaps)

---

# Schema & Validation

**Read this section before drafting in Step 3.** Without these required sections and validation rules, the PRD ticket doesn't carry the structure that `/vorbit:implement:epic` needs to break it into traceable sub-issues. A passing draft skips no required section and trips no validation rule below.

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Title (H1) | Yes | 3-8 words, no jargon. Becomes Linear ticket title. |
| Description | Yes | 1-2 short sentences, no tech detail |
| Problem | Yes | 1-2 short paragraphs, user pain not tech gap |
| Design Source of Truth | If UI work | Target surface + conflict rule. Light. The visual contract lives in Figma; PRD doesn't replicate it. |
| User Stories | Yes | `As a [user], I want ..., so ...` plus `AC-N` items, numbered globally |
| User Flows | Yes | At least one flow in **Notion-doc format** — `F*-S*` step IDs + `[AC-X]` tags per step, Entry/Exit anchors at flow level |
| State List | Yes (UI work) | Every UI state (default/loading/empty/error/etc.) as text, tagged by governing AC. NOT mockups. |
| Component Mapping Intent | Yes (UI work) | Per block from /explore, intent only (kind of component). No concrete DS names. |
| Constraints | Yes | Limits the implementation must respect |
| Success Criteria | Yes | Measurable with numbers |

## Validation Rules

- **Title**: 3-8 words, no jargon
- **Description**: short, plain English, no tech detail
- **Problem**: describes user pain, not the technical fix
- **Design Source of Truth**: required for UI work — target surface and conflict rule. Doesn't replicate the visual; that's Figma's job.
- **User Stories**: `As a [user], I want [goal], so [benefit]`. Each story has at least one `AC-N`. AC numbering is **global** across the PRD (`AC-1` through `AC-N`), not per-story — so `/figma` annotations and `/epic` sub-issues can reference any AC unambiguously.
- **User Flows**: at least one. Notion-doc format: `F*-S*` step IDs + `[AC-X]` tags per step. 3-8 steps per flow is the sweet spot.
- **AC coverage**: every `AC-N` should appear in at least one step's `[AC-X]` tag AND in the State List (if it governs a state) — orphan ACs are a coverage gap caught at /verify time.
- **State List**: every UI state the feature touches, text only, tagged by AC. No state mockups in Figma.
- **Component Mapping Intent**: each block from /explore gets a row with the intent string; never a concrete DS component name.
- **Success Criteria**: contain real numbers (percentages, times, counts)
- **TBD**: allowed in Constraints, Success Criteria numbers, and flow details only — never in Problem, Users, or User Stories. Every `TBD` must have a matching `AskUserQuestion` attempt

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| "We need JWT auth" | "Users cannot access personalized features without accounts" | Problem describes user pain, not the technical fix |
| "Users should be happy with login" | "90% of users complete login in under 10 seconds" | Success criteria need real numbers |
| "OAuth2 JWT Token Auth Implementation" | "User Login and Signup" | Title avoids jargon |
| Flow as system trace (`User → API → DB → API → User`) | `**F1-S1**: Login screen → Click Submit → Loading state → Token returned [AC-1, AC-2]` | Flows describe what the user sees, with `F*-S*` IDs and `[AC-X]` tags per step |
| `component_mappings: ShadcnInput + Badge` | `component_mapping_intent: "search input with inline filter chips, multi-select"` | PRD declares intent; /figma's Phase 2 resolves to concrete DS names from the linked library |
| Empty state in Design Source of Truth as a Figma node | Empty state in **State List** as text + governing AC | States are PRD concerns (text); Figma stays happy-path; code renders each state per AC |
| "Match Figma" | "Example: Implement Figma node `<primary-node-id>` exactly for `<target surface>`; `<reference-node-id>` is reference only; `<specific layout/state rule>` must come from the primary node" | Agents need a concrete source of truth and conflict rule |
