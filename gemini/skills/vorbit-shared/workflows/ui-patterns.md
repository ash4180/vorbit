# Vorbit UI Patterns Workflow

Use as a reference when implementing UI components, building interfaces, creating forms, or any frontend work.

1. Load Vorbit durable rules before doing anything else.
2. Core stack: Tailwind CSS for styling, `motion/react` for animations, `cn()` for class logic, Radix/React Aria/Base UI for primitives. Don't mix primitive systems.
3. Accessible primitives: use headless UI libraries (Radix Dialog, Dropdown, Tooltip, Tabs, Select) — never build from scratch with divs.
4. Form rules: every input needs `<label>` with `htmlFor`, errors use `role="alert"` and `aria-describedby`, use correct input types for mobile.
5. Interactions: destructive actions → AlertDialog with confirm/cancel. Loading → structural skeletons. Errors → near the field, not toast. Empty states → message + action. Disabled buttons → explain why.
6. Animation: max 200ms, only `transform` and `opacity`, always respect `prefers-reduced-motion`.
7. Z-index scale: z-10 (dropdowns), z-20 (sticky), z-30 (modals), z-40 (notifications), z-50 (critical overlays).
8. Performance: no `box-shadow` animations, no `filter: blur()` on scroll, no layout-triggering animations.
9. Checklist: Tailwind, cn(), accessible primitives, labeled inputs, AlertDialog for destructive, animations ≤200ms, reduced motion, z-index scale, no magic numbers, empty/loading states handled.
