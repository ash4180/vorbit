---
name: verify
description: Use when the user asks for a post-implementation validation against explicit acceptance criteria or a linked issue or PRD. It runs the real project tests, checks each criterion and code hygiene with evidence, reports pass or fail, and may comment on or update the Linear issue. Do not use to implement fixes, perform an open-ended code review, or validate requirements that have not been supplied.
---

# Verify Skill

Confirm that implementation meets Requirements, passes Tests, and maintains Quality.

Read and follow `../_shared/execution-contract.md` before starting.

## Step 1: Resolve Requirements

Read and follow `_shared/mcp-tool-routing.md` only when the user supplied an external artifact. Linear is the canonical PRD source; pasted acceptance criteria and local descriptions remain valid read-only inputs.

## Step 2: Determine Context

1. **IF Linear issue ID**: Fetch issue and its acceptance criteria
2. **IF description**: Use explicit criteria; otherwise propose a checklist and label it as proposed
3. **IF no args**: Ask what to validate

Map every acceptance criterion to an observable check before running tests. Enumerate them in document order and check each one — none may be skipped.

## Step 3: Run Tests

Detect and run project test suite:
- Node: `npm test` or `yarn test`
- Python: `pytest`
- Go: `go test ./...`
- Rust: `cargo test`

Record every command, exit status, and material output.

## Step 4: Validate Acceptance Criteria

For each criterion:
1. Check if implementation satisfies requirement
2. Mark PASS or FAIL with evidence (output format per the Verification Schema below)
3. Note any gaps

## Step 5: Code Hygiene

Scan for the leftovers listed in the Verification Schema below. Report findings with file:line locations.

## Step 6: Report

```markdown
# Verification Report

## Status: [PASS / FAIL / BLOCKED]

### Tests
- `[command]` → exit [code] — [result]

### Acceptance Criteria
- [x] Criterion 1
- [ ] Criterion 2 (Evidence of failure...)

### Hygiene
- Found 2 console.logs in `utils.ts`
- Clean? [Yes/No]

### Unverified
- [Anything not run or not observable, with reason]
```

## Step 7: Optional Linear Update

If validating a Linear issue:
- Stay read-only unless the user explicitly requested a Linear update
- After a full pass, add the validation evidence and move to the team's review-ready state if authorized
- Never mark the implementation parent Done before merge

---

# Verification Schema

## Verification Checklist

### 1. Automated Tests
- Run the project's test suite (Node, Python, Go, etc.)
- A test failure is evidence for a FAIL result; continue independent safe checks and do not fix code in verification mode

### 2. Acceptance Criteria (AC)
- Retrieve AC from the Issue, PRD, or Request
- Check each criterion explicitly
- Output: `[PASS] Criterion 1` or `[FAIL] Criterion 2`

### 3. Code Hygiene
Scan for "Leftovers":
- [ ] `console.log` / debug prints
- [ ] Commented-out blocks of code
- [ ] `TODO` or `FIXME` comments introducing tech debt
