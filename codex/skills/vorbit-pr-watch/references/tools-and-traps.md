# Tools and traps

Read before Step 1.

## Tools this skill needs

| Tool | Used for | If missing |
|---|---|---|
| `gh` (GitHub CLI) | PR facts, comments, approval | Stop. Say to install it and sign in. |
| `orca` (Orca CLI) | Browser upload of screenshots | Stop Step 5. Say Orca is needed. Do not post text without the pictures. |
| Linear connector | Read the ticket | Stop Step 1.4. Follow the execution contract's connector login rule. |
| Slack connector | Read the thread, save a draft | Skip Slack. Give the draft text to the user. |
| Browser runner | QA flows | qa-report marks those flows Not done. |
| `ffmpeg` and Pillow | qa-report's review recording | qa-report says which is missing. Point to the per-flow clips. |

Do not use another route for a missing tool. Do not guess a tool name. Inspect the connector's current schema first.

## Scripts

All run in the PR's worktree. `scripts/` is this skill's folder.

| Script | Does |
|---|---|
| `pr_state.py` | `context`, `init`, `tick`, `mark`, `set-status`, `permit`, `slack-ts` |
| `comment_with_images.py` | Upload screenshots, post one comment, check each image loaded |
| `dev_port.py` | `free`, `owners`, `stop` for the dev server port |

Each prints JSON or a PASS or FAIL line. Run one with `--help` to see its options.

## Traps from the first run

1. **Slack links.** `.../p1793154612071909` means ts `1793154612.071909`. A link to a reply carries `?thread_ts=`, and the thread root wins. `pr_state.py slack-ts` does both.
2. **One thread, two PRs.** The thread may link more than one PR. Act only on the PR the user named.
3. **Images.** `gh` cannot upload images. The Orca browser does it. The user signs in to GitHub once in that tab. Ask, then wait for "done".
4. **Runner labels.** Do not trust a Passed label alone. Open the screenshots of each failed flow and of one passed flow.
5. **Pre-existing problems.** A console warning seen on every page load is one. Tag it, search Linear and Slack, and ask once about tickets. Never create a ticket without a yes.
6. **Test data.** Create it only on local or DEV. Name it `QA <date> <what>`. Log it. Delete it at the end.
7. **The author's branch.** Never push, rebase, or reset it. Never edit its code. Update it with `git pull --ff-only` only.
8. **Ports.** Other sessions hold dev ports. `dev_port.py stop` refuses unless the owner's PR is merged. Never stop any other server yourself.
9. **Approval.** A new push removes the approval in this repo. Say so once after you approve.
10. **Slack voice.** A sent message gets a "Sent using Claude" footer. It cannot be removed. Save a draft instead. Send only if the user asks for Claude's voice.
