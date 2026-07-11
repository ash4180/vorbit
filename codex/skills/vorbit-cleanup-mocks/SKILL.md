---
name: vorbit-cleanup-mocks
description: Use only when the user explicitly asks to remove registered prototype or implementation mock data for backend handoff. It reviews an existing mock registry, drafts an API contract for approval, and removes mocks only after a real backend integration passes; otherwise it preserves them and reports needs_backend. Requires a project with tracked mocks; do not use for creating mocks, deleting test fixtures, or general code cleanup.
---

# Vorbit Cleanup Mocks

Before cleaning up:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/cleanup-mocks.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Then follow the cleanup workflow: load registry, generate API contracts, save to PRD, remove mocks, report.
