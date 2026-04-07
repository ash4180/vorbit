# Vorbit React Best Practices Workflow

Use when writing, reviewing, or refactoring React/Next.js code.

1. Load Vorbit durable rules before doing anything else.
2. Priority 1 — Eliminate waterfalls (CRITICAL): defer await until needed, use `Promise.all()` for independent ops, start promises early/await late, use Suspense boundaries.
3. Priority 2 — Bundle size (CRITICAL): avoid barrel file imports (import from source), use `next/dynamic` for heavy components, defer non-critical third-party libs, preload on user intent.
4. Priority 3 — Server-side (HIGH): use `React.cache()` for per-request dedup, LRU cache for cross-request, minimize serialization at RSC boundaries, parallelize data fetching with component composition.
5. Priority 4 — Client data fetching (MEDIUM-HIGH): use SWR for auto dedup, defer state reads to usage point, lazy state initialization, derived state subscriptions, `startTransition` for non-urgent updates.
6. Priority 5 — Re-render optimization (MEDIUM): composition over memoization, move state down, extract expensive children.
7. Priority 6 — Rendering (MEDIUM): `content-visibility: auto` for long lists, prevent hydration mismatch with inline scripts, explicit conditional rendering (`? :` not `&&`).
8. Priority 7 — JS patterns (LOW-MEDIUM): batch DOM CSS via classes, build index maps for repeated lookups, `toSorted()` over `sort()`, early length check for array comparisons.
