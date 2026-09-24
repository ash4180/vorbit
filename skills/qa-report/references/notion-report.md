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
| Passed | the agent saw the expected result, and the row has a picture or video |
| Failed | a fail this branch caused |
| Old bug | a fail tagged `pre-existing` |
| Needs you | the app is safe but differs from the plan, or the check needs a human decision |
| Not tested | blocked, skipped, `needs human`, or no picture or video exists |

## Steps

Follow the execution contract for every Notion call. On a login or access error, stop this step, ask the user to reconnect Notion, and never publish through another tool.

1. **Read the hub.** Fetch the hub. Find the template ID in its `page_templates` list. Note which hub properties exist; fill only those.
2. **Create the report page** from the template, with the hub's `Verdict` set to `In progress`. Title: `PR #[number] [PR title] ([ticket IDs])`, or `Release [YYYY-MM-DD]` for a release. Fill the type, PR, ticket, and FE/BE properties when the hub has them. Record the new page URL at once, so a retry updates this page instead of making a second one.
3. **Fetch the new page** and find the `data-source-url` of its own `All Checks` database. Write rows only there, never to the template's database.
4. **Upload each picture or video.** For each file: call create-file-upload with the file name, then run `python3 scripts/notion_upload.py --url <upload_url> --auth "<authorization value>" --file <path>`. Keep the returned `file_upload_id`. One upload ID can go in both the row's `Screenshot` column and its page body.
5. **Create one row per check**, in plan order, in one batched call:
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
10. **Re-fetch the page** and confirm: the row count equals the plan's check count, and the counts in the Summary match the rows.

## Rules

- Every `Passed` row needs a picture or video. No proof means `Not tested`.
- A check a human ran by hand keeps its result, with `Finding: run by hand, no picture` when none was attached.
- Automated runs: attach the runner's own pictures or videos. When a passing run saved none, attach a screenshot of the runner's HTML report page.
- Never put secrets, tokens, or real customer data in a row or a picture.
