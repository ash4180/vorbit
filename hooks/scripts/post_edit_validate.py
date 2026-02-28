#!/usr/bin/env python3
"""PostToolUse hook - validates files after Edit tool invocation.

Priority: TypeScript > Python > Go. Blocks on validation errors (exit non-zero).
Exits 0 silently if no validator found or on unexpected errors.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from _utils import find_project_root, get_file_path_or_exit, parse_tool_input


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
            result = subprocess.run(["tsc", "--noEmit"], cwd=project_root)
            sys.exit(result.returncode)
        except FileNotFoundError:
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
                    result = subprocess.run(["mypy", file_path])
                    sys.exit(result.returncode)
                except FileNotFoundError:
                    pass
            try:
                result = subprocess.run(["pyright", file_path])
                sys.exit(result.returncode)
            except FileNotFoundError:
                pass
        sys.exit(0)

    # Go validation
    if Path(project_root, "go.mod").exists() and file_ext == "go":
        if dry_run:
            print("[DRY_RUN] Would run: go build ./...")
            sys.exit(0)
        try:
            result = subprocess.run(["go", "build", "./..."], cwd=project_root)
            sys.exit(result.returncode)
        except FileNotFoundError:
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
