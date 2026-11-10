# Record browser checks and keep the evidence

Read before running automated browser tests or agent browser checks. Every browser check needs a recording from before its first action through its observed result, for passes and failures. A screenshot or trace is supporting evidence, not the recording.

## Playwright Test

1. Read the installed Playwright version, existing config, project overrides, and fixtures. Reuse the project's QA command when it actually keeps every video. `video: 'on'` records successful tests too; `retain-on-failure` and `on-first-retry` do not meet this requirement.
2. If the project has no recording mode, use a temporary config beside the existing config so its relative paths retain their meaning. Import that config, preserve its settings, and override video at both the default and project level. Example (adapt the import to the actual config):

   ```ts
   import { defineConfig } from '@playwright/test';
   import base from './playwright.config';

   export default defineConfig(base, {
     use: { ...base.use, video: 'on' },
     projects: base.projects?.map(project => ({
       ...project,
       use: { ...project.use, video: 'on' },
     })),
   });
   ```

   Pass it with the runner's `--config` option. Preserve the plan's test selection and environment. Do not rewrite the tracked project config. A fixture or test that creates its own context needs `recordVideo` on that context; a config override cannot guarantee that. Do not change application code or assertions just to obtain a pass.
3. Request JSON alongside the existing human-readable reporters. For a plain command, use `--reporter=list,json`; preserve required custom reporters when present. Set `PLAYWRIGHT_JSON_OUTPUT_NAME` to an absolute path inside this run's evidence folder, for that command only. Use the package manager's actual argument-forwarding syntax; record the effective command. Video is a config option, not an invented `--video` CLI flag.
4. Run commands sequentially. Immediately after each command, collect its attachments with `scripts/collect_e2e_evidence.py`; the next Playwright run can erase `test-results/`. Keep failed attempts and retries, labeling each. Copy any HTML report you link to into the run folder with its assets before another run replaces it.
5. Remove only the temporary config this run created, including on failure. Keep its settings and effective command in the run's technical details. Never delete an existing config or another run's evidence.

## Agent browser flows

A clip must be readable by a person who was not there. A fast, unlabelled clip proves nothing to them.

- **Use the project's Playwright setup when it has one.** Then each flow runs as a flow test (next section). It reuses the project's sign-in setup, saved logins, app address, and QA video mode, so the runner rebuilds none of them. Never write a separate browser script that redoes what the project's setup already does. Drive a browser tool step by step only when the project has no Playwright setup, looking at the screen before each action.
- Inspect the browser tool's actual recording capability before starting. Browser access or screenshot support does not imply video support. If it cannot record, use an available Playwright runner with the existing test setup for the same flow. If neither can record, the flow is `Not done: no recording`; keep the observation. An observed failure stays Failed even if recording fails.
- **One clip per flow**, named `<check-id>-<flow-name>.webm`. Never one long clip for several flows with time ranges. The review recording is joined from these clips after the run. See `review-recording.md`. It never replaces them. A popup or new tab that holds the tested result gets its own clip named `<check-id>-popup.webm`.
- **Make the clip readable:**
  1. Reuse the project's narrated QA video mode when it has one (the regression scan reports a QA-mode suite; look for a title-card and action-label helper in its fixtures). It already does the next three items.
  2. Else open with a title card for 2 seconds: the check ID, the flow name, and the `You should see:` text.
  3. Label every click, fill, and navigation for about 1 second, and slow actions to about 500 ms (Playwright `slowMo`). Use the installed Playwright's screencast chapter and action-label API when it has one; else draw a small overlay in the page.
  4. Hold the end result on screen for 2 seconds. On a fail, show "Expected: … / Saw: …" for 3 seconds before closing.
- For a Playwright session the agent owns, create the browser context with `recordVideo: { dir: <run evidence folder> }` **before** opening pages. Keep a reference to each page's `video()`. In `finally`, await the owned context's `close()` so videos finish writing even if an assertion fails, then save each video under its check ID with `video.saveAs(...)`. Do not close an unrelated user session. Recording cannot be added after the actions happened.
- Check that the saved files exist, are nonempty, and are playable when playback is available. Watch the result segment before claiming it proves the flow. Never turn screenshots into a fabricated screen recording.
- Use test accounts and safe data throughout, including setup. Do not record passwords being typed, tokens, or private customer data; hide typed secrets with the project's label-hiding helper when it has one. Sign in per `sign-in.md`, which reuses the project's authenticated test setup.

## Flow tests

A flow test is a temporary Playwright test for one plan flow. The parent (Fable or Astra) writes it in Step 2.4, by reading only: choosing what to check is planning work. The parent never runs a test, the app, or a browser. Every run belongs to the runner (Sonnet or Luna). The test does the steps and records them. The plan's words decide the result.

**Write (parent)**

1. **Where:** one file per flow in the project's E2E test folder, named `qa-<check-id>-<flow-name>.spec.ts`. Add the file-name ending the project uses to pick an account, for example `.member.spec.ts`. Import `test` and `expect` the way the project's other tests do, often from a shared fixtures file, so its QA video, sign-in, and lint rules apply. Never change the project's existing tests, fixtures, or config.
2. **Learn the screen first:** read the screen's code and one existing test of a nearby screen. Search first, then read only the lines you need; never print a whole long file or a generated type file. Every later action carries what was read, so reading less keeps each action cheap. Find elements the way a user sees them: role and visible text (for example `getByRole('tab', { name: 'Discussions' })`), then field labels, then test IDs the project already uses. Never use a label you did not read in the code or see on the screen.
3. **Steps:** one `test.step` per plan step, named with the step number and the plan's words. Assert what a test can check: text, a count, the address, focus, a control turned on or off, what stays after a reload. Where only looking can tell (a fade, overlap, alignment, a theme), save a screenshot at that step; the runner judges it from the screenshot and the clip.
4. **Test data:** the test creates its flow's setup records with the project's API helpers or a fixture, for example one that creates a record and deletes it after the test. Use the recorded screens only when creating the record is the tested flow. Log each record per `test-data.md` right after it exists. Delete it when the test ends, pass or fail, and mark it deleted in the log. A record the app cannot delete gets the cleanup `test-data.md` names instead.
5. **Check:** when a second strong model is available (Fable for an Astra test, or Astra for a Fable test), it reads each test against the plan and the screen's code. It opens each line in the handoff's `sources` first and reads more code only where one looks wrong. It checks that the test does every step, checks every `You should see:` result or saves its screenshot, finds elements by labels that exist, makes and deletes its own records, and expects nothing less than the plan says. Its notes are at most 5 problems, one line each. The writer fixes what it finds, once.
6. **Hand over each flow as soon as its test is ready,** so the runner can start it while other tests are still being written: write `flow-tests/<check-id>.json` in the run folder with `{"file": "…", "command": "…", "sources": {"label": "file:line"}}`. `sources` names the code line each label, role, or class came from. The command is the exact QA-mode run of that one file. Write `{"not_done": "reason"}` only for a flow no test can do at all, or `{"browser": true}` when the project has no Playwright setup. **One step a test cannot do never drops the flow.** Examples: a native dialog, or a record no account can create. The test does every other step and checks every other result, and the handoff adds `"skipped_steps": {"8": "reason"}`. The runner's row is then `Not done: step 8 [reason]` when every other step matched, and Failed when any did not. Copy the test into `flow-tests/`, and leave it in the project's test folder for the runner.

**Run (runner)**

7. First load the test without running it (Playwright's `--list`): a load error is a test bug, reported at once. Then run each flow's command from its handoff, for example `yarn e2e:qa e2e/tests/qa-QA1-post-comment.spec.ts --project=chromium-authenticated --workers=1 --reporter=list,json`. The project's setup signs in and renews an old saved login. Right after each run, collect the evidence with Step 2's collector and `--check <check-id>`. A `not_done` handoff keeps its reason.
8. **Test bug:** never write or edit a flow test. A test that stops on an element it cannot find, a wait that is too short, or its own wrong check has no flow result. Give the parent the error and the page snapshot Playwright saved. The parent fixes the test by reading the error, the snapshot, and the screen's code, never by running it. A fix may change how the test finds and waits for things, never what it expects. Then the runner runs it again; that run is not one of the flow's two tries under Flow rule 10. After 2 fixes, the flow is `Not done: flow test could not run ([last error])`. When the screen really lacks or contradicts what the plan names, the flow is Failed, not a test bug.

**After (parent)**

9. Step 2.8 deletes each flow test from the project's test folder. Never commit it. The report lists the copies under For developers as tests a developer may add.

## Attach to the report

Use relative Markdown links labelled **Watch**, one per clip, with the browser when it matters. No time ranges. Keep screenshots under For developers. For Notion, upload the actual video file and embed a video block as described in `notion-report.md`; a local file path is not a shared attachment.

If saving or uploading fails, report the gap and retain the local evidence. Never invent an attachment URL or mark publication complete with broken links. API-only checks may use the runner result only after inspecting the exact test and fixtures and confirming no page is opened.

Playwright references: [recording and context closure](https://playwright.dev/docs/videos), [video saving](https://playwright.dev/docs/api/class-video), [test configuration](https://playwright.dev/docs/test-configuration).
