---
description: Quick exploration of ideas before PRD creation
---

Given the topic/problem description provided as an argument, do this:

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards and output guidelines
2. Source `tools/scripts/common.sh`
3. **Extract feature slug** from arguments:
   - Convert topic to slug using `slugify` function (e.g., "User Authentication" → "user-authentication")
   - Run `ensure_feature_dir "$feature_slug"` to create `.vorbit/features/<slug>/`
4. Load `tools/templates/explore-template.md` as base format

## Create or Update Explore Document

5. **Create the explore document first** with the topic and question:
   - Save to `.vorbit/features/<slug>/explore.md` immediately
   - Include these questions in a "Context Questions" section to ask user (All questions should be listed down with number and real world scenario):
     - **Scope check:** What are the top 10 questions user should be asking for this project?
     - **Competitor market analysis:** What are the 10 most likely competitors in the market?
     - **Scenario planning:** What are the 3 most likely scenarios user will face?
     - **Constraints:** Any budget, timeline, or technical limitations?
     - **Context gap:** Any unclear, missing, or incomplete information that should be clarified before giving user the best answer?
   - Tell user: "Fill in the Context Questions section, then run `/vorbit:init:explore [topic]` again"
6. **If document exists with filled answers**, analyze the problem using:
   - User's answers from the document
   - Arguments provided
   - Existing codebase if relevant
7. Evaluate 3 different approaches following project principles
8. Update the document with completed analysis:
   - `[TOPIC]` → extracted from arguments
   - `[NAME]` → descriptive option names
   - Fill problem statement, options analysis, and final recommendation
9. Report completion with:
   - Feature slug: `<slug>`
   - Explore file path
   - Next step: `/vorbit:init:prd <slug>` to create PRD

## File Structure

```
.vorbit/features/<slug>/
└── explore.md     ← Created by this command
```