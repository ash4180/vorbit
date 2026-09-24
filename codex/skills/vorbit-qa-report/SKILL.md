---
name: vorbit-qa-report
description: Use when the user asks to run the QA checks or produce a QA report for the current branch. It executes the plan's automated E2E commands (Playwright or any runner the plan lists), can click through the unticked manual checks itself when a browser-automation capability is available, records honest results in qa-plan.md, takes a screenshot of every check it runs, and writes a dated human-readable qa-report.md with those pictures embedded — newest run first, with a ready or not-ready verdict. Fails this branch did not cause become follow-ups, not blockers; it checks Linear and Slack for prior discussion and asks before creating a ticket. When the caller names a Notion report hub, it also publishes the run as a page from the hub's template, one row and picture per check, and links that page on the Linear tickets. Otherwise it never writes to Linear. Requires an existing qa-plan.md; do not use to author the plan (qa-plan), check acceptance criteria (the implement skill does that), or fix code.
---

# Vorbit QA Report

Before reporting:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-report.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the qa-report workflow: collect manual results, run the plan's automated commands with approval, and write the dated report with an honest verdict.
