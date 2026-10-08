# Branch Spec Files

Branch-scoped requirement storage for the prd → epic → implement chain. The spec files are the canonical requirements source. Linear carries only the short human-readable summaries posted by the ticket skill.

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
- `explore/YYYY-MM-DD-<topic>.md` (+ `.html` for UI/UX asks) — written by the **explore** skill. Dated research: one approved exploration per file, never overwritten, with its visual solution page and its `-refs/` folder of reference pictures beside it. Unlike the files above, explore files are not tied to one branch: they carry a `Branch:` line for context but never trigger the mismatch stop, and the protected-branch confirm below does not apply to them.
- `qa-screenshots/<YYYY-MM-DD>/` — written by the **qa-report** skill. One picture per check it ran, one folder per run date, embedded in `qa-report.md` by relative path. Other skills never write here. Gitignored with the rest of `.vorbit/`, so the pictures travel only when the user copies the folder.

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
- They do not follow the branch into another worktree. Run the whole chain (prd → epic → ticket → implement → qa-plan → qa-report) inside one worktree.
- If an expected spec file is missing, run `git worktree list` and report which sibling worktree may hold it before doing anything else. Never silently regenerate a missing spec.
- Deleting the worktree deletes its specs. The Linear summaries are the only durable copy, and they are summaries — not the full spec.

## Story Scope and Prerequisites

The PRD's included stories define the implementation scope. Its `Later` section is deferred context, never an executable queue. Each story records `In scope`, `Out of scope`, and `Depends on`; the epic plan preserves these boundaries and lists a `Story Order` with prerequisites first. Older specs may omit these fields: use their explicit requirements and dependency evidence without inventing missing decisions.

Before starting or resuming a spec task or story loop, read the owning story's prerequisites in the epic plan and its source PRD (or the plan's technical baseline when there is no product PRD):

- A prerequisite story must exist in the plan, have all its tasks `done`, and have evidence that its needed outcome works. Check named existing capabilities against the current code or verification evidence as well; a label alone is not proof.
- If a prerequisite is missing, unfinished, cyclic, or unverified, report `needs_input` with the prerequisite and next action before changing code or task status. For an existing loop, preserve its queue and progress, set `active: false` and `status: needs_input`, and stop until the prerequisite is resolved.
- Execute only the selected story's tasks. Do not append tasks from prerequisite stories, excluded work, or Later to its queue. `Story Order` guides selection; each story's own Implementation Order drives execution.

## Identifiers and status

- Stories: `US-###`, defined in `prd.md`, document-unique.
- Tasks: `T1`, `T2`, ... globally unique across one `epic.md`. Never renumber an existing task; new tasks get fresh IDs.
- Every task carries exactly one `**Status:**` line: `pending` | `in-progress` | `done` | `blocked`. The implement and implement-loop skills update this line; nothing else tracks task state.
- `prd.md` may end with a `## Linear Sync` section, written by the ticket skill only: one `US-### → <ticket ID> — <URL> (synced <date>)` line per story. It is the create-vs-update record for syncing; other skills preserve it verbatim and never edit it.
