# Vorbit Epic Workflow

Use for transforming PRD user stories into Linear epics and sub-issues.

1. Load Vorbit durable rules before doing anything else.
2. Gather context: fetch the source PRD as a Linear ticket via `get_issue` (or by `list_issues` title-search if only a name was given), or gather requirements via conversation if no PRD ticket exists. Extract user stories (`US-*`), `AC-*` criteria, user flows, and any Figma/design source nodes. Lock the requirement baseline before codebase analysis.
   - UI/design sub-issues need exact Figma node IDs or explicit `TBD-design`.
   - If UI work says "match Figma" but has no exact node, or if ticket text conflicts with Figma, ask before creating implementation-ready issues.
3. Detect team's Linear setup: verify auth, list teams, get statuses/labels/projects. Keep calls scoped with `team` and `limit`.
4. Analyze codebase: find similar features, discover reusable code (search by usage first, then common dirs), discover constants, check for mock data, detect UI work, analyze Figma source nodes, map coupled file paths.
   - For UI/design work, fetch referenced Figma nodes with `get_design_context` and capture a reference screenshot.
   - Build a Figma structure/flow summary before planning UI tickets: parent frame, selected node boundary, child blocks in render order, inside/outside scope, entry action, visible result, exit state.
   - If the Figma structure or user flow is unclear, ask before creating implementation-ready issues.
   - Build an FE architecture blueprint before UI tickets: mockup block -> Reuse/Adapt/Create matrix, component hierarchy, data/API contract, state ownership, design-system mapping, test seams.
   - If reuse/create or API/component boundaries are unclear after code search, ask before creating implementation-ready issues.
   - Add screenshot verification to UI sub-issues: Figma reference screenshot before coding, browser/app screenshot after implementation, comparison notes for intentional differences or remaining mismatches.
5. Create technical plan (SDD): overview, flow impact matrix, design evidence matrix, FE architecture blueprint, PRD compliance check, data model, API, components, testing strategy, risks.
6. Get user approval before creating issues. Present plan and ask for concerns.
7. Plan epics: 1 User Story = 1 Epic. Each sub-issue includes: Why, Related Epic AC, Related Flow Steps, Reuse & Patterns, Design Source of Truth and Screenshot Evidence when UI/design-driven, File Changes, Acceptance Criteria, Test Criteria (TDD required).
8. Traceability gate: verify US → AC → Flow → sub-issue mapping, plus UI Flow → Figma node/screenshot mapping. Resolve gaps before creating.
9. Create in Linear: parent issue first, sub-issues with `parentId`. Use team's existing labels/states.
10. Report: parent URL, sub-issue count by priority, PRD link, implementation order (phased dependency tree).
