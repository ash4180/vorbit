---
description: Quick exploration of ideas before PRD creation
argument-hint: [topic or problem]
allowed-tools: Read, Grep, Glob, AskUserQuestion, mcp__plugin_Notion_notion__*
---

Explore: $ARGUMENTS

Use the **explore** skill for output format and validation rules.

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

## Step 3: Save to Notion

Ask: "Where should I save this? (database name, page URL, or 'skip')"

If saving:
1. Use `notion-search` or `notion-fetch` to find target
2. Create document with Name = topic, full analysis in body
3. If database has `Type` property, set to `["Exploration"]`

## Report

- Notion URL (if saved)
- Recommended approach summary
- Next: `/vorbit:design:prd`
