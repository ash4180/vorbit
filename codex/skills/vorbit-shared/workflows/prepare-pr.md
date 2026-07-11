# Vorbit Prepare PR Workflow

Use for finalizing a feature branch for merge.

1. Load the Vorbit runtime contract and durable rules.
2. Before any mutation, require a clean non-protected branch; resolve the base; verify the Git remote, GitHub capability/authentication, push access, and optional Linear operations; and run the relevant verification/review gates. Stop on a failed preflight.
3. Inventory the exact planned changes: rebase strategy, whether force-with-lease may be required, tracked design paths under the issue directory, mechanical commits, PR creation, and Linear updates. Get explicit approval for this mutation plan.
4. Rebase locally when requested. Resolve conflicts with the user; never auto-pick a side or auto-stash. Defer the push until the PR body is approved.
5. If stripping designs, record clean-tree `HEAD`, verify every approved path exists at that commit with `git cat-file`, remove only the approved issue directory, and commit the removal. A hash is a recovery hint, not a permanent backup.
6. Fetch the Linear issue when available and generate a PR body from the full branch history: Summary, optional Design files, optional Notable decisions, Related issue/parent links, and AC-derived Test plan.
7. Show the exact title, body, base, and push mode. Wait for approval or edits.
8. Re-check whether a PR already exists. Push normally, or with `--force-with-lease` only after an approved rebase; create or reuse the PR. Only when Linear integration was selected, resolved to an issue, and approved, post the applicable design reference and move that issue to the team's In Review state; otherwise skip Linear and report why.
9. Record each successful external ID so a retry resumes instead of duplicating the PR or comment. Report partial success immediately if a later mutation fails.
10. Report PR URL, branch/base, verification evidence, stripped paths and retention caveat, Linear status, and terminal status.
