<!-- GENERATED from skills/ui-patterns/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# UI Patterns Skill

Opinionated constraints for building better interfaces. Based on [ui-skills.com](https://ui-skills.com).

Read and follow `../references/execution-contract.md` before applying this policy.

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

## Animation Standards

Prefer short, purposeful motion. Match existing product timing before applying the fallback below.

| Constraint | Value |
|------------|-------|
| **Default duration** | Up to 200ms; longer only when the interaction clearly requires it |
| **Properties** | Only `transform` and `opacity` (compositor properties) |
| **Motion preference** | Always respect `prefers-reduced-motion` |

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

- [ ] All inputs have labels and error handling
- [ ] Loading states use the repository's established accessible pattern
