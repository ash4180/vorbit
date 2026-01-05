---
description: Develop Webflow pages, templates, or components. Supports Figma designs or direct build from requirements.
argument-hint: [Figma URL or description]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, TodoWrite, mcp__plugin_figma_figma__*, mcp__plugin_figma_figma-desktop__*, mcp__webflow__*
---

# Webflow Development Workflow

Develop Webflow pages, templates, or components. Two modes:
- **With Figma**: Use Figma design as visual reference
- **Direct Build**: Build from requirements without Figma

## Core Principles

- **Use AskUserQuestion for ANY uncertainty**: If output type, structure, or requirements unclear, ASK. Don't guess.
- **Webflow is the output**: Build in Webflow, Figma is optional reference
- **Block on ambiguity**: When requirements or mappings unclear, stop and ask
- **Use TodoWrite**: Track progress through all phases

**Initial request:** $ARGUMENTS

---

## Phase 0: Determine Mode

**Goal**: Identify build mode and verify connections

**Check arguments:**
- Contains `figma.com` URL → **Figma Mode**
- Contains description/requirements → **Direct Build Mode**
- Unclear → Ask user which mode

**IF Figma Mode:**
1. Extract fileKey and nodeId from URL
2. Use `mcp__plugin_figma_figma__get_design_context` to fetch design
3. **IF fails:** Tell user "Figma connection failed. Run `/mcp` and reconnect Figma, then retry." → STOP
4. **IF succeeds:** Proceed to Phase 1

**IF Direct Build Mode:**
1. Proceed to Phase 1 with requirements gathering

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

**Actions**:
1. Create todo list with all phases

**IF Figma Mode:**
2. Analyze Figma design structure:
   - Identify major sections/frames
   - Note layout patterns (auto-layout, grid)
   - Extract styling (colors, typography)
   - Identify reusable patterns

**IF Direct Build Mode:**
2. Gather requirements through conversation:
   - What sections/elements are needed?
   - What layout pattern? (single column, two column, grid)
   - What styling preferences? (colors, fonts)
   - Reference sites or existing pages?

3. **Use AskUserQuestion** to determine output type:
   - **Page**: Direct build for unique pages
   - **Template**: Reusable scaffold with page slots
   - **Component**: Draggable element for slots

4. Confirm understanding before proceeding

**Output**: Clear specification of what to build

---

## Phase 2: Structure Analysis

**Goal**: Plan Webflow structure using existing project styles

**Load webflow skill** using Skill tool for mapping reference.

**First: Check Existing Styles**
1. Use `style_tool` with `getAllStyles()` to get existing project styles
2. Document existing naming patterns (e.g., `btn-`, `section-`, `text-`)
3. Identify reusable styles to avoid duplicates
4. Follow the project's established conventions

**Actions**:

**IF Figma Mode:**
1. For each Figma section, determine Webflow equivalent:
   - Frames → Sections, Div Blocks
   - Auto-layout → Flexbox
   - Text → Headings, Paragraphs
   - Images → Image elements
   - Components → Webflow components

**IF Direct Build Mode:**
1. Plan structure based on requirements:
   - Sections and their purposes
   - Layout approach per section
   - Component reusability

2. **For Templates**, identify:
   - Fixed elements (header, footer) → Build directly
   - Variable sections → Page slots
   - Repeating patterns → Create as components

3. **For Components**, identify:
   - Self-contained boundaries
   - Internal structure
   - Responsive behavior

4. Plan class naming following conventions:
   - `section-[name]` for sections
   - `[component]-wrapper` for containers
   - `[component]-[element]` for children
   - `is-[state]` for modifiers

5. **Block and ask** when unclear

**Output**: Documented structure plan

---

## Phase 3: Build in Webflow

**Goal**: Create the Webflow page/template/component

**MCP Tools** (see webflow skill `references/mcp-tools.md` for full details):

| Tool | Use For |
|------|---------|
| `element_builder` | Create sections, containers, divs (max 3 levels per call) |
| `element_tool` | Select elements, set text/links/images, apply styles |
| `style_tool` | Create CSS classes, set properties per breakpoint |
| `component_tool` | Register components, create instances |

**Build Workflow:**
1. `element_builder` → Create structure
2. `style_tool` → Create and configure styles
3. `element_tool` → Apply styles, set content
4. `component_tool` → Register reusable components

**For Templates:**
1. Create page template in Webflow
2. Build fixed elements (header, footer)
3. Add Page Slot elements where content varies
4. Name each slot clearly (e.g., `hero-slot`, `features-slot`)
5. Apply styles following Figma specs

**For Components:**
1. Create component in Webflow
2. Build internal structure
3. Apply responsive behavior
4. Test in isolation

**For Pages:**
1. Create page (or use existing template)
2. Build sections following Figma structure
3. Apply all styling
4. Add components where appropriate

**Throughout:**
- Follow class naming conventions
- Match Figma styling closely
- Handle responsive breakpoints
- Update todos as sections complete

---

## Phase 4: Production Safeguards

**Goal**: Ensure safe deployment

**For all changes:**
1. Review what was created
2. **For production sites**: Require explicit confirmation before applying
3. Document any changes to existing classes/elements

---

## Phase 5: Summary & Handoff

**Goal**: Provide clear summary of what was built

**Actions**:
1. Present summary:
   ```
   Created: [Template/Page/Component] "[Name]"
   Location: [Webflow site/page]

   Structure:
   - [List of sections/slots/elements]

   Page Slots (if template):
   - [slot-name]: [Purpose]

   Components (if created):
   - [Component names and purposes]

   Classes created:
   - [List of new classes]

   Next steps:
   - [Recommendations]
   ```

2. Mark all todos complete

**Output**: Complete handoff documentation

---

## Key Decision Points

At these points, **MUST use AskUserQuestion**:

1. **Output type unclear**: "What would you like to create: Page, Template, or Component?"
2. **Fixed vs variable**: "Should this section be fixed or a page slot?"
3. **Mapping ambiguous**: "This Figma element could be [X] or [Y]. Which approach?"
4. **Component boundary**: "Is this one component or should I split it?"
5. **Production changes**: "This will modify [site]. Proceed?"

---

## Integration with Webflow Skill

**MUST load webflow skill** for:
- MCP tool usage guide (`references/mcp-tools.md`)
- Component mapping rules (`references/component-mapping.md`)
- Template patterns (`references/templates.md`)
- Class naming conventions

---

## Anti-Patterns (DON'T)

- Starting to build without gathering requirements (Figma or conversation)
- Guessing output type without asking
- Creating page slots without clear purposes
- Using inconsistent class naming
- Making production changes without confirmation
- Skipping the structure analysis phase

---

## Quality Standards

Every Webflow build must meet:
- [ ] Matches design/requirements closely
- [ ] Follows class naming conventions
- [ ] Page slots clearly named and documented (for templates)
- [ ] Responsive behavior handled
- [ ] Production safeguards followed
- [ ] Summary provided to user

---

**Begin with Phase 0: Determine Mode**
