# Vorbit PRD Workflow

Use for creating Product Requirements Documents.

1. Load Vorbit durable rules before doing anything else.
2. If a URL or existing doc is provided, fetch and restructure it into PRD format. If fetch fails, ask user to paste content.
3. Clarify requirements: ask a MAXIMUM of 3 rounds of questions. Focus on problem, users, scope, constraints, edge cases, and success metrics. Mark unknowns as `TBD` and ask.
4. Generate PRD draft with: Name (3-8 words), Description (max 100 chars), Problem (max 3 sentences, no tech), Users, User Stories with `AC-*` criteria, Assumptions, User Flows (Actor/Surface/Action/Result with Story/AC refs), Story-to-Flow Mapping, Constraints, Out of Scope, Success Criteria (with numbers).
5. User Flow rules: at least one flow required. Primary flow must include User, UI, and System actors. Use `Agent` only for distinct AI steps — not normal backend logic.
6. Show complete PRD in chat. Get user confirmation before saving.
7. Save to connected platform (Notion/Anytype) if user confirms.
8. Report: draft status, URL/ID, summary (X stories, Y criteria), next steps (`/vorbit-epic` or `/vorbit-journey`).
