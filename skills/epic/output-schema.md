# Epic Output Schema & Standards

Reference for `/vorbit:implement:epic` (see SKILL.md for the imperative flow). Read this file before Step 7 (Plan Epics) and Step 8 (Traceability Gate). The flow populates templates from here and validates against the rules below; without this file, the agent invents its own ticket structure, drops required sections, or fabricates validation rules that don't match the team's standards.

## Required Sections per Sub-issue

For EACH sub-issue, the issue body MUST include these sections (in order):

| Section | Required | Purpose |
|---------|----------|---------|
| Why This Is Needed | Yes | What it does + why it matters (plain language) |
| Related Epic AC | Yes | Copy relevant `AC-*` IDs from parent epic |
| Related Flow Steps | Yes | Copy relevant flow step IDs + touched surfaces |
| Reuse & Patterns | Yes | Existing code, utilities, constants — no recreation, no magic numbers |
| FE Architecture Blueprint | If UI work | Per `_shared/frontend-knowledge/architecture-blueprint.md` (6 areas) |
| Design Source of Truth | If UI/design-driven | Per `references/figma-source-of-truth.md` (matrix + rules) |
| Screenshot Evidence | If UI/design-driven | Figma reference + browser/app result + comparison notes |
| File Changes | Yes | Exact file paths with CREATE/MODIFY action |
| Mock Data | If UI work | Mock locations + cleanup note |
| Acceptance Criteria | Yes | Sub-issue specific criteria |
| Test Criteria | Yes | TDD requirements — tests written FIRST |

## Title Format

Transform the User Story Goal into a clear, human-readable epic title.

| User Story | Epic Title |
| :--- | :--- |
| "As a user, I want to **login**..." | User Login |
| "As an admin, I want to **manage users**..." | Admin User Management |

## Priority Mapping

| Priority | Use For |
|----------|---------|
| P1 (Urgent) | Core / blocker |
| P2 (High) | Important |
| P3 (Normal) | Standard |

## Parallel Label Criteria

Apply the **Parallel** label ONLY when ALL of these are true:
1. Sub-issue has NO dependencies on other sub-issues
2. Sub-issue does NOT block other sub-issues
3. Works on separate files/components (no merge conflicts)

**Default: Sequential.** When in doubt, omit the Parallel label.

## TDD Requirement

Every issue (epic and sub-issue) MUST include a `## Test Criteria` section:
- Tests are written FIRST, before implementation code
- Implementation is only "done" when all tests pass
- No issue is complete without corresponding tests

## E2E Test Quality Rules

Apply these to every sub-issue's E2E test criteria, regardless of stack (API, UI, script, service):

**1. Fixtures must match the real data format.** Sample the real system output before writing any fixture. Never hand-write based on assumptions — simplified formats hide bugs that only surface in production.

**2. Assert observable output, not internal signals.** UI: rendered content, visible state, navigation. API: response body, status code, DB state after the request. Script/service: files written, messages sent, external state changed. Internal signals (exit codes, log lines, intermediate variables) are not observable output.

**3. Every code path needs at least one E2E test.** Happy path, error path, empty state, retry — each gets its own test. Coverage of one path does not imply correctness of another.

**4. Assertions must be non-vacuous.** Before asserting on the content of a file/response/record, first assert it exists. An assertion on a missing resource trivially passes.

**5. Test the integrated system, not parts in isolation.** Real HTTP calls, real DB writes, real file I/O. Mocking internals in an E2E test defeats the purpose — reserve mocking for unit tests.

## Validation Rules (Traceability Gate)

Before creating Linear issues, validate this matrix:
- Every `US-*` has at least one `AC-*`
- Every `AC-*` maps to one or more flow steps `F*-S*` OR has an explicit non-journey reason
- Every flow step with implementation impact maps to at least one sub-issue
- Every Epic AC is covered by at least one sub-issue
- Every UI flow step names a Figma source node OR is explicitly marked `TBD-design`
- Every coupled file pair is either in the same sub-issue OR cross-referenced in both sub-issues with the exact shared contract value

If any link is missing, stop and resolve via `AskUserQuestion` before creating issues.

## SDD Document Structure

Used in Step 5 of SKILL.md (Create Technical Plan on Ticket). The SDD must include all of these sections, in this order, posted to the parent Linear ticket as a comment or appended to the description before Step 6 (User Review).

| Section | Purpose | Source |
|---------|---------|--------|
| Technical Overview | High-level approach in 2-4 sentences | Your synthesis |
| Flow Impact Matrix | Flow step → system/module/API/UI touchpoints | PRD flows × codebase |
| Design Evidence Matrix | UI surface → Figma node → implementation target → states/questions | `references/figma-source-of-truth.md` |
| FE Architecture Blueprint | Reuse/create matrix, component hierarchy, API/data contract, state ownership, design-system mapping, test seams | `_shared/frontend-knowledge/architecture-blueprint.md` |
| PRD Compliance Check | Confirm all planned changes satisfy PRD US/AC/Flow baseline | PRD × your plan |
| Data Model Changes | Schema diffs, migrations, indexes | Your plan |
| API Changes | Endpoint additions/modifications, request/response shapes, deprecations | Your plan |
| Component Breakdown | Which existing components are reused, adapted, or created | Step 3 inventory × your plan |
| Testing Strategy | Unit, integration, E2E coverage per the TDD requirement and E2E rules above | Your plan |
| Risks & Unknowns | What could go wrong, what's still uncertain | Your plan |

## Templates

### Epic (Parent) description template

```markdown
## User Story
US-XXX: As a [user], I want [goal]...

## Acceptance Criteria
- [ ] AC-1 Criterion 1
- [ ] AC-2 Criterion 2

## Related PRD Flow Context
| Flow Step | Surface | Why it matters |
|-----------|---------|----------------|
| F1-S2 | UI: `CheckoutForm` | User submits payment details |
| F1-S3 | API: `POST /payments` | Payment processing and order creation |

## Test Criteria (TDD — write tests FIRST)

### Unit Tests
- [ ] Unit test: [component behavior]

### E2E Tests
- [ ] E2E: [happy path] — assert observable output, not internal signals
- [ ] E2E: [each flow branch]
- [ ] E2E: [negative case]

## PRD Reference
[Link to source PRD ticket]
```

### Sub-issue (Child) description template

**Title format:** Use `component-name` or `step-name`. Apply the **Parallel** label only when the Parallel Label Criteria above are met — never use a `Parallel:` prefix in the title.

**Body template:**

```markdown
## Why This Is Needed
**What this does:** [Simple 1-sentence explanation]
**Why it matters:** [Business/user impact — what breaks without this?]

## Related Epic Acceptance Criteria
> This sub-issue must satisfy these goals from the parent epic:
- [ ] AC-1 [Epic AC this sub-issue addresses]
- [ ] AC-2 [Epic AC this sub-issue addresses]

## Related Flow Steps
> Implementation context from PRD flow:
- [ ] F1-S2 [UI/component step covered]
- [ ] F1-S3 [API/service step covered]

⚠️ **Before marking done:** Verify ALL checked items above are satisfied.

## Reuse & Patterns
> Existing code to reference — DO NOT recreate, NO magic numbers

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
Find the shared folder with `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1`, then read `_shared/frontend-knowledge/ui-patterns.md` from there before implementing UI components.
If `react` is in `package.json`, also read `_shared/frontend-knowledge/react-best-practices/index.md` for performance rules.

## FE Architecture Blueprint (if UI work)
> Per `_shared/frontend-knowledge/architecture-blueprint.md` — six required areas. Fill the table below with the concrete decision for this sub-issue.

| Area | Decision |
|------|----------|
| Reuse/create matrix | `[Mockup block] → Reuse/Adapt/Create [component/composition/hook]` |
| Component hierarchy | `[Parent] → [children in render order]` |
| Data/API contract | `[Data needed] → [existing API/hook or new contract]` |
| State ownership | `[URL/server/local/form/optimistic/reset behavior]` |
| Design-system mapping | `[UI primitive/token/icon/responsive/a11y/i18n mapping]` |
| Test seams | `[unit/component/integration/screenshot/edge-state tests]` |

**Rule:** If any area can't be filled, ask before implementing — don't paper over with placeholders.

## Design Source of Truth (if UI/design-driven)
> Required for UI, layout, component, composition, visual state, or design-derived API work.
> Full procedure and rules: see `references/figma-source-of-truth.md`.

| Type | Source | Applies To | Required Detail |
|------|--------|------------|-----------------|
| Primary node | Figma `<primary-node-id>` | `<target surface>` | Implement this node exactly for this surface |
| Parent frame | Figma `<parent-frame-id>` | `<screen or flow>` | Use to understand surrounding structure and navigation |
| Reference only | Figma `<reference-node-id>` | `<reference context>` | Do not copy conflicting layout/state from this node |
| State/variant | Figma `[node-id]` | Empty/loading/error/selected | [What must render] |

## Screenshot Evidence (if UI/design-driven)
| Screenshot | Required | Purpose |
|------------|----------|---------|
| Figma reference | Yes | Source-of-truth node captured before implementation |
| Browser/app result | Yes | Implemented surface after code changes |
| Comparison notes | Yes | List intentional differences and unresolved visual mismatches |

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

> **Handover note:** Run `/vorbit:implement:cleanup-mocks [feature]` before backend takes over.
> Mocks are registered in `.claude/mock-registry.json` for tracking.

## Acceptance Criteria (Sub-issue specific)
- [ ] AC-SUB-1 Criterion 1
- [ ] AC-SUB-2 Criterion 2

## Test Criteria (TDD — write tests FIRST)

### Unit Tests
- [ ] Unit test: [specific behavior]
- [ ] Unit test: [edge case]

### E2E Tests (required if feature involves scripts, hooks, or data parsing)
- [ ] E2E: [happy path] — assert observable output, not just exit code
- [ ] E2E: [each code path / flow branch]
- [ ] E2E: [false positive / negative case]
```

## Implementation Order Format (used in Step 10 Report)

```
Phase 1 (Parallel — no dependencies)
- ABC-101: [Issue title]
- ABC-102: [Issue title]
- ABC-103: [Issue title]

Phase 2 (depends on Phase 1)
- ABC-104: [Issue title]

Phase 3 (depends on Phase 2)
- ABC-105: [Issue title]
- ABC-106: [Issue title]
```

Rules:
- Phase 1 = issues with no dependencies (can run in parallel)
- Each subsequent phase depends on previous phase completing
- Show `blocked by:` for each issue with dependencies
- Group parallel work within the same phase

## Linear Mapping

Linear issues are created via `mcp__plugin_linear_linear__*`. Each issue type:
- **Epic** = Linear parent issue (no `parentId`)
- **Sub-issue** = Linear issue with `parentId` = epic ID
- Labels and states come from the team's existing setup (see SKILL.md Step 2)
