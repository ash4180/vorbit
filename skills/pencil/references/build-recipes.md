# Pencil Build Recipes

Reusable build recipes for Phase 5 (Build Component Library on Canvas). Read this when constructing Screen Shells and screen bones.

## Screen Shell Recipe

A Screen Shell is a reusable frame representing a real device screen with safe area regions built in. Every mockup starts by instancing a Screen Shell, then inserting content into the `content` slot.

**Structure:**
```
Screen Shell [device-name] (reusable, vertical, clip: true)
  ├── status-bar (frame, fixed height = top safe area)
  ├── content (frame, vertical, fill_container height, placeholder: true)
  └── home-indicator (frame, fixed height = bottom safe area)
```

**Safe area values** (from detection/platform reference "Safe Areas" section):
- Determine which safe areas apply based on detected platform
- For iOS: check if project targets Dynamic Island devices (iPhone 14 Pro+) → top: 59pt, or notch (iPhone X-14) → top: 47pt, or no notch (SE) → top: 20pt. Bottom: 34pt for Face ID devices, 0pt for SE.
- For Android: top: 24dp (status bar), bottom: 16dp (gesture nav) or 48dp (3-button nav). Default to gesture nav (16dp) for modern devices.
- For Web: no safe areas needed — just use the viewport dimensions.
- For iPad: top: 24pt (non-M4) or 59pt (M4 with Dynamic Island), bottom: 20pt (Face ID models).

**Build example** (iOS, iPhone standard 390×844, Dynamic Island):
```
I(parent, {type: "frame", reusable: true, name: "Screen Shell - iPhone", width: 390, height: 844, layout: "vertical", fill: "$background", clip: true})
  I(shell, {type: "frame", name: "status-bar", width: "fill_container", height: 59, fill: "$background"})
  I(shell, {type: "frame", name: "content", width: "fill_container", height: "fill_container", layout: "vertical", placeholder: true})
  I(shell, {type: "frame", name: "home-indicator", width: "fill_container", height: 34, fill: "$background"})
```

**Build example** (Android, flagship 412×915, gesture nav):
```
I(parent, {type: "frame", reusable: true, name: "Screen Shell - Android", width: 412, height: 915, layout: "vertical", fill: "$background", clip: true})
  I(shell, {type: "frame", name: "status-bar", width: "fill_container", height: 24, fill: "$background"})
  I(shell, {type: "frame", name: "content", width: "fill_container", height: "fill_container", layout: "vertical", placeholder: true})
  I(shell, {type: "frame", name: "nav-bar", width: "fill_container", height: 16, fill: "$background"})
```

**Build example** (Web, desktop 1440×900):
```
I(parent, {type: "frame", reusable: true, name: "Screen Shell - Desktop", width: 1440, height: 900, layout: "vertical", fill: "$background", clip: true})
  I(shell, {type: "frame", name: "content", width: "fill_container", height: "fill_container", layout: "vertical", placeholder: true})
```

**Usage in mockups — always build the Screen Bone first:**

Instance the shell, then build a "bone" skeleton inside the `content` slot BEFORE placing any components. The bone defines the page's structural zones (header, scroll area). Floating elements (tab bars, FABs) go in a SEPARATE nav-overlay that stacks on top of the bone. See "Screen Bone Pattern" in the detection/platform reference for the full recipe and patterns.

**For screens with floating nav (Pattern A — most common):**
```
screen=I(parent, {type: "ref", ref: "[shell-id]"})
U(screen+"/content", {layout: "none"})
bone=I(screen+"/content", {type: "frame", name: "bone", layout: "vertical", width: 393, height: 759, x: 0, y: 0})
header=I(bone, {type: "frame", name: "header", height: "fit_content", ...})
scroll=I(bone, {type: "frame", name: "scroll-area", height: "fill_container", scroll: true, ...})
nav=I(screen+"/content", {type: "frame", name: "nav-overlay", layout: "none", width: 393, height: 759, x: 0, y: 0})
```
Calculate dimensions: `width = shell_width`, `height = shell_height - status_bar - home_indicator`. `fill_container` does NOT work inside `layout: "none"` — always use explicit pixels for bone and nav-overlay.

Then fill each zone with components:
```
I(header, {type: "text", content: "Hey, Ash", ...})
I(scroll, {type: "ref", ref: "[card-id]"})
I(nav, {type: "ref", ref: "[tab-bar-id]", x: 75, y: 653})
```

Key: the content slot uses `layout: "none"` (stacking mode) so bone and nav-overlay both fill the same space. The bone handles vertical flow. The nav-overlay floats on top with absolute positioning. Never put the nav-overlay INSIDE the bone — it will compete for space with `fill_container` siblings.

**For screens without floating elements (Pattern B-simple, C, D):**
No stacking needed — leave the content slot as `layout: "vertical"` (or `"horizontal"` for sidebar layouts) and build the bone directly.

**CRITICAL — Review layout model and syntax before building:**
Before writing ANY `batch_design` call, review the checklist at the bottom of `references/layout-model.md`. Key rules:
- Text/icon nodes ignore `width`/`height` — wrap in a frame when you need sizing control (see "When to Wrap")
- `fill_container` only works inside flex parents — not inside `layout: "none"` (see "Flexbox" section)
- Padding: `padding: [t,r,b,l]` — NOT `paddingTop`/`paddingLeft` (silently dropped)
- Border: `stroke: {align: "inside", fill: "$--border", thickness: 1}` — NOT `stroke: "$--border", strokeWidth: 1`
- Icons: `type: "icon_font"` with `iconFontFamily: "lucide", iconFontName: "home"` — NOT `type: "icon"`
- Safe areas: All interactive content within shell's content slot, with platform-appropriate margins (16px+ on mobile)
- Always call `get_guidelines("design-system")` first — it has the authoritative Pencil schema with examples.

**Batch strategy** — keep each `batch_design` call under 25 operations:
- Batch 1: Library frame (vertical layout) + Screen Shells (2-3 shells, ~12 ops)
- Batch 2: Section label + simple component variants (e.g., Button/Primary, Button/Secondary, Button/Outline)
- Batch 3: Section label + badge/tag variants (e.g., SeverityBadge with different severity colors)
- Batch 4: Section label + compound components (the project's main cards/rows)
- Batch 5: Navigation components (tab bar, header, search bar)
- After each batch: continue to next (no screenshot needed mid-build)

**After all batches:** Take a screenshot of the full component library frame to verify it looks correct. Each section should be visually labeled and organized.
