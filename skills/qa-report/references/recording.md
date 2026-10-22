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

- Inspect the browser tool's actual recording capability before starting. Browser access or screenshot support does not imply video support. If it cannot record, use an available Playwright runner with the existing test setup for the same flow. If neither can record, the flow is `Not done: no recording`; keep the observation. An observed failure stays Failed even if recording fails.
- **One clip per flow**, named `<check-id>-<flow-name>.webm`. Never one long clip for several flows with time ranges. A popup or new tab that holds the tested result gets its own clip named `<check-id>-popup.webm`.
- **Make the clip readable:**
  1. Reuse the project's narrated QA video mode when it has one (the regression scan reports a QA-mode suite; look for a title-card and action-label helper in its fixtures). It already does the next three items.
  2. Else open with a title card for 2 seconds: the check ID, the flow name, and the `You should see:` text.
  3. Label every click, fill, and navigation for about 1 second, and slow actions to about 500 ms (Playwright `slowMo`). Use the installed Playwright's screencast chapter and action-label API when it has one; else draw a small overlay in the page.
  4. Hold the end result on screen for 2 seconds. On a fail, show "Expected: … / Saw: …" for 3 seconds before closing.
- For a Playwright session the agent owns, create the browser context with `recordVideo: { dir: <run evidence folder> }` **before** opening pages. Keep a reference to each page's `video()`. In `finally`, await the owned context's `close()` so videos finish writing even if an assertion fails, then save each video under its check ID with `video.saveAs(...)`. Do not close an unrelated user session. Recording cannot be added after the actions happened.
- Check that the saved files exist, are nonempty, and are playable when playback is available. Watch the result segment before claiming it proves the flow. Never turn screenshots into a fabricated screen recording.
- Use test accounts and safe data throughout, including setup. Do not record passwords being typed, tokens, or private customer data; hide typed secrets with the project's label-hiding helper when it has one. Sign in per `sign-in.md`, which reuses the project's authenticated test setup.

## Attach to the report

Use relative Markdown links labelled **Watch**, one per clip, with the browser when it matters. No time ranges. Keep screenshots under For developers. For Notion, upload the actual video file and embed a video block as described in `notion-report.md`; a local file path is not a shared attachment.

If saving or uploading fails, report the gap and retain the local evidence. Never invent an attachment URL or mark publication complete with broken links. API-only checks may use the runner result only after inspecting the exact test and fixtures and confirming no page is opened.

Playwright references: [recording and context closure](https://playwright.dev/docs/videos), [video saving](https://playwright.dev/docs/api/class-video), [test configuration](https://playwright.dev/docs/test-configuration).
