# PR Review Pipeline — 3-Layer Architecture

Inspired by [CodeRabbit](https://coderabbit.ai). Each layer feeds into the next.

---

## Layer 1: Static Analysis

Run linters/type checkers **only for languages present in changed files**. Skip gracefully if a tool isn't installed.

### Detect package manager (JS/TS projects only)

Check for lock files in the project root to determine the runner:

| Lock file | Package manager | Runner |
|-----------|----------------|--------|
| `bun.lockb` or `bun.lock` | bun | `bunx` |
| `pnpm-lock.yaml` | pnpm | `pnpm exec` |
| `yarn.lock` | yarn | `yarn` |
| `package-lock.json` | npm | `npx` |
| none found | fallback | `npx` |

Use `$RUNNER` to refer to the detected runner in commands below.

### TypeScript/JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`)

```bash
$RUNNER tsc --noEmit 2>&1                                              # type check
$RUNNER biome check --no-errors-on-unmatched <changed files> 2>&1      # lint (preferred)
$RUNNER eslint <changed files> 2>&1                                    # lint (fallback if no biome)
```

### Python (`.py`)

```bash
ruff check <changed files> 2>&1      # lint
mypy <changed files> 2>&1            # type check
```

### Go (`.go`)

```bash
go vet ./... 2>&1
```

### Rust (`.rs`)

```bash
cargo check 2>&1
```

### Result handling

| Exit code | Action |
|-----------|--------|
| 0 | "All clear" |
| Non-zero | Capture output as findings |
| Command not found | "Skipped (not installed)" |

---

## Layer 2: Blast Radius (Codebase Intelligence)

For each changed file, find files that **import** it (1 level deep). This reveals code that could break from the changes.

### Import search patterns by language

| Language | Pattern |
|----------|---------|
| TS/JS | `from ['"].*{module_name}['"]` and `require\(['"].*{module_name}['"]\)` |
| Python | `^(from\|import)\s+.*{module_name}` |
| Go | `".*{module_name}"` |

Where `{module_name}` is the changed file's name without extension. For `index` files, use the parent directory name instead.

### Building the blast radius

1. Start with all changed files
2. For each changed file, Grep for importers using patterns above
3. Add importers to the list
4. Deduplicate
5. **Cap at 30 files total** — all changed files + up to 20 importers
6. If capped, note which importers were excluded in the report

Read **all** blast radius files into context before dispatching agents.

---

## Layer 3: Independent Review Passes

Use the environment's native subagent mechanism when available. Run independent passes in parallel up to the environment's safe concurrency limit; otherwise run the same focuses locally and sequentially. Do not require `TeamCreate`, `SendMessage`, or any named agent package.

### What each agent receives

- The full diff
- The blast radius file list and contents
- The review rules (from `.claude/review-rules.md`)
- The CLAUDE.md project standards
- Their specific focus (in the prompt)
- Instruction to return findings with exact files/lines, severity, and evidence

### Review focus table

| Pass | Focus | Prompt guidance |
|------|-------|-----------------|
| `correctness` | Logic correctness, regressions, repository-policy compliance | Include diff, blast radius files, review rules, and repository instructions. Distinguish changed files from context. |
| `failure-handling` | Error handling gaps, silent failures, swallowed exceptions | Examine changed code and affected callers. |
| `tests` | Coverage gaps and missing realistic edge cases | Check whether tests exercise observable behavior and each changed branch. |
| `types-and-simplicity` | Invariants, unnecessary complexity, dead code, comments | Review modified types and abstractions; flag only comments that are stale, misleading, or restate obvious code. |

Prefer four strong passes over six overlapping agents. The orchestrator must deduplicate findings and verify each one against the source before reporting it.

### Failure handling

If any pass fails or times out, note the gap and continue. Never present an unverified subagent claim as a finding.

---

## Report Template

```markdown
# PR Review Report

## TL;DR
[1-3 sentences with the most critical finding and merge risk]

## Static Analysis
[Results per tool, or "All clear — no issues found"]

## Blast Radius
[N changed + M affected = T total files in scope]
[List affected files if M > 0]

## Code Review
[Findings by severity: Critical > Important > Minor]
[Or "No issues found"]

## Error Handling
[Silent failure findings]
[Or "No issues found"]

## Test Coverage
[Coverage gaps]
[Or "Coverage looks adequate"]

## Type Safety
[Type design findings]
[Or "No type issues found"]

## Comments
[Misleading, stale, or missing comments]
[Or "No comment issues found"]

## Simplification Opportunities
[Over-engineered patterns, dead code, complexity reduction suggestions]
[Or "No simplification needed"]

## Review Rules Applied
[Rules from .claude/review-rules.md that matched]
[Or "No review rules file yet"]

## Action Items
[Numbered list ordered by severity]
[Or "No action items — this PR looks good."]
```
