---
name: vorbit-qa-plan
description: Use when the user asks to build or update a QA test plan for the current branch — a human-runnable checklist covering story flows, edge cases and error paths, device and browser coverage, regression risks, and performance checks, drafted from the branch prd.md and epic.md and written to the branch spec folder. Requires the branch PRD; do not use for agent-run acceptance validation (that is verify), writing requirements, or implementing fixes.
---

# Vorbit QA Plan

Before planning:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/qa-plan.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the qa-plan workflow: read the branch specs, resolve test targets with the user, draft the human-runnable checklist, get approval, and write qa-plan.md.
