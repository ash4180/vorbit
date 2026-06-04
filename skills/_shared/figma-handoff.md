# Figma Design Handoff Primitives

Shared rules for turning a Figma design into engineering work. Applied by `/epic` (creating design-aware sub-issues), `/implement` (coding from a design), and `/verify` (checking the build against the design). Each skill uses these in its own context; the rules live here so they can't drift between skills.

## A Figma node ID is required

Any UI work must resolve to an exact Figma node ID before proceeding. The phrasing doesn't matter — "match Figma", "like the mockup", "same as X's design", a screenshot with no URL, a description with no link — all must resolve to a concrete node. If none is supplied, stop and ask.

## Structure / flow summary (before coding or ticketing)

Summarize, from the Figma node + PRD:
- Parent frame / page and nearest meaningful ancestor
- Selected node boundary and child blocks in render order
- What's inside vs outside implementation scope
- Interaction flow: entry action, visible result, exit state

If any part is unclear, ask before proceeding.

## Conflict rule

If ticket text, implementation notes, screenshots, and Figma disagree, stop and ask which source wins before coding. Don't silently average the sources.

## Screenshot capture-and-compare

- Capture the Figma reference screenshot (`get_screenshot`, or the image `get_design_context` returns) before building.
- After building, capture a browser/app screenshot of the implemented surface.
- Compare: layout (hierarchy, spacing, alignment), token bindings (colors, type, radii — not hardcoded), the states the PRD lists, and copy. Call out intentional differences; fix unintended ones unless explicitly out of scope.
