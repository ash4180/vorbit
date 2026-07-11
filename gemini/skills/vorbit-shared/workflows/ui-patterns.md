# Vorbit UI Patterns Workflow

Use as a reference when implementing UI components, building interfaces, creating forms, or any frontend work.

1. Load the Vorbit runtime contract and durable rules. This is supporting policy, not standalone authorization to edit.
2. Inspect and preserve the repository's styling, class-helper, animation, and primitive systems. Tailwind, `motion/react`, `cn()`, and Radix/React Aria/Base UI are examples to reuse only when already standard; do not introduce a second stack silently.
3. Use semantic native elements or the repository's accessible primitives for complex widgets. Do not rebuild keyboard/focus behavior from generic divs.
4. Form rules: every input needs `<label>` with `htmlFor`, errors use `role="alert"` and `aria-describedby`, use correct input types for mobile.
5. Interactions: irreversible actions require the project's confirmation dialog. Field errors stay near fields; background/action failures may use the existing notification pattern. Empty and disabled states must explain the next action.
6. Animation: match product timing; prefer ≤200ms and compositor properties, and always respect `prefers-reduced-motion`.
7. Use the project's layer and spacing tokens; only use the documented z-10..z-50 scale as a fallback when no scale exists.
8. Performance: no `box-shadow` animations, no `filter: blur()` on scroll, no layout-triggering animations.
9. Checklist: existing stack reused, accessible primitives, labeled inputs, irreversible-action confirmation, reduced motion, project tokens, and empty/loading/error states handled.
