---
name: vorbit-qa-report
description: Run the branch QA plan flow by flow and write a short, dated report a non-technical reader can act on. One table, flow first, each problem in its flow's row, with a narrated recording per flow and one review video that joins them. Three results only (Passed, Failed, Not done); developer detail stays in a folded section. Checks test data before running, creates missing records on the local app or DEV and deletes them after, never fakes the server unless asked, and never re-runs the suite on the base code. When requested, publishes the report to a named Notion hub. Requires qa-plan.md; use qa-plan to author it and implement to fix code.
---

# Vorbit QA Report

Before reporting:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-report.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the qa-report workflow: check the plan's needs and authorization, run its automated commands, prepare and resume one native subagent for browser flows when the host supports the selected model, review its evidence, and write the dated report with an honest verdict. Report missing delegation capabilities rather than silently using the parent.
