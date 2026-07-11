# Mobile Platform — Scanning & Building Guide

Self-contained reference for React Native, Expo, Flutter, and native mobile projects.
Agent reads this file once after platform detection — no other platform files needed.

## Full App Structure Trace

Scan top-down, not file-by-file. Each layer informs what to look for in the next.

### Layer 1: Entry Point

Find the app's root to understand the architecture:

| Signal | File Pattern | What to Extract |
|--------|-------------|----------------|
| Expo | `app/_layout.tsx`, `App.tsx` | Root navigator type, providers, theme context |
| RN CLI | `App.tsx`, `index.js` | Root navigator, providers |
| Flutter | `lib/main.dart` | MaterialApp, theme, home route |

Read the entry file. Look for:
- Navigation container (`NavigationContainer`, `Stack.Navigator`, `MaterialApp.router`)
- Theme provider wrapping (`ThemeProvider`, `GestureHandlerRootView`)
- What navigator is the root (stack? drawer? tabs?)

### Layer 2: Navigation Structure

Trace from root navigator to discover all screens and tab configuration.

**React Navigation (RN/Expo):**

1. Find the navigator config:
   - Grep for `createBottomTabNavigator`, `createMaterialBottomTabNavigator`
   - Grep for `createNativeStackNavigator`, `createDrawerNavigator`
   - Check `app/_layout.tsx` for Expo Router file-based navigation

2. Read the navigator file and extract:
   - **Tab names**: `<Tab.Screen name="Home" .../>` — these are the tab identifiers
   - **Tab icons**: Look for ALL icon patterns (they vary widely):
     ```
     // Pattern A: tabBarIcon prop (standard)
     tabBarIcon: ({ color }) => <Home color={color} size={22} />

     // Pattern B: TAB_ICONS map (common in custom tab bars)
     const TAB_ICONS: Record<string, typeof Home> = {
       Home, Inbox, Member: CircleUser  // key may differ from component name
     };

     // Pattern C: Custom tabBar component
     tabBar: (props) => <FloatingTabBar {...props} />
     // → Must also read FloatingTabBar source to find icon rendering

     // Pattern D: Expo Router (file-based)
     // Icons defined in app/(tabs)/_layout.tsx
     ```
   - **Active/inactive styling**: `tabBarActiveTintColor`, `tabBarInactiveTintColor`, `tabBarStyle`, or custom renderer
   - **Screen-to-component mapping**: `<Tab.Screen component={HomeScreen} />` or `getComponent={() => HomeScreen}`

3. If custom `tabBar` component is used:
   - Read that component's source too
   - Find how it renders icons (may use the TAB_ICONS map, not standard tabBarIcon)
   - Find styling (background, height, border radius, shadow)

**Flutter:**
- Look for `BottomNavigationBar`, `NavigationBar` in scaffold
- Extract `destinations` or `items` for tab names and icons
- Read `onDestinationSelected` for screen routing

### Layer 3: Screens

For each screen discovered in Layer 2:

1. Read the screen file's render method / build method
2. Extract the layout structure:
   - What's the root layout? (`SafeAreaView` → `ScrollView` → content)
   - Is there a fixed header? What's in it?
   - Is there a floating action button or bottom sheet?
   - What components are used and in what order?
3. Note which components from the component library are imported

### Layer 4: Components

For each component imported by screens:

1. Read the component file (follow the Component Inventory Scan in detection-matrix.md)
2. Extract props, variants, styles
3. **Read `StyleSheet.create()`** — this IS the design spec for Pencil translation
4. Note theme token usage (`useThemeColors`, `spacing[4]`, `borderRadius.md`)

### Layer 5: Shared Patterns

After scanning layers 1-4, identify cross-cutting patterns:

- **Theme hook**: Which hook do components use? (`useThemeColors`, `useTheme`, `useColorScheme`)
- **Common layout**: Do most screens use header + scroll + bottom nav? Or full-scroll?
- **Spacing rhythm**: What's the most common gap/padding value?
- **Typography scale**: Which font sizes appear most?
- **Icon library**: Confirmed from imports (Lucide, Expo Vector Icons, Material, etc.)
- **Icon size**: Standard icon sizes used across the app (typically 20-24 for nav, 16-18 for inline)

## Token Extraction — Mobile

### RN StyleSheet + Theme Object

Primary source for React Native projects. Read in this order:

1. `src/theme/index.ts` — understand the structure (what's exported, what's re-exported)
2. `src/theme/colors.ts` — color tokens, light/dark variants
3. `src/theme/spacing.ts` — spacing scale + semantic aliases
4. `src/theme/typography.ts` — font families, sizes, weights, text styles
5. `src/theme/borderRadius.ts` — radius tokens
6. `src/theme/shadows.ts` — shadow definitions (may be platform-specific iOS/Android)

Also check: `theme.ts`, `tokens.ts`, `design-tokens.ts` (single-file themes)

**Dark mode detection:**
- Look for `useThemeColors(isDarkMode)` or `useColorScheme()`
- Check if `legacyColors` defaults to `dark.*` — indicates dark-first design
- Note which theme (light/dark) the app defaults to

### NativeWind / Tailwind for RN

- Read `tailwind.config.js` or `nativewind.config.ts`
- Extract `theme.extend` values
- Same token extraction as web Tailwind

### Flutter

- Read `lib/theme/` or `ThemeData` definition in `main.dart`
- Extract `ColorScheme`, `TextTheme`, spacing constants

## Screen Presets — Mobile

| Framework | Primary | Secondary | Compact |
|-----------|---------|-----------|---------|
| React Native | 390 × 844 (iPhone) | 412 × 915 (Android) | 360 × 780 (Android compact) |
| Expo | 390 × 844 (iPhone) | 412 × 915 (Android) | 375 × 667 (iPhone SE) |
| Flutter | 390 × 844 (iPhone) | 412 × 915 (Android) | 360 × 780 (Android compact) |
| Swift/SwiftUI | 393 × 852 (iPhone Pro) | 820 × 1180 (iPad Air) | 375 × 667 (iPhone SE) |
| Kotlin/Compose | 412 × 915 (Flagship) | 360 × 780 (Compact) | 414 × 921 (Large) |

### Refinement signals

| Signal | Add |
|--------|-----|
| `react-native-web` in deps | Desktop: 1440×900, Tablet: 768×1024 |
| `react-native-screens` + tablet layout code | iPad: 820×1180 |
| `@expo/next-adapter` in deps | Desktop: 1440×900 |

### Safe Areas

**iOS:**
- Dynamic Island (iPhone 14 Pro+): top 59pt
- Notch (iPhone X–14): top 47pt
- No notch (SE): top 20pt
- Home indicator: bottom 34pt
- No home button (SE): bottom 0pt

**Android:**
- Status bar: top 24dp (typical)
- Navigation bar (gesture): bottom 16dp
- Navigation bar (3-button): bottom 48dp

**iPad:**
- Status bar: top 24pt (no notch), top 59pt (M4 Dynamic Island)
- Home indicator: bottom 20pt (Face ID models)

## Pencil Build Rules — Mobile

### Screen Shell Recipe

```
Screen Shell [device] (reusable, vertical, clip: true)
  ├── status-bar (height: [top safe area], fill: $--background)
  ├── content (fill_container, vertical, placeholder: true)
  └── home-indicator (height: [bottom safe area], fill: $--background)
```

Build one shell per detected screen size. For dual-platform (iOS + Android), build BOTH.

### Tab Bar Recipe

Read the navigator config (Layer 2) before building. Extract:
- Tab count and names from `Tab.Screen` declarations
- Icon names from `tabBarIcon`, `TAB_ICONS` map, or custom tabBar source
- Active/inactive styling from `tabBarActiveTintColor` / custom renderer

```
Tab bar (reusable, horizontal, justifyContent: space_around)
  ├── tab-[name] (vertical, alignItems: center, gap: 2)
  │   ├── icon (icon_font, iconFontFamily: [detected], iconFontName: [from navigator])
  │   └── label (text, fontSize: 10)
  └── ... per tab

Active/inactive: READ FROM CODEBASE — don't assume primary fill.
Common patterns:
  - Color-only: active = foreground, inactive = mutedForeground
  - Fill highlight: active background = primary/secondary
  - Underline: active has bottom border
```

### Header Recipe

```
Header (reusable, horizontal, height: 44, padding: [0, 16])
  ├── back-button (icon_font, optional)
  ├── title (text, fill_container)
  └── actions (horizontal, gap: 8)
```

### Screen Bone — Mobile Default

Most mobile apps use **Pattern A** (Header + Scroll + Floating Nav):

```
content (layout: "none" — stacking)
  ├── bone (vertical, explicit W×H, x:0, y:0)
  │   ├── header (fit_content)
  │   └── scroll-area (fill_container, scroll: true)
  └── nav-overlay (layout: "none", same W×H, x:0, y:0)
      └── tab-bar (positioned near bottom)
```

Calculate: `W = shell_width`, `H = shell_height - status_bar - home_indicator`

`fill_container` resolves to 0 inside `layout: "none"` — always use explicit pixel dimensions for bone and nav-overlay.

## Anti-Patterns — Mobile

- **Reading component files in isolation** — always trace from navigator → screens → components (Layer 2 → 3 → 4). A component file alone doesn't tell you which icons the nav uses or which screen it appears on.
- **Assuming tab icons from component names** — the TAB_ICONS map key may differ from the Lucide component name (e.g., `Member: CircleUser`). Always read the actual icon mapping.
- **Assuming active tab uses primary color fill** — read `tabBarActiveTintColor` or custom tabBar renderer. Many apps use color-only change, not filled background.
- **Building shells for only one platform** — React Native targets both iOS and Android. Build shells for BOTH.
- **Skipping custom tabBar source** — if `tabBar: (props) => <FloatingTabBar {...props} />`, you MUST also read FloatingTabBar to find icon rendering and styling.
