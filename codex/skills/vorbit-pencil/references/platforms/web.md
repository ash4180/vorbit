# Web Platform — Scanning & Building Guide

Self-contained reference for Next.js, Nuxt, SvelteKit, React, Vue, Svelte, Astro, and plain HTML/CSS projects.
Agent reads this file once after platform detection — no other platform files needed.

## Full App Structure Trace

Scan top-down, not file-by-file. Each layer informs what to look for in the next.

### Layer 1: Entry Point & Routing

| Framework | Entry Pattern | What to Extract |
|-----------|--------------|----------------|
| Next.js App Router | `app/layout.tsx` | Root layout, providers, nav component |
| Next.js Pages | `pages/_app.tsx` | Wrapper, providers |
| Nuxt | `app.vue`, `layouts/default.vue` | Root layout, NuxtPage slot |
| SvelteKit | `src/routes/+layout.svelte` | Root layout, slot |
| React (Vite/CRA) | `src/App.tsx`, `src/main.tsx` | Router config, providers |
| Vue | `src/App.vue`, `src/main.ts` | Router, root component |
| Astro | `src/layouts/Layout.astro` | Base layout, slots |
| Plain HTML | `index.html` | Structure, linked CSS/JS |

Read the entry file. Look for:
- Navigation component (header, sidebar, top nav)
- Layout structure (does every page share a sidebar? a top bar?)
- Theme provider or dark mode context
- Router configuration (file-based vs config-based)

### Layer 2: Navigation & Layout

1. Find the main navigation component:
   - Grep for `<Nav`, `<Header`, `<Sidebar`, `<TopNav`, `<Navigation`
   - Check layout files for persistent nav elements
   - Look for route/link definitions (`<Link>`, `<NuxtLink>`, `<a>`)

2. Extract from nav component:
   - **Nav items**: labels, hrefs/routes, icons
   - **Nav type**: top bar, sidebar, hamburger menu, or combined
   - **Active state styling**: how does the current route get highlighted?
   - **Responsive behavior**: does sidebar collapse to hamburger on mobile?

3. Determine the layout pattern:
   - Sidebar + main content → Pattern C
   - Top nav + content → Pattern D
   - Full-width scrolling → Pattern B-simple
   - Dashboard with sidebar → Pattern C

### Layer 3: Pages/Routes

For each key page discovered:
1. Read the page/route component
2. Extract layout structure (what sections, what components used)
3. Note page-specific overrides (different nav, no footer, etc.)

### Layer 4: Components

Follow the Component Inventory Scan from detection-matrix.md:
1. Resolve import aliases (`tsconfig.json`, `components.json`)
2. Glob for component files
3. Read each — extract props, variants, styles
4. For Shadcn: extract `cva()` variants
5. For Radix: note compound component patterns

### Layer 5: Shared Patterns

- **CSS approach**: Tailwind classes, CSS modules, styled-components, vanilla CSS
- **Responsive breakpoints**: check Tailwind config or media queries for breakpoint values
- **Color scheme**: light/dark mode toggle? CSS variables with `prefers-color-scheme`?
- **Grid system**: max-width containers, grid templates, flex layouts
- **Typography**: font imports (Google Fonts, local), base size, heading scale

## Token Extraction — Web

### Tailwind CSS v4
- **File:** `app.css`, `globals.css`, or main CSS entry
- **Pattern:** `@theme { --color-*: ...; --spacing-*: ...; --font-*: ...; }`
- **Confirm:** `@import "tailwindcss"` present

### Tailwind CSS v3
- **File:** `tailwind.config.{js,ts,mjs,cjs}`
- **Pattern:** `theme.extend.colors`, `theme.extend.spacing`, `theme.extend.fontFamily`

### CSS Custom Properties
- **File:** Glob `src/**/*.css` for `:root` declarations
- **Pattern:** `--color-*`, `--spacing-*`, `--font-*`, `--radius-*`, `--shadow-*`

### Shadcn/ui Tokens
- **File:** `src/app/globals.css` or `src/styles/globals.css`
- **Pattern:** `:root { --background: ...; --foreground: ...; --primary: ...; }` with HSL values
- **Also check:** `components.json` for `cssVariables: true`

### CSS Modules / Styled Components
- Extract recurring values from component styles
- Look for shared theme objects or design token files

## Screen Presets — Web

| Viewport Class | Width × Height | Use For |
|---------------|---------------|---------|
| Desktop large | 1920 × 1080 | Full HD monitors |
| Desktop standard | 1440 × 900 | Design standard, MacBook Pro 15" |
| Desktop compact | 1280 × 800 | MacBook Air 13", smaller laptops |
| Tablet landscape | 1024 × 768 | iPad landscape |
| Tablet portrait | 768 × 1024 | iPad portrait |
| Mobile | 390 × 844 | iPhone-class mobile browser |
| Mobile compact | 360 × 780 | Android-class mobile browser |

Default set for web frameworks:
- Primary: 1440 × 900 (Desktop)
- Secondary: 768 × 1024 (Tablet)
- Compact: 390 × 844 (Mobile)

### Refinement signals

| Signal | Add |
|--------|-----|
| Responsive breakpoints in CSS/Tailwind | Include all breakpoint widths |
| PWA manifest (`manifest.json`) | Ensure mobile preset included |
| `electron` in deps | Add Desktop App sizes |

No safe areas needed for web — just viewport dimensions.

## Pencil Build Rules — Web

### Screen Shell Recipe — Web

No safe areas. Shell is just a viewport frame:

```
Screen Shell [viewport] (reusable, vertical, clip: true)
  └── content (fill_container, vertical, placeholder: true)
```

### Screen Bone — Web

**Pattern C — Sidebar + Main (dashboards, admin panels, web apps):**
```
content (layout: "horizontal")
  ├── sidebar (vertical, fixed width 240-280, fill_container height)
  │   └── nav items, logo, user menu
  └── main (vertical, fill_container × fill_container)
      ├── top-bar (horizontal, fit_content height)
      └── content-area (vertical, fill_container, scroll: true)
```

**Pattern D — Top Nav + Scroll (marketing, content sites, blogs):**
```
content (layout: "vertical")
  └── bone (vertical, fill_container)
      ├── top-nav (horizontal, fit_content, padding: [0, 24])
      │   └── logo, nav links, CTA
      ├── content-area (vertical, fill_container, scroll: true)
      │   └── hero, sections, features
      └── footer (vertical, fit_content)
```

### Component Recipes — Web

Components follow the project's styling approach. Read source and map:

**Shadcn/Tailwind → Pencil:**
- `className="bg-primary text-primary-foreground"` → `fill: "$--primary"`, text `fill: "$--primary-foreground"`
- `className="rounded-lg p-4"` → `cornerRadius: "$--radius-lg"`, `padding: 16`
- `className="flex gap-4"` → `layout: "horizontal"`, `gap: 16`

**CSS Variables → Pencil:**
- `var(--background)` → `$--background`
- `var(--radius)` → `$--radius`

## Anti-Patterns — Web

- **Assuming all web projects are dashboards** — marketing sites use Pattern D (top nav), not Pattern C (sidebar). Read the actual layout.
- **Adding mobile safe areas to web projects** — web viewports have no safe areas. Don't add status bars or home indicators.
- **Ignoring responsive breakpoints** — if the project defines breakpoints at 768px and 1024px, those are meaningful screen sizes to include.
- **Hardcoding Tailwind default values** — read the project's `tailwind.config` for customized theme values. Don't assume default Tailwind spacing/colors.
