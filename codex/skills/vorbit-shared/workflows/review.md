# Vorbit Review Workflow

Use for code review or pre-PR review.

1. Load the Vorbit runtime contract and durable rules. Review is read-only unless the user separately asks for fixes.
2. Resolve the exact scope (files, diff, commit, branch, or PR) and base. If there is no change, stop explicitly.
3. Run repository-native static checks relevant to changed file types, then inspect affected callers/consumers.
4. Use independent review passes when available, but verify every candidate finding against source before reporting it.
5. Prioritize correctness, regressions, security, silent failure, missing realistic tests, and risky assumptions. Do not inflate preferences into defects.
6. Report findings first by severity with concrete file/line evidence, impact, and smallest fix. Deduplicate overlapping findings.
7. If there are no findings, say so explicitly and note residual risk, skipped checks, and untested areas.
