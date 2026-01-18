---
name: verify
version: 1.1.0
description: Use when user says "verify implementation", "check acceptance criteria", "validate feature", "does this meet requirements", "QA check", or wants to confirm code meets the original requirements and passes quality checks.
---

# Verify Skill

Confirm that implementation meets Requirements, passes Tests, and maintains Quality.

## Step 1: Detect Platform & Verify Connection

**IF user provides a PRD reference, auto-detect platform:**
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

**IF no PRD is needed:** skip to Step 2

## Step 2: Determine Context

1. **IF Linear issue ID**: Fetch issue and its acceptance criteria
2. **IF Notion PRD URL**: Fetch PRD from Notion and use success criteria
3. **IF Anytype PRD URL or object ID**: Fetch PRD from Anytype and use success criteria
4. **IF description**: Ask user for acceptance criteria
5. **IF no args**: Ask what to validate

## Step 3: Run Tests

Detect and run project test suite:
- Node: `npm test` or `yarn test`
- Python: `pytest`
- Go: `go test ./...`
- Rust: `cargo test`

**STOP if tests fail** - run `/vorbit:implement:implement` to fix first

## Step 4: Validate Acceptance Criteria

For each criterion:
1. Check if implementation satisfies requirement
2. Mark PASS or FAIL with evidence
3. Note any gaps

Output format:
- `[PASS] Criterion 1`
- `[FAIL] Criterion 2 - [reason]`

## Step 5: Code Hygiene

Scan for issues:
- TODO/FIXME comments
- Debug statements (console.log, print, etc.)
- Commented-out code

Report findings with file:line locations.

## Step 6: Report

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

## Step 7: Update Linear

If validating a Linear issue:
- Add validation comment with results
- Update status if passed
- Link any relevant PRs

---

# Verification Schema

## Verification Checklist

### 1. Automated Tests
- Run the project's test suite (Node, Python, Go, etc.)
- **Constraint**: If tests fail, STOP. Fix the code first.

### 2. Acceptance Criteria (AC)
- Retrieve AC from the Issue, PRD, or Request
- Check each criterion explicitly
- Output: `[PASS] Criterion 1` or `[FAIL] Criterion 2`

### 3. Code Hygiene
Scan for "Leftovers":
- [ ] `console.log` / debug prints
- [ ] Commented-out blocks of code
- [ ] `TODO` or `FIXME` comments introducing tech debt
