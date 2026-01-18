---
name: implement
version: 1.2.0
description: Use when user says "implement this", "build feature", "fix this bug", "code this", "work on issue", "start coding", or asks to implement from a Linear issue or description. Standard TDD workflow for coding tasks.
---

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

## Handle Loop Mode

**If `--loop` or `--cancel` in arguments:**
Use the **implement-loop** skill for loop state management and sub-issue tracking.

**If no loop flags:** Continue with normal implementation below.

## Step 1: Detect Platform & Verify Connection

**IF the issue links to a PRD, auto-detect platform:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- Anytype URL or object ID → use Anytype

**Only verify the detected platform:**

### If Notion detected:
1. Run `notion-find` to search for "test"
2. **IF fails:** "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed

**IF no PRD is needed:** skip this step

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
  - **Notion PRD**: Use `notion-find` to fetch
  - **Anytype PRD**: Use `API-get-object` to fetch

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
4. **UI Patterns** → If present, invoke `/vorbit:design:ui-patterns`

### Check "File Changes"
If present:
1. This is your implementation plan
2. CREATE files at exact paths listed
3. MODIFY files at exact paths listed
4. **Rule:** Don't deviate without updating the issue

### Detect UI Work
If issue involves UI components:
- Check for ui-patterns reference in issue
- If UI work detected, use ui-patterns skill for constraints
- Follow: Tailwind, motion/react, accessibility primitives

## Step 4: Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Grep for similar features in codebase
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

**Rule**: Consistency > Novelty. This ensures code matches team's style.

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

### Task Complete Criteria
**ONLY mark done when:**
- [ ] Unit test exists and passes
- [ ] Code matches team's style
- [ ] No regressions in existing tests
- [ ] No mock data remains (check for `MOCK_`, mock imports, `.json` test data)
- [ ] **All "Related Epic Acceptance Criteria" satisfied** (if present in issue)
- [ ] **File changes match planned paths** (if "File Changes" section exists)
- [ ] **Used utilities/constants from "Reuse & Patterns"** (no magic numbers, no recreated functions)

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

## Validation Checklist

Before finishing, ask yourself:
- "Did I delete any dead code I created?"
- "Did I leave any TODOs?"
- "Did I break any existing tests?"
- "Did I satisfy ALL Related Epic Acceptance Criteria?"
- "Did I use the utilities/constants from Reuse & Patterns?"
- "Did I use any magic numbers instead of constants?"
- "Did I recreate any function that already exists?"
- "Did I follow the File Changes plan?"
