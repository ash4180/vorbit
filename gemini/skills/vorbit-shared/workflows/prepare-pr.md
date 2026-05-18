# Vorbit Prepare PR Workflow

Use for finalizing a feature branch for merge.

1. Load Vorbit durable rules before doing anything else.
2. Pre-flight: verify on feature branch (not main/dev/demo), extract issue-id from branch name, check git state (uncommitted changes, push status), detect design files in `designs/`, detect lo-fi wireframes in `.claude/wireframes/`, check mock data.
3. Design file handling (if `designs/` exists): record recovery hash BEFORE stripping (`git log -1 --format="%H" -- designs/`), inventory `.pen` files, `git rm -r designs/{issue-id}/`, commit stripping ("chore: strip design files before merge", no AI attribution).
4. Lo-fi wireframe cleanup (if `.claude/wireframes/` exists): unlike `.pen` design files, wireframes don't need a recovery hash — they're ephemeral lo-fi artifacts from `/vorbit-explore`. Run `git rm -rf .claude/wireframes/ 2>/dev/null || true` to remove any tracked files, then `rm -rf .claude/wireframes/` to clean untracked (gitignored) files. Commit only if anything was tracked: "chore: strip lo-fi wireframes before merge" (no AI attribution).
5. PR body generation: fetch Linear issue (title, description, ACs, URL), analyze commit history (ignore mechanical "strip design files" and "strip lo-fi wireframes" commits), generate body with Summary, Design files section (if stripped), Notable decisions, Related (Closes link), Test plan from ACs.
6. Show PR title and body to user. Wait for approval or edits.
7. Create PR: push branch, `gh pr create`, post design recovery reference to Linear (if stripped), update Linear status to "In Review".
8. Report: PR URL, branch info, design file count, wireframes cleanup status, Linear status.
