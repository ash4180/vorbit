# Vorbit Pencil Workflow

Use for syncing design tokens, components, and conventions to Pencil.

> **MCP namespace**: This workflow uses `mcp__pencil__*` and optionally `mcp__mobbin__search_screens` for reference patterns. See `vorbit-shared/references/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

1. Load Vorbit durable rules before doing anything else.
2. Verify Pencil MCP connection. If unavailable, stop and ask user to reconnect.
3. Phase 1 — Codebase scan: detect framework, styling, component library, icon library, platform/screen sizes from `package.json` and config files. If no codebase, ask user for platform and select design system from Pencil's style guides.
4. Confirm stack detection with user (Confirmation 1 of 2).
5. Phase 2 — Token extraction (codebase only): read theme/config files, extract colors, spacing, typography, borders, shadows. Map tokens to usage (background vs text vs border).
6. Phase 3 — Component inventory (codebase only): resolve import aliases, find components, read source files for props/variants/defaults. Cap at 30 components.
7. Show combined sync preview (Confirmation 2 of 2, codebase only).
8. Phase 4 — Sync tokens to Pencil as variables. Diff against existing — add new, update changed, skip unchanged.
9. Phase 5 — Build component library on canvas: Screen Shells first (one per screen size), then top 10-12 components ranked by import frequency. Read actual StyleSheet for exact values. Build 2-3 variants per component. Cap at 15 reusable components.
10. Phase 6 — Write `.claude/rules/pencil.md` with stack, screen presets, code generation rules, Pencil mockup rules, component IDs, token usage map, layout patterns.
11. Flags: `--refresh` (skip detection, update only), `--components-only` (skip tokens).
