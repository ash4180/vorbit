---
name: prototype
description: Reusable UI prototype patterns. Prototypes become production code - frontend swaps mocks for real API.
---

# Prototype Patterns

A prototype is a **page or feature** that frontend devs will reuse. They swap mocks for real API - that's it.

## What is a Prototype?

A prototype is:
- A **complete page or feature** users can interact with
- **Composition** of multiple components with clean props
- **Mock data** that defines the API contract
- **Reusable structure** - becomes production code

A prototype is NOT:
- A single reusable component (that's a component, not a prototype)
- Throwaway demo code
- Fully tested (tests come in implementation phase)

## Handover-Ready Structure

For frontend to reuse easily:
1. **Clean props** - Components receive data via props, not hardcoded
2. **Single mock location** - Each component imports mock in ONE place
3. **Props flow down** - Data flows through props, not scattered state
4. **Types match API** - Interfaces/types define expected API response

## Framework Detection

Check codebase before generating:

| Check | Framework | Generate |
|-------|-----------|----------|
| `package.json` has `react` | React | JSX/TSX pages |
| `package.json` has `vue` | Vue | SFC pages |
| `package.json` has `svelte` | Svelte | Svelte pages |
| `index.html` only | Vanilla | HTML + CSS + JS |

## Page/Feature Structure

**Keep it simple. Mock data under feature folder.**

```
src/
└── pages/                    # or routes/, views/
    └── [FeatureName]/
        ├── index.tsx         # Main page component
        ├── components/       # Feature-specific components
        │   ├── Header.tsx
        │   ├── List.tsx
        │   └── Form.tsx
        └── mocks/            # Mock data FOR THIS FEATURE
            └── data.json     # → swap to real API later
```

Or match existing codebase structure.

## Mock Data Strategy

**PURPOSE: Define data shape for backend. Easy handover to frontend.**

```
src/pages/UserDashboard/
├── index.tsx
├── components/
│   └── ActivityFeed.tsx
└── mocks/
    ├── users.json      # → GET /api/users
    └── activity.json   # → GET /api/activity
```

```typescript
// mocks/users.json - shows exact fields UI needs (API contract)
[
  { "id": "u1", "name": "Alice", "role": "admin" },
  { "id": "u2", "name": "Bob", "role": "member" }
]
```

```typescript
// MANDATORY: TODO comment after every mock import
import mockUsers from './mocks/users.json';
// TODO: Replace with real API
const users = mockUsers;
```

Rules:
- Mock folder lives inside feature folder: `pages/Feature/mocks/`
- One JSON file per API endpoint
- JSON filename indicates endpoint: `users.json` → `/api/users`
- Show only fields the UI actually uses
- **MANDATORY: TODO comment after every mock import**
- If multiple components need same data, share the mock file
- When implementing, delete entire `mocks/` folder

**DON'T over-engineer:**
- ❌ Add fields the UI doesn't use
- ❌ Create mock utilities, factories, or generators
- ❌ Duplicate same data in multiple mock files
- ❌ Skip the TODO comment

## Composition Pattern

A prototype page composes existing components + new feature components:

```tsx
// pages/UserDashboard/index.tsx
import { Layout } from '@/components/Layout';      // Existing
import { Card } from '@/components/ui/Card';       // Existing
import { UserStats } from './components/Stats';    // New for this feature
import { ActivityFeed } from './components/Feed';  // New for this feature
import mockActivity from './mocks/activity.json';
// TODO: Replace with real API

export function UserDashboard() {
  const activity = mockActivity;

  return (
    <Layout>
      <UserStats />
      <Card>
        <ActivityFeed items={activity} />
      </Card>
    </Layout>
  );
}
```

## Prototype Checklist

**Before coding:**
- [ ] Analyzed codebase patterns (pages, components, styling)
- [ ] Asked user about layout, fields, actions, empty states
- [ ] Did NOT invent features user didn't request

**Structure:**
- [ ] Framework detected from codebase
- [ ] Page structure matches existing patterns
- [ ] **Components receive data via props (not hardcoded)**
- [ ] **Mock import in ONE place per component**
- [ ] Composes existing UI components (buttons, cards, inputs)

**Mocks:**
- [ ] Mock data under feature folder: `pages/Feature/mocks/`
- [ ] Mock shows only fields UI actually uses
- [ ] **Every mock import has `// TODO: Replace with real API` comment**
- [ ] Components needing same data share the same mock file

**Final:**
- [ ] Page is navigable/renderable

## Output Format

When creating prototype, report:
```
Created:
- src/pages/Feature/index.tsx (main page)
- src/pages/Feature/components/List.tsx
- src/pages/Feature/components/Form.tsx
- src/pages/Feature/mocks/items.json

Mock data (delete mocks/ folder when implementing real API):
- mocks/items.json → GET /api/items

Used existing components:
- Layout, Card, Button, Input

Next: Review with team, then /vorbit:implement:epic
```

## Rules

1. **Ask before building** - Clarify layout, fields, actions, empty states
2. **No invented features** - Don't add search/filter/tabs/pagination unless asked
3. **Analyze codebase first** - Find patterns before writing any code
4. **Handover-ready** - Frontend swaps mocks for API, keeps everything else
5. **Clean props** - Data via props, not hardcoded in components
6. **Single mock location** - One import per component, easy to find/replace
7. **Reuse existing components** - Don't recreate buttons, cards, inputs
8. **Match project style** - Follow existing naming and structure
9. **Mocks under feature** - `pages/Feature/mocks/` not global
10. **No tests yet** - Tests come in implementation phase
