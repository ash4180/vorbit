---
name: verify
version: 2.0.0
description: Use when user says "verify implementation", "check acceptance criteria", "validate feature", "does this meet requirements", "QA check", or wants to confirm code meets the original requirements and passes quality checks.
---

# Verify Skill

Validate that an implementation meets the requirements in the parent Linear issue / PRD — not just that tests pass.

> **Linear MCP namespace**: All Linear calls use `mcp__plugin_linear_linear__*`. Figma calls use `mcp__figma__*` for design-driven sub-issues.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

> **Required reading**: `/vorbit:implement:epic` produces sub-issues with structured sections (Required Sections per Sub-issue — see `skills/epic/output-schema.md`). Verify validates each section, not just tests. A passing test suite is the floor, not the ceiling.

> **UX patterns reference**: When validating state coverage, consult `_shared/ux-knowledge/edge-case-catalog.md` (concrete edge cases) and `ux-philosophy.md` (state-design principles). Read directly.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected platforms, ask user which to use, verify connection. If no PRD is needed, skip to Step 2.

## Step 2: Determine Context

1. **IF Linear issue ID provided**: Fetch the issue via `get_issue`. Read its description. Identify whether it's a sub-issue (has `parentId`) — if so, also fetch the parent epic for its Acceptance Criteria.
2. **IF Notion PRD URL**: Use `notion-fetch` to fetch the PRD.
3. **IF description only**: Ask the user for the acceptance criteria.
4. **IF no args**: Ask what to validate.

**Parse the sub-issue body for these sections** (per `skills/epic/output-schema.md → Required Sections per Sub-issue`):

| Section | What to look for |
|---------|------------------|
| Related Epic AC | List of `AC-*` IDs from parent epic this sub-issue must satisfy |
| Related Flow Steps | `F*-S*` IDs and touched surfaces |
| Reuse & Patterns | Utilities/constants/similar features the implementer was meant to use |
| FE Architecture Blueprint | 6-area table (reuse/create, hierarchy, data/API, state, design-system, test seams) |
| Design Source of Truth | Figma node IDs, target surface, states, conflicts |
| Screenshot Evidence | Figma reference + browser/app result expected |
| File Changes | CREATE/MODIFY file paths planned |
| Mock Data | Mock files/state planned |
| Acceptance Criteria | Sub-issue specific AC |
| Test Criteria | TDD requirements |

If the issue body is missing structured sections (older issues, hand-written), fall back to validating just the Acceptance Criteria + Test Criteria you can find.

## Step 3: Run Tests First

Detect and run the project test suite:
- Node: `npm test` or `yarn test`
- Python: `pytest`
- Go: `go test ./...`
- Rust: `cargo test`

**STOP if tests fail** — run `/vorbit:implement:implement` to fix first. No further validation runs until tests pass.

## Step 4: TDD-First Check (if Test Criteria section exists)

The sub-issue's Test Criteria was meant to be written FIRST per /epic's TDD rule. Verify:

1. **Tests exist** for every Test Criteria item:
   - Unit tests at the paths the issue's "File Changes" section listed under CREATE
   - E2E tests if the feature involves scripts, hooks, or data parsing
2. **Tests were committed before implementation** — check `git log` for the test file:
   - If the first commit that introduces the test file is the SAME commit that introduces the implementation, TDD was likely not followed
   - If test files don't exist at all, TDD was bypassed
3. **Assertions are non-vacuous** (per `output-schema.md → E2E Test Quality Rules`):
   - Before asserting on a file/response/record's content, assert it exists
   - E2E tests assert observable output (rendered UI, response body, files written), not internal signals (exit code, log lines)

Report TDD status:
- `[TDD OK] Tests written before implementation, observable assertions`
- `[TDD WARN] Tests exist but committed alongside implementation`
- `[TDD FAIL] No tests found for feature`

## Step 5: Validate Acceptance Criteria

For each `AC-*` item in the issue (and parent epic's "Related Epic AC" list):

1. Locate the code that implements the criterion (grep, file inspection)
2. Check the criterion against actual behavior — read code, optionally run the feature
3. Mark each criterion `[PASS]` / `[FAIL]` / `[PARTIAL]` with evidence
4. Cite file:line locations for each finding

If the criterion has a `[GIVEN/WHEN/THEN]` scenario format, walk each clause:
- GIVEN: precondition — is the setup present in code?
- WHEN: action — does the handler exist?
- THEN: outcome — does the code produce the stated result?

## Step 6: FE Architecture Blueprint Compliance (if UI work)

If the sub-issue has an "FE Architecture Blueprint" section, check the implementation against each row:

| Blueprint area | Verify by |
|----------------|----------|
| Reuse/create matrix | Each block in the mockup → actual component used. `Reuse`/`Adapt` items must reference existing files; `Create` items must have new files in the right location |
| Component hierarchy | Component tree matches the planned parent→children render order |
| Data/API contract | API call exists, handles loading/error/empty as planned |
| State ownership | State lives in the planned owner (URL/server/local/form/optimistic) |
| Design-system mapping | UI primitives/tokens/icons used match the plan |
| Test seams | Tests exist at the planned levels (unit/component/integration/screenshot) |

If the implementation diverges from the blueprint, mark as `[BLUEPRINT DRIFT]` and explain — divergence might be justified (new info during implementation) or a bug (silent override of the plan).

## Step 7: Design Source of Truth + Screenshot Evidence (if UI/design-driven)

If the sub-issue has a "Design Source of Truth" section with a Figma node ID:

1. **Fetch the Figma reference**: call `mcp__figma__get_design_context` with the primary node ID
2. **Capture browser/app screenshot** of the implemented surface:
   - Start the dev server if needed
   - Use a screenshot tool (browser MCP, Playwright, or manual)
3. **Compare side-by-side** per `_shared/figma-handoff.md` — layout, token bindings, states (empty/loading/error rendered as designed), and copy; follow the conflict rule when sources disagree.
4. **Flag mismatches**:
   - `[FIGMA MATCH]` — implemented surface matches the source node
   - `[FIGMA DRIFT — INTENTIONAL]` — differs from Figma but the issue has a noted exception
   - `[FIGMA DRIFT — UNEXPLAINED]` — differs with no documented reason → ask before passing

The issue's Screenshot Evidence section should already have the Figma reference + browser result captured by `/implement`. Cross-check that both screenshots exist and the comparison notes are present.

## Step 8: File Changes & Mock Data

**File Changes check**:
- Compare the issue's planned File Changes (CREATE/MODIFY rows) to `git diff --name-only` for this branch
- `[FILES OK]` — all planned files changed, no surprise files
- `[FILES UNEXPECTED]` — files outside the plan changed (could be valid, but explain)
- `[FILES MISSING]` — planned files weren't touched

**Mock Data check**:
- If the issue's Mock Data section lists entries, verify they're in `.claude/mock-registry.json`
- If the sub-issue is the LAST before backend handover, also check no `MOCK_` prefixed constants or hardcoded mock arrays remain in production paths (run `/vorbit:implement:cleanup-mocks` if not done)

## Step 9: i18n Compliance (if project has localization)

Per `_shared/frontend-knowledge/i18n-detection.md` — if the project uses i18n:
1. Grep the changed files for hardcoded user-facing strings (no `t()`, `useTranslations`, `$t`, etc. wrapping the text)
2. If hardcoded strings found, mark `[i18n MISSING]` with file:line
3. Check that translation keys exist in ALL locale files, not just the default

## Step 10: Code Hygiene

Scan for leftovers:
- `console.log` / `print` / debug statements
- `TODO` / `FIXME` comments introducing tech debt (existing comments OK if unrelated)
- Commented-out code blocks
- Dead code (functions/imports not referenced)

Report findings with file:line locations.

## Step 11: Report

```markdown
# Verification Report

## Status: [PASS / FAIL / PASS WITH WARNINGS]

### Tests
- Passed: X / Failed: Y
- TDD status: [OK / WARN / FAIL]

### Related Epic Acceptance Criteria
- [x] AC-1 ... — `src/path/file.ts:42`
- [ ] AC-2 ... — FAIL: [reason]
- [x] AC-3 ... — `src/path/file.ts:120`

### Sub-issue Acceptance Criteria
- [x] AC-SUB-1 ...
- [ ] AC-SUB-2 ... — FAIL

### FE Architecture Blueprint (UI work)
- [x] Reuse/create matrix followed
- [ ] State ownership: planned URL state, implemented as local state — drift

### Design Source of Truth (UI work)
- Figma reference: [node-id]
- Browser screenshot: [path or "captured"]
- [FIGMA MATCH] or [FIGMA DRIFT]: ...

### File Changes
- [FILES OK] / [FILES UNEXPECTED]: ...

### Mock Data
- [x] All planned mocks registered
- [ ] 2 unregistered mocks in `src/pages/X/`

### i18n (if applicable)
- [ ] 3 hardcoded strings in `src/components/Form.tsx:15-18`

### Hygiene
- Found 2 `console.log` in `utils.ts:34`, `helpers.ts:88`

### Verdict
[1-2 sentences. What's still blocking, or "Ready to mark Done."]
```

## Step 12: Update Linear

If validating a Linear issue:
- Add a verification comment with the report
- If PASS → update status to "Done" or "In Review" (per team convention)
- If FAIL → leave at "In Progress" and list the blockers

---

# Validation Schema

## Required Checks (in order)

| # | Check | Required when |
|---|-------|---------------|
| 1 | Tests pass | Always — blocking |
| 2 | TDD-first verified | If `Test Criteria` section exists |
| 3 | Acceptance Criteria | Always |
| 4 | FE Architecture Blueprint compliance | If `FE Architecture Blueprint` section exists |
| 5 | Figma Source of Truth + Screenshot Evidence | If `Design Source of Truth` section exists |
| 6 | File Changes match plan | If `File Changes` section exists |
| 7 | Mock Data registered | If `Mock Data` section exists or project has mocks |
| 8 | i18n complete | If project uses any i18n library |
| 9 | Code hygiene | Always |

## Pass / Fail / Warn Semantics

- **PASS**: every required check is `[OK]` or `[PASS]` for the rows that apply
- **PASS WITH WARNINGS**: required checks pass but non-blocking findings exist (hygiene leftovers, minor drift with explanation)
- **FAIL**: any required check is `[FAIL]`, or `[BLUEPRINT DRIFT — UNEXPLAINED]`, or `[FIGMA DRIFT — UNEXPLAINED]`, or `[TDD FAIL]`

## Anti-Patterns

- **Treating "tests pass" as full validation** — tests are the floor, not the ceiling. /epic produces sub-issues with rich requirements; tests cover only a slice.
- **Skipping Figma comparison when the issue says "match Figma"** — every UI sub-issue with a source node needs side-by-side screenshot validation
- **Marking PASS when File Changes are missing** — if the planned files weren't touched, the implementation is incomplete regardless of test results
- **Ignoring i18n in i18n projects** — missing translations are blocking, not cosmetic
- **Running /verify without parsing the sub-issue's structured sections** — defeats the purpose; you'd only be running tests and grep
