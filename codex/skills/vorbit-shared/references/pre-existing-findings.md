# Pre-existing Findings

Read `execution-contract.md` in this directory first.

Applies to every skill that reports findings, fails, or a verdict: `review`, `qa-report`.

## Rule

A bug this branch did not cause never blocks. It becomes a follow-up, not a fail. The finding still gets reported, with evidence, in its own section.

## Step 1: Tag every finding

Tag each finding `from this branch` or `pre-existing`. Use the code as proof, never a guess:

1. Resolve `<base>` per the Base Branch section of the execution contract. Get the branch scope: `git diff --name-only $(git merge-base HEAD <base>)..HEAD`. When that diff is empty, use the uncommitted diff instead.
2. Find the code behind the finding: file and lines for a review finding, the screen handler or component for a QA check.
3. Run `git blame -L <start>,<end> <file>` on those lines. Compare each blamed commit against `git rev-list $(git merge-base HEAD <base>)..HEAD`.
4. Tag `pre-existing` only when ALL of these hold:
   - the blamed lines were not changed by any commit on this branch
   - the behavior is outside the branch's acceptance criteria and flows (spec files, or the ticket when no spec exists)
   - the agent can name the base-branch commit or file that already carries the bug
5. For a failing automated test whose spec and screen are outside the branch diff, the proof may also be the project's scheduled suite result (for example the latest nightly run) showing the same test failing on the base branch.
6. When any point is unsure, tag `from this branch`. A wrong block is safer than a wrong pass.

Never re-run the test suite on the base-branch code to prove a finding is pre-existing. That costs a full run and still proves nothing about flaky tests. Use blame, the base-branch file, or the scheduled suite result; what stays unsure stays `from this branch` or `unresolved`.

Never re-tag a finding as pre-existing to make a verdict pass.

## Step 2: Keep it out of the verdict

- Pre-existing findings never change the verdict, the status, or the merge-risk line.
- `review`: they go in their own section named `Pre-existing (follow-up)`, after the branch findings. `qa-report`: one line with the count in the human part, and the table under For developers.
- Each entry has three parts: what is wrong, where (file:line or QA flow ID), and the evidence it predates the branch (blame commit, base-branch file, or scheduled suite result).

## Step 3: Look for existing discussion

For each pre-existing finding, before asking about a ticket:

1. Use the environment's connector discovery to find the Linear tools and inspect their current search schema. Search issues with 2 or 3 keywords from the finding (error text, screen name, file name). Read-only.
2. Do the same for Slack when a Slack connector exists. Search messages with the same keywords. Read-only. Skip silently when no Slack connector exists.
3. Record one line per source under the finding:
   - `Linear: TL-123 (open, "title")` or `Linear: nothing found`
   - `Slack: #channel, date, one-line gist` or `Slack: nothing found` or `Slack: not connected`
4. A search that fails is recorded as `search failed: [reason]`. Never block on it.

## Step 4: Ask once about tickets

After the report, ask the user one batched question: for each pre-existing finding with no Linear issue, create a ticket or not. A finding that already has an issue gets the line `link found, no new ticket` instead.

Only on an explicit yes:

1. Verify the Linear connector and inspect its current create-issue schema.
2. Create one issue per approved finding. Title in plain language. Description: what is wrong, where, evidence, and a link to the Slack thread or related issue when found. Use the same team and project as the branch's story tickets when `prd.md` has a `## Linear Sync` section; otherwise ask.
3. Report the created issue IDs in the session. Never comment on other issues (execution contract).

No answer, or "no", means no Linear write.
