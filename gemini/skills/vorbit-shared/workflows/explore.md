# Vorbit Explore Workflow

Use for lightweight idea exploration before PRD creation.

1. Load Vorbit durable rules before doing anything else.
2. Ask at least 10 questions in batches of 3-4. Probe core functionality, scale, user control, error handling, and constraints. Do NOT proceed until 10+ questions are asked.
3. Question quota gate: list every question asked with abbreviated answers. If fewer than 10, go back and ask more.
4. Analyze: summarize insights, identify root cause (not symptoms), propose 2-3 approaches with pros/cons/effort/risk, make a recommendation.
5. Draft exploration document in chat: Problem Statement, Context, Options (each with name/description/pros/cons/effort/risk), Recommendation, and PRD Handoff separating confirmed decisions from unresolved questions.
6. Get user confirmation before saving.
7. Save to a connected platform (Notion/Anytype) if requested and confirmed. Missing optional storage never blocks the exploration or approved chat draft.
8. Treat the exploration as decision input, never as the canonical PRD or an implementation plan. Carry unresolved decisions forward explicitly.
9. Report: URL/ID, recommendation, unresolved decisions, and next step (`$vorbit-prd [pasted PRD Handoff or local export]`) to create the canonical Linear spec ticket; retain the exploration URL as provenance.
