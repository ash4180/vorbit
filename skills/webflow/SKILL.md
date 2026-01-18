---
name: webflow
version: 1.1.0
description: Use when user says "build in Webflow", "create Webflow page", "develop Webflow template", "Figma to Webflow", "create Webflow component", "add page slots", "create static page template", "build directly in Webflow", "develop from Figma design", or wants to develop layouts and components in Webflow. Supports pages, templates with page slots, and reusable components - with or without Figma designs.
---

# Webflow Development Skill

Develop Webflow pages, templates, and components. Optionally use Figma designs as reference, or build directly in Webflow from requirements.

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

### Step 1: Gather Inputs

Collect required information:
- **Webflow site** - Target site (required)
- **Output type** - Page, Template, or Component
- **Figma URL** - Design reference (optional)

If output type unclear, ask:
> "What would you like to create: a Page (direct build), Template (reusable with slots), or Component (draggable section)?"

### Step 2: Get Design Context

**Mode A - With Figma:**
Use Figma MCP to get design context:
```
mcp__plugin_figma_figma__get_design_context
```
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

### Scenario 1: Landing Page Template from Figma
User: "Create a landing page template from this Figma design"
1. Fetch Figma design
2. Identify: header (fixed), hero/features/CTA (slots), footer (fixed)
3. Create template with 3 page slots
4. Build header and footer as fixed elements
5. Document slot purposes

### Scenario 2: Direct Build Template
User: "Build a landing page template with hero, features, and CTA sections"
1. Clarify layout and structure requirements
2. Plan: header (fixed), hero/features/CTA (slots), footer (fixed)
3. Create template with page slots
4. Apply clean structure and naming
5. Document slot purposes

### Scenario 3: Component Library from Figma
User: "Turn these Figma sections into Webflow components"
1. Fetch Figma design
2. Identify self-contained sections
3. Create each as standalone component
4. Apply consistent class naming
5. Test in page slots

### Scenario 4: Direct Build Component
User: "Create a hero component with headline, subtext, and CTA"
1. Clarify content and layout requirements
2. Plan structure and responsive behavior
3. Build component with clean class naming
4. Document usage

### Scenario 5: Page from Template
User: "Build a page using the landing template"
1. Create page from existing template
2. Add components to slots
3. Customize content
4. Preview and confirm

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

## Rules

1. **Webflow is the output** - Build in Webflow, Figma is optional reference
2. **Ask before building** - Clarify output type, gather requirements
3. **Block on ambiguity** - Never guess unclear requirements
4. **Consistent naming** - Follow class naming conventions
5. **Production safeguards** - Confirm before live changes
6. **Templates enable scale** - Prefer templates for repeatable pages
7. **Components enable reuse** - Extract reusable sections
8. **CMS structure only** - Create structure, don't populate content
9. **Document slots** - Every page slot needs a clear purpose
10. **Respect limits** - Max 40 templates per site
