# Webflow MCP Tools Reference

Guide for which MCP tools to call when building in Webflow. Tools are exposed by the official Webflow MCP server.

## Tool Categories

The Webflow MCP server exposes two categories of tools:

| Category | Purpose | Requires |
|----------|---------|----------|
| **Data API Tools** | Site info, CMS, collections | OAuth authentication |
| **Designer API Tools** | Create elements, styles, components | MCP Companion App open in Designer |

## Data API Tools

### get_sites

Retrieves all Webflow sites accessible to the authenticated user.

**When to use:**
- Starting a project to discover available sites
- Listing sites for user selection
- Getting workspace context

**Returns:** Site IDs, names, preview URLs, custom domains, localization settings

---

### get_site

Retrieves detailed information about a specific site.

**When to use:**
- After user selects a site to work on
- Getting site-specific configuration before building
- Checking custom domains and localization settings

**Parameters:**
- `siteId` (required): The site identifier

---

## Designer API Tools

**Requirement:** The MCP Companion App must be open in Webflow Designer for all Designer API tools to function.

### element_builder

Creates nested elements on the current page.

**When to use:**
- Creating page structure (sections, containers, divs)
- Building component internal structure
- Adding text, images, links to page

**Parameters:**
- `siteId` (required): Site identifier
- `actions` (required): Array of creation actions containing:
  - `parentElementId`: Object with component and element IDs
  - `creationPosition`: "append" or "prepend"
  - `elementSchema`: Element definition with type and optional children

**Supported element types:**
- **Containers** (can have children): `section`, `container`, `div`, `flexbox`
- **Content**: `h1`-`h6`, `p`, `text`, `image`, `link`
- **Forms**: `form`, form inputs

**Nesting rules:**
- Maximum 3 levels of nesting per call
- Only container-type elements can have children
- For deeper structures, make multiple sequential calls

**Example workflow:**
```
1. Create section with container child
2. Select container
3. Create content elements inside container
```

---

### element_tool

Performs actions on existing elements.

**Actions available:**

| Action | Purpose | When to Use |
|--------|---------|-------------|
| `getAllElements` | Get all page elements | Inspecting existing page structure |
| `getSelectedElement` | Get selected element details | After user selects an element |
| `selectElement` | Select element by ID | Before modifying specific element |
| `addOrUpdateAttribute` | Add custom attributes | Setting data attributes, aria labels |
| `setText` | Set text content | Populating headings, paragraphs |
| `removeAttribute` | Delete attributes | Cleaning up elements |
| `updateIdAttribute` | Change HTML id | Setting unique identifiers |
| `setLink` | Configure link destination | Making elements clickable |
| `setHeadingLevel` | Change heading level | Converting h1 to h2, etc. |
| `setStyle` | Apply existing styles | Applying classes to elements |
| `setImageAsset` | Set image source | Adding images to img elements |

**Workflow pattern:**
```
1. Use getAllElements to understand page structure
2. Use selectElement to target specific element
3. Use setText/setStyle/etc. to modify
```

---

### style_tool

Creates and manages CSS styles (classes).

**When to use:**
- Creating reusable class styles
- Setting responsive styles per breakpoint
- Managing pseudo-states (hover, active, focus)

**Actions available:**

| Action | Purpose |
|--------|---------|
| `createStyle(name)` | Create new style with unique name |
| `getAllStyles()` | List all existing styles |
| `getStyleByName(name)` | Get specific style by name |
| `setProperty(name, value)` | Set single CSS property |
| `setProperties(map, options)` | Batch-set multiple properties |
| `removeStyle()` | Delete a style |
| `removeStyleProperty()` | Remove specific property |

**Responsive options:**

| Breakpoint | Description |
|------------|-------------|
| `xxl` | Extra extra large |
| `xl` | Extra large |
| `large` | Large screens |
| `main` | Default (desktop) |
| `medium` | Tablet |
| `small` | Mobile landscape |
| `tiny` | Mobile portrait |

**Pseudo-states:** `hover`, `active`, `focus`, `visited`, `focus-visible`, `focus-within`

**Workflow:**
```
1. createStyle("hero-heading")
2. setProperties({ "font-size": "48px", "font-weight": "bold" })
3. setProperties({ "font-size": "32px" }, { breakpoint: "small" })
4. Apply to element via element_tool setStyle action
```

**Limitation:** Only CSS classes supported; HTML tag styling not available.

---

### component_tool

Registers and manages reusable components.

**When to use:**
- Creating reusable component definitions
- Adding component instances to pages
- Working inside component edit mode

**Actions available:**

| Action | Purpose |
|--------|---------|
| `registerComponent(name, rootElement)` | Convert element tree to component definition |
| `createInstance(componentDef)` | Add component instance to canvas |
| `enterComponent()` | Enter component edit mode |
| `exitComponent()` | Exit component edit mode |
| `getComponent()` | Get current component definition |
| `getRootElement()` | Get root element of current component |
| `getComponentName()` | Get component name |
| `setComponentName(name)` | Rename component |

**Workflow for creating component:**
```
1. Build element structure with element_builder
2. Select the root element (parent container)
3. registerComponent("hero-section", rootElement)
4. Component now available for reuse
```

**Workflow for using component:**
```
1. Get component definition
2. createInstance(componentDef)
3. Position in desired location
```

**Limitation:** Component properties (editable text, images) not yet supported via API.

---

## Tool Selection Guide

### By Task

| Task | Primary Tool | Supporting Tools |
|------|--------------|------------------|
| **Create page structure** | element_builder | style_tool |
| **Create template** | element_builder | style_tool, component_tool |
| **Create component** | element_builder, component_tool | style_tool |
| **Apply styling** | style_tool | element_tool (setStyle) |
| **Add content** | element_tool (setText, setImageAsset) | - |
| **Configure links** | element_tool (setLink) | - |
| **Check existing structure** | element_tool (getAllElements) | - |
| **Site discovery** | get_sites, get_site | - |

### By Workflow Phase

| Phase | Tools Used |
|-------|------------|
| **Discovery** | get_sites, get_site, element_tool (getAllElements) |
| **Structure creation** | element_builder |
| **Styling** | style_tool, element_tool (setStyle) |
| **Content population** | element_tool (setText, setImageAsset, setLink) |
| **Component creation** | component_tool |
| **Validation** | element_tool (getAllElements, getSelectedElement) |

---

## Respecting Existing Project Styles

**Critical:** Before creating new styles, always check existing project styles.

### Discovery Workflow

```
1. style_tool: getAllStyles() → Get all existing styles
2. Analyze naming patterns (e.g., "btn-", "section-", "heading-")
3. Identify reusable styles for current task
4. Only create new styles when no match exists
```

### Style Reuse Rules

| Scenario | Action |
|----------|--------|
| Exact style match exists | Reuse existing style |
| Similar style exists | Extend with combo class OR reuse if close enough |
| No match | Create new following project conventions |
| Conflicting naming pattern | Ask user which convention to follow |

### Naming Convention Discovery

Before building, identify the project's patterns:
- Button styles: `btn-primary`, `button-main`, etc.
- Section styles: `section-hero`, `s-hero`, etc.
- Text styles: `heading-lg`, `text-body`, etc.
- Utility styles: `is-`, `has-`, `u-`

**Always follow discovered patterns rather than imposing new conventions.**

---

## Common Patterns

### Pattern 1: Create Styled Section

```
1. element_builder: Create section with container
2. style_tool: Create "section-hero" style
3. style_tool: Set background, padding properties
4. element_tool: Apply style to section
5. element_builder: Add child elements (heading, text, button)
```

### Pattern 2: Build Template with Slots

```
1. element_builder: Create header section (fixed)
2. element_builder: Create main content area
3. element_builder: Add slot placeholders as divs
4. style_tool: Create slot-specific styles
5. element_builder: Create footer section (fixed)
6. Document slot locations for later component insertion
```

### Pattern 3: Create Reusable Component

```
1. element_builder: Build complete element structure
2. style_tool: Create and apply all necessary styles
3. element_tool: Verify structure with getAllElements
4. component_tool: registerComponent with root element
5. Verify component appears in components panel
```

### Pattern 4: Add Component Instance

```
1. element_tool: getAllElements to find target location
2. element_tool: selectElement for parent container
3. component_tool: createInstance with component definition
4. element_tool: Customize instance content if needed
```

---

## Error Handling

| Error | Likely Cause | Resolution |
|-------|--------------|------------|
| Designer API calls fail | Companion App not open | Open MCP Companion App in Designer |
| Style name conflict | Duplicate name | Use unique name or get existing style |
| Element not found | Invalid ID | Use getAllElements to find correct IDs |
| Nesting limit exceeded | >3 levels in single call | Split into multiple element_builder calls |
| Component registration fails | No child elements | Ensure root has at least one child |

---

## Prerequisites

1. **Webflow MCP Server** connected and authenticated
2. **MCP Companion App** installed and open in Webflow Designer
3. **Site selected** with appropriate edit permissions
4. **Page open** in Designer for element operations

---

## Sources

- [Webflow MCP Server Overview](https://developers.webflow.com/mcp/reference/overview)
- [Webflow Designer API: Elements](https://developers.webflow.com/designer/reference/elements-overview)
- [Webflow Designer API: Styles](https://developers.webflow.com/designer/reference/styles-overview)
- [Webflow Designer API: Components](https://developers.webflow.com/designer/reference/components-overview)
- [GitHub: webflow/mcp-server](https://github.com/webflow/mcp-server)
