# Layout Model: Frontend → Pencil

How frontend layout works, and how it maps to Pencil. Read this before building any Pencil layout. Understanding the *why* prevents entire categories of bugs — instead of memorizing "don't do X", think like a frontend developer.

## The Box Model

Every visual element on the web (or in React Native) is a box. The box model has two fundamental categories:

### Block-Level Elements (HTML: `<div>`, RN: `<View>`, Pencil: `frame`)
- **Take up full available width** by default
- Accept explicit `width`, `height`, `padding`, `margin`
- Can contain children and control their layout (flex, grid)
- Can scroll (`overflow: scroll`)

### Inline Elements (HTML: `<span>`, RN: `<Text>`, Pencil: `text`, `icon_font`)
- **Sized by their content** — width/height are determined by the text or icon itself
- `width` and `height` properties are **ignored** (silently dropped in Pencil, no error)
- Cannot be flex parents
- Cannot scroll

This is the single most important distinction. When you need an inline element to take up space, **wrap it in a block-level element** — exactly like wrapping a `<span>` in a `<div>` in HTML, or a `<Text>` inside a `<View>` in React Native.

**Example — label that fills remaining width:**
```
// Wrong: width is silently dropped on text
I(row, {type: "text", content: "Label", width: "fill_container"})

// Correct: frame wrapper takes the width, text sits inside
wrap=I(row, {type: "frame", width: "fill_container"})
I(wrap, {type: "text", content: "Label"})
```

## Flexbox — The Layout Engine

Pencil uses flexbox, same as CSS and React Native. The mental model is identical.

### Axis and Direction

| Pencil | CSS | React Native | What it does |
|--------|-----|-------------|--------------|
| `layout: "vertical"` | `flex-direction: column` | `flexDirection: 'column'` | Children stack top→bottom |
| `layout: "horizontal"` | `flex-direction: row` | `flexDirection: 'row'` | Children flow left→right |
| `layout: "none"` | `position: absolute` on children | — | No flow — children positioned by x/y |

### Space Distribution

| Pencil | CSS | What it means |
|--------|-----|--------------|
| `width: "fill_container"` | `flex: 1` | Grow to fill remaining space in parent's main axis |
| `height: "fill_container"` | `flex: 1` (column) | Same, but for the cross/main axis depending on direction |
| `width: "fit_content"` | `width: fit-content` | Shrink to content size |
| `width: 200` | `width: 200px` | Fixed size |

**Critical rule:** `fill_container` only works when the parent is a flex container (`layout: "vertical"` or `layout: "horizontal"`). Inside `layout: "none"`, there is no flex axis — `fill_container` resolves to 0. Use explicit pixel values instead.

### Alignment

| Pencil | CSS | What it controls |
|--------|-----|-----------------|
| `justifyContent: "center"` | `justify-content: center` | Alignment along **main axis** |
| `alignItems: "center"` | `align-items: center` | Alignment along **cross axis** |
| `justifyContent: "space_between"` | `justify-content: space-between` | Even spacing, first/last at edges |

### Padding and Gap

| Pencil | CSS | Notes |
|--------|-----|-------|
| `padding: 16` | `padding: 16px` | All sides |
| `padding: [12, 16]` | `padding: 12px 16px` | [vertical, horizontal] |
| `padding: [8, 16, 12, 16]` | `padding: 8px 16px 12px 16px` | [top, right, bottom, left] |
| `gap: 8` | `gap: 8px` | Space between children |

`paddingTop`, `paddingLeft`, etc. are **silently dropped** in Pencil. Always use the array form.

## When to Wrap

These are the situations where frontend devs add a wrapper div. The same logic applies in Pencil.

| Situation | Frontend Pattern | Pencil Pattern |
|-----------|-----------------|----------------|
| Text needs to fill width | `<div style="flex:1"><span>Label</span></div>` | frame (fill_container) → text inside |
| Click target larger than content | `<button style="padding:12px">text</button>` | frame (padding) → text inside |
| Group items to align as unit | `<div style="display:flex">...</div>` | frame (layout: horizontal/vertical) → children |
| Overlap / stack layers | `<div style="position:relative">` + absolute children | frame (layout: none) → children with x/y |

**Don't over-wrap.** If a text node just needs to display at its natural size, don't wrap it. Only wrap when you need block-level control (width, padding, layout).

## Safe Areas — Platform Content Boundaries

Every device has regions where the OS draws system UI (status bar, home indicator, navigation bar, notch/Dynamic Island). Content must respect these boundaries.

### Why Safe Areas Exist

In modern devices, the screen extends edge-to-edge. The OS overlays system UI on top:
- **Top:** Status bar (time, battery, signal) and notch/Dynamic Island
- **Bottom:** Home indicator (iOS) or gesture/navigation bar (Android)
- **Sides:** Display cutouts on some devices

Apps draw their backgrounds edge-to-edge (behind system UI), but **interactive and readable content** must be inset to the safe area.

### The Safe Area Model

```
┌─────────────────────────┐ ← Physical screen edge
│      Status Bar          │ ← System UI overlay (not safe)
│─────────────────────────│ ← Safe area top
│                          │
│     SAFE AREA            │ ← All tappable/readable content here
│     (your content)       │
│                          │
│─────────────────────────│ ← Safe area bottom
│    Home Indicator        │ ← System UI overlay (not safe)
└─────────────────────────┘ ← Physical screen edge
```

### Platform-Specific Values

**iOS (Apple Human Interface Guidelines):**
- Dynamic Island devices (iPhone 14 Pro+): top inset **59pt**
- Notch devices (iPhone X–14): top inset **47pt**
- No notch (iPhone SE): top inset **20pt**
- Home indicator (Face ID devices): bottom inset **34pt**
- Home button (SE): bottom inset **0pt**
- Standard content margins: **16pt** horizontal padding
- Recommended readable width: **672pt** max on iPad

**Android (Material Design 3):**
- Status bar: top inset **24dp** (typical, varies by device)
- Gesture navigation: bottom inset **16dp**
- 3-button navigation: bottom inset **48dp**
- Standard content margins: **16dp** horizontal (compact), **24dp** (medium+)
- Edge-to-edge is enforced on Android 15+ (SDK 35)

**Web:**
- No device safe areas (unless PWA on mobile)
- Viewport is the safe area
- Content max-width: **1200px** typical (Vercel Geist: 1200px, common pattern)
- Body margins: **16px** mobile, **24–32px** tablet, **auto** (centered) desktop

**iPad:**
- Status bar: **24pt** (non-M4), **59pt** (M4 with Dynamic Island)
- Home indicator: **20pt** (Face ID models)
- Sidebar: **320pt** standard width in split view

### Safe Areas in Pencil Screen Shells

Every Screen Shell MUST include safe area zones as structural frames:

```
Screen Shell (reusable, vertical, clip: true)
  ├── status-bar    → height: [top inset], fill: $--background
  ├── content       → fill_container, placeholder: true  ← ALL content goes here
  └── home-indicator → height: [bottom inset], fill: $--background
```

The content slot is the safe area. Never place interactive content outside it. Backgrounds and decorative elements CAN extend behind system bars (that's what the shell's fill does).

### Content Margins Within Safe Areas

After safe area insets, content needs horizontal margins. This is what the platform guidelines call "layout margins" or "content padding":

| Platform | Compact/Mobile | Medium/Tablet | Expanded/Desktop |
|----------|---------------|---------------|-----------------|
| iOS (HIG) | 16pt | 20pt | Centered, max readable width |
| Android (M3) | 16dp | 24dp | 24dp with max content width |
| Web | 16px | 24px | Auto margins, 1200px max |

In Pencil, apply these as horizontal padding on the content frames inside the bone:
```
header=I(bone, {type: "frame", padding: [0, 16], ...})
scroll=I(bone, {type: "frame", padding: [0, 16], ...})
```

Or on individual cards/rows if the design calls for edge-to-edge backgrounds with inset text.

## Stacking Layers (Position Absolute)

When elements need to overlap (floating nav bar over scrolling content, modal over page), use `layout: "none"` on the parent — equivalent to `position: relative` in CSS with `position: absolute` children.

**Key rule:** In `layout: "none"`, children are positioned by `x`/`y` coordinates. Flex properties (`fill_container`, `justifyContent`, `gap`) have no effect. Every child needs explicit `width` and `height`.

**The Bone + Nav-Overlay Pattern:**
```
content (layout: "none")         ← stacking context
  ├── bone (vertical, w×h, x:0 y:0)    ← flex layout for page content
  │   ├── header (fit_content)
  │   └── scroll (fill_container)       ← fill works here — bone IS flex
  └── nav-overlay (none, w×h, x:0 y:0) ← floating layer
      └── tab-bar (x:76, y:683)         ← positioned absolutely
```

This is exactly how React Native does it: `<View style={{flex:1}}>` for the main content, then a sibling `<View style={{position:'absolute', bottom:0}}>` for the floating tab bar. Same pattern, same reasoning.

## Common Layout Recipes

### Row with label + value pushed apart
Frontend: `<div style="display:flex"><span style="flex:1">Label</span><span>Value</span></div>`

Pencil:
```
row=I(parent, {type: "frame", layout: "horizontal", alignItems: "center"})
wrap=I(row, {type: "frame", width: "fill_container"})
I(wrap, {type: "text", content: "Label"})
I(row, {type: "text", content: "Value"})
```

### Scrollable list with fixed header
Frontend: fixed header + `overflow-y: scroll` below

Pencil:
```
container=I(parent, {type: "frame", layout: "vertical", height: [explicit]})
header=I(container, {type: "frame", height: "fit_content", padding: [0, 16]})
scroll=I(container, {type: "frame", height: "fill_container", scroll: true, layout: "vertical"})
```

### Card with accent bar
Frontend: `<div style="display:flex"><div style="width:4px; background:red"></div><div style="flex:1; padding:16px">content</div></div>`

Pencil:
```
card=I(parent, {type: "frame", layout: "horizontal", borderRadius: 14, clip: true})
bar=I(card, {type: "frame", width: 4, height: "fill_container", fill: "$--severity-p1"})
body=I(card, {type: "frame", layout: "vertical", width: "fill_container", padding: 16, gap: 8})
```

## Checklist Before Every batch_design Call

1. **Am I setting width/height on a text or icon_font?** → Wrap in a frame
2. **Am I using fill_container inside layout: "none"?** → Use explicit pixels
3. **Am I using paddingTop/paddingLeft?** → Use `padding: [t,r,b,l]` array
4. **Am I using strokeWidth or stroke: "#hex"?** → Use `stroke: {align, fill, thickness}`
5. **Does my content respect safe areas?** → All interactive content inside the shell's content slot
6. **Does my content have platform-appropriate margins?** → 16px/dp minimum on mobile
