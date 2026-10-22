# Publish the QA Report to Notion

Load this file only when the caller named a Notion report hub. The local `qa-report.md` stays the full record; the Notion page is the copy people read.

## Inputs

- **Hub:** the Notion database the caller named (a URL or `collection://` ID).
- **Template:** the hub template the caller named. Default: the template called `QAT Report`.
- **Linear tickets:** the tickets this run covers, from the PR or the caller.

## What the template holds

The template already contains the whole layout, so never build the layout yourself:

- a 💡 Summary callout and a 🧪 Test details callout, with `[placeholder]` text
- chart views (by section, by result) and two lists (`Needs you`, `Problems found`)
- an inline `Flows` database. Every chart and list reads this database, so the page fills itself once the rows exist.

`Flows` columns: `Flow` (title), `Result`, `Section`, `Finding`, `Video`.

## Result values

Map every check in this run to exactly one `Result`:

| Result | When |
|---|---|
| Passed | complete expected result verified with a saved browser recording, a confirmed API-only pass, a documented PROD speed resolution per `api-performance.md`, or an explicit human result with tester/date/environment |
| Failed | a fail this branch caused |
| Old bug | a fail tagged `pre-existing` |
| Needs you | human-only check awaiting its tester, a flaky test, or a result that needs a human decision |
| Not done | blocked, skipped, incomplete, or a browser success missing its recording; state the precise gap in Finding |

The local report uses three results. `Passed` and `Failed` map as named. A local `Not done` becomes `Needs you` when its reason is a person, a decision, or a flaky test, and stays `Not done` otherwise. Each local flow row becomes one Notion row.

## Steps

Follow the execution contract for every Notion call. On a login or access error, stop this step, ask the user to reconnect Notion, and never publish through another tool.

1. **Read the hub.** Fetch the hub. Find the template ID in its `page_templates` list. Note which hub properties exist; fill only those.
2. **Create the report page** from the template, with the hub's `Verdict` set to `In progress`. Title: `PR #[number] [PR title] ([ticket IDs])`, or `Release [YYYY-MM-DD]` for a release. Fill the type, PR, ticket, and FE/BE properties when the hub has them. Record the new page URL at once, so a retry updates this page instead of making a second one.
3. **Fetch the new page** and find the `data-source-url` of its own `Flows` database. Write rows only there, never to the template's database. Fetch that data source too: Notion rejects a `Section` or `Result` value that is not already an option, so add every missing option (keep the existing ones) before creating rows.
4. **Upload the actual recordings and screenshots.** For each file: call create-file-upload with the file name, then run `python3 scripts/notion_upload.py --url <upload_url> --auth "<authorization value>" --file <path>`. Keep the returned `file_upload_id`. One upload ID can go in both the row's `Video` column and its page body. A local path is not a shared attachment. If an upload fails, retain the local report and leave publication `In progress`; report the upload gap without inventing a URL.
5. **Create one row per check**, in plan order, in batched calls. An automated command becomes **one row per test** from the collector's output (`QP1-1`, `QP1-2`, …), never one row per command; skip `setup` entries. See "Automated test rows" below.
   - `Flow`: the check ID, a colon, and the flow name from the plan (`QA3: Upgrade from Free with a new card`)
   - `Result`: from the table above
   - `Section`: the plan section the check belongs to (story title or subsection name)
   - `Finding`: what actually happened; for an unresolved check, include the next action and who needs to do it. Identify human confirmations with tester/date/environment.
   - Page body: `**Did:**`, `**Expected:**`, `**Saw:**`, and `**Tested by:**` lines, followed by the embedded recording and its browser/time range. Put technical fix details (Step 2.7) after the evidence, plus the Linear or Slack line for an old bug.
   - For API speed checks, use the same DEV vs PROD comparison as the local report: target, measured values/sample counts, environment/deployment equivalence, and timing evidence. A PROD speed pass has `Finding: Passed — PROD verified; DEV [measured result]`. Attach the timing log or source link; retain browser recordings when the check includes a browser flow.
6. **Attach the recording to each row's `Video` column** using the same upload ID; keep the existing column name to preserve template views. Include screenshots as supporting attachments. A screenshot must not disguise a missing recording.
7. **Fill the two callouts** by replacing their placeholder text only. Use small search-and-replace edits; never rewrite the whole page, because Notion reorders the blocks.
   - Summary: lead with the local report's verdict and concrete reason. Then `[N] of [M] report rows passed`, counts for the other results, and who needs to do what next. Label these as report-row counts: automated commands expand into individual tests, so this is not the local plan-check denominator.
   - Test details: date/time, who ran it, actual browser/device (label emulation), branch/revision, environment, and what test data was created and deleted.
8. **Set the verdict last:** `Ready` only when the local report is `READY`, every row is `Passed` or `Old bug`, and required evidence was uploaded. Otherwise `Not Ready` once publication is complete. A crashed/incomplete upload stays `In progress`.
9. **Link the page on each Linear ticket** as a link attachment titled `QA report`. Never as a comment.
10. **Re-fetch the page** and confirm: row count equals manual plan checks plus non-setup automated tests plus any command-level gap rows described below. Summary counts must match those rows. Confirm recordings appear as uploaded attachments and playable video blocks, not local paths. Fetch each agent row and check its Slack links point at a reply (see "Agent behaviour rows"). A fetch can return an older cached copy: when its `as of` time is earlier than your last edit, fetch again before trusting it.

## Automated test rows

Build each row from one collector entry:

| Column | Value |
|---|---|
| `Flow` | the entry's `id`, then a colon and its `title` (`QP1-12: Team field opens the list`) |
| `Result` | Default to `qa_status`, never raw `status`: `passed` → Passed; `flaky` → Needs you; `failed` → Failed (or Old bug when confirmed); `not_tested` or `needs_evidence` → Not done. Apply only the documented PROD speed resolution below as an exception. |
| `Section` | `Automated checks` |
| `Finding` | observed outcome, or the entry's `note` in plain words plus the next action |
| `Video` | the uploaded recording; screenshots may support failures but do not clear recording gaps |

Page body: `**Did:**` the user-facing action; `**Expected:**` the assertion's meaning; `**Saw:**` the result and any gap. Then one block per evidence file: `<video src="file-upload://…">` for a video, `<image src="file-upload://…">` for a screenshot. Label browser and attempt number/status; show the failed attempt as well as the retry. Put the test path, command, and optional failed trace after the evidence. For a confirmed API-only pass, state the inspected test/fixtures and assertion instead of claiming a recording exists.

For a DEV-only API-duration failure resolved under `api-performance.md`, use `Passed` only when the local report documents the equivalent PROD speed pass and completed functional assertions. Set `Finding` to `Passed — PROD speed verified; DEV timing failed`, and include both measurements and evidence in the page body. Keep the raw DEV runner result in technical details. Never apply this exception to a functional failure, flaky test, incomplete run, missing recording, or undeployed backend change. Summary counts are assessed QA results; label raw DEV runner totals separately.

Before setting the verdict, compare the counts: rows under `Automated checks` must equal the collector's `summary.tests` for every command. A mismatch means rows are missing, so fix it first.

Keep command-level gaps in a separate `Run gaps` section: create a `QP#` row when its command did not run, produced no tests/report, or had a setup/runner error not represented by a test row. Never lose that blocker because there are no individual test entries. Do not create an extra command row for a healthy run or solely for speed failures already represented by test rows with documented PROD resolutions.

## Agent behaviour rows (chat tests in Slack)

One row per agent check (`QB#`, `QS#`), never one per run:

| Column | Value |
|---|---|
| `Flow` | the ID, a colon, and the check name (`QS4: Korean question gets a Korean answer`) |
| `Result` | Passed only when every run met `Must show` and avoided `Must not show`; any failed run → Failed; the tester could not reach the behaviour (for example its account is not linked) → Not done |
| `Section` | `Agent behaviour` |
| `Finding` | `[passed runs] of [runs] passed`, plus one line for anything wrong |

Page body: `**Sent:**` the exact message. Then for each run, `**Run N:**` pass or fail, the answer time in seconds, and a `Slack thread` link; below it, the final answer as a quote. The Slack thread link is the proof; a quoted answer alone is not.

**The Slack link must open the thread, not just the channel:**
- Link to the agent's **final answer** (a reply inside the thread), never to the question that started it. Notion turns every Slack link into its own Slack-message link. A link to a thread's first message opens only the channel; a link to a reply opens the thread.
- Get it from Slack's permalink call for the answer's own timestamp, and paste the full URL unchanged, including `?thread_ts=…&cid=…`. Never trim or rebuild it.
- When reading back the page, each link shows as `slackMessage://<workspace>/<channel>/<message ts>/<thread ts>`. The two timestamps must differ. If they are equal, the link points at the question: replace it before setting the verdict.

## Rules

- Every agent-run browser `Passed` row needs its recording. Confirmed API-only tests use their inspected assertion and runner result; agent chat checks use the Slack thread proof below. A missing recording means `Not done`, with `missing recording` in Finding, even if the raw runner passed.
- A check a human ran by hand keeps its confirmed result and tester/date/environment, with `no recording supplied` when none was attached. An unexplained tick is not human confirmation.
- Never infer an API-only test from absent video. Use the collector's explicit API-only confirmation process.
- Never put secrets, tokens, or real customer data in a row or a picture.
