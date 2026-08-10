<!-- GENERATED from skills/epic/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-epic` skill directory (a sibling of `vorbit-shared`).

# Epic Planning Skill

Transform User Stories from the branch PRD spec into a deterministic, ordered task plan in `epic.md`.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/spec-files.md` for spec path resolution, write guards, identifiers, and status fields before any spec read or write.

Read `../references/glossary.md`: use the project's `CONTEXT.md` glossary terms when it exists, and record newly agreed terms there.

## Step 1: Locate the Branch PRD

PRDs live as branch spec files written by `$vorbit-prd`. Resolve the spec folder per `../references/spec-files.md`:

- **IF `prd.md` exists** in the branch spec folder: it is the requirements source.
- **IF it is missing**: run `git worktree list` and report any sibling worktree that may hold it. If none does, and no legacy artifact or technical description was supplied (Step 2), direct the user to `$vorbit-prd` and stop.

## Step 2: Gather Context

The branch `prd.md` is the canonical PRD.

Resolve source context in this order:

**IF the branch `prd.md` exists:**
1. Read it
2. Extract user stories (`US-###`), each story's acceptance criteria verbatim, its flow steps, constraints, success criteria, and `TBD-###` items

**IF explicit legacy content is provided instead (a Linear ticket URL, pasted PRD content, or a user-specified local file):**
1. Read it as a legacy import and record its provenance (for a Linear ticket, direct the user to run `$vorbit-prd <ticket>` when the import needs restructuring beyond mechanical normalization)
2. Normalize it to `US-###` stories, each with plain acceptance-criteria checkboxes and numbered flow steps, without changing meaning
3. Mark the plan as `canonicalization required`: after user approval, write the normalized PRD to the branch `prd.md` (per the prd skill's schema) before writing any epic plan

If the PRD has stories without acceptance criteria, or flows whose steps are an unreadable blob, draft a normalization, show the exact mapping, and get approval to update `prd.md` before planning. Do not change requirement meaning while normalizing.

**IF no product PRD but the user explicitly provides a technical work description** (pasted spec, a named file, or explicit scope in the command arguments — e.g. a migration, upgrade, or refactor with no user-facing stories):
1. Write that description verbatim into the epic plan's baseline section under a `Technical epic — no product PRD` label
2. The baseline must contain explicit acceptance-criteria checkboxes; if the description lacks them, draft them from its stated outcomes and confirm with the user before writing the plan. Tasks quote these verbatim as usual
3. Do not invent `US-###` stories or user flows for it. Create one story section for the technical scope (or one per explicitly named workstream) headed `TS-001`, `TS-002`, ...; the TBD gate, verbatim criterion quoting, and Implementation Order apply unchanged, with the baseline section as what `$vorbit-verify` and implement-loop bind to

**IF no branch PRD, no explicit legacy artifact, and no explicit technical description:** stop and direct the user to `$vorbit-prd`. Do not invent requirements from casual conversation inside epic planning.

**Traceability requirements before planning:**
- Every user story has at least one acceptance criterion
- Every acceptance criterion is satisfied by at least one flow step, or has an explicit non-journey reason
- Reference a criterion by quoting its text, and a step as `Flow N, step M`. Do not mint IDs the PRD does not have
- If any user story has no criteria, or any criterion has no flow coverage and no reason, resolve it before Step 4

### Implementation-Affecting TBD Gate (Blocking)

Inspect every inline `TBD`, `TBD-###`, "unknown", and unresolved question. A TBD is implementation-affecting when its answer can change observable behavior, AC wording, a flow branch, API/data contracts, task boundaries, dependencies, file changes, or test criteria.

- Ask focused questions to resolve every implementation-affecting TBD.
- If any remains unresolved, **STOP before codebase analysis and technical planning**. Report the blocking IDs and their impact; do not create an SDD or any epic plan.
- A genuinely non-blocking TBD may remain only when it cannot change implementation scope or ordering. Carry it into Risks & Unknowns with its explicit classification.

**PRD-first sequencing rule (required):**
- Lock requirement baseline first: each `US-###` -> its acceptance criteria -> the flow steps that satisfy them
- Do NOT start codebase analysis until the requirement baseline is complete
- Codebase analysis is used to implement PRD requirements, not redefine them
- If existing code conflicts with PRD intent, raise the conflict and resolve with user before writing the plan

## Step 3: Check for an Existing Plan

If `epic.md` already exists in the spec folder, this run is a **revision**:

1. Read it fully before planning
2. Preserve existing task IDs — never renumber; new tasks get fresh IDs continuing the sequence
3. Preserve the `**Status:**` line of every task that is `in-progress` or `done`
4. If a `done` task's work would be dropped or materially changed, list it and ask before proceeding
5. Show removed, changed, and added tasks explicitly in the Step 6 review

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
- Include "Swap mock to real API" as a task

### 4.5 Detect UI Work
If feature includes UI components:
- Note: "Reference `$vorbit-ui-patterns` skill"
- Identify existing UI patterns to follow

### 4.6 Map Coupled File Paths (Required)

**Before writing any task, identify files that must change together.**

A "coupled pair" is any two files where one file's output/format is consumed by the other. If one changes without the other, the system breaks.

Examples of coupling:
- Script output format ↔ agent recognition string in rules file
- API response shape ↔ client parser
- Config schema ↔ validator

**For each coupled pair:**
1. Identify the **shared contract** (exact string, format, field name, or value both sides depend on)
2. Put both files in the **same task** — OR — add an explicit cross-reference in both tasks with the exact shared contract value

**Rule:** Never split tightly coupled file changes across separate tasks without explicitly documenting the shared contract in both. Partial implementation of one task will break the system until the other is also done.

**For large codebases:** If the dependency graph is unclear, run an independent blast-radius analysis before planning tasks. Who imports what and what consumes each contract matters more than directory guesses.

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

**CRITICAL: Get approval before writing the plan file.**

Present plan and ask:
- "Does this approach make sense?"
- "Any concerns?"
- "Ready to write the epic plan?"

Show the full proposed topology before asking: branch `prd.md` -> one story section for each `US-###` -> that section's executable tasks -> that section's implementation order. If using a legacy fallback, include writing the canonical branch `prd.md` in this approval. For a revision (Step 3), show removed/changed/added tasks.

**DO NOT proceed until user confirms.**

## Step 7: Plan Story Sections from User Stories

**Exactly 1 User Story = 1 story section in `epic.md`.**

The topology is deterministic:

```text
prd.md (requirements source; never edited by this skill except approved canonicalization)
└── epic.md
    ├── US-001 -> story section A -> A's tasks -> A's Implementation Order
    ├── US-002 -> story section B -> B's tasks -> B's Implementation Order
    └── US-003 -> story section C -> C's tasks -> C's Implementation Order
```

Story sections reference the PRD by quoting it; tasks live inside their story section so implement-loop can queue one story at a time.

For each User Story, create:
- **Section title**: `## US-###: [clear, human-readable title derived from the story goal]`
- **Section header**: user story + related flow context + acceptance criteria + **test criteria (REQUIRED for TDD)**
- **Tasks**: Decompose into executable tasks when the story needs more than one ordered unit of work. A story that is itself one small executable unit gets a single task carrying its Test Criteria. Apply **Parallel** per the criteria at the end of this document
- **Slice vertically**: prefer tasks that cut one narrow but complete path through every layer the story touches (data → API → UI → test), so each finished task is demoable or verifiable on its own. Avoid tasks that build a single layer with nothing observable. Exception — a wide mechanical refactor (rename, retype) that breaks many call sites at once: sequence it as expand (add new form beside old) → migrate call sites in batches → contract (delete old form), each its own task

**Verification rule:** Every story section and every task MUST include a `## Test Criteria` section. Behavior tests are written first when the repository has a runnable harness; otherwise specify an honest observable validation method.

**Test quality rules (every Test Criteria section):**
- Unit tests mock only at the network edge (fake the API answer, never the app's own modules); every story includes at least one test that exercises the real API or the full integrated path
- UI test criteria treat an unexpected browser-console error as a failure, even when the screen looks right

**Epic planning inputs per story (required):**
- User story ID (`US-###`)
- The story's acceptance criteria, quoted verbatim from the PRD
- The flow steps from the PRD, with the screen or API each one touches (for example `Flow 1, step 3` — `API /orders`)

**Task derivation rule:**
- Use flow steps to identify concrete technical work:
  - UI/component changes
  - API/service changes
  - Data/state changes
  - Error-path handling

### Task Creation Checklist

Every task must contain every section shown in the Task Template below (Mock Data only for UI work). No section may be omitted or left as a placeholder.

### Mapping Story AC to Tasks

1. List all story Acceptance Criteria, quoted verbatim from the PRD
2. List all related flow steps for the story, as `Flow N, step M`
3. For each task, identify which story criteria and flow steps it satisfies
4. Copy those criteria **verbatim** into "Related Story Acceptance Criteria" and the steps into "Related Flow Steps". Quoting the text is what binds a task to its requirement — do not paraphrase
5. **Rule:** Every story AC must be covered by at least one task
6. **Rule:** Every in-scope flow step with implementation impact must be covered by at least one task

## Step 7.5: Traceability Gate (Required)

Before writing `epic.md`, validate this matrix:
- The Step 2 traceability requirements (each `US-###` -> its acceptance criteria -> the flow steps that satisfy them) still hold
- `US-###` -> exactly one planned story section
- Every in-scope flow step -> task(s) inside that story's section
- Every planned task -> exactly one story section
- Every remaining TBD -> explicitly non-blocking

If any link is missing, stop and resolve via plain-text chat questions before Step 8.

## Step 8: Write the Epic Plan

Using the approved plan:

1. If the source was a legacy fallback, write the approved canonical `prd.md` first (prd schema). It becomes the requirements reference for the whole plan.
2. Run the write guards per `../references/spec-files.md` (branch, protected-branch check, `.gitignore` line).
3. Write `epic.md` per the Epic Schema below: header (including the `Outcome:` gist copied from the PRD's Problem and Description), then story sections in PRD order, each with its tasks and its own `## Implementation Order` using real task IDs. Every new task starts with `**Status:** pending`.
4. For a revision, apply the Step 3 preservation rules (IDs, statuses, no silent removals).
5. Re-read the written file and verify: story count matches the PRD, every task has exactly one Status line, every Implementation Order references only task IDs that exist in the same story section. Flag any mismatch instead of claiming success.

No Linear write happens in this skill. Posting human-readable summaries is a separate explicit step: `$vorbit-linear-sync`.

## Step 9: Report

Present the following:

1. **Spec folder path** and branch (canonical source: `prd.md` + `epic.md`)
2. **All story sections**, in PRD user-story order, with the owning `US-###`
3. **Per story:** task count by priority and its own Implementation Order (the same tree persisted in Step 8)
4. **Topology verification:** X user stories, X story sections, Y total tasks; flag any mismatch instead of claiming success
5. Reminder: the plan lives only in this worktree and is gitignored; Linear holds only summaries until `$vorbit-linear-sync` runs

### Implementation Order Format

Implementation order is calculated independently for each story section:

  Phase 1 (Parallel - no dependencies)
  - T1: [Task title]
  - T2: [Task title]
  - T3: [Task title]

  Phase 2 (depends on Phase 1)
  - T4: [Task title]

  Phase 3 (depends on Phase 2)
  - T5: [Task title]
  - T6: [Task title]

**Rules for dependency tree:**
- Phase 1 = tasks with no dependencies (can run in parallel)
- Each subsequent phase depends on previous phase completing
- Show `Blocked by:` for each task with dependencies
- Group parallel work within same phase
- Include only tasks that belong to the story section being reported

Next: run `$vorbit-linear-sync` to post story summaries, then start Phase 1 with `$vorbit-implement T1`

---

# Epic Schema & Standards

## epic.md Layout

```markdown
# Epic: [Feature Name from prd.md H1]

Source: prd.md (this folder)
Branch: [branch name]
Outcome: [1-2 plain sentences copied from prd.md Problem + Description: the user-visible result this epic delivers. A copy for orientation only; prd.md stays the source of truth]

## US-001: [Story Section Title]

[story section header — see template below]

### T1: [task title]

[task body — see template below]

### T2: [task title]

...

## US-002: [Story Section Title]

...
```

Task IDs are globally unique across the file (`T1`...`Tn`, no per-story restart). A technical epic uses `TS-###` section headings with the baseline description in place of the story fields.

## Story Section Title Format

Transform the user story goal into a clear, human-readable title (e.g. "As a user, I want to **login**..." → "User Login").

## Story Section Header Template

```markdown
## US-001: [Title]

**Story:** As a [user], I want [goal]...

**Acceptance Criteria (verbatim from PRD):**
- [ ] [Criterion, copied verbatim from the PRD]
- [ ] [Another criterion, copied verbatim from the PRD]

**Related PRD Flow Context:**
| Flow Step | Surface | Why it matters |
|-----------|---------|----------------|
| Flow 1, step 2 | UI: `CheckoutForm` | User submits payment details |
| Flow 1, step 3 | API: `POST /payments` | Payment processing and order creation |

**Test Criteria (TDD - write tests FIRST):**

Unit Tests
- [ ] Unit test: [component behavior]

E2E Tests
- [ ] E2E: [happy path] — assert observable output, not internal signals
- [ ] E2E: [each flow branch]
- [ ] E2E: [negative case]

**Implementation Order:**
Phase 1 (Parallel - no dependencies)
- T1: [Task title]

Phase 2 (depends on Phase 1)
- T2: [Task title]
```

## Task Template

```markdown
### T1: [task title]

**Status:** pending
**Priority:** P1 | P2 | P3
**Parallel:** yes | no
**Blocked by:** — | T2, T3

## Why This Is Needed
**What this does:** [Simple 1-sentence explanation]
**Why it matters:** [Business/user impact - what breaks without this?]

## Related Story Acceptance Criteria
> This task must satisfy these goals from its story section:
- [ ] [Story criterion this task addresses — copied verbatim, not paraphrased]
- [ ] [Another story criterion this task addresses]

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
> Mocks must be registered in the runtime-neutral Vorbit project registry; copy the exact resolved registry path from the prototype/implementation context into this task. Never hardcode an agent-specific directory.

## Acceptance Criteria (Task-specific)
- [ ] [Criterion this task alone must satisfy]
- [ ] [Another task-specific criterion]

## Test Criteria (TDD - write tests FIRST)

### Unit Tests
- [ ] Unit test: [specific behavior]
- [ ] Unit test: [edge case]

### E2E Tests (required for every task that touches a screen, and for scripts, hooks, or data parsing)
- [ ] E2E: [happy path] — assert observable output ([file written / state changed]), not just exit code
- [ ] E2E: [each code path / flow branch] — one test per distinct flow
- [ ] E2E: [false positive / negative case] — inputs that must NOT trigger
```

Task criteria are plain checkboxes. The task already has its own `T#` ID and its own story section — that is the handle. Do not mint per-criterion IDs.

**Priority Mapping**:
- P1 (Urgent): Core / Blocker
- P2 (High): Important
- P3 (Normal): Standard

---

## E2E Test Quality Rules

Before writing E2E criteria for any task, read and apply `references/e2e-test-quality.md` from this skill's installed directory.

---

## Parallel Criteria

**Set `Parallel: yes` ONLY when ALL are true:**
1. Task has NO dependencies on other tasks
2. Task does NOT block other tasks
3. Works on separate files/components (no merge conflicts)

**Default: `Parallel: no`.** When in doubt, keep it sequential.
