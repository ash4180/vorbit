# Explore

Quick exploration of ideas before PRD creation.

Use the **explore-schema** rule for output format and validation.

## Step 1: Ask 10+ Questions

* **MANDATORY: Ask at least 10 questions before generating options.**
* Generate 10 questions specific to the topic
* Present ALL 10 in a single interaction

Question categories:
1. Core functionality question
2. User needs question
3. Scale/volume question
4. Error handling question
5. Constraints question
6. Integration question
7. Security/compliance question
8. Timeline question
9. Trade-off question
10. Edge case question

Ask: "Which are most important? What's missing?"

Then follow-up:
* **Competitors**: "Who are existing solutions?"
* **User scenarios**: "Describe 3 real scenarios"
* **Constraints**: "Budget, timeline, or technical limitations?"

**DO NOT proceed until you have answers to 10+ questions.**

## Step 2: Analyze

After gathering context:
1. Summarize insights from all question answers
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros/cons/effort/risk
4. Make recommendation addressing constraints

## Step 3: Save to Notion (if available)

Ask: "Where should I save this? (database name, page URL, or 'skip')"

If saving:
1. Search for target database
2. Create document with Name = topic, full analysis in body
3. If database has `Type` property, set to `["Exploration"]`

## Report

* Notion URL (if saved)
* Recommended approach summary
* Next: `/prd` workflow
