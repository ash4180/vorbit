# Codebase Coverage Audit

How to audit a codebase to discover what needs testing.

## Step 1: Detect Framework

| Framework | Indicators |
|---|---|
| React (Vite) | `vite.config.ts`, `src/App.tsx` |
| React (CRA) | `react-scripts` in package.json |
| Next.js | `next.config.js`, `pages/` or `app/` |
| Vue | `vue.config.js`, `.vue` files |
| Svelte | `svelte.config.js` |
| Angular | `angular.json` |
| Express/Fastify | `server.ts`, `app.ts` with route handlers |
| Django | `urls.py`, `views.py` |
| Rails | `config/routes.rb` |

## Step 2: Route Discovery

### React Router (most common for React SPAs)

1. Search for route definitions:
   ```
   Grep: "Route.*path=" or "createBrowserRouter" or "useRoutes"
   ```
2. Read the main router file (usually `App.tsx` or `routes.tsx`)
3. Extract all `path` values — these are the testable URLs
4. Note nested routes (layout routes that wrap children)

### Next.js

1. Glob: `pages/**/*.tsx` or `app/**/page.tsx`
2. Each file = one route (file-based routing)

### Other frameworks

Search for route registration patterns in the framework's docs.

## Step 3: Page Component Inventory

```bash
# Count page components
find src/pages -name "*.tsx" -o -name "*.ts" | wc -l

# Count sub-components within pages
find src/pages/**/components -name "*.tsx" | wc -l
```

Glob equivalents:
- `src/pages/**/*.tsx` — all page files
- `src/pages/**/components/**/*.tsx` — page-local components

## Step 4: Shared Component Inventory

```bash
# UI primitives
find src/components/ui -name "*.tsx" | wc -l

# Compositions (higher-level combined components)
find src/compositions -name "*.tsx" | wc -l
```

## Step 5: Utility Inventory

```bash
find src/utils -name "*.ts" | wc -l
find src/hooks -name "*.ts" | wc -l
find src/stores -name "*.ts" | wc -l
```

## Step 6: Existing Test Detection

```bash
# Test files
find src -name "*.test.*" -o -name "*.spec.*" | wc -l

# Test directories
find src -type d -name "__tests__"
```

Also check:
- Test framework: look for `vitest`, `jest`, `cypress`, `playwright` in package.json
- Test config: `vitest.config.ts`, `jest.config.ts`, `cypress.config.ts`, `playwright.config.ts`
- Coverage config: look for `c8`, `istanbul`, `v8` coverage settings

## Step 7: Navigation/Sidebar Discovery

Search for sidebar or navigation configuration:

```
Grep: "sidebar" or "navigation" or "menuItems" or "navItems"
```

Common locations:
- `src/constants.ts` — static nav config
- `src/layouts/` — sidebar component with nav items
- `src/config/navigation.ts`

The sidebar defines what users actually SEE — it's the primary input for feature area grouping.

## Step 8: Compile Audit Summary

```markdown
## Codebase Audit Summary

| Category | Count |
|---|---|
| Routes | X |
| Pages (top-level) | Y |
| Page sub-components | Z |
| Shared components | A |
| Compositions | B |
| Utilities | C |
| Custom hooks | D |
| State stores | E |
| Test files | F |
| **Test coverage** | **F/(Y+Z+A+B+C+D+E) = N%** |

### Test Framework
- Runner: [Vitest/Jest/etc.]
- UI testing: [React Testing Library/Enzyme/etc.]
- E2E: [Playwright/Cypress/None]

### Feature Areas (from sidebar)
1. [Area name] — X routes, Y pages
2. [Area name] — X routes, Y pages
...

### Hidden Routes (no sidebar entry)
- `/path` — [description if determinable]

### Test Gaps
- Feature areas with 0 test files: [list]
- Utility files with no corresponding test: [list]
```

## Common Patterns by Tech Stack

### React + tRPC + TanStack Query
- API layer: `utils/trpcClient.ts`
- Type definitions: auto-generated from server
- Query hooks: via tRPC integration with TanStack Query
- Testing: mock tRPC responses, test query states (loading, error, success)

### React + REST + Axios/Fetch
- API layer: `services/` or `api/` directory
- Testing: MSW (Mock Service Worker) for API mocking

### Next.js
- API routes: `pages/api/` or `app/api/`
- Server components: test data fetching separately
- Client components: standard React testing
