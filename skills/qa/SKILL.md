---
name: qa
version: 1.0.0
description: Use when user says "QA plan", "test plan", "test coverage", "QA coverage", "write test cases", "audit test coverage", or wants to generate a structured QA test plan for a project. Generates test plans (not test results). Supports codebase audit, browser validation, and coverage comparison.
---

# QA Skill

Generate structured QA test plans by auditing the codebase, validating against the live app, and outputting to Notion or Anytype.

**Critical distinction:** This skill produces **test plans** (what SHOULD be tested with expected behavior), NOT **test execution reports** (what WAS tested with pass/fail results). Never mix them unless explicitly asked.

## References

Detailed specs live in `references/` within this skill's directory. Glob for `**/skills/qa/references/` to resolve the path.

| File | Contains |
|---|---|
| `references/test-plan-format.md` | Test type taxonomy, table format spec, priority tiers, Notion markdown templates |
| `references/coverage-audit.md` | Codebase audit steps, route discovery, component inventory, existing test detection |
| `references/comparison.md` | How to compare two QA documents, overlap matrix, gap analysis format |

---

## Mode Detection

1. **`--plan` or no flag** (default) → **Plan Mode** — full QA plan generation
2. **`--compare <file>`** → **Compare Mode** — compare existing test doc against a plan
3. **`--audit`** → **Audit Mode** — codebase stats only, no plan output
4. **`--validate`** → **Validate Mode** — use Chrome to confirm plan against live app

---

## Plan Mode (Default)

### Step 1: Detect Platform & Verify Connection

Read and follow the platform detection steps in `_shared/platform-detection.md` (glob for `**/skills/_shared/platform-detection.md`). Pass the detected platform to subsequent steps.

### Step 2: Audit the Codebase

Read `references/coverage-audit.md` for the full audit procedure. Execute it.

**Summary of what to discover:**
1. **Routes** — scan router config (App.tsx, routes.ts, etc.) for all defined routes
2. **Pages** — glob `src/pages/**/*.tsx` (or framework equivalent) to count page components
3. **Compositions/Components** — count shared components
4. **Utilities** — count helper files
5. **Existing tests** — glob `**/*.test.*`, `**/*.spec.*`, `**/__tests__/**` to count current test files
6. **Sidebar/Navigation** — find nav config to identify user-facing feature areas
7. **Coverage percentage** — test files / total source files

Dispatch an Explore agent for this work. Output is the **Codebase Audit Summary**.

### Step 3: Identify Feature Areas

From the audit, group routes and pages into feature areas. Typical grouping:
- Each top-level sidebar section = one feature area
- Hidden routes (no sidebar entry) = flag as potential issues
- Auth/layout/error = cross-cutting concerns

Assign priority tiers:
- **P0** — Core business flows (the reason users open the app)
- **P1** — Important supporting features
- **P2** — Secondary features, configuration, analytics

### Step 4: Generate Test Cases

Read `references/test-plan-format.md` for the table format and test type taxonomy.

For each feature area, generate test cases covering:

1. **Smoke tests** — page loads, critical elements visible
2. **Functional tests** — interactive elements work (filters, dropdowns, forms, navigation)
3. **E2E tests** — complete user flows (create, edit, delete, full lifecycle)
4. **Edge cases** — concurrency, permissions, bulk operations, empty states, invalid input, boundary values
5. **Validation tests** — data accuracy, required fields, format enforcement
6. **Security tests** — auth redirects, RBAC, token handling
7. **Performance tests** — large datasets, slow networks, many concurrent users
8. **Regression tests** — known bugs that must stay fixed
9. **Integration tests** — external service connections (Slack, email, OAuth)

**Depth targets per area:**
- P0 areas: 15-30 test cases each
- P1 areas: 8-15 test cases each
- P2 areas: 5-10 test cases each

### Step 5: Browser Validation (Optional)

If Chrome MCP tools are available and user wants validation:

1. Navigate to each route on the live app
2. Use `read_page` to confirm elements exist
3. Confirm feature area grouping matches actual sidebar
4. Note any bugs found (add to Known Issues section)

**Known limitation:** Excel Online, Google Sheets, and other iframe-heavy apps are NOT accessible via Chrome MCP. If content is behind auth, ask user to download the file locally.

### Step 6: Show Draft in Chat

Present the full test plan in chat for review before saving:

```
# QA Test Plan — [Project Name]

## Codebase Audit Summary
- Pages: X | Components: Y | Utilities: Z
- Existing tests: N (M% coverage)
- Feature areas: K

## Test Cases by Feature Area
[tables per section]

## Known Issues
[bugs found during validation]

## Summary
Total: X test cases | Smoke: N | Functional: N | E2E: N | Edge Case: N | ...
```

**After showing draft, ask:** "Does this plan look good? Ready to save?"

### Step 7: Save to Platform

**Only proceed after user confirms the draft.**

**If platform was detected in Step 1:** use that platform directly.

**If no platform detected:** Use AskUserQuestion: "Where should I save this QA plan?"

### If Notion:
1. Ask for database name or page URL
2. Use `notion-find` to locate target database
3. Fetch database schema to understand properties
4. Create page with:
   - Name = "QA Coverage Plan — [Project Name]"
   - Type = `["Document"]` (if property exists)
   - Description = summary line
   - Body = full test plan in Notion-flavored markdown
5. Use tables with `fit-page-width="true"` and `header-row="true"`
6. Use callouts for summary and known issues
7. Use `table_of_contents` after the header callout

### If Anytype:
1. Use `API-list-spaces` to show available spaces
2. Ask user which space
3. Use `API-create-object` with full plan as markdown body

### Step 8: Verify Output

Fetch the saved page back to confirm content rendered correctly. If tables are broken or content is truncated, fix and re-save.

### Step 9: Report

```
QA Plan saved:
- URL: [link]
- Feature areas: X
- Test cases: Y (Smoke: N, Functional: N, E2E: N, Edge: N, ...)
- Known issues: Z
- Next: Share with QA team or run /vorbit:qa --compare to check against existing test docs
```

---

## Compare Mode

Compare an existing test document against the QA plan.

### Step 1: Load Both Documents

1. **QA plan** — fetch from Notion/Anytype (user provides URL or ID)
2. **Existing doc** — user provides file path (PDF, Excel, CSV) or URL

For authenticated URLs (SharePoint, Google Docs): ask user to download locally. Read PDF/Excel with the Read tool.

### Step 2: Parse Both

Extract test cases from both documents. Normalize into: `[ID, Description, Feature Area, Type]`.

### Step 3: Build Coverage Matrix

Read `references/comparison.md` for the comparison format. Output:

| Feature Area | Plan Count | Doc Count | Coverage | Gaps |
|---|---|---|---|---|
| Incidents | 30 | 35 | Deep but partial | Missing: pagination, AI summary |
| Alerts | 17 | 1 | 6% | Missing: filters, bulk actions, detail |

### Step 4: Identify

1. **Direct overlaps** — test cases that exist in both (table of mappings)
2. **Plan has, doc doesn't** — gaps in existing testing
3. **Doc has, plan doesn't** — valuable additions to incorporate
4. **Overall coverage %** — doc covers X% of plan scope

### Step 5: Report

Present comparison in chat. Ask if user wants to update the plan with findings from the existing doc.

---

## Audit Mode

Codebase stats only. No plan, no output.

1. Run Step 2 from Plan Mode (codebase audit)
2. Present stats in chat
3. Stop

---

## Validate Mode

Browser validation only against an existing plan.

1. Fetch the QA plan from Notion/Anytype
2. Run Step 5 from Plan Mode (browser validation)
3. Update the plan's Known Issues section with findings
4. Report what was validated and what bugs were found

---

## Error Handling

- **No routes found** → "Can't detect routes. What's the router file?" Ask user.
- **Notion connection fails** → "Notion connection expired. Run `/mcp` to reconnect."
- **Chrome MCP unavailable** → Skip browser validation. Note in output.
- **PDF/Excel can't be read** → "Can't parse this file format. Try exporting as CSV or paste the content."
- **Database has no Type property** → Skip setting Type, just set Name and body.
