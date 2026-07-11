---
name: ui-patterns
description: Apply when implementing or reviewing user-facing frontend components, forms, interactions, layout, accessibility, animation, or UI performance. It supplies implementation constraints and should accompany the relevant build, prototype, or review workflow; it does not by itself authorize edits. Do not use for backend work, Figma or Pencil design-only tasks, Webflow authoring, or generic UX research.
---

# UI Patterns Skill

Opinionated constraints for building better interfaces. Based on [ui-skills.com](https://ui-skills.com).

Read and follow `../_shared/execution-contract.md` before applying this policy.

Use this as supporting policy for user-facing UI work. First inspect the repository's existing stack; this skill does not authorize a framework migration or dependency install.

## Stack Compatibility

| Concern | Reuse when present | Avoid |
|-------------|-----|-----------|
| **Styling** | The repository's established system; Tailwind when already standard | Introducing a second styling system |
| **Animations** | Existing motion/CSS conventions; `motion/react` when already installed | Adding an animation library for one effect |
| **Class Logic** | Existing helper such as `cn()` | Duplicating a class helper |
| **Primitives** | Existing accessible primitives or semantic native elements | Rebuilding complex widgets from generic divs |

Do not mix primitive systems within a feature. If the project has none and a complex widget is required, present the dependency choice before installing anything.

## Component Patterns

### Accessible Primitives
Use the project's accessible primitive library for complex components. The table shows examples, not mandatory packages:

| Component | Use Primitive | Don't Build From Scratch |
|-----------|---------------|--------------------------|
| Modal/Dialog | Existing Dialog/AlertDialog primitive | `<div>` with click handlers |
| Dropdown | Existing menu primitive | Hand-rolled focus management |
| Tooltip | Existing tooltip primitive | Hover-only custom tooltip |
| Tabs | Existing tabs primitive | Divs without keyboard semantics |
| Select | Native `<select>` or existing select primitive | Inaccessible custom select |

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
| **Irreversible destructive actions** | Use the project's confirmation dialog with confirm/cancel |
| **Loading states** | Structural skeletons matching final layout |
| **Errors** | Field errors stay near the field; background/action failures may use the project's notification pattern |
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

Prefer short, purposeful motion. Match existing product timing before applying the fallback below.

| Constraint | Value |
|------------|-------|
| **Default duration** | Up to 200ms; longer only when the interaction clearly requires it |
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
const prefersReducedMotion = useReducedMotion() // existing SSR-safe project hook

// Skip animations if user prefers reduced motion
<motion.div
  animate={prefersReducedMotion ? {} : { opacity: 1 }}
>
```

## Typography & Layout

| Rule | Implementation |
|------|----------------|
| **Headings** | Use `text-balance` for multi-line headings |
| **Z-index** | Use the project's named layer/scale tokens |
| **Spacing** | Use the project's token scale |

### Fallback Z-Index Scale
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

- [ ] Matches the repository's existing styling system
- [ ] Reuses the existing conditional-class helper when one exists
- [ ] Uses accessible native elements or the project's primitive library for complex components
- [ ] All inputs have labels and error handling
- [ ] Irreversible destructive actions require confirmation
- [ ] Animations follow existing timing and prefer transform/opacity
- [ ] Respects `prefers-reduced-motion`
- [ ] Z-index and spacing use project tokens/scales
- [ ] Empty states are handled
- [ ] Loading states use the repository's established accessible pattern

## Integration with Epic/Implement

When a sub-issue has a "UI Patterns" reference:
1. Apply this skill as supporting policy
2. Follow all constraints above
3. Use the "Reuse & Patterns" section for existing components
4. Verify checklist before marking done
