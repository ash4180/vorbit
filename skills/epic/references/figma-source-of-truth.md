# Figma Source of Truth (Epic skill reference)

Loaded by `/vorbit:implement:epic` Step 3.7 for UI / layout / component / composition / block build-up work. Skip entirely for backend-only work that has no design surface.

This file covers:
1. The 10-step source-of-truth analysis procedure
2. The design evidence matrix shape (rendered inside Linear tickets via `../output-schema.md → Design Source of Truth`)
3. Conflict, structure/flow, API/backend contract, and mockup-missing rules
4. When a Figma node ID is required regardless of how the PRD names the design

## When a Figma node ID is required

The PRD must name an exact Figma node ID for any UI work. The phrasing the user chose doesn't matter — "match Figma", "like the mockup", "same as X's design", a screenshot without a URL, a description with no link, etc., all need to resolve to a concrete node before sub-issues can be created. If the PRD doesn't supply one, stop and ask.

## The 10-step procedure

1. Fetch every referenced Figma node with `get_design_context`. Use `get_metadata` only for hierarchy inspection, then return to `get_design_context` for implementation context.
2. Capture a reference screenshot for every primary Figma node with `get_screenshot` or the screenshot returned by `get_design_context`.
3. Read Figma annotations and development notes; treat them as requirements only after checking them against the PRD.
4. Build the design evidence matrix (shape below).
5. Build a Figma structure/flow summary before planning tickets: what page or frame this belongs to, what the selected node contains, what's inside vs outside the implementation scope, how the user reaches this surface, and what changes after the interaction.
6. If structure or flow cannot be explained from Figma + PRD, ask the user before creating issues.
7. Compare the Figma node to the PRD text. If they conflict, ask which source wins before creating issues.
8. For each UI/component/composition sub-issue, include the exact instruction: `Implement Figma node <node-id> exactly for <target surface>.` Add any conflict rule, e.g. `<primary-node-id> is source of truth; <reference-node-id> is reference only.`
9. Add screenshot verification to each UI sub-issue: capture the Figma reference screenshot before coding, capture the browser or app screenshot after implementation, compare them, and call out intentional differences.
10. For API / backend / service sub-issues, include a Figma node only when it defines data visible in the UI. Otherwise include the design-derived contract without pixel or layout requirements.

## Design evidence matrix shape

The matrix tracks, per surface or flow step:

- Surface or flow step
- Primary Figma node ID and URL
- Reference screenshot captured / attached
- Parent frame / page and nearest meaningful ancestor
- Child block structure in render order
- Reference-only node IDs (if any)
- Implementation target file / component
- Required states / variants / responsive behavior
- Interaction flow: entry, user action, visible result, exit state
- Explicit exclusions and open questions

When this matrix appears inside a Linear ticket body, render it per `../output-schema.md → Design Source of Truth`.

## Rules

**Mockup missing rule.** If a UI sub-issue cannot name its source node, do not create it as implementation-ready. Ask for the mockup or mark `TBD-design` and keep the sub-issue blocked.

**Conflict rule.** If ticket text, implementation notes, screenshots, and Figma disagree, stop and ask which source wins before coding. Do not silently average the sources.

**Structure/flow rule.** Before coding, summarize the parent frame, selected node boundary, child blocks in render order, entry action, visible result, and exit state. If any part is unclear, ask before implementation.

**API/backend contract rule.** Backend sub-issues that derive a contract from a design must include only the fields, states, ordering, or copy the UI needs. Do not put pixel or layout requirements in backend tickets — those belong in the matching UI sub-issue.
