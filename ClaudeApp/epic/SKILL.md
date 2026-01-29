---
name: epic
description: Use when user says "create issues", "break down PRD", "set up epic", "create Linear tasks", "plan sprint", "convert to issues", "draft ticket", "make ticket", "create ticket for [feature]", or wants to transform PRD user stories into Linear epics and sub-issues. Also triggers when user describes a feature idea without a PRD - will use UX skill to gather requirements first.
---

# Epic Planning Skill

Transform User Stories (from PRD) into executable Engineering Tasks (Epics/Issues) in Linear.

**Key Features:**
- Sub-issues include plain-language "Why" section
- Each sub-issue references parent epic's acceptance criteria
- File paths are specified with exact locations
- Existing code patterns and constants are identified for reuse
- UI sub-issues include reminder for implementer to use ui-patterns skill
- Visual dependency tree shows implementation order by phase

## Step 1: Detect Platform & Verify Connection

**Auto-detect platform from user input:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- User mentions "Notion" → use Notion
- Anytype URL or object ID → use Anytype
- User mentions "Anytype" → use Anytype
- Otherwise → skip platform, gather requirements via conversation

**Only verify the detected platform (don't test both):**

### If Notion detected:
1. Run `notion-find` to search for "test"
2. **IF fails:** "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If no platform detected: proceed to next step

## Step 2: Gather Context

**IF Notion PRD URL provided:**
1. Use `notion-find` to fetch the PRD
2. Extract user stories and acceptance criteria
3. **Check completeness** → If ACs are vague/missing, go to "Incomplete Requirements" below

**IF Anytype PRD URL or object ID provided:**
1. Use `API-get-object` to fetch the PRD
2. Extract user stories and acceptance criteria
3. **Check completeness** → If ACs are vague/missing, go to "Incomplete Requirements" below

**IF feature name/description provided (no PRD URL):**
1. Ask user: "Do you have a PRD for this? Or should I help define requirements?"
2. If PRD exists → get URL and fetch it
3. If no PRD → go to "Incomplete Requirements" below

**Incomplete Requirements (USE UX SKILL):**
Trigger when ANY of these are true:
- No PRD exists
- PRD lacks acceptance criteria
- User provides only a feature idea/description
- Requirements are vague ("add login", "improve performance")
- Edge cases undefined

**>>> READ AND USE THE `ux` SKILL - MANDATORY <<<**
```bash
# MUST read this skill file first
cat skills/ux/SKILL.md
```
1. Read the UX skill file above
2. Follow UX skill process: exhaustive questioning using question-matrix
3. UX skill returns structured acceptance criteria
4. Use those acceptance criteria to create epics (proceed to Step 3)

**Rule:** Never skip UX questioning when requirements are incomplete. Vague tickets = bugs.

## Step 3: Detect Team's Linear Setup

**Adapt to team's existing patterns.**

Use Linear MCP:
- `list_teams` - Get team ID
- `list_issue_statuses` - Get actual state names
- `list_issue_labels` - Get existing labels
- `list_projects` - Get relevant project

Ask user if unclear: "Which team/project?"

## Step 4: Learn Codebase Style & Discover Reusables

Before planning, analyze the codebase thoroughly:

### 4.1 Find Similar Features
```bash
# Search for similar patterns
grep -r "similar-feature" --include="*.tsx" --include="*.ts"
```
- Note file structure patterns
- Identify naming conventions
- Find test patterns

### 4.2 Discover Reusable Code
**Find existing utilities:**
- Search `src/utils/`, `src/lib/`, `src/helpers/`
- List functions that can be reused
- Note: "Use X, don't recreate"

**Find existing components:**
- Search `src/components/ui/`, `src/components/common/`
- List UI primitives available
- Note component library in use (Radix, Base UI, etc.)

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
- Add note in sub-issue: "⚠️ Implementer: Use `/vorbit:design:ui-patterns` skill"
- Identify existing UI patterns to follow

## Step 5: Create Technical Plan (SDD)

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Create SDD (Specification-Driven Development) document:
- Technical Overview
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
- **Title**: Transform user story goal → kebab-case (e.g., "I want to login" → `add-user-login`)
- **Description**: User story + acceptance criteria + **test criteria (REQUIRED for TDD)**
- **Sub-issues** (if complex): Apply **Parallel** label only when truly independent

**TDD rule:** Every issue MUST include `## Test Criteria` section. Tests are written FIRST before implementation.

### Sub-issue Creation Checklist

For EACH sub-issue, include all these sections:

| Section | Required | Purpose |
|---------|----------|---------|
| **Why This Is Needed** | ✅ | What it does + why it matters |
| **Related Epic AC** | ✅ | Copy relevant ACs from parent epic |
| **Design Decisions** | ⚡ | Technical choices with rationale (when trade-offs exist) |
| **Required Skills** | ✅ | Skills implementer MUST read before coding |
| **Reuse & Patterns** | ✅ | Existing code, utilities, constants |
| **File Changes** | ✅ | Grouped by ADDED/MODIFIED/REMOVED |
| **Acceptance Criteria** | ✅ | Structured scenarios with GIVEN/WHEN/THEN |
| **Test Criteria** | ✅ | TDD requirements |

⚡ = Include when multiple valid approaches exist or security/performance trade-offs are involved

### Required Skills Detection

Analyze each sub-issue and add required skills:

| If sub-issue involves... | Add Required Skill |
|--------------------------|-------------------|
| React/Next.js components | `react-best-practices` |
| UI components, forms, modals, accessibility | `ui-patterns` |
| Both React + UI work | Both skills |

**Rule:** Implementer MUST read these skill files before writing any code.

### Mapping Epic AC to Sub-issues

1. List all Epic Acceptance Criteria (numbered)
2. For each sub-issue, identify which Epic ACs it satisfies
3. Copy those specific ACs into "Related Epic AC" section
4. **Rule:** Every Epic AC must be covered by at least one sub-issue

### Plan Implementation Phases (REQUIRED)

**Before creating issues, determine execution order:**

1. **Identify dependencies** between sub-issues:
   - Which sub-issues can run in parallel? (no shared files, no dependencies)
   - Which sub-issues block others? (API before UI, schema before queries)

2. **Group into phases:**
   - **Phase 1**: No dependencies (can run in parallel)
   - **Phase 2**: Depends on Phase 1
   - **Phase 3**: Depends on Phase 2
   - etc.

3. **Set blocked_by relationships:**
   - For each dependent sub-issue, note which issues block it
   - This will be used in Linear and in the final report

**Rule:** Always plan phases BEFORE creating issues. Implementation Order in report comes from this planning.

## Step 8: Create in Linear

Using plan from Step 7:
1. Create parent issue (epic) first
2. Create sub-issues with `parentId` = epic ID
3. **Set `blocked_by` relationships** based on Implementation Phases planned above
4. Apply **Parallel** label to Phase 1 issues (no dependencies)
5. Use team's existing labels/states

## Step 9: Report

**MUST include ALL of these sections:**

### 1. Summary
```
**Epic:** [ABC-100] [Epic title]
**URL:** [Linear URL]
**Sub-issues:** X total (P1: Y, P2: Z, P3: W)
**PRD:** [URL or object ID]
```

### 2. Implementation Order (REQUIRED - DO NOT SKIP)

**>>> THIS SECTION IS MANDATORY <<<**

Show the phased dependency tree so implementer knows execution order:

```
## Implementation Order

Phase 1 (Parallel - no dependencies)
├── ABC-101: [Issue title]
├── ABC-102: [Issue title]
└── ABC-103: [Issue title]

Phase 2 (depends on Phase 1)
└── ABC-104: [Issue title]
    └── blocked by: ABC-101, ABC-102

Phase 3 (depends on Phase 2)
├── ABC-105: [Issue title]
│   └── blocked by: ABC-104
└── ABC-106: [Issue title]
    └── blocked by: ABC-104
```

**Rules for dependency tree:**
- Phase 1 = issues with no dependencies (can run in parallel)
- Each subsequent phase depends on previous phase completing
- Show `blocked by:` for each issue with dependencies
- Group parallel work within same phase

### 3. Verification Checklist (Pre-Close)

**Include in epic description for implementer to check before closing:**

```markdown
## Verification (Check before closing epic)

### Completeness
- [ ] All sub-issues completed
- [ ] Every Epic AC addressed by at least one sub-issue
- [ ] No orphaned requirements (ACs without implementation)

### Correctness
- [ ] Implementation matches spec scenarios (not assumptions)
- [ ] All THEN clauses from scenarios are satisfied
- [ ] Edge cases from scenarios handled

### Coherence
- [ ] Code follows patterns from "Reuse & Patterns" sections
- [ ] No magic numbers (constants used per spec)
- [ ] Design Decisions rationale still valid
- [ ] Required skills were applied
```

**Rule:** Epic is not complete until all verification items pass.

### 4. Next Steps
```
Ready to implement! Start with Phase 1:
→ `/vorbit:implement:implement ABC-101`
```

**Rule:** Never finish epic without showing Implementation Order. Implementer needs this to know where to start.

---

# Epic Schema & Standards

## Title Format

**Transform the User Story Goal into a kebab-case title.**

| User Story | Epic Title |
| :--- | :--- |
| "As a user, I want to **login**..." | `add-user-login` |
| "As an admin, I want to **manage users**..." | `add-admin-user-management` |

**Rules**:
- Action verbs: `add-`, `implement-`, `fix-`, `update-`
- Lowercase, hyphens, no special chars
- Match Git branch conventions: `git checkout -b add-user-login`

## Issue Structure

### Epic (Parent)

**Description template:**
```markdown
## User Story
US-XXX: As a [user], I want [goal]...

## Acceptance Criteria (Structured Scenarios)

#### Scenario: [Happy path - primary use case]
- **GIVEN** [initial state/context]
- **WHEN** [user action]
- **THEN** [expected outcome]
- **AND** [additional outcome]

#### Scenario: [Alternative flow or edge case]
- **GIVEN** [initial state/context]
- **WHEN** [action performed]
- **THEN** [expected outcome]

#### Scenario: [Error handling]
- **GIVEN** [initial state/context]
- **WHEN** [invalid action or error condition]
- **THEN** [system SHALL respond with specific behavior]

## Design Decisions (if trade-offs exist)

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| [Key technical choice] | A vs B vs C | B | [Why B over alternatives] |

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [derived from scenario THEN clauses]
- [ ] Integration test: [user flow covering multiple scenarios]

## Verification (Check before closing epic)

### Completeness
- [ ] All sub-issues completed
- [ ] Every AC scenario addressed

### Correctness
- [ ] All THEN clauses satisfied
- [ ] Edge case scenarios handled

### Coherence
- [ ] Patterns followed, no magic numbers
- [ ] Design decisions still valid

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
- [ ] [Epic AC #1 that this sub-issue addresses]
- [ ] [Epic AC #2 that this sub-issue addresses]

⚠️ **Before marking done:** Verify ALL checked items above are satisfied.

## Design Decisions
> ⚡ Include when trade-offs exist. Skip for straightforward implementations.

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| [Technical choice] | Option A vs Option B | Option A | [Why this over alternatives] |

*(Delete this section if no meaningful trade-offs exist)*

## Required Skills
> ⚠️ **MUST READ before coding.** Implementer: Read these skill files first.

| Skill | Path | Why |
|-------|------|-----|
| `react-best-practices` | `skills/react-best-practices/SKILL.md` | Performance patterns, waterfall elimination |
| `ui-patterns` | `skills/ui-patterns/SKILL.md` | Accessibility, Tailwind, animation rules |

*(Remove rows not applicable to this sub-issue)*

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
⚠️ Implementer: Use `/vorbit:design:ui-patterns` skill when implementing.

## File Changes

### + ADDED (new files)
| File Path | Purpose |
|-----------|---------|
| `src/components/feature/Component.tsx` | Main component |
| `src/tests/feature/component.test.ts` | Unit tests |

### ~ MODIFIED (existing files)
| File Path | Change Description |
|-----------|-------------------|
| `src/api/routes.ts` | Add new endpoint |

### − REMOVED (cleanup)
| File Path | Reason |
|-----------|--------|
| `src/mocks/featureMock.ts` | No longer needed after real API |

*(Delete empty sections. Always document REMOVED files with reasoning.)*

## Acceptance Criteria (Structured Scenarios)

#### Scenario: [Happy path description]
- **GIVEN** [initial state/context]
- **WHEN** [action performed]
- **THEN** [expected outcome]
- **AND** [additional outcome if needed]

#### Scenario: [Edge case or error handling]
- **GIVEN** [initial state/context]
- **WHEN** [action performed]
- **THEN** [expected outcome]

*(Use SHALL/MUST for unambiguous requirements: "System SHALL display error within 200ms")*

## Test Criteria (TDD - write tests FIRST)
- [ ] Unit test: [specific behavior from scenario THEN clause]
- [ ] Unit test: [edge case from scenario]
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
