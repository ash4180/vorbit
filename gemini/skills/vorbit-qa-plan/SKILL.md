---
name: vorbit-qa-plan
description: Use when the user asks to build or update a QA test plan for the current branch — a human-runnable checklist covering story flows, test data, edge cases and error paths, list and table reliability, device and browser coverage, regression risks, performance checks, and automated Playwright runs when the project has them. It drafts from the branch prd.md and epic.md when they exist, or from the user's answers (or the PR and diff in an unattended run) when they do not, always builds regression checks (from epic.md, else from the git diff), and writes the plan to the branch spec folder. Do not use for agent-run acceptance checks (the implement skill does those), writing requirements, or implementing fixes.
---

# Vorbit QA Plan

Before planning:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-plan.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the qa-plan workflow: read the branch specs, run the regression scan, resolve test targets with the user (or assume and note them when unattended), draft the human-runnable checklist, get approval unless unattended, and write qa-plan.md.
