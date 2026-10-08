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
- an inline `All Checks` database. Every chart and list reads this database, so the page fills itself once the rows exist.

`All Checks` columns: `Check` (title), `Result`, `Section`, `What`, `Finding`, `Screenshot`.

## Result values

Map every check in this run to exactly one `Result`:

| Result | When |
|---|---|
| Passed | the expected result was seen, and the row has proof (picture, video, or pass line for a no-page test) |
| Failed | a fail this branch caused |
| Old bug | a fail tagged `pre-existing` |
| Needs you | the app is safe but differs from the plan, or the check needs a human decision |
| Not tested | blocked, skipped, `needs human`, or no picture or video exists |

## Steps

Follow the execution contract for every Notion call. On a login or access error, stop this step, ask the user to reconnect Notion, and never publish through another tool.

1. **Read the hub.** Fetch the hub. Find the template ID in its `page_templates` list. Note which hub properties exist; fill only those.
2. **Create the report page** from the template, with the hub's `Verdict` set to `In progress`. Title: `PR #[number] [PR title] ([ticket IDs])`, or `Release [YYYY-MM-DD]` for a release. Fill the type, PR, ticket, and FE/BE properties when the hub has them. Record the new page URL at once, so a retry updates this page instead of making a second one.
3. **Fetch the new page** and find the `data-source-url` of its own `All Checks` database. Write rows only there, never to the template's database. Fetch that data source too: Notion rejects a `Section` or `Result` value that is not already an option, so add every missing option (keep the existing ones) before creating rows.
4. **Upload each picture or video.** For each file: call create-file-upload with the file name, then run `python3 scripts/notion_upload.py --url <upload_url> --auth "<authorization value>" --file <path>`. Keep the returned `file_upload_id`. One upload ID can go in both the row's `Screenshot` column and its page body.
5. **Create one row per check**, in plan order, in batched calls. An automated command becomes **one row per test** from the collector's output (`QP1-1`, `QP1-2`, …), never one row per command; skip `setup` entries. See "Automated test rows" below.
   - `Check`: the check ID (`QA3`, `QR1`, `QP2`)
   - `Result`: from the table above
   - `Section`: the plan section the check belongs to (story title or subsection name)
   - `What`: the action, in the plan's own words, shortened to one line
   - `Finding`: one line for anything not `Passed`; empty for a pass
   - Page body: `**Did:**`, `**Expected:**`, `**Saw:**` lines. For a fail or old bug, add `**Fix idea:**` (from Step 2.7), plus the Linear or Slack line for an old bug. Then the image or video block.
6. **Attach the picture to each row's `Screenshot` column** with the same upload ID.
7. **Fill the two callouts** by replacing their placeholder text only. Use small search-and-replace edits; never rewrite the whole page, because Notion reorders the blocks.
   - Summary: `[N] of [M] checks passed.` Then one short sentence each for Needs you, Failed, Old bug, and what was not tested. Skip a sentence when its count is zero.
   - Test details: date, who ran it, browser, branch, where it was tested, and what test data was created and deleted.
8. **Set the verdict last:** `Ready` when every row is `Passed` or `Old bug`; otherwise `Not Ready`. Setting it last means a crashed run stays `In progress`, which is honest.
9. **Link the page on each Linear ticket** as a link attachment titled `QA report`. Never as a comment.
10. **Re-fetch the page** and confirm: the row count equals the plan's check count, and the counts in the Summary match the rows. Fetch each agent row and check its Slack links point at a reply (see "Agent behaviour rows"). A fetch can return an older cached copy: when its `as of` time is earlier than your last edit, fetch again before trusting it.

## Automated test rows

Build each row from one collector entry:

| Column | Value |
|---|---|
| `Check` | the entry's `id`, then a colon and its `title` (`QP1-12: Team field opens the list`) |
| `Result` | `passed` → Passed; `passed` with `flaky: true` → Needs you, Finding "passed only on a retry"; failed, timedOut, or interrupted → Failed (or Old bug when tagged pre-existing); `skipped` → Not tested |
| `Section` | `Automated checks` |
| `What` | the entry's `path` |
| `Finding` | empty for a pass; otherwise the entry's `note` in plain words |
| `Screenshot` | the uploaded video, or the screenshot when there is no video |

Page body: `**Did:**` the test's path and the command that ran it; `**Saw:**` the result, plus the `note` when present. Then one block per evidence file: `<video src="file-upload://…">` for a video, `<image src="file-upload://…">` for a screenshot. Attach a trace file as `<file src="file-upload://…">` only for a fail. For an API-only pass, write `**Proof:** Playwright reported this test as passed` instead of a picture.

Before setting the verdict, compare the counts: rows under `Automated checks` must equal the collector's `summary.tests` for every command. A mismatch means rows are missing, so fix it first.

## Agent behaviour rows (chat tests in Slack)

One row per agent check (`QB#`, `QS#`), never one per run:

| Column | Value |
|---|---|
| `Check` | the ID, a colon, and the check name (`QS4: Korean question gets a Korean answer`) |
| `Result` | Passed only when every run met `Must show` and avoided `Must not show`; any failed run → Failed; the tester could not reach the behaviour (for example its account is not linked) → Not tested |
| `Section` | `Agent behaviour` |
| `What` | the message sent, shortened to one line |
| `Finding` | `[passed runs] of [runs] passed`, plus one line for anything wrong |

Page body: `**Sent:**` the exact message. Then for each run, `**Run N:**` pass or fail, the answer time in seconds, and a `Slack thread` link; below it, the final answer as a quote. The Slack thread link is the proof; a quoted answer alone is not.

**The Slack link must open the thread, not just the channel:**
- Link to the agent's **final answer** (a reply inside the thread), never to the question that started it. Notion turns every Slack link into its own Slack-message link. A link to a thread's first message opens only the channel; a link to a reply opens the thread.
- Get it from Slack's permalink call for the answer's own timestamp, and paste the full URL unchanged, including `?thread_ts=…&cid=…`. Never trim or rebuild it.
- When reading back the page, each link shows as `slackMessage://<workspace>/<channel>/<message ts>/<thread ts>`. The two timestamps must differ. If they are equal, the link points at the question: replace it before setting the verdict.

## Rules

- Every `Passed` row needs proof: a picture or video, the runner's pass line for a test that opened no page, or the Slack thread link for an agent check. No proof means `Not tested`.
- A check a human ran by hand keeps its result, with `Finding: run by hand, no picture` when none was attached.
- Automated runs: attach the runner's own videos or pictures, one row per test. A test that opened no page uses its pass line as proof.
- Never put secrets, tokens, or real customer data in a row or a picture.
