---
name: vorbit-pr-watch
description: Use when the user gives a teammate's pull request and asks to review it, QA it, comment on it, watch it for new pushes, and approve it. It reviews the PR diff, runs the QA flows in a browser, explains each problem as a short story, posts one plain comment with screenshots, and watches the PR every 60 minutes, re-testing each new push. When the PR is clean it hands the PR to the user to approve, with the QA review recording (it approves itself only when told to), then saves a Slack draft reply. It never pushes to the author's branch. Requires the GitHub CLI and a PR URL, plus the Orca CLI for screenshots; do not use for your own PR (use prepare-pr), a review only (use review), QA only (use qa-report), or fixing the code.
---

# Vorbit PR Watch

Before watching a PR:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/pr-watch.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the pr-watch workflow: prepare, review, QA, explain, comment with screenshots, watch for new pushes, hand over for approval, then save a Slack draft.
