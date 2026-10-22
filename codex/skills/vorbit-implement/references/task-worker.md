# Delegate one implementation task

The parent resolves scope and dependencies, handles tracking, reviews the diff, and decides completion. One worker searches existing code, implements one selected task, and tests it. Use a fresh worker for each new task, and resume the same worker for corrections to that task. Only one writer operates in a worktree at a time.

## Native dispatch

Inspect the live tool schema. Select the model through a supported tool parameter or an agent configuration you have read; a model name in a prompt does not select it.

| Host | Prepare | Resume |
|---|---|---|
| Claude Code | `Agent` with `subagent_type: "vorbit:implement-worker"`. Its plugin definition sets `model: sonnet`; pass `model: "sonnet"` too when supported. | `SendMessage` to the returned agent ID, or the installed native resume operation. |
| Codex with per-agent model selection | `spawn_agent` with `model: "gpt-6-luna"`, `fork_turns: "none"`, a unique task name, and the handoff path. | `followup_task` using the returned ID, or an equivalent that wakes a finished worker. |
| Other hosts | Require native delegation with explicit selection of the requested model and continuation. | Inspect the installed interface; do not invent parameters. |

Use the parent's exact worktree after branch setup. Do not request worktree isolation or a full-history fork that overrides the requested model. Supply all context explicitly. Never spawn a shell CLI as a fallback. If the named Claude worker is missing, reload the plugin or restart; for a source install, `bash dev-setup.sh` installs new components. Do not claim a launch before the native tool returns a handle.

Missing dispatch/model selection is `blocked_missing_capability` (or `blocked_missing_runtime` when the required runtime is absent). Leave the task unfinished. In a loop, preserve progress and stop active iteration with `status: failed`, `active: false`, and the capability reason; do not spend iterations retrying an unavailable tool. An explicit user override to another model or parent execution may proceed, recorded as an override. A known runtime model substitution requires that decision too.

## Parent: prepare the task

After implement Steps 1–3.5 and selecting exactly one item via Step 5, resolve storage and write guards using the spec-files reference. Create a unique `<spec folder>/implement-runs/<task-id>/<timestamp>/` folder, adding a suffix on collision. For description-only work, use a stable local task label; do not require or invent a PRD, epic, or tracker issue.

Write `worker-task.md` with:

- Role `implementation worker; do not delegate`, the selected task/story IDs or issue ID, and **Perform Prepare now; wait for continuation only before Execute** for the first turn.
- Absolute worktree, branch, HEAD, evidence folder, requested model, and installed implement workflow, this reference, execution contract, and applicable policy/skill paths. In Codex/Gemini installations the workflow lives in the sibling `vorbit-shared/workflows/implement.md`; this reference lives in the installed `vorbit-implement` directory.
- Exact requirements and acceptance criteria, relevant flow steps, test criteria, dependencies and evidence they are satisfied, scope exclusions, and approved file changes. Include a technical epic's supplied baseline when it has no product PRD. For Linear, provide the fetched requirements and their update timestamp; the worker does not need tracker access.
- The requirement baseline **after** the parent's in-progress update. Save the task/story and PRD text or content digests. Save a starting diff and status, and content snapshots of pre-existing editable files within write scope, including untracked files and user edits. A hash alone cannot reconstruct those edits for review; Git HEAD alone is insufficient in a dirty worktree. Keep snapshots local, protect any sensitive contents, and do not copy unrelated private files into evidence.
- Existing reusable code, test harness and commands, app/test environment, and localization/UI policies. State any missing prerequisites honestly.
- Write scope: selected application/test files, run evidence, and only explicitly required supporting files such as the mock registry or project glossary. Workers must not edit PRD/epic, task status, loop state, tracker records, or unrelated files; commit, push, publish, and branch switching belong outside this task. Do not disable tests, fake services, or relax assertions to obtain a pass. Repository testing rules take precedence.

The parent may track the selected item as in-progress but must not change requirements while a worker is active. Do not run competing source edits or tests that mutate the same environment.

## Worker: Prepare only

Start Prepare immediately on the initial dispatch; it needs no additional continuation. Read the handoff and referenced instructions. Verify worktree, branch, task baseline, allowed files, dependencies, and test capabilities. Search existing implementations and tests first, following implement Steps 4 and 4.5. Do not edit application code or run mutating tests yet.

Write `worker-ready.json` with `task_id`, `worktree`, `branch`, `revision`, `status` (`ready` or `blocked`), `reuse_files`, `planned_files`, `test_commands`, and `blockers`, then return. Use ready only for a clear, executable task with a real verification method. If a different file is needed, explain the code evidence and return it to the parent before editing. Do not invent requirements, expand scope, or decide product tradeoffs.

## Parent: save the handle and resume

Wait for Prepare to finish. Validate readiness against the task and actual worktree. Save `worker-session.json` with `task_id`, `agent_id` from the native tool, `runtime`, `requested_model`, `actual_model`, `model_evidence`, `worktree`, `branch`, `revision`, baseline references, `phase` (`prepare`, `execute`, or `review`), and `status` (`prepared`, `running`, `awaiting_review`, `accepted`, `blocked`, `failed`, or `canceled`). Keep a `reason` for non-success states.

Use null for an unverified actual model and say `requested via native model selection; actual model unverified`. Native metadata or transcript model fields can confirm it; the worker's self-description cannot. Record failures even when no handle was returned. Never fabricate a ready response or mark a blocked readiness result prepared.

For loop mode, persist the absolute session-file path in `workerSessionFile` before dispatch, initially with a null agent ID and `phase: prepare`, then immediately save the returned handle. Save `phase: execute` before the execution message and `phase: review` only after native execution completion. Recovery checks the saved phase and native activity: finished Prepare requires readiness validation followed by Execute, not review; finished Execute requires result review. A crash between dispatch and recording its acknowledgment is uncertain state: inspect the native transcript and partial results before sending another execution message. Never resend Execute to a running worker or launch a replacement because a record is incomplete.

Only after ready status, accepted scope, and the handle record, tell the user `Implementation worker prepared: [task], requested [model], agent [ID]`. Persist `phase: execute`, `status: prepared` before each execution continuation, including corrections, then resume that ID with **Execute the selected task; read [absolute worker-session.json] first; do not delegate**. Preserve the selected model on continuation. Do not launch a second worker. Set session status running when continuation succeeds; record a dispatch failure and inspect native activity before retrying.

## Worker: implement and return evidence

Require ready status and a prepared/running session for the same task. Recheck the worktree, requirements, and starting files before the first edit. If another writer changed the starting state, return the conflict; do not overwrite it. Apply implement Step 6, including reproducing bugs, Red/Green/Refactor, localization, and the project's real verification rules. Do not re-enter implement-loop because its state file exists.

Save verbose test logs and `worker-result.json` after meaningful progress using a temporary file and atomic rename. Stop owned test/browser/server processes and finish writes before returning. A worker result contains:

- `task_id`, `agent_id` copied from the session record, `worktree`, `branch`, `revision`, and the requirement baseline reference.
- `outcome`: `ready_for_review`, `blocked`, or `failed`; it never means the task is done.
- `changed_files` and a description of changes relative to the saved starting state, including new/deleted files and preservation of existing user edits.
- `criteria`: each exact acceptance criterion, observed result, and evidence path. Unverified criteria stay explicit.
- `tests`: command, working directory, phase (red/green/regression), exit code, and log path. Record skipped tests and unavailable checks; zero exit alone is insufficient.
- `blockers`, any scope questions, and remaining work. A partial or interrupted result remains unfinished.

If a failure persists after a focused correction, or a requirement/capability is missing, return evidence to the parent. Do not spend repeated turns on the same failure, silently upgrade models, or make product decisions. Corrections authorized by the parent resume this same worker and reuse its partial work.

## Parent: review before completion

1. Wait for native completion; message delivery, a ready response, or temporary silence is not completion. Verify the writer and its owned processes have stopped before reviewing or taking over. Record interrupted/failed work even if the result file is missing.
2. Match result task/agent/worktree/baseline to the session. Read the actual diff and new files against the saved starting state, not just the worker summary. Check scope, reuse, localization, and preservation of pre-existing edits. Missing or inconsistent evidence prevents acceptance.
3. Re-read requirements; an external change pauses implementation for reconciliation. First stop any surviving worker and verify shutdown; retain its handle if unverified. Set loop state inactive with `status: needs_input` and the reason, preventing automatic continuation while requirements are unresolved. Parent-owned status changes are not requirement changes: compare requirement content separately and refresh the recorded file timestamp after an authorized status-only update.
4. Check every acceptance criterion and inspect tests for meaningful coverage. Independently run the decisive focused checks on the resulting code. Reuse valid regression logs when no subsequent change invalidates them; repeat broader checks only for new failures, changes, or unresolved risk. Record the review decision and commands in `parent-review.md`.
5. For a correction within approved scope, persist the prepared execution state described above, then resume the same worker with specific findings. If a new decision or stronger model is needed, the parent resolves it, reports the change, and records any explicit caller override. Do not mark done or advance a loop while evidence is missing or a check fails.
6. Once accepted, set session status accepted. The parent alone performs implement Step 7 and advances loop state. Clear the current `workerSessionFile` only after saving acceptance and queue progress; retain the evidence folder. Use a fresh worker for the next task.

On cancellation, immediately persist `status: canceled`, `active: false` in loop state and mark the worker session canceled, retaining its handle. Then stop the native worker and verify it and its owned processes stopped before deleting loop state. Preserve partial edits and evidence; never reset or stash user work. If stop cannot be verified, keep the canceled state/handle with the reason; it must not automatically resume. An explicit later restart must establish the old worker is stopped before reconciling work. The same check applies when a restarted session cannot resume an old handle: establish shutdown, reconcile files/results, then record any replacement relationship.

Claude runtime reference: [native subagents and model selection](https://code.claude.com/docs/en/sub-agents). Codex capabilities vary by host; use the live tool schema.
