# Vorbit Prepare PR Workflow

Use for finalizing a feature branch for merge.

> **MCP namespace**: This workflow optionally uses `mcp__plugin_linear_linear__*` for Linear integration (skipped when no issue ID is detected). See `vorbit-shared/references/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

1. Load Vorbit durable rules before doing anything else.
2. Pre-flight: verify on feature branch (not main/dev/demo), extract issue-id from branch name, check git state (uncommitted changes, push status), detect design files in `designs/`, check mock data.
3. Design file handling (if `designs/` exists): record recovery hash BEFORE stripping (`git log -1 --format="%H" -- designs/`), inventory `.pen` files, `git rm -r designs/{issue-id}/`, commit stripping ("chore: strip design files before merge", no AI attribution).
4. PR body generation: fetch Linear issue (title, description, ACs, URL), analyze commit history (ignore the mechanical "strip design files" commit), generate body with Summary, Design files section (if stripped), Notable decisions, Related (Closes link), Test plan from ACs.
5. Show PR title and body to user. Wait for approval or edits.
6. Create PR: push branch, `gh pr create`, post design recovery reference to Linear (if stripped), update Linear status to "In Review".
7. Report: PR URL, branch info, design file count, Linear status.
