---
name: implement
description: Standard TDD implementation workflow. Use for general coding tasks and issue resolution.
---

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

## Workflow

### Phase 1: Context & Setup
1.  **Understand Goal**: Read the issue description, PRD, or user request.
2.  **Learn Style**:
    -   Search for similar features in the codebase (`grep_search`).
    -   Identify patterns for naming, file structure, and implementation.
    -   **Rule**: Consistency > Novelty.

### Phase 2: TDD Cycle (Strict)
**Rule**: The task is NOT done until tests pass.

**Rule**: If you implement backend API changes, also implement the corresponding frontend site API integration. Use explicit `TODO:` markers only for temporary placeholders so they are easy to find, replace, and remove during cleanup.

1.  **Red (Write Test)**:
    -   Create a new test file or add a case to an existing one.
    -   Assert the specific acceptance criteria.
    -   Run the test. It **MUST FAIL**. (This validates the test).
2.  **Green (Implement)**:
    -   Write the minimum code to pass the test.
    -   Follow the patterns identified in Phase 1.
3.  **Refactor**:
    -   Clean up code.
    -   Ensure no regressions.

### Phase 3: Completion
-   [ ] Unit test exists and passes.
-   [ ] Code matches project style.
-   [ ] No mock data remains (unless prototyping).
-   [ ] "Definition of Done": All acceptance criteria met.

## Validation Checklist
Before finishing, ask yourself:
-   "Did I delete any dead code I created?"
-   "Did I leave any TODOs?"
-   "Did I break any existing tests?"
