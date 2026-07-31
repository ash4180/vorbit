# Branch Spec Files

Branch-scoped requirement storage for the prd → epic → implement chain. The spec files are the canonical requirements source. Linear carries only the short human-readable summaries posted by the linear-sync skill.

## Resolution

Resolve once per run, inside the repository the user is working in (never the Vorbit plugin directory):

1. Root: `git rev-parse --show-toplevel` — the current worktree's root.
2. Branch: `git branch --show-current`.
3. Spec folder: `<root>/.vorbit/` — flat, no branch subfolder. The worktree already belongs to one branch; the branch link lives inside each file (see Branch linkage below).

Files, one owner each:

- `prd.md` — written by the **prd** skill. Canonical requirements: user stories, acceptance criteria, flows, constraints, success criteria.
- `epic.md` — written by the **epic** skill. Technical plan: one section per story, fully specified tasks, implementation order, task status.
- `qa-plan.md` — written by the **qa-plan** skill. Human-runnable test plan: story checks, edge cases, device matrix, regression, performance, plus automated E2E runs when the project has a runner. Whoever tests ticks the boxes and adds `**Fail:**` notes; the qa-report skill may also update check states, but only after a real observed run (automated command or agent-run browser check) — never by guessing.
- `qa-report.md` — written by the **qa-report** skill. Dated run history, newest run first, with a ready/not-ready verdict; old run sections are never rewritten. Other skills never edit it, and its content never goes to Linear.

## Guards (before any spec write)

- Empty branch output (detached HEAD): stop and ask the user to create or switch to a feature branch.
- Branch is `main`, `master`, `dev`, `develop`, or `demo`: warn that specs are branch-scoped working documents and confirm before writing.
- Ensure `<root>/.gitignore` contains a `.vorbit/` line; append it when missing and report the append in the session. Leave the `.gitignore` change uncommitted for the user.

## Branch linkage

- Every spec file records its branch in a `Branch:` line near the top (`prd.md` directly under the H1; the other files in their headers).
- Before reading or writing specs, compare each file's `Branch:` line with the current branch. A mismatch means the folder holds another branch's leftovers (possible in a shared checkout after a branch switch): stop and ask before touching them.
- Branch renamed? Update the `Branch:` lines and report it. No folders move — that is the point of keeping the path flat.

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
