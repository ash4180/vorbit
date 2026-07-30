---
name: vorbit-qa-report
description: Use when the user asks to run the QA checks or produce a QA report for the current branch. It reads the manual results in qa-plan.md, optionally executes the plan's automated E2E commands (Playwright or any runner the plan lists), and writes a dated human-readable qa-report.md in the branch spec folder — newest run first, with a ready or not-ready verdict. It never writes to Linear. Requires an existing qa-plan.md; do not use to author the plan (qa-plan), validate acceptance criteria (verify), or fix code.
---

# Vorbit QA Report

Before reporting:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-report.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the qa-report workflow: collect manual results, run the plan's automated commands with approval, and write the dated report with an honest verdict.
