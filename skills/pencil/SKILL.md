---
name: pencil
description: Use when the user explicitly asks to configure Pencil for a project, sync codebase design tokens or components to Pencil, refresh a Pencil library, or start a Pencil design system from a style guide. It requires an active Pencil canvas, writes variables and reusable components, and updates project Pencil rules. Do not use for generic frontend coding, Figma work, or image-only mockups.
---

# Pencil Skill

Scan a codebase to detect its stack, extract design tokens, build a component inventory, create reusable Pencil components on canvas, and write project rules so AI-generated mockups and code match project conventions.

Read and follow `../_shared/execution-contract.md` before starting.

## Core Principles

- **Detect, don't guess**: Use file signals (package.json, config files, CSS) to determine the stack.
- **Confirm twice, not five times**: Stack detection + final sync preview. That's it.
- **Build for reuse**: Create reusable Pencil components that future mockups copy instead of rebuilding.
- **Idempotent**: Running again updates changed tokens and components without duplicating.
- **Non-destructive**: Never modifies source code. Writes to `.claude/rules/` and Pencil canvas only.

## Phase 0: Verify Pencil Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`).

1. Run `ToolSearch` for `"pencil"` to check if Pencil MCP is available
2. **IF no Pencil tools found:** "No Pencil connection found. Run `/mcp` to connect, then retry." → **STOP**
3. **IF found:** Call `mcp__pencil__get_editor_state` to verify connection
4. **IF fails:** "Pencil connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
5. **IF succeeds:** Note whether a `.pen` file is currently open (needed for Phases 4-5)

## Phase 1: Codebase Scan

**Goal**: Detect framework, styling, component library, icon library, and target platform with screen sizes.

Read the detection tables at `references/detection.md` relative to this skill.

**Actions**:
1. Create todo list with all phases (0-6)
2. Check flags:
   - **`--refresh`:** Read existing `.claude/rules/pencil.md`, skip to Phase 2 using cached stack config. No confirmations until final sync preview.
   - **`--components-only`:** Skip token extraction (Phase 2), go straight to Phase 3.
   - **First run:** Continue with full scan below.
3. Read `package.json` (if it exists) to detect dependencies
4. Apply detection rules for: Framework, Styling, Component library, Icon library `[Skill ref: detection.md]`
5. **Detect platform and screen sizes** — two paths:

   **Path A — Project detected** (package.json or framework signals found):
   - Read the platform-specific reference: `references/platforms/{detected}.md` `[Skill ref]`
     - Mobile detected → `platforms/mobile.md`
     - Web detected → `platforms/web.md`
     - Desktop detected → `platforms/desktop.md`
     - Ambiguous → `platforms/custom.md`
   - Use the platform file's "Screen Presets" and "Refinement Signals" sections
   - Include platform + screens in the confirmation prompt

   **Path B — No project or ambiguous platform** (no package.json, plain HTML, or framework like React that could be web or mobile):

   **Step 1 — Ask platform** `[User]`:
   - **Use AskUserQuestion** to ask the user:
     ```
     What platform are you designing for?
       1. Web (Desktop + Tablet + Mobile)
       2. iOS (iPhone + iPad)
       3. Android
       4. iOS + Android (cross-platform mobile)
       5. Desktop App (Electron, Tauri, native)
       6. Marketing / Social Media (banners, posts, stories)
       7. Custom size (specify exact dimensions)
       8. Multiple / All platforms

     Any specific devices or sizes? (e.g., iPhone 16 Pro, 1200×630 OG image, 728×90 banner)
     ```
   - Map the user's answer to screen presets using the platform reference file (`platforms/{chosen}.md`)
   - **Also derive the default Screen Bone pattern** from the platform file's "Screen Bone" section. For unambiguous platforms (iOS → Pattern A, Desktop App → Pattern C), use the default. For ambiguous ones (Web could be sidebar or top-nav), ask which layout fits.
   - **For custom sizes:** accept any width × height the user provides. No Screen Shell safe areas unless the user specifies a device.
   - **For marketing/social:** use the "Common Marketing / Custom Sizes" table from `detection.md`. No safe areas, no bone needed (single canvas).

   **Step 2 — Select design system from Pencil** `[Pencil]`:
   Since there's no codebase to extract tokens from, use Pencil's built-in style guides as the token source:
   1. Call `mcp__pencil__get_style_guide_tags` to get available style tags
   2. **Use AskUserQuestion** `[User]` — present the tags and ask:
      ```
      What visual style do you want? Pick a few keywords or describe:
        e.g., minimal + dark-mode, brutalist + bold, calm + soft, elegant + modern...

      Available directions: [show relevant subset of tags from get_style_guide_tags]
      Or say "show me options" and I'll preview a few.
      ```
   3. Call `mcp__pencil__get_style_guide(tags)` with the user's chosen tags + platform tag (e.g., `mobile`, `webapp`)
      - The response includes a **named design system** with complete tokens: colors, typography, spacing, radii, icons
   4. **Use AskUserQuestion** `[User]` — show the style guide preview:
      ```
      Style: [name] — [description summary]
        Colors:     [count] ([list key names])
        Typography: [families] at [count] sizes
        Spacing:    [scale summary]
        Icons:      [library]

      Use this design system? Or want to see another? (say different tags to try again)
      ```
   5. If user wants another → repeat step 3-4 with new tags
   6. If user wants a specific named style → call `mcp__pencil__get_style_guide(name="[name]")`
   7. On approval → store the style guide tokens for Phase 4

6. Present findings and **use AskUserQuestion** to confirm:

   **Path A (codebase detected) — show full stack:**
   ```
   Stack detected:
     Framework:     React Native
     Styling:       RN StyleSheet + Theme Object
     Components:    Custom (14 found)
     Icons:         Lucide
     Platform:      iOS + Android
     Screens:       iPhone (390×844), Android (412×915), Android compact (360×780)
     Page layout:   Pattern A — Header + Scroll + Bottom Nav

   Is this correct? Adjust anything?
   ```

   **Path B (no codebase) — show platform + selected design system:**
   ```
   Platform:      iOS + Android
   Screens:       iPhone 16 Pro (393×852), Pixel 8 (412×924)
   Page layout:   Pattern A — Header + Scroll + Bottom Nav
   Design system: [style guide name] ([key aesthetic summary])

   This will:
     1. Sync design system tokens as Pencil variables
     2. Create Screen Shells for both devices
     3. Build bone demo with the layout above

   Is this correct? Adjust screens, layout, or style?
   ```

   Path B omits Framework, Styling, Components, Icons — those only matter when a codebase exists. The design system comes from Pencil's style guide, not code.

The user can adjust screens, page layout pattern, or style.

**Output**: Confirmed stack configuration

## Phase 2: Token Extraction (Path A only)

**Goal**: Extract design tokens from project theme/config files.

**Path B (no codebase):** Skip this phase entirely. Tokens come from the Pencil style guide selected in Phase 1 Step 2.

**Actions** `[Codebase]`:
1. Use the platform file's "Token Extraction" section `[Skill ref]` to find token files
2. Based on styling approach, read the appropriate source:
   - **Tailwind v4:** Parse `@theme` block in main CSS
   - **Tailwind v3:** Parse `tailwind.config.*` theme object
   - **CSS Variables:** Parse `:root` custom properties
   - **RN StyleSheet + Theme Object:** Read `src/theme/index.ts` first, then each sub-module (colors, spacing, typography, borderRadius, shadows). Extract exported objects — these ARE the tokens.
   - **Theme objects (generic):** Parse exported theme JS/TS
   - **Shadcn:** Parse globals.css HSL variables
3. Extract and categorize:
   - **Colors**: Named color values (hex, HSL, RGB, oklch)
   - **Spacing**: Spacing scale values
   - **Typography**: Font families, sizes, weights, line heights
   - **Borders**: Border radii, widths
   - **Shadows**: Box shadow definitions
4. Build token-to-usage mapping by scanning component files:
   - Which colors are used for backgrounds vs text vs borders
   - Which spacing values are standard padding/gap
   - Which typography combinations form heading/body/caption styles

**Do NOT ask for confirmation here.** Tokens are shown in the combined preview (Phase 3).

**Output**: Categorized token list with usage context

## Phase 3: Component Inventory (Path A only)

**Goal**: Extract component information so Pencil builds with existing components.

**Path B (no codebase):** Skip this phase entirely. No components to inventory.

**CRITICAL: Read actual source files, not just filenames.**

Follow the "Component Inventory Scan" section in `detection.md` `[Skill ref]`:

1. **Resolve import aliases** from `tsconfig.json` / `jsconfig.json` / `components.json`
2. **Find component files** using priority-ordered glob patterns
3. **Filter non-components** (tests, stories, barrel-only files, pages, `_`-prefixed)
4. **Read each component file** and extract:
   - Component name, full props interface with types
   - Required vs optional props
   - Variant definitions and allowed values
   - Default values
5. **Apply library-specific extraction** (Shadcn/cva, Radix compound, MUI wrapper, Custom)
6. **Default to the ~30 most-used components**, prioritizing `ui/` and `common/`; inventory more only when the design system genuinely needs them.

**Combined sync preview (Path A):**

   **Path A (codebase detected):**
   ```
   Ready to sync to Pencil canvas:

   Platform: iOS + Android
     Screens: iPhone 16 Pro (393×852), iPhone SE (375×667), Pixel 8 (412×924)

   Tokens (23):
     Colors:     12 (primary, secondary, background, foreground, ...)
     Spacing:    8 (0, 1, 2, 3, 4, 6, 8, 12)
     Typography: 3 families, 7 sizes
     Borders:    4 radii
     Shadows:    3 levels

   Components (14):
     Button       6 variants, 4 sizes
     Card         5 sub-components
     Dialog       compound (7 parts)
     Input        3 required props
     ...

   This will:
     1. Sync tokens as Pencil variables
     2. Build reusable components on canvas (top 10)
     3. Write project rules with screen presets to .claude/rules/pencil.md

   Proceed?
   ```

   **Path B (no codebase) — skip this combined sync preview.** There are no code tokens or components to inventory; the style guide and platform/screen summary were already approved in Phase 1, so continue to Phase 4.

**Use AskUserQuestion** with this preview (Path A only). User can adjust what gets synced.

**Output**: Confirmed extraction ready for sync

## Phase 4: Sync Tokens to Pencil

**Goal**: Push tokens into the active `.pen` file as Pencil variables.

Token source depends on the path:
- **Path A (codebase):** tokens come from Phase 2 extraction (theme files, CSS, tailwind config)
- **Path B (no codebase):** tokens come from Phase 1 Step 2 style guide selection `[Pencil]`

**Actions**:
1. **IF no `.pen` file is open** (from Phase 0):
   - Ask: "No .pen file is open. Skip Pencil sync and just write project rules?"
   - **IF skip:** Jump to Phase 6
   - **IF user opens a file:** Call `mcp__pencil__get_editor_state` again `[Pencil]`
   - Never create a `.pen` file yourself — out of scope
2. Call `mcp__pencil__get_variables` `[Pencil]` to read existing canvas variables
3. Diff tokens against existing:
   - **New:** Add
   - **Changed:** Update
   - **Unchanged:** Skip
   - **Canvas-only:** Leave untouched
4. Call `mcp__pencil__set_variables` `[Pencil]` with the token payload

**Token format for `set_variables`:**
- Color tokens → color type variables
- Spacing tokens → number type variables
- Typography → string (font names) + number (sizes) variables

**Output**: Tokens synced to canvas

## Phase 5: Build Component Library on Canvas

**Goal**: Create reusable Pencil components that future mockups can copy/instance instead of rebuilding from scratch.

This is the key performance improvement. Without this phase, every mockup builds every Button, Card, Input from raw primitives. With reusable components, mockups use `I(parent, {type: "ref", ref: "btnId"})` — one operation instead of 8-12.

### Step 1: Load layout model and Pencil guidelines

**First**, read `references/layout-model.md` relative to this skill — the CSS→Pencil mental model. This teaches how block vs inline elements work, when to wrap text in frames, how flex layout maps to Pencil, and platform safe area rules. Understanding this prevents layout bugs at the source.

**Then** load the appropriate Pencil guidelines based on the path and detected platform:

**Path A (codebase — building reusable components):**
- Call `mcp__pencil__get_guidelines("design-system")` `[Pencil]` — how to structure reusable components (naming, slots, nesting)
- **Also call platform-specific guideline:**
  - Mobile detected → `mcp__pencil__get_guidelines("mobile-app")` `[Pencil]`
  - Web detected → `mcp__pencil__get_guidelines("web-app")` `[Pencil]`

**Path B (no codebase — building Screen Shells + bone demo only):**
- Skip `get_guidelines("design-system")` — no reusable components to build yet
- **Call platform-specific guideline only:**
  - Mobile chosen → `mcp__pencil__get_guidelines("mobile-app")` `[Pencil]`
  - Web chosen → `mcp__pencil__get_guidelines("web-app")` `[Pencil]`

### Step 2: Check for existing component library

Call `mcp__pencil__batch_get` with `patterns: [{ reusable: true }]` and `searchDepth: 2` to find any existing reusable components on canvas.

- **IF components already exist:** Map them to extracted inventory. Only build missing ones.
- **IF no components:** Build from scratch.

### Step 3: Find canvas space

Call `mcp__pencil__find_empty_space_on_canvas` to position the component library frame away from existing content.

### Step 4: Create component library frame

Build a "Component Library" container frame on canvas, then populate it with reusable components.

**Priority order:**

**Always build first — Screen Shells (one per detected screen size):**
1. Screen Shell — primary (e.g., 390×844 for iPhone, 1440×900 for Desktop, or user-specified custom size)
2. Screen Shell — secondary (e.g., 412×915 for Android, 768×1024 for Tablet)
3. Screen Shell — compact or additional (e.g., 360×780 for Android compact, 728×90 for banner)

Screen Shells are the foundation every mockup starts from. For device screens (mobile, tablet), they include safe area padding. For non-device targets (banners, social media, custom sizes, desktop apps), they are simple frames with no safe areas — just the correct dimensions. See "Screen Shell Recipe" below.

**Then build the PROJECT's actual components — not a generic UI kit.**

Do NOT use a fixed list of generic components (Button, Input, Card, etc.). Instead:

1. **Rank by import frequency** — Grep for `import.*from` across component files. The most-imported components are the ones mockups will need most.
2. **Start with the top 10-12** — Build these as reusable Pencil components first.
3. **Include navigation patterns** — If the project uses bottom tabs (`@react-navigation/bottom-tabs`) or a top navigation bar, build those as reusable components too. Every screen needs navigation. Read the actual tab navigator config (tabBarActiveTintColor, custom tabBar renderer) to determine the active-state highlight — many apps use a color-only change, not a filled background.

Around 15 reusable components total (including Screen Shells) keeps batch_design calls manageable; build more in additional batches when mockup fidelity genuinely requires them.

**For each component — read the source, don't guess:**

The component's `StyleSheet.create()` block (or equivalent styles) IS the design spec. Read it and map every property to Pencil equivalents using the "StyleSheet → Pencil Mapping" table in the detection/platform reference.

1. **Read the component file** — look at `StyleSheet.create()` for exact padding, gap, borderRadius, colors, typography
2. Create a `reusable: true` frame matching the codebase component name
3. Map stylesheet properties directly to Pencil frame properties (see detection/platform reference mapping table)
4. Use token variable references (`$--color-primary`) for colors that come from theme hooks — use the token name that matches the theme key (e.g., `colors.card` → `$--color-card`)
5. **Build 2-3 key variants side by side** — not just the default. For example:
   - Button: primary + secondary + outline + destructive
   - Badge: different severity colors
   - Input: default + focused (highlighted border) + error (red border)
   - Card: different content states
   - Tab/segment: active + inactive states
6. Name child nodes to match the code structure (e.g., "accent-bar", "meta-row", "text-column")
7. Keep nesting shallow (max 3 levels) for easy instance overrides

**Showcase layout** — organize the component library vertically with labeled sections:
```
Component Library (vertical layout, gap: 60)
  ├── "Screen Shells" label
  │   └── shells row (horizontal, gap: 40)
  ├── "Buttons" label
  │   └── variants row (horizontal, gap: 16)
  ├── "Badges" label
  │   └── variants row (horizontal, gap: 16)
  ├── "Cards" label
  │   └── card variants (horizontal, gap: 24)
  └── ... more sections
```

### Screen Shell Recipe

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

Instance the shell, then build a "bone" skeleton inside the `content` slot BEFORE placing any components. The bone defines the page's structural zones (header, scroll area). Floating elements (tab bars, FABs) go in a SEPARATE nav-overlay that stacks on top of the bone. See "Screen Bone Pattern" in the detection/platform reference for the full recipe and patterns. When building a demo screen, read the actual screen/page file's render method (e.g., `HomeScreen.tsx`) and follow its exact layout hierarchy — don't add header icons, titles, or sections that aren't in the source.

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
- Never `U()` descendants of `C()` nodes — copy assigns new child IDs
- Always use real node IDs from `batch_get`/`batch_design` responses — never fabricate IDs
- Safe areas: All interactive content within shell's content slot, with platform-appropriate margins (16px+ on mobile)
- Always call `get_guidelines("design-system")` first — it has the authoritative Pencil schema with examples.

**Batch strategy** — prefer batches of roughly 25 operations or fewer (a failed op in a huge batch is hard to isolate):
- Batch 1: Library frame (vertical layout) + Screen Shells (2-3 shells, ~12 ops)
- Batch 2: Section label + simple component variants (e.g., Button/Primary, Button/Secondary, Button/Outline)
- Batch 3: Section label + badge/tag variants (e.g., SeverityBadge with different severity colors)
- Batch 4: Section label + compound components (the project's main cards/rows)
- Batch 5: Navigation components (tab bar, header, search bar)
- After each batch: continue to next (no screenshot needed mid-build)

**After all batches:** Take a screenshot of the full component library frame to verify it looks correct. Each section should be visually labeled and organized.

### Step 5: Record component IDs

After building, call `mcp__pencil__batch_get` on the library frame to get the real node IDs of each reusable component. These IDs are needed for the rules file so future mockup instructions can reference them.

Save a mapping like:
```
Button: "abc123"
Card: "def456"
Input: "ghi789"
```

**Output**: Reusable component library on canvas with known IDs

## Phase 6: Write Project Rules

**Goal**: Write `.claude/rules/pencil.md` with both code generation AND Pencil mockup rules.

Read `references/project-rules-output.md` relative to this skill now. Fill its required template from the confirmed stack, extracted tokens, screen shells, and real Pencil component IDs; never leave bracket placeholders or example values in the written file. Write the result to `.claude/rules/pencil.md`, report the exact destination and sync counts, then mark all todos complete.

## Refresh Mode (`--refresh`)

1. Read existing `.claude/rules/pencil.md` for cached stack config
2. Skip stack detection and confirmation
3. Re-extract tokens and components
4. Diff tokens → sync only changes to Pencil
5. Diff component library → build only new/changed components
6. Update rules file
7. **No AskUserQuestion stops** — refresh is meant to be fast

## Components-Only Mode (`--components-only`)

1. Read existing `.claude/rules/pencil.md` for cached stack + tokens
2. Skip token extraction (Phase 2) entirely
3. Re-scan components (Phase 3)
4. Skip token sync (Phase 4)
5. Rebuild/update component library on canvas (Phase 5)
6. Update rules file
