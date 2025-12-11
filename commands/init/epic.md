---
description: Convert PRD into an EPIC for parallel task execution (Phase 1-2)
---

Given the feature slug provided as an argument, do this:

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Source `tools/scripts/common.sh`
3. **Resolve feature context**:
   - **IF argument is existing feature slug**: Use that slug (check `.vorbit/features/<arg>/` exists)
   - **IF no argument**: Run `list_features` to show available features and ask user which to use
   - **ELSE**: Create new slug from feature description using `slugify` function
4. Run `ensure_feature_dir "$feature_slug"` to ensure feature directory exists

## Phase 1: Design Complete

5. Load implementation context (priority order):
   - **IF EXISTS** `.vorbit/features/<slug>/prd.md`: Use PRD for requirements
   - **ELSE**: Use `{ARGS}` and conversation as requirements source
   - Analyze codebase directly for patterns and context
6. Load `tools/templates/epic-template.md` as base format
7. Fill template and save to `.vorbit/features/<slug>/epic.md`:
   - `[EPIC_NAME]` → extracted from PRD title or arguments
   - `[DATE]` → current date
   - `[PRD_FILE]` → path to source PRD
   - Technical context and design decisions
8. Mark Phase 1 complete in epic.md

## Phase 2: Ready for Task Generation

9. Review User Stories are complete with:
   - Clear acceptance criteria (Given/When/Then)
   - Edge cases identified
   - Story IDs (S-001, S-002, etc.) for task mapping
10. Mark Phase 2 complete in epic.md
11. Report completion with:
    - Feature slug: `<slug>`
    - Epic file path

## 5-Phase Progress Tracking
- [ ] Phase 1: Design complete (this command)
- [ ] Phase 2: Stories ID ready for task mapping (this command)
- [ ] Phase 3: Tasks generated `/vorbit:manage:task` command
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation runs tests `/vorbit:manage:validate` command