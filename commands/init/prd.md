---
description: Create a Product Requirements Document. No fluff, just what needs building.
---

Given the feature slug or description provided as an argument, do this:

## Setup

1. Read ./CLAUDE.md and ~/.claude/CLAUDE.md for project standards
2. Source `tools/scripts/common.sh`
3. **Resolve feature context**:
   - **IF argument is existing feature slug**: Use that slug (check `.vorbit/features/<arg>/` exists)
   - **IF argument references explore file**: Extract slug from explore file location
   - **ELSE**: Create new slug from feature description using `slugify` function
4. Run `ensure_feature_dir "$feature_slug"` to ensure feature directory exists
5. Load `tools/templates/prd-template.md` as base format

## Create PRD

6. Check for existing `.vorbit/features/<slug>/explore.md` for context
7. Fill template and save to `.vorbit/features/<slug>/prd.md`:
   - `[FEATURE_NAME]` → extracted from arguments or explore doc
   - `[DATE]` → current date
   - Fill all sections with business requirements only (no technical details)
8. Report completion with:
   - Feature slug: `<slug>`
   - PRD file path
   - Next step: `/vorbit:init:epic <slug>` to create implementation plan

## PRD Requirements

1. **One user journey per PRD** - If you can't ship value from this PRD alone, split it
2. **Set success criteria** - How do we know when we're done? Measurable business outcomes
3. **List functional requirements** - What must this thing do? List specific user behaviors
4. **Define business constraints** - What limits us? Budget, timeline, compliance, user workflows
5. **Include edge cases & failures** - What can go wrong from user perspective? How do we handle it?
6. **Specify out of scope** - What are we NOT building? Be clear

## File Structure

```
.vorbit/features/<slug>/
├── explore.md     ← Optional (from /init:explore)
└── prd.md         ← Created by this command
```