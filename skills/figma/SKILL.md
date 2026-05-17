---
name: figma
version: 1.0.0
description: Use when user says "figma", "figma it", "sync figma", "figma mockup", "create figma file", "design to figma", "figma from PRD", "figma from journey", "build in figma", "figma design system", or wants to create, sync, or update anything in Figma (design system, components, variables, mockups, or front-end-ready screens). Always checks linked Figma libraries first; asks the user when no linked library exists rather than inventing primitives.
---

# Figma Skill

Create Figma design-system assets and front-end-ready mockups that engineers can implement without guessing.

## Core Principles

- **Think like the implementer**: Break flows into pages, routes, components, states, and data boundaries before drawing.
- **Use linked design system first**: Reuse Figma components, variables, text styles, and effect styles before creating custom primitives.
- **Search code first**: Read routes, pages, components, token files, and imports before inventing layout or components.
- **Confirm every phase**: Discovery, page inventory, design-system mapping, mockup plan, and each generated page/screen.
- **Use Figma app logic**: Use Figma-specific MCP tools, linked-library behavior, metadata checks, and screenshot validation.

## Phase 0: Verify Figma Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`).

1. Run `ToolSearch` for `"figma"` to check if Figma MCP tools are available.
2. **IF no Figma tools found:** "No Figma connection found. Run `/mcp` to connect, then retry." → **STOP**
3. Verify connection with a lightweight Figma read operation such as file/page metadata.
4. **IF verification fails:** "Figma connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
5. **Reference patterns (optional):** Run `ToolSearch` for `"mobbin"`. If Mobbin tools are available, note this — they'll be used in Phase 4B to fetch real-world UI references before drawing each new screen. If absent, continue without reference patterns (do **not** block).

## Phase 1: Discovery

**Goal**: Understand the product flow, implementation surface, and existing design system before creating anything.

1. Create todo list with all phases.
2. Gather source context:
   - PRD or requirements
   - Journey / user flow
   - Existing Figma file URL or target file
   - Screenshots or reference frames
   - Codebase routes/pages/components
3. If journey context exists, use it only to understand flow and page needs.
4. Inspect the codebase:
   - Framework and routing
   - Styling/token source
   - Existing UI components and import aliases
   - Data-loading boundaries and page states
5. Inspect Figma:
   - Pages and existing frames
   - Local and linked variables
   - Components and component sets
   - Text styles and effect styles
   - **Empty-file check**: if the target file or frame is blank (screenshot returns nothing, `get_design_context` reports "nothing selected"), the file has not been seeded yet. Do NOT keep fetching — switch to **code→design push mode** and use `generate_figma_design` (or equivalent write tool) to push the current UI/intent into Figma first, then continue from a populated frame.
6. Search linked Figma libraries for relevant components, variables, and styles before creating anything custom.
7. Present discovery findings and **use AskUserQuestion** to confirm before planning.

## Phase 2: Page Inventory

**Goal**: Convert complex flow into implementation-sized screens.

Before drawing, produce a page inventory:

| Field | Meaning |
|-------|---------|
| Page name | Human-readable screen name |
| Route | Expected frontend route or screen ID |
| User goal | Why this page exists |
| Entry point | How user gets here |
| Exit point | Where user goes next |
| Primary actions | Buttons/actions that must be implemented |
| Data needed | API/model data shown on the page |
| States | Default, loading, empty, error, disabled, permission denied, success |

Use shadcn-friendly implementation boundaries where applicable:
Button, Input, Form, Card, Dialog, Sheet, Tabs, Table, Dropdown, Badge, Toast, Accordion, Checkbox, RadioGroup, Select, Switch, Tooltip.

Present the inventory and **use AskUserQuestion** to confirm before mapping design-system assets.

## Phase 3: Design-System Mapping

**Goal**: Decide exactly what linked Figma assets will be used.

For each page/component, map:

| Code / Need | Figma asset | Source | Action |
|-------------|-------------|--------|--------|
| Button primary | Button / Primary | Linked library | Reuse |
| Form field | Input | Local component | Reuse |
| Missing empty state | None | Gap | Ask before creating |

Rules:
1. **Always check linked Figma libraries first** — components, variables, text styles, effect styles. This is a hard gate, not a preference.
2. Reuse linked-library assets when they match the need; reuse local existing assets when no linked match exists.
3. **If a needed asset is missing from the linked library, STOP and ASK the user**: add it to the library, point to a different linked library, or explicitly approve a custom primitive. Never invent primitives silently.
4. Stop and ask if no linked design system exists at all — do not fall back to "create custom primitives" without explicit user approval.
   - **Before asking**, read `_shared/design-knowledge/references/aesthetic-direction.md` `[Skill ref]` so the question is grounded in concrete aesthetic vocabulary (committed direction, restraint, clarity). Skim `_shared/design-knowledge/data/styles.csv` and `colors.csv` if proposing palette or style options.
5. Stop and ask if code and Figma disagree on tokens, components, or naming.

Present the mapping and **use AskUserQuestion** to confirm before writing anything.

## Phase 4A: Design-System Sync Path

Use this path when the user asks to create, sync, or reconcile Figma design-system assets from code.

1. Compare code tokens/components with Figma variables, styles, and components.
2. Lock exact v1 scope: variables, text styles, effect styles, components, and variants.
3. Get user confirmation before writing.
4. Build foundations before components:
   - Variables
   - Text styles
   - Effect styles
   - Page/file structure
   - Reusable components
5. Validate after each major write using Figma metadata and screenshot checks when available.
6. Confirm with the user after foundations, file structure, each component, and final QA.

## Phase 4B: Mockup Creation Path

Use this path when the user asks for Figma mockups, screens, pages, or journey-informed designs.

1. Present the mockup plan:
   - Frame names
   - Routes/screens
   - Sections
   - Reused design-system assets
   - Required states
2. **Use AskUserQuestion** to confirm before creating screens.
3. **Reference patterns (Mobbin, if connected in Phase 0):** Before drawing each new screen, call `mcp__mobbin__search_screens({ query: "<screen purpose or named pattern>", platform: "<ios|web>", limit: 5, mode: "deep" })`. Pick the platform based on the project's target. Use top 3 results as visual reference for layout, components, edge states, and copy patterns. Skip the search when the screen is a direct re-skin of an existing component or when Mobbin is unavailable. Do **not** block on Mobbin failures — degrade to drawing from the design system alone.
4. Create screens with linked component instances and variables whenever available.
5. Do not hardcode styling when a token or component exists.
6. Name frames by page, route, section, and state.
7. Use auto-layout and stable frame hierarchy so frontend implementation is obvious.
8. Validate each generated page with metadata and screenshot checks when available.
9. **Use AskUserQuestion** after each generated page/screen before continuing.

## Handoff Rules

Final report must include:

- Figma page/frame links or IDs
- Page inventory
- Reused design-system assets
- Missing design-system assets
- Confirmed states
- Frontend component boundaries
- Next implementation steps

## Anti-Patterns

- Creating screens before confirming the page inventory
- Drawing hardcoded rectangles when linked components or tokens exist
- **Inventing primitives when the linked library is missing the asset** — always STOP and ASK the user. Silent invention fragments the design system over time.
- **Treating "no linked library" as permission to create custom primitives** — ask the user how to proceed (link a library, request library updates, or explicitly approve custom work) before drawing anything
- **Fetching from an empty Figma file in a loop** — if the file or frame is blank, switch to push mode (`generate_figma_design`) and seed it first
- Inventing pages not supported by PRD, journey, or code
- Making visual-only mockups with unclear route/component/state boundaries
- Depending on another design tool's rules or node IDs
- Skipping screenshot or metadata validation after generated screens
