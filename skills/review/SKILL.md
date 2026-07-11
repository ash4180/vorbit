---
name: review
description: Use when the user asks for a read-only review of files, a branch diff, or a pull request, including pre-merge checks and code-review commands. It reports severity-ranked findings first and edits code only after separate user approval. Do not use as the implementation workflow, as acceptance-criteria verification, or for a generic request to explain code.
---

# Code Review Skill

Findings-first code review with two modes:
- **File mode** — review specific files/directories
- **PR mode** — 3-layer pipeline: static analysis → blast radius → parallel AI agents

Read and follow `../_shared/execution-contract.md` before starting.

## References

Detailed pipeline specs live in `references/` within this skill's directory. Glob for `**/skills/review/references/` to resolve the path.

| File | Contains |
|---|---|
| `references/pr-pipeline.md` | 3-layer pipeline: static analysis commands, blast radius patterns, agent dispatch table, report template |

---

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Read `.claude/review-rules.md` if it exists — learnable rules from previous reviews
3. Determine mode from input (see Mode Detection)

---

## Mode Detection

1. **`--pr` flag present** → PR Review Mode (strip the flag, remaining arg is base branch)
2. **Arguments are file/directory paths** → File Review Mode
3. **No arguments** → PR Review Mode (default base: main)

To detect without flag: if any argument matches an existing file or directory path, use File Review Mode. Otherwise, treat arguments as a base branch name for PR Review Mode.

---

## Review Voice

- Be direct, specific, and professional.
- State what is broken, why it matters, and the smallest correct fix.
- Do not perform a persona, insult the author, or pad findings with attitude.
- Do not report stylistic preferences as defects unless repository policy requires them.

---

## FILE REVIEW MODE

### Phase 1: ANALYZE (No edits)

1. **Read the files** specified in arguments
2. **Apply CLAUDE.md standards ruthlessly**
3. **Audit for:**
   - **Over-engineering**: Factories for single classes, excessive interfaces, abstractions with single implementations, "future-proofing" (YAGNI)
   - **Dead Code**: Functions never called, commented-out code "just in case"
   - **Complexity**: 3+ levels of indentation, "clever" one-liners that are unreadable
   - **Naming**: Vague names like `Manager`, `Processor`
   - **Mocks**: Mock services where real ones work
4. **Present findings by severity, with concrete evidence**
5. **For each issue**: WHAT is wrong, WHY it matters, HOW to fix

**Report Format:**
```
## file.ts - 2 issues

### Line 42: Over-engineered abstraction
WHAT: `DataProcessorFactory` returns exactly one type.
WHY: Complexity for zero benefit.
HOW: Delete the factory. Instantiate directly.

### Line 89: Dead code
WHAT: `legacyHandler()` is never called.
HOW: Delete it. Git has history.
```

End with: **"Say 'fix it' to apply changes, or tell me what you disagree with."**

---

## PR REVIEW MODE

### Step 1: Determine Diff Scope

1. Detect base branch: `git merge-base HEAD main` (or use argument if a branch name is provided)
2. Get committed diff: `git diff <base>..HEAD`
3. Get changed file list: `git diff --name-only <base>..HEAD`
4. **If no committed changes**: fall back to uncommitted changes with `git diff` (staged + unstaged) and `git diff --name-only`
5. **If STILL no changes** → output "No changes detected (committed or uncommitted)." → **STOP**

### Steps 2–5: Run the 3-Layer Pipeline

Read the pipeline spec (glob for `**/skills/review/references/pr-pipeline.md`) and execute all three layers in order:
1. **Layer 1: Static Analysis** — run linters/type checkers for changed file types
2. **Layer 2: Blast Radius** — find importers of changed files, read all into context
3. **Layer 3: AI Review** — run 4 independent focus passes, parallel only up to the host's safe concurrency limit, and collect results

Then print the consolidated report using the template from the pipeline spec.

End with: **"Say 'fix it' to apply changes, or tell me what you disagree with."**

---

## Phase 2: FIX (Both modes, after user approval)

**Only proceed when user says "fix it" / "approved" / "go ahead":**

1. Use Edit tool to fix code directly (NO COMMENTS)
2. Delete the garbage
3. Simplify the logic
4. Rename variables for clarity
5. Report what was fixed

**Summary Format:**
```
Done. Fixed X files:
- Deleted Y lines of garbage
- Fixed Z issues
- Renamed W functions

Run `/vorbit:implement:verify` when ready.
```

---

## Error Handling

- **No file arguments and not a git repo** → "Not a git repository and no files specified." Stop.
- **Linter not installed** → skip, note "Skipped (not installed)"
- **Agent fails/times out** → note in that section, continue with remaining agents
- **Blast radius > 30 files** → cap at 30 total (all changed files + up to 20 importers), note excluded importers in the report
- **No `.claude/review-rules.md`** → "No review rules file yet" (normal for first run)
