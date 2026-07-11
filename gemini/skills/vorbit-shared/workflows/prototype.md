# Vorbit Prototype Workflow

Use for creating UI prototypes with mock data that become production code.

1. Load Vorbit durable rules before doing anything else.
2. Discovery: fetch canonical PRD context from Linear by URL/ID or scoped title search; accept explicit pasted/local PRDs only as labeled legacy fallbacks. Extract exact US/AC/flow IDs and constraints. Fetch optional Figma design separately. If purpose is unclear, ask.
3. Codebase analysis (before writing any code): detect framework, pages location, styling approach, existing UI components. Report findings and confirm with user.
4. Requirements clarification: if Figma is provided, use it as the visual source of truth only; Linear remains canonical for behavior/scope. Otherwise ask about layout, data fields, actions, and empty states. Don't invent features.
5. Build prototype: create page structure matching codebase patterns. Use exactly one feature-level mock integration boundary; only it imports all feature mocks and carries the replacement TODO. Presentational components receive typed props and never import mocks. Read `../references/mock-registry.md`, resolve the runtime's `storage_root` and `project_slug` without reconstructing them, and register that boundary with schema 1.1. Never use an agent-specific directory.
6. Verification: reuse the project's test/router patterns. Run a narrow smoke test proving the route renders primary content and real router/navigation reaches it, then relevant typecheck/build. If no harness exists, smoke the real local app; do not install a framework just for this.
7. Report: canonical PRD URL/provenance, files, single boundary, mocks, reused components, exact smoke commands/results, next steps (`$vorbit-epic` or `$vorbit-cleanup-mocks`).
