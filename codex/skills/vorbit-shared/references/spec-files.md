# Branch Spec Files

Branch-scoped requirement storage for the prd → epic → implement chain. The spec files are the canonical requirements source. Linear carries only the short human-readable summaries posted by the linear-sync skill.

## Resolution

Resolve once per run, inside the repository the user is working in (never the Vorbit plugin directory):

1. Root: `git rev-parse --show-toplevel` — the current worktree's root.
2. Branch: `git branch --show-current`.
3. Slug: the branch name with every `/` replaced by `-` (`feature/vib-12-login` → `feature-vib-12-login`).
4. Spec folder: `<root>/.vorbit/specs/<slug>/`.

Files, one owner each:

- `prd.md` — written by the **prd** skill. Canonical requirements: user stories, acceptance criteria, flows, constraints, success criteria.
- `epic.md` — written by the **epic** skill. Technical plan: one section per story, fully specified tasks, implementation order, task status.
- `qa-plan.md` — written by the **qa-plan** skill. Human-runnable test plan: story checks, edge cases, device matrix, regression, performance. Whoever tests ticks the boxes and adds `**Fail:**` notes; skills never untick them.

## Guards (before any spec write)

- Empty branch output (detached HEAD): stop and ask the user to create or switch to a feature branch.
- Branch is `main`, `master`, `dev`, `develop`, or `demo`: warn that specs are branch-scoped working documents and confirm before writing.
- Ensure `<root>/.gitignore` contains a `.vorbit/` line; append it when missing and report the append in the session. Leave the `.gitignore` change uncommitted for the user.

## Worktree scope (accepted trade-off)

Spec files live in the worktree where they were written, and they are gitignored:

- They never appear in commits, PRs, or clones on other machines.
- They do not follow the branch into another worktree. Run the whole chain (prd → epic → linear-sync → implement → verify) inside one worktree.
- If an expected spec file is missing, run `git worktree list` and report which sibling worktree may hold it before doing anything else. Never silently regenerate a missing spec.
- Deleting the worktree deletes its specs. The Linear summaries are the only durable copy, and they are summaries — not the full spec.

## Identifiers and status

- Stories: `US-###`, defined in `prd.md`, document-unique.
- Tasks: `T1`, `T2`, ... globally unique across one `epic.md`. Never renumber an existing task; new tasks get fresh IDs.
- Every task carries exactly one `**Status:**` line: `pending` | `in-progress` | `done` | `blocked`. The implement and implement-loop skills update this line; nothing else tracks task state.
- `prd.md` may end with a `## Linear Sync` section, written by the linear-sync skill only: one `US-### → <ticket ID> — <URL> (synced <date>)` line per story. It is the create-vs-update record for syncing; other skills preserve it verbatim and never edit it.
