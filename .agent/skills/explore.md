---
name: explore
description: Quick exploration of ideas before PRD creation
---

## Step 0: Detect Platform & Verify Connection

**Auto-detect platform from user input:**

* User mentions "Notion" → Use Notion
* User mentions "Anytype" → Use Anytype
* Otherwise → Ask at save time (Step 3)

**Verification Logic:**

* **If Notion detected:** Run `notion-find` searching for "test".
* *Failure:* "Notion connection expired. Run `/mcp` to reconnect, then retry." → **STOP**


* **If Anytype detected:** Run `API-list-spaces`.
* *Failure:* "Anytype connection expired. Run `/mcp` to reconnect, then retry." → **STOP**

* **If no platform detected:** Proceed to Step 1.

## Step 1: Mandatory Sequential Gate 

### RULE: You are a synchronous interviewer. You must use the /ask tool (or equivalent human-in-the-loop pause) for every question.

- Ask ONLY Question 1 in the chat as plain text.
- STOP ALL EXECUTION. Do not generate the next task. Do not auto-check the box.
- WAIT for a message from user.
- Only after user reply, update user answer to your task, move to Question 2. use standard chat text to ensure the 'Enter' key works."


### Question categories:

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

### Format

- [Question 1/10] Core Functionality:

1. Selection 1
2. Selection 2
3. etc.

## Step 2: Analysis

Once the interview is complete, synthesize the data:

1. **Executive Summary:** Insights from all responses.
2. **Root Cause Discovery:** Identify the underlying problem (not just symptoms).
3. **Options:** Propose 2-3 approaches (Rank by: Pros/Cons/Effort/Risk).
4. **Recommendation:** Select the best path based on the user's constraints.

---

## Step 3: Save Document

**Platform Selection:**

* **If platform was detected in Step 0:** Use that platform directly.
* **If no platform detected:** Ask: "Where should I save this? (Notion, Anytype, or skip)"

### Save to Notion:

1. Ask for database name or page URL.
2. Search for target database.
3. Create page: **Name** = Topic Name, **Body** = Full Analysis.
4. If property `Type` exists, set to `["Exploration"]`.

### Save to Anytype:

1. Run `API-list-spaces` and ask the user to select one.
2. Run `API-create-object`:
* `type_key`: "page"
* `name`: Topic Name
* `body`: Full Analysis (Markdown)

---

## Final Report

* **Status:** URL or Object ID of the saved document.
* **Platform:** Mention if Notion or Anytype was used.
* **Summary:** 2-sentence summary of the recommended approach.
* **Next Step:** Suggest the `/prd` workflow to begin technical specs.