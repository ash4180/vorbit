---
description: Validate implementation against epic acceptance criteria
---

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Source `tools/scripts/common.sh`
3. **Resolve feature context**:
   - **IF argument is existing feature slug**: Use that slug
   - **IF no argument**: Run `list_features` to show available features and ask user which to validate
4. Run `tools/scripts/task.sh setup` to validate environment

## Input Sources (priority order)

1. **IF EXISTS** `.vorbit/features/<slug>/epic.md`: Use epic acceptance criteria
2. **ELSE IF `{ARGS}`**: Use provided acceptance criteria directly
3. **ELSE**: Error - no validation criteria found

## 1. Check Task Completion

- Read `.vorbit/features/<slug>/tasks.md`
- Verify all tasks marked as completed
- Report any incomplete or failed tasks
- **STOP if tasks incomplete** - cannot validate partial implementation

## 2. Run Integration Tests

- Find test files in project (look for test directories, *_test.*, *.test.*, etc.)
- Run the project's test suite using detected test runner:
  - Node: `npm test` or `yarn test`
  - Python: `pytest` or `python -m unittest`
  - Go: `go test ./...`
  - Rust: `cargo test`
- Capture and report test results
- **STOP if tests fail** - fix before validating

## 3. Validate Acceptance Criteria

- Read acceptance criteria from `.vorbit/features/<slug>/epic.md` `## Acceptance Criteria` section
- For each criterion:
  - Check if implementation satisfies the requirement
  - Mark as PASS or FAIL with evidence
  - Note any gaps or partial implementations

## 4. Generate Validation Report

Save to `.vorbit/logs/<slug>-validation-report.md`:

```markdown
# Validation Report
Date: [current date]
Feature: [slug]
Epic: [epic name]

## Task Status
- Total: X tasks
- Completed: X
- Failed: X

## Test Results
- Test suite: [passed/failed]
- Coverage: X% (if available)

## Acceptance Criteria
- [ ] Criterion 1: PASS/FAIL [evidence]
- [ ] Criterion 2: PASS/FAIL [evidence]

## Summary
[Overall pass/fail with notes]

## Next Steps
[If failed: what needs fixing]
[If passed: ready for deployment/review]
```

## 5. Update Epic Progress

- Mark Phase 5 complete in `.vorbit/features/<slug>/epic.md` if validation passes
- Report final status to user

## 6. Code Cleanliness Check

Scan modified files for implementation artifacts:

**Search for:**
- `// TODO`, `// FIXME`, `// HACK`, `// XXX` comments
- `[UNCLEAR]` markers from task generation
- Debug statements: `console.log`, `print(`, `fmt.Println`, `println!`
- Commented-out code blocks

**Report findings:**
```
Code Cleanliness:
- 3 TODO comments found (file.ts:42, file.ts:89, utils.ts:12)
- 1 debug console.log (api.ts:156)
- 0 UNCLEAR markers
```

**IF issues found:** List them, ask user if they should be removed or are intentional.

## 7. Cleanup (On Pass)

**IF validation passes AND code is clean (or user approved):**

Ask user: "Validation passed. Clean up working files? (y/n)"

**On confirm:**
1. Remove `.vorbit/features/<slug>/` directory
2. Report: "Cleaned up. Feature `<slug>` complete."

**On decline:**
- Keep all files
- Report: "Files preserved. Run `/vorbit:manage:validate <slug>` again when ready to cleanup."

## Output

- Display validation report summary
- Show feature slug: `[<slug>]`
- Show PASS or FAIL status
- List any failed criteria with details
- Code cleanliness status
- Cleanup status (if performed)
- Suggest next steps
