<!-- GENERATED from skills/qa-plan/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-qa-plan` skill directory (a sibling of `vorbit-shared`).

# QA Plan Skill

Build a test plan a person can click through. One check is one complete flow, from a named starting screen to the end result. The plan lives next to the other branch specs; the qa-report skill runs it and writes the report.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/spec-files.md` for spec path resolution, write guards, and file ownership before any spec read or write.

This plan is for testing by hand or by the agent in a browser. The implement skill already checks every acceptance criterion before a task is done; the two do not replace each other.

**Model roles:** use Claude Fable or Codex Astra (`gpt-6-astra`) for planning and reviewing results. Once a plan exists, qa-report hands browser execution to one native subagent in the same worktree: Claude's `vorbit:qa-runner` on Sonnet or Codex's runner on `gpt-6-luna`. A skill cannot change the current session's model: report the actual model when known, never claim a switch, and honor an explicit caller override. Hosts without native delegation and model selection report the missing capability as described in qa-report's runner reference.

## Unattended Runs

A run is unattended when the caller says no one is watching (for example "do not ask questions") or the session cannot take answers. In an unattended run, never stop to ask. Every place below that says "ask" becomes: make the sensible choice named there, and record it in the plan header as one `Assumed:` line per choice. Save the plan without the approval question. An unattended run never ends as `needs_input`.

## Step 1: Read the Branch Specs

1. Resolve the spec folder per `../references/spec-files.md`.
2. Read `prd.md` when it exists; it is the best source (stories, flows, criteria). If missing, run `git worktree list` first and report any sibling worktree that may hold it before building from scratch.
3. **No PRD is not a blocker.** When no `prd.md` exists anywhere, ask the user, batched: what the feature does, the main user paths (happy path first), and what must never break. Record `Source: conversation` in the header and group flows under one `## Feature flows` section. Mention once that `$vorbit-prd` would give the plan a firmer base, then continue.
   - Unattended: do not ask. Read the PR title and description (`gh pr view`), the commits since the base branch, and the diff. Record `Source: PR + diff` (or `Source: commits + diff`).
4. Read `epic.md` when present; it is the first choice for the regression list (its File Changes tables).
5. **Always run the regression scan**: `python3 scripts/regression_scan.py` from this skill's folder, inside the repository. Add `--base <ref>` when the caller names the comparison branch, or when the Base Branch section of the execution contract resolves one the script would miss. It prints the modified shared files with the files that use them, and the project's E2E suites. With `epic.md`, use the scan only to add shared files the epic missed and to find the test runner. Without `epic.md`, the scan is the regression source.
6. If `qa-plan.md` already exists, this run is a revision; the Step 4 preservation rules apply.

## Step 2: Resolve Test Targets

Ask the user, batched, whatever the PRD does not answer. Never guess:

1. **Devices**: which of mobile, tablet, desktop matter for this feature.
2. **Browsers**: which ones the team supports.
3. **Performance targets**: numbers from the PRD Success Criteria first; else simple observable targets ("list appears in under 3 seconds"), or `TBD-###`. Keep API response time apart from whole-page readiness. An API speed check needs a limit, a measurement, and a PROD address; while any is unresolved, write one Open items line instead of a check.
4. **Test environment**: where the tester clicks through (local app, staging URL, test account).
5. **Test data and preconditions**: the accounts, roles, workspaces, records, and starting state each flow needs. For a list or table, require repeated values in the displayed sort field and enough records to cross a page, lazy-load, or group boundary when those states are reachable. Name what exists today and what must be created. On the local app or DEV, mark records the test accounts can create through the app or the project's API as `Agent creates:`; the QA run creates them and deletes them after. Only data the agent cannot create, or any missing data on another environment, becomes a `TBD-###` with who provides it.
6. **Automated E2E runner**: do not ask; detect it: a `playwright.config.*` file, a Playwright or Cypress dependency in `package.json`, or an `e2e_suites` entry from the Step 1 scan.

Record unresolved items as `TBD-###` with the prd skill's impact classification. Performance targets and missing test data may stay unresolved in a saved plan, each with its impact line; unresolved devices, browsers, or primary test environment block the save.

Unattended: nothing blocks the save. Use these choices and write each one as an `Assumed:` line in the header:
- Devices: desktop, plus mobile when the diff touches layout or responsive styles
- Browsers: Chrome (the browser the E2E runner and browser tools use)
- Performance: `TBD-###`, unless the PR description states a number
- Environment: the preview or staging URL in the PR description; else the local dev server from the project's `dev` or `start` script
- Test data: the test accounts and seed data the repository documents (E2E setup, README, `.env.example`); else "any account with access to the changed screens"

## Step 3: Draft the Plan

**Writing rules (every check):**
- One check = one complete flow. It has a name a user would say ("Upgrade from Free with a new card"), 2 to 8 numbered steps, one `You should see:` with the end result (and any mid-flow result that matters), and one `Needs:` line (account, workspace, records, starting state). More than 8 steps means two flows.
- Plain language for a non-technical tester. Name screens and buttons the way the user sees them. No code words, no file paths.
- Put shared setup under `## Test data & preconditions`; the `Needs:` line names only what that flow uses.
- Check IDs are file-unique and never renumbered: `QA1`, `QA2`, … for story, failure, and performance flows; `QR1`, `QR2`, … for regression flows; `QP1`, … for commands.
- A step a person must do (judgment, real device, camera, print, sign-off) gets `**Needs human:** [what and why]` on the check. When the rest of the flow can run without it, split that step into its own check so an automated pass cannot clear the human part.

**Section sources:**
- **Test data & preconditions**: from Step 2. Name the account, role, workspace, starting state, and records. For a list or table, state the record count, repeated visible sort values, and reachable boundaries. No vague setup such as "use enough data."
- **Story flows**: one flow per user path in each story of `prd.md`: the happy path first, then each alternative path (conversation mode: from the gathered answers, under `## Feature flows`). Coverage gate: every acceptance criterion is checked by a `You should see:` line of some flow.
- **Failure paths**: one flow per realistic failure: wrong or empty input, offline or slow network, empty state, missing permission, double click or repeat. Derive from the flows and criteria; do not invent cases the feature cannot reach.
- **List & table reliability**: one flow whenever a story displays, sorts, filters, groups, paginates, lazy-loads, or selects rows. Its steps cover every applicable case: same row order and identity after refresh with repeated sort values; no missing or duplicate rows across a page, lazy-load, or group boundary; selection and row stability in filtered and unfiltered views; range or bulk selection across boundaries; a fetch-sensitive action repeated five times with no rows jumping.
- **Device & browser matrix**: map only the flows whose behavior can differ per device or browser to the Step 2 targets.
- **Regression flows**: never skipped. Source: `epic.md` File Changes when it exists; otherwise the scan's `shared_modified_files`. One flow per existing feature that uses a modified shared file, named in the words a user sees on screen. Skip created-from-scratch files. When many features use one file, test the three most-used screens and name the rest in one line. When no shared file changed, write one line saying so and naming the base branch. Always write `Regression source: epic.md` or `Regression source: git diff against [base]` under the heading.
- **Full regression suite**: only for a release plan (the caller says release). Then add the scan's primary suite as the first `QP#` check, labelled `Full regression suite`, using the QA-mode variant (such as `e2e:qa`) when the project has one. A PR plan never includes the full suite; the project's scheduled suite covers the rest of the app, and the plan says so in one line under Automated checks.
- **Performance flows**: human-observable phrasing of the Step 2 targets ("page is ready in under 3 seconds on a normal connection"). An API speed check only when its limit, measurement, and PROD address are resolved; it records both DEV and PROD, and PROD decides. Keep page readiness and API speed as separate checks.
- **Automated checks**: only when Step 2 detected a runner. Search the project's E2E folders for spec files that touch the changed screens and flows. One check per relevant spec file, with its exact run command. Add a `Covers:` mapping only after reading the test's assertions and confirming they verify the complete expected result with the required data and browser. Never map a human-only step to an automated pass. Add at most one `suggested:` line per story for an important flow no spec covers; a missing list or table reliability spec takes priority.

Before showing the draft, verify both coverage gates and state their results in chat: criteria coverage and list or table reliability coverage. Keep the mappings out of the file.

Show the full draft in chat and ask: **"Ready to save the QA plan?"** Do not write the file before approval. A request for a draft or review only stops here. Unattended: skip the question and save; the `Assumed:` lines take the place of the approval.

## Step 4: Write the File

1. Run the write guards per `../references/spec-files.md`.
2. Write `qa-plan.md` in the spec folder per the schema below.
3. **Revision rules:** preserve the `Result:` line of every unchanged check; never renumber existing IDs; new checks get fresh IDs continuing each sequence; list removed checks explicitly and ask before dropping any check whose last result is Failed (unattended: keep that check instead of asking).
4. Re-read the written file: every flow has steps, one `You should see:`, and a `Needs:` line; one section per PRD story; all IDs unique; every applicable list or table story has its reliability flow; the Regression section names its source and has at least one flow or the "no shared files changed" line.

## Step 5: Report

- File **path** and branch
- Counts: story flows, failure paths, list or table flows, matrix rows, regression flows, performance checks, automated checks
- Coverage gate results
- Any `TBD-###` left open, with who provides it
- Regression source (epic.md or git diff against which base) and whether this is a release plan with the full suite
- Unattended: every `Assumed:` line
- Reminder: the plan lives only in this worktree and is gitignored
- Next steps:
  - test by hand and record results (rules below)
  - `$vorbit-qa-report` to run the flows and write the dated report

## How the Tester Records Results

Whoever runs a flow (a person in the app, or the agent) adds or replaces one line under the check:

`Result: Passed | Failed | Not done (reason), YYYY-MM-DD, [name or agent], [Watch](link)`

- **Passed**: only after doing every step and seeing every `You should see:` result. An agent pass needs the recording link.
- **Failed**: add the step and what appeared, in 12 words or fewer.
- **Not done**: give the reason: `need [X]`, `needs a person`, `no recording`, `not reached`.
- Nothing else goes into the plan; detail and evidence live in the report. Never delete or rewrite a flow while recording results.
- Update the `Updated:` line in the header to the test date.

---

# qa-plan.md Schema

```markdown
# QA Plan: [Feature Name from prd.md H1]

Source: prd.md + epic.md (this folder)
Branch: [branch name]
Updated: [YYYY-MM-DD]
Environment: [where to test]
Devices: [list] | Browsers: [list]
Assumed: [unattended only: one line per choice made without asking]

## Test data & preconditions

- [account, role, workspace, and starting screen]
- [list or table only: record count, repeated visible sort values, and reachable boundaries]
- Agent creates: [records the QA run creates on the local app or DEV, then deletes]
- [what a person must provide, with its TBD-###]

## US-001: [Story Title]

### Story flows

- [ ] QA1: Upgrade from Free with a new card
  1. On the Free workspace, open Settings, then Billing.
  2. Click "Upgrade your plan" and pick a plan.
  3. Click "Add a card". On Stripe, enter 4242 4242 4242 4242 and confirm.
  4. Back on Billing, reload the page.
  You should see: "Card saved", the plan dialog open on your plan, and no second message after the reload.
  Needs: admin of a workspace billed in gems, no card saved.

### Failure paths

- [ ] QA2: Card declined on the first charge
  1. Save the card 4000 0000 0000 0341, pick a plan, click "Pay and start".
  You should see: "Card declined" saying nothing was charged; the plan stays Free.
  Needs: same workspace as QA1.

### List & table reliability

- [ ] QA3: Invoice list stays stable
  1. With 3 or more invoices, 2 from the same day, click "Refresh" five times.
  2. Reload the page five times.
  You should see: the same rows in the same order each time, none missing, none repeated.
  Needs: a workspace with 3 or more invoices, 2 issued the same day.

### Performance

- [ ] QA4: Billing page is ready quickly
  1. Open the Billing page on a normal connection.
  You should see: the full page in under 3 seconds.
  Needs: same workspace as QA1.

## US-002: [Story Title]

...

## Device & Browser Matrix

| Flow | Mobile | Desktop Chrome | Desktop Safari |
|------|--------|----------------|----------------|
| QA1  | yes    | yes            | yes            |

Only flows that can behave differently per device or browser get a row.

## Regression flows

Regression source: [epic.md | git diff against origin/dev]

- [ ] QR1: Members page still works
  1. Open Settings, then Members.
  You should see: the member list, with no error message.
  Needs: admin account.

## Automated checks

- [ ] QP1: run `npx playwright test e2e/tests/settings-sidebar.spec.ts`. You should see: all tests pass. Covers: QR1
- suggested: no spec covers the card return from Stripe (QA1)
- The full suite is not part of this plan; the project's scheduled suite covers the rest of the app.

## Open items

- TBD-001: [what is missing]. Who: [person]. Impact: [flows that wait on it].
```

Include the Automated checks section only when the project has a runner, and the `Assumed:` line only in unattended runs; `QP#` IDs follow the same never-renumber rule. In conversation mode (no `prd.md`), the header carries `Source: conversation` and story sections are replaced by one `## Feature flows` section. Include `### List & table reliability` only for stories with reachable list or table behavior.

Result line example:

```markdown
- [ ] QA2: Card declined on the first charge
  ...
  Result: Failed (step 1: the plan started anyway), 2026-10-16, agent, [Watch](qa-screenshots/2026-10-16/172402/qa2-card-declined.webm)
```
