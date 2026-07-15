<!-- GENERATED from skills/epic/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-epic` skill directory (a sibling of `vorbit-shared`).

# Epic Planning Skill

Transform User Stories from one PRD spec ticket into deterministic implementation-parent trees in Linear.

Read and follow `../references/execution-contract.md` before starting.

> **Linear connector**: Resolve the connected Linear capability per your connector preflight before the first call. Bare verb names below (`get_user`, `list_teams`, `list_issues`, etc.) refer to that connector's operations — inspect its current schema; never substitute a verb remembered from another runtime.

## Step 1: Verify Linear Connection

PRDs live as Linear tickets (see `$vorbit-prd`). Confirm Linear auth before fetching the source ticket: call `get_user` with `query: "me"`. On failure, tell the user to reconnect the Linear connector in Codex and stop.

## Step 2: Gather Context

Linear is the canonical PRD provider. The PRD is a **spec ticket**, not the implementation parent.

Resolve source context in this order:

**IF Linear ticket URL or ID provided:**
1. Use `get_issue` to fetch the PRD spec ticket
2. Extract user stories (`US-###`), each story's acceptance criteria verbatim, its flow steps, constraints, success criteria, and `TBD-###` items

**IF feature name provided (no ticket ID):**
1. Use `list_issues` scoped to the team with a title-based filter to locate the PRD ticket
2. If multiple candidates, ask the user which one via plain-text chat questions
3. Fetch with `get_issue` and extract as above

If a fetched Linear PRD has stories without acceptance criteria, or flows whose steps are an unreadable blob, draft a normalization, show the exact mapping, and get approval to update the spec before planning. Do not change requirement meaning while normalizing.

**IF explicit pasted PRD content or a user-specified local file is provided:**
1. Read it as a legacy fallback and record its provenance
2. Normalize it to `US-###` stories, each with plain acceptance-criteria checkboxes and numbered flow steps, without changing meaning
3. Mark the plan as `canonicalization required`: after user approval, create/import the Linear PRD spec ticket before any implementation parent

**IF no Linear PRD and no explicit legacy artifact exists:** stop and direct the user to `$vorbit-prd`. Do not invent a PRD from casual conversation inside epic planning.

**Traceability requirements before planning:**
- Every user story has at least one acceptance criterion
- Every acceptance criterion is satisfied by at least one flow step, or has an explicit non-journey reason
- Reference a criterion by quoting its text, and a step as `Flow N, step M`. Do not mint IDs the PRD does not have
- If any user story has no criteria, or any criterion has no flow coverage and no reason, resolve it before Step 4

### Implementation-Affecting TBD Gate (Blocking)

Inspect every inline `TBD`, `TBD-###`, "unknown", and unresolved question. A TBD is implementation-affecting when its answer can change observable behavior, AC wording, a flow branch, API/data contracts, issue boundaries, dependencies, file changes, or test criteria.

- Ask focused questions to resolve every implementation-affecting TBD.
- If any remains unresolved, **STOP before codebase analysis and technical planning**. Report the blocking IDs and their impact; do not create an SDD, implementation parents, or sub-issues.
- A genuinely non-blocking TBD may remain only when it cannot change implementation scope or ordering. Carry it into Risks & Unknowns with its explicit classification.

**PRD-first sequencing rule (required):**
- Lock requirement baseline first: each `US-###` -> its acceptance criteria -> the flow steps that satisfy them
- Do NOT start codebase analysis until the requirement baseline is complete
- Codebase analysis is used to implement PRD requirements, not redefine them
- If existing code conflicts with PRD intent, raise the conflict and resolve with user before creating issues

## Step 3: Detect Team's Linear Setup

**Adapt to team's existing patterns with reliable, scoped calls.**

Use Linear MCP in this order:
1. `get_user` with `query: "me"` to verify auth/session
2. `list_teams` (scoped `limit`, for example 10-20) to get candidates
3. Ask user to pick team if multiple teams exist
4. `list_issue_statuses` with selected team
5. `list_issue_labels` with selected team and scoped `limit`
6. `list_projects` with selected team and scoped `limit`

Reliability rules:
- Do NOT run broad, unfiltered workspace-wide listing when team is known
- Keep calls scoped with `team` and `limit`; page only when needed
- On temporary MCP/API error: retry once with the same parameters
- If a non-critical call still fails:
  - statuses missing -> ask user for preferred default workflow states
  - labels missing -> continue without labels and ask user for required labels
  - projects missing -> ask user for project name/ID directly
- Only block execution when auth/team resolution fails

Ask user if unclear: "Which team/project?"

## Step 4: Learn Codebase Style & Discover Reusables

After Step 2 requirement baseline is locked, analyze the codebase thoroughly:

### 4.1 Find Similar Features
Search the codebase using terms from the PRD (story titles, nouns in the criteria, screens named in the flows).
- Note file structure patterns
- Identify naming conventions
- Find test patterns

### 4.2 Discover Reusable Code
Use a **pattern-first, paths-second** strategy:

1. **Find by usage/symbol first (required):**
   - Search imports/usages from the screens named in the PRD flows and the nouns in its criteria
   - Search exported helpers/components/hooks/services, then trace existing call sites
   - Prefer exact symbols already used in similar flows

2. **Then scan common directories (optional heuristic):**
   - Utilities candidates: `src/utils/`, `src/lib/`, `src/helpers/`, `shared/`, `packages/*`
   - UI candidates: `src/components/ui/`, `src/components/common/`, feature-local component folders, `packages/*`
   - If paths don't exist, continue with repo-wide search only

3. **Detect UI library by actual usage (not assumptions):**
   - Infer from imports/usages (for example Radix/Base UI/shadcn/custom primitives)
   - Note which primitives and wrappers are already standard in this repo

4. **Produce reusable inventory for planning:**
   - List candidate utility/component, file path, current usages, and why it fits
   - Mark each as `Reuse`, `Adapt`, or `Do not use`
   - Include confidence and any search gaps (what might be missing)

### 4.3 Discover Constants
Locate the project's constants/config files.
- List relevant constants for this feature
- Identify where new constants should go
- Reuse constants for shared domain values and policy limits; do not create constants for obvious one-off literals

### 4.4 Check for Mock Data
If prototype exists with mock data:
- List all mock locations (`mocks/` folders)
- Include "Swap mock to real API" as sub-issue

### 4.5 Detect UI Work
If feature includes UI components:
- Note: "Reference `$vorbit-ui-patterns` skill"
- Identify existing UI patterns to follow

### 4.6 Map Coupled File Paths (Required)

**Before creating any ticket, identify files that must change together.**

A "coupled pair" is any two files where one file's output/format is consumed by the other. If one changes without the other, the system breaks.

Examples of coupling:
- Script output format ↔ agent recognition string in rules file
- API response shape ↔ client parser
- Config schema ↔ validator

**For each coupled pair:**
1. Identify the **shared contract** (exact string, format, field name, or value both sides depend on)
2. Put both files in the **same sub-issue** — OR — add an explicit cross-reference in both tickets with the exact shared contract value

**Rule:** Never split tightly coupled file changes across separate tickets without explicitly documenting the shared contract in both. Partial implementation of one ticket will break the system until the other is also done.

**For large codebases:** If the dependency graph is unclear, run an independent blast-radius analysis before planning tickets. Who imports what and what consumes each contract matters more than directory guesses.

## Step 5: Create Technical Plan (SDD)

**RULE: If ANY requirement is unclear, use plain-text chat questions. The TBD gate applies (Step 2).**

Create SDD (Specification-Driven Development) document:
- Technical Overview
- Flow Impact Matrix (`Flow N, step M` -> system/module/API/UI touchpoints)
- PRD Compliance Check (confirm all planned changes satisfy the exact `US -> AC -> Flow` baseline)
- Data Model Changes
- API Changes
- Component Breakdown
- Testing Strategy
- Risks & Unknowns

## Step 6: User Review

**CRITICAL: Get approval before creating issues.**

Present plan and ask:
- "Does this approach make sense?"
- "Any concerns?"
- "Ready to create Linear issues?"

Show the full proposed topology before asking: PRD spec ticket -> one implementation parent for each `US-###` -> that parent's executable sub-issues -> that parent's implementation order. If using a legacy fallback, include creation of the canonical Linear PRD spec ticket in this approval.

**DO NOT proceed until user confirms.**

## Step 7: Plan Implementation Parents from User Stories

**Exactly 1 User Story = 1 implementation parent.**

The topology is deterministic:

```text
Linear PRD spec ticket (requirements source; not an implementation parent)
├── US-001 -> implementation parent A -> A's sub-issues -> A's Implementation Order
├── US-002 -> implementation parent B -> B's sub-issues -> B's Implementation Order
└── US-003 -> implementation parent C -> C's sub-issues -> C's Implementation Order
```

The arrows from the PRD are traceability links in each parent's description, not `parentId` nesting. Reserve `parentId` for executable sub-issues under their implementation parent so implement-loop can query one parent tree at a time.

For each User Story, create:
- **Title**: Write a clear, human-readable implementation-parent title derived from the user story goal
- **Description**: User story + related flow context + acceptance criteria + **test criteria (REQUIRED for TDD)**
- **Sub-issues**: Decompose into executable sub-issues when the story needs more than one ordered unit of work. A story that is itself one small executable unit may skip children — the parent then carries its own Test Criteria and acts as the executable node (implement-loop falls back to the parent when a queue is empty). Apply **Parallel** per the criteria at the end of this document

**Verification rule:** Every issue MUST include a `## Test Criteria` section. Behavior tests are written first when the repository has a runnable harness; otherwise specify an honest observable validation method.

**Epic planning inputs per story (required):**
- User story ID (`US-###`)
- The story's acceptance criteria, quoted verbatim from the PRD
- The flow steps from the PRD, with the screen or API each one touches (for example `Flow 1, step 3` — `API /orders`)

**Ticket derivation rule:**
- Use flow steps to identify concrete technical work:
  - UI/component changes
  - API/service changes
  - Data/state changes
  - Error-path handling

### Sub-issue Creation Checklist

Every sub-issue must contain every section shown in the Sub-issue Description Template below (Mock Data only for UI work). No section may be omitted or left as a placeholder.

### Mapping Parent AC to Sub-issues

1. List all parent Acceptance Criteria, quoted verbatim from the PRD
2. List all related flow steps for the story, as `Flow N, step M`
3. For each sub-issue, identify which parent criteria and flow steps it satisfies
4. Copy those criteria **verbatim** into "Related Parent Acceptance Criteria" and the steps into "Related Flow Steps". Quoting the text is what binds a sub-issue to its requirement — do not paraphrase
5. **Rule:** Every parent AC must be covered by at least one sub-issue
6. **Rule:** Every in-scope flow step with implementation impact must be covered by at least one sub-issue

## Step 7.5: Traceability Gate (Required)

Before creating Linear issues, validate this matrix:
- The Step 2 traceability requirements (each `US-###` -> its acceptance criteria -> the flow steps that satisfy them) still hold
- `US-###` -> exactly one planned implementation parent
- Every in-scope flow step -> sub-issue(s) under that story's parent
- Every planned sub-issue -> exactly one implementation parent
- Every remaining TBD -> explicitly non-blocking

If any link is missing, stop and resolve via plain-text chat questions before Step 8.

## Step 8: Create in Linear

Using the approved plan:

1. If the source was a legacy fallback, create the approved Linear PRD spec ticket first. Its URL becomes the canonical PRD reference for every implementation parent.
2. Use `(canonical PRD ID, US-###)` as the idempotency key. Before creating anything, search for an existing indexed parent and resume/repair it rather than duplicating it.
3. Iterate user stories in PRD order. For each `US-###`, create exactly one top-level implementation parent. Do not reuse the PRD spec ticket as a parent and do not combine stories.
4. Create only that story's executable sub-issues with `parentId` = that implementation parent's ID; lookup by planned stable child ID/title before create.
5. Use the team's existing labels/states.
6. **Persist that parent's Implementation Order**: after its sub-issues exist, update that implementation parent's description (`save_issue`) to append its own `## Implementation Order` phased tree with real child IDs. Never put another parent's children in this section. This preserves the existing implement-loop contract; an order that only appears in chat is lost when the session ends.
7. Re-fetch each implementation parent and verify its child IDs and persisted order before moving to the next story.
8. After every parent verifies, re-read the canonical PRD spec ticket and append or replace `## Implementation Parents` with `US-### -> [parent ID and URL]` entries in PRD order. Preserve all existing PRD content. This index is the deterministic link from the spec to its implementation trees.

## Step 9: Report

Present the following:

1. **PRD spec ticket URL** (canonical source)
2. **All implementation parent URLs**, in PRD user-story order, with the owning `US-###`
3. **Per parent:** sub-issue count by priority and its own Implementation Order (the same tree persisted in Step 8 item 6)
4. **Topology verification:** X user stories, X implementation parents, Y total sub-issues; flag any mismatch instead of claiming success

### Implementation Order Format

Implementation order is calculated independently for each implementation parent:

  Phase 1 (Parallel - no dependencies)
  - ABC-101: [Issue title]
  - ABC-102: [Issue title]
  - ABC-103: [Issue title]

  Phase 2 (depends on Phase 1)
  - ABC-104: [Issue title]

  Phase 3 (depends on Phase 2)
  - ABC-105: [Issue title]
  - ABC-106: [Issue title]

**Rules for dependency tree:**
- Phase 1 = issues with no dependencies (can run in parallel)
- Each subsequent phase depends on previous phase completing
- Show `blocked by:` for each issue with dependencies
- Group parallel work within same phase
- Include only children whose `parentId` is the implementation parent being reported

Next: choose one implementation parent and start its Phase 1 using `$vorbit-implement ABC-101`

---

# Epic Schema & Standards

## Implementation Parent Title Format

Transform the user story goal into a clear, human-readable epic title (e.g. "As a user, I want to **login**..." → "User Login").

## Issue Structure

### Implementation Parent (one per User Story)

**Description template:**
```markdown
## User Story
US-001: As a [user], I want [goal]...

## Acceptance Criteria
- [ ] [Criterion, copied verbatim from the PRD]
- [ ] [Another criterion, copied verbatim from the PRD]

## Related PRD Flow Context
| Flow Step | Surface | Why it matters |
|-----------|---------|----------------|
| Flow 1, step 2 | UI: `CheckoutForm` | User submits payment details |
| Flow 1, step 3 | API: `POST /payments` | Payment processing and order creation |

## Test Criteria (TDD - write tests FIRST)

### Unit Tests
- [ ] Unit test: [component behavior]

### E2E Tests
- [ ] E2E: [happy path] — assert observable output, not internal signals
- [ ] E2E: [each flow branch]
- [ ] E2E: [negative case]

## PRD Reference
[Link]

## Implementation Order
Phase 1 (Parallel - no dependencies)
- [ISSUE-ID]: [Issue title]

Phase 2 (depends on Phase 1)
- [ISSUE-ID]: [Issue title]
```

*The `## Implementation Order` section is appended per parent in Step 8 item 6, after that parent's sub-issues exist and their IDs are known.*

### Sub-issue (Child)

**Title**: `component-name` or `step-name` (use **Parallel** label, not prefix)

**Description template:**
```markdown
## Why This Is Needed
**What this does:** [Simple 1-sentence explanation]
**Why it matters:** [Business/user impact - what breaks without this?]

## Related Parent Acceptance Criteria
> This sub-issue must satisfy these goals from the implementation parent:
- [ ] [Parent criterion this sub-issue addresses — copied verbatim, not paraphrased]
- [ ] [Another parent criterion this sub-issue addresses]

## Related Flow Steps
> Implementation context from PRD flow:
- [ ] Flow 1, step 2 — [UI/component step covered]
- [ ] Flow 1, step 3 — [API/service step covered]

⚠️ **Before marking done:** Verify ALL checked items above are satisfied.

## Reuse & Patterns
> Existing code to reference - DO NOT recreate

**Similar features to follow:**
| Reference | Location | What to copy |
|-----------|----------|--------------|
| [Feature] | `src/path/file.tsx` | [Pattern to follow] |

**Utilities to use (don't recreate):**
| Function | Location | Use for |
|----------|----------|---------|
| `validateEmail()` | `src/utils/validation.ts` | Email validation |

**Constants (NO magic numbers):**
| Instead of | Use | Location |
|------------|-----|----------|
| `5` | `MAX_ATTEMPTS` | `src/constants/auth.ts` |
| `"error"` | `MESSAGES.ERROR` | `src/constants/messages.ts` |

⚠️ **New constants:** Add to `src/constants/[category].ts`, don't hardcode.

**UI Patterns (if applicable):**
Run `$vorbit-ui-patterns` before implementing UI components.

## File Changes
| Action | File Path | Purpose |
|--------|-----------|---------|
| CREATE | `src/components/feature/Component.tsx` | Main component |
| MODIFY | `src/api/routes.ts` | Add endpoint |
| CREATE | `src/tests/feature/component.test.ts` | Unit tests |

## Mock Data (if UI work)
| Mock File | Endpoint | Status |
|-----------|----------|--------|
| `src/pages/Feature/mocks/data.json` | `GET /api/resource` | Will create |
| None expected | - | N/A |

> **Handover note:** Run `$vorbit-cleanup-mocks [feature]` before backend takes over.
> Mocks must be registered in the runtime-neutral Vorbit project registry; copy the exact resolved registry path from the prototype/implementation context into this issue. Never hardcode an agent-specific directory.

## Acceptance Criteria (Sub-issue specific)
- [ ] [Criterion this sub-issue alone must satisfy]
- [ ] [Another sub-issue-specific criterion]

## Test Criteria (TDD - write tests FIRST)

### Unit Tests
- [ ] Unit test: [specific behavior]
- [ ] Unit test: [edge case]

### E2E Tests (required if feature involves scripts, hooks, or data parsing)
- [ ] E2E: [happy path] — assert observable output ([file written / state changed]), not just exit code
- [ ] E2E: [each code path / flow branch] — one test per distinct flow
- [ ] E2E: [false positive / negative case] — inputs that must NOT trigger
```

Sub-issue criteria are plain checkboxes. The sub-issue is already a Linear ticket with its own ID and its own parent — that is the handle. Do not mint per-criterion IDs.

**Priority Mapping**:
- P1 (Urgent): Core / Blocker
- P2 (High): Important
- P3 (Normal): Standard

---

## E2E Test Quality Rules

Before writing E2E criteria for any sub-issue, read and apply `references/e2e-test-quality.md` from this skill's installed directory.

---

## Parallel Label Criteria

**Apply Parallel label ONLY when ALL are true:**
1. Sub-issue has NO dependencies on other sub-issues
2. Sub-issue does NOT block other sub-issues
3. Works on separate files/components (no merge conflicts)

**Default: Sequential.** When in doubt, don't add Parallel label.
