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


def find_project_root(file_path):
    """Find git root, falling back to file's parent directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
            cwd=str(Path(file_path).parent)
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return str(Path(file_path).parent)


def main():
    tool_input_str = os.environ.get("TOOL_INPUT", "")
    try:
        tool_input = json.loads(tool_input_str) if tool_input_str else {}
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        sys.exit(0)

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
