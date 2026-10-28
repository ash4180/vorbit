# Watch loop and monitor file

Read before Step 6, and on every wake-up.

## The monitor file

Path: `.vorbit/pr<N>-monitor.md` in the PR's worktree. It holds all state, so the watch survives an app restart. The scripts write the header lines and the tick log. You edit only the `## Notes` section, with the Edit tool.

Every `tick`, `mark`, `set-status`, and `permit` below is a `pr_state.py` command. Write it as `python3 scripts/pr_state.py <command> <N> ...`.

| Line | Meaning | Written by |
|---|---|---|
| `Branch` | The PR branch. A different branch stops the run. | init |
| `Slack threads` | `channel/thread ts`, from the links the user gave. | init |
| `Auto-comment` | `yes` when the user allowed comments on new problems. | init |
| `Auto-approve` | `yes` when the user allowed approval when all gates hold. | init |
| `Approval rule` | The three gates for approval. | init |
| `Baseline SHA` | The head commit when the watch began. | init |
| `Reviewed SHA` | The last commit whose review and QA are both done. | `mark reviewed` |
| `Commented SHA` | The last commit that got a PR comment. | `mark commented` |
| `Told until` | Time of the last teammate reply the user heard about. | `mark told` |
| `Status` | `watching`, `waiting_for_user`, or `stopped`. | `set-status` |

Keep these Notes up to date:

- the dev server port and start command
- the saved-login renew command
- the last QA run folder
- the open finding, with its comment link
- pre-existing problems

Keep the line "Only act on PR #N".

## Permissions

Posting a comment and approving are outward actions. They need a go.

1. The user's words are the go: "leave a comment to the author" or "approve it".
2. Or the user allowed it at the start. "Comment if there is a problem" sets `--auto-comment`. "Approve if it is fine" sets `--auto-approve`.
3. With neither, say what you would do. Run `set-status <N> waiting_for_user "<what you wait for>"`. Do not schedule another wake-up. When the user says go, do the action. Then run `set-status <N> watching` and schedule again.

Did the user say "from now on"? Run `permit <N> comment` or `permit <N> approve`. Add `--off` to take it back.

Slack is always a draft. See `comment-style.md`.

## Start the loop

1. Run `set-status <N> watching`.
2. In Claude Code, start the `loop` skill in self-paced mode. Its prompt is the pr-watch entry line. Add the PR number and the worktree's full path. Each wake-up moves to that folder first. Wake up about every 15 minutes with `ScheduleWakeup`.
3. In another agent with no scheduler, report `blocked_missing_capability` for this step. Tell the user to run pr-watch with the PR number. Each run is one check. The monitor file keeps everything.

## Each wake-up

Move to the worktree. Run `python3 scripts/pr_state.py tick <N>`. It logs one line by itself. Act on `event`:

| Event | Do this |
|---|---|
| `no_change` | Nothing. Schedule the next wake-up. |
| `new_comment` | Tell the user in one line: who wrote and the first line. Then run `mark <N> told <at>` with the time of the newest reply. Do nothing else. |
| `new_push` | See "New push" below. |
| `merged` or `closed` | Run `set-status <N> stopped "<event>"`. Tell the user. End the loop. |
| `already_stopped` | End the loop. Say nothing. |

Does `new_comments` have entries on any event? Tell the user about them too. Then run `mark <N> told <at>`. A skipped bot comment is only a count. Say nothing about it.

## New push

1. If `history_rewritten` is true, the author force-pushed. Tell the user. Run `set-status <N> waiting_for_user "history rewritten"`. Ask before you update the worktree. On a yes, with a clean `git status`, run `git fetch` and `git reset --keep origin/<branch>`. Then run `tick` again.
2. If `needs_pull` is true, run `git pull --ff-only`. Then run `tick` again to get `changed_files`. If the pull fails, tell the user once. Run `set-status <N> waiting_for_user "pull failed"`.
3. Run Step 2 (review) on the new changes. Run Step 3 (QA) on two groups of flows. One group uses a changed file. The other did not pass last time. A flow whose files did not change keeps its earlier pass. Name that commit in the approval text.
4. Run `mark <N> reviewed <commit you tested>`. Use the commit you tested, not a newer one.
5. A problem: Step 4, then Step 5. No problem: Step 7.
6. If checks are `pending`, wait for the next wake-up before Step 7. If checks are `failing`, tell the user once. That is the author's build, not yours to fix.

## Order of writes

Do the work first. Mark it done second. A stop between the two is safe. The next wake-up repeats the step.

1. Comment posted, then `mark commented`.
2. User told, then `mark told`.
3. Review and QA both done, then `mark reviewed`.

## After an app restart

A running subagent stops when the app restarts. Do not start over.

1. Open the newest run evidence folder. Read `runner-session.json` and `flow-results.json` there.
2. Keep flows that finished. Resume the same agent for the rest, as qa-report's flow-runner reference says.
3. Check `created-data.json` for test data to delete.
4. Then continue from the monitor file. `Reviewed SHA` tells you if the commit is done.

## After approval

In this repo, a new push removes the approval. Tell the user once. End the loop with `set-status <N> stopped "approved"`.
