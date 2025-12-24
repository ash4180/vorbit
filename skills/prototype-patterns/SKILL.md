---
name: Prototype Patterns
description: This skill provides patterns for generating fast UI prototypes. Use when creating prototype components, analyzing codebase patterns, or setting up mock data that mirrors real API shapes.
---

## Purpose

Generate working UI prototypes fast by following existing codebase patterns. Simple mocks now, real API during implementation.

## Prototype Structure

| Step | Action | Output |
|------|--------|--------|
| Detect | Scan package.json/config | Framework identified |
| Analyze | Find existing patterns | Component/style structure |
| Generate | Create prototype files | Working UI code |
| Mock | Add inline or JSON mocks | Data matching API shape |

## Framework Detection

| File | Framework |
|------|-----------|
| `package.json` with `react` | React |
| `package.json` with `vue` | Vue |
| `package.json` with `svelte` | Svelte |
| `package.json` with `next` | Next.js |
| No framework deps | Vanilla HTML/CSS |

## Core Rules

1. **USE existing components** - Don't recreate UI primitives
2. **MATCH project style** - Follow patterns exactly
3. **SIMPLE mocks** - Inline or JSON file, no complex mock services
4. **MINIMAL code** - Just enough to show the flow
5. **NO tests** - Tests come during implementation

## Mock Data Pattern

Keep it simple:

```typescript
// Option 1: Inline (fastest)
const MOCK_USERS = [{ id: 1, name: "Test" }];

// Option 2: JSON file (for larger data)
import mockData from './mocks/users.json';
```

**Key:** Shape must match expected API. Mock cleanup happens during implementation.

## References

- `references/framework-patterns.md` - Patterns for each framework

## Examples

- `examples/react-prototype.md` - React component prototype
- `examples/vanilla-prototype.md` - HTML/CSS prototype

## Validation Checklist

Before presenting prototype:
- [ ] Uses existing components from codebase
- [ ] Follows project's styling approach
- [ ] Mock data shape matches expected API
- [ ] Mock locations are documented in output
- [ ] Can run with single command
