# Vorbit Implement Loop Workflow

Use for autonomous iteration through sub-issues until completion.

1. Load the Vorbit runtime contract and durable rules. Require an explicit Linear issue plus loop/auto-continue intent.
2. Resolve runtime storage from `vorbit-resolve-rules` and use `<storage-root>/state/<project-slug>/gemini-implement-loop.json`; do not write Claude-specific state into the repository.
3. For cancel: read and report state, optionally add a Linear cancellation comment, delete runtime state, and leave code untouched.
4. For resume: never overwrite an existing state. Re-fetch the parent. If its source update timestamp changed, persist `active: false`, `status: needs_input`, and the reason. An inactive `needs_input`, `blocked`, or `failed` state resumes only after the user supplies or confirms the missing resolution; then reconcile, update the baseline, clear failure tracking, reset `iteration` to 1, and set it back to `active: true`, `status: running`.
5. For a new queue, parse each parent's `## Implementation Order` by phase. Within a phase sort by priority then creation time; skip terminal issues; accept a flat list as sequential. Append missing sub-issues as an `unplanned` final phase. If no order exists, build a labeled fallback guess. If a parent has no sub-issues at all, the parent itself is the queue's single executable item.
6. A Parallel label expresses dependency independence, not permission for concurrent writers. Use isolated worktrees only with explicit approval; otherwise process deterministically.
7. Show the multi-issue queue once and confirm Start/Reorder/Cancel before persisting. A single issue explicitly started in loop mode begins directly.
8. Persist version, active/status, source timestamp, queue entries with phase, current index, completed IDs, iteration/max (50), and repeated-failure fingerprint/count. Write state atomically.
9. For each item, apply the normal implement workflow to that item only: search/reuse, mapped ACs/flows, honest focused test, implementation, regression checks. Move to In Progress and comment when starting.
10. Mark a sub-issue Done only after its ACs and tests pass; record evidence, advance state, and continue. Keep the implementation parent In Progress until a PR exists.
11. If the same failure fingerprint repeats three cycles, or 50 iterations are reached, persist `active: false`, `status: blocked`, and the reason, then stop for input. Do not retry blindly.
12. After the queue, verify parent ACs. If covered, comment "ready for verification/PR", mark runtime state completed, and delete it. Otherwise persist `active: false`, `status: needs_input`, and the missing ACs rather than inventing work.
13. Report `completed`, `needs_input`, `blocked`, `failed`, or `canceled`, with current issue, AC evidence, tests, queue progress, and next action.
