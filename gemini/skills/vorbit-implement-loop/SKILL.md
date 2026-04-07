---
name: vorbit-implement-loop
description: Use when the user wants to iterate autonomously through sub-issues, run implement in loop mode, or auto-continue through an epic's work queue.
---

# Vorbit Implement Loop

Before looping:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/implement-loop.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the loop workflow: parse args, build work queue from Linear, iterate through sub-issues, update Linear status on each completion.
