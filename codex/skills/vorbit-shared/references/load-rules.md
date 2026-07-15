# Vorbit Runtime Contract for Codex

Apply this contract once before every Vorbit workflow.

## Resolve Durable Rules

1. Resolve the project root with `git rev-parse --show-toplevel`, falling back to the current directory.
2. Resolve `CODEX_HOME` from the environment, defaulting to `~/.codex`.
3. Run:

   ```bash
   "$CODEX_HOME/bin/vorbit-resolve-rules" --agent codex --project-root "$PROJECT_ROOT"
   ```

4. Read the returned JSON. Traverse its `rules` array in ascending `order`, load only each listed readable `path`, and retain that item's `authority`, `specificity`, and `tier` metadata while reasoning. The same JSON carries top-level `storage_root` and `project_slug` — use them whenever a workflow needs a state or registry path (e.g. `<storage_root>/projects/<project_slug>/mock-registry.json`); `<rules-root>` in workflow text means `<storage_root>/rules`.
5. If the resolver is missing, stop with `blocked_missing_runtime` and tell the user to rerun `scripts/sync-codex-skills.sh`. Do not reconstruct the hashed project slug or storage config by guesswork.

The resolver is authoritative for `VORBIT_HOME`, global `[storage].root`, project slug overrides, path-hashed default slugs, include flags, and deterministic filename ordering.

## Precedence

Use this authority order:

1. system/developer instructions;
2. explicit user request and approvals;
3. repository instructions such as `AGENTS.md`;
4. project-scoped shared Vorbit policy;
5. universal shared Vorbit policy;
6. project-scoped Codex guidance;
7. universal Codex guidance;
8. workflow defaults.

Read order does not grant authority. More-specific rules may refine lower levels but cannot override higher authority. Surface same-level contradictions as `blocked_rule_conflict`; never use last-file-wins.

## Capability and Mutation Gate

Before an external write, destructive local change, commit, push, or publication:

1. verify that the required capability exists and inspect its current operation/parameter schema;
2. read current state and check whether the intended artifact already exists;
3. show any workflow-required mutation preview and obtain approval;
4. record successful external IDs so retries resume rather than duplicate work.

Do not guess unavailable tool names. A missing required capability ends as `blocked_missing_capability`. Ordinary local edits explicitly requested by the user do not need redundant confirmation.

## Source, Policies, and Result

- For requirements-driven work, carry the source artifact ID/URL and update timestamp or revision. If it changes mid-work, stop and reconcile.
- Carry globally unique `US-*` story identifiers through planning, implementation, and verification; quote acceptance criteria verbatim and address flow steps as `Flow N, step M`.
- Treat `vorbit-ux`, `vorbit-ui-patterns`, and `vorbit-react-best-practices` as conditional supporting policies. Repository conventions win over framework examples.
- Verify observable behavior with project-native checks. Report commands run, passes, failures, and unverified areas.
- End with one status: `completed`, `needs_input`, `needs_backend`, `blocked`, `blocked_missing_capability`, `blocked_missing_runtime`, `blocked_rule_conflict`, `failed`, or `canceled`.
- Workflow-specific results such as verification `passed` or `failed` are evidence fields, not substitutes for this execution status.
- On partial external success, report completed mutations and the exact resume point immediately.
