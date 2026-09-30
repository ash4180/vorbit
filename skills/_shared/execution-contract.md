# Vorbit Execution Contract

Apply this contract before every Vorbit workflow.

## Instruction Precedence

Below the standard system > user > repository-instructions order, Vorbit layers rank: project-scoped durable policy > universal durable policy > agent-specific guidance > workflow defaults. More specific guidance may refine lower levels but cannot override a higher-authority rule. File read order does not grant authority. Surface same-level contradictions instead of silently choosing the last file read.

## Capability and Mutation Gate

Before an external write, destructive local change, commit, push, or publication:

1. verify the required capability and its current operation/parameter schema;
2. read current state and detect whether the intended artifact already exists;
3. show any workflow-required mutation preview and obtain its approval;
4. record successful external IDs so a retry resumes rather than duplicates work.

Do not guess unavailable tool names. A missing required capability ends as `blocked_missing_capability`. Ordinary local edits explicitly requested by the user do not need redundant confirmation.

## Connector Login Failures

When a connector (MCP) call fails because of login or access (expired token, 401, 403, "not authenticated", "reconnect"):

1. Stop the step that needs it. Do not do the same job through another connector, another workspace, WebFetch, or a shell call.
2. Tell the user which connector failed and the exact fix: reconnect it (in Claude Code, run `/mcp`). Then wait for the user.
3. Never report that step as done, and never offer an unrelated workaround in place of the fix.
4. Unattended run: finish every step that does not need the connector. Put the failure and the reconnect step at the top of the final result. The terminal status is `blocked_missing_capability`, with the finished steps listed.

## Tracker Communication

Do not create Linear comments, except the single user-approved comment the tutorial workflow may post. Report progress, evidence, blockers, cancellation, and completion in the current session instead. Explicitly authorized issue creation, description edits, and status changes remain allowed.

Keep Linear titles, descriptions, and approved comments focused on the project work. Do not mention Vorbit, add tool attribution, or expose local skill commands, private spec paths, or worktree locations. Include the project branch name or an available PR link when useful; local workflow details stay in the current session.

## Base Branch

The base branch is the branch this branch merges into. Diffs compare against it, and new branches start from it. Use the first step that gives an answer; if a step fails, go to the next:

1. A branch the user or caller names.
2. The open PR's base (`gh pr view --json baseRefName -q .baseRefName`).
3. A saved project rule naming the integration branch.
4. The remote default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, without the remote prefix).

If step 4 gives `main` but a `dev` or `develop` branch also exists, ask the user once for this project. Teams often keep GitHub's default on `main` while merging work into `dev`, and a wrong base shows other people's changes as yours. Save the answer as a project rule, so step 3 answers next time. In an unattended run, use step 4 and write an `Assumed:` line that names the other branch.

## Source Baseline

For requirements-driven work, record the source artifact ID/URL and update timestamp or revision. Carry globally unique user-story IDs (`US-*`) forward; reference acceptance criteria by quoting their text verbatim and flow steps as `Flow N, step M`. If the source changes mid-work, stop and reconcile before continuing.

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
