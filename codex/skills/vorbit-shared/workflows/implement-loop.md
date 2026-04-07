# Vorbit Implement Loop Workflow

Use for autonomous iteration through sub-issues until completion.

1. Load Vorbit durable rules before doing anything else.
2. Parse arguments: issue ID (required), `--loop` flag, `--cancel` flag, optional `--completion-signal`.
3. If `--cancel`: delete `.claude/.loop-state.json` and stop.
4. Check for sub-issues: fetch parent issue, parse "Implementation Order" section, build work queue (skip Done/Completed/Cancelled issues).
5. Create state file (`.claude/.loop-state.json`): active, command, completion signal, max iterations (50), issue tracking.
6. During implementation: read state file, work on `subIssues[currentSubIssueIndex]` if parent has sub-issues, otherwise work on main issue directly.
7. After each cycle: verify acceptance criteria met and tests pass. If complete: update Linear to "Done", add completion comment, advance to next sub-issue. If not complete: describe remaining work, continue same issue.
8. Linear updates are REQUIRED: update status to "In Progress" when starting, add progress comments, mark "Done" when complete. Actually call the tools — don't just describe updates.
9. When all sub-issues done: check parent acceptance criteria, mark parent "Done" if met.
10. State file is gitignored, deleted on completion or cancel.
