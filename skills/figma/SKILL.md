---
name: figma
version: 1.2.0
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

## Phase 0.5: Pre-Write Contract

⚠ **Do not depend on the Figma MCP's "MANDATORY companion skills" (`figma-use`, `figma-generate-design`).** They are declared in the MCP server instructions but are NOT installed as `Skill`-callable entries in most environments. Earlier versions of this skill relied on loading them — that protection silently failed and produced orphan frames. The contract below replaces that reliance with inline requirements using tools that are confirmed to work.

Before ANY call to `generate_figma_design`, `use_figma`, or another Figma write tool, the working context MUST contain:

1. **A live `mcp__figma__get_libraries` result** for the target file, in this conversation. Stale knowledge from earlier sessions does not count.
2. **For every component need surfaced in Phase 3: a real component key** returned by `mcp__figma__search_design_system`. Not a guessed name. Not a placeholder. Not "TBD."
3. **For every token need: a real variable ID** returned by `mcp__figma__get_variable_defs`. Not a hex value. Not a CSS-style string like `var(--foreground)`. The literal Figma variable identifier.
4. **The component keys and variable IDs MUST appear verbatim in the prompt body passed to the write tool.** Naming a component without including its key in the prompt is equivalent to not using it — `generate_figma_design` will draw fresh primitives.

If any of (1)–(4) is missing, return to Phase 1 step 6 to run the discovery tools. Do not call any write tool until the contract is satisfied.

**Why this contract exists:** A real test on 2026-05-17 showed `generate_figma_design` producing 100% orphan frames (zero `<instance>` nodes) even when the linked library was rich (shadcn/ui kit). Root cause: the write call received only natural-language descriptions of components, not their actual keys. Including the keys in the prompt is the difference between "draw a rectangle labeled Button" and "instance component key `comp:abc123`."

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
   - Pages and existing frames (`get_metadata`)
   - Local and linked variables (`get_variable_defs`)
   - Components and component sets
   - Text styles and effect styles
   - **Empty-file check**: if the target file or frame is blank (screenshot returns nothing, `get_design_context` reports "nothing selected"), the file has not been seeded yet. Do NOT keep fetching — switch to **code→design push mode** and use `generate_figma_design` (or equivalent write tool) to push the current UI/intent into Figma first, then continue from a populated frame.
6. **Discover linked libraries — executable, not aspirational:**
   - Call `mcp__figma__get_libraries` to list every library connected to the target file. Record library names, IDs, and whether each is enabled.
   - **IF the result is empty:** the file has no linked library. STOP here and ask the user (link a library, point to a different file, or explicitly approve custom primitives). Do not skip ahead to drawing.
   - For each component/variable need surfaced in step 4, call `mcp__figma__search_design_system` with a concrete query (e.g. `"button primary"`, `"card surface"`). Record the returned component key, node ID, and library source.
   - Call `mcp__figma__get_variable_defs` to capture token IDs for colors, spacing, radii, and typography. These IDs — not hex codes — are what `generate_figma_design` needs to bind tokens.
   - If `search_design_system` returns no match for a need, mark it as a **gap** for Phase 3 to resolve with the user. Never silently substitute a custom primitive.
7. Present discovery findings (including library names, matched component keys, captured variable IDs, and any gaps) and **use AskUserQuestion** to confirm before planning.

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

For each page/component, map. **The "Figma key/ID" column must contain a real key returned by `search_design_system` or `get_variable_defs` — not a name, not a placeholder.** If a row has no real key, it's a gap, not a match.

| Code / Need | Figma asset | Figma key/ID | Source | Action |
|-------------|-------------|--------------|--------|--------|
| Button primary | Button / Primary | `comp:abc123` (from `search_design_system`) | Linked library "DS Core" | Reuse as instance |
| Color / background | `--surface-bg` | `var:xyz789` (from `get_variable_defs`) | Linked library "DS Tokens" | Bind variable |
| Form field | Input | `comp:def456` | Local component | Reuse as instance |
| Empty state illustration | None | — | Gap | Ask before creating |

Rules:
1. **Always check linked Figma libraries first** — components, variables, text styles, effect styles. This is a hard gate, not a preference. Phase 1 step 6 should have already produced the keys; this phase pins them to each need.
2. Reuse linked-library assets when they match the need; reuse local existing assets when no linked match exists.
3. **If a needed asset is missing from the linked library, STOP and ASK the user**: add it to the library, point to a different linked library, or explicitly approve a custom primitive. Never invent primitives silently.
4. Stop and ask if no linked design system exists at all — do not fall back to "create custom primitives" without explicit user approval.
   - **Before asking**, read `_shared/design-knowledge/references/aesthetic-direction.md` `[Skill ref]` so the question is grounded in concrete aesthetic vocabulary (committed direction, restraint, clarity). Skim `_shared/design-knowledge/data/styles.csv` and `colors.csv` if proposing palette or style options.
5. Stop and ask if code and Figma disagree on tokens, components, or naming.
6. **A row without a real key is a gap, not a match.** If you find yourself writing "Button / Primary" in the asset column with nothing in the key column, you didn't actually look it up — go back to Phase 1 step 6 and run `search_design_system` for it.

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

**Pre-flight (gate the whole phase):**
- Phase 0.5 Pre-Write Contract must be satisfied — `get_libraries` ran this session, every Phase 3 row has a real component key from `search_design_system`, every token need has a real variable ID from `get_variable_defs`.
- The prompt you are about to send to `generate_figma_design` must include those keys and IDs as literal strings in the body. If they're not there, the tool can't bind them — it will draw fresh primitives.

1. Present the mockup plan:
   - Frame names
   - Routes/screens
   - Sections
   - **Reused design-system assets — listed with the actual component keys and variable IDs from Phase 3**, not just names. Engineers (and the agent itself) need to see which keys bind to which slots.
   - Required states
2. **Use AskUserQuestion** to confirm before creating screens.
3. **Reference patterns (Mobbin, if connected in Phase 0):** Before drawing each new screen, call `mcp__mobbin__search_screens({ query: "<screen purpose or named pattern>", platform: "<ios|web>", limit: 5, mode: "deep" })`. Pick the platform based on the project's target. Use top 3 results as visual reference for layout, components, edge states, and copy patterns. Skip the search when the screen is a direct re-skin of an existing component or when Mobbin is unavailable. Do **not** block on Mobbin failures — degrade to drawing from the design system alone.
4. **Generate with the keys, not the names.** When calling `generate_figma_design`, pass the component keys from Phase 3 in the prompt/payload so the tool instances them instead of drawing fresh primitives. Naming a component without its key tells the tool nothing — it draws a rectangle and labels it.
5. Do not hardcode styling when a token or component exists. Bind variables by ID; do not write hex codes inline.
6. Name frames by page, route, section, and state.
7. Use auto-layout and stable frame hierarchy so frontend implementation is obvious.
8. Validate each generated page with `get_metadata` and `get_screenshot`. **Orphan-frame check is mandatory and blocking** — run after every `generate_figma_design` call, no exceptions:
   - Pull `get_metadata` for the new node.
   - For each child whose name matches a Phase 3 component need (e.g. `Button`, `NavItem-*`, `Card`, `Input`, `Sidebar`), verify the metadata shows it as an `<instance>` element with a `componentKey` matching a key returned by `search_design_system`. Plain `<frame>` elements where instances were expected are orphans.
   - Scan for `<text>` nodes containing emoji characters (👤 🔔 💳 etc.) — these almost always indicate the agent substituted emoji for icon components because no icon component was looked up.
   - **If any orphan is found**: STOP. Do not present the result as done. Report the orphan list to the user with each frame's id and name, and re-generate that section with the explicit keys in the prompt. Re-running the same prompt without explicit keys will reproduce the same orphans.
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
- **Depending on the Figma MCP companion skills (`figma-use`, `figma-generate-design`) as the binding mechanism** — they're declared MANDATORY by the MCP server but are NOT installed as `Skill`-callable entries in most environments. The binding must be inlined: explicit `search_design_system` keys in the write prompt, plus a blocking `get_metadata` orphan check after.
- **Treating component names as keys** — writing "Button / Primary" in the mapping without the actual key from `search_design_system` means you didn't look it up. Generation will fall back to a fresh rectangle.
- **Substituting emoji for icon components** — using 👤 🔔 💳 etc. as text nodes is a tell that no icon component was looked up. Search the linked library for icon components first; emoji are never the answer when a real icon component exists.
- **Inventing primitives when the linked library is missing the asset** — always STOP and ASK the user. Silent invention fragments the design system over time.
- **Treating "no linked library" as permission to create custom primitives** — ask the user how to proceed (link a library, request library updates, or explicitly approve custom work) before drawing anything
- **Fetching from an empty Figma file in a loop** — if the file or frame is blank, switch to push mode (`generate_figma_design`) and seed it first
- **Skipping the orphan-frame metadata check** — after each generated page, scan `get_metadata` for nodes that should be library instances but have no `componentKey`. Silent orphans drift forward into engineering handoff and look like the library is broken.
- Inventing pages not supported by PRD, journey, or code
- Making visual-only mockups with unclear route/component/state boundaries
- Depending on another design tool's rules or node IDs
- Skipping screenshot or metadata validation after generated screens
