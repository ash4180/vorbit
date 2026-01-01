---
description: Create a Product Requirements Document. No fluff, just what needs building.
argument-hint: [feature description or Notion URL]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*
---

Create a PRD for: $ARGUMENTS

Use the **prd** skill for output format and validation rules.

## Step 0: Verify Notion Connection (if Notion needed)

**IF user provides a Notion URL OR will want to save to Notion:**
1. Run a lightweight test: use `notion-find` to search for "test"
2. **IF the call fails (auth error, token expired, connection refused):**
   - Tell the user: "Notion connection has expired. Please run `/mcp` and reconnect the Notion server, then run this command again."
   - **STOP HERE** - do not proceed with the rest of the command
3. **IF the call succeeds:** proceed to Step 1

## Step 1: Gather Context

**IF Notion URL provided:**
1. Use `notion-find` with page title from URL
2. If content retrieval fails, ask user to paste relevant sections
3. Proceed to Step 3 (restructure mode)

**IF existing context (explore doc, conversation):**
1. Use that context as input
2. Proceed to Step 2 for gaps

**IF starting fresh:**
1. Proceed to Step 2

## Step 2: Clarify Requirements

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Ask about:
1. **Problem** - "What problem does this solve?"
2. **Users** - "Who has this problem?" (options: Internal team, End users, Admins, etc.)
3. **Priority** - "How urgent?" (Critical, High, Medium, Low)
4. **Scope** - For ambiguous requirements, ask with options
5. **Constraints** - Budget, timeline, compliance

Keep asking until ALL requirements are clear. Don't guess.

## Step 3: Generate PRD

Use the **prd** skill template. Include:
- Name (3-8 words, no jargon)
- Problem (max 3 sentences, no tech)
- Users
- User Stories with acceptance criteria
- User Flow: `[To be added via /vorbit:design:journey]`
- Constraints
- Out of Scope
- Success Criteria (with numbers)

## Step 4: Save to Notion

Ask: "Where should I save this PRD? (database name, page URL, or 'skip')"

If saving:
1. Use `notion-search` or `notion-fetch` to find target
2. Create with Name = feature name, full PRD in body
3. If database has `Type` property, set to `["PRD"]`

**Hook auto-validates before save. Fix issues if prompted.**

## Report

- Notion URL (if saved)
- Summary: X user stories, Y success criteria
- Next: `/vorbit:design:journey` or `/vorbit:implement:epic`
