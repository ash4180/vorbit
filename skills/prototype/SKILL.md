---
name: prototype
description: Fast UI prototype patterns. Use when generating page/feature prototypes with mock data.
---

# Prototype Patterns

Patterns for generating fast UI prototypes. A prototype is a **page or feature** (not just a component) that combines multiple components with mock data.

## What is a Prototype?

A prototype is:
- A **complete page or feature** users can interact with
- **Composition** of multiple components
- **Mock data** that mirrors real API shapes
- **Functional** enough to demo the flow

A prototype is NOT:
- A single reusable component
- Production-ready code
- Fully tested implementation

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

**Mock data under feature folder = easy to find and replace.**

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
// mocks/users.json - matches GET /api/users
[
  { "id": "u1", "name": "Alice Chen", "email": "alice@example.com", "role": "admin" },
  { "id": "u2", "name": "Bob Smith", "email": "bob@example.com", "role": "member" }
]
```

```typescript
// In page component
import mockUsers from './mocks/users.json';

// TODO: Replace with useSWR('/api/users')
const users = mockUsers;
```

Rules:
- Mock folder lives inside feature folder: `pages/Feature/mocks/`
- One JSON file per API endpoint the feature uses
- JSON filename indicates endpoint: `users.json` → `/api/users`
- Use realistic data (real names, valid emails, proper IDs)
- Add TODO comment showing the real API call
- When implementing real feature, delete entire `mocks/` folder

## Composition Pattern

A prototype page composes existing components + new feature components:

```tsx
// pages/UserDashboard/index.tsx
import { Layout } from '@/components/Layout';      // Existing
import { Card } from '@/components/ui/Card';       // Existing
import { UserStats } from './components/Stats';    // New for this feature
import { ActivityFeed } from './components/Feed';  // New for this feature
import mockActivity from './mocks/activity.json'; // Mock under feature

export function UserDashboard() {
  // TODO: Replace with useSWR('/api/activity')
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

- [ ] Framework detected from codebase
- [ ] Page structure matches existing patterns
- [ ] Composes existing UI components (buttons, cards, inputs)
- [ ] New feature-specific components created
- [ ] Mock data under feature folder: `pages/Feature/mocks/`
- [ ] Mock data shape matches expected API
- [ ] TODO comments mark mock → real swaps
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

1. **Reuse existing components** - Don't recreate buttons, cards, inputs
2. **Match project style** - Follow existing naming and structure
3. **Mocks under feature** - `pages/Feature/mocks/` not global
4. **Complete page** - User can navigate to and interact with it
5. **No tests yet** - Tests come in implementation phase
6. **Minimal dependencies** - Don't add packages unless necessary
