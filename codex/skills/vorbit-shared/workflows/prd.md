# Vorbit PRD Workflow

Use for creating a Linear ticket from a product requirement.

1. Load Vorbit durable rules before doing anything else.
2. If a URL or existing doc is provided, fetch and restructure it into the PRD format below. If fetch fails, ask the user to paste the content and continue.
3. Clarify requirements: MAXIMUM 3 rounds of questions. Focus on problem, users, scope, constraints, edge cases, and success metrics. Mark unknowns as `TBD` and ask a question for every `TBD`.
4. Generate the PRD draft with these sections, in this order:
   - Feature name (H1, 3-8 words, no jargon) — becomes the Linear ticket title.
   - `## Description`: 1-2 short sentences.
   - `## Problem`: 1-2 short paragraphs, no tech detail.
   - `## User Stories`: `US-001`, `US-002`, ... each with `As a [user], I want [goal], so [benefit]` and `- [ ] AC-1`, `- [ ] AC-2`, ... checkboxes.
   - `## User Flows`: at least one happy flow in prose form. Use `**Entry:** [Start] → [Step] → [Step] → **Exit:** [End]`. Add separate flows for alternate or error paths.
   - `## Constraints`: limits the implementation must respect.
   - `## Success Criteria`: measurable with real numbers.
5. `TBD` is never allowed in Problem, Users, or User Stories.
6. Show the complete PRD in chat. Get user confirmation before creating the ticket.
7. Create the ticket via the Linear MCP: verify auth, pick team and project (ask if multiple), then call `save_issue` with `title` = the H1 line, `team` and `project` as name strings, and `description` = the full PRD body starting at `## Description`.
8. Report: ticket URL, team and project used, summary (X stories, Y flows, Z criteria), and the suggested next step (epic breakdown or journey diagram).
