---
description: Quick exploration of ideas before PRD creation
argument-hint: [topic or problem]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*, mcp__anytype__*
---

Explore: $ARGUMENTS

Use the **explore** skill for output format and validation rules.

## Step 0: Detect Platform & Verify Connection

**Auto-detect platform from user input:**
- Notion URL (contains `notion.so` or `notion.site`) → use Notion
- User mentions "Notion" → use Notion
- Anytype URL or object ID → use Anytype
- User mentions "Anytype" → use Anytype
- Otherwise → ask at save time (Step 3)

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

## Step 3: Draft in Chat

**Show the complete exploration document in chat for review:**

```markdown
# [Topic] - Exploration

## Problem Statement
[One sentence identifying root cause]

## Context
[Summary of insights from questions]

## Options

### Option 1: [Name]
- **Description**: ...
- **Pros**: ...
- **Cons**: ...
- **Effort**: Low/Medium/High
- **Risk**: Low/Medium/High

### Option 2: [Name]
...

## Recommendation
[Which option and why, addressing constraints]
```

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 4: Save Document

**Only proceed after user confirms the draft.**

**If platform was detected in Step 0:** use that platform directly (don't ask again).

**If no platform detected:** Use AskUserQuestion: "Where should I save this exploration?"
- Options: Notion, Anytype, Other

### If Notion:
1. Ask for database name or page URL
2. Use `notion-find` to locate target database
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
