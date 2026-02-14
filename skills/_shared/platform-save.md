# Platform Save

Use this block when a skill needs to save content to the detected platform.

**Caller must provide:** `type` (e.g. "PRD", "Explore"), `name` (document title), `body` (markdown content).

## If platform was detected in Step 1:

Use that platform directly (don't ask again).

## If no platform detected:

Use AskUserQuestion: "Where should I save this?"
- Options: Notion, Anytype, Other

## Notion:
1. Ask for database name or page URL
2. Use `notion-find` to locate target database
3. Create with Name = document title, full content in body
4. If database has `Type` property, set to `["<type>"]`

## Anytype:
1. Use `API-list-spaces` to show available spaces
2. Ask user which space to save to
3. Use `API-create-object` with:
   - `type_key`: "page" (or appropriate type)
   - `name`: document title
   - `body`: full content as markdown
