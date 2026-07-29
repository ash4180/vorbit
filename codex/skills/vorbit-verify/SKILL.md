---
name: vorbit-verify
description: Use when the user asks for a post-implementation validation against explicit acceptance criteria, a branch spec task or story, or a linked issue or PRD. It runs the real project tests, checks each criterion and code hygiene with evidence, reports pass or fail in the session, and may update spec task status or Linear issue status only when explicitly requested. Do not use to implement fixes, perform an open-ended code review, or validate requirements that have not been supplied.
---

# Vorbit Verify

Before verifying:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/verify.md`.
3. Load the applicable durable Vorbit rules for the current project and Codex agent scope.
4. Verify using the repo's real test and validation surfaces, then report only what was actually checked.
