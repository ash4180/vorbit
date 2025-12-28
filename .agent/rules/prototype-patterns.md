# Prototype Patterns

Patterns for generating fast UI prototypes with mock data.

## What is a Prototype?

A prototype is:
* A **complete page or feature** users can interact with
* **Composition** of multiple components
* **Mock data** that mirrors real API shapes
* **Functional** enough to demo the flow

A prototype is NOT:
* A single reusable component
* Production-ready code
* Fully tested implementation

## Framework Detection

Check codebase before generating:
* `package.json` has `react` → Generate JSX/TSX pages
* `package.json` has `vue` → Generate SFC pages
* `package.json` has `svelte` → Generate Svelte pages
* `index.html` only → Generate HTML + CSS + JS

## Page/Feature Structure

Keep it simple. Mock data under feature folder.

```
src/
└── pages/                    # or routes/, views/
    └── [FeatureName]/
        ├── index.tsx         # Main page component
        ├── components/       # Feature-specific components
        └── mocks/            # Mock data FOR THIS FEATURE
            └── data.json     # → swap to real API later
```

Or match existing codebase structure.

## Mock Data Strategy

* Mock folder lives inside feature folder: `pages/Feature/mocks/`
* One JSON file per API endpoint the feature uses
* JSON filename indicates endpoint: `users.json` → `/api/users`
* Use realistic data (real names, valid emails, proper IDs)
* Add TODO comment showing the real API call
* When implementing real feature, delete entire `mocks/` folder

## Prototype Rules

1. **Reuse existing components** - Don't recreate buttons, cards, inputs
2. **Match project style** - Follow existing naming and structure
3. **Mocks under feature** - `pages/Feature/mocks/` not global
4. **Complete page** - User can navigate to and interact with it
5. **No tests yet** - Tests come in implementation phase
6. **Minimal dependencies** - Don't add packages unless necessary

## Output Format

When creating prototype, report:
```
Created:
- src/pages/Feature/index.tsx (main page)
- src/pages/Feature/components/List.tsx
- src/pages/Feature/mocks/items.json

Mock data (delete mocks/ folder when implementing real API):
- mocks/items.json → GET /api/items

Used existing components:
- Layout, Card, Button, Input
```
