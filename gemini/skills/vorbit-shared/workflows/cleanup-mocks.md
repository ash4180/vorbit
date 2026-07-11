# Vorbit Cleanup Mocks Workflow

Use for cleaning up mock data and generating API contract docs for backend handover.

1. Load the Vorbit runtime contract and durable rules. Treat this as application-mock migration, never as test-fixture cleanup.
2. Read `../references/mock-registry.md`, then load and validate the resolved registry. If absent, scan only production source and exclude tests, fixtures, stories, seeds, examples, and static demo content. A hardcoded initial state is not a mock unless code evidence ties it to a temporary API substitute.
3. Inventory each candidate with its consumers and exact fields used. Treat any endpoint inferred from a filename as a proposal, not fact.
4. Draft a contract with method/path, auth, request, success/error shapes, field semantics, and consumers. Present the inventory and contract for approval before any external write or code deletion.
5. Save the approved contract to the canonical Linear PRD/specification ticket when available; otherwise create `docs/api-contracts/[feature].md`. Record the source mock paths and approved contract revision.
6. Preflight the real backend/API client. If it does not exist or required details remain unknown, stop with `needs_backend`; keep the working mocks and report the contract only.
7. When the real API is available, write integration tests, implement the repository-native client/adapter, and switch one integration boundary from mocks to the real path. Do not replace working behavior with `null`, empty state, or TODO placeholders.
8. Run focused and regression tests. Delete only mocks proven unused after the real path passes, then update the registry atomically.
9. Report contract location, integration evidence, files removed/updated, remaining mocks, and terminal status.
