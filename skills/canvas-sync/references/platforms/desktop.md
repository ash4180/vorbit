# Desktop Platform — Scanning & Building Guide

Self-contained reference for Electron, Tauri, and native desktop app projects.
Agent reads this file once after platform detection — no other platform files needed.

## Full App Structure Trace

### Layer 1: Entry Point

| Framework | Entry Pattern | What to Extract |
|-----------|--------------|----------------|
| Electron | `main.js`, `electron/main.ts` | Window config (size, min size), IPC channels |
| Tauri | `src-tauri/tauri.conf.json` | Window dimensions, title, decorations |
| Electron + React | `src/App.tsx` | Root component, router |
| Tauri + React | `src/App.tsx` | Root component, router |

Look for:
- Window dimensions in config (`width`, `height`, `minWidth`, `minHeight`)
- Whether the app has multiple windows (main, settings, dialog)
- Title bar configuration (native vs custom)
- Menu bar configuration

### Layer 2: Navigation & Layout

Desktop apps typically use one of:
- **Sidebar navigation** — icon rail or labeled sidebar (most common)
- **Tab-based** — horizontal tabs for different sections
- **Menu bar only** — traditional desktop (no in-app nav)
- **Multi-window** — separate windows for different functions

Find the nav component and extract:
- Nav items, icons, labels
- Active state styling
- Collapse/expand behavior (icon-only vs full sidebar)

### Layer 3: Views/Panels

Read each main view/panel component:
- Layout structure (sidebar detail, split pane, etc.)
- Which components are used
- Fixed vs scrollable regions

### Layer 4: Components

Follow the Component Inventory Scan from detection-matrix.md.
Desktop components often include:
- Data tables, tree views, split panes
- Toolbars, status bars
- Modal dialogs, context menus
- Resizable panels

### Layer 5: Shared Patterns

- **Window chrome**: custom title bar? traffic lights position?
- **Panel layout**: resizable? fixed? collapsible sidebar?
- **Density**: desktop UIs are typically denser than mobile (smaller gaps, more content)
- **Keyboard shortcuts**: any visible shortcut hints in the UI?

## Token Extraction — Desktop

Same as web (the renderer is typically a web view):
- Tailwind → read `tailwind.config`
- CSS Variables → read `:root` declarations
- Theme objects → read exported theme files
- Shadcn → read `globals.css` HSL variables

## Screen Presets — Desktop

| Viewport Class | Width × Height | Use For |
|---------------|---------------|---------|
| Desktop large | 1920 × 1080 | Full HD, primary working size |
| Desktop standard | 1440 × 900 | MacBook Pro, common laptop |
| Desktop compact | 1280 × 720 | Minimum supported window |
| Sidebar/panel | 320 × 900 | Sidebar or panel layout testing |

Default set:
- Primary: 1440 × 900
- Secondary: 1920 × 1080
- Compact: 1280 × 720

No safe areas — desktop windows have no system UI overlaps.

## Pencil Build Rules — Desktop

### Screen Shell Recipe — Desktop

No safe areas. May include custom title bar:

**With custom title bar:**
```
Screen Shell [size] (reusable, vertical, clip: true)
  ├── title-bar (horizontal, height: 32-40, draggable area)
  │   ├── traffic-lights / window-controls
  │   ├── title (text)
  │   └── toolbar-actions
  └── content (fill_container, vertical, placeholder: true)
```

**With native title bar (simpler):**
```
Screen Shell [size] (reusable, vertical, clip: true)
  └── content (fill_container, vertical, placeholder: true)
```

### Screen Bone — Desktop Default

Most desktop apps use **Pattern C** (Sidebar + Main):

```
content (layout: "horizontal")
  ├── sidebar (vertical, width: 48-240, fill_container height)
  │   └── icon rail or labeled nav items
  └── main (vertical, fill_container × fill_container)
      ├── toolbar (horizontal, fit_content, optional)
      └── content-area (vertical, fill_container, scroll: true)
```

For multi-panel layouts (IDE-style):
```
content (layout: "horizontal")
  ├── sidebar (vertical, width: 48)
  ├── panel-left (vertical, width: 240)
  ├── main (vertical, fill_container)
  └── panel-right (vertical, width: 300, optional)
```

## Anti-Patterns — Desktop

- **Using mobile screen sizes** — desktop apps use window dimensions, not phone viewports
- **Adding mobile safe areas** — no status bar or home indicator on desktop
- **Ignoring multi-window** — if the config shows multiple windows, create shells for each
- **Using mobile-density spacing** — desktop UIs are typically denser (8-12px gaps vs 16-24px on mobile)
