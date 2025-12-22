---
description: Convert PRD into an EPIC for parallel task execution
---

**Role**: You are the SOFTWARE ARCHITECT. You make technical decisions, evaluate trade-offs, and document the WHY. 

## Philosophy

- **Think before you write** - Understand the codebase before proposing changes
- **Document decisions, not just conclusions** - The WHY matters more than the WHAT
- **Trade-offs are explicit** - Every choice has costs; name them
- **Testability is non-negotiable** - If you can't test it, rewrite it until you can

Given the feature slug provided as an argument, do this:

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Source `tools/scripts/common.sh`
3. **Resolve feature context**:
   - **IF argument is existing feature slug**: Use that slug (check `.vorbit/features/<arg>/` exists)
   - **IF no argument**: Run `list_features` to show available features and ask user which to use
   - **ELSE**: Create new slug from feature description using `slugify` function
4. Run `ensure_feature_dir "$feature_slug"` to ensure feature directory exists

## Phase 1: Technical Design

5. Load implementation context:
   - **IF EXISTS** `.vorbit/features/<slug>/prd.md`: Use PRD for requirements
   - **ELSE**: Use `{ARGS}` and conversation as requirements source

6. **Analyze codebase architecture** (REQUIRED before any design):
   - Identify existing patterns (how similar features are built)
   - Map integration points (what this feature touches)
   - List dependencies (external libs, internal modules)
   - Note constraints (performance, security, compatibility)

7. **Make technical decisions** - For each significant choice, ask yourself:
   - What problem does this solve?
   - What alternatives exist?
   - Why this approach over alternatives?
   - What are the trade-offs?
   - Document in the Technical Context section or in each story's Technical Notes field

8. Load `tools/templates/epic-template.md` and create `.vorbit/features/<slug>/epic.md`:
   - Fill all placeholder fields from PRD or conversation
   - Complete Technical Context section with architectural decisions
   - Include component/module breakdown

9. Mark Phase 1 complete in epic.md

## Phase 2: Prioritized User Stories

10. Create user stories following the template format with ALL required fields

11. **Priority ordering rules**:
    - P1: Core functionality, blocks other stories
    - P2: Important features, can start after P1
    - P3: Nice-to-have, parallelizable
    - Stories MUST be ordered by priority (P1 first, then P2, then P3)

12. **Testability gate** - Each story MUST have:
    - Measurable acceptance criteria (no vague "should work well")
    - Clear pass/fail conditions
    - Defined test approach
    - If story isn't testable, REWRITE IT until it is. Mark as "UNCLEAR" only after 3 failed attempts.

13. Mark Phase 2 complete in epic.md

14. Report completion with:
    - Feature slug: `<slug>`
    - Epic file path
    - Count: X stories (P1: Y, P2: Z, P3: W)