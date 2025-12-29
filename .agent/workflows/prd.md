# PRD

Create a Product Requirements Document. No fluff, just what needs building.

Use the **prd-schema** rule for output format and validation.

## Step 1: Gather Context

* **IF Notion URL provided**: Fetch page content, proceed to Step 3 (restructure mode)
* **IF existing context (explore doc, conversation)**: Use that context, proceed to Step 2 for gaps
* **IF starting fresh**: Proceed to Step 2

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

## Step 4: Save to Notion (if available)

Ask: "Where should I save this PRD? (database name, page URL, or 'skip')"

If saving:
1. Search for target database
2. Create with Name = feature name, full PRD in body
3. If database has `Type` property, set to `["PRD"]`

## Report

* Notion URL (if saved)
* Summary: X user stories, Y success criteria
* Next: `/journey` or `/epic`
