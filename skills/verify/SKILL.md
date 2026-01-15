---
name: verify
description: Validate implementation against acceptance criteria and ensure code quality.
---

# Verify Skill

## Objective
Confirm that the implementation meets Requirements, passes Tests, and maintains Quality.

## Verification Checklist

### 1. Automated Tests
-   Run the project's test suite (Node, Python, Go, etc.).
-   **Constraint**: If tests fail, STOP. Fix the code first.

### 2. Acceptance Criteria (AC)
-   Retrieve AC from the Issue, PRD, or Request.
-   Check each criterion explicitly.
-   Output: `[PASS] Criterion 1` or `[FAIL] Criterion 2`.

### 3. Code Hygiene
Scan for "Leftovers":
-   [ ] `console.log` / debug prints
-   [ ] Commented-out blocks of code
-   [ ] `TODO` or `FIXME` comments introducting tech debt

## Report Template
```markdown
# Verification Report

## Status: [PASS / FAIL]

### Tests
- Passed: [X]
- Failed: [Y]

### Acceptance Criteria
- [x] Criterion 1
- [ ] Criterion 2 (Evidence of failure...)

### Hygiene
- Found 2 console.logs in `utils.ts`
- Clean? [Yes/No]
```
