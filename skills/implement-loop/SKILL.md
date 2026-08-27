---
name: implement-loop
description: Use only when the user explicitly invokes loop mode, supplies --loop or --cancel, or asks to autonomously work through an ordered task queue from the branch epic plan or a Linear epic. After one queue confirmation it changes code, runs tests, updates task or issue statuses, and reports progress in the session until completion. Loop execution requires a branch spec story or a Linear issue; do not use for a one-off implementation, issue planning, or unattended work without explicit loop intent.
---

# Implement Loop Skill

Run an approved implementation queue — a story from the branch epic plan, or a legacy Linear parent — as a bounded, resumable state machine. Use the normal implement skill's search, scope, TDD, and verification rules for each queue item.

Read and follow `../_shared/execution-contract.md` before starting.

Spec mode reads the queue from `.vorbit/epic.md` in the current worktree — read `../_shared/spec-files.md` for path resolution, the `Branch:` line check, and status fields — and needs no Linear connection. Linear mode: use the connected Linear tools only after verifying their current schemas. The Vorbit Claude plugin normally exposes `get_issue`, `list_issues`, `save_issue`, and `list_issue_statuses`.

## Inputs and Preconditions

Require:

- a queue source: a story ID (`US-###`) from the branch epic plan — or that plan's only story when unambiguous — or a Linear issue ID or URL;
- explicit `--loop` intent, unless resuming an active state file;
- a working Linear connection for Linear mode only;
- a repository with a clean or understood worktree;
- one queue confirmation before a multi-item run.

The stop hook keys off the state file's `status` field, never chat text: the loop ends only when `status` is `completed`, so ordinary prose can never stop it accidentally.

## State File

Store runtime state at `.claude/.loop-state.json`. It is local runtime state and must not be committed.

```json
{
  "version": 2,
  "active": true,
  "status": "running",
  "command": "/vorbit:implement:implement VIB-100 --loop",
  "maxIterations": 50,
  "iteration": 1,
  "parentIssueId": "VIB-100",
  "sourceUpdatedAt": "2026-01-01T00:00:00Z",
  "queue": [
    {"id": "VIB-101", "phase": 1, "priority": "High"},
    {"id": "VIB-102", "phase": 1, "priority": "Normal"},
    {"id": "VIB-103", "phase": 2, "priority": "High"}
  ],
  "currentIndex": 0,
  "completedIssueIds": [],
  "lastFailureFingerprint": null,
  "repeatedFailureCount": 0,
  "blockReason": null
}
```

`status` is the single source of truth for the stop hook; `active` is a human-readable mirror that is true only while `status` is `running`. The `command` must include `--loop`; the stop hook re-injects it on every iteration and ignores state written with a different `version`. In spec mode, `parentIssueId` holds the story ID (e.g. `US-001`), queue entries hold task IDs (e.g. `T3`), and `sourceUpdatedAt` holds the epic.md modification time — the state machine is otherwise identical.

## Initialization

### 1. Handle Cancel

For `--cancel`:

1. Read the state before deleting it.
2. Report the current issue, completed items, and worktree state.
3. Report cancellation in the current session; do not claim the code was reverted.
4. Delete the state file and stop.

Never discard or reset code during cancellation.

### 2. Resume or Build the Queue

If an active `running` state exists, resume it. Re-read the source first (the story section in `epic.md`, or the Linear parent); if it changed since `sourceUpdatedAt`, set `active: false`, `status: "needs_input"`, and a precise `blockReason`, then preserve state and stop to reconcile the queue.

If an inactive `needs_input`, `blocked`, or `failed` state exists, report its reason and resume point instead of replacing it. Resume only after the user supplies or confirms the missing resolution: reconcile the source/queue as needed, update the baseline, clear failure tracking, reset `iteration` to 1, then set `active: true` and `status: "running"`. Resetting `iteration` matters: a state blocked at `maxIterations` would otherwise re-block after a single cycle. A completed state is left for the stop hook to delete.

For a new run:

1. Spec mode: read the story section and its tasks from `epic.md`. Linear mode: fetch the parent and its sub-issues.
2. Parse the source's `Implementation Order` section phase by phase.
3. Within a phase, sort by priority (`P1`/`Urgent`, `P2`/`High`, `P3`/`Normal`, `Low`), then listed or creation order.
4. Skip tasks whose `Status` is `done` and issues that are `Done`, `Completed`, or `Cancelled`.
5. Accept a flat numbered list as a single sequential phase.
6. Append tasks or sub-issues missing from the section as an `unplanned` final phase and call them out.
7. If the section is absent, build a priority-ordered fallback and label it as a guess.

A `Parallel` label means dependency independence, not permission for concurrent writers in one worktree. Process items deterministically unless the environment provides isolated worktrees and the user explicitly approves parallel execution.

### 3. Confirm and Persist

For a multi-issue queue, show issue IDs, titles, phases, priorities, skipped items, unplanned items, and whether fallback ordering was used. Ask once:

- **Start** — persist state and begin;
- **Reorder** — accept a revised order, show it again, and re-confirm;
- **Cancel** — do not write state.

For a single issue explicitly started with `--loop`, persist and begin without another confirmation.

## Iteration

For the current `queue[currentIndex]` item, or the parent when the queue is empty:

1. Re-read the current item (its task section in `epic.md`, or the Linear issue) and compare its baseline (file modification time, or issue update timestamp) with the one used for the current cycle.
2. Mark it started — spec task: set its `**Status:**` line to `in-progress`; Linear issue: move it to the team's exact In Progress state — and report the start in the current session.
3. Apply the normal implement workflow without re-entering loop initialization:
   - search for existing code and tests first;
   - map the issue's acceptance criteria and flow steps;
   - write or update an honest focused test when a harness exists;
   - implement only the current issue;
   - run focused and relevant regression checks.
4. Record AC-by-AC evidence and test commands.

### Complete Current Item

Only when every current-item AC passes and relevant tests pass:

1. Report completion, changed files, and verification evidence in the current session.
2. Spec task: set its `**Status:**` line to `done`. Linear sub-issue: move it to the team's Done/Completed state.
3. Add its ID to `completedIssueIds`, increment `currentIndex`, clear failure tracking, and write state atomically.
4. Continue with the next item.

### Incomplete or Failed Current Item

If work remains, keep the same queue index. Report the unmet AC or failing check.

Create a failure fingerprint from the failing command/error plus the unmet acceptance criteria. If the same fingerprint occurs three consecutive cycles:

1. set `active: false`, `status: "blocked"`, and `blockReason`;
2. preserve the state file for inspection;
3. report the blocker concisely in the current session;
4. stop and ask for the missing decision or external change.

Do not burn iterations repeating the same failure.

## Queue Completion

After all sub-issues finish:

1. Re-read the source (the story section, or the Linear parent) and verify every story/parent AC against accumulated evidence.
2. If an AC is unmet and no remaining item owns it, set `active: false`, `status: "needs_input"`, and `blockReason`, then preserve state and stop; do not invent unplanned scope.
3. Report "ready for verification/PR" in the current session. Spec mode: suggest `/vorbit:ticket` to refresh the story summaries. Linear mode: keep the implementation parent In Progress; a parent becomes In Review after PR creation and Done only after merge.
4. Set state to `active: false`, `status: "completed"`.

The stop hook deletes a completed state and lets the session end. Report completion in your final message for the user; the hook does not read that text.

## Terminal States

- `completed` — queue and parent ACs verified; the stop hook deletes the state.
- `needs_input` — a requirement, queue, or source revision needs a user decision.
- `blocked` — the same failure repeated three times or iteration limit reached.
- `failed` — a non-recoverable tool or state error.
- `canceled` — user canceled; state deleted, code left untouched.

At `maxIterations`, preserve state as blocked and report the current issue and reason. Never delete evidence silently.

## Progress Output

Each cycle reports:

```text
Current: T2 (spec mode) or VIB-102 (Linear mode) — title
Phase: 1
Acceptance criteria: 3/4 passed
Queue progress: 1/3 complete
Tests: command + result
Status: running | needs_input | blocked | failed | completed
```
