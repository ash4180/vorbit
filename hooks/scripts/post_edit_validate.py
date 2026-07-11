#!/usr/bin/env python3
"""PostToolUse hook - advisory type check after Edit tool invocation.

Priority: TypeScript > Python > Go. Never blocks: on checker failure it
reports the errors to the model as PostToolUse additionalContext JSON and
exits 0. A multi-file refactor is transiently inconsistent between related
edits; blocking on that state penalizes legitimate work, so the errors are
surfaced as context the model acts on at the next natural point instead.
Exits 0 silently when the checker passes, is missing, or an unexpected
error occurs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _utils import find_project_root, get_file_path_or_exit, parse_tool_input

MAX_ADVISORY_CHARS = 2000


def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def _advise(label: str, output: str) -> None:
    """Surface checker errors to the model without blocking the edit."""
    if len(output) > MAX_ADVISORY_CHARS:
        output = output[:MAX_ADVISORY_CHARS] + "\n[... truncated]"
    context = (
        f"Advisory type check (non-blocking): `{label}` reported errors after this edit. "
        "If you are mid-refactor, finish the related edits first, then resolve anything "
        "still failing before completing the task.\n"
        f"{output}"
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )


def main():
    tool_input = parse_tool_input()
    if not tool_input:
        sys.exit(0)

    file_path = get_file_path_or_exit(tool_input)
    project_root = find_project_root(file_path)
    file_ext = Path(file_path).suffix.lstrip(".")
    dry_run = os.environ.get("DRY_RUN") == "1"

    # TypeScript validation
    if Path(project_root, "tsconfig.json").exists() and file_ext in ("ts", "tsx"):
        if dry_run:
            print("[DRY_RUN] Would run: tsc --noEmit")
            sys.exit(0)
        try:
            code, output = _run(["tsc", "--noEmit"], cwd=project_root)
            if code != 0:
                _advise("tsc --noEmit", output)
        except FileNotFoundError:
            pass
        sys.exit(0)

    # Python validation (mypy or pyright)
    pyproject = Path(project_root, "pyproject.toml")
    if pyproject.exists() and file_ext == "py":
        try:
            content = pyproject.read_text()
            has_mypy = "[tool.mypy]" in content
            has_pyright = "[tool.pyright]" in content
        except Exception:
            has_mypy = has_pyright = False

        if has_mypy or has_pyright:
            if dry_run:
                print(f"[DRY_RUN] Would run: mypy or pyright {file_path}")
                sys.exit(0)
            if has_mypy:
                try:
                    code, output = _run(["mypy", file_path])
                    if code != 0:
                        _advise("mypy", output)
                    sys.exit(0)
                except FileNotFoundError:
                    pass
            try:
                code, output = _run(["pyright", file_path])
                if code != 0:
                    _advise("pyright", output)
            except FileNotFoundError:
                pass
        sys.exit(0)

    # Go validation
    if Path(project_root, "go.mod").exists() and file_ext == "go":
        if dry_run:
            print("[DRY_RUN] Would run: go build ./...")
            sys.exit(0)
        try:
            code, output = _run(["go", "build", "./..."], cwd=project_root)
            if code != 0:
                _advise("go build ./...", output)
        except FileNotFoundError:
            pass
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
