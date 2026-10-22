---
name: qa-report
description: Run the branch QA plan flow by flow and write a short, dated report a non-technical reader can act on. One table, flow first, each problem in its flow's row, with a narrated recording per flow. Three results only (Passed, Failed, Not done); developer detail stays in a folded section. Checks test data before running, creates missing records on the local app or DEV and deletes them after, never fakes the server unless asked, and never re-runs the suite on the base code. When requested, publishes the report to a named Notion hub. Requires qa-plan.md; use qa-plan to author it and implement to fix code.
---

# QA Report Skill

Run the plan's flows and show what works, what is broken, and what no one could test yet. Readers are not developers: the report reads top to bottom, with no jumping between tables. A pass needs a recording of the whole flow. Code review, unit tests, and a screenshot do not prove a flow.

Read and follow `../_shared/execution-contract.md` before starting.

Read `../_shared/spec-files.md` for spec path resolution, write guards, and file ownership before any spec read or write.

Read `../_shared/pre-existing-findings.md` for how to tag, report, and follow up problems this branch did not cause.

This skill writes to Linear only for a follow-up ticket the user approves per `pre-existing-findings.md`, and for the `QA report` link Step 3.5 adds. QA results never go into ticket descriptions.

**Browser execution belongs to a subagent.** For an authorized test run, read `references/flow-runner.md` before browser work. Step 1 may inspect test prerequisites; Step 2 runs automated commands. Step 2.5 requires a native Sonnet/Luna subagent, a returned agent ID, and the prepare/resume handoff before any flow starts. Saying "delegated" is not proof of a launch. Do not silently run flows in the parent or start a separate CLI session. Report-only runs do not launch a runner; an explicit caller override is recorded.

## Step 1: Read the Plan and Check What It Needs

1. Resolve the spec folder per `../_shared/spec-files.md`.
2. Require `qa-plan.md`. If missing, run `git worktree list`, report any sibling worktree that may hold it, direct the user to `/vorbit:implement:qa-plan`, and stop.
3. Read earlier results and their dates. An old result is not a pass for this run. Keep earlier reports intact and rerun every flow in scope.
4. After the spec write guards, create a unique run evidence folder: `<spec folder>/qa-screenshots/<YYYY-MM-DD>/<HHMMSS>/`. If it exists, add a numeric suffix; never reuse it. Clips, screenshots, JSON results, and manifests live here.
5. **Check every `Needs:` line before running anything.** Sign in with each account per `references/sign-in.md`, open each workspace, and confirm each record exists. On the local app or DEV, create missing records per `references/test-data.md`. A need that still cannot be met is `Not done: need [X]`, in one line. Do not fake server answers or build a harness to work around a missing need. Attended run: ask once, batched, for every remaining missing need before the first flow. Unattended run: record the gap and run the flows that can run.
   - A `UI-only run` is allowed only when the user asks for it by that name. Faked server answers then keep the flow `Not done: server faked, page looked right`, never Passed.
6. Separate flows the agent can run from flows marked `Needs human` (judgment, real device, camera, print, sign-off). Those stay `Not done: needs a person`. Missing access is `Not done: need [access]`.
7. A request to run QA, including QA alongside review, authorizes the plan's commands and browser flows; do not ask again. If only a report was requested, ask once before running. An unattended report-only run uses existing results and records gaps. Honor `--skip-automated` without inferring that skipped commands passed.

## Step 2: Run the Automated Checks

Only when the plan has an `Automated checks` section:

1. Run the `QP#` commands in plan order. Each is a spec file for a changed screen, or the full suite when the plan is a release plan. Never add the full suite yourself.
2. Read `references/recording.md` before any run. Reuse the project's QA video mode when it keeps a video of every test, passed or failed; `retain-on-failure` does not.
3. A temporary config is allowed on DEV when a command needs one, for example to stop error reports from reaching the on-call. It must not change what the tests see: reuse the project's own helper (one that answers the blocked call with an empty OK). Never point a host at a dead address; that logs console errors and fails every test that must stay clean. Remove the config after the run and record it under For developers.
4. Capture exit status and the runner's summary. A zero exit code alone is not a pass: skipped tests, an empty suite, retries, and runner errors stay visible.
5. Collect every test's proof **right after each command**, before the next one runs: Playwright wipes `test-results/` at the start of every run.
   - **Playwright:** run `python3 scripts/collect_e2e_evidence.py --report <JSON file> --dest <run evidence folder> --check <QP#>`. It copies all attempts and writes a manifest with one entry per test (`QP1-1`, `QP1-2`, …). Use `qa_status`, not `status`, for results: `passed` → Passed; `failed` → Failed; `flaky`, `not_tested`, `needs_evidence` → Not done with that reason. Exclude `setup` entries from counts, but keep setup failures as run blockers.
   - A test without video is not automatically API-only. Inspect that test and its fixtures; only if it opens no page, rerun the collector with `--api-only <test-id>` and note the inspected assertion under For developers.
   - **Other runners:** copy every test's videos and screenshots to the run folder and apply the same rules.
6. Tick a `QP#` only when the command succeeded, at least one non-setup test ran, every test has `qa_status: passed`, and no setup or runner error remains. Otherwise leave it unchecked with the reason. A `Covers:` mapping never ticks a flow by itself: the flow needs its own recording.
7. A command that cannot run is `Not done: [reason]`, never guessed.
8. **Never run the suite on the base-branch code** to sort out failures. Tag unrelated failures per `pre-existing-findings.md` (blame, base-branch file, or the project's scheduled suite result). Failures that stay unsure are listed under For developers as `unresolved`, and the command stays Failed.

## Step 2.5: Run the Flows in the Browser

Run every eligible flow when Step 1 authorizes testing, even when the plan has no automated commands. Follow `references/flow-runner.md`: prepare one native Claude Sonnet or Codex Luna (`gpt-6-luna`) subagent in the same worktree, save its returned ID and model selection in `runner-session.json`, then resume that same agent to execute. If launch, model selection, or resume is unavailable, affected flows are `Not done` with the reason. The subagent follows the flow rules below and returns evidence; the parent reviews it before Steps 2.6–4 and alone updates the plan and report. An assigned runner never delegates again. Report-only runs do not launch a runner.

### Flow rules (also apply inside the child)

1. Confirm the environment from the plan header and that the app is reachable. If not, every browser flow is `Not done: need [X]`.
2. Sign in per `references/sign-in.md`, with the plan's test accounts only, never the user's real account.
3. For each flow, in plan order: start the recording **before** the first step, per `references/recording.md` (title card, labelled actions, slow motion, one clip per flow). Do every step with the stated data. Compare each `You should see:` line with what appears.
4. Save the clip as `<check-id>-<flow-name>.webm` and a screenshot of the end result as `<check-id>-<flow-name>.png`. On a fail, frame the wrong result. When a console error is the fail, also save `<check-id>-console.png`. Use safe test data from the start; a hidden value in the screenshot is still in the clip.
5. After each flow, read the browser console. A new error fails the flow even when the screen looks right; quote it under For developers.
6. One result per flow, one of three:
   - `Passed`: every `You should see:` matched and the clip is saved.
   - `Failed`: a step differed. Note the step and what appeared, in the words a user would use. A flow with several wrong things is one Failed flow listing each problem.
   - `Not done`: with a short reason: `need [X]`, `needs a person`, `no recording` (keep the observation, rerun with recording), or `not reached` (an earlier step failed).
7. An emulated viewport is labelled `(emulated)`. It does not clear a real-device need or another browser's matrix cell.
8. Never replace a run with reading code, an idle screenshot, or an unrelated green suite. A safe result that differs from the plan is Failed with the note `plan may need rewording`.
9. A human result is `Passed (person: name, date, where)`; never claim the agent saw it. Never invent a recording, tester, or confirmation.

## Step 2.6: API Speed

Only when the plan has an API speed check with a limit and a PROD address. Then read `references/api-performance.md` and follow it. Otherwise skip this step; the plan's Open items line already says what is missing. Keep measurements in the evidence folder and show the DEV vs PROD table only under For developers.

## Step 2.7: Suggest a Fix for Every Failed Flow

Every problem from this branch gets a suggested fix. This skill suggests only; it never edits code. Suggestions appear only under For developers.

1. Detect the stack once per run: React or Next.js when `package.json` lists `react` or `next`.
2. React or Next project: load the `react-best-practices` skill, plus `ui-patterns` when the problem is a screen, form, list, or accessibility, so each fix names a pattern from those guides.
3. Other stacks: match a nearby file in this repository that solves the same problem.
4. Never suggest a new dependency or a library the project does not have.
5. Locate the code first: `epic.md` task, then a repository search for the screen or component. When unclear, describe the change in plain words and mark the file `not located`. Never guess a path.
6. One `Suggested fix:` line per problem: what to change, the file when located, and the pattern it follows.
7. The real fix belongs to `/vorbit:implement:implement`. No suggestion for a flow the agent did not run.

## Step 2.8: Delete Test Data

When this run created records, delete them per `references/test-data.md` before writing the report. Leftovers go under For developers and in Step 4.

## Step 3: Write the Report

1. Run the write guards per `../_shared/spec-files.md`. Tag every problem `from this branch` or `pre-existing` per `../_shared/pre-existing-findings.md` Step 1.
2. Write `qa-report.md` in the spec folder. Newest run on top; earlier runs stay untouched below.
3. **One table, flow first.** Every plan flow gets one row, in plan order: flow name, result, and its problems or reason in the same row. The reader never jumps between tables to match a problem to its flow.
4. **Three results only** in the human part: `Passed`, `Failed`, `Not done`. Every other label (flaky, blocked, needs decision, missing recording, PROD verified) becomes a short reason inside the row or goes under For developers.
5. **No code words in the human part.** No file paths, test file names, ports, localhost, commit hashes, console error text, API or function names, load averages, or tool names. Say what the user saw.
6. Each problem appears once in the human part, in its flow's row, with a `Watch` link. Suggested fixes, commands, raw runner totals, per-test inventories, old-bug tables, timing tables, and manifests go under `For developers`.
7. Pre-existing problems: one line in the human part (count and flow names). The table with evidence and the Linear and Slack lines goes under For developers.
8. Flows that are Not done for the same reason are summarised in the verdict line; their rows stay in the table.
9. Count flows once. Each `QP#` command is one row; its tests are listed under For developers.

### Report schema (one run section)

```markdown
# QA Report: [Feature], PR #[number]

## Run [YYYY-MM-DD HH:MM], took [h min]

**Not ready.** [N] problems found. [M] flows could not be tested: [one reason].
(or) **Ready.** Every flow passed.

| Flow | Result | Problems or reason |
|---|---|---|
| Who can see the Billing page | Passed | real accounts, [Watch](qa-screenshots/2026-10-16/172402/qa1-who-can-see.webm) |
| Upgrade from Free, saved card | Failed | After "Pay": a normal card shows "Confirm with your bank" for a few seconds. [Watch](qa-screenshots/2026-10-16/172402/qa4-upgrade-saved-card.webm) |
| Parts that could not be read | Failed | 1. Page says "No card on file" while the card lookup failed. [Watch](...) 2. Dialog still offers "Add a card". [Watch](...) |
| Buy extra gems | Not done | need a workspace billed in gems |
| Korean wording | Not done | needs a person who reads Korean |
| Other screens still work | Passed | 8 of 8, [Watch](qa-screenshots/2026-10-16/172402/qr1-other-screens.webm) |
| Automated tests, changed screens | Passed | 14 of 14 |

Old problems not caused by this branch: [count], in [flow names]. See For developers.

### What a person must do next

1. Developer: fix the [N] problems. Details under For developers.
2. Tester: [provide X], then re-run the [M] Not done flows.
3. [Designer or product]: [the human-only checks].

<details>
<summary>For developers</summary>

- Tested: [branch], [revision, local changes yes or no], [environment], [browser, emulation label], [accounts], [run by]
- One block per problem: expected, actual, screenshot, tag, console text when relevant, `Suggested fix:` (Step 2.7)
- Automated runs: command, exit code, raw totals, manifest link, one line per test with its recording, unresolved failures
- Pre-existing table: what, where, evidence it predates the branch, Linear and Slack lines
- API speed table when measured, temporary configs used, data created and deleted

</details>

---
```

**Verdict rule:** `Ready` only when every flow is `Passed` with a current recording or a named human result, except flows whose only problems are confirmed pre-existing. Any `Failed` or `Not done` flow means `Not ready`. Never re-tag a problem as pre-existing to reach Ready. A report-only run states whether its old results cover the current revision.

### Write results back to the plan

Under each check in `qa-plan.md`, add or replace one line: `Result: Passed | Failed | Not done (reason), YYYY-MM-DD, [agent | person name], [Watch](link)`. Nothing else goes into the plan; detail lives in the report. Do not change check wording or IDs. Update the header's `Updated:` line.

## Step 3.5: Publish to Notion (only when the caller names a hub)

When the caller names a Notion report hub, read `references/notion-report.md` and follow it after the local report is written. Without a named hub, skip this step and mention in Step 4 that the report can be published to Notion.

## Step 4: Report in the Session

- Verdict, one line
- File path, and the Notion page URL when Step 3.5 ran
- Problems in plain words (max 5; if more, count them and name the worst)
- Flows Not done, grouped by reason, with who can unblock each
- Pre-existing problems, each with its Linear and Slack line, then the one batched ticket question per `../_shared/pre-existing-findings.md` Step 4
- Evidence folder path and links to the recordings of failed flows
- Test data created, and any record that could not be deleted
- Reminder: the report is local and gitignored. Share it with its `qa-screenshots/` folder, or publish to the named Notion hub.
- Next steps:
  - fix problems via `/vorbit:implement:implement`, then re-run this skill
  - report details never go into Linear ticket descriptions; publish to a Notion hub to share them
