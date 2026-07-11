#!/usr/bin/env python3
"""Continue an active Vorbit implementation loop.

Exit codes: 0 = allow stop, 2 = inject stdout and continue or block on invalid state.
The hook never mutates source code and never deletes blocked state.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


COMPLETION_SIGNAL = "<!-- VORBIT_LOOP_COMPLETE -->"


def _project_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return Path.cwd()

    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    return Path(os.getcwd())


def _read_state(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_state(path: Path, state: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)


def main() -> None:
    # Always drain stdin before any early exit. Claude pipes its final output here.
    claude_output = sys.stdin.read()
    state_file = _project_root() / ".claude" / ".loop-state.json"

    if not state_file.exists():
        return

    state = _read_state(state_file)
    if state is None:
        print(
            f"Vorbit loop state is unreadable; fix or remove it explicitly: {state_file}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    completion_signal = state.get("completionSignal")
    if state.get("status") == "completed":
        if completion_signal != COMPLETION_SIGNAL:
            state["active"] = False
            state["status"] = "failed"
            state["blockReason"] = "Loop state has an invalid completion signal"
            _write_state(state_file, state)
            return
        if COMPLETION_SIGNAL in claude_output:
            state_file.unlink(missing_ok=True)
        return

    if not state.get("active"):
        return

    if completion_signal != COMPLETION_SIGNAL:
        state["active"] = False
        state["status"] = "failed"
        state["blockReason"] = "Loop state has an invalid completion signal"
        _write_state(state_file, state)
        return

    current_iteration = state.get("iteration", 1)
    max_iterations = state.get("maxIterations", 50)
    if (
        type(current_iteration) is not int
        or type(max_iterations) is not int
        or current_iteration < 1
        or max_iterations < 1
    ):
        state["active"] = False
        state["status"] = "failed"
        state["blockReason"] = "Invalid iteration values in loop state"
        _write_state(state_file, state)
        return

    if current_iteration >= max_iterations:
        state["active"] = False
        state["status"] = "blocked"
        state["blockReason"] = f"Reached maxIterations ({max_iterations})"
        _write_state(state_file, state)
        print(f"Vorbit loop blocked after {max_iterations} iterations; state preserved at {state_file}.")
        return

    command = state.get("command")
    try:
        command_tokens = shlex.split(command) if isinstance(command, str) else []
    except ValueError:
        command_tokens = []
    if not command_tokens or "--loop" not in command_tokens:
        state["active"] = False
        state["status"] = "failed"
        state["blockReason"] = "Loop command is missing or does not include --loop"
        _write_state(state_file, state)
        return

    state["iteration"] = current_iteration + 1
    _write_state(state_file, state)
    print(command)
    raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f"Vorbit loop controller failed closed: {error}", file=sys.stderr)
        sys.exit(2)
