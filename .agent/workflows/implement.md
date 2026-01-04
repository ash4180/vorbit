---
description: Execute tasks from issue tracker or implement from description.
---

## Determine Context

**Priority order for finding issue:**

1. **IF args = issue ID** (e.g., `ABC-123`): Fetch issue details
2. **IF args = issue URL**: Extract ID from URL, fetch details
3. **IF no args, check conversation**: Look for issue URLs from recent `/epic` output
   * If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Show assigned issues, ask which to work on
5. **IF description only**: Work directly on what user describes (no tracking)

## Before Starting

For tracked issues:
* Update issue status to "In Progress"
* Read issue description for requirements
* Check parent issue for SDD and style findings
* Check linked PRD if available

## Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Search for similar features in codebase
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

This ensures code matches team's style and is easy to review.

## Check for Parallel Tasks

**For parent issues (epics):**

1. Fetch all sub-issues
2. Filter sub-issues where title starts with `[P]` (parallel marker)
3. Group `[P]` sub-issues by shared dependencies
4. For each parallel group: work on tasks together
5. Process non-`[P]` sub-issues sequentially after parallel groups

## TDD Implementation

**RULE: Task is NOT done until tests pass.**

For each sub-task:

### 1. Write Test First
* Create test that validates acceptance criteria
* Follow project's test file patterns
* Run test - **MUST fail** (proves test is valid)

### 2. Implement Feature
* Follow existing codebase patterns
* Match style of example files found earlier
* Use existing components/utilities
* No over-engineering

### 3. Pass Test
* Run test - should pass
* Check coverage on new code
* Fix any issues

### 4. Task Complete Criteria
**ONLY mark done when:**
* [ ] Unit test exists and passes
* [ ] Code matches team's style
* [ ] No regressions in existing tests
* [ ] No mock data remains

## On Sub-task Completion

* Update status to "Done" or "In Review"
* Add comment: what was done, files changed

## On Feature Completion

After ALL sub-tasks done, create memory.md with:
* What Was Built
* Technical Decisions
* Lessons Learned
* Code Patterns

## Report

* What was implemented
* Files changed
* Tests added/updated
* memory.md location
* Next: `/verify`

## Quick Mode

For simple tasks (< 30 lines):
* Just implement it
* Run existing tests
* Skip memory.md
