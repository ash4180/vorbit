---
name: review
description: Use when the user asks for a read-only review of files, a branch diff, or a pull request, including pre-merge quality checks and code-review commands. It reports severity-ranked findings first and edits code only after separate user approval. Do not use as the implementation workflow, for acceptance-criteria verification, for branch finalization or PR creation (that is prepare-pr), or for a generic request to explain code.
---

# Code Review Skill

Findings-first code review with two modes:
- **File mode** — review specific files/directories
- **PR mode** — 3-layer pipeline: static analysis → blast radius → parallel AI agents

Read and follow `../_shared/execution-contract.md` before starting.

Read `../_shared/pre-existing-findings.md` for how to tag, report, and follow up findings this branch did not cause. Pre-existing findings never count toward merge risk.

## References

Detailed pipeline specs live in `references/` within this skill's directory. Glob for `**/skills/review/references/` to resolve the path.

| File | Contains |
|---|---|
| `references/pr-pipeline.md` | 3-layer pipeline: static analysis commands, blast radius patterns, agent dispatch table, report template |

---

## Setup

1. Honor the project's standing instructions files if the runtime has not already loaded them
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

- Do not report stylistic preferences as defects unless repository policy requires them.

---

## FILE REVIEW MODE

### Phase 1: ANALYZE (No edits)

1. **Read the files** specified in arguments
2. **Apply the repository's instruction files** (CLAUDE.md, AGENTS.md, rule files) as the standard
3. **Audit for:**
   - **Over-engineering**: Factories for single classes, excessive interfaces, abstractions with single implementations, "future-proofing" (YAGNI)
   - **Dead Code**: Functions never called, commented-out code "just in case"
   - **Complexity**: 3+ levels of indentation, "clever" one-liners that are unreadable
   - **Naming**: Vague names like `Manager`, `Processor`
   - **Mocks**: Mock services where real ones work
4. **Tag each finding** `from this branch` or `pre-existing` per `../_shared/pre-existing-findings.md` Step 1 (in file mode, "this branch" means the branch diff against main; with no diff, every finding is in scope and none is pre-existing)
5. **Present findings by severity, with concrete evidence**; pre-existing ones go in their own `Pre-existing (follow-up)` section at the end
6. **For each issue**: WHAT is wrong, WHY it matters, HOW to fix

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

## Pre-existing (follow-up)

### utils.ts:12: Date parsing ignores timezone
WHAT: `parseDate()` drops the offset.
EVIDENCE: lines unchanged on this branch, last touched in commit a1b2c3d on main.
Linear: nothing found. Slack: not connected.
```

End with: **"Say 'fix it' to apply changes, or tell me what you disagree with."** Then, when pre-existing findings exist, ask the one batched ticket question per `../_shared/pre-existing-findings.md` Step 4.

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
4. **Tag findings** — the orchestrator tags each verified finding `from this branch` or `pre-existing` per `../_shared/pre-existing-findings.md` Step 1, then runs its Step 3 (Linear and Slack search) for the pre-existing ones

Then print the consolidated report using the template from the pipeline spec.

End with: **"Say 'fix it' to apply changes, or tell me what you disagree with."** Then, when pre-existing findings exist, ask the one batched ticket question per `../_shared/pre-existing-findings.md` Step 4.

---

## Phase 2: FIX (Both modes, after user approval)

Only proceed when the user says "fix it" / "approved" / "go ahead".
Apply the approved fixes directly, re-run the relevant checks, and report what was fixed. Pre-existing findings are not fixed here unless the user names them; they stay follow-ups.

**Summary Format:**
```
Done. Fixed X issues across Y files.

Run `/vorbit:implement:qa-plan` when ready.
```

---

## Error Handling

- **No file arguments and not a git repo** → "Not a git repository and no files specified." Stop.
- **Linter not installed** → skip, note "Skipped (not installed)"
- **Agent fails/times out** → note in that section, continue with remaining agents
- **Blast radius > 30 files** → cap at 30 total (all changed files + up to 20 importers), note excluded importers in the report
- **No `.claude/review-rules.md`** → "No review rules file yet" (normal for first run)
