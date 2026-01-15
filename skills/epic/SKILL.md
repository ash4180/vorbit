---
name: epic
description: Linear issue schema and planning workflow. Use when converting PRD user stories into executable EPICS and Issues.
---

# Epic Planning Skill

This skill handles the transformation of User Stories (from PRD) into executable Engineering Tasks (Epics/Issues).

## Workflow Instructions

### Step 1: Context & Platform
1.  **Analyze Request**: Identify the source PRD (Notion/Anytype) or feature description.
2.  **Verify Connections**:
    -   If Notion: Run `notion-find` to verify access.
    -   If Anytype: Run `API-list-spaces` to verify access.
    -   *If connection fails, stop and notify user.*

### Step 2: PRD Analysis
1.  **Extract User Stories**: Read the PRD.
2.  **Breakdown**:
    -   **1 User Story = 1 Epic** (Parent Issue).
    -   Complex stories? Break into **Sub-issues**.
3.  **Check Existing**: Search Linear for duplicates before creating.

### Step 3: Technical Planning (The "How")
Before creating issues, draft a loose plan:
-   **Style Check**: `grep` for similar existing features.
-   **Data Model**: What needs to change?
-   **Dependencies**: What must happen first? (Mark as `[Blocker]`).

### Step 4: Execution (Create Issues)
**Rule**: Get User Approval on the plan before creating 10+ issues.

1.  **Create Parent Issue (Epic)**:
    -   Title: `add-[feature-name]` (Branch-friendly kebab-case).
    -   Description: PRD Link + Acceptance Criteria.
2.  **Create Sub-issues**:
    -   Link to Parent `parentId`.
    -   Apply **Parallel** label for independent tasks (see criteria below).

---

# Epic Schema & Standards

## Title Format
**Transform the User Story Goal into a kebab-case title.**

| User Story | Epic Title |
| :--- | :--- |
| "As a user, I want to **login**..." | `add-user-login` |
| "As an admin, I want to **manage users**..." | `add-admin-user-management` |

**Rules**:
-   Action verbs: `add-`, `implement-`, `fix-`, `update-`.
-   Lowercase, hyphens, no special chars.
-   Match Git branch conventions.

## Issue Structure

### Epic (Parent)
-   **Description**:
    ```markdown
    ## User Story
    US-XXX: As a [user], I want [goal]...

    ## Acceptance Criteria
    - [ ] Criterion 1
    - [ ] Criterion 2

    ## Test Criteria (TDD - write tests FIRST)
    - [ ] Unit test: [component behavior]
    - [ ] Integration test: [user flow]

    ## PRD Reference
    [Link]
    ```

### Sub-issue (Child)
-   **Title**: `component-name` or `step-name` (use **Parallel** label, not prefix).
-   **Description**:
    ```markdown
    ## Summary
    [Technical task description]

    ## Acceptance Criteria
    - [ ] Criterion 1
    - [ ] Criterion 2

    ## Test Criteria (TDD - write tests FIRST)
    - [ ] Unit test: [specific behavior]
    - [ ] Unit test: [edge case]
    ```
-   **Priority Mapping**:
    -   P1 (Urgent): Core / Blocker.
    -   P2 (High): Important.
    -   P3 (Normal): Standard.

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
