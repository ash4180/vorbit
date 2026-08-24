---
name: vorbit-qa-plan
description: Use when the user asks to build or update a QA test plan for the current branch — a human-runnable checklist covering story flows, test data, edge cases and error paths, list and table reliability, device and browser coverage, regression risks, performance checks, and automated Playwright runs when the project has them. It drafts from the branch prd.md and epic.md when they exist, or from answers the user gives when they do not, and writes the plan to the branch spec folder. Do not use for agent-run acceptance validation (that is verify), writing requirements, or implementing fixes.
---

# Vorbit QA Plan

Before planning:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-plan.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the qa-plan workflow: read the branch specs, resolve test targets with the user, draft the human-runnable checklist, get approval, and write qa-plan.md.
