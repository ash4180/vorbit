<!-- GENERATED from skills/prototype/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Prototype Skill

Create reusable UI prototypes that become production code. Frontend devs swap mocks for real API.

Read and follow `../references/execution-contract.md` before starting.

## Core Principles

- **Ask when it changes the contract**: Use plain-text chat questions when a decision changes the mock boundary, the data contract, or user-visible scope. Make reasonable inline choices for cosmetic details and record them in the final summary.
- **Analyze codebase first**: Find existing patterns before writing any code.
- **Props-driven**: Components receive data as props. Never hardcode data inside components.
- **One mock integration boundary**: Exactly one feature-level container/adapter imports mock data. Presentational components only receive typed props and never import mocks.
- **Linear-first PRD context**: Linear is canonical. Pasted text and explicit local files are legacy fallbacks.
- **Smoke-tested**: The prototype is not complete until its route renders and navigation reaches it.
- **Keep a markdown progress checklist**: Track progress through all phases.

## Phase 0: Detect Platform & Verify Connection

### Pencil Check
Before starting, check if Pencil MCP is available and configured:
1. Check your configured connectors for `"pencil"` — if Pencil tools exist:
2. Check if `<rules-root>/projects/<project-slug>/pencil.md` (resolve the root via `vorbit-resolve-rules`) exists (check with a shell listing)
3. **IF Pencil available but no pencil.md:** Use plain-text chat questions: "Pencil is connected but not configured for this project. Run `$vorbit-pencil` first to sync your design tokens and components? (Recommended)" with options: "Run pencil first (Recommended)", "Skip — continue without sync"
4. **IF user chooses to sync:** Stop and tell them to run `$vorbit-pencil`, then come back
5. **IF pencil.md exists:** Read it — use detected stack, tokens, and component inventory to inform prototype decisions

### Platform Discovery
Preflight required connectors: confirm each needed connector is configured in Codex and inspect its current operation/parameter schemas; never guess tool names. Verify only the external services actually needed. Linear is the canonical PRD provider; Figma is an optional design input, not a competing requirements source.

**IF Figma URL provided:**
1. Use the connected Figma `get_design_context` tool resolved during connector preflight to fetch the design
2. **IF fails:** "Figma connection failed. Reconnect the connector in Codex, then retry." → **STOP**
3. **IF succeeds:** extract design specs

**IF no external services needed:** skip to Phase 1

## Phase 1: Discovery

**Goal**: Understand what prototype needs to be built

**Actions**:
1. Create todo list with all 6 phases (0-5)
2. Resolve PRD context in this order:
   - **Linear URL/ID:** use `get_issue`
   - **Feature name:** use scoped `list_issues` title search, ask if multiple match, then `get_issue`
   - **Explicit pasted PRD or user-specified local file:** use it as a legacy fallback and record provenance
   - **Inaccessible non-Linear URL:** ask the user to paste/export it; do not guess
3. Extract exact `US-###`, `US-###.AC-##`, `F#-S#`, constraints, and unresolved `TBD-###` items. Keep the Linear ticket URL in the handoff.
4. **IF Figma URL provided:**
   - Use design context from Phase 0
   - Extract layout, components, and styling specs
5. **IF purpose is unclear, use plain-text chat questions:**
   - What is this feature for?
   - Who uses it and when?
   - Any reference designs or similar features?
6. **Use plain-text chat questions** to confirm understanding before proceeding

**Output**: Clear statement of prototype purpose

## Phase 2: Codebase Analysis

**Goal**: Understand existing patterns before writing any code

**DO THIS BEFORE WRITING ANY CODE.**

**Actions**:
1. Check `package.json` for framework:
   - `react` → React/TSX
   - `vue` → Vue SFC
   - `svelte` → Svelte
   - None → Vanilla HTML/CSS

2. Scan codebase for patterns:
   - Where pages/routes live (src/pages/, src/routes/, app/)
   - Component structure (how components are organized)
   - Styling approach (CSS modules, Tailwind, styled-components)
   - Existing UI components to reuse (buttons, cards, inputs, layouts)

3. **Report findings to user**:
   ```
   Framework: React/TSX
   Pages location: src/pages/
   Styling: Tailwind CSS
   Existing components: Layout, Card, Button, Input, Table
   ```

4. **Use plain-text chat questions** to confirm: "These are the patterns I found. Should I follow them?"

**Output**: Documented codebase patterns to follow

## Phase 3: Requirements Clarification

**Goal**: Resolve all ambiguities before building

**CRITICAL**: This is the most important phase. DO NOT SKIP.

**IF Figma design provided:**
- Use design specs as the visual source of truth for layout and styling; Linear remains canonical for behavior and scope
- Only ask about behavior not shown in design (actions, empty states)

**IF no Figma design, MUST ask using plain-text chat questions:**
- **Layout**: List, grid, table, or cards?
- **Data fields**: What info should each item show?
- **Actions**: What can users do? (view, edit, delete, filter, etc.)
- **Empty state**: What shows when there's no data?

**Wait for answers before proceeding.**

**Don't invent features:**
- Adding search/filter without asking
- Creating tabs or navigation not requested
- Adding pagination "just in case"
- Inventing extra fields or columns

**Output**: Complete specification for prototype

## Phase 4: Build Prototype

**Goal**: Create prototype following codebase patterns

**Actions**:
1. Create page structure matching codebase patterns:
   ```
   src/pages/[Feature]/
   ├── index.tsx                # Main page
   ├── data-source.ts           # ONLY mock integration boundary
   ├── index.smoke.test.tsx     # Render/navigation smoke test (name follows repo pattern)
   ├── components/              # Feature-specific presentational components
   └── mocks/                   # Mock data (delete when implementing real API)
       └── data.json            # Shape matches API response
   ```

2. Create components with clean props:
   - Components receive data via props, not hardcoded
   - Compose using existing UI components from codebase
   - Feature-specific components under the page folder
   - **IF Figma provided:** Match design specs exactly

3. Create one feature data boundary and mock data:
   - Mock folder under feature: `pages/Feature/mocks/`
   - JSON filename = endpoint: `users.json` → `/api/users`
   - Show exact fields the UI needs (API contract)
   - Choose one route container **or** one adapter as the boundary; do not create both
   - That boundary is the only module that imports file mocks or initializes mock-only state
   - Pass all data and callbacks from that boundary into child components via typed props
   - If the feature has multiple mock payloads, import them all at the same boundary; do not create per-component boundaries

4. **MANDATORY**: Resolve the runtime-neutral Vorbit registry before writing:

   - Use the active runtime contract/resolver for the current project and read its `storage_root` and `project_slug`; do not reconstruct the slug.
   - Registry path: `<storage_root>/projects/<project_slug>/mock-registry.json`.
   - If the current runtime has no resolver, use the project-local fallback `.vorbit/mock-registry.json` and report the fallback explicitly (this registry fallback is intentional and does not override the rule-loading contract's missing-resolver stop).
   - Never hardcode agent-runtime storage paths.

   Register mocks in the resolved registry:

   The registry root is `{ "version": "1.1", "mocks": [...] }`. The snippets below are individual entries appended to `mocks`.

   The following are alternatives. Register the one boundary actually used; do not create both forms for the same feature.

   **For mock files:**
   ```json
   {
     "feature": "[Feature name]",
     "type": "file",
     "path": "src/pages/Feature/mocks/data.json",
     "endpoint": "proposed:GET /api/[resource]",
     "createdBy": "prototype",
     "createdAt": "[ISO timestamp]",
     "components": ["src/pages/Feature/data-source.ts"]
   }
   ```

   **For mock state (useState, stores, context):**
   ```json
   {
     "feature": "[Feature name]",
     "type": "state",
     "path": "src/pages/Feature/index.tsx",
     "location": "useState:users (line 15)",
     "endpoint": "proposed:GET /api/[resource]",
     "stateType": "useState",
     "createdBy": "prototype",
     "createdAt": "[ISO timestamp]",
     "components": ["src/pages/Feature/index.tsx"]
   }
   ```
   - Create registry file if doesn't exist
   - Append to existing mocks array if file exists

5. **MANDATORY**: The single mock boundary MUST have the replacement TODO next to its imports:
   ```tsx
   import mockData from './mocks/data.json';
   // TODO: Replace this mock boundary with the real API client.
   ```

   Child components must not import anything from `mocks/`.

6. Update todos as each component is completed

**Mock Data Rules:**
- Show only fields the UI actually uses
- Don't add fields "for completeness"
- Don't create mock utilities, factories, or generators
- Don't duplicate same data in different mock files
- Keep the integration seam boring: one boundary can be replaced without editing presentational components

**Output**: Working prototype with clean structure

## Phase 5: Verification & Handoff

**Goal**: Ensure prototype is ready for frontend handover

**Actions**:
1. **Verify checklist**:
   - [ ] Components receive data via props (not hardcoded)
   - [ ] Exactly one feature-level module imports from `mocks/`
   - [ ] That boundary has `// TODO: Replace this mock boundary with the real API client.`
   - [ ] No presentational component imports mocks or knows whether data is mocked
   - [ ] Page is navigable/renderable
   - [ ] Uses existing UI components from codebase
   - [ ] Matches codebase styling patterns
   - [ ] **IF Figma:** Matches design specs

2. **Run render/navigation smoke tests (required):**
   - Reuse the project's existing test runner and routing test pattern; search before adding a test
   - Assert the feature route renders its primary observable content
   - Assert an existing navigation entry or direct router navigation reaches the feature route
   - Use the real router configuration and the feature's mock data boundary; do not mock the router or service layer
   - Run the narrow smoke test first, then the project's relevant typecheck/build command
   - If no test harness exists, run the real local app and perform an equivalent browser/HTTP render plus navigation smoke check. Report the exact commands and evidence; do not install a framework just for the prototype

3. **Present summary to user**:
   ```
   Created:
   - src/pages/Feature/index.tsx
   - src/pages/Feature/components/...
   - src/pages/Feature/mocks/...

   Mock data registered in [resolved Vorbit project registry path]:
   - data-source.ts (single boundary) → mocks/data.json → GET /api/...

   Verified:
   - [smoke-test command] — route render + navigation passed

   Used existing components:
   - Layout, Card, Button, Input

   Next steps:
   - Review with team
   - $vorbit-epic to create issues
   - $vorbit-cleanup-mocks [feature] before backend handover
   ```

4. Mark all todos complete

**Output**: Complete, documented prototype ready for handover

---

# Prototype Schema & Validation

## What is a Prototype?

A prototype is:
- A **complete page or feature** users can interact with
- **Composition** of multiple components with clean props
- **Mock data** that defines the API contract
- **Reusable structure** - becomes production code

A prototype is NOT:
- A single reusable component (that's a component, not a prototype)
- Throwaway demo code
- Fully covered by implementation tests; only render/navigation smoke coverage is required here

The directory layout, mock rules, and verification gates for these properties live in Phases 4-5; the Phase 5 checklist is the single completion gate.
