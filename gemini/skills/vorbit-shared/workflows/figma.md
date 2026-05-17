# Vorbit Figma Workflow

Use for Figma design-system sync and front-end-ready Figma mockups.

## Required Setup

1. Load Vorbit durable rules before doing anything else.
2. Verify Figma MCP connection before any Figma read or write. If unavailable, stop and ask user to reconnect.
3. Do NOT depend on the Figma MCP's "MANDATORY companion skills" (`figma-use`, `figma-generate-design`) as the binding mechanism. They are declared in the MCP server instructions but are not installed as `Skill`-callable entries in most environments. Use the inline pre-write contract below instead.
4. **Pre-write contract** — before any call to `generate_figma_design` or `use_figma`, the working context must contain a live `get_libraries` result, a real component key from `search_design_system` for every component need, a real variable ID from `get_variable_defs` for every token need, AND those keys/IDs must appear verbatim in the prompt body sent to the write tool. Naming a component without its key tells the tool nothing — it draws a fresh primitive.
5. Work incrementally. Never batch unrelated Figma mutations into one step.
6. Validate major Figma changes with metadata and screenshot checks when tools support them.

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
5. Discover linked libraries — executable, not aspirational:
   - Call `get_libraries` to list every library connected to the target file. Record library names and IDs.
   - If the result is empty, stop and ask the user (link a library, point to a different file, or explicitly approve custom primitives). Do not skip ahead to drawing.
   - For each component need, call `search_design_system` with a concrete query (e.g. "button primary", "card surface"). Record the returned component key and library source.
   - Call `get_variable_defs` to capture token IDs for colors, spacing, radii, and typography. These IDs — not hex codes — are what `generate_figma_design` needs to bind tokens.
   - If `search_design_system` returns no match for a need, mark it as a gap. Never silently substitute a custom primitive.
6. Present discovery findings (including library names, matched component keys, captured variable IDs, and any gaps) and get user confirmation before planning screens or syncing a library.

## Design-System Sync Path

Use this path when the user asks to create, sync, or reconcile a Figma design system from code.

1. Compare code tokens/components with existing Figma variables, styles, and components.
2. Present a design-system mapping: code source, Figma target, reusable linked asset, gap, and proposed action.
3. Get user confirmation before writing tokens, styles, pages, or components.
4. Build foundations before components: variables, text styles, effect styles, page structure, then reusable components.
5. Confirm with the user after foundations, file structure, each component, and final QA.

## Mockup Creation Path

Use this path when the user asks for Figma mockups, screens, pages, or journey-informed designs.

1. Build a page inventory before drawing: page name, route, user goal, entry point, exit point, primary actions, data needed, and required states.
2. Map each page to front-end component boundaries before creating Figma frames.
3. Use shadcn-friendly boundaries where applicable: Button, Input, Form, Card, Dialog, Sheet, Tabs, Table, Dropdown, Badge, Toast, Accordion, Checkbox, RadioGroup, Select, Switch, Tooltip.
4. Include the states engineers need to implement: default, loading, empty, error, disabled, permission denied, and success where the flow requires them.
5. Present the page inventory and get user confirmation.
6. Present the design-system mapping for each page. Every mapped component must include the real `search_design_system` key and every mapped token must include the real `get_variable_defs` ID. A name without a key is a gap, not a match — go back and look it up. Get user confirmation.
7. Present the mockup plan with frame names, sections, the actual component keys and variable IDs bound to each slot, and states. Get user confirmation before creating screens.
8. Generate with the keys, not the names. When calling `generate_figma_design`, pass the component keys and variable IDs in the prompt/payload so the tool instances them instead of drawing fresh primitives. Naming a component without its key tells the tool nothing — it draws a rectangle and labels it.
9. Name frames by page, route, section, and state so frontend implementation is obvious.
10. Validate each generated page with `get_metadata` and `get_screenshot`. Orphan-frame check is mandatory and blocking: scan metadata for child nodes whose names suggest library components (Button, NavItem-*, Card, Input, Sidebar) but appear as `<frame>` rather than `<instance>`. Also flag any `<text>` node containing emoji characters — that almost always means an icon component wasn't looked up. If any orphan is found, STOP, do not present the result as done, report the orphan list, and re-generate that section with explicit keys in the prompt.
11. Get user confirmation after each generated page or screen before continuing.

## Handoff Rules

1. Make mockups easy to implement, not visually clever.
2. Prefer existing product layout and component patterns over new abstractions.
3. Use auto-layout, consistent spacing tokens, and stable frame names.
4. Keep custom primitives to a minimum. If a linked component exists, use it.
5. Call out any missing design-system components as explicit implementation gaps.
6. Final report must include Figma page/frame links or IDs, page inventory, reused design-system assets, missing assets, confirmed states, and next implementation steps.
