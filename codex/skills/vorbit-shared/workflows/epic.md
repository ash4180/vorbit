# Vorbit Epic Workflow

Use for transforming PRD user stories into Linear implementation-parent trees.

1. Load Vorbit durable rules before doing anything else.
2. Gather context: Linear is canonical. Fetch the PRD spec ticket via `get_issue` (or scoped `list_issues` title search). Confirm an ID-only normalization for legacy Linear specs; accept explicit pasted/local PRDs only as legacy fallbacks and include creation/import of the canonical Linear spec ticket in approval. Without either artifact, stop and run PRD first.
3. Lock `US-### -> US-###.AC-## -> F#-S#` before codebase analysis. Block if an implementation-affecting TBD can change behavior, contracts, issue boundaries, dependencies, files, or tests; only explicitly non-blocking TBDs may remain.
4. Detect team's Linear setup: verify auth, list teams, get statuses/labels/projects. Keep calls scoped with `team` and `limit`.
5. Analyze codebase: find similar features, discover reusable code (usage first), constants, mock data, UI patterns, and coupled paths.
6. Create the SDD and show the deterministic topology: PRD spec -> exactly one implementation parent per user story -> at least one executable child per parent -> that parent's own order. Each issue includes honest test criteria, with tests-first only when the repository has a runnable harness. Get approval.
7. Traceability gate: verify each US has one parent, each exact AC maps to flow/reason, each in-scope flow maps to a child under the correct parent, and all remaining TBDs are non-blocking.
8. Create/import the PRD spec if needed. Use `(PRD ID, US-###)` and stable planned child IDs/titles as idempotency keys; lookup and resume before create. Then, in PRD order, create one top-level implementation parent per story, its children with `parentId`, and persist only those child IDs in that parent's `## Implementation Order`.
9. Re-fetch and verify every parent tree, then preserve the PRD description while adding an `## Implementation Parents` index (`US-### -> parent ID/URL`).
10. Report the canonical PRD URL, **all** implementation parent URLs in story order, per-parent child counts/orders, and topology totals.
