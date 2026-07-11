# MCP Tool Routing

Read `execution-contract.md` in this directory first.

## Rule

Before interacting with an external platform, use the environment's capability discovery surface (`ToolSearch` in Claude Code) and inspect the current tool schema.

If platform tools exist, use them for platform data. Never bypass an authenticated connector with WebFetch or shell HTTP calls.

## Discover & Connect

1. Recognize the platform from user input (URL, name, ID) or task context
2. Run `ToolSearch` with the platform name (for example `"linear"` or `"figma"`)
3. Inspect returned operation and parameter schemas; do not rely on a verb remembered from another connector version
4. If a required capability is absent, end as `blocked_missing_capability`. If the platform is only an optional save destination, keep the completed local/chat artifact and report that saving was skipped

## Ask User for Platform

When the skill needs to read from or save to an external platform and the user hasn't specified one:

1. Run `ToolSearch` for the workflow's supported platforms to discover which are connected
2. Use `AskUserQuestion` with only the connected platforms as options
3. Use the selected platform for the rest of the session

## Verify Connection

Before a platform mutation, run a lightweight read operation:
- If it succeeds → proceed
- If it fails → stop before mutating and report `blocked_missing_capability`

## Save Content

When a skill needs to save content (PRD, explore doc, etc.):

1. Use the platform selected earlier (don't ask again)
2. Read/search first to detect an existing artifact or a partially completed prior attempt
3. Use the verified create/update operation
4. Record and return the URL or object ID so retries resume rather than duplicate content
