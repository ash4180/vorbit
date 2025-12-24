---
description: Generate UI prototype fast. Creates branch, components, mock data.
argument-hint: [feature name]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Create a prototype for: $ARGUMENTS

## SPEED IS PRIORITY

Skip documentation. Skip over-engineering. Generate working UI fast.

## Setup

1. Detect project framework:
   - package.json with react → React
   - package.json with vue → Vue
   - package.json with svelte → Svelte
   - No framework → vanilla HTML/CSS

2. Create branch:
   ```bash
   git checkout -b prototype/$ARGUMENTS
   ```

## Generate Prototype

### Analyze Existing Patterns

Scan codebase for:
- Component structure (where components live)
- Styling approach (CSS modules, Tailwind, styled-components)
- State management pattern
- API structure (for mock data shape)

### Create Components

For each screen/view in the flow:

1. Create component file matching project patterns
2. Use existing UI components if available
3. Add mock data (inline or JSON file)
4. Include basic interactivity

### Mock Data Strategy

Keep it simple - inline mocks or colocated JSON:

```typescript
// Inline mock (simplest)
const MOCK_USERS = [{ id: 1, name: "Test" }];

// Or colocated JSON file
import mockData from './mocks/users.json';
```

**Shape must match expected API response** for easy swap later.

## Rules

1. **Use existing components** - Don't recreate buttons, inputs, etc.
2. **Match project style** - Follow existing patterns exactly
3. **Simple mocks only** - Inline or JSON, no complex mock services
4. **Minimal code** - Just enough to demonstrate the flow
5. **No tests yet** - Tests come in implementation phase

## Output

Report:
- Branch name: `prototype/$ARGUMENTS`
- Files created (list paths)
- How to preview: (based on detected framework's dev command or open HTML file directly)
- **Mock data locations** (files/components with mock data)

Next:
- Review prototype with team
- `/vorbit:implement:epic` for implementation plan
- `/vorbit:implement:implement` to build real version
