# Vorbit Prepare PR Workflow

Use for finalizing a feature branch for merge.

1. Load Vorbit durable rules before doing anything else.
2. Pre-flight: verify on feature branch (not main/dev/demo), extract issue-id from branch name, check git state (uncommitted changes, push status), detect design files, check mock data.
3. Design file handling (if `designs/` exists): record recovery hash BEFORE stripping (`git log -1 --format="%H" -- designs/`), inventory `.pen` files, `git rm -r designs/{issue-id}/`, commit stripping (no AI attribution).
4. PR body generation: fetch Linear issue (title, description, ACs, URL), analyze commit history, generate body with Summary, Design files section (if stripped), Notable decisions, Related (Closes link), Test plan from ACs.
5. Show PR title and body to user. Wait for approval or edits.
6. Create PR: push branch, `gh pr create`, post design recovery reference to Linear (if stripped), update Linear status to "In Review".
7. Report: PR URL, branch info, design file count, Linear status.
