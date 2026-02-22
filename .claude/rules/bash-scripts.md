# Bash Script Rules

Patterns learned from writing and testing hook scripts in this project.

## jq Inside Bash
- **Never use `!=` in jq expressions run from bash** — `!` triggers histexpand and mangles the expression. Use `== ""` with inverted logic instead.

## macOS Path Resolution
- **`/tmp` resolves to `/private/tmp`** — `git rev-parse --show-toplevel` returns the resolved symlink path. When computing project slugs in tests, always use the resolved path. Raw `/tmp/...` and resolved `/private/tmp/...` produce different slugs.

## Subshell Traps
- **`cd` inside `$()` doesn't persist** — command substitution (`result=$(my_func)`) runs in a subshell. Any `cd` inside the function doesn't affect the caller. Always `cd` explicitly after the substitution if you need to be in that directory.

## Test Harness
- **Each test file must define all assert helpers it uses** — helpers defined in a sibling test file are not available. Calling an undefined function with `set -uo pipefail` (no `-e`) prints "command not found" to stderr but doesn't abort; `TESTS_RUN` never increments, giving a silent missing test with a green count. Always define every assert helper inside the file that uses it.
- **Never suppress stderr with `2>/dev/null` on script invocations in tests** — this can hide failures from `set -e` pipelines and mask errors that only surface in the test environment. Use `2>"$log_file"` to capture stderr for debugging instead.
- **Green tests can miss real failure modes** — tests that only use "safe" fixture inputs (unambiguous keywords, clean paths) pass while the script fails on real inputs. Always include adversarial fixtures: inputs that should NOT trigger but share characteristics with inputs that should (e.g. "not working" should trigger but "I know nothing" should not).
- **Tests that share global sidecar state need explicit teardown** — when a script writes to a sidecar file (e.g. `~/.claude/rules/.seen-correction-sessions`), each test must delete it in teardown. Without this, a session ID written by test N silently deduplicates test N+1 that reuses the same ID, causing a green result for the wrong reason.
- **Validate fixture format against a real sample before writing tests** — simplified fixtures (e.g. `"content": "plain string"`) hide bugs that only surface on real data. For transcript parsing, always check a real `.jsonl` file first to confirm the actual field structure, then build fixtures that match it. The Claude transcript format stores message content as an array of `{type, text}` blocks, not a plain string.

## Keyword Extraction
- **Session continuation summaries produce false positives** — when Claude Code continues a session, the continuation summary quotes past corrections ("User said 'wrong'..."). The keyword filter matches these quoted keywords. Filter out messages over ~500 characters or detect the `"This session is being continued"` pattern before keyword matching.
- **Teammate messages produce false positives** — when using team agents, `<teammate-message>` blocks contain audit/analysis text with words like "wrong", "error", "broken" that trigger the keyword filter. Filter out messages containing `<teammate-message` tags before keyword matching.
- **jq regex is substring-matching by default** — `test("no"; "i")` matches inside "not", "know", "cannot". Use Oniguruma word boundaries: build regex as `\\b${KEYWORD_REGEX}\\b` in bash (each `\b` needs double-escaping). Always verify with adversarial inputs that share characters with legitimate keywords.
- **Short common words make poor correction signals** — even with word boundaries, words like `no`, `error`, `actually` appear constantly in normal technical discussion and produce false positives. Prefer multi-word phrases or domain-specific terms that can't appear incidentally.

## Pipefail + Missing Files
- **`awk file | cmd || fallback` double-captures when file is missing** — with `set -uo pipefail`, if `awk` fails on a missing file, the pipeline fails and `|| fallback` runs. But `cmd` (e.g. `jq`) already wrote output before the pipeline exit was evaluated — so the variable captures both `cmd`'s output AND `fallback`'s output, producing invalid data. Fix: wrap awk in a group: `{ awk ... 2>/dev/null || true; } | cmd || fallback` — the `|| true` ensures the group always exits 0, so `|| fallback` never fires spuriously.
- **Grep patterns with `[` need escaping** — in `assert_file_contains`, patterns like `[msg:` are treated as unclosed regex bracket expressions by grep. Escape with `\[`: `assert_file_contains "$file" '\[msg:' "test name"`.

## Script Design
- **Separate dedup state from output data** — don't write session IDs or seen-markers into the output file users will read (e.g. `unprocessed-corrections.md`). Use a dedicated sidecar file (e.g. `.seen-correction-sessions`) for dedup tracking. Output files should contain only real content, never structural markers added to prevent re-processing.

## Documentation vs Scripts
- **Manual instructions must mirror script logic** — if `dev-setup.sh` resolves paths and versions dynamically (`$PLUGIN_SOURCE`, `$VERSION`), CLAUDE.md manual instructions must do the same. Never hardcode values that the script reads from config files (e.g., version from `plugin.json`).

## Git Workflow
- **Unstaged changes are lost on branch switch** — switching branches discards uncommitted modifications. Commit or stash before switching. If lost, rewrite from the session transcript.
