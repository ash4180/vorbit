---
name: vorbit-implement-loop
description: Use only when the user explicitly invokes loop mode, supplies --loop or --cancel, or asks to autonomously work through an ordered Linear epic or sub-issue queue. After one queue confirmation it changes code, runs tests, updates Linear statuses, and reports progress in the session until completion. Loop execution requires a Linear issue; do not use for a one-off implementation, issue planning, or unattended work without explicit loop intent.
---

# Vorbit Implement Loop

Before looping:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/implement-loop.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the loop workflow: parse args, build work queue from Linear, iterate through sub-issues, update Linear status on each completion.
