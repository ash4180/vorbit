# Vorbit Implement Workflow

Use for feature work and bug fixes.

1. Load Vorbit durable rules before doing anything else.
2. Ground in the current codebase: find the closest existing implementation, test pattern, and interface shape.
3. Prefer TDD when the repo has an existing test harness.
4. Keep consistency over novelty: match project naming, imports, structure, and existing utilities.
5. For UI/design-driven work with a Figma source, fetch the primary node with `get_design_context`, capture a Figma reference screenshot, and write a structure/flow summary before coding: parent frame, selected node boundary, child blocks in render order, inside/outside scope, entry action, visible result, exit state.
6. Before UI coding, READ the FE architecture blueprint from the sub-issue body (produced by `/vorbit-epic`): mockup block -> Reuse/Adapt/Create matrix, component hierarchy, data/API contract, state ownership, design-system mapping, test seams. Do NOT rebuild it — that drifts from the plan. If the blueprint is missing or has gaps, ask before coding.
7. If the Figma structure, user flow, reuse/create choice, API/component boundary, missing exact node, or ticket/Figma conflict is unclear, ask before coding.
8. Implement against the source node, then capture a browser/app screenshot of the running result. Compare screenshots and fix visible mismatches unless explicitly out of scope.
9. Treat project-shared Vorbit rules as repo policy. Treat Gemini agent-local Vorbit rules as guidance for avoiding repeat Gemini mistakes.
10. Finish with verification against the changed behavior, screenshot evidence for UI work, and any acceptance criteria in the prompt or repo context.
