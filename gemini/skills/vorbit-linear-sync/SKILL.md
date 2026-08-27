---
name: vorbit-linear-sync
description: Use when the user asks to create a Linear ticket for the current branch work ("create ticket", "create the Linear ticket", "make a ticket") or to post or refresh its short human-readable Linear summaries. It reads the branch prd.md and epic.md, creates or updates one compact summary ticket per user story with progress and a pointer to the branch, and records ticket IDs back into prd.md. Tickets stay summaries; implementation detail lives only in the branch spec files. Requires Linear and an existing branch PRD; do not use to write the PRD or epic plan, implement code, or create engineering sub-issues.
---

# Vorbit Linear Sync

Before syncing:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/linear-sync.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the linear-sync workflow: read the branch spec files, compose one short summary ticket per story, get approval, create or update the Linear tickets, and record the mapping.
