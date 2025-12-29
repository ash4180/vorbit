---
description: Generate UI prototype fast. Creates page/feature with mock data.
argument-hint: [feature name]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*
---

Create a prototype for: $ARGUMENTS

Use the **prototype** skill for patterns and structure.

## SPEED IS PRIORITY

Skip documentation. Skip over-engineering. Generate working UI fast.

## Step 1: Detect Framework

Check `package.json`:
- `react` → React/TSX
- `vue` → Vue SFC
- `svelte` → Svelte
- None → Vanilla HTML/CSS

## Step 2: Analyze Existing Patterns

Scan codebase for:
- Where pages/routes live
- Component structure
- Styling approach (CSS modules, Tailwind, styled-components)
- Existing UI components to reuse

## Step 3: Create Prototype

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

For the feature:
1. Create page/route component matching project patterns
2. Create feature-specific components under the page folder
3. Create `mocks/` folder under the feature with JSON files
4. Compose using existing UI components (buttons, cards, inputs)

Structure:
```
src/pages/[Feature]/
├── index.tsx           # Main page
├── components/         # Feature-specific components
└── mocks/              # Mock data (delete when implementing real API)
    └── data.json       # Shape matches API response
```

## Mock Data Rules

- Mock folder under feature: `pages/Feature/mocks/`
- JSON filename = endpoint: `users.json` → `/api/users`
- Mock shape MUST match expected API response
- Add TODO comment: `// TODO: Replace with useSWR('/api/...')`
- Use realistic data (real names, valid emails)

## Report

```
Created:
- src/pages/Feature/index.tsx
- src/pages/Feature/components/...
- src/pages/Feature/mocks/...

Mock data (delete mocks/ when implementing real API):
- mocks/data.json → GET /api/...

Used existing components:
- [list]

Next: Review with team, then /vorbit:implement:epic
```
