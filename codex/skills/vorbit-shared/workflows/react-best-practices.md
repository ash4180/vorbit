<!-- GENERATED from skills/react-best-practices/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-react-best-practices` skill directory (a sibling of `vorbit-shared`).

# React Best Practices

Read and follow `../references/execution-contract.md` before applying this policy.

## Overview

Performance heuristics for React and Next.js applications. Treat every rule as conditional on the repository's React/Next version, runtime, existing dependencies, and measured or clearly evidenced bottleneck.

## When to Apply

Before applying a rule:

1. inspect the framework/runtime version and existing data/cache libraries;
2. confirm the rule targets the actual code path;
3. prefer structural fixes over new dependencies;
4. verify behavior and, for performance-only changes, capture a meaningful before/after signal when practical.

Do not add SWR, `better-all`, an LRU package, or any other dependency merely because it appears below.

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Eliminating Waterfalls | CRITICAL |
| 2 | Bundle Size Optimization | CRITICAL |
| 3 | Server-Side Performance | HIGH |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH |
| 5 | Re-render Optimization | MEDIUM |
| 6 | Rendering Performance | MEDIUM |
| 7 | JavaScript Performance | LOW-MEDIUM |
| 8 | Advanced Patterns | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Eliminate Waterfalls:**
- Defer await until needed (move into branches)
- Use `Promise.all()` for independent async operations
- Start promises early, await late
- Restructure partial dependencies with existing primitives; use `better-all` only if the repository already depends on it
- Use Suspense boundaries to stream content

**Reduce Bundle Size:**
- Avoid barrel file imports (import directly from source)
- Use the framework's existing lazy/dynamic loading mechanism for genuinely heavy, non-critical components
- Defer non-critical third-party libraries
- Preload based on user intent

### High-Impact Server Patterns

- Use the runtime-supported request cache for repeated request-local work
- Add cross-request caching only with explicit freshness, invalidation, and resource bounds
- Minimize serialization at RSC boundaries
- Parallelize data fetching with component composition

### Medium-Impact Client Patterns

- Reuse the project's client data library for request deduplication
- Defer state reads to usage point
- Use lazy state initialization for expensive values
- Use derived state subscriptions
- Apply `startTransition` for non-urgent updates

### Rendering Patterns

- Animate SVG wrappers, not SVG elements directly
- Use `content-visibility: auto` for long lists
- Prevent hydration mismatch using the repository's established SSR-safe pattern; inline scripts require a security/CSP review
- Use explicit conditional rendering (`? :` not `&&`)

### JavaScript Patterns

- Batch DOM CSS changes via classes
- Build index maps for repeated lookups
- Cache repeated function calls
- Avoid mutating shared arrays; use `toSorted()` only when the target runtime supports it
- Early length check for array comparisons

## References

Full documentation with code examples is available in:

- `references/react-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, search `references/rules/` for the relevant category.
