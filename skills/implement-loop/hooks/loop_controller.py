#!/usr/bin/env python3
"""Continue an active Vorbit implementation loop after a session stop.

This is a Claude Code Stop hook. It ALWAYS exits 0:

- to let the session stop, it returns without printing anything;
- to keep the loop going, it prints a JSON ``block`` decision on stdout,
  which is the documented channel a Stop hook uses to reach the model
  (stdout on a non-zero exit is discarded, so exit 2 would drop the command).

The loop state file's ``status`` field is the single source of truth. The
hook never touches source code. Unreadable or unsupported state is moved
aside rather than left in place, so a stuck file cannot block every future
session stop.
"""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

STATE_RELPATH = (".claude", ".loop-state.json")
SUPPORTED_VERSION = 2


def _find_state_file() -> Path | None:
    """Walk up from cwd to the repo root, returning the loop-state path if present."""
    current = Path.cwd().resolve()
    for directory in (current, *current.parents):
        candidate = directory.joinpath(*STATE_RELPATH)
        if candidate.exists():
            return candidate
        if (directory / ".git").exists():
            break
    return None


def _load_state(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_state(path: Path, state: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)


def _quarantine(path: Path, reason: str) -> None:
    """Move an unusable state file aside so it cannot block future stops."""
    location = path
    try:
        aside = path.with_suffix(".invalid")
        path.replace(aside)
        location = aside
    except OSError:
        pass
    print(f"Vorbit loop: {reason} Moved aside to {location}.", file=sys.stderr)


def _retire(path: Path, state: dict[str, Any], status: str, reason: str) -> None:
    """Record a terminal status with a visible reason, then allow the stop."""
    state["status"] = status
    state["active"] = False
    state["blockReason"] = reason
    try:
        _write_state(path, state)
    except OSError:
        pass
    print(f"Vorbit loop {status}: {reason}", file=sys.stderr)


def _continue(path: Path, state: dict[str, Any], command: str, iteration: int, maximum: int) -> None:
    """Block the stop and tell Claude to run the next loop iteration."""
    state["iteration"] = iteration + 1
    _write_state(path, state)
    reason = (
        f"Vorbit loop iteration {iteration + 1}/{maximum} in progress. "
        f"Continue the queue by running: {command}"
    )
    print(json.dumps({"decision": "block", "reason": reason}))


def main() -> None:
    # Drain stdin first: Claude Code pipes a JSON control payload here, and the
    # pipe can block if the hook exits without reading it.
    sys.stdin.read()

    state_file = _find_state_file()
    if state_file is None:
        return

    state = _load_state(state_file)
    if state is None:
        _quarantine(state_file, "state file is unreadable or not an object.")
        return

    if state.get("version") != SUPPORTED_VERSION:
        _quarantine(
            state_file,
            f"state version {state.get('version')!r} is unsupported "
            f"(expected {SUPPORTED_VERSION}); not resuming.",
        )
        return

    status = state.get("status")
    if status == "completed":
        state_file.unlink(missing_ok=True)
        return
    if status != "running":
        # blocked / needs_input / failed / canceled / unknown: wait for the user.
        return

    command = state.get("command")
    try:
        tokens = shlex.split(command) if isinstance(command, str) else []
    except ValueError:
        tokens = []
    if not tokens or "--loop" not in tokens:
        _retire(state_file, state, "failed", "loop command is missing or does not include --loop.")
        return

    iteration = state.get("iteration", 1)
    maximum = state.get("maxIterations", 50)
    if type(iteration) is not int or type(maximum) is not int or iteration < 1 or maximum < 1:
        _retire(state_file, state, "failed", "iteration values in loop state are invalid.")
        return

    if iteration >= maximum:
        _retire(state_file, state, "blocked", f"reached maxIterations ({maximum}).")
        return

    _continue(state_file, state, command, iteration, maximum)


if __name__ == "__main__":
    # A Stop hook must never exit non-zero on an unexpected error, or Claude Code
    # reports "Stop hook error" and blocks the session. Catch everything (including
    # KeyboardInterrupt) and fall through to exit 0.
    try:
        main()
    except BaseException as error:  # noqa: BLE001 - stop hooks fail open by contract
        print(f"Vorbit loop controller failed open: {error}", file=sys.stderr)
    sys.exit(0)
