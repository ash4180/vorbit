# MCP Tool Routing

## Rule

**Before interacting with ANY external platform, use `ToolSearch` to check if MCP tools exist for it.**

If MCP tools exist → use ONLY those tools. NEVER use Read, WebFetch, Write, or Bash curl for MCP-backed platforms. Their content is API-backed — generic tools cannot access it.

## Announce the Plugin Tool to the User

Announce once per session, on the first MCP call: say one short chat line naming the plugin and the specific tool. Re-announce only when the namespace prefix changes (e.g. `mcp__figma__` → `mcp__mobbin__`). Do not re-announce on subsequent tools within the same namespace.

Example:

> Using `mcp__figma__use_figma` to build the modal frame. Optional: `mcp__mobbin__search_screens` for competitor research first.

Skip entirely when no MCP tool will be called (pure git, pure filesystem, pure analysis).

## Discover & Connect

1. Recognize the platform from user input (URL, name, ID) or task context
2. Run `ToolSearch` with the platform name (e.g. `"notion"`, `"linear"`, `"figma"`)
3. If MCP tools returned → use them exclusively
4. If no MCP tools found → tell user: "No [platform] connection found. Run `/mcp` to connect, then retry." → **STOP**

## Ask User for Platform

When the skill needs to read from or save to an external platform and the user hasn't specified one:

1. Run `ToolSearch` with broad terms (`"notion"`, `"linear"`, `"figma"`) to discover which platforms are connected
2. Use `AskUserQuestion` with only the connected platforms as options
3. Use the selected platform for the rest of the session

## Verify Connection

Before doing real work, run a lightweight read operation on the selected platform:
- If it succeeds → proceed
- If it fails → "Connection expired. Run `/mcp` to reconnect, then retry." → **STOP**

## Save Content

When a skill needs to save content (PRD, explore doc, etc.):

1. Use the platform selected earlier (don't ask again)
2. Use that platform's MCP tools to create/update content
3. Return the URL or object ID to the user

## Plugin Tool Index — which vorbit skill calls which plugin

Canonical map of every MCP-using vorbit skill — source of truth for plugin/tool selection.

| Vorbit skill | Primary namespace | Key tools | Optional plugins |
|---|---|---|---|
| `vorbit:design:figma` | `mcp__figma__*` (canonical) — fallback `mcp__plugin_figma_figma__*` if only plugin variant connected | `use_figma`, `get_design_context`, `get_libraries`, `search_design_system`, `get_screenshot` | `mcp__mobbin__search_screens` (research) |
| `vorbit:design:pencil` | `mcp__pencil__*` | `batch_get`, `get_variables`, `set_variables`, `get_style_guide` | `mcp__mobbin__search_screens` (patterns) |
| `vorbit:design:journey` | `mcp__claude_ai_Excalidraw__*` | `read_me` (load once), `create_view` (inline preview), `export_to_excalidraw` (publish to shareable URL) | — |
| `vorbit:design:explore` | `mcp__mobbin__*` | `search_screens` | `mcp__claude-in-chrome__*` (live screenshot) |
| `vorbit:design:prd` | `mcp__plugin_linear_linear__*` | `save_issue`, `list_teams`, `list_projects` | — |
| `vorbit:implement:epic` | `mcp__plugin_linear_linear__*` | `save_issue`, `list_issues`, `list_issue_statuses` | — |
| `vorbit:implement:implement` | `mcp__plugin_linear_linear__*` | `get_issue`, `update_issue`, `list_comments` | `mcp__figma__*` (for UI sub-issues — `get_design_context`, `get_screenshot`) |
| `vorbit:implement:implement-loop` | `mcp__plugin_linear_linear__*` | `list_issues` (parentId), `update_issue` | — |
| `vorbit:implement:webflow` | `mcp__webflow__*` | `element_builder`, `style_tool`, `component_builder`, `data_cms_tool` | `mcp__figma__get_design_context` (ref) |
| `vorbit:implement:prototype` | — (no required MCP) | — | `mcp__figma__get_design_context`, `mcp__pencil__*` (refs) |
| `vorbit:implement:prepare-pr` | `mcp__plugin_linear_linear__*` (optional) | `get_issue`, `update_issue`, `save_comment` | — |
| `vorbit:implement:cleanup-mocks` | `mcp__plugin_linear_linear__*` (optional) | `update_issue` | — |
| `vorbit:implement:verify` | `mcp__plugin_linear_linear__*` (optional) | `get_issue` | `mcp__figma__*` (for UI sub-issue screenshot comparison) |

Note: specialized external plugin skills (`webflow-skills:*`, `pr-review-toolkit:*`, `security-review`, `frontend-design:frontend-design`) are user-invoked entry points with their own scope — vorbit does not delegate to them mid-task.

## Namespace disambiguation — Linear, Notion, Figma

Multiple MCP servers may be configured for the same platform. Vorbit skills always use the plugin namespace shipped with vorbit; other namespaces are for direct/outside-skill use.

### Linear

| Namespace | Source | Use for |
|-----------|--------|---------|
| `mcp__plugin_linear_linear__*` | Ships with vorbit plugin | **All vorbit skills use this** — canonical for /epic, /prd, /implement, /verify, /prepare-pr, /implement-loop, /cleanup-mocks |
| `mcp__linear-server__*` | Locally configured Linear MCP (per `settings.local.json`) | Direct Linear operations outside vorbit skill flows |
| `mcp__claude_ai_Linear__*` | Claude.ai OAuth integration | Last resort — only `list_teams` is pre-approved |

### Notion

| Namespace | Source | Use for |
|-----------|--------|---------|
| `mcp__plugin_Notion_notion__*` (capital N in `Notion`) | Ships with vorbit plugin | **All vorbit skills use this** — `notion-fetch`, `notion-search`, `notion-update-page`, `notion-create-pages` |
| `mcp__notion__*` | Locally configured Notion MCP | Sometimes available; for direct Notion operations |
| `mcp__claude_ai_Notion__*` | Claude.ai OAuth integration | Fallback only; can't access user's personal Notion workspace |

### Figma

| Namespace | Source | Use for |
|-----------|--------|---------|
| `mcp__figma__*` | Figma's official MCP | **Canonical for vorbit skills** — `use_figma`, `get_design_context`, `get_screenshot`, `get_libraries`, `search_design_system`, `get_variable_defs` |
| `mcp__plugin_figma_figma__*` | Figma plugin variant | Has tools not in bare server (`generate_diagram` — currently unused after /ux Step 5 removal). Use only for those tools. |
| `mcp__plugin_figma_figma-desktop__*` | Figma Desktop variant | Used by /webflow for desktop-app-specific tools |

**Rule for all vorbit skills:** prefer the namespace listed in the Plugin Tool Index above. If only a non-canonical variant is connected at runtime, fall back gracefully (most tools work across variants). Don't mix namespaces within one skill invocation.
