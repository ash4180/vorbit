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

1. Run `ToolSearch` with broad terms (`"notion"`, `"linear"`, `"anytype"`, `"figma"`) to discover which platforms are connected
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
| `vorbit:design:figma` | `mcp__figma__*` | `use_figma`, `get_design_context`, `get_libraries`, `search_design_system`, `get_screenshot` | `mcp__mobbin__search_screens` (research) |
| `vorbit:design:pencil` | `mcp__pencil__*` | `batch_get`, `get_variables`, `set_variables`, `get_style_guide` | `mcp__mobbin__search_screens` (patterns) |
| `vorbit:design:journey` | `mcp__claude_ai_Excalidraw__*` | `read_me` (load once), `create_view` (inline preview), `export_to_excalidraw` (publish to shareable URL) | — |
| `vorbit:design:explore` | `mcp__mobbin__*` | `search_screens` | `mcp__claude-in-chrome__*` (live screenshot) |
| `vorbit:design:prd` | `mcp__plugin_linear_linear__*` | `save_issue`, `list_teams`, `list_projects` | — |
| `vorbit:implement:epic` | `mcp__plugin_linear_linear__*` | `save_issue`, `list_issues`, `list_issue_statuses` | — |
| `vorbit:implement:implement` | `mcp__plugin_linear_linear__*` | `get_issue`, `update_issue`, `list_comments` | — |
| `vorbit:implement:implement-loop` | `mcp__plugin_linear_linear__*` | `list_issues` (parentId), `update_issue` | — |
| `vorbit:implement:webflow` | `mcp__webflow__*` | `element_builder`, `style_tool`, `component_builder`, `data_cms_tool` | `mcp__figma__get_design_context` (ref) |
| `vorbit:implement:prototype` | — (no required MCP) | — | `mcp__figma__get_design_context`, `mcp__pencil__*` (refs) |
| `vorbit:implement:prepare-pr` | `mcp__plugin_linear_linear__*` (optional) | `get_issue`, `update_issue`, `save_comment` | — |
| `vorbit:implement:cleanup-mocks` | `mcp__plugin_linear_linear__*` (optional) | `update_issue` | — |
| `vorbit:implement:verify` | `mcp__plugin_linear_linear__*` (optional) | `get_issue` | — |

Note: specialized external plugin skills (`webflow-skills:*`, `pr-review-toolkit:*`, `security-review`, `frontend-design:frontend-design`) are user-invoked entry points with their own scope — vorbit does not delegate to them mid-task.
