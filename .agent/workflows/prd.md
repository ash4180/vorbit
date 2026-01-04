---
description: Create a Product Requirements Document. No fluff, just what needs building.
---

## Step 0: Detect Platform & Verify Connection

**Auto-detect platform from user input:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- User mentions "Notion" → use Notion
- Anytype URL or object ID → use Anytype
- User mentions "Anytype" → use Anytype
- Otherwise → ask at save time (Step 4)

**Only verify the detected platform (don't test both):**

### If Notion detected:
1. Run `notion-find` to search for "test"
2. **IF fails:** "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed to Step 1

### If Anytype detected:
1. Run `API-list-spaces` to verify connection
2. **IF fails:** "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**
3. **IF succeeds:** proceed to Step 1

### If no platform detected: proceed to Step 1 (ask later)

## Step 1: Gather Context

**IF Notion URL provided:**
1. Use `notion-find` with page title from URL
2. If content retrieval fails, ask user to paste relevant sections
3. Proceed to Step 3 (restructure mode)

**IF Anytype URL or object ID provided:**
1. Use `API-get-object` to retrieve content
2. If content retrieval fails, ask user to paste relevant sections
3. Proceed to Step 3 (restructure mode)

**IF existing context (explore doc, conversation):**
1. Use that context as input
2. Proceed to Step 2 for gaps

**IF starting fresh:**
1. Proceed to Step 2

## Step 2: Clarify Requirements

**RULE: If ANY requirement is unclear, ask questions.**

Ask about:
1. **Problem** - "What problem does this solve?"
2. **Users** - "Who has this problem?" (Internal team, End users, Admins, etc.)
3. **Priority** - "How urgent?" (Critical, High, Medium, Low)
4. **Scope** - For ambiguous requirements, ask with options
5. **Constraints** - Budget, timeline, compliance

Keep asking until ALL requirements are clear. Don't guess.

## Step 3: Generate PRD

Use the **prd-schema** rule template. Include:
* Name (3-8 words, no jargon)
* Problem (max 3 sentences, no tech)
* Users
* User Stories with acceptance criteria
* User Flow: `[To be added via /journey]`
* Constraints
* Out of Scope
* Success Criteria (with numbers)

## Step 4: Save Document

**If platform was detected in Step 0:** use that platform directly (don't ask again).

**If no platform detected:** Ask: "Where should I save this PRD? (Notion, Anytype, or skip)"

### If Notion:
1. Ask for database name or page URL
2. Search for target database
3. Create with Name = feature name, full PRD in body
4. If database has `Type` property, set to `["PRD"]`

### If Anytype:
1. Use `API-list-spaces` to show available spaces
2. Ask user which space to save to
3. Use `API-create-object` with:
   - `type_key`: "page" (or appropriate type)
   - `name`: feature name
   - `body`: full PRD content as markdown

## Report

* URL or object ID (if saved)
* Platform used (Notion/Anytype)
* Summary: X user stories, Y success criteria
* Next: `/journey` or `/epic`
