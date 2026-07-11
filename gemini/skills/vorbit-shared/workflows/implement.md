# Vorbit Implement Workflow

Use for feature work and bug fixes.

1. Load the Vorbit runtime contract and durable rules before doing anything else.
2. Resolve one implementation target. For a Linear ID/URL, preflight the current Linear connector, fetch the issue, parent implementation issue, and linked PRD, then record the source update timestamp. For a complete local description, do not require Linear.
3. If loop mode is requested, delegate queue ownership to `vorbit-implement-loop`; normal implementation owns one issue only.
4. Reject implementation-affecting `TBD`s. Map the target to its `US-*`, `US-*.AC-*`, and `F*-S*` identifiers when present.
5. Ground in the current codebase: find the closest implementation, call sites, test pattern, and interface shape before editing. Reuse existing code; do not create a duplicate to satisfy a stale ticket path.
6. Treat repository instructions and project rules as policy. Treat Gemini-local rules and UI/performance skills as conditional guidance that cannot replace the repository's established stack.
7. When a runnable test harness exists, write or update a focused test first and observe the expected failure. If no honest test surface exists, agree on a real verification method instead of inventing a cheater test.
8. Keep the change within the selected issue. Do not add frontend/backend counterparts, abstractions, or unrelated cleanup unless the acceptance criteria require them.
9. If temporary application mocks are required, keep them behind one feature boundary and register that boundary using `../references/mock-registry.md`; test fixtures are excluded. Then verify the changed behavior, likely regressions, and every mapped AC. Registered prototype mocks may remain; unregistered placeholders may not.
10. Implementation sub-issues may move to Done after their own ACs pass. Keep the implementation parent In Progress until a PR exists. Report evidence and the next allowed transition.
