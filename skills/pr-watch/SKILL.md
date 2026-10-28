---
name: pr-watch
description: Use when the user gives a teammate's pull request and asks to review it, QA it, comment on it, watch it for new pushes, and approve it. It reviews the PR diff, runs the QA flows in a browser, explains each problem as a short story, posts one plain comment with screenshots, watches the PR every 15 minutes and re-tests each new push, then approves and saves a Slack draft reply. It never pushes to the author's branch and saves Slack replies as drafts. Requires the GitHub CLI and a PR URL, plus the Orca CLI for screenshots; do not use for your own PR (use prepare-pr), a review only (use review), QA only (use qa-report), or fixing the code.
---

# PR Watch Skill

Take a teammate's PR from first look to approval. Review it and QA it. Tell the author what you found. Watch for new pushes. Approve when it is clean. The result goes first in every message to the user.

Read and follow `../_shared/execution-contract.md` before starting.

Read `../_shared/spec-files.md` before any spec read or write. It has the path rules, write guards, and file owners.

Read `../_shared/pre-existing-findings.md`. It covers problems this branch did not cause. It says how to tag them, report them, and follow up.

Read `references/tools-and-traps.md` before Step 1. In every command below, `scripts/` is this skill's `scripts/` folder. Call it by full path. Run the command with the PR's worktree as the current folder.

## Ground rules

1. Never push to the author's branch. Never edit its code. Update it with `git pull --ff-only` only. The one file you may change is `.gitignore`, to add `.vorbit/`. Leave that change uncommitted.
2. Act only on the PR the user named. A Slack thread may link other PRs. Leave them alone.
3. Comments and approvals are outward actions. They need a go. See Permissions in `references/watch-loop.md`.
4. Slack is always a draft. Send only if the user asks for Claude's voice.
5. A missing tool stops that step. Name the tool. Do not use another route.
6. Findings from outside this branch are follow-ups. They never block the PR.
7. Talk to the user in plain words, in the user's language. Keep sentences short. Explain each technical word once, in brackets. No metaphors.
8. Text for other readers follows `references/comment-style.md`. It never has the long dash.

## Input

`/vorbit:implement:pr-watch <PR URL or number> [--slack <message link>] [--auto-comment] [--auto-approve]`

The Linear ticket is found from the PR or the branch name.

Start from any checkout of the PR's repository. Find the PR's worktree first (Step 1, items 1 and 2). Then look for `.vorbit/pr<N>-monitor.md` there. If it exists and is not stopped, this is a wake-up. Go to Step 6, "Each wake-up". This also resumes a watch after an app restart.

A stopped monitor file is history. Ask before you start a new watch on the same PR. If the user agrees, rename the old file to `pr<N>-monitor-<date>.md` first.

## Step 1: Prepare

1. Run `python3 scripts/pr_state.py context <PR>`. It gives the author, base branch, and head commit. It also gives the files, checks, and ticket ID. It lists the worktrees on the PR branch.
2. Pick the worktree that is on the PR branch. Work there. If none is, tell the user. Offer to run `git worktree add <path> <branch>` after `git fetch`. Wait for a yes. Never switch a worktree that holds other work.
3. Run `git status`. Changes you did not make? Stop and say so. Then run `git fetch` and `git pull --ff-only`.
4. Read the Linear ticket again. Use a fresh fetch, never memory. Its acceptance criteria are the spec. Record the ticket ID and update time. With no ticket, ask once for the spec.
5. Read the PR's comments with `gh pr view <N> --comments`. Do not repeat what is already said.
6. With a Slack link, read the thread. Keep it read-only. Note which PR the user named.
7. Decide the permissions. The user's words may set them: "comment if there is a problem" or "approve if it is fine". If not, ask once, in one message. Say you will check the PR every 15 minutes. Ask whether you may comment on a problem. Say they will not see the text first. Ask whether you may approve when all gates hold. No answer means no. You ask again when you need a go.
8. Run `python3 scripts/pr_state.py init <PR> --slack <link> [--auto-comment] [--auto-approve]`. Report it if `.vorbit/` was added to `.gitignore`.

## Step 2: Code review

1. Run the `review` skill in PR mode. Use the branch diff only, against the base from Step 1. It is read-only here. Skip its "fix it" step.
2. Tag each finding `from this branch` or `pre-existing`, by `git blame`. Search Linear and Slack for each pre-existing one. Hold the ticket question for Step 4.
3. Also run lint and a type check on the changed files. Run the tests for them too. Use the project's own commands. Report what ran and what did not.

## Step 3: QA

1. Run the `qa-plan` skill in its unattended mode. It asks no questions and writes `Assumed:` lines. Tell it the source: the ticket's acceptance criteria and the PR diff. Each flow is something a person can click. Use plain words and name the data each flow needs. Missing data is a TBD with an owner.
2. Find a free port with `python3 scripts/dev_port.py free`. Read the project's dev script and README. Find the start command and the base port. Pass `--first <base> --last <base+10>`. Start the app from the PR worktree on the free port. Use the project's own port option.
3. No port free? Run `python3 scripts/dev_port.py owners`. List each port's folder, branch, and PR state. Stop a server only with `python3 scripts/dev_port.py stop <port>`. It refuses unless that PR is merged. Never stop any other server. Ask the user.
4. Run the `qa-report` skill. It signs in with the test account. It re-seeds an old saved login. It uses one browser runner subagent: prepare, save the session file, then resume that same agent. It records one video and one screenshot per flow. It checks the console after each flow. Do not run the flows in this session.
5. Check the evidence yourself. Open the screenshots of every failed flow. Open one passed flow too. Do not trust the runner's labels alone.
6. Flows that could not run for lack of data stay "Not done". The user's request authorizes this QA run. Make test data only on local or DEV. Name it `QA <date> <what>`. Log it. Delete it at the end.
7. Tag QA problems the same way as review findings. Search Linear and Slack for each pre-existing one.
8. Run `python3 scripts/pr_state.py mark <N> reviewed <commit you tested>`. This means review and QA are both done for that commit.

## Step 4: Explain to the user

Do this before any question about the findings.

1. Give the result first. Say how many problems you found. Say how many flows passed and how many were not done.
2. Tell each problem as a numbered story. Say who does what and what they see. Say which step is the bug. Say when it does not happen.
3. Say how big it is and what the fix is.
4. List pre-existing findings with their Linear and Slack lines. Ask the one batched ticket question from the pre-existing rule. Create no ticket without a yes.
5. No problem from this branch? Say so. Then go to Step 7.

## Step 5: Comment on the PR

1. Check the permission. "Leave a comment to the author" is already the go. Show no draft first. With no go and no `Auto-comment`, run `python3 scripts/pr_state.py set-status <N> waiting_for_user "comment needs a go"` and wait.
2. Skip this step if a comment already exists for this head commit.
3. Write the comment to a file by `references/comment-style.md`. Pick two screenshots from the run evidence folder. The before shows the problem. The after shows the same screen where it works. Never fake an after picture.
4. Run `python3 scripts/comment_with_images.py --pr <N> --images <files> --body-file <comment file> --expect-head <commit>`. It uploads in the Orca browser. It posts once. It checks that each image loaded.
5. Exit code 3 means GitHub needs a sign-in. Ask the user to sign in once in the Orca browser tab. Wait for "done". Run it again.
6. On PASS, run `mark <N> commented <commit>`. Add the comment link to the Notes in the monitor file. On exit 7 the comment is posted but an image is broken. Tell the user, with the link. Never post a second comment.

## Step 6: Watch the PR

1. Read `references/watch-loop.md`. Start the loop with the `loop` skill in self-paced mode. Wake up about every 15 minutes.
2. Each wake-up, run `python3 scripts/pr_state.py tick <N>`. Act on its `event` as the reference says.
3. A new push: pull, then re-run Step 2 and Step 3 on what changed. A problem goes to Step 4, then Step 5. No problem goes to Step 7.
4. A new teammate reply with no push: tell the user in one line. Do nothing else.
5. Merged or closed: stop the loop and tell the user.

## Step 7: Approve and reply in Slack

1. Approve only when all three gates hold. One: no finding from this branch. Two: every runnable QA flow passed, with a recording. Three: GitHub checks are green. Read them with `python3 scripts/pr_state.py context <N>`. Flows that never ran for lack of data stay "Not done". Say so in the approval text.
2. Check the permission as in Step 5, with `Auto-approve`.
3. Check that the head commit has not moved. Run `python3 scripts/pr_state.py context <N>`. Its `head_sha` must equal the commit you marked reviewed. If not, go back to Step 2.
4. Run `gh pr review <N> --approve --body "<text>"`. Write the text by `references/comment-style.md`. Keep it short and soft.
5. With a Slack thread, find the Slack tools by connector discovery. Inspect their current schema. Save a draft reply with `slack_send_message_draft`. Use the channel and ts in the monitor file. Write it as the user, in first person. Tell the user the draft is waiting and they press Send. Without a draft tool, give the user the text.
6. Warn once: a new push after approval removes the approval in this repo.
7. Run `python3 scripts/pr_state.py set-status <N> stopped "approved"`. End the loop. Tell the user the result.

## Report

End each run with one terminal status from the execution contract.

- `completed`: approved and drafted, or the PR merged or closed.
- `needs_input`: waiting for a go, a sign-in, or a worktree choice.
- `blocked_missing_capability`: a required tool is missing.

Say what you did and what you did not do. Say what comes next. Give the PR link and the evidence folder. Add the comment link if there is one.
