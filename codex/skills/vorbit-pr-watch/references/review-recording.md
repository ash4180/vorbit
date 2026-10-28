# Review recording

Read before Step 3, item 8. The recording is one video of the whole QA run. The user watches it, then decides to approve.

## What it is

1. One summary card first. It shows the PR, commit, ticket, verdict, and counts.
2. Then one result card per flow, in plan order. Each card shows Passed, Failed, or Not done, with the reason.
3. After each card comes that flow's clip, when it has one.

It is made from the clips qa-report already saved. Those clips stay the proof. The recording is for watching only. Never put it in the report in place of a clip.

## Where it lives

`.vorbit/pr<N>-review/<commit>/` holds `review-manifest.json` and `review.mp4`. Make one folder per commit. Never overwrite an older one. Do not write into `qa-screenshots/`. That folder belongs to qa-report.

## The manifest

Write it from the final QA report. Do not use the runner's first labels. Use one row for each flow and each automated test command. Keep the plan's order.

| Field | Rule |
|---|---|
| `title` | `PR #<N>: <short title>` |
| `commit` | The short commit you tested |
| `ticket` | The ticket ID, if there is one |
| `verdict` | `Ready` or `Not ready`, as the report says |
| `flows[].id` | The plan ID, such as `QA1` or `QP1` |
| `flows[].name` | The flow name, in the words users see |
| `flows[].result` | `Passed`, `Failed`, or `Not done` |
| `flows[].reason` | One short line. Required for Not done |
| `flows[].clip` | The full path of the real clip, or `null` |
| `flows[].commit` | Set it when the flow kept an earlier pass. Use the commit of that pass |
| `flows[].kind` | `command` for an automated test run with no video |

Rules the script enforces:

1. A Passed browser flow must have a clip. A pass needs a recording.
2. A clip file must exist and must not be empty.
3. A Not done flow needs a reason.
4. Each ID appears once.

Never make footage. Never point a flow at another flow's clip. A Failed flow with no clip gets a card only.

Example:

```json
{
  "title": "PR #1316: Chat search highlights the typed word",
  "commit": "40ef8e3",
  "ticket": "VIB-5072",
  "verdict": "Not ready",
  "flows": [
    {"id": "QA1", "name": "Search a word and see only that word highlighted", "result": "Passed",
     "reason": "Only the typed word is yellow.", "clip": "/path/to/QA1-search-redis.webm"},
    {"id": "QA4", "name": "One-character search in Korean", "result": "Not done",
     "reason": "need Korean chat messages on dev", "clip": null},
    {"id": "QP1", "name": "Automated tests, changed screens", "result": "Passed",
     "reason": "26 of 26 tests passed.", "clip": null, "kind": "command"}
  ]
}
```

## Run it

`python3 scripts/review_recording.py <manifest> --out <folder>/review.mp4`

It prints the path, the length, the size, and the counts. Check the counts against the report. A mismatch is a mistake in the manifest.

## When it cannot run

Exit code 4 means `ffmpeg` or Pillow is missing. Say which one. Tell the user to install it. Then point them to the per-flow clips in `qa-report.md`. Do not use another tool.

## Sharing

The recording stays on this machine. Do not attach it to the PR or Slack. The user decides who sees it.
