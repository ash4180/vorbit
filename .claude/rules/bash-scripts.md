# Bash Script Rules

Patterns learned from writing and testing hook scripts in this project.

## jq Inside Bash
- **Never use `!=` in jq expressions run from bash** — `!` triggers histexpand and mangles the expression. Use `== ""` with inverted logic instead.

## macOS Path Resolution
- **`/tmp` resolves to `/private/tmp`** — `git rev-parse --show-toplevel` returns the resolved symlink path. When computing project slugs in tests, always use the resolved path. Raw `/tmp/...` and resolved `/private/tmp/...` produce different slugs.

## Subshell Traps
- **`cd` inside `$()` doesn't persist** — command substitution (`result=$(my_func)`) runs in a subshell. Any `cd` inside the function doesn't affect the caller. Always `cd` explicitly after the substitution if you need to be in that directory.

## Test Harness
- **Never suppress stderr with `2>/dev/null` on script invocations in tests** — this can hide failures from `set -e` pipelines and mask errors that only surface in the test environment. Use `2>"$log_file"` to capture stderr for debugging instead.

## Keyword Extraction
- **Session continuation summaries produce false positives** — when Claude Code continues a session, the continuation summary quotes past corrections ("User said 'wrong'..."). The keyword filter matches these quoted keywords. Filter out messages over ~500 characters or detect the `"This session is being continued"` pattern before keyword matching.

## Git Workflow
- **Unstaged changes are lost on branch switch** — switching branches discards uncommitted modifications. Commit or stash before switching. If lost, rewrite from the session transcript.
