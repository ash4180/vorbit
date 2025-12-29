---
description: Validate implementation against acceptance criteria
argument-hint: [Linear issue ID or feature description]
allowed-tools: Read, Bash, Grep, Glob, mcp__plugin_Notion_notion__*, mcp__plugin_linear_linear__*
---

Validate: $ARGUMENTS

## Determine Context

1. **IF Linear issue ID**: Fetch issue and its acceptance criteria
2. **IF Notion PRD URL**: Fetch PRD and use success criteria
3. **IF description**: Ask user for acceptance criteria
4. **IF no args**: Ask what to validate

## Run Tests

Detect and run project test suite:
- Node: `npm test` or `yarn test`
- Python: `pytest`
- Go: `go test ./...`
- Rust: `cargo test`

**STOP if tests fail** - run `/vorbit:implement:implement` to fix first

## Validate Acceptance Criteria

For each criterion:
1. Check if implementation satisfies requirement
2. Mark PASS or FAIL with evidence
3. Note any gaps

## Code Cleanliness

Scan for issues:
- TODO/FIXME comments
- Debug statements (console.log, print, etc.)
- Commented-out code

Report findings with file:line locations.

## Report

```
VALIDATION: PASS / FAIL

Tests: X passed, Y failed
Acceptance Criteria: X/Y passed

[If issues]
Failed Criteria:
1. [Criterion]: [Why it failed]

Code Issues:
- [file:line]: [issue]

[If pass]
Ready for: PR review / deployment
```

## Update Linear

If validating a Linear issue:
- Add validation comment with results
- Update status if passed
- Link any relevant PRs
