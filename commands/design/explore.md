---
description: Quick exploration of ideas before PRD creation
argument-hint: [topic or problem]
allowed-tools: Read, Grep, Glob, AskUserQuestion, Notion
---

Explore: $ARGUMENTS

Use the **explore-schema** skill for exact output format.

## Step 1: Gather Context via Conversation

Use the **AskUserQuestion** tool to gather context interactively:

1. **Generate 10 questions** specific to the topic
   - Questions should probe key decisions, trade-offs, and unknowns
   - Present all 10 questions, let user answer or add their own

2. **Competitors** - "Who are the main competitors or existing solutions?"

3. **User scenarios** - "What are 3 real scenarios users will face?"

4. **Constraints** - "Any budget, timeline, or technical limitations?"

Keep questions conversational. Use tool options when there are clear choices, free text when open-ended.

## Step 2: Analyze

After gathering context:

1. Summarize key insights from user's answers to the 10 questions
2. Identify the core problem (root cause, not symptoms)
3. Consider existing codebase patterns if relevant
4. Propose 2-3 approaches with pros/cons
5. Make a recommendation with trade-offs

## Step 3: Save to Notion

Ask user: "Where should I save this? (Notion database name, page URL, or 'skip')"

If user provides a location:
1. Use `notion-search` or `notion-fetch` to find target
2. Create exploration document:
   - `Name` = topic
   - `Description` = one-line summary
   - Full analysis in body
3. If database has `Type` property, set to `["Document"]`

## Report

- Notion page URL (if saved)
- Recommended approach summary
- Next: `/vorbit:design:prd` to create PRD
