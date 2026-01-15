# Webflow Page Template Patterns

Strategies and patterns for creating effective static page templates with page slots.

## What Are Page Templates?

Page templates are reusable scaffolds that:
- Define fixed structure (header, footer, layout)
- Provide **page slots** where content varies
- Enable Designer → Marketer workflow
- Speed up page creation for repeated patterns

**Key distinction:** Templates aren't published directly - they're scaffolds for creating pages.

## Template Anatomy

### Fixed Elements

Elements that stay constant across all pages using the template:

| Element | Typical Content |
|---------|-----------------|
| Header/Navbar | Logo, navigation, CTA button |
| Footer | Links, social, copyright |
| Sidebar (if any) | Navigation, filters |
| Background pattern | Design elements |

### Page Slots

Placeholder areas where content varies:

| Slot Type | Purpose |
|-----------|---------|
| Hero slot | Main above-fold content |
| Content slot | Primary page content |
| Feature slot | Feature sections |
| CTA slot | Call-to-action sections |
| Sidebar content | Dynamic sidebar content |

## Template Patterns

### Pattern 1: Landing Page Template

**Structure:**
```
[Fixed: Header]
├── [Slot: Hero] - Hero component goes here
├── [Slot: Features] - Feature sections go here
├── [Slot: Social Proof] - Testimonials, logos
├── [Slot: CTA] - Call-to-action section
[Fixed: Footer]
```

**Best for:** Marketing pages, product pages, campaign pages

**Slot guidance:**
- Hero slot: Allow hero variations (image left, image right, centered)
- Features slot: Allow multiple feature components
- CTA slot: Single CTA component

### Pattern 2: Content Page Template

**Structure:**
```
[Fixed: Header]
├── [Fixed: Page Title Area]
├── [Slot: Main Content] - Article/content goes here
├── [Slot: Related] - Related content, sidebar
[Fixed: Footer]
```

**Best for:** About pages, policy pages, help articles

**Slot guidance:**
- Main content slot: Rich text or content components
- Related slot: Optional, can be empty

### Pattern 3: Feature Page Template

**Structure:**
```
[Fixed: Header]
├── [Slot: Hero] - Feature hero with headline
├── [Slot: Problem] - Problem statement section
├── [Slot: Solution] - Solution/feature detail
├── [Slot: How It Works] - Process/steps
├── [Slot: Pricing] - Optional pricing section
├── [Slot: CTA]
[Fixed: Footer]
```

**Best for:** Product features, use cases, solutions

### Pattern 4: Two-Column Template

**Structure:**
```
[Fixed: Header]
├── [Fixed: Two-Column Layout]
│   ├── [Slot: Main Content] - Primary content (left/wider)
│   └── [Slot: Sidebar] - Secondary content (right/narrow)
[Fixed: Footer]
```

**Best for:** Blog layouts, documentation, resource pages

## Slot Strategies

### Single vs Multiple Slots

| Approach | When to Use |
|----------|-------------|
| Single large slot | Maximum flexibility, less guardrails |
| Multiple named slots | Clear structure, guided assembly |
| Nested slots | Complex layouts with sub-sections |

### Slot Naming Convention

Name slots clearly so marketers know what goes where:

```
✅ Good slot names:
- hero-content
- feature-sections
- testimonials-area
- primary-cta

❌ Bad slot names:
- slot1
- content
- area
- section
```

### Slot Documentation

For each slot, document:
1. **Purpose** - What content belongs here
2. **Components** - Which components work in this slot
3. **Limits** - Min/max components (if any)
4. **Examples** - Sample configurations

## Component-Template Fit

### Designing Components for Slots

Components should:
- Be self-contained (no dependencies on slot context)
- Have consistent width behavior (full-width or constrained)
- Handle responsive behavior internally
- Work in any slot (when appropriate)

### Component Categories

| Category | Examples | Typical Slots |
|----------|----------|---------------|
| Heroes | Hero with image, Video hero | Hero slot only |
| Features | Feature grid, Feature list | Features, content slots |
| Social proof | Testimonials, Logo bar | Dedicated or content slots |
| CTAs | CTA banner, CTA card | CTA slot, any slot |
| Content | Rich text, FAQ accordion | Content slots |

## Responsive Considerations

### Template Responsiveness

Templates handle responsive layout:
- Fixed elements stack appropriately
- Slots maintain proper spacing
- Two-column becomes single-column on mobile

### Component Responsiveness

Components handle their own responsive behavior:
- Internal layout changes
- Font size adjustments
- Image sizing

### Breakpoint Strategy

| Breakpoint | Template Behavior |
|------------|-------------------|
| Desktop | Full layout as designed |
| Tablet | Reduced margins, possible sidebar collapse |
| Mobile | Single column, stacked slots |

## Creating Templates from Figma

### Step 1: Identify Template Structure

Look for in Figma design:
- What's consistent across page variations?
- What changes between pages?
- Where are the content boundaries?

### Step 2: Mark Slot Boundaries

In the Figma-to-Webflow process:
1. Fixed elements → Build directly
2. Variable sections → Create page slots
3. Repeating patterns → Build as components

### Step 3: Create Empty Slots

In Webflow:
1. Build fixed structure
2. Add Page Slot element where content varies
3. Name each slot clearly
4. Test with sample components

### Step 4: Document the Template

Create documentation showing:
- Template purpose and use cases
- Slot locations and purposes
- Compatible components per slot
- Example assembled pages

## Template Limits

### Webflow Constraints

| Limit | Value |
|-------|-------|
| Max templates per site | 40 |
| Slots per template | Unlimited (practical limit ~10) |
| Components per slot | Unlimited |

### Practical Recommendations

| Aspect | Recommendation |
|--------|----------------|
| Templates per project | 5-10 for small sites |
| Slots per template | 3-7 for usability |
| Component variants | Create enough for flexibility |

## Template Governance

### Who Creates What

| Role | Creates | Uses |
|------|---------|------|
| Designer | Templates, components | - |
| Developer | Complex components, CMS setup | Templates |
| Marketer | - | Templates, components → Pages |

### Change Management

When updating templates:
1. Changes affect all pages using template
2. Test changes on staging first
3. Communicate changes to team
4. Document template versions

## Anti-Patterns

### Template Anti-Patterns

| Anti-Pattern | Why Bad | Better Approach |
|--------------|---------|-----------------|
| One giant slot | No structure guidance | Multiple named slots |
| Too many slots | Overwhelming for marketers | Consolidate related areas |
| Fixed content in slots | Defeats purpose | Move to fixed elements |
| No slot documentation | Marketers don't know what fits | Document each slot |

### Component Anti-Patterns

| Anti-Pattern | Why Bad | Better Approach |
|--------------|---------|-----------------|
| Component depends on page context | Won't work in all slots | Self-contained components |
| Too many variants | Decision paralysis | Fewer, well-designed options |
| Inconsistent sizing | Looks broken in slots | Consistent full-width behavior |

## Example: E-commerce Landing Template

**Template: Product Landing**

```
[Fixed: Announcement Bar]
[Fixed: Header with Cart]
├── [Slot: Hero]
│   Compatible: product-hero, video-hero, image-hero
├── [Slot: Features]
│   Compatible: feature-grid, feature-list, benefit-cards
├── [Slot: Social Proof]
│   Compatible: testimonial-carousel, logo-bar, review-grid
├── [Slot: Product Details]
│   Compatible: spec-table, comparison-chart, faq-accordion
├── [Slot: CTA]
│   Compatible: cta-banner, pricing-card, signup-form
[Fixed: Footer with Newsletter]
```

**Usage:**
1. Marketer creates new page from template
2. Drags product-hero into Hero slot
3. Adds feature-grid and benefit-cards to Features slot
4. Adds testimonial-carousel to Social Proof slot
5. Publishes page

**Result:** Consistent brand, fast page creation, designer-approved structure.
