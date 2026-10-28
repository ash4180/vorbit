---
name: vorbit-pr-watch
description: Use when the user gives a teammate's pull request and asks to review it, QA it, comment on it, watch it for new pushes, and approve it. It reviews the PR diff, runs the QA flows in a browser, explains each problem as a short story, posts one plain comment with screenshots, and watches the PR every 15 minutes, re-testing each new push. After each QA run it makes one review recording that covers every flow. When the PR is clean it hands the PR to the user to approve (it approves itself only when told to), then saves a Slack draft reply. It never pushes to the author's branch. Requires the GitHub CLI and a PR URL, plus the Orca CLI for screenshots and ffmpeg for the recording; do not use for your own PR (use prepare-pr), a review only (use review), QA only (use qa-report), or fixing the code.
---

# Vorbit PR Watch

Before watching a PR:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/pr-watch.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the pr-watch workflow: prepare, review, QA, explain, comment with screenshots, watch for new pushes, make the review recording, then hand over for approval and save a Slack draft.
