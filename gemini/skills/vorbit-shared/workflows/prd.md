# Vorbit PRD Workflow

Use for creating a Linear ticket from a product requirement.

1. Load Vorbit durable rules before doing anything else.
2. Gather context without blocking greenfield drafting. If the user supplies a Linear URL/ID, fetch it as canonical; use scoped title search only when locating an existing PRD. Accept pasted content or an explicit local file as a labeled legacy import, and ask for pasted/exported content when another URL is inaccessible. Otherwise use the conversation or fresh feature request directly. Do not require an existing Linear ticket to draft; Linear becomes canonical only after the approved creation step.
3. Clarify requirements in batched rounds; when unknowns remain after a few rounds, park them as classified TBDs rather than continuing to interrogate. Focus on problem, users, scope, constraints, edge cases, and success metrics. Every factual requirement and numeric target must trace to user input, a cited source artifact, or a durable rule. Number unknowns `TBD-###`, ask a question for every one, and classify any remainder as implementation-affecting or non-blocking. Do not invent privacy, persistence, retention, permissions, exclusions, or metric targets.
4. Generate the PRD draft with these sections, in this order:
   - Feature name (H1, 3-8 words, no jargon) — becomes the Linear ticket title.
   - `## Description`: 1-2 short sentences.
   - `## Problem`: 1-2 short paragraphs, no tech detail.
   - `## User Stories`: `US-001`, `US-002`, ... each with `As a [user], I want [goal], so [benefit]` and globally unique story-scoped ACs (`US-001.AC-01`, `US-001.AC-02`, ...).
   - `## User Flows`: at least one happy flow. Number every step (`F1-S1`, `F1-S2`, ...), name surface/action/visible result, preserve branches and loops, and put exact AC IDs in each step's `Covers` list.
   - `## Constraints`: limits the implementation must respect.
   - `## Success Criteria`: measurable with confirmed, sourced numbers; use classified `TBD-###` placeholders when targets are unknown.
   - `## Open Questions`: every unresolved assumption or target, its source/question attempt, and impact classification.
5. `TBD` is never allowed in Problem, Users, or User Stories. Never promote an inference into a constraint merely to remove a TBD. Before confirmation, verify all US/AC/flow IDs are unique and every AC is covered by at least one `F#-S#`.
6. Show the complete PRD in chat. If the user requested draft/review only, stop without a creation prompt or Linear call; report `needs_input` when an implementation-affecting TBD remains, otherwise `completed`. For creation requests, get explicit user confirmation and resolve implementation-affecting TBDs before creating the ticket.
7. Create the ticket via the current Linear connector: verify auth, pick team/project, inspect the available tool schemas, and call the operation whose schema explicitly creates an issue. Pass title, full PRD description, team, and project exactly as that schema requires; do not assume `save_issue` or any unverified alias.
8. Report: canonical ticket URL, legacy import provenance if any, team/project, summary (X stories, Y flows, Z criteria), and the suggested next step (epic breakdown or journey diagram).
