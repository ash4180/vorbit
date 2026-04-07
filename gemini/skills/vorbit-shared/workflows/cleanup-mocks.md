# Vorbit Cleanup Mocks Workflow

Use for cleaning up mock data and generating API contract docs for backend handover.

1. Load Vorbit durable rules before doing anything else.
2. Load mock registry (`.claude/mock-registry.json`). If no registry, scan codebase for mock patterns: `**/mocks/*.json`, `**/mocks/*.ts`, `// TODO: Replace with real API`, `MOCK_` constants, hardcoded useState data, Zustand/Redux mock state.
3. For each mock: read content, infer endpoint from filename/location, generate API contract entry with endpoint, response shape, example response, consuming components.
4. Present complete API contract document for review. Get confirmation before proceeding.
5. Save API contract: append to PRD in Notion/Anytype, or create local file at `docs/api-contracts/[feature].md`.
6. Clean up: delete mock files, replace mock imports with API placeholders (`// TODO: Connect to real API`), replace hardcoded useState with empty/loading state, clean stores/context, update mock registry.
7. Report: contract save location, endpoints documented, files removed, files updated, next steps for backend.
