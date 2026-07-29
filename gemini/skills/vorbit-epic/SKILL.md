---
name: vorbit-epic
description: Use when the user asks to turn an approved branch PRD spec into an executable epic plan — one story section per user story with traceable ordered tasks written to the branch epic spec file — or to decompose an explicitly supplied technical scope (migration, upgrade, refactor) into a technical epic plan. It analyzes the codebase, presents the full topology for approval, then writes the plan file. Requires a branch PRD or explicit technical description; no Linear connection is needed. Do not use for generic sprint scheduling, writing the PRD, implementing code, or brainstorming.
---

# Vorbit Epic

Before creating issues:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/epic.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the epic workflow: gather PRD context, analyze codebase, create technical plan, and generate Linear issues.
