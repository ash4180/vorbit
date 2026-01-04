---
description: Generate UI prototype fast. Creates page/feature with mock data.
argument-hint: [feature name, Notion PRD URL, or Figma URL]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, TodoWrite, mcp__plugin_Notion_notion__*, mcp__plugin_figma_figma__*
---

# Prototype Creation Workflow

Guide the user through creating a reusable UI prototype that becomes production code. Frontend devs will swap mocks for real API.

## Core Principles

- **Use AskUserQuestion for ANY uncertainty**: If anything is unclear, ASK. Don't guess. Don't invent.
- **Analyze codebase first**: Find existing patterns before writing any code.
- **Props-driven**: Components receive data as props. Never hardcode data inside components.
- **Single mock import**: Each component imports mock at top of file, with `// TODO: Replace with real API`.
- **Use TodoWrite**: Track progress through all phases.

**Initial request:** $ARGUMENTS

---

## Phase 0: Verify External Connections (if needed)

**Goal**: Ensure Notion/Figma access works before proceeding

**IF Notion URL provided OR wants to fetch PRD from Notion:**
1. Run a lightweight test: use `notion-find` to search for "test"
2. **IF the call fails (auth error, token expired, connection refused):**
   - Tell the user: "Notion connection has expired. Please run `/mcp` and reconnect the Notion server, then run this command again."
   - **STOP HERE** - do not proceed
3. **IF the call succeeds:** proceed to Phase 1

**IF Figma URL provided:**
1. Use `mcp__plugin_figma_figma__get_design_context` to fetch the design
2. **IF the call fails:**
   - Tell the user: "Figma connection failed. Please run `/mcp` and reconnect the Figma server, then run this command again."
   - **STOP HERE** - do not proceed
3. **IF the call succeeds:** extract design specs for Phase 3

**IF no external services needed:** skip to Phase 1

---

## Phase 1: Discovery

**Goal**: Understand what prototype needs to be built

**Actions**:
1. Create todo list with all 6 phases (0-5)
2. **IF Notion PRD URL provided:**
   - Fetch PRD from Notion
   - Extract user stories and UI requirements
   - Summarize what needs to be prototyped
3. **IF Figma URL provided:**
   - Use design context from Phase 0
   - Extract layout, components, and styling specs
   - Note any design tokens or variables
4. **IF feature name provided:**
   - Search Notion for existing PRD
   - If found, extract requirements
   - If not found, gather requirements via conversation
5. **IF purpose is unclear, use AskUserQuestion:**
   - What is this feature for?
   - Who uses it and when?
   - Any reference designs or similar features?
6. **Use AskUserQuestion** to confirm understanding before proceeding

**Output**: Clear statement of prototype purpose

---

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

---

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

**Example**: User said "user list" → ask what columns. Don't guess.

**Output**: Complete specification for prototype

---

## Phase 4: Build Prototype

**Goal**: Create prototype following codebase patterns

**Load prototype skill** using Skill tool before building.

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

4. **MANDATORY**: Every mock import MUST have TODO comment:
   ```tsx
   import mockData from './mocks/data.json';
   // TODO: Replace with real API
   ```

5. Update todos as each component is completed

**Mock Data Rules:**
- Show only fields the UI actually uses
- Don't add fields "for completeness"
- Don't create mock utilities, factories, or generators
- Don't duplicate same data in different mock files

**Output**: Working prototype with clean structure

---

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

   Mock data (delete mocks/ when implementing real API):
   - mocks/data.json → GET /api/...

   Used existing components:
   - Layout, Card, Button, Input

   Next: Review with team, then /vorbit:implement:epic
   ```

3. Mark all todos complete

**Output**: Complete, documented prototype ready for handover

---

## Key Decision Points (Use AskUserQuestion)

At these points, **MUST use AskUserQuestion** to get user confirmation:

1. **After Phase 1**: "Is this understanding correct? [summary]"
2. **After Phase 2**: "Should I follow these codebase patterns? [patterns]"
3. **After Phase 3**: "Ready to build with these specs? [layout, fields, actions]"
4. **After Phase 5**: "Prototype complete. Any changes needed?"

---

## Quality Standards

Every prototype must meet these standards:
- Follows existing codebase patterns
- Components are props-driven (reusable as-is)
- Mock imports in single location per component
- TODO comments mark all mock → real API swaps
- No invented features user didn't request
- Uses existing UI components (don't recreate)
- Matches Figma design (if provided)

---

## Anti-Patterns (DON'T)

- Starting to code before analyzing codebase
- Guessing layout/fields/actions without asking
- Adding search, filter, tabs, pagination "just in case"
- Hardcoding data in components
- Creating mock utilities or factories
- Duplicating mock data across files
- Skipping TODO comments on mock imports
- Creating new UI components when existing ones work
- Deviating from Figma design without asking

---

**Begin with Phase 0 (if Notion/Figma needed) or Phase 1: Discovery**
