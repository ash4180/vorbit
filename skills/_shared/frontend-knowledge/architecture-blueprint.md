# FE Architecture Blueprint

Reference loaded by `/vorbit:implement:epic`, `/vorbit:implement:implement`, and other vorbit skills that need to plan or evaluate a frontend feature before writing tickets or code.

## When to use

Before creating UI/component/composition sub-issues, or before implementing one, build the blueprint that answers the six questions below. If any answer is unclear, ask the user — the blueprint exists so that "Create a new Component X" is the last resort, not the default.

## The six blueprint areas

| Area | Decision to make |
|------|------------------|
| **Reuse/create matrix** | For every visible block in the mockup, map to an existing component/composition/hook/API helper as `Reuse`, `Adapt`, or `Create`. Do not assign `Create` until search has proven `Reuse` and `Adapt` are wrong. |
| **Component hierarchy** | Parent container, child components in render order, local composition boundaries, and which component owns each interaction. |
| **Data/API contract** | What data each block needs, which existing endpoint/client/hook provides it, what new API shape is needed, and the loading / error / empty behavior for each. |
| **State ownership** | URL state, server state, local UI state, form state, optimistic updates, and reset behavior. Name the owner for each piece of state. |
| **Design-system mapping** | Existing UI primitives, design tokens, icons, responsive rules, accessibility requirements, and i18n keys the feature touches. |
| **Test seams** | Unit / component tests, integration tests, browser or screenshot verification, and the edge states each test exercises. |

## Why this matters

Without the blueprint:
- Sub-issues jump to "Create Component X" and reinvent primitives the codebase already has
- Ownership of state ends up split across files without anyone realizing
- Loading / error / empty behavior gets discovered during review, not during planning
- Test strategy stays implicit until reviewers ask for it

The blueprint forces every visible block to defend itself against `Reuse` and `Adapt` before it gets to `Create`, and it forces every piece of state to have a named owner.

## How to fail this gracefully

If you can't fill an area from PRD + Figma + codebase search, do NOT paper over with a placeholder. Stop and ask the user. A blueprint with a clear "unknown — needs user input" entry is more useful than one with confident wrong guesses.

## Rendering in a Linear ticket

When this blueprint appears inside a sub-issue or epic body, render it as a table with one row per area. The "Decision" column carries the concrete answer for that ticket, not the generic guidance from this file. See each skill's `output-schema.md → FE Architecture Blueprint` for the exact table template.
