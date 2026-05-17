# Vorbit Figma Workflow

Use for Figma design-system sync and front-end-ready Figma mockups.

## Required Setup

1. Load Vorbit durable rules before doing anything else.
2. Load `figma-use` before any Figma write or unique Figma read.
3. For Figma screen/mockup creation, load `figma-generate-design`.
4. For Figma design-system creation or reconciliation, load `figma-generate-library`.
5. Work incrementally. Never batch unrelated Figma mutations into one call.

## Shared Mindset

1. Think like the engineer who must implement the mockup.
2. Break complex flows into pages, routes, components, states, and data boundaries before drawing screens.
3. Search the codebase before inventing components or patterns.
4. Use the linked Figma design system first: components, variables, text styles, and effect styles.
5. Stop and ask if no linked design system exists or if Figma and code disagree.
6. Use Figma-specific APIs, linked-library behavior, validation loops, and screenshots.

## Discovery Phase

1. Gather source context: PRD, journey, existing Figma file, screenshots, codebase routes/pages, and relevant components.
2. If journey context is needed, read `journey.md` and use it only to understand flow and page needs.
3. Inspect the codebase for framework, routing, styling, component library, import aliases, and reusable UI components.
4. Inspect the target Figma file for pages, existing frames, local variables, components, text styles, and effect styles.
5. Search linked Figma libraries for relevant components, variables, and styles before creating anything custom.
6. Present discovery findings and get user confirmation before planning screens or syncing a library.

## Design-System Sync Path

Use this path when the user asks to create, sync, or reconcile a Figma design system from code.

1. Compare code tokens/components with existing Figma variables, styles, and components.
2. Present a design-system mapping: code source, Figma target, reusable linked asset, gap, and proposed action.
3. Get user confirmation before writing tokens, styles, pages, or components.
4. Follow `figma-generate-library` phase order: discovery, foundations, file structure, components, integration, QA.
5. Confirm with the user after foundations, file structure, each component, and final QA.

## Mockup Creation Path

Use this path when the user asks for Figma mockups, screens, pages, or journey-informed designs.

1. Build a page inventory before drawing: page name, route, user goal, entry point, exit point, primary actions, data needed, and required states.
2. Map each page to front-end component boundaries before creating Figma frames.
3. Use shadcn-friendly boundaries where applicable: Button, Input, Form, Card, Dialog, Sheet, Tabs, Table, Dropdown, Badge, Toast, Accordion, Checkbox, RadioGroup, Select, Switch, Tooltip.
4. Include the states engineers need to implement: default, loading, empty, error, disabled, permission denied, and success where the flow requires them.
5. Present the page inventory and get user confirmation.
6. Present the design-system mapping for each page and get user confirmation.
7. Present the mockup plan with frame names, sections, components, and states. Get user confirmation before creating screens.
8. Create screens with linked design-system component instances and variables whenever available. Do not hardcode styling when a token or component exists.
9. Name frames by page, route, section, and state so frontend implementation is obvious.
10. Validate each generated page with Figma metadata and screenshot checks.
11. Get user confirmation after each generated page or screen before continuing.

## Handoff Rules

1. Make mockups easy to implement, not visually clever.
2. Prefer existing product layout and component patterns over new abstractions.
3. Use auto-layout, consistent spacing tokens, and stable frame names.
4. Keep custom primitives to a minimum. If a linked component exists, use it.
5. Call out any missing design-system components as explicit implementation gaps.
6. Final report must include Figma page/frame links or IDs, page inventory, reused design-system assets, missing assets, confirmed states, and next implementation steps.
