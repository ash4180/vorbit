---
name: vorbit-prepare-pr
description: Use only when the user explicitly asks to finalize the current feature branch, strip design files for merge, or open a GitHub pull request. It checks and may rebase the branch, can remove and commit design files, pushes commits, creates the approved PR, and may update Linear. Requires a clean non-protected branch plus GitHub access; do not use for code review, commit-only requests, or generic Git advice.
---

# Vorbit Prepare PR

Before preparing:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/prepare-pr.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the prepare-pr workflow: pre-flight checks, design file handling, PR body generation, create PR with Linear integration.
