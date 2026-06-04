---
name: implement
version: 1.3.0
description: Use when user says "implement this", "build feature", "fix this bug", "code this", "work on issue", "start coding", or asks to implement from a Linear issue or description. Standard TDD workflow for coding tasks.
---

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

> **Linear MCP namespace**: All Linear calls in this skill use `mcp__plugin_linear_linear__*` (the namespace shipped with the vorbit plugin). Bare verb names below (`list_issues`, `update_issue`, etc.) refer to the corresponding `mcp__plugin_linear_linear__<verb>` tool.

> **Figma MCP namespace**: For UI/design-driven sub-issues, bare Figma verbs below (`get_design_context`, `get_metadata`, `get_screenshot`) refer to `mcp__figma__<verb>` (canonical per `_shared/mcp-tool-routing.md`). If only the plugin variant is connected, `mcp__plugin_figma_figma__<verb>` works equivalently.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Handle Loop Mode

**If `--loop` or `--cancel` in arguments:**
Use the **implement-loop** skill for loop state management and sub-issue tracking.

**If no loop flags:** Continue with normal implementation below.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected platforms, ask user which to use, and verify connection. If no PRD is needed, skip this step.

## Step 2: Determine Context

**Priority order for finding issue:**

1. **IF args = Linear issue ID** (e.g., `ABC-123`): Fetch issue details from Linear
2. **IF args = Linear URL**: Extract issue ID from URL, fetch details
3. **IF no args, check conversation**: Look for Linear issue URLs from recent `/vorbit:implement:epic` output
   - If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Use `list_issues` with `assignee: "me"` to show assigned issues, ask which to work on
5. **IF description only**: Work directly on what user describes (no Linear tracking)

## Step 3: Before Starting

For Linear issues:
- Update issue status to "In Progress"
- Read issue description for requirements
- Check parent issue for SDD and style findings
- Check linked PRD if available:
  - **Notion PRD**: Use `notion-fetch` to fetch

## Step 3.5: Parse Enhanced Issue Format

**CRITICAL: If issue contains these sections, use them:**

### Check "Related Epic Acceptance Criteria"
If present:
1. Read the parent epic's ACs listed in the issue
2. These are your PRIMARY success criteria
3. **Rule:** Task is NOT done until ALL listed epic ACs are satisfied

### Check "Reuse & Patterns"
If present:
1. **Similar features** → Open and study these files FIRST
2. **Utilities** → Use these, DO NOT recreate
3. **Constants** → Use these, NO magic numbers allowed
4. **UI Patterns** → If present, read `_shared/frontend-knowledge/ui-patterns.md`
5. **If `react` is in `package.json`** → also read `_shared/frontend-knowledge/react-best-practices/index.md` for performance rules

### Check "File Changes"
If present:
1. This is your implementation plan
2. CREATE files at exact paths listed
3. MODIFY files at exact paths listed
4. **Rule:** Don't deviate without updating the issue

### Detect UI Work
If issue involves UI components:
- Check for ui-patterns reference in issue
- If UI work detected, read `_shared/frontend-knowledge/ui-patterns.md` for constraints
- If `react` is in `package.json`, also read `_shared/frontend-knowledge/react-best-practices/index.md` for performance rules
- Follow: Tailwind, motion/react, accessibility primitives

### Check "Design Source of Truth" and "Screenshot Evidence"
If the issue includes UI/design-driven work:
1. Fetch the primary Figma node with `get_design_context`; use `get_metadata` only for hierarchy, then return to `get_design_context`.
2. Capture the Figma reference screenshot with `get_screenshot` or the screenshot returned by `get_design_context`.
3. Build a short structure/flow summary before coding:
   - Parent frame/page and nearest meaningful ancestor
   - Selected node boundary and child blocks in render order
   - What is inside vs outside implementation scope
   - Entry action, visible result, and exit state
4. If the Figma structure or interaction flow is unclear, stop and ask before implementing.
5. Start the local app if needed and capture a browser/app screenshot of the implemented surface after changes.
6. Compare screenshots against the issue's Design Source of Truth. Fix visible mismatches unless the issue explicitly marks them out of scope.
7. If the issue says "match Figma" but does not name an exact node, stop and ask for the node before implementing.
8. If ticket text and Figma disagree, stop and ask which source wins before coding.

## Step 4: Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Grep for similar features in codebase
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

**Rule**: Consistency > Novelty. This ensures code matches team's style.

### Step 4.1: FE Architecture Blueprint — Read from Issue, Don't Rebuild

If the task touches UI, layout, component composition, or user-visible state:

1. **Find the FE Architecture Blueprint section** in the sub-issue body (per `skills/epic/output-schema.md`). `/epic` is responsible for writing this — it's a 6-area table covering reuse/create matrix, component hierarchy, data/API contract, state ownership, design-system mapping, and test seams. The full structure is defined in `_shared/frontend-knowledge/architecture-blueprint.md`.
2. **Read it as the implementation plan.** The blueprint is the contract `/epic` made with you. Don't rebuild it from scratch — that drifts from the plan and wastes work.
3. **If the blueprint is missing or has gaps**, stop and ask the user. Don't paper over with guesses. Options:
   - Ask `/epic` to update the sub-issue (preferred — keeps the plan in Linear)
   - Confirm a specific gap inline and proceed, noting the decision in your implementation comment
4. **Validate the blueprint against reality** as you code:
   - When the blueprint says `Reuse src/components/Button.tsx`, confirm that file actually exists and the import works
   - When the blueprint says `Adapt` an existing hook, check the existing hook for whether adaptation is sane
   - When the blueprint says `Create`, search first to confirm nothing similar already exists — `Create` is the last resort

If the blueprint is unfillable from Figma + PRD + code search at planning time, that's `/epic`'s problem to resolve. At implementation time, treat the blueprint as authoritative.

## Step 4.5: Detect i18n/Localization Requirements

If this is UI work and the project may be localized, read `_shared/frontend-knowledge/i18n-detection.md` and run its detection strategy. If a localization system is detected, apply its universal rules to every new user-facing string — no hardcoded text, new keys added to **every** locale file, matching the project's existing key-naming convention. If the project has any localization setup, missing translations are a blocker.

## Step 5: Check for Sub-issues

**For parent issues (epics):**

1. Use `list_issues` with `parentId: [issue ID]` to fetch all sub-issues
2. Filter sub-issues that have the **Parallel** label
3. Group parallel sub-issues by shared dependencies
4. For each parallel group:
   - Use Task tool to spawn one agent per sub-issue
   - Each agent follows TDD approach below
   - Wait for all agents in group to complete before next group
5. Process non-parallel sub-issues sequentially after all parallel groups

## Step 6: TDD Implementation

**RULE: Task is NOT done until tests pass.**

**RULE**: If you implement backend API changes, also implement the corresponding frontend site API integration. Use explicit `TODO:` markers only for temporary placeholders.

For each task:

### Red (Write Test First)
- Create test that validates acceptance criteria
- Follow project's test file patterns
- Run test - **MUST FAIL** (proves test is valid)

### Green (Implement)
- Write the minimum code to pass the test
- Follow existing codebase patterns
- Match style of example files found earlier
- Use existing components/utilities
- No over-engineering

### Refactor
- Clean up code
- Check coverage on new code
- Ensure no regressions

### If Creating Mock Data During Implementation
Register every mock — file and state — in `.claude/mock-registry.json` with `"createdBy": "implement"` so it can be cleaned up before backend handover. See `_shared/mock-registry.md` for the schema, write templates, when to register, and what to capture. Append to the existing `mocks` array.

### Task Complete Criteria
**ONLY mark done when:**
- [ ] Unit test exists and passes
- [ ] Code matches team's style
- [ ] No regressions in existing tests
- [ ] No mock data remains (check for `MOCK_`, mock imports, `.json` test data) **OR mocks registered in `.claude/mock-registry.json`**
- [ ] **All "Related Epic Acceptance Criteria" satisfied** (if present in issue)
- [ ] **File changes match planned paths** (if "File Changes" section exists)
- [ ] **Used utilities/constants from "Reuse & Patterns"** (no magic numbers, no recreated functions)
- [ ] **No dead code or leftover TODOs**
- [ ] **i18n complete** (if project has localization): All user-facing strings use translation system, keys added to ALL locale files
- [ ] **Screenshot evidence complete** (if UI/design-driven): Figma reference screenshot captured, browser/app screenshot captured after implementation, and mismatches resolved or documented as intentional

## Step 7: On Task Completion

- Update Linear status to "Done" or "In Review"
- Add comment: what was done, files changed

## Step 8: On Feature Completion

**After ALL tasks done, create memory.md:**

```markdown
# Feature: [Name]

## What Was Built
[Summary]

## Technical Decisions
[Why chose approach X]

## Lessons Learned
[What worked, what was hard]

## Code Patterns
[Reference README.md or CLAUDE.md if patterns documented there, otherwise note new patterns discovered]
```

## Step 9: Report

- What was implemented
- Files changed
- Tests added/updated
- memory.md location
- Next: `/vorbit:implement:verify` to verify

## Quick Mode

For simple tasks (< 30 lines):
- Just implement it
- Run existing tests
- Skip memory.md
