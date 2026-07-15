---
name: figma
description: Use when the requested deliverable is a Figma design-system sync, component or variable update, a mockup explicitly targeted at Figma, or a front-end-ready Figma screen derived from code, a PRD, or a journey. It requires a working Figma connection, checks linked libraries first, confirms plans before writing, and modifies the target Figma file. Do not trigger merely because a Figma link is reference input, or for a mockup request that names no design surface — that routes to prototype.
---

# Figma Skill

Create Figma design-system assets and front-end-ready mockups that engineers can implement without guessing.

Read and follow `../_shared/execution-contract.md` before starting.

## Core Principles

- **Think like the implementer**: Break flows into pages, routes, components, states, and data boundaries before drawing.
- **Search code first**: Read routes, pages, components, token files, and imports before inventing layout or components.
- **Confirm every phase**: Discovery, page inventory, design-system mapping, mockup plan, and each generated page/screen.
- **Use Figma app logic**: Use Figma-specific MCP tools, linked-library behavior, metadata checks, and screenshot validation.

## Phase 0: Verify Figma Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`). Resolve the Figma connector before any write; if discovery or verification fails, tell the user to run `/mcp` and stop.

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

Use standard shadcn components as implementation boundaries where applicable.

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
3. Create screens with linked component instances and variables whenever available; do not hardcode styling when a token or component exists.
4. Name frames by page, route, section, and state.
5. Use auto-layout and stable frame hierarchy so frontend implementation is obvious.
6. Validate each generated page with metadata and screenshot checks when available.
7. **Use AskUserQuestion** after each generated page/screen before continuing.

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

- Inventing pages not supported by PRD, journey, or code
- Depending on another design tool's rules or node IDs
