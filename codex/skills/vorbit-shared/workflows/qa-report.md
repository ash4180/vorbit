<!-- GENERATED from skills/qa-report/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# QA Report Skill

Run the QA plan and turn the results into a dated, forwardable report: what passed, what failed, and whether the feature is ready. Testing and reporting happen in one run — the skill executes the automated commands, can click through manual checks in a real browser, and then writes the report. The report is a plain-language file a stakeholder can read without opening the app or the plan.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/spec-files.md` for spec path resolution, write guards, and file ownership before any spec read or write.

This skill never writes to Linear. The story tickets keep only linear-sync's short `QA: N of M` count line.

## Step 1: Read the Plan and Its Results

1. Resolve the spec folder per `../references/spec-files.md`.
2. Require `qa-plan.md`. If missing, run `git worktree list`, report any sibling worktree that may hold it, direct the user to `$vorbit-qa-plan`, and stop.
3. Collect manual results: ticked boxes, unticked boxes, and `**Fail:**` notes, per section.
4. If unticked manual checks remain and a browser-automation capability exists, the agent runs them itself by default (Step 2.5) — the single Step 2 approval covers it; no extra question. Hand-testing is only for what the agent honestly cannot do: those checks come back marked `needs human`. Ask the user to choose (test by hand now, or `not tested` in the report) only when no browser capability exists or the app is unreachable.

## Step 2: Run the Automated Checks (optional, approved once)

Only when the plan has an `Automated checks` section:

1. List the `QP#` commands and ask once for approval to run the whole plan — this one approval covers both the commands here and the browser checks in Step 2.5. If the user declines, the report uses the boxes as they stand, marked `not run this time`.
2. Run each command exactly as the plan stores it. The tool does not matter — Playwright, Cypress, Maestro, or any open-source runner works the same because the plan stores the command, not the tool.
3. Judge each run by exit status plus the runner's own summary line; quote failing test names in plain words. When a Playwright HTML/JSON results file exists, use it for the failing-test details.
4. Update `qa-plan.md` to match reality: tick a `QP#` box on pass; on fail, untick it and add the `**Fail:**` note line. Touch nothing else in the plan file.
5. A command that cannot run (missing dependency, no browser, no environment) is recorded as `blocked: [reason]` — never guessed as pass or fail.

## Step 2.5: Agent-Run Manual Checks (default when possible)

Runs by default when the runtime has a browser-automation capability (for example Playwright MCP tools or a connected browser) and the Step 2 approval was given — no second question:

1. Confirm the test environment from the plan header (URL, test account) and that the app is reachable. If not, ask or fall back to `not tested`.
2. For each unticked manual check, in plan order: perform the action exactly as written, then compare what actually appears against the check's `You should see:` text.
3. Record honestly, using the same rules a human tester follows:
   - matches → tick the box
   - differs → leave unchecked and add `**Fail:** [what actually appeared] ([date])`
   - cannot truly perform it (real phone in hand, camera, printed output, a browser the tool cannot open) → add `needs human: [reason]` under the check and leave it unchecked
4. Device-matrix rows may be run with an emulated screen size; then note `(emulated)` on that check — an emulated phone is not a real phone.
5. **Never tick a check the agent did not actually observe.** No screenshot or page state seen = not tested.

## Step 3: Write the Report

1. Run the write guards per `../references/spec-files.md`.
2. Write `qa-report.md` in the spec folder. Newest run goes **on top**; earlier run sections stay untouched below. Never rewrite an old run.
3. Every line is plain language for a non-technical reader. Name checks by ID plus a short human phrase, not by test-file paths.

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
- QP1: login E2E run — 2 of 14 tests failed (wrong redirect after login, missing error text)

### Automated run
- QP1: `npx playwright test e2e/login.spec.ts` → 12 passed, 2 failed
- QP2: not run this time (user skipped)

### Not tested
- QA7, QA8 (device matrix rows for Safari — no Safari available this run)
- QA9 (needs human: real phone in hand)

---
```

**Verdict rule:** `READY` only when every check in the plan is ticked. Any fail, block, or untested check = `NOT READY`, with the reason listed. Never soften a fail.

## Step 4: Report in the Session

- Verdict, one line
- File path
- Fails in plain words (max 5; if more, count them and name the worst)
- Reminder: the report is local and gitignored — copy the run section out to share it
- Next steps:
  - fix fails via `$vorbit-implement`, then re-run this skill
  - `$vorbit-linear-sync` refreshes only the short `QA: N of M` count on the story tickets — report details never go to Linear
