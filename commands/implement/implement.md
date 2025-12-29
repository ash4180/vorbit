---
description: Execute tasks from Linear or implement from description
argument-hint: [Linear issue ID or feature description]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, mcp__plugin_Notion_notion__*, mcp__plugin_linear_linear__*
---

Implement: $ARGUMENTS

## Determine Context

**Priority order for finding issue:**

1. **IF args = Linear issue ID** (e.g., `ABC-123`): Fetch issue details from Linear
2. **IF args = Linear URL**: Extract issue ID from URL, fetch details
3. **IF no args, check conversation**: Look for Linear issue URLs from recent `/vorbit:implement:epic` output
   - If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Use `list_issues` with `assignee: "me"` to show assigned issues, ask which to work on
5. **IF description only**: Work directly on what user describes (no Linear tracking)

## Before Starting

For Linear issues:
- Update issue status to "In Progress"
- Read issue description for requirements
- Check parent issue for SDD and style findings
- Check linked PRD in Notion if available

## Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Grep for similar features in codebase
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

This ensures code matches team's style and is easy to review.

## Check for Parallel Tasks

**For parent issues (epics):**

1. Use `list_issues` with `parentId: [issue ID]` to fetch all sub-issues
2. Filter sub-issues where title starts with `[P]` (parallel marker from epic command)
3. Group `[P]` sub-issues by shared dependencies (e.g., same module, same API)
4. For each parallel group:
   - Use Task tool to spawn one agent per sub-issue
   - Each agent follows TDD approach below
   - Wait for all agents in group to complete before next group
5. Process non-`[P]` sub-issues sequentially after all parallel groups

## TDD Implementation

**RULE: Task is NOT done until tests pass.**

For each sub-task:

### 1. Write Test First
- Create test that validates acceptance criteria
- Follow project's test file patterns
- Run test - **MUST fail** (proves test is valid)

### 2. Implement Feature
- Follow existing codebase patterns
- Match style of example files found earlier
- Use existing components/utilities
- No over-engineering

### 3. Pass Test
- Run test - should pass
- Check coverage on new code
- Fix any issues

### 4. Task Complete Criteria
**ONLY mark done when:**
- [ ] Unit test exists and passes
- [ ] Code matches team's style
- [ ] No regressions in existing tests
- [ ] No mock data remains (check for `MOCK_`, mock imports, `.json` test data)

## On Sub-task Completion

- Update Linear status to "Done" or "In Review"
- Add comment: what was done, files changed

## On Feature Completion

**After ALL sub-tasks done, create memory.md:**

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


## Report

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
