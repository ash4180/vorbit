---
name: vorbit-qa-plan
description: Use when the user asks to build or update a QA test plan for the current branch. One check is one complete user flow a person can click through, start to end result, with its steps, expected result, and the data it needs. The plan covers story flows, failure paths, list and table reliability, device and browser coverage, regression flows for touched features, and the automated test files for the changed screens (the full suite only for a release). It drafts from the branch prd.md and epic.md when they exist, or from the user's answers (or the PR and diff in an unattended run), and writes the plan to the branch spec folder. Do not use for agent-run acceptance checks (the implement skill does those), writing requirements, or implementing fixes.
---

# Vorbit QA Plan

Before planning:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-plan.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the qa-plan workflow: read the branch specs, run the regression scan, resolve test targets with the user (or assume and note them when unattended), draft the human-runnable checklist, get approval unless unattended, and write qa-plan.md.
