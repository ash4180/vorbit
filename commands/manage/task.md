---
description: Create tasks from epic or conversation
---

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Source `tools/scripts/common.sh`
3. **Resolve feature context**:
   - **IF argument is existing feature slug**: Use that slug
   - **IF no argument**: Run `list_features` to show available features and ask user which to use
   - **ELSE**: Create new slug from conversation using `slugify` function
4. Run `tools/scripts/task.sh setup` to validate environment

## Create Tasks

5. Generate tasks:
   - **IF** `.vorbit/features/<slug>/epic.md` exists:
     Run `tools/scripts/task.sh generate .vorbit/features/<slug>/epic.md .vorbit/features/<slug>`
   - **ELSE**:
     Run `tools/scripts/task.sh generate-conversation "{ARGS}" .vorbit/features/<slug>`

6. Report completion with:
   - Feature slug: `<slug>`
   - Tasks file path
   - Next step: `/vorbit:manage:implement <slug>` to start implementation

## File Structure

```
.vorbit/features/<slug>/
├── explore.md     ← Optional
├── prd.md         ← Optional
├── epic.md        ← Optional (from /vorbit:init:epic)
└── tasks.md       ← Created by this command
```

## Task ID Format

- Task IDs: T001, T002, etc.
- TDD pairs: T001a (test), T001b (implementation)
