# Vorbit UX Clarification Workflow

Use when any skill needs to clarify user experience requirements through exhaustive questioning.

1. Load Vorbit durable rules before doing anything else.
2. Receive input: owning `US-###` and story text (or a provisional task), existing context, and the next available document-wide flow number. Do not mint final AC IDs without an owning story.
3. Question by category (use 2-4 questions per batch):
   - Entry & happy path
   - Validation rules
   - System errors
   - Permissions
   - Loading & empty states
   - Concurrent & time-based edge cases
   - Device & accessibility
   - Recovery & notifications
4. Skip irrelevant categories. Cross-check answers against common edge cases.
5. If user says "I don't know" — present options with trade-offs, let them choose.
6. Preserve every requirement-bearing question and answer verbatim as immutable evidence (`E-01`, `E-02`, ...).
7. Separately normalize evidence into observable, testable ACs. Confirm any added specificity with the user, preserve exact UI copy/domain terms, then assign story-scoped IDs (`US-001.AC-01`, ...). Link every AC to evidence; never emit final IDs without an owning `US-###`.
8. Using the next available document-wide flow number, map every confirmed AC to explicit `F#-S#` steps with surface/action/visible result; preserve branches and loops. Output: UX Expectation, Evidence, User Flow, and confirmed Acceptance Criteria grouped by Happy Path, Validation, Errors, States, Permissions, Accessibility, and Edge Cases. Complex diagrams route through journey rather than calling `generate_diagram` directly.
9. Quick mode for simple tasks (< 3 ACs): ask only relevant categories, skip the catalog, and return minimal evidence plus confirmed normalized AC candidates.
