---
name: prepare-pr
version: 1.0.0
description: Prepare a feature branch for PR — strip design files, generate PR body, create the pull request, and post design file references to Linear. Use when user says "prepare PR", "create PR", "ready for review", "ship it", "open PR", "submit PR", "PR time", or wants to finalize a feature branch for merge. Also triggers on "strip designs", "clean up for merge", or "ready to merge". Handles both branches with and without design files.
---

# Prepare PR Skill

Finalize a feature branch for merge: run pre-flight checks, strip design files per the management standard, generate a PR body from Linear context and commit history, create the pull request, and post design file recovery references to the Linear ticket.

> **MCP namespace**: This skill optionally uses `mcp__plugin_linear_linear__*` for Linear integration (skipped when no issue ID is detected). See `_shared/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Why This Skill Exists

Design files (`.pen`) live on feature branches during development so teammates can review them. But they must never reach `dev`, `main`, or `demo` — a CI gate (`design-files-check`) blocks PRs that contain `designs/`. This skill automates the stripping, records the recovery hash (the only way to get designs back after branch deletion), and posts references to both the PR and Linear ticket so the design is never lost.

For branches without design files, the skill still handles PR body generation and Linear integration.

## Phase 1: Pre-flight Checks

**Goal**: Verify the branch is ready for PR creation.

1. **Get current branch and determine base:**
   ```bash
   git branch --show-current
   ```
   - Base branch: `dev` if it exists, otherwise `main`
   - **Guard**: If on `main`, `dev`, or `demo` → "You're on a protected branch. Switch to a feature branch first." → **STOP**

2. **Extract issue-id** from branch name — first match of `[a-zA-Z]+-\d+` (case-insensitive):
   - `feature/on-329-ux-improvement` → `ON-329`
   - `fix/tl-42-broken-auth` → `TL-42`
   - No match → **Use AskUserQuestion**: ask for the Linear issue ID, or skip Linear integration

3. **Check git state:**
   - Uncommitted changes → Warn: "You have uncommitted changes. Commit or stash before continuing?"
   - Not pushed to remote → Note for Phase 5 (will push before PR creation)

4. **Detect design files:**
   - Does `designs/` directory exist with `.pen` files?
   - If yes → Phase 3 will handle stripping
   - If no → Skip Phase 3

5. **Check mock data (informational):**
   - Does `.claude/mock-registry.json` exist with entries?
   - If yes → Warn: "Mock data detected. Consider running `/cleanup-mocks` first."
   - Don't block — just inform

6. **Suggest review (informational):**
   - "Have you run `/review`? Consider it before creating the PR."
   - Don't block — just inform

**Output**: Branch state confirmed, blockers surfaced

## Phase 2: Sync with Base

**Goal**: Catch merge conflicts on your machine instead of discovering them in the GitHub PR review. Rebase onto the latest base when clean; walk the user through fixing them when not.

**Skip this phase if `--skip-rebase` flag is set.**

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

5. **Assisted conflict resolution.** The rebase halts at the first conflicting commit. Walk the user through each conflict — never auto-pick a side.

   a. **List conflicted files:**
      ```bash
      git diff --name-only --diff-filter=U
      ```

   b. **For each conflicted file**, read it to find conflict blocks (markers `<<<<<<<`, `=======`, `>>>>>>>`). For each block, show the user using AskUserQuestion:
      ```
      File: {path}, lines {start}-{end}

      From {base-branch}:
        {their version}

      Your branch:
        {your version}

      Pick a resolution:
        1. Keep base version
        2. Keep my version
        3. Keep both (base first, then mine)
        4. Let me edit this file manually
        5. Show more context (5 lines above and below)
      ```

   c. **Apply the choice:**
      - Options 1–3 → Edit the file in place: remove the markers and write the chosen content.
      - Option 4 → Stop and tell the user: "Edit `{file}`, remove all `<<<<<<<` / `=======` / `>>>>>>>` markers, then say 'continue'." When they reply, run `git diff --check`. If markers remain, ask them to finish. If clean, proceed.
      - Option 5 → Re-show the block with more surrounding lines, then re-ask.

   d. **Stage the resolved file:**
      ```bash
      git add {file}
      ```

   e. **After all files in the current commit are resolved**, continue the rebase:
      ```bash
      git rebase --continue
      ```
      - **Exit 0** → all commits applied. Continue to step 7.
      - **Halts again with more conflicts** → repeat from step 5a.

6. **Abort path.** At any point during step 5, if the user says "abort", "stop", or "cancel":
   ```bash
   git rebase --abort
   ```
   Branch returns to its pre-rebase state. Stop the entire skill: "Rebase aborted. Branch unchanged. PR not created."

7. **Push the rebased branch:**
   ```bash
   git push --force-with-lease
   ```
   `--force-with-lease` refuses to push if someone else updated the remote branch since the last fetch — prevents wiping a teammate's work. Never use plain `--force`.

8. **Report:**
   ```
   Synced with {base-branch}:
     {N} commits applied
     {M} conflicts resolved (if any)
   ```

**Output**: Branch is up to date with base, ready for design stripping and PR creation.

## Phase 3: Design File Handling

**Skip this phase if no `designs/` directory exists, or if `--skip-designs` flag is set.**

**Goal**: Strip design files and record the recovery reference. The recovery hash is captured BEFORE stripping because it points to the last commit where the files still exist — this is the only way to recover them later.

1. **Record the recovery hash** — this MUST happen before any `git rm`:
   ```bash
   git log -1 --format="%H" -- designs/
   ```
   Store this hash. It points to the last commit where design files exist.

2. **Inventory design files** being stripped:
   ```bash
   find designs/ -name "*.pen" -type f
   ```
   Record the full paths (e.g., `designs/on-329/scheduling.pen`).

3. **Strip design files:**
   ```bash
   git rm -r designs/{issue-id}/
   ```
   Only remove the issue-specific directory. If other issue directories exist under `designs/`, leave them — they belong to other features.

4. **Commit the stripping** — this is a mechanical commit, do NOT add `Co-Authored-By` or any AI attribution:
   ```bash
   git commit -m "chore: strip design files before merge"
   ```

5. **Build the design files reference block** for use in the PR body:
   ```markdown
   ## Design files
   Design files were stripped before merge per the [management standard](https://www.notion.so/vibranium-labs/Pencil-Design-Files-in-Git-Management-Standard-313477245840818dbf27dcc2d6774bde).
   To view them:
   ```
   git checkout {full-hash} -- {path-to-each-pen-file}
   ```
   ```
   If multiple `.pen` files, list each recovery command on its own line.

**Output**: Design files stripped, recovery reference prepared

## Phase 4: PR Body Generation

**Goal**: Generate a complete PR body from Linear context and commit history.

1. **Fetch Linear issue** (if issue-id was found):
   - Call `mcp__plugin_linear_linear__get_issue` with the issue identifier
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
   - [{ISSUE-ID}]({linear-issue-url})
   - Parent epic: [{epic-id}]({epic-url}) {epic title} if applicable

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

5. **Present for review — Use AskUserQuestion:**
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

2. **Create the PR** — use the approved body exactly as the user approved it. Do NOT append `🤖 Generated with Claude Code` or `Co-Authored-By` footers:
   ```bash
   gh pr create --base {base-branch} --title "{title}" --body "$(cat <<'EOF'
   {approved body}
   EOF
   )"
   ```

3. **Post design recovery reference to Linear** (if design files were stripped):
   - Call `mcp__plugin_linear_linear__save_comment` on the issue:
     ```
     📐 Design files archived

     Design files were stripped before merge per management standard.

     Commit: {full-hash}
     Recovery:
       git checkout {full-hash} -- {path-to-each-pen-file}

     PR: {pr-url}
     ```
   This comment is the PERMANENT reference. It survives branch deletion, PR archival, and repo history compaction. The design file was already referenced on this ticket when it was created by Pencil — this comment closes the loop.

4. **Update Linear issue status:**
   - Call `mcp__plugin_linear_linear__save_issue` with `state: "In Review"`

5. **Report:**
   ```
   PR created: {pr-url}

     Branch:        {branch} → {base}
     Design files:  {count} stripped, recovery hash recorded
     Linear:        {issue-id} → "In Review", design reference posted
   ```

## Flags

- **`--skip-rebase`**: Skip Phase 2. Use when the team's workflow does conflict resolution at merge time (squash-and-merge), or when you intentionally want the reviewer to see the conflicts in GitHub.
- **`--skip-designs`**: Skip Phase 3 even if `designs/` exists. For PRs where design files should remain (e.g., the PR sets up the design file infrastructure itself).
- **`--draft`**: Create as draft PR (`gh pr create --draft`). For early feedback before the feature is complete.
- **`--base {branch}`**: Override base branch detection. Default: `dev` or `main`.

## Anti-Patterns

- Using plain `git push --force` instead of `--force-with-lease` after a rebase — plain force will silently overwrite a teammate's work if they pushed to the same branch since your last fetch
- Auto-resolving conflicts by always picking one side (e.g., "ours" or "theirs") — file-by-file user choice is the only safe path; auto-picks routinely lose intent
- Auto-stashing uncommitted changes to make the rebase possible — that hides in-progress work and risks losing it. Always require a clean tree first
- Continuing the skill after a rebase abort — when the user aborts, stop. They likely need to think before pushing
- Skipping the rebase phase silently when there are conflicts — only skip when `--skip-rebase` is explicitly passed, never as a "fall-through" fallback
- Stripping design files without recording the recovery hash first — capture the hash BEFORE `git rm`, because after stripping `git log -- designs/` returns the strip commit, not the one with actual files
- Posting recovery reference to ONLY the PR — Linear ticket must also get it as the permanent record
- Removing `designs/library/` — that's the shared template directory (gitignored), not feature-specific
- Stripping other features' design directories (e.g., `designs/on-500/` when working on `on-329`)
- Creating the PR without showing the body to the user first
- Amending existing commits to strip designs — always create a NEW commit for stripping
- Auto-squashing commits without user consent
- Pushing directly to `main` or `dev`
