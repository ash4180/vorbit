---
name: qa-plan
description: Use when the user asks to build or update a QA test plan for the current branch — a human-runnable checklist covering story flows, test data, edge cases and error paths, list and table reliability, device and browser coverage, regression risks, performance checks, and automated Playwright runs when the project has them. It drafts from the branch prd.md and epic.md when they exist, or from answers the user gives when they do not, and writes the plan to the branch spec folder. Do not use for agent-run acceptance validation (that is verify), writing requirements, or implementing fixes.
---

# QA Plan Skill

Build a manual test plan a human can click through: plain language, one action and one expected result per check. The plan lives next to the other branch specs, and linear-sync reports its progress on the story tickets.

Read and follow `../_shared/execution-contract.md` before starting.

Read `../_shared/spec-files.md` for spec path resolution, write guards, and file ownership before any spec read or write.

This plan is for a person testing by hand. Agent-run acceptance validation stays in `/vorbit:implement:verify`; the two do not replace each other.

## Step 1: Read the Branch Specs

1. Resolve the spec folder per `../_shared/spec-files.md`.
2. Read `prd.md` when it exists — it is the best source (stories, flows, criteria). If it is missing, run `git worktree list` first and report any sibling worktree that may hold it before building from scratch.
3. **No PRD is not a blocker.** When no `prd.md` exists anywhere, build the plan from the user instead: ask, batched, what the feature does, the main user actions (happy path), and what must never break. Their answers take the place of stories and criteria. Record `Source: conversation` in the file header, and group checks under one `## Feature checks` section instead of story sections. Mention once that `/vorbit:design:prd` would give the plan a firmer base, then continue.
4. Read `epic.md` when present — the regression list is built from its File Changes tables. Without it, build the other sections and state plainly that the regression list is skipped until the epic plan exists.
5. If `qa-plan.md` already exists, this run is a revision — the Step 4 preservation rules apply.

## Step 2: Resolve Test Targets

Ask the user, batched, whatever the PRD does not answer. Never guess:

1. **Devices** — which of mobile / tablet / desktop matter for this feature
2. **Browsers** — which ones the team supports
3. **Performance targets** — take numbers from the PRD Success Criteria first; if none apply, ask for simple observable targets (for example "list appears in under 3 seconds"), or mark `TBD-###`
4. **Test environment** — where the tester clicks through (local app, staging URL, test account)
5. **Test data and preconditions** — the account, role, records, and starting state needed to run the checks. For any list or table, require repeated values in the displayed sort field and enough records to cross a page, lazy-load, or group boundary when those states are reachable.
6. **Automated E2E runner** — do not ask; detect it: a `playwright.config.*` file or a Playwright/Cypress dependency in `package.json`. If found, the plan gets an Automated checks section (Step 3)

Record unresolved items as `TBD-###` with the prd skill's impact classification. Only performance targets may stay TBD in a saved plan; unresolved devices, browsers, environment, or required test data block the save.

## Step 3: Draft the Plan

**Writing rules (every check):**
- Plain language for a non-technical tester. Name screens and buttons the way the user sees them. No code words, no file paths.
- One check = one action plus one `You should see:` result. If a check needs "and then" twice, split it.
- Put shared setup under `## Test data & preconditions`; do not repeat it inside every check.
- Check IDs are file-unique and never renumbered: `QA1`, `QA2`, ... for story/edge/performance checks; `QR1`, `QR2`, ... for regression checks.

**Section sources:**
- **Test data & preconditions** — from Step 2. Name the account, role, starting state, and records the tester needs. For a list or table, state the required record count, repeated visible sort values, and page, lazy-load, or group boundaries. Do not use vague setup such as "use enough data."
- **Story checks** — from each story's User Flow and acceptance criteria in `prd.md` (conversation mode: from the gathered answers, under `## Feature checks`). Requirements coverage gate: every acceptance criterion — or every gathered answer — is covered by at least one check in its own section.
- **Edge cases & errors** — realistic failure paths per story: wrong or empty input, offline or slow network, empty states, permission limits, double-click/repeat actions. Derive from the flows and criteria; do not invent scenarios the feature cannot reach.
- **List & table reliability** — required whenever a story displays, sorts, filters, groups, paginates, lazy-loads, or selects rows. Add every applicable check below; omit only unreachable cases:
  - when records do not change, repeated visible sort values keep the same row order and identity after refresh or refetch
  - when records do not change, crossing a page, lazy-load, or group boundary creates no missing or duplicate rows
  - applicable selection and row-stability checks run in both filtered and unfiltered views
  - range or bulk selection works across reachable boundaries
  - an intermittent or fetch-sensitive action succeeds five times without rows jumping
- **Device & browser matrix** — map only the checks whose behavior can differ per device or browser to the targets from Step 2. Do not list every check.
- **Regression checks** — from `epic.md` File Changes: for each modified shared file, name the existing feature that uses it and add one check that it still works. Skip created-from-scratch files.
- **Performance checks** — human-observable phrasing of the Step 2 targets ("page is ready in under 3 seconds on a normal connection", "scrolling a long list stays smooth"). One check per target.
- **Automated checks (Playwright)** — only when Step 2 detected an E2E runner. Search the project's E2E folders for spec files touching the screens and flows in this plan. One check per relevant spec file, with its exact run command and which manual checks a green run covers — so the tester can skip hand-testing what the machine already proves. Add at most one `suggested:` line per story for an important flow no spec covers yet; when list or table reliability lacks automation, that gap takes priority. A suggestion does not replace the manual reliability check.

Before showing the draft, verify both coverage gates and state their results in chat: requirements coverage and applicable list/table reliability coverage. Keep the mappings out of the file. A plan fails the second gate if it uses only small, unique, single-page data for a reachable list or table state.

Show the full draft in chat and ask: **"Ready to save the QA plan?"** Do not write the file before approval. A request for a draft or review only stops here.

## Step 4: Write the File

1. Run the write guards per `../_shared/spec-files.md`.
2. Write `qa-plan.md` in the spec folder per the schema below.
3. **Revision rules:** preserve the `- [x]` state and any `**Fail:**` note of every unchanged check; never renumber existing IDs; new checks get fresh IDs continuing each sequence; list removed checks explicitly and ask before dropping any check that has a `**Fail:**` note.
4. Re-read the written file: one section per PRD story, all IDs unique, every section from the schema present, and every applicable list or table story has reliability checks (Regression may carry the "skipped — no epic.md" note).

## Step 5: Report

- File **path** and branch
- Counts: story checks, edge cases, list/table reliability checks, matrix rows, regression checks, performance checks (per story where it applies)
- Requirements coverage gate and list/table reliability gate results
- Any `TBD-###` left open
- Reminder: the plan lives only in this worktree and is gitignored
- Next steps:
  - test by hand and tick the boxes (recording rules below)
  - `/vorbit:implement:qa-report` to run the automated checks and write the dated report
  - `/vorbit:implement:linear-sync` to show "QA: N of M checks passed" on each story ticket

## How the Tester Records Results

Whoever runs the plan (a person, in the app):

- **Passed** → tick the box: `- [x] QA3: ...`
- **Failed** → leave the box unchecked and add one indented line under the check: `**Fail:** [what actually happened] ([date])`
- Never delete or rewrite a check while recording results; notes go under the check.

linear-sync counts ticked boxes per story section and flags `**Fail:**` notes on the story ticket.

---

# qa-plan.md Schema

```markdown
# QA Plan: [Feature Name from prd.md H1]

Source: prd.md + epic.md (this folder)
Branch: [branch name]
Environment: [where to test]
Devices: [list] | Browsers: [list]

## Test data & preconditions

- [account, role, and starting screen]
- [list/table only: record count, repeated visible sort values, and reachable page/lazy-load/group boundaries]

## US-001: [Story Title]

### Story checks

- [ ] QA1: [action on a named screen]. You should see: [result]
- [ ] QA2: [next action]. You should see: [result]

### Edge cases & errors

- [ ] QA3: [wrong input / offline / empty case]. You should see: [safe, clear result]

### List & table reliability

- [ ] QA4: Without changing any records, refresh a list with [repeated visible sort values]. You should see: the same rows stay in the same order with no missing or duplicate rows.
- [ ] QA5: Repeat [range or bulk selection] five times across [page/lazy-load/group boundary]. You should see: the intended rows stay selected and no row jumps.

### Performance

- [ ] QA6: [observable target, e.g. results appear in under 3 seconds]

## US-002: [Story Title]

...

## Device & Browser Matrix

| Check | Mobile | Desktop Chrome | Desktop Safari |
|-------|--------|----------------|----------------|
| QA1   | yes    | yes            | yes            |
| QA3   | yes    | no             | no             |

Only checks that can behave differently per device or browser get a row.

## Regression checks

- [ ] QR1: [existing feature touched by this change] still works: [action]. You should see: [result]

## Automated checks (Playwright)

- [ ] QP1: run `npx playwright test e2e/login.spec.ts`. You should see: all tests pass. Covers: QA1, QA2
- suggested: no spec covers the empty-email error yet (QA3)
```

Include the Automated checks section only when the project has an E2E runner; `QP#` IDs follow the same never-renumber rule. In conversation mode (no `prd.md`), the header carries `Source: conversation` and story sections are replaced by one `## Feature checks` section.

Include `### List & table reliability` only for stories with reachable list or table behavior. Its checks and concrete test data are mandatory when it applies.

Fail note example:

```markdown
- [ ] QA3: Submit the form with an empty email. You should see: "Email required".
  **Fail:** form submitted with no error (2026-07-30)
```
