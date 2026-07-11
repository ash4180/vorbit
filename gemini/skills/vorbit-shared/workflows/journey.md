# Vorbit Journey Workflow

Use for creating user journey diagrams.

1. Load Vorbit durable rules before doing anything else.
2. Linear is the canonical PRD provider: resolve URL/ID, then scoped title search. Accept explicit pasted/local content as a labeled legacy fallback. Extract exact `US-###`, `US-###.AC-##`, `F#-S#`, branches, retries, loops, constraints, and TBDs.
3. Confirm only missing/conflicting flow details. Draft the complete ID-stable outline and `AC -> F#-S#` coverage ledger; get confirmation.
4. Before every `generate_diagram` call, load the installed Figma prerequisite whose unqualified name is `figma-generate-diagram` (use its catalog-qualified name). Follow its current flowchart guidance instead of copied limits; if unavailable, preserve the validated text flow and report `blocked_missing_capability`.
5. Preserve real loops and alternate/error paths. When dense, split into overview plus all cohesive detail flows, use explicit continuation/return IDs, reuse the first `fileKey`, and verify `AC -> step -> diagram/node` coverage. Never drop requirements to reduce node count.
6. Re-read and update the canonical Linear PRD with all FigJam URLs, covered ranges, Mermaid recovery source, and coverage ledger without overwriting other content. Legacy sources are reported, not falsely claimed as updated.
7. Report every diagram URL, source/update status, X/X AC and Y/Y step coverage, split map, and next steps.
