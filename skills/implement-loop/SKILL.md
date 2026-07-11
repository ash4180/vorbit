---
name: implement-loop
description: Use only when the user explicitly invokes loop mode, supplies --loop or --cancel, or asks to autonomously work through an ordered Linear epic or sub-issue queue. After one queue confirmation it changes code, runs tests, and updates Linear statuses and comments until completion. Loop execution requires a Linear issue; do not use for a one-off implementation, issue planning, or unattended work without explicit loop intent.
---

# Implement Loop Skill

Run an approved Linear implementation queue as a bounded, resumable state machine. Use the normal implement skill's search, scope, TDD, and verification rules for each queue item.

Read and follow `../_shared/execution-contract.md` before starting.

Use the connected Linear tools only after verifying their current schemas. The Vorbit Claude plugin normally exposes `get_issue`, `list_issues`, `save_issue`, `save_comment`, and `list_issue_statuses`.

## Inputs and Preconditions

Require:

- a Linear issue ID or URL;
- explicit `--loop` intent, unless resuming an active state file;
- a working Linear connection;
- a repository with a clean or understood worktree;
- one queue confirmation before a multi-issue run.

Use the fixed completion marker `<!-- VORBIT_LOOP_COMPLETE -->`. Do not accept arbitrary completion text: ordinary prose must never stop the hook accidentally.

## State File

Store runtime state at `.claude/.loop-state.json`. It is local runtime state and must not be committed.

```json
{
  "version": 2,
  "active": true,
  "status": "running",
  "command": "/vorbit:implement:implement VIB-100 --loop",
  "completionSignal": "<!-- VORBIT_LOOP_COMPLETE -->",
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

The `command` must include `--loop`; the stop hook re-injects it on every iteration.

## Initialization

### 1. Handle Cancel

For `--cancel`:

1. Read the state before deleting it.
2. Report the current issue, completed items, and worktree state.
3. If a Linear issue was started, add a cancellation comment; do not claim the code was reverted.
4. Delete the state file and stop.

Never discard or reset code during cancellation.

### 2. Resume or Build the Queue

If an active `running` state exists, resume it. Re-fetch the parent first; if its description changed since `sourceUpdatedAt`, set `active: false`, `status: "needs_input"`, and a precise `blockReason`, then preserve state and stop to reconcile the queue.

If an inactive `needs_input`, `blocked`, or `failed` state exists, report its reason and resume point instead of replacing it. Resume only after the user supplies or confirms the missing resolution: reconcile the source/queue as needed, update the baseline, clear failure tracking, then set `active: true` and `status: "running"`. A completed state is left for the stop hook to validate and delete.

For a new run:

1. Fetch the parent and its sub-issues.
2. Parse the parent's `## Implementation Order` section phase by phase.
3. Within a phase, sort by Linear priority (`Urgent`, `High`, `Normal`, `Low`), then creation time.
4. Skip `Done`, `Completed`, and `Cancelled` issues.
5. Accept a flat numbered list as a single sequential phase.
6. Append Linear sub-issues missing from the section as an `unplanned` final phase and call them out.
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

1. Re-fetch the issue and compare its update timestamp with the baseline used for the current cycle.
2. Move it to the team's exact In Progress state and add one start comment.
3. Apply the normal implement workflow without re-entering loop initialization:
   - search for existing code and tests first;
   - map `US-*.AC-*` and `F*-S*` requirements;
   - write or update an honest focused test when a harness exists;
   - implement only the current issue;
   - run focused and relevant regression checks.
4. Record AC-by-AC evidence and test commands.

### Complete Current Item

Only when every current-item AC passes and relevant tests pass:

1. Add a completion comment containing files and verification evidence.
2. For a sub-issue, move it to the team's Done/Completed state.
3. Add its ID to `completedIssueIds`, increment `currentIndex`, clear failure tracking, and write state atomically.
4. Continue with the next item.

### Incomplete or Failed Current Item

If work remains, keep the same queue index. Report the unmet AC or failing check.

Create a failure fingerprint from the failing command/error plus unmet AC IDs. If the same fingerprint occurs three consecutive cycles:

1. set `active: false`, `status: "blocked"`, and `blockReason`;
2. preserve the state file for inspection;
3. add a concise Linear blocker comment when authorized;
4. stop and ask for the missing decision or external change.

Do not burn iterations repeating the same failure.

## Queue Completion

After all sub-issues finish:

1. Re-fetch the parent and verify every parent AC against accumulated evidence.
2. If an AC is unmet and no remaining issue owns it, set `active: false`, `status: "needs_input"`, and `blockReason`, then preserve state and stop; do not invent unplanned scope.
3. Keep the implementation parent In Progress and add a "ready for verification/PR" comment. A parent becomes In Review after PR creation and Done only after merge.
4. Set state to `active: false`, `status: "completed"`.
5. Emit the exact marker `<!-- VORBIT_LOOP_COMPLETE -->` once.

The stop hook deletes a completed state only when both the stored status and exact marker agree.

## Terminal States

- `completed` — queue and parent ACs verified; emit the marker.
- `needs_input` — a requirement, queue, or source revision needs a user decision.
- `blocked` — the same failure repeated three times or iteration limit reached.
- `failed` — a non-recoverable tool or state error.
- `canceled` — user canceled; state deleted, code left untouched.

At `maxIterations`, preserve state as blocked and report the current issue and reason. Never delete evidence silently.

## Progress Output

Each cycle reports:

```text
Current: VIB-102 — title
Phase: 1
Acceptance criteria: 3/4 passed
Queue progress: 1/3 complete
Tests: command + result
Status: running | needs_input | blocked | failed | completed
```
