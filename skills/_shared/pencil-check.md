# Pencil Check — Shared Pre-flight

Reference loaded by `/vorbit:implement:prototype` and `/vorbit:implement:webflow` before they build UI. Detects whether Pencil is configured for the project and routes the user through `/vorbit:design:pencil` sync if not.

This file is shared because both /prototype and /webflow have identical pencil-detection logic — extracting it here keeps them in sync. Any skill that builds UI from a codebase + Pencil tokens should reference this.

## Procedure

1. **Check if Pencil MCP is available:** Run `ToolSearch` for `"pencil"`.
2. **If Pencil tools NOT found:** Continue without Pencil sync — the project may not use Pencil yet, which is fine. Don't block.
3. **If Pencil tools found:** Check if `.claude/rules/pencil.md` exists (Glob for it).
4. **IF Pencil available but no `pencil.md`:** Use `AskUserQuestion`:
   ```
   Pencil is connected but not configured for this project.
   Run `/vorbit:design:pencil` first to sync your design tokens and components?
   Options:
   - "Run pencil first (Recommended)"
   - "Skip — continue without sync"
   ```
5. **If user chooses to sync:** Stop the current skill and tell them to run `/vorbit:design:pencil`, then come back.
6. **If `pencil.md` exists:** Read it — use the detected stack, tokens, and component inventory to inform UI build decisions (which components to instance, which tokens to reference, which screen presets to target).

## Why this matters

`/vorbit:design:pencil` writes a `.claude/rules/pencil.md` file documenting the project's design tokens, component inventory, screen presets, and Pencil mockup rules. When /prototype or /webflow builds UI without consulting that file, they may re-invent primitives that already have Pencil component IDs, miss screen-shell conventions, or use raw hex colors instead of token variable references.

The check is non-blocking (skips if Pencil isn't available) but offers the user an explicit branch when Pencil is connected but not yet synced. The recommended path is "sync first" — but the user gets the choice.

## When NOT to consult this

- Backend/API-only work — no UI, no Pencil need
- Quick scratch prototypes where the user explicitly wants to skip design-system alignment
- Projects where Pencil isn't part of the workflow
