# Vorbit Prototype Workflow

Use for creating UI prototypes with mock data that become production code.

1. Load Vorbit durable rules before doing anything else.
2. Discovery: fetch PRD/Figma design if provided. If purpose unclear, ask.
3. Codebase analysis (before writing any code): detect framework, pages location, styling approach, existing UI components. Report findings and confirm with user.
4. Requirements clarification: if Figma provided, use as source of truth. Otherwise ask about layout, data fields, actions, empty states. Don't invent features.
5. Build prototype: create page structure matching codebase patterns. Components receive data via props (not hardcoded). Mock data under feature folder. Every mock import has `// TODO: Replace with real API`. Register mocks in `.claude/mock-registry.json`.
6. Verification: components use props, mock imports in one place, TODO comments present, existing UI components reused, matches codebase patterns.
7. Report: files created, mocks registered, existing components used, next steps (`/vorbit-epic` or `/vorbit-cleanup-mocks`).
