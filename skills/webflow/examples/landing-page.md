# Example: Landing Page Template Workflow

Complete example of creating a landing page template from Figma design.

## Scenario

**User request:** "Create a landing page template from this Figma design"
**Figma URL:** `https://figma.com/design/abc123/Landing-Page?node-id=1-2`

## Step 1: Fetch Figma Design

```
Tool: mcp__plugin_figma_figma__get_design_context
Input: nodeId=1:2, fileKey=abc123
```

**Figma structure returned:**
```
Landing Page (Frame 1440x3200)
├── Header (Frame)
│   ├── Logo (Component)
│   ├── Nav Links (Auto-layout)
│   └── CTA Button (Component)
├── Hero Section (Frame)
│   ├── Headline (Text)
│   ├── Subheadline (Text)
│   ├── Hero Image (Image)
│   └── CTA Buttons (Auto-layout)
├── Features Section (Frame)
│   ├── Section Title (Text)
│   └── Feature Cards (Auto-layout)
│       ├── Feature Card 1
│       ├── Feature Card 2
│       └── Feature Card 3
├── Testimonials Section (Frame)
│   ├── Section Title (Text)
│   └── Testimonial Cards (Auto-layout)
├── CTA Section (Frame)
│   ├── CTA Headline (Text)
│   └── CTA Button (Component)
└── Footer (Frame)
    ├── Footer Links (Auto-layout)
    └── Copyright (Text)
```

## Step 2: Analyze and Plan

**Fixed elements identified:**
- Header - consistent across all landing pages
- Footer - consistent across all landing pages

**Variable sections → Page slots:**
- Hero Section → `hero-slot`
- Features Section → `features-slot`
- Testimonials Section → `social-proof-slot`
- CTA Section → `cta-slot`

**Confirmation to user:**
> "I'll create a landing page template with:
> - Fixed: Header and Footer
> - Slots: Hero, Features, Social Proof, CTA
>
> Should I proceed?"

## Step 3: Create Template Structure

### 3.1 Create Template in Webflow

```
Tool: Webflow MCP - Create Page Template
Name: "Landing Page Template"
```

### 3.2 Build Header (Fixed)

```
Structure:
Section.section-header
├── Container.header-container
│   ├── Link Block.header-logo
│   │   └── Image (logo)
│   ├── Nav.header-nav
│   │   ├── Nav Link.nav-link "Features"
│   │   ├── Nav Link.nav-link "Pricing"
│   │   └── Nav Link.nav-link "About"
│   └── Link Block.header-cta.button.is-primary "Get Started"
```

**Classes created:**
- `section-header`
- `header-container`
- `header-logo`
- `header-nav`
- `nav-link`
- `header-cta`
- `button`
- `is-primary`

### 3.3 Add Page Slots

```
Structure after header:
Page Slot (name: "hero-slot")
Page Slot (name: "features-slot")
Page Slot (name: "social-proof-slot")
Page Slot (name: "cta-slot")
```

### 3.4 Build Footer (Fixed)

```
Structure:
Section.section-footer
├── Container.footer-container
│   ├── Div Block.footer-links
│   │   ├── Link.footer-link "Privacy"
│   │   ├── Link.footer-link "Terms"
│   │   └── Link.footer-link "Contact"
│   └── Paragraph.footer-copyright "© 2024 Company"
```

## Step 4: Create Components

### 4.1 Hero Component

```
Tool: Webflow MCP - Create Component
Name: "Hero - Image Right"

Structure:
Section.section-hero
├── Container.hero-container
│   ├── Div Block.hero-content
│   │   ├── Heading H1.hero-headline
│   │   ├── Paragraph.hero-subheadline
│   │   └── Div Block.hero-buttons
│   │       ├── Link Block.button.is-primary
│   │       └── Link Block.button.is-secondary
│   └── Div Block.hero-image-wrapper
│       └── Image.hero-image
```

### 4.2 Features Component

```
Tool: Webflow MCP - Create Component
Name: "Feature Grid - 3 Column"

Structure:
Section.section-features
├── Container.features-container
│   ├── Heading H2.section-title
│   └── Div Block.features-grid
│       ├── Div Block.feature-card
│       │   ├── Image.feature-icon
│       │   ├── Heading H3.feature-title
│       │   └── Paragraph.feature-description
│       ├── Div Block.feature-card
│       └── Div Block.feature-card
```

### 4.3 Testimonials Component

```
Tool: Webflow MCP - Create Component
Name: "Testimonial Carousel"

Structure:
Section.section-testimonials
├── Container.testimonials-container
│   ├── Heading H2.section-title
│   └── Slider.testimonial-slider
│       └── Slide.testimonial-slide
│           ├── Block Quote.testimonial-quote
│           ├── Paragraph.testimonial-author
│           └── Paragraph.testimonial-role
```

### 4.4 CTA Component

```
Tool: Webflow MCP - Create Component
Name: "CTA Banner"

Structure:
Section.section-cta
├── Container.cta-container
│   ├── Heading H2.cta-headline
│   └── Link Block.button.is-primary.is-large
```

## Step 5: Summary Report

```
Created: Template "Landing Page Template"
Location: Site > Pages > Templates

Structure:
├── [Fixed] Header with navigation
├── [Slot: hero-slot] For hero components
├── [Slot: features-slot] For feature sections
├── [Slot: social-proof-slot] For testimonials/logos
├── [Slot: cta-slot] For call-to-action
└── [Fixed] Footer with links

Components created:
├── Hero - Image Right
├── Feature Grid - 3 Column
├── Testimonial Carousel
└── CTA Banner

Classes created: 24 new classes following naming convention

Compatible components per slot:
- hero-slot: Hero - Image Right, (create more hero variants)
- features-slot: Feature Grid - 3 Column, (create list variant)
- social-proof-slot: Testimonial Carousel, (create logo bar)
- cta-slot: CTA Banner

Next steps:
1. Create additional component variants
2. Test by creating a page from template
3. Add components to slots and preview
```

## Usage After Creation

### Creating a Page from Template

1. Go to Pages panel
2. Click "Create new page"
3. Select "Landing Page Template"
4. Name the page

### Adding Components to Slots

1. Open page in Designer
2. Drag "Hero - Image Right" into hero-slot
3. Drag "Feature Grid - 3 Column" into features-slot
4. Drag "Testimonial Carousel" into social-proof-slot
5. Drag "CTA Banner" into cta-slot
6. Edit content as needed
7. Publish

### Result

Consistent, on-brand landing page created in minutes using designer-approved template and components.
