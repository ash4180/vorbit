---
name: webflow
description: Use when the user explicitly asks to create or modify a Webflow page, reusable template, page slot, CMS structure, or component, either from requirements or a Figma reference. It requires a connected target Webflow site, confirms ambiguous or live-site changes, and writes to Webflow. Do not use for Figma design creation, general frontend code, publishing-only requests, or advice that does not require Webflow changes.
---

# Webflow Development Skill

Develop Webflow pages, templates, and components. Optionally use Figma designs as reference, or build directly in Webflow from requirements.

Read and follow `../_shared/execution-contract.md` before starting.

## Core Concept

This skill treats Webflow as the **development platform**. Two modes supported:
- **With Figma**: Use Figma design as visual reference and specification
- **Direct build**: Build from requirements/description without Figma

## Output Types

Three distinct output types, each serving different purposes:

| Output Type | Purpose | When to Use |
|-------------|---------|-------------|
| **Page** | Direct page build | One-off pages, quick builds |
| **Template** | Reusable scaffold with page slots | Landing pages, feature pages, repeated patterns |
| **Component** | Draggable element for slots | Reusable sections (hero, features, CTA) |

### Pages
Direct implementation of a Figma design as a Webflow page. Use for unique pages that won't be replicated.

### Templates
Reusable page scaffolds with fixed elements (header, footer) and **page slots** where marketers can drop components. Best for:
- Landing pages
- Feature pages
- Use case pages
- Target persona pages

Templates enable the Designer → Marketer workflow: designers create templates, marketers assemble pages.

### Components
Standalone, draggable sections that fit into page slots. Build as reusable elements that marketers can add to template slots.

## Workflow

### Step 0: Pencil Check

Before starting, check if Pencil MCP is available and configured:
1. Run `ToolSearch` for `"pencil"` — if Pencil tools exist:
2. Check if `.claude/rules/pencil.md` exists (Glob for it)
3. **IF Pencil available but no pencil.md:** Use `AskUserQuestion`: "Pencil is connected but not configured for this project. Run `/vorbit:design:pencil` first to sync your design tokens and components? (Recommended)" with options: "Run pencil first (Recommended)", "Skip — continue without sync"
4. **IF user chooses to sync:** Stop and tell them to run `/vorbit:design:pencil`, then come back
5. **IF pencil.md exists:** Read it — use detected stack, tokens, and component inventory to inform Webflow development decisions

### Step 1: Gather Inputs

Collect required information:
- **Webflow site** - Target site (required)
- **Output type** - Page, Template, or Component
- **Figma URL** - Design reference (optional)

If output type unclear, ask:
> "What would you like to create: a Page (direct build), Template (reusable with slots), or Component (draggable section)?"

### Step 2: Get Design Context

**Mode A - With Figma:**
Use the connected Figma MCP's `get_design_context` tool (resolve the connector per `_shared/mcp-tool-routing.md`).
Extract: layout structure, styling, component hierarchy, design tokens.

**Mode B - Direct Build:**
Gather requirements through conversation:
- What sections/elements are needed?
- What layout pattern? (single column, two column, grid)
- What styling preferences? (colors, fonts)
- Reference sites or existing pages?

### Step 3: Analyze and Plan

**With Figma:** Map Figma elements to Webflow structure using `references/component-mapping.md`.

**Direct Build:** Plan structure based on requirements:
- Sections and their purposes
- Layout approach per section
- Component reusability

**For Templates:** Identify:
- Fixed elements (header, footer, sidebar)
- Variable content areas → page slots
- Repeating patterns → potential components

**For Components:** Identify:
- Self-contained boundaries
- Internal structure
- Responsive behavior

### Step 4: Block and Ask

When structure or mapping is unclear:
- **STOP** and ask the user
- Explain the options
- Wait for decision

Never guess on ambiguous requirements.

### Step 5: Build in Webflow

Use Webflow MCP tools (see `references/mcp-tools.md` for detailed tool reference):

| Tool | Purpose |
|------|---------|
| `element_builder` | Create page structure (sections, containers, divs) |
| `element_tool` | Select, modify, and configure existing elements |
| `style_tool` | Create and apply CSS classes |
| `component_tool` | Register components and create instances |

**Workflow:**
1. Use `element_builder` to create structure (max 3 levels per call)
2. Use `style_tool` to create and configure styles
3. Use `element_tool` to apply styles and set content
4. Use `component_tool` to register reusable components

**For Templates:**
- Add Page Slot elements where content varies
- Document slot purposes
- Keep fixed elements (header, footer) outside slots

### Step 6: Confirm and Document

Present summary:
```
Created: [Template/Page/Component] "[Name]"
Location: [Webflow site/page path]

Structure:
- [List of sections/elements created]

Page Slots (if template):
- [Slot name]: [Purpose]

Classes created:
- [List of new classes]

Next: Add components to slots, or create more components
```

## Class Naming Convention

Follow consistent naming for Webflow classes:

| Pattern | Example | Use For |
|---------|---------|---------|
| `section-[name]` | `section-hero` | Page sections |
| `[component]-wrapper` | `features-wrapper` | Component containers |
| `[component]-[element]` | `hero-heading` | Elements within components |
| `is-[state]` | `is-active` | State modifiers |
| `has-[feature]` | `has-background` | Feature modifiers |

## Production Safeguards

When working with production sites:

1. **Confirm before changes** - Always ask before modifying live sites
2. **Show diff first** - Describe what will change before applying
3. **Backup awareness** - Remind user to publish/backup before major changes

## CMS Integration

For templates with CMS:
- Create CMS structure (collections, fields)
- Do NOT populate content
- Map Figma fields to CMS fields
- Document field purposes

Figma controls layout/style; Webflow owns content.

## Common Scenarios

Canonical walkthrough — landing page template from Figma ("Create a landing page template from this Figma design"):
1. Fetch Figma design
2. Identify: header (fixed), hero/features/CTA (slots), footer (fixed)
3. Create template with 3 page slots
4. Build header and footer as fixed elements
5. Document slot purposes

Variants follow the same shape:
- **Direct build** (template or component): replace step 1 with gathering requirements through conversation (Step 2 Mode B); the rest is identical.
- **Components from Figma**: identify self-contained sections instead of slots, create each as a standalone component, test in page slots.
- **Page from existing template**: create the page from the template, add components to slots, customize content, preview and confirm.

## Error Handling

| Issue | Action |
|-------|--------|
| Figma element has no Webflow equivalent | Block and ask user |
| Requirements unclear | Ask clarifying questions |
| Class name conflict | Append unique suffix, inform user |
| Template slot limit (40 per site) | Warn user before creating |
| Production site changes | Require explicit confirmation |

## Additional Resources

### Reference Files

For detailed mapping and patterns, consult:
- **`references/mcp-tools.md`** - Webflow MCP tools: when to use each tool
- **`references/component-mapping.md`** - Figma to Webflow element mapping rules
- **`references/templates.md`** - Page template patterns and slot strategies

### Example Files

Working examples in `examples/`:
- **`examples/landing-page.md`** - Complete landing page template workflow

## Integration with Vorbit

This skill works standalone or chains with other vorbit commands:

| Flow | Description |
|------|-------------|
| Standalone (Figma) | `/vorbit:design:webflow [figma-url]` |
| Standalone (Direct) | `/vorbit:design:webflow [description]` |
| From PRD | PRD → `/vorbit:design:webflow` |
