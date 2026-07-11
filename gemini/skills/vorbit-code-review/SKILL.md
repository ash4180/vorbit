---
name: vorbit-code-review
description: Use when the user asks for a read-only review of files, a branch diff, or a pull request, including pre-merge checks and code-review commands. It reports severity-ranked findings first and edits code only after separate user approval. Do not use as the implementation workflow, as acceptance-criteria verification, or for a generic request to explain code.
---

# Vorbit Review

Before reviewing:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/review.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Present findings first, with file references and concrete risk statements.
