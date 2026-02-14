---
name: epic
version: 1.4.2
description: Use when user says "create issues", "break down PRD", "set up epic", "create Linear tasks", "plan sprint", "convert to issues", or wants to transform PRD user stories into Linear epics and sub-issues.
---

# Epic Planning Skill

Transform User Stories (from PRD) into executable Engineering Tasks (Epics/Issues) in Linear.

**Key Features:**
- Sub-issues include plain-language "Why" section
- Each sub-issue references parent epic's acceptance criteria
- Each sub-issue references related PRD flow steps
- File paths are specified with exact locations
- Existing code patterns and constants are identified for reuse
- UI components reference the ui-patterns skill
- Visual dependency tree shows implementation order by phase

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`). Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Gather Context

**IF Notion PRD URL provided:**
1. Use `notion-find` to fetch the PRD
2. Extract user stories, acceptance criteria (`AC-*` IDs), user flows, and story-to-flow mapping

**IF Anytype PRD URL or object ID provided:**
1. Use `API-get-object` to fetch the PRD
2. Extract user stories, acceptance criteria (`AC-*` IDs), user flows, and story-to-flow mapping

**IF feature name provided:**
1. Search detected platform for existing PRD
2. Extract user stories, acceptance criteria (`AC-*` IDs), user flows, and story-to-flow mapping

**IF no PRD exists:**
1. Gather requirements via conversation

**Traceability requirements before planning:**
- Every user story has at least one `AC-*`
- Story-to-flow mapping exists (or explicit `No user flow required` reason)
- Every `AC-*` maps to flow step(s) or is marked non-journey with reason
- If any item is missing, use `AskUserQuestion` and resolve before Step 5

**PRD-first sequencing rule (required):**
- Lock requirement baseline first: `US-* -> AC-* -> Flow`
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
```bash
# Build search terms from PRD (US titles, AC nouns, flow surfaces)
rg -n "<term1>|<term2>|<term3>" .
```
- Note file structure patterns
- Identify naming conventions
- Find test patterns

### 4.2 Discover Reusable Code
Use a **pattern-first, paths-second** strategy:

1. **Find by usage/symbol first (required):**
   - Search imports/usages from PRD flow surfaces and AC terms
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

### 4.3 Discover Constants (NO MAGIC NUMBERS)
```bash
# Find constant files
find . -name "constants*" -o -name "config*" | head -20
```
- List relevant constants for this feature
- Identify where new constants should go
- **Rule:** Every hardcoded value must reference a constant

### 4.4 Check for Mock Data
If prototype exists with mock data:
- List all mock locations (`mocks/` folders)
- Include "Swap mock to real API" as sub-issue

### 4.5 Detect UI Work
If feature includes UI components:
- Note: "Reference `/vorbit:design:ui-patterns` skill"
- Identify existing UI patterns to follow

## Step 5: Create Technical Plan (SDD)

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Create SDD (Specification-Driven Development) document:
- Technical Overview
- Flow Impact Matrix (flow step -> system/module/API/UI touchpoints)
- PRD Compliance Check (confirm all planned changes satisfy PRD `US/AC/Flow` baseline)
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

**DO NOT proceed until user confirms.**

## Step 7: Plan Epics from User Stories

**1 User Story = 1 Epic**

For each User Story, create:
- **Title**: Write a clear, human-readable epic title derived from the user story goal
- **Description**: User story + related flow context + acceptance criteria + **test criteria (REQUIRED for TDD)**
- **Sub-issues** (if complex): Apply **Parallel** label only when truly independent

**TDD rule:** Every issue MUST include `## Test Criteria` section. Tests are written FIRST before implementation.

**Epic planning inputs per story (required):**
- User story ID (`US-*`)
- Relevant AC IDs (`AC-*`)
- Flow step IDs and surfaces from PRD (for example `F1-S3`, `API /orders`)

**Ticket derivation rule:**
- Use flow steps to identify concrete technical work:
  - UI/component changes
  - API/service changes
  - Data/state changes
  - Error-path handling

### Sub-issue Creation Checklist

For EACH sub-issue, include all these sections:

| Section | Required | Purpose |
|---------|----------|---------|
| **Why This Is Needed** | ✅ | What it does + why it matters |
| **Related Epic AC** | ✅ | Copy relevant ACs from parent epic |
| **Related Flow Steps** | ✅ | Copy relevant flow step IDs + touched surfaces |
| **Reuse & Patterns** | ✅ | Existing code, utilities, constants |
| **File Changes** | ✅ | Exact file paths with action (CREATE/MODIFY) |
| **Mock Data** | If UI work | Expected mocks and cleanup note |
| **Acceptance Criteria** | ✅ | Sub-issue specific criteria |
| **Test Criteria** | ✅ | TDD requirements |

### Mapping Epic AC to Sub-issues

1. List all Epic Acceptance Criteria (`AC-*`)
2. List all related flow steps for the story (`F*-S*`)
3. For each sub-issue, identify which Epic ACs and flow steps it satisfies
4. Copy those specific ACs into "Related Epic AC" and flow steps into "Related Flow Steps"
5. **Rule:** Every Epic AC must be covered by at least one sub-issue
6. **Rule:** Every in-scope flow step with implementation impact must be covered by at least one sub-issue

## Step 7.5: Traceability Gate (Required)

Before creating Linear issues, validate this matrix:
- `US-*` -> `AC-*`
- `AC-*` -> `Flow step(s)` (`F*-S*`) or explicit non-journey reason
- `Flow step(s)` -> sub-issue(s)

If any link is missing, stop and resolve via `AskUserQuestion` before Step 8.

## Step 8: Create in Linear

Using plan from Step 7:
1. Create parent issue (epic) first
2. Create sub-issues with `parentId` = epic ID
3. Use team's existing labels/states

## Step 9: Report

Present the following:

1. **Parent issue URL**
2. **Sub-issue count:** X total (P1: Y, P2: Z, P3: W)
3. **PRD link** (URL or object ID)
4. **Implementation Order** (dependency tree)

### Implementation Order Format

Implementation order based on dependencies:

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

Next: Start with Phase 1 issues using `/vorbit:implement:implement ABC-101`

---

# Epic Schema & Standards

## Title Format

**Transform the User Story Goal into a clear, human-readable epic title.**

| User Story | Epic Title |
| :--- | :--- |
| "As a user, I want to **login**..." | User Login |
| "As an admin, I want to **manage users**..." | Admin User Management |

## Issue Structure

### Epic (Parent)

**Description template:**
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

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [component behavior]
- [ ] Integration test: [user flow]

## PRD Reference
[Link]
```

### Sub-issue (Child)

**Title**: `component-name` or `step-name` (use **Parallel** label, not prefix)

**Description template:**
```markdown
## Why This Is Needed
**What this does:** [Simple 1-sentence explanation]
**Why it matters:** [Business/user impact - what breaks without this?]

## Related Epic Acceptance Criteria
> This sub-issue must satisfy these goals from the parent epic:
- [ ] AC-1 [Epic AC that this sub-issue addresses]
- [ ] AC-2 [Epic AC that this sub-issue addresses]

## Related Flow Steps
> Implementation context from PRD flow:
- [ ] F1-S2 [UI/component step covered]
- [ ] F1-S3 [API/service step covered]

⚠️ **Before marking done:** Verify ALL checked items above are satisfied.

## Reuse & Patterns
> Existing code to reference - DO NOT recreate, NO magic numbers

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
Run `/vorbit:design:ui-patterns` before implementing UI components.

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
> Mocks will be registered in `.claude/mock-registry.json` for tracking.

## Acceptance Criteria (Sub-issue specific)
- [ ] AC-SUB-1 Criterion 1
- [ ] AC-SUB-2 Criterion 2

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [specific behavior]
- [ ] Unit test: [edge case]
```

**Priority Mapping**:
- P1 (Urgent): Core / Blocker
- P2 (High): Important
- P3 (Normal): Standard

---

## TDD Requirement

**CRITICAL: All implementation follows Test-Driven Development.**

Every issue (epic and sub-issue) MUST include `## Test Criteria` section:
- Tests are written FIRST before implementation code
- Implementation is only "done" when all tests pass
- No issue is complete without corresponding tests

---

## Parallel Label Criteria

**Apply Parallel label ONLY when ALL are true:**
1. Sub-issue has NO dependencies on other sub-issues
2. Sub-issue does NOT block other sub-issues
3. Works on separate files/components (no merge conflicts)

**Default: Sequential.** When in doubt, don't add Parallel label.
