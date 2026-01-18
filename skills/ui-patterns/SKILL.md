---
name: ui-patterns
version: 1.0.0
description: Use when implementing UI components, building interfaces, creating forms, or any frontend work. Provides opinionated constraints for accessible, performant, consistent UI based on ui-skills.com patterns.
---

# UI Patterns Skill

Opinionated constraints for building better interfaces. Based on [ui-skills.com](https://ui-skills.com).

**When to use:** Any UI component implementation, form building, layout work.

## Core Stack Requirements

| Requirement | Use | Don't Use |
|-------------|-----|-----------|
| **Styling** | Tailwind CSS | CSS-in-JS, plain CSS |
| **Animations** | `motion/react` (Framer Motion) | CSS transitions, other animation libs |
| **Class Logic** | `cn()` utility (clsx + tailwind-merge) | String concatenation |
| **Primitives** | Radix, React Aria, or Base UI | Custom implementations |

**Rule:** Don't mix primitive systems. Pick one and stick to it.

## Component Patterns

### Accessible Primitives
Use headless UI libraries for complex components:

| Component | Use Primitive | Don't Build From Scratch |
|-----------|---------------|--------------------------|
| Modal/Dialog | `@radix-ui/react-dialog` | `<div>` with click handlers |
| Dropdown | `@radix-ui/react-dropdown-menu` | Custom dropdown |
| Tooltip | `@radix-ui/react-tooltip` | Title attribute |
| Tabs | `@radix-ui/react-tabs` | Manual state + divs |
| Select | `@radix-ui/react-select` | `<select>` styling hacks |

### Form Patterns
```typescript
// Use controlled inputs with proper labels
<label htmlFor="email">Email</label>
<input id="email" type="email" aria-describedby="email-error" />
{error && <span id="email-error" role="alert">{error}</span>}
```

**Rules:**
- Every input needs a `<label>` with matching `htmlFor`
- Error messages use `role="alert"` and `aria-describedby`
- Use `type="email"`, `type="tel"`, etc. for mobile keyboards

## Interaction Rules

| Interaction | Pattern |
|-------------|---------|
| **Destructive actions** | Always use AlertDialog with confirm/cancel |
| **Loading states** | Structural skeletons matching final layout |
| **Errors** | Place near the field, not in toast/modal |
| **Empty states** | Clear message + action, never blank |
| **Disabled buttons** | Explain why (tooltip or nearby text) |

### AlertDialog for Destructive Actions
```tsx
// Always confirm before delete, remove, clear
<AlertDialog>
  <AlertDialogTrigger>Delete</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogTitle>Delete this item?</AlertDialogTitle>
    <AlertDialogDescription>This cannot be undone.</AlertDialogDescription>
    <AlertDialogCancel>Cancel</AlertDialogCancel>
    <AlertDialogAction>Delete</AlertDialogAction>
  </AlertDialogContent>
</AlertDialog>
```

## Animation Standards

**Rule:** Animations should be felt, not seen.

| Constraint | Value |
|------------|-------|
| **Max duration** | 200ms (never more) |
| **Properties** | Only `transform` and `opacity` (compositor properties) |
| **Motion preference** | Always respect `prefers-reduced-motion` |

### Motion Wrapper Pattern
```tsx
import { motion } from "motion/react"

// Fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.15 }}
>
  {children}
</motion.div>
```

### Reduced Motion Support
```tsx
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches

// Skip animations if user prefers reduced motion
<motion.div
  animate={prefersReducedMotion ? {} : { opacity: 1 }}
>
```

## Typography & Layout

| Rule | Implementation |
|------|----------------|
| **Headings** | Use `text-balance` for multi-line headings |
| **Z-index** | Use fixed scale: `z-10`, `z-20`, `z-30`, `z-40`, `z-50` |
| **Spacing** | Use Tailwind scale, no arbitrary values |

### Z-Index Scale
```
z-10  - Dropdowns, tooltips
z-20  - Sticky headers, floating buttons
z-30  - Modals, dialogs
z-40  - Notifications, toasts
z-50  - Critical overlays only
```

## Performance Rules

**Prohibited (expensive):**
- `box-shadow` animations
- `filter: blur()` on scroll
- Layout-triggering animations (`width`, `height`, `top`, `left`)
- Large SVG animations

**Allowed:**
- `transform` (translate, scale, rotate)
- `opacity`
- CSS containment for complex components

## Design Constraints

| Rule | Why |
|------|-----|
| **No gradients** | Unless user explicitly requests |
| **No drop shadows on text** | Accessibility issue |
| **Clear empty states** | Never show blank areas |
| **Consistent iconography** | One icon set per project |

## Checklist Before Completion

Before marking UI work done:

- [ ] Uses Tailwind for all styling
- [ ] Uses `cn()` for conditional classes
- [ ] Uses accessible primitives (Radix/React Aria) for complex components
- [ ] All inputs have labels and error handling
- [ ] Destructive actions use AlertDialog
- [ ] Animations ≤ 200ms, only transform/opacity
- [ ] Respects `prefers-reduced-motion`
- [ ] Z-index follows scale
- [ ] No magic numbers in spacing/sizing
- [ ] Empty states are handled
- [ ] Loading states use skeletons

## Integration with Epic/Implement

When sub-issue has "UI Patterns" reference:
1. This skill is auto-invoked
2. Follow all constraints above
3. Use the "Reuse & Patterns" section for existing components
4. Verify checklist before marking done

## Quick Reference

```bash
# Install required dependencies
npm install clsx tailwind-merge motion @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# cn utility (add to lib/utils.ts)
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```
