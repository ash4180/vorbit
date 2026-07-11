<!-- GENERATED from skills/prepare-pr/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Prepare PR Skill

Finalize a feature branch for merge: run pre-flight checks, strip design files per the management standard, generate a PR body from Linear context and commit history, create the pull request, and post design file recovery references to the Linear ticket.

Read and follow `../references/execution-contract.md` before starting.

## Why This Skill Exists

Design files (`.pen`) live on feature branches during development so teammates can review them. But they must never reach `dev`, `main`, or `demo` — a CI gate (`design-files-check`) blocks PRs that contain `designs/`. This skill removes the approved files and records the exact pre-removal commit. Recovery remains subject to the repository's commit-retention policy; a hash alone is not a permanent archive.

For branches without design files, the skill still handles PR body generation and Linear integration.

## Phase 1: Pre-flight Checks

**Goal**: Verify the branch is ready for PR creation.

1. **Get current branch and determine base:**
   - Base branch: `dev` if it exists, otherwise `main`
   - **Guard**: If on `main`, `dev`, or `demo` → "You're on a protected branch. Switch to a feature branch first." → **STOP**

2. **Extract issue-id** from branch name — first match of `[a-zA-Z]+-\d+` (case-insensitive):
   - `feature/on-329-ux-improvement` → `ON-329`
   - `fix/tl-42-broken-auth` → `TL-42`
   - No match → **Use plain-text chat questions**: ask for the Linear issue ID, or skip Linear integration

3. **Check git and publication capabilities before any mutation:**
   - Require a clean working tree. If not clean, stop; never discard work.
   - Verify `origin` and the selected base exist.
   - Verify `gh` is installed and authenticated (`gh auth status`). If not, stop before rebase, deletion, or commit.
   - If Linear integration is selected, verify its read/update/comment operations now. A missing optional Linear connection may be skipped only with user approval.
   - Note whether the branch has an upstream; Phase 5 performs the push.

4. **Detect design files:**
   - Does `designs/` directory exist with `.pen` files?
   - If yes → Phase 3 will handle stripping
   - If no → Skip Phase 3

5. **Check mock data (informational):**
   - Does the resolved project mock registry (fallback `.vorbit/mock-registry.json`) contain entries?
   - If yes → Warn: "Mock data detected. Consider running `/cleanup-mocks` first."
   - Don't block — just inform

6. **Redundant comment gate (hard block):**
   - Get the diff scope: `git diff {base-branch}...HEAD --name-only -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.py' '*.go'`
   - If the file list is empty → skip this step.
   - Use `pr-review-toolkit:comment-analyzer` when available; otherwise inspect only comment lines added or modified by the diff locally. Do not fail merely because that named agent is absent.
   - Use this prompt:
     ```
     Review comments added or modified in these files: {file list}.

     Redundancy rule: a comment is redundant unless it explains a non-obvious WHY — a hidden constraint, subtle invariant, workaround for a specific bug, or behavior that would surprise a reader. Comments that restate WHAT the code does, reference the current task/PR/issue, or could be removed without confusing a future reader are redundant.

     Output a per-file list: `path:line — one-line reason`. Findings only, no remediation suggestions.
     ```
   - **No findings → continue to step 7.**
   - **Findings present → block via plain-text chat questions:**
     ```
     Redundant comments found in {N} files:
       {file:line — reason}
       ...

     1. Strip all listed comments now (skill removes the lines, commits `chore: strip redundant comments`)
     2. I'll clean up manually — stop the skill, I'll re-run after
     3. Show the full agent report
     ```
   - **Option 1** → Edit each listed file, remove only the lines the agent flagged, then `git commit -m "chore: strip redundant comments"` (no AI attribution). Re-run the agent once to confirm clean; if findings remain, re-ask. Continue when clean.
   - **Option 2** → **STOP**: "Skill stopped. Clean up the listed comments and re-run `/prepare-pr`."
   - **Option 3** → Print the full report, then re-ask.

7. **Release evidence gate:**
   - Run the repository's focused checks and smallest relevant regression suite, or verify equivalent successful evidence from the current task.
   - If checks fail or blocking review findings remain, stop. Preparing a PR is not a way to bypass verification.

8. **Show one mutation preview and get approval:**
   - Base and rebase strategy
   - Whether a force-with-lease push may be needed
   - Exact design files/directories proposed for removal
   - Planned mechanical commits
   - GitHub PR and optional Linear mutations
   - Do not begin Phase 2 until the user approves this plan.

**Output**: Capabilities verified, branch clean, checks passing, and mutation plan approved

## Phase 2: Sync with Base

**Goal**: Catch merge conflicts on your machine instead of discovering them in the GitHub PR review. Rebase onto the latest base when clean; walk the user through fixing them when not.

**Skip this phase only if the `--skip-rebase` flag is explicitly set — never as a fallback when conflicts appear.**

1. **Require a clean working tree.** Rebase cannot run with uncommitted changes. If `git status --porcelain` shows any output, stop: "You have uncommitted changes. Commit or stash, then run again." Do NOT auto-stash — that hides the user's in-progress work.

2. **Fetch the latest base:**
   ```bash
   git fetch origin {base-branch}
   ```

3. **Check if behind:**
   ```bash
   git rev-list --count HEAD..origin/{base-branch}
   ```
   - **Returns 0** → already up to date. Report "Already synced with {base-branch}." Skip the rest of this phase.
   - **Returns N > 0** → continue to step 4.

4. **Attempt the rebase:**
   ```bash
   git rebase origin/{base-branch}
   ```
   - **Exit 0 (clean rebase)** → skip to step 7.
   - **Non-zero exit (conflicts)** → continue to step 5.

5. **Assisted conflict resolution.** The rebase halts at the first conflicting commit. List the conflicted files (`git diff --name-only --diff-filter=U`), show them to the user, and ask how to proceed: resolve here with the user choosing the resolution for each conflict, or abort. Never auto-resolve or auto-pick a side ("ours"/"theirs"). Apply each resolution per the user's direction, verify no conflict markers remain (`git diff --check`), `git add` the resolved files, then `git rebase --continue`; if it halts again with more conflicts, repeat.

6. **Abort path.** At any point during step 5, if the user says "abort", "stop", or "cancel", run `git rebase --abort` — the branch returns to its pre-rebase state. Stop the entire skill: "Rebase aborted. Branch unchanged. PR not created."

7. **Record whether history changed.** Do not push yet; Phase 5 pushes only after the PR title/body are approved. If a previously pushed branch was rebased, Phase 5 must use `--force-with-lease`, never plain `--force`. Never auto-squash commits without user consent.

8. **Report:**
   ```
   Synced with {base-branch}:
     {N} commits applied
     {M} conflicts resolved (if any)
   ```

**Output**: Local branch is up to date with base; push is deferred until final approval.

## Phase 3: Design File Handling

**Skip this phase if no `designs/` directory exists, or if `--skip-designs` flag is set.**

**Goal**: Remove only the approved tracked design files and record a verified pre-removal reference.

1. **Record the pre-removal hash** — this MUST happen before any `git rm`:
   ```bash
   git rev-parse HEAD
   ```
   Store this hash. Because the tree is clean, it contains the exact tracked files being reviewed.

2. **Inventory the exact tracked files** in the issue-specific directory:
   ```bash
   git ls-files "designs/{issue-id}/"
   ```
   Resolve the actual directory name from tracked paths; do not assume case. If multiple directories match the issue, stop and ask. Re-show the list if it differs from the approved preview.

3. **Verify recovery for every file:**
   ```bash
   git cat-file -e "{full-hash}:{path}"
   ```
   If any file cannot be read from that commit, stop before deletion.

4. **Strip the approved issue directory:**
   ```bash
   git rm -r designs/{issue-id}/
   ```
   Only remove the issue-specific directory. If other issue directories exist under `designs/`, leave them — they belong to other features. Never remove `designs/library/` — that's the shared template directory (gitignored), not feature-specific.

5. **Commit the stripping** as a NEW commit — never amend an existing commit. This is a mechanical commit, do NOT add `Co-Authored-By` or any AI attribution:
   ```bash
   git commit -m "chore: strip design files before merge"
   ```

6. **Build the design files reference block** for use in the PR body:
   ```markdown
   ## Design files
   Design files were stripped before merge per the [management standard](https://www.notion.so/vibranium-labs/Pencil-Design-Files-in-Git-Management-Standard-313477245840818dbf27dcc2d6774bde).
   To view them:
   ```
   git checkout {full-hash} -- {path-to-each-pen-file}
   ```
   ```
   List each recovery command on its own line and state that recovery depends on commit retention.

**Output**: Design files stripped, recovery reference prepared

## Phase 4: PR Body Generation

**Goal**: Generate a complete PR body from Linear context and commit history.

1. **Fetch Linear issue** (if issue-id was found):
   - Call the Linear connector's `get_issue` with the issue identifier (resolve the connector per your connector preflight; inspect its current schema)
   - Extract: title, description, acceptance criteria, labels, parent issue, **url**
   - The issue response includes a `url` field — use it for the "Related" section links
   - If issue has a parent → fetch the parent too for its url and title

2. **Analyze commit history** on this branch:
   ```bash
   git log {base-branch}...HEAD --format="%h %s" --no-merges
   ```
   Read ALL commits to understand the full scope of work. Group by type (feat, fix, refactor, chore). Ignore the "strip design files" commit — it's mechanical.

3. **Generate PR body** using this template:

   ```markdown
   ## Summary
   - [2-5 bullet points summarizing what was built/changed]

   ## Design files
   [Include the design files reference block from Phase 3]
   [Omit this entire section if no design files were stripped]

   ## Notable decisions
   [Key architectural/UX decisions worth calling out]
   [Omit this section if nothing notable]

   ## Related
   - Issue: [{issue-id}]({linear-issue-url})
   [- Parent epic: [{epic-id}]({epic-url}) {epic title} if applicable]

   ## Test plan
   - [ ] [AC 1 from Linear issue]
   - [ ] [AC 2]
   - [ ] ...
   [If no ACs found, ask user for test plan items]
   ```

4. **Generate PR title:**
   - Format: `{type}: {Linear issue title} ({issue-id})`
   - Type from labels or commit prefixes (feat/fix/refactor)
   - Keep under 70 characters

5. **Present for review — Use plain-text chat questions:**
   ```
   PR ready for review:

   Title: {title}

   Body:
   {body}

   Base: {base-branch}

   Edit anything? Or say "go" to create.
   ```
   The user can modify the title, body, add Jam links, screenshots, or approve as-is.

**Output**: Approved PR title and body

## Phase 5: Create PR and Post References

**Goal**: Push, create the PR, and post references.

1. **Push branch** (if not already pushed or has new commits):
   ```bash
   git push -u origin {branch-name}
   ```
   If Phase 2 rebased an already-published branch, use `git push --force-with-lease` instead. Never use plain `--force` — it silently overwrites a teammate's work if they pushed to the branch since your last fetch. Never push directly to `main` or `dev`.

2. **Create the PR** — use the approved body exactly as the user approved it. Do NOT append `🤖 Generated with Claude Code` or `Co-Authored-By` footers:
   ```bash
   gh pr create --base {base-branch} --title "{title}" --body "$(cat <<'EOF'
   {approved body}
   EOF
   )"
   ```

3. **Post design recovery reference to Linear** only if design files were stripped and Linear integration was selected, resolved to an issue, and approved. Otherwise keep the recovery block in the PR and report that the Linear comment was skipped.
   - Call the Linear connector's comment-creation operation (inspect the connector schema for the current comment-creation verb) on the issue:
     ```
     📐 Design files archived

     Design files were stripped before merge per management standard.

     Commit: {full-hash}
     Recovery:
       git checkout {full-hash} -- {path-to-each-pen-file}

     PR: {pr-url}
     ```
   This comment records how to recover the files while the referenced commit remains retained. It is not a backup; if permanent retention is required, archive the design in the team's approved design storage before stripping.

4. **Update Linear issue status** only when Linear integration was selected, resolved, and approved:
   - Call the Linear connector's issue-update operation (inspect the connector schema for the current issue-update verb) with `state: "In Review"`

5. **Report:**
   ```
   PR created: {pr-url}

     Branch:        {branch} → {base}
     Design files:  {count} stripped, recovery hash recorded
     Linear:        {issue-id} → "In Review", design reference posted | skipped with reason
   ```

## Flags

- **`--skip-rebase`**: Skip Phase 2. Use when the team's workflow does conflict resolution at merge time (squash-and-merge), or when you intentionally want the reviewer to see the conflicts in GitHub.
- **`--skip-designs`**: Skip Phase 3 even if `designs/` exists. For PRs where design files should remain (e.g., the PR sets up the design file infrastructure itself).
- **`--draft`**: Create as draft PR (`gh pr create --draft`). For early feedback before the feature is complete.
- **`--base {branch}`**: Override base branch detection. Default: `dev` or `main`.
