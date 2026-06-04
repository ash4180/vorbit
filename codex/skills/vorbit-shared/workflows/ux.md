# Vorbit UX Clarification Workflow

Use when any skill needs to clarify user experience requirements through exhaustive questioning, OR when a calling workflow needs to consult senior-UX-designer knowledge directly without invoking the full Q&A ritual.

**Knowledge files (read directly when needed):**
- `vorbit-shared/references/ux-knowledge/question-matrix.md` — 14 question categories for exhaustive UX questioning
- `vorbit-shared/references/ux-knowledge/edge-case-catalog.md` — concrete edge cases per input/state/network/auth/device/time/business-logic
- `vorbit-shared/references/ux-knowledge/ux-philosophy.md` — decision frameworks (block vs warn, auto-save vs manual, etc.) and state design principles

1. Load Vorbit durable rules before doing anything else.
2. Receive input: user story or task description + existing context from calling skill.
3. **Question by category** — load `vorbit-shared/references/ux-knowledge/question-matrix.md` and use 2-4 questions per batch via AskUserQuestion. Walk relevant categories:
   - Entry & happy path
   - Validation rules
   - System errors
   - Permissions
   - Loading & empty states
   - Concurrent & time-based edge cases
   - Device & accessibility
   - Recovery & notifications
4. Skip irrelevant categories. **Cross-check answers against `edge-case-catalog.md`** — identify common edge cases the user hasn't covered yet.
5. If user says "I don't know" — load `ux-philosophy.md` for decision frameworks. Present options with trade-offs; let them choose.
6. Output structured UX content: UX Expectation (user's exact words), User Flow (textual; for diagrams use `/vorbit-journey`), Acceptance Criteria grouped by: Happy Path, Validation, Errors, States, Permissions, Accessibility, Edge Cases.
7. Key principle: use user's verbatim answers as acceptance criteria. Never interpret or rephrase.
8. Quick mode for simple tasks (< 3 ACs): only ask relevant categories, skip edge case catalog, return minimal output.

**Direct reference access for other workflows:** `/vorbit-explore`, `/vorbit-prd`, `/vorbit-journey`, `/vorbit-figma`, `/vorbit-epic`, `/vorbit-implement`, `/vorbit-verify` can read `vorbit-shared/references/ux-knowledge/*.md` files directly without invoking this full workflow. Use direct read for quick lookups (e.g., "what does the catalog say about empty states?"); invoke this full workflow when requirements are vague and you need the whole question-batch ritual.
