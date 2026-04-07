---
name: prepare-pr
version: 1.0.0
description: Prepare a feature branch for PR — strip design files, generate PR body, create the pull request, and post design file references to Linear. Use when user says "prepare PR", "create PR", "ready for review", "ship it", "open PR", "submit PR", "PR time", or wants to finalize a feature branch for merge. Also triggers on "strip designs", "clean up for merge", or "ready to merge". Handles both branches with and without design files.
---

# Prepare PR Skill

Finalize a feature branch for merge: run pre-flight checks, strip design files per the management standard, generate a PR body from Linear context and commit history, create the pull request, and post design file recovery references to the Linear ticket.

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
   - Not pushed to remote → Note for Phase 4 (will push before PR creation)

4. **Detect design files:**
   - Does `designs/` directory exist with `.pen` files?
   - If yes → Phase 2 will handle stripping
   - If no → Skip Phase 2

5. **Check mock data (informational):**
   - Does `.claude/mock-registry.json` exist with entries?
   - If yes → Warn: "Mock data detected. Consider running `/cleanup-mocks` first."
   - Don't block — just inform

6. **Suggest review (informational):**
   - "Have you run `/review`? Consider it before creating the PR."
   - Don't block — just inform

**Output**: Branch state confirmed, blockers surfaced

## Phase 2: Design File Handling

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

## Phase 3: PR Body Generation

**Goal**: Generate a complete PR body from Linear context and commit history.

1. **Fetch Linear issue** (if issue-id was found):
   - Call `mcp__linear-server__get_issue` with the issue identifier
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
   [Include the design files reference block from Phase 2]
   [Omit this entire section if no design files were stripped]

   ## Notable decisions
   [Key architectural/UX decisions worth calling out]
   [Omit this section if nothing notable]

   ## Related
   - Closes [{ISSUE-ID}]({linear-issue-url})
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

## Phase 4: Create PR and Post References

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
   - Call `mcp__linear-server__save_comment` on the issue:
     ```
     📐 Design files archived

     Design files were stripped before merge per management standard.

     Commit: {full-hash}
     Recovery:
       git checkout {full-hash} -- {path-to-each-pen-file}

     PR: {pr-url}
     ```
   This comment is the PERMANENT reference. It survives branch deletion, PR archival, and repo history compaction. The design file was already referenced on this ticket when it was created (by canvas-sync) — this comment closes the loop.

4. **Update Linear issue status:**
   - Call `mcp__linear-server__save_issue` with `state: "In Review"`

5. **Report:**
   ```
   PR created: {pr-url}

     Branch:        {branch} → {base}
     Design files:  {count} stripped, recovery hash recorded
     Linear:        {issue-id} → "In Review", design reference posted
   ```

## Flags

- **`--skip-designs`**: Skip Phase 2 even if `designs/` exists. For PRs where design files should remain (e.g., the PR sets up the design file infrastructure itself).
- **`--draft`**: Create as draft PR (`gh pr create --draft`). For early feedback before the feature is complete.
- **`--base {branch}`**: Override base branch detection. Default: `dev` or `main`.

## Anti-Patterns

- Stripping design files without recording the recovery hash first — capture the hash BEFORE `git rm`, because after stripping `git log -- designs/` returns the strip commit, not the one with actual files
- Posting recovery reference to ONLY the PR — Linear ticket must also get it as the permanent record
- Removing `designs/library/` — that's the shared template directory (gitignored), not feature-specific
- Stripping other features' design directories (e.g., `designs/on-500/` when working on `on-329`)
- Creating the PR without showing the body to the user first
- Amending existing commits to strip designs — always create a NEW commit for stripping
- Auto-squashing commits without user consent
- Pushing directly to `main` or `dev`
