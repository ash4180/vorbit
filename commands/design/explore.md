---
description: Quick exploration of ideas before PRD creation
argument-hint: [topic or problem]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*, mcp__anytype__*
---

Explore: $ARGUMENTS

Use the **explore** skill for output format and validation rules.

## Step 0: Verify Documentation Connection (if saving later)

**At the START of exploration, ask user if they plan to save (Notion, Anytype, or skip).**

### If Notion:
1. Run a lightweight test: use `notion-find` to search for "test"
2. **IF the call fails (auth error, token expired, connection refused):**
   - Tell the user: "Notion connection has expired. Please run `/mcp` and reconnect the Notion server, then run this command again."
   - **STOP HERE** - do not proceed with the rest of the command
3. **IF the call succeeds:** proceed to Step 1

### If Anytype:
1. Run a lightweight test: use `API-list-spaces` to verify connection
2. **IF the call fails:**
   - Tell the user: "Anytype connection has expired. Please run `/mcp` and reconnect the Anytype server, then run this command again."
   - **STOP HERE** - do not proceed with the rest of the command
3. **IF the call succeeds:** proceed to Step 1

### If skip: proceed directly to Step 1

## Step 1: Ask 10+ Questions

**MANDATORY: Ask at least 10 questions before generating options.**

Generate 10 questions specific to the topic. Ask in batches of 3-4 using AskUserQuestion - wait for responses before asking the next batch:

```
"For [topic], let's explore these questions:
1. [Core functionality question]
2. [User needs question]
3. [Scale/volume question]
4. [Error handling question]
5. [Constraints question]
6. [Integration question]
7. [Security/compliance question]
8. [Timeline question]
9. [Trade-off question]
10. [Edge case question]
```

Then ask follow-ups:
- **Competitors**: "Who are existing solutions?"
- **User scenarios**: "Describe 3 real scenarios"
- **Constraints**: "Budget, timeline, or technical limitations?"
- **Confirm**: "Which are most important? What's missing?"

**DO NOT proceed until you have answers to 10+ questions.**

## Step 2: Analyze

After gathering context:
1. Summarize insights from all question answers
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros/cons/effort/risk
4. Make recommendation addressing constraints

## Step 3: Save Document

Ask: "Where should I save this exploration?"
- Options: Notion, Anytype, Skip

### If Notion:
1. Ask for database name or page URL
2. Use `notion-search` or `notion-fetch` to find target
3. Create document with Name = topic, full analysis in body
4. If database has `Type` property, set to `["Exploration"]`

### If Anytype:
1. Use `API-list-spaces` to show available spaces
2. Ask user which space to save to
3. Use `API-create-object` with:
   - `type_key`: "page" (or appropriate type)
   - `name`: topic
   - `body`: full exploration content as markdown

## Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Recommended approach summary
- Next: `/vorbit:design:prd`
