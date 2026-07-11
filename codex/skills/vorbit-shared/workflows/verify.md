# Vorbit Verify Workflow

Use for validation after implementation.

1. Load the Vorbit runtime contract and durable rules. Verification is read-only unless the user explicitly requests a Linear update.
2. Resolve the requirement baseline and map each `US-*.AC-*` to observable evidence. If no criteria exist, derive a proposed checklist from the request and label it as proposed.
3. Run project-native focused tests first, then the smallest relevant regression suite and targeted smoke checks. A failing command marks the result failed but does not suppress other safe checks.
4. Record each command, exit status, relevant output, and untested area. Never convert "not run" into a pass.
5. Report a structured result: `passed`, `failed`, or `blocked`; AC-by-AC evidence; regression evidence; hygiene findings; and residual risk.
6. Only after a full pass and explicit authorization, add the evidence to Linear or move the issue to the team's review-ready state. Do not mark the implementation parent Done before merge.
