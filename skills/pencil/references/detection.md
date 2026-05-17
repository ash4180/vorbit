# Detection Tables

Heuristics for detecting project stack from codebase files. Check in order — first match wins per category.

After detection, read the appropriate platform reference file:
- Mobile detected → `platforms/mobile.md`
- Web detected → `platforms/web.md`
- Desktop detected → `platforms/desktop.md`
- Ambiguous/none → `platforms/custom.md`

## Framework Detection

Check in order — first match wins. Mobile frameworks must come before web counterparts.

| Signal | Framework | Platform | Check Method |
|--------|-----------|----------|-------------|
| `react-native` in deps | React Native | Mobile | Grep `package.json` for `"react-native"` |
| `expo` in deps | Expo (React Native) | Mobile | Grep `package.json` for `"expo"` |
| `next` in deps | Next.js | Web | Grep `package.json` for `"next"` |
| `nuxt` in deps | Nuxt | Web | Grep `package.json` for `"nuxt"` |
| `@sveltejs/kit` in deps | SvelteKit | Web | Grep `package.json` for `"@sveltejs/kit"` |
| `svelte` in deps | Svelte | Web | Grep `package.json` for `"svelte"` |
| `vue` in deps | Vue | Web | Grep `package.json` for `"vue"` |
| `react` + `react-dom` in deps | React | Web | Grep for both `"react"` and `"react-dom"` |
| `astro` in deps | Astro | Web | Grep `package.json` for `"astro"` |
| `electron` in deps | Electron | Desktop | Grep `package.json` for `"electron"` |
| `@tauri-apps/api` in deps | Tauri | Desktop | Grep `package.json` for `"@tauri-apps"` |
| No package.json or no framework dep | Plain HTML/CSS | Web | Glob for `*.html` files |

## Styling Detection

| Signal | Approach | Check Method |
|--------|----------|-------------|
| `nativewind` in deps | NativeWind (Tailwind for RN) | Grep `package.json` for `"nativewind"` |
| `tamagui` in deps | Tamagui | Grep `package.json` for `"tamagui"` |
| `@shopify/restyle` in deps | Restyle | Grep `package.json` for `"@shopify/restyle"` |
| `tailwind.config.*` exists | Tailwind CSS | Glob `tailwind.config.{js,ts,mjs,cjs}` |
| `@tailwindcss` in package.json | Tailwind CSS v4 | Grep `package.json` for `"@tailwindcss"` |
| `*.module.css` files exist | CSS Modules | Glob `src/**/*.module.css` |
| `styled-components` in deps | Styled Components | Grep `package.json` for `"styled-components"` |
| `@emotion` in deps | Emotion | Grep `package.json` for `"@emotion"` |
| `*.scss` files exist | SASS/SCSS | Glob `src/**/*.scss` |
| `src/theme/` exists + React Native | RN StyleSheet + Theme Object | Glob `src/theme/**/*.{ts,js}` |
| React Native + none of above | RN StyleSheet (no theme) | Default for React Native |
| None of the above | Vanilla CSS | Default |

## Component Library Detection

| Signal | Library | Check Method |
|--------|---------|-------------|
| `@shadcn` in deps or `components.json` | Shadcn/ui | Glob `components.json` or Grep deps |
| `@radix-ui` in deps | Radix UI | Grep `package.json` |
| `@mui/material` in deps | Material UI | Grep `package.json` |
| `@chakra-ui` in deps | Chakra UI | Grep `package.json` |
| `antd` in deps | Ant Design | Grep `package.json` |
| `@mantine` in deps | Mantine | Grep `package.json` |
| `react-native-paper` in deps | RN Paper | Grep `package.json` |
| `@rneui` in deps | RN Elements | Grep `package.json` |
| `@gluestack-ui` in deps | Gluestack UI | Grep `package.json` |
| None detected | Custom / None | Scan `src/components/` |

## Icon Library Detection

| Signal | Library | Check Method |
|--------|---------|-------------|
| `lucide-react-native` in deps | Lucide (RN) | Grep `package.json` |
| `lucide-react` in deps | Lucide | Grep `package.json` |
| `@expo/vector-icons` in deps | Expo Vector Icons | Grep `package.json` |
| `react-native-vector-icons` in deps | RN Vector Icons | Grep `package.json` |
| `@heroicons` in deps | Heroicons | Grep `package.json` |
| `@mui/icons-material` in deps | Material Icons | Grep `package.json` |
| `react-icons` in deps | React Icons | Grep `package.json` |
| `@phosphor-icons` in deps | Phosphor | Grep `package.json` |
| `@tabler/icons-react` in deps | Tabler Icons | Grep `package.json` |
| None detected | No icon library | Note in output |

## Common Marketing / Custom Sizes

| Type | Width × Height | Use For |
|------|---------------|---------|
| Instagram Post | 1080 × 1080 | Square social posts |
| Instagram Story | 1080 × 1920 | Vertical stories/reels |
| Facebook/LinkedIn | 1200 × 630 | Link preview / OG image |
| Twitter/X Header | 1500 × 500 | Profile banner |
| Leaderboard Banner | 728 × 90 | Standard web banner |
| Large Rectangle | 336 × 280 | Sidebar ad unit |
| Email | 600 × 900 | Email template |
| Presentation 16:9 | 1920 × 1080 | Slide deck |
| Presentation 4:3 | 1024 × 768 | Classic slide deck |
| Custom | User-specified | Any dimensions |

## Component Inventory Scan

### Step 1: Resolve import aliases

Read `tsconfig.json` / `jsconfig.json` for path aliases:
- `"paths": { "@/*": ["./src/*"] }` or `"baseUrl": "./src"`
- Shadcn: also read `components.json` for `"aliases"`

### Step 2: Find component files

Glob in priority order (stop when populated directory found):

| Priority | Glob Pattern |
|----------|-------------|
| 1 | `components/ui/**/*.{tsx,jsx}` |
| 2 | `src/components/ui/**/*.{tsx,jsx}` |
| 3 | `src/components/**/*.{tsx,jsx,vue,svelte}` |
| 4 | `components/**/*.{tsx,jsx,vue,svelte}` |
| 5 | `lib/components/**/*.{tsx,jsx}` |
| 6 | `app/components/**/*.{tsx,jsx}` |

### Step 3: Filter non-components

Exclude: `*.test.*`, `*.spec.*`, `*.stories.*`, `_`-prefixed, `pages/`, `app/` routes, barrel-only `index.ts`

### Step 4: Read each component

Extract: name, props interface, required vs optional, variants, defaults, import path.

### Step 5: Library-specific patterns

- **Shadcn/cva:** Extract `variants` object keys + values + `defaultVariants`
- **Radix:** Note compound components (Root + sub-components)
- **MUI/Chakra/Mantine:** Extract wrapper props + which library component it wraps
- **RN StyleSheet:** Extract `StyleSheet.create()` + theme hook usage + token references
- **Custom:** Extract props from interface/type

### Step 6: Build inventory

Cap at 30 components. Prioritize `ui/` and `common/` directories.

## Pencil Property Reference (Shared)

### StyleSheet → Pencil Mapping

| StyleSheet Property | Pencil Property |
|-------------------|----------------|
| `flexDirection: 'row'` | `layout: "horizontal"` |
| `flexDirection: 'column'` | `layout: "vertical"` |
| `gap: N` | `gap: N` |
| `padding: N` | `padding: N` |
| `paddingHorizontal` / `paddingVertical` | `padding: [vertical, horizontal]` |
| `borderRadius: N` | `cornerRadius: N` |
| `borderWidth: 1` | `stroke: {align: "inside", thickness: 1, fill: ...}` |
| `backgroundColor` | `fill: "..."` |
| `color` (text) | `fill: "..."` (text fill) |
| `fontSize` | `fontSize: N` |
| `fontWeight` | `fontWeight: "N"` (string) |
| `alignItems` | `alignItems: "..."` |
| `justifyContent` | `justifyContent: "..."` |
| `flex: 1` | `width: "fill_container"` or `height: "fill_container"` |
| `overflow: 'hidden'` | `clip: true` |
| Lucide icon | `{type: "icon_font", iconFontFamily: "lucide", iconFontName: "home"}` |
| Material icon | `{type: "icon_font", iconFontFamily: "Material Symbols Rounded", iconFontName: "home"}` |

### Properties That Silently Drop

| Wrong (silently dropped) | Correct |
|--------------------------|---------|
| `paddingTop`, `paddingBottom`, `paddingLeft`, `paddingRight` | `padding: N` or `padding: [v, h]` or `padding: [t, r, b, l]` |
| `stroke: "#color"`, `strokeWidth: 1` | `stroke: {align: "inside", fill: "...", thickness: 1}` |
| `icon: "lucide/home"` | `iconFontFamily: "lucide", iconFontName: "home"` |
| `type: "icon"` | `type: "icon_font"` |
