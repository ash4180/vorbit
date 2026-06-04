---
name: prototype
version: 1.1.0
description: Use when user says "create prototype", "build UI mockup", "quick prototype", "mock this feature", "prototype page", or wants to generate UI with mock data that becomes production code by swapping mocks for real API.
---

# Prototype Skill

Create reusable UI prototypes that become production code. Frontend devs swap mocks for real API.

## Core Principles

- **Use AskUserQuestion for ANY uncertainty**: If anything is unclear, ASK. Don't guess.
- **Analyze codebase first**: Find existing patterns before writing any code.
- **Props-driven**: Components receive data as props. Never hardcode data inside components.
- **Single mock import**: Each component imports mock at top of file, with `// TODO: Replace with real API`.
- **Use TaskCreate/TaskUpdate**: Track progress through all phases.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Phase 0: Detect Platform & Verify Connection

### Pencil Check

Follow `_shared/pencil-check.md` — shared 6-step procedure that detects Pencil connection, checks for `.claude/rules/pencil.md`, and routes the user through `/vorbit:design:pencil` sync if needed. The same procedure is used by `/vorbit:implement:webflow`; keeping it shared prevents drift.

### Platform Discovery
Read and follow `_shared/mcp-tool-routing.md`. Discover connected platforms, ask user which to use, and verify connection.

**IF Figma URL provided:**
1. Use `mcp__figma__get_design_context` to fetch the design (canonical per `_shared/mcp-tool-routing.md`). `mcp__plugin_figma_figma__get_design_context` also works if the bare server isn't connected.
2. **IF fails:** "Figma connection failed. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** extract design specs

**IF no external services needed:** skip to Phase 1

## Phase 1: Discovery

**Goal**: Understand what prototype needs to be built

**Actions**:
1. Create todo list with all 6 phases (0-5)
2. **IF Notion PRD URL provided:**
   - Fetch PRD from Notion
   - Extract user stories and UI requirements
3. **IF Figma URL provided:**
   - Use design context from Phase 0
   - Extract layout, components, and styling specs
4. **IF feature name provided:**
   - Search Notion for existing PRD
   - If not found, gather requirements via conversation
5. **IF purpose is unclear, use AskUserQuestion:**
   - What is this feature for?
   - Who uses it and when?
   - Any reference designs or similar features?
6. **Use AskUserQuestion** to confirm understanding before proceeding

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

4. **Use AskUserQuestion** to confirm: "These are the patterns I found. Should I follow them?"

**Output**: Documented codebase patterns to follow

## Phase 3: Requirements Clarification

**Goal**: Resolve all ambiguities before building

**CRITICAL**: This is the most important phase. DO NOT SKIP.

**IF Figma design provided:**
- Use design specs as source of truth for layout, fields, styling
- Only ask about behavior not shown in design (actions, empty states)

**IF no Figma design, MUST ask using AskUserQuestion:**
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
   ├── index.tsx           # Main page
   ├── components/         # Feature-specific components
   └── mocks/              # Mock data (delete when implementing real API)
       └── data.json       # Shape matches API response
   ```

2. Create components with clean props:
   - Components receive data via props, not hardcoded
   - Compose using existing UI components from codebase
   - Feature-specific components under the page folder
   - **IF Figma provided:** Match design specs exactly

3. Create mock data:
   - Mock folder under feature: `pages/Feature/mocks/`
   - JSON filename = endpoint: `users.json` → `/api/users`
   - Show exact fields the UI needs (API contract)
   - If multiple components need SAME data, share the mock

4. **MANDATORY**: Register every mock — file and state — in `.claude/mock-registry.json` with `"createdBy": "prototype"`. See `_shared/mock-registry.md` for the schema, write templates, when to register, and what to capture. Create the registry if absent; otherwise append to the `mocks` array.

5. **MANDATORY**: Every mock (file or state) MUST have TODO comment:
   ```tsx
   import mockData from './mocks/data.json';
   // TODO: Replace with real API
   ```

6. Update todos as each component is completed

**Mock Data Rules:**
- Show only fields the UI actually uses
- Don't add fields "for completeness"
- Don't create mock utilities, factories, or generators
- Don't duplicate same data in different mock files

**Output**: Working prototype with clean structure

## Phase 5: Verification & Handoff

**Goal**: Ensure prototype is ready for frontend handover

**Actions**:
1. **Verify checklist**:
   - [ ] Components receive data via props (not hardcoded)
   - [ ] Mock import in ONE place per component
   - [ ] Every mock import has `// TODO: Replace with real API` comment
   - [ ] Components needing same data share the same mock file
   - [ ] Page is navigable/renderable
   - [ ] Uses existing UI components from codebase
   - [ ] Matches codebase styling patterns
   - [ ] **IF Figma:** Matches design specs

2. **Present summary to user**:
   ```
   Created:
   - src/pages/Feature/index.tsx
   - src/pages/Feature/components/...
   - src/pages/Feature/mocks/...

   Mock data registered in .claude/mock-registry.json:
   - mocks/data.json → GET /api/...

   Used existing components:
   - Layout, Card, Button, Input

   Next steps:
   - Review with team
   - /vorbit:implement:epic to create issues
   - /vorbit:implement:cleanup-mocks [feature] before backend handover
   ```

3. Mark all todos complete

**Output**: Complete, documented prototype ready for handover

---

# Prototype Reference

## What is a Prototype?

A prototype is:
- A **complete page or feature** users can interact with
- **Composition** of multiple components with clean props
- **Mock data** that defines the API contract
- **Reusable structure** - becomes production code

A prototype is NOT:
- A single reusable component (that's a component, not a prototype)
- Throwaway demo code
- Fully tested (tests come in implementation phase)

## Page/Feature Structure

```
src/
└── pages/                    # or routes/, views/
    └── [FeatureName]/
        ├── index.tsx         # Main page component
        ├── components/       # Feature-specific components
        │   ├── Header.tsx
        │   ├── List.tsx
        │   └── Form.tsx
        └── mocks/            # Mock data FOR THIS FEATURE
            └── data.json     # → swap to real API later
```

The build checklist and anti-patterns live inline in Phases 3–5 (where they're actionable), so they're not repeated here.
