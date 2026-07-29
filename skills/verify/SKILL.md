---
name: verify
description: Use when the user asks for a post-implementation validation against explicit acceptance criteria, a branch spec task or story, or a linked issue or PRD. It runs the real project tests, checks each criterion and code hygiene with evidence, reports pass or fail in the session, and may update spec task status or Linear issue status only when explicitly requested. Do not use to implement fixes, perform an open-ended code review, or validate requirements that have not been supplied.
---

# Verify Skill

Confirm that implementation meets Requirements, passes Tests, and maintains Quality.

Read and follow `../_shared/execution-contract.md` before starting.

## Step 1: Resolve Requirements

The branch spec files are the canonical requirements source — read `../_shared/spec-files.md` for path resolution. If the user supplied a Linear artifact, read `_shared/mcp-tool-routing.md` before fetching it. Pasted acceptance criteria and local descriptions remain valid read-only inputs.

## Step 2: Determine Context

1. **IF spec task or story ID** (`T3`, `US-002`) — or no args while the branch spec plan exists: read the task section(s) and story header from `epic.md` and the owning story from `prd.md`. Their acceptance criteria plus every `Test Criteria` section are the authoritative contract. With no args, confirm with the user which story to validate
2. **IF Linear issue ID**: Fetch issue and its acceptance criteria. If the issue carries a `## Test Criteria` section, it is the authoritative test contract — validate each entry alongside the acceptance criteria
3. **IF description**: Use explicit criteria; otherwise propose a checklist and label it as proposed
4. **IF no args and no spec plan**: Ask what to validate

Map every acceptance criterion to an observable check before running tests. Enumerate them in document order and check each one — none may be skipped.

## Step 3: Run Tests

Detect and run the project's test suite. Record every command, exit status, and material output.

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

## Step 7: Optional Status Update

If validating a spec task or story:
- Report all validation evidence in the current session
- Stay read-only unless the user explicitly requested a status update; then set the validated task's `**Status:**` line (`done` on pass, `blocked` plus the reason in the report on fail) and change nothing else in the file
- Suggest `/vorbit:implement:linear-sync` to refresh the Linear summaries after a status change

If validating a Linear issue:
- Report all validation evidence in the current session
- Stay read-only unless the user explicitly requested a Linear status update
- After a full pass, move to the team's review-ready state only if authorized
- Never mark the implementation parent Done before merge

---

# Verification Schema

A test failure is evidence for a FAIL result; continue independent safe checks and do not fix code in verification mode.

## Code Hygiene
Scan for "Leftovers":
- [ ] `console.log` / debug prints
- [ ] Commented-out blocks of code
- [ ] `TODO` or `FIXME` comments introducing tech debt
