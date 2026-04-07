# Vorbit Webflow Workflow

Use for developing Webflow pages, templates, and components.

1. Load Vorbit durable rules before doing anything else.
2. Gather inputs: target Webflow site, output type (Page/Template/Component), optional Figma URL.
3. Get design context: if Figma provided, fetch via Figma MCP. If direct build, gather requirements (sections, layout pattern, styling, references).
4. Analyze and plan: map Figma elements to Webflow structure (if Figma), or plan from requirements. For templates: identify fixed elements vs page slots. For components: identify boundaries, structure, responsive behavior.
5. Block on ambiguity — never guess unclear requirements. Stop and ask.
6. Build in Webflow using MCP tools: `element_builder` for structure (max 3 levels), `style_tool` for CSS classes, `element_tool` for content, `component_tool` for reusable components.
7. Class naming: `section-[name]`, `[component]-wrapper`, `[component]-[element]`, `is-[state]`, `has-[feature]`.
8. Production safeguards: confirm before live changes, show diff first, remind about backups.
9. Report: what was created, structure, page slots (if template), classes, next steps.
