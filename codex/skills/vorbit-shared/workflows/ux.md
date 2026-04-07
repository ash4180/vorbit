# Vorbit UX Clarification Workflow

Use when any skill needs to clarify user experience requirements through exhaustive questioning.

1. Load Vorbit durable rules before doing anything else.
2. Receive input: user story or task description + existing context from calling skill.
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
6. Output structured UX content: UX Expectation (user's exact words), User Flow, Acceptance Criteria grouped by: Happy Path, Validation, Errors, States, Permissions, Accessibility, Edge Cases.
7. Key principle: use user's verbatim answers as acceptance criteria. Never interpret or rephrase.
8. Quick mode for simple tasks (< 3 ACs): only ask relevant categories, skip edge case catalog, return minimal output.
