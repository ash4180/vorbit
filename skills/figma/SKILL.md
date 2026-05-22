---
name: figma
version: 1.5.0
description: Use when user says "figma", "figma it", "sync figma", "figma mockup", "create figma file", "design to figma", "figma from PRD", "figma from journey", "build in figma", or "figma design system" — anything that creates, syncs, or updates Figma design systems, components, variables, mockups, or front-end-ready screens. Always checks linked Figma libraries first; asks the user when none exists rather than inventing primitives.
---

# Figma Skill

Create Figma design-system assets and front-end-ready mockups that engineers can implement without guessing.

> **MCP namespace**: This skill uses `mcp__figma__*` (primary writer is `use_figma`) and optionally `mcp__mobbin__search_screens` for competitor research. See `_shared/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Core Principles

- **Think like the implementer**: Break flows into pages, routes, components, states, and data boundaries before drawing, ask questions to understand the user flow logic if any unclear.
- **Use linked design system first**: Reuse and import components, variables, text styles, and effect styles from the linked design system. If no design system is linked, ask the user to link one or confirm with the user that creating a design system is required.
- **Search code first**: Read routes, pages, components, token files, and imports before inventing layout or components.
- **Confirm every phase**: Discovery, page inventory, design-system mapping, mockup plan, and each generated page/screen.
- **Use Figma app logic**: Use Figma plugin, MCP Tools, linked-library behavior, metadata checks, and screenshot validation.

## Phase 0: Verify Figma Connection

Read and follow `_shared/mcp-tool-routing.md`.

1. Run `ToolSearch` for `"figma"` to check if Figma MCP tools are available.
2. **IF no Figma tools found:** "No Figma connection found. Run `/mcp` to connect, then retry." → **STOP**
3. Verify connection with a lightweight Figma read operation such as file/page metadata.
4. **IF verification fails:** "Figma connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
5. **Check for Mobbin:** Run `ToolSearch` for `"mobbin"`. If available, it's required in Phase 1 step 7. Inspect the exposed Mobbin tool names/schema before assuming first-class flow support. Record one of:
   - `native flow search` — a dedicated flow search tool or flow IDs/metadata are exposed.
   - `screen search grouped into flow candidates` — only screen search is exposed; infer flows by grouping screens by app, feature area, and recurring UI structure.
   - `Mobbin unavailable` — no Mobbin tool is connected; record the gap and continue.

## Phase 0.5: Load Writer Guidance

Before calling `use_figma`, load the figma-use guidance via `ReadMcpResourceTool` (`server: figma`, `uri: skill://figma/figma-use/SKILL.md`). Do not use the `Skill` tool for figma-use — the MCP resource path is the supported route.

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
     - Before calling `generate_figma_design`, load its companion guidance: `ReadMcpResourceTool` with `server: figma`, `uri: skill://figma/figma-generate-design/SKILL.md`.
6. **Discover linked libraries — executable, not aspirational:**
   - Call `mcp__figma__get_libraries` to list every library connected to the target file. Record library names, IDs, and whether each is enabled.
   - **IF the result is empty:** the file has no linked library. STOP here and ask the user (link a library, point to a different file, or explicitly approve custom primitives). Do not skip ahead to drawing.
   - **Discover compositions by library structure, not by name.** Naming conventions vary by team (slashes, spaces, prefixes, none). Libraries are organized by **page or folder** much more reliably — atoms on one page, composed templates on another. After `get_libraries`, surface each library's page/folder structure (via `mcp__figma__search_design_system` with broad queries or library metadata), report the page list to the user, and **use AskUserQuestion**: "These are the pages in your library: [list]. Which contain composed/template components I should reuse before atoms — or does your library not use compositions?" Search the user-named composition pages first for each Phase 2 need. A composition supersedes the atoms it would replace — record only the composition key, not its child atoms. If the user says no compositions exist, skip composition search and proceed straight to atomic search.
   - For each remaining need not satisfied by a composition, call `mcp__figma__search_design_system` with a concrete query (e.g. `"button primary"`, `"card surface"`). Record the returned component key, node ID, and library source.
   - Call `mcp__figma__get_variable_defs` to capture token IDs for colors, spacing, radii, and typography. These IDs — not hex codes — are what `generate_figma_design` needs to bind tokens.
   - If `search_design_system` returns no match for a need, mark it as a **gap** for Phase 3 to resolve with the user. Never silently substitute a custom primitive.
7. **Mobbin reference research — flow-pattern first, then per-screen (MANDATORY when Mobbin connected).** See `_shared/mobbin-research.md` for the full per-screen synthesis format (bullets, app attribution, URL coverage rules). The figma-specific steps below cover the flow-pattern discovery layer that sits on top of that shared workflow.

   - **a. Flow-pattern discovery (run FIRST when the request spans multiple screens).** Use the Mobbin capability mode recorded in Phase 0:
     - If Mobbin exposes a dedicated flow search tool, use it.
     - If Mobbin only exposes screen search, use:
       `mcp__mobbin__search_screens({ query: "<full flow description, e.g. 'billing and subscription management flow'>", platform: "<ios|web>", limit: 8, mode: "deep" })`
       Then group results by app, feature area, and recurring UI structure. These are **flow-pattern candidates**, not guaranteed Mobbin flow objects.

     Report the top 3 candidates to chat before asking. Use one block per candidate:

     ```
     **Flow Candidate <N> — <App / pattern name>**
     - Fit: <why this matches the requested flow>
     - Screens observed: <screen names or inferred stages>
     - Strong patterns: <2-3 concrete patterns>
     - Copy tone: <brief tone read>
     - Evidence: <native flow metadata, or "inferred from screen results">
     - Caveat: <missing screen, weak match, or none>
     ```

     Then **use AskUserQuestion**: "Which flow pattern should anchor the screen-level searches?" The user's pick anchors all per-screen searches in step b — bias screen queries toward that app's conventions and copy tone.

     Skip this sub-step ONLY when the request is a single isolated screen.

   - **b. Per-screen search.** For each anticipated screen:
     `mcp__mobbin__search_screens({ query: "<screen purpose>", platform: "<ios|web>", limit: 5, mode: "deep" })`

     If a flow-pattern candidate was chosen in step a, prefer results from that app/pattern when interpreting which patterns to highlight. Still mention stronger outside matches when they solve a screen better.

   - **c. Report per-screen findings** following the synthesis format in `_shared/mobbin-research.md` (4–7 bullets per screen, `[App](URL)` in every bullet, distinguish universal vs app-specific). If a screen returns no usable references, write `No Mobbin matches for <screen> — proceeding from library only.`

   - **d. Evidence rules.** Every Mobbin-derived recommendation must include:
     - App name.
     - Screen URL or screen ID when available.
     - Whether the observation is `observed directly` or `inferred`.
     - Whether the pattern is `universal`, `app-specific`, or a combination of multiple apps.
     - No 1:1 copying. Extract layout, hierarchy, state behavior, and copy tone; do not copy brand styling, colors, fonts, or proprietary component details.

   - **e. Ask direction.** After all per-screen reports are posted, **use AskUserQuestion** to pick the direction. Prefer one consolidated question over interrupting after every screen unless the flow is genuinely ambiguous. Reference report items by number:

     ```
     Which direction should I use for Phase 2?

     1. Follow Flow Candidate <N> closely for structure and tone.
     2. Combine patterns from Screens <A/B/C>.
     3. Use Mobbin only as reference and prioritize our design system.
     4. Specify another direction.
     ```

   - **Task list requirements:**
     - Multi-screen requests: `Mobbin flow-pattern discovery` → `Report Mobbin flow-pattern findings` → for each screen: `Mobbin screen search: <X>` → `Report Mobbin findings: <X>`
     - Single-screen requests: `Mobbin search: <screen>` → `Report Mobbin findings: <screen>`
     - Missing the report task = silent skip; user audits the list directly.

   - The only legitimate skip is "Mobbin not connected" (record as gap). No "direct re-skin" escape.
8. Present consolidated findings — library names, component keys, variable IDs, Mobbin capability mode, selected flow-pattern candidate, Mobbin picks per screen, gaps — and **use AskUserQuestion** to confirm before Phase 2.

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
3. **If a needed asset is missing from the linked library, STOP and ASK the user.** Options:
   - Add it to the library (Phase 4A work).
   - Point to a different linked library that has it.
   - Use the **sibling reference frame** pattern in Phase 4B step 3 — keep the mockup library-pure, put the missing element in a separate `[Reference / Gap]` frame next to the mockup so the user can see the gap and decide.
   - Explicitly approve a custom primitive (rare; only when no other option fits).
   Never invent primitives silently inside the mockup.
4. Stop and ask if no linked design system exists at all — do not fall back to "create custom primitives" without explicit user approval.
   - **Before asking**, read `_shared/design-knowledge/references/aesthetic-direction.md` `[Skill ref]` so the question is grounded in concrete aesthetic vocabulary (committed direction, restraint, clarity). Skim `_shared/design-knowledge/data/styles.csv` and `colors.csv` if proposing palette or style options.
5. Stop and ask if code and Figma disagree on tokens, components, or naming.

Present the mapping and **use AskUserQuestion** to confirm before writing anything.

## Phase 4A: Design-System Sync Path

Use this path when the user asks to create, sync, or reconcile Figma design-system assets from code.

**Before starting Phase 4A, also load `figma-generate-library`** via `ReadMcpResourceTool` (`server: figma`, `uri: skill://figma/figma-generate-library/SKILL.md`). It covers what to build and in what order — variables, text styles, effect styles, components, variants — so the design system comes out professional-grade.

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

**Pre-flight (gate the phase):**
- Phase 1 step 7 Mobbin references gathered. Phase 2 inventory done + user-confirmed. Phase 3 mapping has a real key/ID in every row. Mockup plan drafted.
- Phase 0.5 done — `figma-use` guidance loaded. Writer = `use_figma` (default); `generate_figma_design` only as web-app screenshot reference.
- **Import contract:** for every Phase 3 component key, the JS passed to `use_figma` must call `await figma.importComponentByKeyAsync("<key>")` before any `.createInstance()`. Bind variables via `figma.variables.getVariableByIdAsync("<var-id>")` — no inline hex. See `figma-use` guidance (Phase 0.5) for the full Plugin API skeleton.
- **Task list check:** Phase 1 Mobbin + Phase 2 inventory + Phase 3 mapping + Phase 4B plan + per-screen build/confirm tasks all present. Build-only task lists are a process-skip signal.

If any pre-flight item is incomplete, return to that earlier phase.

1. Present the mockup plan: frame names, routes, sections, **reused assets listed with actual keys/IDs from Phase 3**, required states.
2. **Use AskUserQuestion** to confirm.
3. **Build with `use_figma`.** Pass Phase 3 keys to `code`; JS calls `figma.importComponentByKeyAsync(key)` then `.createInstance()`. For web-app pixel-perfect copies, run `generate_figma_design` in parallel as a screenshot reference, refine `use_figma` to match, then delete the screenshot output. For PRD/intent/iOS/Android, skip `generate_figma_design`.
   - **If using `generate_figma_design`**, load its companion guidance first: `ReadMcpResourceTool` with `server: figma`, `uri: skill://figma/figma-generate-design/SKILL.md`.

   **Mobbin reference rule — borrow concept, use library:**
   - Pull the Mobbin reference screen(s) or flow-pattern candidate the user picked in Phase 1 step 7. Use them ONLY for **layout, flow, and concept** — hierarchy, density, section order, copy register.
   - Build the actual mockup using **our linked library components and variables** (Phase 3 mapping). Never copy Mobbin's colors, fonts, or specific components. Bind everything to our variables via `getVariableByIdAsync`.
   - **If the Mobbin concept needs an element our library doesn't have**, choose one of these — never invent primitives in the main mockup:
     - **a. Add to library**: if the element is good enough to belong in the design system, mark it as a Phase 4A task for the user to approve. Skip the element from this mockup until added.
     - **b. Sibling reference frame**: create a separate frame next to the mockup, named `[Reference / Gap] <element name>`, showing what's needed. This makes the gap visible without polluting the mockup with custom primitives. User decides next steps.
4. Bind variables by ID (`figma.variables.getVariableByIdAsync` + `setBoundVariable`); no inline hex.
5. Name frames by page, route, section, state.
6. Use auto-layout and stable hierarchy.
7. Validate with `get_metadata` and `get_screenshot`. **Post-write checks (mandatory, blocking) — `get_metadata` is the source of truth, not the JS you wrote:**
   - **Orphan frames**: children whose names match a Phase 3 need but appear as `<frame>` not `<instance>`. `<text>` nodes with emoji where icon components should be.
   - **Variant match**: every instance's `mainComponent.name` (full path including variant) matches the exact Phase 3 row. `Button / Primary` ≠ `Button / Secondary` — right component, wrong variant still fails.
   - **Token bindings**: every fill, stroke, effect, and text-style property on a node mapped to a Phase 3 token row has `boundVariables` set in metadata. A SOLID fill with a raw `{r,g,b}` color where a variable was declared = silent override.
   - **Inline-override drift**: scan each instance's `overrides`; flag any that change fills, strokes, corner radius, or padding to non-Phase-3 values.
   - **If any check fails**: STOP, report the failing nodes, re-run `use_figma` with corrective JS — re-import via `importComponentByKeyAsync`, re-bind via `getVariableByIdAsync` + `setBoundVariable`, or strip overrides.
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
- **Using `generate_figma_design` as the main writer** — it's reserved for web-app screenshot reference. `use_figma` is the default writer.
- **Calling `use_figma` without loading `figma-use` first** — covers Plugin API gotchas that cause silent JavaScript failures.
- **Running Mobbin searches without reporting findings to chat** — the flow-pattern and per-screen report blocks are the deliverable. AskUserQuestion alone is not a substitute; the user needs to see what was returned before picking direction.
- **Listing Phase 3 component keys in JS comments without `importComponentByKeyAsync` calls** — the keys must appear in actual `importComponentByKeyAsync(...)` calls in the JS body, not just in comments or the `description` parameter. Otherwise the library components aren't imported and the result is orphan frames named like the components but unlinked.
- **Substituting emoji for icon components** — tells that no icon component was imported. Search the library for real icons.
- **Inventing primitives when the library is missing the asset or no library exists** — STOP and ASK the user (link a library, update it, or explicitly approve custom work). Silent invention fragments the design system.
- **Fetching from an empty Figma file in a loop** — if blank, push mode (`generate_figma_design`) seeds it first.
- Inventing pages not supported by PRD, journey, or code.
- Making visual-only mockups with unclear route/component/state boundaries.
- Depending on another design tool's rules or node IDs.
