# Vorbit Figma Workflow

Use for Figma design-system sync and front-end-ready Figma mockups.

## Required Setup

1. Load Vorbit durable rules before doing anything else.
2. **Choose the right writer.** Per Figma's own `use_figma` tool description: `use_figma` is the default for all writes (it runs JavaScript via the Plugin API and imports library components by key). `generate_figma_design` is the exception — only for capturing a web-app page as a pixel-perfect reference, then deleted. For PRD-driven, from-scratch, iOS, or Android mockups, use `use_figma` only.
3. **Load `figma-use` guidance before any `use_figma` call.** If `figma:figma-use` is in your available-skills list, call `Skill` with `figma:figma-use`. Otherwise call `ReadMcpResourceTool` with `server: figma` and `uri: skill://figma/figma-use/SKILL.md`. Both load the same content; pick whichever exists.
4. **Pre-write contract** — `get_libraries` must have run this session, every component need must have a real key from `search_design_system`, every token need must have a real variable ID from `get_variable_defs`, AND the JavaScript code passed to `use_figma` must call `figma.importComponentByKeyAsync` with each key before creating instances.
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
5. Discover linked libraries — executable, not aspirational:
   - Call `get_libraries` to list every library connected to the target file. Record library names and IDs.
   - If the result is empty, stop and ask the user (link a library, point to a different file, or explicitly approve custom primitives). Do not skip ahead to drawing.
   - For each component need, call `search_design_system` with a concrete query (e.g. "button primary", "card surface"). Record the returned component key and library source.
   - Call `get_variable_defs` to capture token IDs for colors, spacing, radii, and typography. These IDs — not hex codes — are what `generate_figma_design` needs to bind tokens.
   - If `search_design_system` returns no match for a need, mark it as a gap. Never silently substitute a custom primitive.
6. Mobbin reference research — collaborative with the user, MANDATORY when Mobbin is connected, one search per anticipated screen, no exceptions. Mobbin belongs in Discovery, not at draw time: the library tells you which components exist; Mobbin shows how real shipped apps compose them. Co-evaluate with the user before locking the inventory.
   - For each anticipated screen, call `mcp__mobbin__search_screens({ query: "<screen purpose>", platform: "<ios|web>", limit: 5, mode: "deep" })`.
   - Present top 3 Mobbin results per screen alongside the matched library components. Ask the user to pick a direction per screen — layout, state model, copy tone, edge cases.
   - Task list MUST include one "Mobbin reference: <screen name>" task per anticipated screen, BEFORE any build task. Missing tasks = silent skip; user can audit the list directly.
   - No "direct re-skin" escape. The only legitimate skip is "Mobbin is not connected" (record as gap; degraded quality is expected).
7. Present consolidated discovery findings — library names, matched component keys, captured variable IDs, Mobbin pattern picks per screen, any gaps — and get user confirmation before moving forward.

## Design-System Sync Path

Use this path when the user asks to create, sync, or reconcile a Figma design system from code.

1. Compare code tokens/components with existing Figma variables, styles, and components.
2. Present a design-system mapping: code source, Figma target, reusable linked asset, gap, and proposed action.
3. Get user confirmation before writing tokens, styles, pages, or components.
4. Follow `figma-generate-library` phase order: discovery, foundations, file structure, components, integration, QA.
5. Confirm with the user after foundations, file structure, each component, and final QA.

## Mockup Creation Path

Use this path when the user asks for Figma mockups, screens, pages, or journey-informed designs.

⚠ **This path IS the design process — not just tooling execution.** Every step below runs in full regardless of how cleanly the tools work. A passing `use_figma` import only proves you can place a library instance — whether it belongs on this screen, in this position, alongside which neighbors, at what state, is design. Page inventory, design-system mapping with real keys, mockup plan, Mobbin reference patterns, and per-screen user confirmation are non-skippable. Skipping any of them because "tools are working" produces decoration, not a mockup an engineer can implement.

⚠ **Mobbin references should already exist from Discovery Phase step 6.** This path is execution of an agreed plan, not the moment to discover references. If you find yourself wanting to search Mobbin here, return to the Discovery Phase — do the collaborative research with the user, record picks per screen, then come back. Task list discipline: Mobbin tasks belong in Discovery, before any build task. A build task without a corresponding upstream Mobbin task is evidence Discovery was skipped or reordered.

1. Build a page inventory before drawing: page name, route, user goal, entry point, exit point, primary actions, data needed, and required states.
2. Map each page to front-end component boundaries before creating Figma frames.
3. Use shadcn-friendly boundaries where applicable: Button, Input, Form, Card, Dialog, Sheet, Tabs, Table, Dropdown, Badge, Toast, Accordion, Checkbox, RadioGroup, Select, Switch, Tooltip.
4. Include the states engineers need to implement: default, loading, empty, error, disabled, permission denied, and success where the flow requires them.
5. Present the page inventory and get user confirmation.
6. Present the design-system mapping for each page. Every mapped component must include the real `search_design_system` key and every mapped token must include the real `get_variable_defs` ID. A name without a key is a gap, not a match — go back and look it up. Get user confirmation.
7. Present the mockup plan with frame names, sections, the actual component keys and variable IDs bound to each slot, and states. Get user confirmation before creating screens.
8. Build with `use_figma`, not `generate_figma_design`. Pass Phase 3 component keys and variable IDs in the JavaScript code body. The code must call `figma.importComponentByKeyAsync(key)` for each component and bind variables via `figma.variables.getVariableByIdAsync` + `setBoundVariable`. `generate_figma_design` is reserved for web-app screenshot capture only — for PRD or non-web targets, skip it.
9. Name frames by page, route, section, and state so frontend implementation is obvious.
10. Validate each generated page with `get_metadata` and `get_screenshot`. Orphan-frame check is mandatory and blocking: scan metadata for child nodes whose names suggest library components (Button, NavItem-*, Card, Input, Sidebar) but appear as `<frame>` rather than `<instance>`. Also flag any `<text>` node containing emoji characters — that almost always means an icon component wasn't imported. If any orphan is found, STOP, do not present the result as done, report the orphan list, and re-run `use_figma` with JavaScript that explicitly imports each missing component via `figma.importComponentByKeyAsync`.
11. Get user confirmation after each generated page or screen before continuing.

## Handoff Rules

1. Make mockups easy to implement, not visually clever.
2. Prefer existing product layout and component patterns over new abstractions.
3. Use auto-layout, consistent spacing tokens, and stable frame names.
4. Keep custom primitives to a minimum. If a linked component exists, use it.
5. Call out any missing design-system components as explicit implementation gaps.
6. Final report must include Figma page/frame links or IDs, page inventory, reused design-system assets, missing assets, confirmed states, and next implementation steps.
