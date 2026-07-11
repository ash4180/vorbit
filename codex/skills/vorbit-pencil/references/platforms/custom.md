# Custom / Fallback Platform — Scanning & Building Guide

For projects where no specific platform was detected, or the user is designing from scratch without a codebase. Also covers uncommon frameworks (Unity UI, Flutter Web, etc.) and mixed-platform setups.

Agent reads this file when:
- No `package.json` or framework signals found
- User selected "Custom size" or "Multiple / All platforms"
- Framework detected but not in the mobile/web/desktop categories
- Ambiguous platform (could be web or mobile)

## When No Codebase Exists (Path B)

There's nothing to scan. The design system comes from Pencil's style guides (selected in Phase 1 Step 2). Skip to the build rules below.

## When Codebase Exists But Platform Is Ambiguous

Use the generic scanning approach — same layers, but without framework-specific hints.

### Layer 1: Entry Point

Look for common entry patterns:
- `index.html`, `App.tsx`, `main.ts`, `main.dart`, `lib/main.dart`
- Read whatever root file exists and follow imports

### Layer 2: Navigation

Grep broadly for navigation patterns:
- `<nav`, `<Nav`, `navigation`, `router`, `routes`
- `sidebar`, `header`, `menu`, `tab`
- Follow whatever nav component you find

### Layer 3: Pages/Screens

Find the main content areas:
- `pages/`, `screens/`, `views/`, `routes/`
- Read 2-3 representative pages to understand the structure

### Layer 4: Components

Standard scan:
- `components/`, `ui/`, `common/`, `shared/`
- Read each — extract props, variants, styles

### Layer 5: Shared Patterns

Look for ANY styling approach:
- CSS files, SCSS, styled-components, inline styles
- Theme files, design token files, config files
- Icon imports (search for common icon libraries)

## Screen Presets — Custom

There are no automatic presets for custom platform. **Use AskUserQuestion** `[User]`:

```
What type of design are you creating?
  1. App window (provide width × height, e.g., 1200×800)
  2. Social media post (Instagram, Facebook, LinkedIn, Twitter)
  3. Banner / Ad unit (Leaderboard, Rectangle, Skyscraper)
  4. Email template
  5. Presentation slide (16:9 or 4:3)
  6. Custom size (provide exact dimensions)
  7. Multiple sizes (list all you need)
```

Based on selection:
- **Option 1 or 6:** Use exact dimensions the user provides, no safe areas
- **Option 2:** Use `AskUserQuestion` to pick specific social platform, then map from `detection.md` "Common Marketing / Custom Sizes" table
- **Option 3:** Use `AskUserQuestion` to pick ad format, then map from same table
- **Option 4:** Use 600 × 900
- **Option 5:** Use `AskUserQuestion` — "16:9 (1920×1080) or 4:3 (1024×768)?"
- **Option 7:** Collect all sizes, create a Screen Shell for each

Never guess dimensions — always confirm with the user.

## Pencil Build Rules — Custom

### Screen Shell Recipe

For custom sizes — simple frame, no safe areas:

```
Screen Shell [label] (reusable, vertical, clip: true)
  └── content (fill_container, vertical, placeholder: true)
```

For marketing assets — even simpler:

```
[Asset Name] (reusable, clip: true, exact W×H)
  └── content area
```

No bone needed for single-canvas designs (banners, social posts, cards).

### When to Use a Bone

Only add bone structure if the design has:
- Scrollable content regions
- Fixed navigation elements
- Multiple layout zones

For static assets (banners, posts, cards) — skip the bone entirely.

## Anti-Patterns — Custom

- **Guessing a platform** — if you can't detect it, ask the user
- **Forcing standard device sizes** — custom means custom, respect user-provided dimensions
- **Adding safe areas to non-device targets** — banners, social posts, and custom sizes have no system UI
- **Building navigation for single-canvas designs** — a 728×90 banner doesn't need a tab bar
