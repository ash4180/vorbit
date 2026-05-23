---
name: epic
version: 1.7.0
description: Transform a PRD's user stories into Linear epics and sub-issues. Use whenever the user wants to break down a PRD, create Linear tickets, plan a sprint, decompose a feature into tasks, set up an epic, or convert a user story into implementation work — even if they don't say "epic" explicitly. Common triggers include "create issues", "break down PRD", "set up epic", "epic from VIB-XXX", "create Linear tasks", "plan sprint", "decompose this feature", "sub-issues for this story", "turn this PRD into tickets". Consumes the redesigned PRD + Figma schemas (AC-*, F*-S* flow_steps, state_list, component_mapping_intent from PRD; Flow Page, approved mapping_table, Dev Mode `implements: AC-X` annotations from Figma) without re-asking — output schema for sub-issues is unchanged.
---

# Epic Planning Skill

Transform User Stories (from PRD) into executable Engineering Tasks (Epics/Issues) in Linear.

> **Linear MCP namespace**: All Linear calls in this skill use `mcp__plugin_linear_linear__*` (the namespace shipped with the vorbit plugin). Bare verb names below (`get_user`, `list_teams`, `list_issues`, etc.) refer to the corresponding `mcp__plugin_linear_linear__<verb>` tool.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

> **Templates and standards**: All issue body templates, validation rules, the Parallel-label criteria, TDD requirements, and E2E test quality rules live in `./output-schema.md` (sibling of this file). Read it before Step 7 (Plan Epics) and Step 8 (Traceability Gate). Skipping causes a known failure mode — the agent invents its own issue templates, drops the Required Sections table, or fabricates validation rules that don't match the team's standards. The schema is what makes tickets reviewable.

## Step 1: Gather Context

**IF Linear ticket URL or ID provided:**
1. Use `get_issue` to fetch the parent ticket
2. Extract from the description (PRD v2.1.0+ schema, see `/vorbit:design:prd`):
   - User stories (`US-*` IDs)
   - Acceptance criteria (`AC-*` IDs, numbered globally across the PRD)
   - User Flows — ordered steps with `F*-S*` IDs and `[AC-X]` tags per step (Notion-doc format). These become "Related Flow Steps" in sub-issues.
   - **State List** — text-only enumeration of every UI state (default / empty / loading / error / permission-denied / etc.) tagged by the governing AC. Feeds sub-issue "Design Source of Truth → states" directly; do NOT infer states from PRD prose if the State List exists.
   - **Component Mapping Intent** — per-block intent (what kind of component each block needs, no concrete DS name). /figma's Phase 2 resolves intent → concrete DS in the mapping_table; if a Figma file is linked, prefer Figma's resolved table (see Step 3.7).
   - Constraints and success criteria

**IF feature name provided (no ticket ID):**
1. Use `list_issues` scoped to the team with a title-based filter
2. If multiple candidates, ask the user via `AskUserQuestion`
3. Fetch with `get_issue` and extract as above

**IF no PRD ticket exists:**
1. Ask the user if they want to create the PRD first via `/vorbit:design:prd` — recommend that path so the source of truth lives in Linear
2. If the user skips PRD, gather requirements via conversation and capture them inline so the epic still has US/AC/flow content to trace against

**Traceability pre-flight (lightweight check, not the gate):**
The authoritative validation runs in Step 8 against the matrix in `./output-schema.md → Validation Rules`. Here, just catch obvious gaps as you extract — so broken data doesn't carry through Step 3:
- A user story missing any `AC-*` at all
- A user story whose flows clearly don't cover its ACs
- UI/design stories with no Figma node IDs and no `TBD-design` marker

If any surface, raise immediately with `AskUserQuestion` rather than proceeding.

**PRD-first sequencing rule:**
- Lock requirement baseline first: `US-* → AC-* → Flow`
- Do NOT start codebase analysis until the requirement baseline is complete
- Codebase analysis implements PRD requirements, it does not redefine them
- If existing code conflicts with PRD intent, raise the conflict and resolve with user before creating issues

**Design-source extraction (required for UI work):**
- Extract every Figma URL/node ID from the PRD, parent ticket comments, and user request
- For each visual surface, record the primary node, any reference-only nodes, and the implementation target it controls
- If the PRD references a design without naming exact Figma node IDs (regardless of phrasing — screenshots only, "match Figma", "like the mockup", "same design as X", etc.), ask the user for the exact node before creating UI sub-issues
- If written AC conflicts with the Figma node, stop and ask which source wins — do not silently average the two
- For API/backend work, carry Figma references only when the API must support specific visible fields, ordering, states, errors, or copy from the design

## Step 2: Detect Team's Linear Setup

Adapt to the team's existing patterns with reliable, scoped calls.

Use Linear MCP in this order:
1. `get_user` with `query: "me"` to verify auth/session
2. `list_teams` (scoped `limit`, e.g. 10-20) to get candidates
3. Ask user to pick team if multiple teams exist
4. `list_issue_statuses` with selected team
5. `list_issue_labels` with selected team and scoped `limit`
6. `list_projects` with selected team and scoped `limit`

Reliability rules:
- Do NOT run broad, unfiltered workspace-wide listing when team is known
- Keep calls scoped with `team` and `limit`; page only when needed
- On temporary MCP/API error: retry once with the same parameters
- If a non-critical call still fails:
  - statuses missing → ask user for preferred default workflow states
  - labels missing → continue without labels and ask user for required labels
  - projects missing → ask user for project name/ID directly
- Only block execution when auth/team resolution fails

Ask user if unclear: "Which team/project?"

## Step 3: Learn Codebase Style & Discover Reusables

After the Step 1 requirement baseline is locked, analyze the codebase. Cover all of the following before moving on.

### 3.1 Find Similar Features
Build search terms from PRD (US titles, AC nouns, flow surfaces):
```bash
rg -n "<term1>|<term2>|<term3>" .
```
Note file structure patterns, naming conventions, and test patterns.

### 3.2 Discover Reusable Code
Pattern-first, paths-second:
1. **Find by usage/symbol first (required):** search imports/usages from PRD flow surfaces and AC terms; search exported helpers/components/hooks/services and trace existing call sites; prefer symbols already used in similar flows.
2. **Then scan common directories (optional):** utilities in `src/utils/`, `src/lib/`, `src/helpers/`, `shared/`, `packages/*`; UI in `src/components/ui/`, `src/components/common/`, feature-local folders. If paths don't exist, continue with repo-wide search.
3. **Detect UI library by actual usage**, not assumptions — infer from imports (Radix/Base UI/shadcn/custom primitives) and note which primitives are standard in this repo.
4. **Produce reusable inventory for planning** — list candidate utility/component, file path, current usages, why it fits; mark each `Reuse`, `Adapt`, or `Do not use`; include confidence and search gaps.

### 3.3 Create FE Architecture Blueprint (required for UI work)
Before creating UI/component/composition sub-issues, build the blueprint following the structure in `_shared/frontend-knowledge/architecture-blueprint.md`. It defines the six required areas (reuse/create matrix, component hierarchy, data/API contract, state ownership, design-system mapping, test seams) and explains why each one matters.

**Seed the Reuse/Create matrix from `/figma`'s approved `mapping_table[]`** (see Step 3.7). Each row in the mapping_table — `block_name → DS resolution` (concrete component) — becomes a row in the Reuse/Create matrix with status `Reuse`. Blocks marked `propose new DS component` in the mapping_table become `Create` rows. This eliminates the failure mode where /epic re-derives components from the lo-fi or hi-fi mockup and reaches for generic names instead of the DS-resolved ones the user already signed off on.

If the blueprint cannot be filled from Figma's mapping_table + PRD + codebase search, ask the user before creating implementation-ready issues. A "needs user input" entry is more useful than a confident wrong guess.

### 3.4 Discover Constants (NO MAGIC NUMBERS)
```bash
find . -name "constants*" -o -name "config*" | head -20
```
List relevant constants. Identify where new constants should go. **Rule:** every hardcoded value must reference a constant.

### 3.5 Check for Mock Data
If a prototype exists with mock data, list all mock locations (`mocks/` folders) and include "Swap mock to real API" as a sub-issue.

### 3.6 Detect UI Work
If the feature includes UI components, queue these reads for the implementing agent:
- `_shared/frontend-knowledge/ui-patterns.md`
- If `react` is in `package.json`: also `_shared/frontend-knowledge/react-best-practices/index.md` for performance rules

Identify existing UI patterns to follow.

### 3.7 Analyze Figma Source of Truth (required for UI work)
For UI, layout, component, composition, or block build-up work, read `references/figma-source-of-truth.md` (in this skill folder) before creating issues. It covers:

- The 10-step source-of-truth analysis procedure
- The design evidence matrix shape (rendered inside tickets via `output-schema.md → Design Source of Truth`)
- Conflict, structure/flow, API/backend contract, and mockup-missing rules
- When a Figma node ID is required regardless of how the PRD references the design

**Consume `/figma` v1.6.0+ structured outputs (the redesigned Figma chain produces these):**
- **`mapping_table[]`** — the user-approved block→DS-component resolution from /figma's Phase 2 mapping gate. This is the source of truth for concrete DS names; use it to seed the FE Architecture Blueprint Reuse/Create matrix (see Step 3.3). NOT re-derived from frame inspection — that's how the v1.5.0 ignore-DS failure leaked.
- **Flow Page frame** — one dedicated frame at the file root named `Flow` (or `Flow Page`) listing the canonical journey with `[AC-X]` tags per step. Read it via `mcp__figma__get_metadata` and use the steps directly as "Related Flow Steps" in sub-issues (instead of inferring from frame names or page hierarchy).
- **Dev Mode `implements: AC-X` annotations** — every interactive element in the Figma file should have one. Read them via `get_metadata`'s `annotations` field (per `[[reference_figma_metadata_authoritative_fields]]`). Use them to populate sub-issue "Design Source of Truth → states / target surface / conflicts" — annotations are the ground truth for which frame implements which AC. **Pin-style canvas annotations don't work**; only Dev Mode does.

Apply every step in `figma-source-of-truth.md`. If any element is unclear from Figma + PRD, ask the user before creating UI sub-issues.

## Step 4: Map Coupled File Paths (Required)

Before creating any ticket, identify files that must change together.

A "coupled pair" is any two files where one file's output/format is consumed by the other. If one changes without the other, the system breaks.

Examples of coupling:
- Script output format ↔ agent recognition string in rules file
- API response shape ↔ client parser
- Config schema ↔ validator

For each coupled pair:
1. Identify the **shared contract** (exact string, format, field name, or value both sides depend on)
2. Put both files in the **same sub-issue** — OR — add an explicit cross-reference in both tickets with the exact shared contract value

**Rule:** Never split tightly coupled file changes across separate tickets without explicitly documenting the shared contract in both.

**For large codebases:** If the dependency graph is unclear, spawn a team or use `/vorbit:review` to map it before planning tickets.

## Step 5: Create Technical Plan on Ticket (SDD)

If any requirement is unclear at this point, stop and use `AskUserQuestion` — the SDD doc is downstream of clear requirements, not a way to make vague ones concrete.

Create the SDD following the structure in `./output-schema.md → SDD Document Structure`. It lists every required section (Technical Overview, Flow Impact Matrix, Design Evidence Matrix, FE Architecture Blueprint, PRD Compliance Check, Data Model Changes, API Changes, Component Breakdown, Testing Strategy, Risks & Unknowns) and where each one draws its content from.

## Step 6: User Review

**CRITICAL: Get approval before creating issues.**

Present the plan and ask:
- "Does this approach make sense?"
- "Any concerns?"
- "Ready to create Linear issues?"

**DO NOT proceed until the user confirms.**

## Step 7: Plan Epics from User Stories

**Read `./output-schema.md` now.** It holds the Title Format table, the Epic (Parent) and Sub-issue (Child) description templates, the Required Sections table, the Priority Mapping, the Parallel Label Criteria, the TDD Requirement, and the E2E Test Quality Rules. Populate templates from there.

**1 User Story = 1 Epic.**

For each User Story, prepare:
- **Title** — per the Title Format table in `output-schema.md`
- **Description** — populate the Epic (Parent) description template with the user story, related flow context, acceptance criteria, and **Test Criteria** (required for TDD)
- **Sub-issues** (if complex) — populate the Sub-issue (Child) description template for each. Apply the **Parallel** label only when the Parallel Label Criteria are met.

**Epic planning inputs per story (required):**
- User story ID (`US-*`)
- Relevant AC IDs (`AC-*`)
- Flow step IDs and surfaces from PRD (e.g. `F1-S3`, `API /orders`)

**Ticket derivation rule:**
Use flow steps to identify concrete technical work — UI/component changes, API/service changes, data/state changes, error-path handling.

**Mapping Epic AC to Sub-issues:**
1. List all Epic Acceptance Criteria (`AC-*`)
2. List all related flow steps for the story (`F*-S*`)
3. For each sub-issue, identify which Epic ACs and flow steps it satisfies
4. Copy those specific ACs into "Related Epic AC" and flow steps into "Related Flow Steps"
5. **Rule:** Every Epic AC must be covered by at least one sub-issue
6. **Rule:** Every in-scope flow step with implementation impact must be covered by at least one sub-issue

## Step 8: Traceability Gate (Required)

**Read `./output-schema.md` → Validation Rules** and check every link in the matrix:
- `US-*` → `AC-*`
- `AC-*` → flow steps `F*-S*` (or explicit non-journey reason)
- Flow steps → sub-issue(s)
- UI flow steps → Figma source node(s) or explicit `TBD-design`
- Every coupled file pair → either bundled in one sub-issue OR cross-referenced in both with the shared contract

If any link is missing, stop and resolve via `AskUserQuestion` before Step 9.

## Step 9: Create in Linear

Using the plan from Steps 7 + 8:
1. Create the parent issue (epic) first
2. Create sub-issues with `parentId` = epic ID
3. Use the team's existing labels/states (collected in Step 2)

## Step 10: Report

Present the following:
1. **Parent issue URL**
2. **Sub-issue count:** X total (P1: Y, P2: Z, P3: W)
3. **PRD ticket URL** (the source Linear ticket the epic was derived from)
4. **Implementation Order** — populate using the format in `output-schema.md → Implementation Order Format` (Phase 1/2/3 tree with `blocked by:` lines)

Next: Start with Phase 1 issues using `/vorbit:implement:implement ABC-101`
