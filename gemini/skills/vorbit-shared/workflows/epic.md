# Vorbit Epic Workflow

Use for transforming PRD user stories into Linear epics and sub-issues.

1. Load Vorbit durable rules before doing anything else.
2. Gather context: fetch PRD from Notion/Anytype or conversation. Extract user stories, `AC-*` criteria, user flows, and story-to-flow mapping. Lock requirement baseline before codebase analysis.
3. Detect team's Linear setup: verify auth, list teams, get statuses/labels/projects. Keep calls scoped with `team` and `limit`.
4. Analyze codebase: find similar features, discover reusable code (search by usage first, then common dirs), discover constants, check for mock data, detect UI work, map coupled file paths.
5. Create technical plan (SDD): overview, flow impact matrix, PRD compliance check, data model, API, components, testing strategy, risks.
6. Get user approval before creating issues. Present plan and ask for concerns.
7. Plan epics: 1 User Story = 1 Epic. Each sub-issue includes: Why, Related Epic AC, Related Flow Steps, Reuse & Patterns, File Changes, Acceptance Criteria, Test Criteria (TDD required).
8. Traceability gate: verify US → AC → Flow → sub-issue mapping. Resolve gaps before creating.
9. Create in Linear: parent issue first, sub-issues with `parentId`. Use team's existing labels/states.
10. Report: parent URL, sub-issue count by priority, PRD link, implementation order (phased dependency tree).
