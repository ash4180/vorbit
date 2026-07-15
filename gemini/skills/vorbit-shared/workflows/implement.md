<!-- GENERATED from skills/implement/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

Read and follow `../references/execution-contract.md` before starting.

> **Linear tools**: Use the connected Linear tools shipped with Vorbit. Verify the available operation and parameter schema before calling it; never guess a verb or field name.

## Handle Loop Mode

**If `--loop` or `--cancel` is present, or the gemini implement-loop state file (see the implement-loop workflow) shows an active loop:**
Use the **implement-loop** skill for loop state management and sub-issue tracking.

**If no loop flags:** Continue with normal implementation below.

## Step 1: Resolve Input and Capabilities

Preflight required connectors: confirm each needed connector is configured in Gemini CLI and inspect its current operation/parameter schemas; never guess tool names. Only require Linear for a Linear issue or URL. A connection failure blocks Linear tracking, not implementation from a complete user-provided description.

## Step 2: Determine Context

**Priority order for finding issue:**

1. **IF args = Linear issue ID** (e.g., `ABC-123`): Fetch issue details from Linear
2. **IF args = Linear URL**: Extract issue ID from URL, fetch details
3. **IF no args, check conversation**: Look for Linear issue URLs from recent `$vorbit-epic` output
   - If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Ask what to implement. Do not select assigned work without the user's request
5. **IF description only**: Work directly on what user describes (no Linear tracking)

For a Linear issue, record the issue ID and description update timestamp used as the requirement baseline. If it changes during implementation, stop and reconcile the new requirements.

## Step 3: Before Starting

For Linear issues:
- Read issue description for requirements
- Check parent issue for SDD and style findings
- Fetch the linked Linear PRD/specification ticket when available
- Map the issue to its user story (`US-*`), its acceptance criteria, and its flow steps
- Confirm no implementation-affecting `TBD` remains
- Only after those gates pass, update the selected implementation issue to the team's exact In Progress state before editing code

## Step 3.5: Parse Enhanced Issue Format

**CRITICAL: If issue contains these sections, use them:**

### Check "Related Parent Acceptance Criteria"
If present:
1. Read the implementation parent's acceptance criteria listed in the issue
2. These are your PRIMARY success criteria
3. **Rule:** Task is NOT done until ALL listed parent criteria are satisfied

### Check "Test Criteria"
If present, this is the test contract: write these tests first (TDD) and treat the task as incomplete until each listed check passes or has an honest recorded blocker.

### Check "Reuse & Patterns"
If present:
1. **Similar features** → Open and study these files FIRST
2. **Utilities** → Use these, DO NOT recreate
3. **Constants** → Use these, NO magic numbers allowed
4. **UI Patterns** → If present, invoke `$vorbit-ui-patterns`

### Check "File Changes"
If present:
1. This is your implementation plan
2. Treat listed paths as the approved plan, not proof that the current codebase still matches it
3. If code evidence requires a different path, explain why before editing and update the issue after approval
4. Never create a duplicate merely to match a stale path

### Detect UI Work
If issue involves UI components:
- Check for ui-patterns reference in issue
- If UI work detected, use ui-patterns skill for constraints
- Preserve the repository's existing styling and primitive stack; apply Tailwind or `motion/react` only when already present or explicitly approved

## Step 4: Learn Codebase Style

Before writing code, study similar features and call sites: import style, naming conventions, file structure, test patterns. **Consistency > Novelty** — match the team's existing style.

## Step 4.5: i18n/Localization Rules

Detect whether the project uses any localization system (libraries, locale files, translation-function usage). If it does:

- **NO hardcoded user-facing strings** — all UI text goes through the project's translation system
- **ALL locales updated** — new keys must be added to EVERY locale file
- **Match existing patterns** — follow the project's key naming convention and plural/interpolation syntax
- **Rule**: If the project has ANY localization setup, missing translations = broken UX. This is a blocker.

## Step 5: Handle Parent Issues

If the selected issue has open sub-issues, do not silently implement the whole tree. Show the queue from the parent's `## Implementation Order` section and ask the user to choose one sub-issue or explicitly start loop mode. Normal implementation owns one issue at a time; implement-loop owns multi-issue progression.

## Step 6: TDD Implementation

**RULE: Task is NOT done until tests pass.**

Keep the change within the selected issue. Do not add a frontend or backend counterpart unless its acceptance criteria require it.

For each task, follow Red/Green/Refactor:

- **Red**: When the repository has a runnable harness, write a failing test for the changed behavior first (follow the project's test patterns; confirm the focused test fails for the expected reason). If no suitable harness exists, agree on a real verification surface; do not invent a cheater test.
- **Green**: Write the minimum code to pass, following existing codebase patterns and the example files found earlier; no over-engineering.
- **Refactor**: Clean up, check coverage on new code, ensure no regressions. Remove dead code and unregistered placeholder TODOs (registered prototype mocks may remain until backend integration).

### If Creating Mock Data During Implementation
Register every temporary application mock in the project registry before the task is done (test fixtures are excluded) — this enables cleanup before backend handover. Read `../references/mock-registry.md` for the path resolution, schema, and field semantics; entries created here use `"createdBy": "implement"`.

### Task Complete Criteria
Mark done only when every gate defined in Steps 3.5-6 above is satisfied.

## Step 7: On Task Completion

- Keep the implementation parent "In Progress" until a PR exists. Implementation sub-issues may move to "Done" after their own ACs and tests pass.
- Add a Linear comment with changed files, verification evidence, and remaining release steps.

## Step 8: On Feature Completion

Do not create a generic `memory.md`. Record durable decisions only in an existing repository-approved location, and only when future maintainers need them.

## Step 9: Report

- What was implemented
- Files changed
- Tests added/updated
- Next: `$vorbit-verify` to verify

## Quick Mode

For simple tasks (< 30 lines):
- Keep the same search, scope, and verification rules
- Skip issue ceremony only when no Linear issue was supplied
