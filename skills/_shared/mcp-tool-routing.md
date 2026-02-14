# MCP Tool Routing

## Rule

**Before interacting with ANY external platform, use `ToolSearch` to check if MCP tools exist for it.**

If MCP tools exist → use ONLY those tools. NEVER use Read, WebFetch, Write, or Bash curl for MCP-backed platforms. Their content is API-backed — generic tools cannot access it.

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
