# Vorbit Pencil Workflow

Use for syncing design tokens, components, and conventions to Pencil.

1. Load Vorbit durable rules before doing anything else.
2. Verify Pencil MCP connection. If unavailable, stop and ask user to reconnect.
3. Phase 1 - Codebase scan: detect framework, styling, component library, icon library, and platform/screen sizes from `package.json` and config files. If no codebase exists, ask user for platform and select a design system from Pencil style guides.
4. Confirm stack detection with user.
5. Phase 2 - Token extraction (codebase only): read theme/config files, extract colors, spacing, typography, borders, and shadows. Map tokens to usage such as background, text, and border.
6. Phase 3 - Component inventory (codebase only): resolve import aliases, find components, read source files for props, variants, and defaults. Cap at 30 components.
7. Show combined Pencil sync preview and get user confirmation before writing to Pencil.
8. Phase 4 - Sync tokens to Pencil as variables. Diff against existing values: add new, update changed, skip unchanged.
9. Phase 5 - Build Pencil component library: Screen Shells first (one per screen size), then top 10-12 components ranked by import frequency. Read actual styles for exact values. Build 2-3 variants per component. Cap at 15 reusable components.
10. Phase 6 - Write `pencil.md` into the resolver's project-scoped shared-rule directory (`<storage-root>/rules/projects/<project-slug>/`) with stack, screen presets, code generation rules, Pencil mockup rules, component IDs, token usage map, and layout patterns.
11. Flags: `--refresh` skips detection and updates only; `--components-only` skips tokens.
