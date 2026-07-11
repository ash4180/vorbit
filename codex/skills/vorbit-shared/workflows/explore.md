# Vorbit Explore Workflow

Use for lightweight idea exploration before PRD creation.

1. Load Vorbit durable rules before doing anything else.
2. Ask targeted questions until every PRD-blocking unknown is answered or explicitly parked. Probe core functionality, scale, user control, error handling, and constraints; size batches to what the user can answer comfortably.
3. Before analyzing, list each question asked with its answer, then list the unknowns still open; carry open unknowns into the PRD Handoff as unresolved decisions instead of filling them with assumptions.
4. Analyze: summarize insights, identify root cause (not symptoms), propose 2-3 approaches with pros/cons/effort/risk, make a recommendation.
5. Draft exploration document in chat: Problem Statement, Context, Options (each with name/description/pros/cons/effort/risk), Recommendation, and PRD Handoff separating confirmed decisions from unresolved questions.
6. Get user confirmation before saving.
7. Save to a connected platform (Notion/Anytype) if requested and confirmed. Missing optional storage never blocks the exploration or approved chat draft.
8. Treat the exploration as decision input, never as the canonical PRD or an implementation plan. Carry unresolved decisions forward explicitly.
9. Report: URL/ID, recommendation, unresolved decisions, and next step (`$vorbit-prd [pasted PRD Handoff or local export]`) to create the canonical Linear spec ticket; retain the exploration URL as provenance.
