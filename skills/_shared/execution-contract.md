# Vorbit Execution Contract

Apply this contract before every Vorbit workflow.

## Instruction Precedence

Use this authority order:

1. system/developer instructions;
2. the user's explicit request and approvals;
3. repository instructions such as `AGENTS.md` or `CLAUDE.md`;
4. project-scoped durable Vorbit policy;
5. universal durable Vorbit policy;
6. agent-specific guidance;
7. workflow defaults.

More specific guidance may refine lower levels but cannot override a higher-authority rule. File read order does not grant authority. Surface same-level contradictions instead of silently choosing the last file read.

## Capability and Mutation Gate

Before an external write, destructive local change, commit, push, or publication:

1. verify the required capability and its current operation/parameter schema;
2. read current state and detect whether the intended artifact already exists;
3. show any workflow-required mutation preview and obtain its approval;
4. record successful external IDs so a retry resumes rather than duplicates work.

Do not guess unavailable tool names. A missing required capability ends as `blocked_missing_capability`. Ordinary local edits explicitly requested by the user do not need redundant confirmation.

## Source Baseline

For requirements-driven work, record the source artifact ID/URL and update timestamp or revision. Carry globally unique user-story, acceptance-criterion, and flow-step IDs forward. If the source changes mid-work, stop and reconcile before continuing.

## Policy Composition

`ux`, `ui-patterns`, and `react-best-practices` are supporting policies, not lifecycle stages. Apply them only when relevant. Repository conventions win over their framework examples; never introduce a new UI, data, caching, or animation stack silently.

## Verification and Terminal Result

Verify observable behavior with project-native checks. Report what ran, what passed, what failed, and what remains unverified. Use one terminal status:

- `completed`
- `needs_input`
- `needs_backend`
- `blocked`
- `blocked_missing_capability`
- `blocked_missing_runtime`
- `blocked_rule_conflict`
- `failed`
- `canceled`

Workflow-specific results such as verification `passed` or `failed` are evidence fields, not substitutes for this execution status.

Never call an incomplete or unverified artifact complete. On partial external success, report the completed mutations and resume point immediately.
