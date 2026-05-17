---
name: figma
version: 1.3.0
description: Use when user says "figma", "figma it", "sync figma", "figma mockup", "create figma file", "design to figma", "figma from PRD", "figma from journey", "build in figma", "figma design system", or wants to create, sync, or update anything in Figma (design system, components, variables, mockups, or front-end-ready screens). Always checks linked Figma libraries first; asks the user when no linked library exists rather than inventing primitives. Uses `use_figma` (Plugin API JavaScript) as the writer.
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
5. **Check for Mobbin:** Run `ToolSearch` for `"mobbin"`. If available, it's required in Phase 1 step 7 (one search per anticipated screen). If not connected, note the gap and continue.

## Phase 0.5: Load Writer Guidance

**Default writer is `mcp__figma__use_figma`** — runs JavaScript via the Figma Plugin API, imports library components by key, creates real instances. Before calling it, load `figma-use` guidance (covers Plugin API gotchas):

1. Try `Skill` tool → load `figma-use`.
2. If not registered, fall back to `ReadMcpResourceTool` with URI `skill://figma/figma-use/SKILL.md`.


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
7. **Mobbin reference research — collaborative with user (MANDATORY when Mobbin connected, one search per screen, no exceptions):**
   - Why upstream: library tells you *which components exist*; Mobbin shows *how real apps compose them*. That decision shapes the inventory and state model — locking the plan first means Mobbin is too late.
   - For each anticipated screen, call `mcp__mobbin__search_screens({ query: "<screen purpose>", platform: "<ios|web>", limit: 5, mode: "deep" })`.
   - Present top 3 results per screen alongside the matched library components from step 6. **Use AskUserQuestion** to let the user pick direction: pattern, state model, copy tone, edge cases. These choices feed Phase 2 + 3.
   - **Task list MUST contain a "Mobbin reference: \<screen>" task per anticipated screen, before any Phase 2/4B task.** Missing = silent skip; user audits the list directly.
   - The only legitimate skip is "Mobbin not connected" (record as gap). No "direct re-skin" escape.
8. Present consolidated findings — library names, component keys, variable IDs, Mobbin picks per screen, gaps — and **use AskUserQuestion** to confirm before Phase 2.

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

⚠ **This phase IS design, not tooling execution.** Mobbin references must already exist from Phase 1 step 7. Page inventory (Phase 2), mapping with real keys (Phase 3), mockup plan (step 1 below), and per-screen confirmations (steps 2, 8) are non-skippable.

⚠ **Task list is the proof.** Before any build task, your task list MUST contain: Phase 1 Mobbin tasks per screen + Phase 2 inventory + Phase 3 mapping + Phase 4B plan + per-screen build/confirm. A list with only "Build X / Y / Z" — or build tasks before discovery — is visible evidence the process was skipped.

**Pre-flight (gate the phase):**
- Phase 2 inventory done + user-confirmed. Phase 3 mapping has a real key/ID in every row. Mockup plan drafted.
- Phase 0.5 done — `figma-use` guidance loaded. Writer = `use_figma` (default); `generate_figma_design` only as web-app screenshot reference.
- The JavaScript you pass to `use_figma` MUST call `figma.importComponentByKeyAsync(key)` for each Phase 3 key, then `.createInstance()`. Naming components without importing them draws primitives.

If any pre-flight item is incomplete, return to that earlier phase.

1. Present the mockup plan: frame names, routes, sections, **reused assets listed with actual keys/IDs from Phase 3**, required states.
2. **Use AskUserQuestion** to confirm.
3. **Build with `use_figma`.** Pass Phase 3 keys to `code`; JS calls `figma.importComponentByKeyAsync(key)` then `.createInstance()`. For web-app pixel-perfect copies, run `generate_figma_design` in parallel as a screenshot reference, refine `use_figma` to match, then delete the screenshot output. For PRD/intent/iOS/Android, skip `generate_figma_design`.
4. Bind variables by ID (`figma.variables.getVariableByIdAsync` + `setBoundVariable`); no inline hex.
5. Name frames by page, route, section, state.
6. Use auto-layout and stable hierarchy.
7. Validate with `get_metadata` and `get_screenshot`. **Orphan-frame check (mandatory, blocking):**
   - Children whose names match a Phase 3 need but appear as `<frame>` not `<instance>` = orphans.
   - `<text>` nodes with emoji where icon components should be = orphans.
   - **If found**: STOP, report the list, re-run with explicit `importComponentByKeyAsync` calls.
8. **Use AskUserQuestion** after each page before continuing.

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

- **Treating "tooling works" as permission to skip the design process** — `use_figma` succeeding is the floor. Without inventory, mapping, Mobbin, and confirmations, the output is shapes-with-keys, not design.
- Creating screens before confirming the page inventory.
- **Using `generate_figma_design` as the main writer** — it's reserved for web-app screenshot reference. `use_figma` is the default writer; wrong tool was the v1.0–v1.2 root cause of orphan frames.
- **Calling `use_figma` without loading `figma-use` first** — covers Plugin API gotchas that cause silent JavaScript failures.
- **Substituting emoji for icon components** — tells that no icon component was imported. Search the library for real icons.
- **Inventing primitives when the library is missing the asset or no library exists** — STOP and ASK the user (link a library, update it, or explicitly approve custom work). Silent invention fragments the design system.
- **Fetching from an empty Figma file in a loop** — if blank, push mode (`generate_figma_design`) seeds it first.
- Inventing pages not supported by PRD, journey, or code.
- Making visual-only mockups with unclear route/component/state boundaries.
- Depending on another design tool's rules or node IDs.
