# Vorbit Implement Workflow

Use for feature work and bug fixes.

1. Load Vorbit durable rules before doing anything else.
2. Ground in the current codebase: find the closest existing implementation, test pattern, and interface shape.
3. Prefer TDD when the repo has an existing test harness.
4. Keep consistency over novelty: match project naming, imports, structure, and existing utilities.
5. Treat project-shared Vorbit rules as repo policy. Treat Gemini agent-local Vorbit rules as guidance for avoiding repeat Gemini mistakes.
6. Finish with verification against the changed behavior and any acceptance criteria in the prompt or repo context.
