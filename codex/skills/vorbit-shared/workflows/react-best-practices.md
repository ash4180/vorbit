# Vorbit React Best Practices Workflow

Use when writing, reviewing, or refactoring React/Next.js code.

1. Load the Vorbit runtime contract and durable rules. This is conditional supporting guidance, not authorization for unrelated refactoring.
2. Inspect React/Next versions, runtimes, existing libraries, and the actual bottleneck before selecting a rule. Do not install a library merely because it appears in guidance.
3. Priority 1 — Eliminate proven waterfalls: defer work until needed, use `Promise.all()` only for independent operations, start independent promises early, and use existing streaming/Suspense patterns where supported.
4. Priority 2 — Bundle size: prefer direct imports when the package supports them, lazy-load genuinely heavy non-critical code with the repository's framework mechanism, and preload only from user intent.
5. Priority 3 — Server-side: use runtime-supported request deduplication; add cross-request caches only with explicit freshness, invalidation, and resource bounds; minimize unnecessary server/client serialization.
6. Priority 4 — Client data: reuse the project's data library, lazy-initialize expensive state, subscribe narrowly, and use transitions only for genuinely non-urgent updates.
7. Priority 5 — Re-render optimization: prefer composition and moving state down before adding memoization.
8. Priority 6 — Rendering: consider `content-visibility` for measured long-list cost; use established SSR-safe hydration patterns; inline scripts require CSP/security review.
9. Priority 7 — JS patterns: optimize repeated hot-path lookups when evidence warrants it; avoid mutating shared arrays and check target support before `toSorted()`.
10. Verify behavior first and capture a meaningful before/after signal for performance-only changes when practical.
