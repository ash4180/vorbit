# Hook Script Rules

Patterns learned from writing and testing hook scripts in this project.
Hook scripts are now Python (`hooks/scripts/*.py`, `skills/*/hooks/*.py`). Bash-only patterns (jq, pipefail, histexpand) have been removed.

## Python Hook Scripts

- **`sys.exit()` raises `SystemExit` (BaseException), not caught by `except Exception`** — this is intentional and correct for stop hooks. Never wrap `sys.exit()` in a bare `except Exception` block; use `except BaseException` or restructure to call `sys.exit()` only at the top level.
- **Stop hook scripts must consume `sys.stdin.read()` before any early exit** — Claude Code pipes output into stdin; if the hook exits without reading, the pipe can block or error. Call `sys.stdin.read()` as the first statement in `main()`.
- **Use `try: main() / except Exception: sys.exit(0)` in `__main__`** — unexpected errors in a stop hook must fall back to `sys.exit(0)`, not crash with a non-zero code that Claude Code treats as "Stop hook error". Wrap the top-level call in a broad exception handler.

## Pyre2 Type Checking

- **Add type annotations to all hook script functions** — Pyre2 can't infer types through nested generics like `list[dict[str, Any]]`. Without annotations, subscripting (`messages[i]`) and slicing (`text[:200]`) produce cascading errors. Annotate parameters, return types, empty list initializers (`all_matching: list[int] = []`), and local variables extracted from generic containers (`entry: dict[str, Any] = messages[i]`).
- **Pyre2 doesn't narrow types through `sys.exit()` guards** — `if not match: sys.exit(0)` doesn't tell Pyre2 that `match` is non-None afterward. Add `assert match is not None` after the guard to explicitly narrow the type.

## macOS Path Resolution

- **`/tmp` resolves to `/private/tmp`** — `git rev-parse --show-toplevel` returns the resolved symlink path. When computing project slugs in tests, always use `path.resolve()` (Python) or `realpath` (bash). Raw `/tmp/...` and resolved `/private/tmp/...` produce different slugs.

## Test Harness (pytest)

- **Override `HOME` env in subprocess to isolate hook file I/O** — hooks that call `Path.home()` read `$HOME`. Pass `{"HOME": str(tmp_home)}` in `env_overrides` so all `~/.claude/` reads and writes go to a temp directory instead of the real user home.
- **Green tests can miss real failure modes** — tests that only use "safe" fixture inputs (unambiguous keywords, clean paths) pass while the script fails on real inputs. Always include adversarial fixtures: inputs that should NOT trigger but share characteristics with inputs that should (e.g. "not working" should trigger but "I know nothing" should not).
- **Validate fixture format against a real sample before writing tests** — simplified fixtures (e.g. `"content": "plain string"`) hide bugs that only surface on real data. For transcript parsing, always check a real `.jsonl` file first to confirm the actual field structure. The Claude transcript format stores assistant message content as an array of `{"type": "text", "text": "..."}` blocks, not a plain string.
- **Sidecar state is isolated automatically by `tmp_home`** — pytest's `tmp_path` fixture gives each test a unique temp dir; the `tmp_home` fixture roots all `~/.claude/` I/O inside it. No explicit teardown of seen files or output files is needed between tests.

## Keyword Extraction

- **Session continuation summaries produce false positives** — when Claude Code continues a session, the continuation summary quotes past corrections ("User said 'wrong'..."). The keyword filter matches these quoted keywords. Filter out messages over ~500 characters or detect the `"This session is being continued"` pattern before keyword matching.
- **Teammate messages produce false positives** — when using team agents, `<teammate-message>` blocks contain audit/analysis text with words like "wrong", "error", "broken" that trigger the keyword filter. Filter out messages containing `<teammate-message` tags before keyword matching.
- **Python `re` is substring-matching by default** — `re.search(r"no", text, re.I)` matches inside "not", "know", "cannot". Use word boundaries: `r"\b(keyword)\b"` in Python `re`. Always verify with adversarial inputs that share characters with legitimate keywords.
- **Short common words make poor correction signals** — even with word boundaries, words like `no`, `error`, `actually` appear constantly in normal technical discussion and produce false positives. Prefer multi-word phrases or domain-specific terms that can't appear incidentally.

## Script Design

- **Separate dedup state from output data** — don't write session IDs or seen-markers into the output file users will read (e.g. `unprocessed-corrections.md`). Use a dedicated sidecar file (e.g. `.seen-correction-sessions`) for dedup tracking. Output files should contain only real content, never structural markers added to prevent re-processing.

## Documentation vs Scripts

- **Manual instructions must mirror script logic** — if `dev-setup.sh` resolves paths and versions dynamically (`$PLUGIN_SOURCE`, `$VERSION`), CLAUDE.md manual instructions must do the same. Never hardcode values that the script reads from config files (e.g., version from `plugin.json`).

## Git Workflow

- **Unstaged changes are lost on branch switch** — switching branches discards uncommitted modifications. Commit or stash before switching. If lost, rewrite from the session transcript.
