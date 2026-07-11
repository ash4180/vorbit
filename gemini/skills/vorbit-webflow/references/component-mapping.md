# Figma to Webflow Component Mapping

Detailed mapping rules for translating Figma design elements to Webflow components.

## Frame Mapping

### Figma Frames → Webflow Sections

| Figma Pattern | Webflow Element | Class Convention |
|---------------|-----------------|------------------|
| Top-level frame | Section | `section-[name]` |
| Frame named "Header" | Navbar or Section | `navbar` or `section-header` |
| Frame named "Footer" | Section | `section-footer` |
| Frame named "Hero" | Section | `section-hero` |
| Auto-layout frame | Div Block with Flexbox | `[parent]-wrapper` |
| Grid frame | Div Block with Grid | `[parent]-grid` |

### Naming Convention Extraction

Extract Webflow class names from Figma layer names:

```
Figma: "Hero Section"     → Webflow: section-hero
Figma: "Features/Card"    → Webflow: features-card
Figma: "CTA Button"       → Webflow: cta-button
Figma: "Nav/Link/Active"  → Webflow: nav-link is-active
```

**Rules:**
- Convert spaces to hyphens
- Convert "/" to separate class or BEM-style naming
- Lowercase everything
- Remove special characters

## Layout Mapping

### Auto-Layout → Flexbox

| Figma Auto-Layout | Webflow Flexbox |
|-------------------|-----------------|
| Direction: Horizontal | Flex Direction: Row |
| Direction: Vertical | Flex Direction: Column |
| Gap: X | Column Gap / Row Gap: X |
| Padding: X | Padding: X |
| Alignment: Center | Align Items: Center |
| Distribution: Space Between | Justify Content: Space Between |

### Constraints → Positioning

| Figma Constraint | Webflow Position |
|------------------|------------------|
| Left & Right | Width: Auto, Left/Right margins |
| Center | Margin: 0 auto |
| Scale | Width: percentage |
| Fixed width | Width: fixed px |

## Typography Mapping

### Text Styles → Webflow Typography

| Figma Property | Webflow Property |
|----------------|------------------|
| Font Family | Font Family |
| Font Size | Font Size |
| Font Weight | Font Weight |
| Line Height | Line Height |
| Letter Spacing | Letter Spacing |
| Text Align | Text Align |
| Text Transform | Text Transform |

### Heading Detection

Detect heading levels from Figma:

| Figma Indicator | Webflow Element |
|-----------------|-----------------|
| Layer name contains "H1" or "Heading 1" | H1 |
| Layer name contains "H2" or "Heading 2" | H2 |
| Font size > 36px, prominent position | H1 or H2 |
| Font size 24-36px | H3 |
| Font size 18-24px | H4 |
| Body text | Paragraph |

## Color Mapping

### Figma Colors → Webflow

| Figma Source | Webflow Target |
|--------------|----------------|
| Fill color | Background Color |
| Stroke color | Border Color |
| Text fill | Color (text) |
| Gradient fill | Background: Linear Gradient |

### Design Tokens

If Figma uses variables/tokens:
1. Note the token name (e.g., `colors/primary`)
2. Create Webflow class with same semantic name
3. Apply color value
4. Document for future design system sync

## Component Mapping

### Figma Components → Webflow Components

| Figma Component Type | Webflow Approach |
|----------------------|------------------|
| Simple component | Div Block with class |
| Component with variants | Base class + modifier classes |
| Instance with overrides | Base component + custom class |
| Nested components | Nested Div Blocks |

### Variant Handling

Figma variants map to Webflow class combinations:

```
Figma: Button / Primary / Large
Webflow: class="button is-primary is-large"

Figma: Card / Hover
Webflow: class="card" with hover state
```

## Interactive Elements

### Buttons

| Figma Pattern | Webflow Element |
|---------------|-----------------|
| Rectangle + Text "Button" | Button or Link Block |
| Component named "Button" | Button element |
| Interactive prototype link | Link Block with href |

### Links

| Figma Pattern | Webflow Element |
|---------------|-----------------|
| Text with underline | Text Link |
| Frame with click action | Link Block |
| Navigation item | Nav Link |

### Forms

| Figma Pattern | Webflow Element |
|---------------|-----------------|
| Rectangle + placeholder text | Text Input |
| Multi-line text area | Text Area |
| Dropdown indicator | Select |
| Checkbox/radio visual | Checkbox/Radio |
| "Submit" button | Submit Button |

## Image Handling

### Figma Images → Webflow

| Figma Element | Webflow Approach |
|---------------|------------------|
| Image fill | Image element with uploaded asset |
| Background image | Div with background image |
| Icon (vector) | Image or embed SVG |
| Placeholder frame | Image with placeholder |

**Asset Workflow:**
1. Export from Figma (or use Figma asset URL)
2. Upload to Webflow Assets
3. Apply to element
4. Set alt text

## Responsive Behavior

### Breakpoint Mapping

| Figma Frame Width | Webflow Breakpoint |
|-------------------|-------------------|
| 1920px | Desktop (default) |
| 1440px | Desktop |
| 1280px | Desktop or Tablet Landscape |
| 991px | Tablet |
| 767px | Mobile Landscape |
| 478px | Mobile Portrait |

### Responsive Patterns

| Figma Pattern | Webflow Response |
|---------------|------------------|
| Multiple frame sizes | Create styles per breakpoint |
| "Mobile" variant | Apply to Mobile Portrait |
| Stack on mobile | Change flex-direction at breakpoint |

## Ambiguous Mappings

### When to Block and Ask

These patterns require user clarification:

| Figma Pattern | Why Ambiguous | Ask |
|---------------|---------------|-----|
| Complex nested frames | Multiple valid structures | "How should I structure this: nested divs or flat with grid?" |
| Custom illustrations | Vector vs image | "Should I export as SVG or upload as image?" |
| Animation indicators | Multiple IX2 approaches | "What interaction should this trigger?" |
| Unclear component boundary | Where does component end? | "Is this one component or multiple?" |
| Overlapping elements | Absolute positioning or different approach | "How should these overlapping elements be positioned?" |

### Default Decisions (When Not Blocking)

For common patterns, use these defaults without asking:

| Pattern | Default Decision |
|---------|------------------|
| Button-like rectangle | Link Block (more flexible) |
| Simple icon | Image element |
| Text with no clear heading | Paragraph |
| Container with padding | Div Block |
| Simple shadow | Box shadow |

## Special Cases

### Sticky Elements

| Figma Indicator | Webflow Implementation |
|-----------------|------------------------|
| "Sticky" in layer name | Position: Sticky |
| Header that persists | Navbar with sticky |
| Sidebar that follows | Sticky with top offset |

### Background Patterns

| Figma Pattern | Webflow Approach |
|---------------|------------------|
| Full-bleed image | Background image, cover |
| Pattern/texture | Background image, repeat |
| Gradient overlay | Pseudo-element or overlay div |
| Video background | Background video element |

### CMS-Ready Elements

When building for CMS:

| Element Type | CMS Consideration |
|--------------|-------------------|
| Repeating cards | Collection List |
| Dynamic text | CMS text field binding |
| Dynamic image | CMS image field binding |
| Category labels | CMS reference or multi-reference |
