---
name: vorbit-ticket
description: Use when the user asks to create a Linear ticket for the current branch work ("create ticket", "create the Linear ticket", "make a ticket") or to post or refresh its short human-readable Linear summaries, or to update the branch's existing ticket when requirements change. It reads the branch prd.md and epic.md, creates or updates one compact summary ticket per user story with its goal and acceptance criteria, and records ticket IDs back into prd.md. When the branch plan was made from an existing ticket, it edits only that ticket's changed lines after a before-and-after preview. Tickets stay summaries; implementation detail lives only in the branch spec files. Requires Linear and a branch PRD or a plan made from a ticket; do not use to write the PRD or epic plan, implement code, or create engineering sub-issues.
---

# Vorbit Ticket

Before syncing:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/ticket.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the ticket workflow: read the branch spec files, compose one short summary ticket per story, get approval, create or update the Linear tickets, and record the mapping.
