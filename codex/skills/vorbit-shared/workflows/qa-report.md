<!-- GENERATED from skills/qa-report/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# QA Report Skill

Run the QA plan and turn the results into a dated, forwardable report: what passed, what failed, and whether the feature is ready. Testing and reporting happen in one run — the skill executes the automated commands, can click through manual checks in a real browser, and then writes the report. Every check the agent runs also gets a picture, saved next to the report and shown inside it. Every fail also gets a suggested modern fix, written against the project's current framework patterns, never against habit. The report is a plain-language file a stakeholder can read without opening the app or the plan.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/spec-files.md` for spec path resolution, write guards, and file ownership before any spec read or write.

Read `../references/pre-existing-findings.md` for how to tag, report, and follow up fails this branch did not cause.

This skill writes to Linear only for a follow-up ticket the user approves per `pre-existing-findings.md`. The story tickets keep only the ticket skill's short `QA: N of M` count line.

## Step 1: Read the Plan and Its Results

1. Resolve the spec folder per `../references/spec-files.md`.
2. Require `qa-plan.md`. If missing, run `git worktree list`, report any sibling worktree that may hold it, direct the user to `$vorbit-qa-plan`, and stop.
3. Collect manual results: ticked boxes, unticked boxes, and `**Fail:**` notes, per section.
4. Set the run picture folder: `<spec folder>/qa-screenshots/<YYYY-MM-DD>/`, one folder per run date, so an earlier run's pictures are never overwritten. Create it the first time this run saves a picture.
5. If unticked manual checks remain and a browser-automation capability exists, the agent runs them itself by default (Step 2.5) — the single Step 2 approval covers it; no extra question. Hand-testing is only for what the agent honestly cannot do: those checks come back marked `needs human`. Ask the user to choose (test by hand now, or `not tested` in the report) only when no browser capability exists or the app is unreachable.

## Step 2: Run the Automated Checks (optional, approved once)

Only when the plan has an `Automated checks` section:

1. List the `QP#` commands and ask once for approval to run the whole plan — this one approval covers both the commands here and the browser checks in Step 2.5. If the user declines, the report uses the boxes as they stand, marked `not run this time`.
2. Run each command exactly as the plan stores it. The tool does not matter — Playwright, Cypress, Maestro, or any open-source runner works the same because the plan stores the command, not the tool.
3. Judge each run by exit status plus the runner's own summary line; quote failing test names in plain words. When a Playwright HTML/JSON results file exists, use it for the failing-test details.
4. Copy the runner's own screenshots into the run picture folder before reporting. Playwright writes a failure shot under `test-results/.../test-failed-1.png` and wipes that folder on the next run, so a copy is the only version the report can keep. Name each copy `<QP#>-<short-label>.png`.
5. Update `qa-plan.md` to match reality: tick a `QP#` box on pass; on fail, untick it and add the `**Fail:**` note line. Touch nothing else in the plan file.
6. A command that cannot run (missing dependency, no browser, no environment) is recorded as `blocked: [reason]` — never guessed as pass or fail.

## Step 2.5: Agent-Run Manual Checks (default when possible)

Runs by default when the runtime has a browser-automation capability (for example Playwright MCP tools or a connected browser) and the Step 2 approval was given — no second question:

1. Confirm the test environment from the plan header (URL, test account) and that the app is reachable. If not, ask or fall back to `not tested`.
2. Sign in with the test account from the plan header only, never the user's real account.
3. For each unticked manual check, in plan order: perform the action exactly as written, then compare what actually appears against the check's `You should see:` text.
4. **Take a screenshot of every check, pass or fail**, right after the action and before moving to the next check. Save it in the run picture folder as `<check-id>-<short-label>.png`, lowercase with dashes, for example `qa3-empty-email.png`.
   - On a fail, frame the shot so the wrong result is visible, not just the page.
   - When a console error is what fails the check, save the console panel too as `<check-id>-console.png`.
   - Scroll past or hide test data that looks private before the shot.
5. After each check, read the browser console (the browser's hidden error list). Any new error there fails the check even when the screen looks right — quote the error in the `**Fail:**` note.
6. Record honestly, using the same rules a human tester follows:
   - matches → tick the box
   - differs → leave unchecked and add `**Fail:** [what actually appeared] ([date])`
   - cannot truly perform it (real phone in hand, camera, printed output, a browser the tool cannot open) → add `needs human: [reason]` under the check and leave it unchecked
7. Device-matrix rows may be run with an emulated screen size; then note `(emulated)` on that check — an emulated phone is not a real phone.
8. **Never tick a check the agent did not actually observe.** No screenshot or page state seen = not tested.
9. **Never write an image line for a picture that was not taken.** A check with no picture gets `_no picture: [reason]_` in the report instead. Checks a human ran by hand, and every check in a run with no browser capability, always use that line.

## Step 2.7: Suggest a Modern Fix for Every Fail

Every failed check carries a suggested fix. This skill suggests only. It never edits code.

1. Detect the stack once per run: React or Next.js when `package.json` lists `react` or `next`.
2. **React or Next project: load the `react-best-practices` skill before writing a single suggestion.** This is required, not optional. Load `ui-patterns` alongside it whenever the fail is about a screen, a form, a list, or accessibility — `react-best-practices` asks for that pairing itself. A suggestion written without loading them does not go in the report.
3. Any other stack: follow the patterns already used in this repository. Read a nearby file that solves the same problem and match it.
4. Never suggest a fix that adds a new dependency, and never name a library the project does not already have.
5. Locate the code before suggesting: check `epic.md` for the task that built the failing screen, then search the repository for that screen or component name. When the file is still unclear, describe the change in plain words and mark the file `not located`. Never guess a path.
6. Write one `**Suggested fix:**` line per fail, holding three things: what to change in plain words, the file path when located, and the named pattern it follows so a developer can check the source.
7. Two sentences maximum. The real fix belongs to `$vorbit-implement`, not to this report.
8. No suggestion for a check the agent did not actually run. A guess dressed as a fix is worse than an empty line.

## Step 3: Write the Report

1. Run the write guards per `../references/spec-files.md`. Tag every fail `from this branch` or `pre-existing` per `../references/pre-existing-findings.md` Step 1. A pre-existing fail keeps its `**Fail:**` note in `qa-plan.md` with the prefix `pre-existing:`.
2. Write `qa-report.md` in the spec folder. Newest run goes **on top**; earlier run sections stay untouched below. Never rewrite an old run.
3. Every line is plain language for a non-technical reader. Name checks by ID plus a short human phrase, not by test-file paths.
4. Put each check's picture directly under its line, as a relative path from the report file: `![QA3](qa-screenshots/2026-09-16/qa3-empty-email.png)`. Never use an absolute path — the picture stops showing the moment the folder moves.
5. Fails show their pictures open. Passed checks keep theirs inside one collapsed block, so the reader sees the problems first and the proof stays one click away.
6. Every fail line carries its `**Suggested fix:**` line from Step 2.7, directly under the picture.

### Report schema (one run section)

```markdown
# QA Report: [Feature Name]

## Run [YYYY-MM-DD]

**Branch:** [branch] | **Environment:** [where tested] | **Devices:** [what was actually used]
**Run by:** [human | agent (browser) | mixed]
**Verdict: READY** — all checks passed
(or) **Verdict: NOT READY** — [N] checks failed, [M] not tested

### Per story
- US-001 [Story title]: 5 of 6 passed — 1 fail
- US-002 [Story title]: all 4 passed

### Failed checks
- QA3: Submit with empty email — expected "Email required", the form submitted with no error
  ![QA3](qa-screenshots/2026-09-16/qa3-empty-email.png)
  **Suggested fix:** Block the submit until the email field is filled, and show the error text from the form's own state, in `app/signup/SignupForm.tsx`. Pattern: ui-patterns, form validation and error text.
- QP1: login E2E run — 2 of 14 tests failed (wrong redirect after login, missing error text)
  ![QP1](qa-screenshots/2026-09-16/qp1-login-redirect.png)
  **Suggested fix:** Start the session request and the profile request together instead of one after the other, in `app/login/actions.ts`. Pattern: react-best-practices, Eliminating Waterfalls.

### Passed checks

<details>
<summary>12 passed. Open this to see the pictures.</summary>

- QA1: Log in with a good email and password
  ![QA1](qa-screenshots/2026-09-16/qa1-login-ok.png)
- QA2: Log out from the account menu
  ![QA2](qa-screenshots/2026-09-16/qa2-logout.png)
- QA4: Tested by hand
  _no picture: run by hand_

</details>

### Pre-existing (follow-up)
- QA5: Profile photo upload shows no progress bar. Evidence: `ProfilePhoto.tsx` untouched on this branch, last changed in commit a1b2c3d on main. Linear: nothing found. Slack: #design, 2 Sep, "photo upload feels frozen".
  ![QA5](qa-screenshots/2026-09-16/qa5-photo-upload.png)
  **Suggested fix:** Show upload progress from the upload's own state, in `ProfilePhoto.tsx`. Pattern: ui-patterns, loading and progress feedback.
(omit this section when there are none)

### Automated run
- QP1: `npx playwright test e2e/login.spec.ts` → 12 passed, 2 failed
- QP2: not run this time (user skipped)
- Full technical detail: `playwright-report/index.html` (include this line only when the runner produced a report; use the runner's actual output path)

### Not tested
- QA7, QA8 (device matrix rows for Safari — no Safari available this run)
- QA9 (needs human: real phone in hand)

---
```

**Verdict rule:** `READY` only when every check in the plan is ticked or tagged pre-existing. Any branch-caused fail, block, or untested check = `NOT READY`, with the reason listed. Never soften a fail, and never re-tag a fail as pre-existing to reach `READY`.

## Step 4: Report in the Session

- Verdict, one line
- File path
- Fails in plain words (max 5; if more, count them and name the worst), each with its suggested fix in one short line
- Pre-existing fails, each with its Linear and Slack line, then the one batched ticket question per `../references/pre-existing-findings.md` Step 4
- Picture folder path, so the user can open the shots directly
- Reminder: the report is local and gitignored — copy the run section out to share it, and copy the `qa-screenshots/` folder with it or the pictures stop showing
- Next steps:
  - fix fails via `$vorbit-implement`, then re-run this skill
  - `$vorbit-ticket` refreshes only the short `QA: N of M` count on the story tickets — report details never go to Linear
