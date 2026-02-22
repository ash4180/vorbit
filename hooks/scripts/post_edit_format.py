#!/usr/bin/env python3
"""PostToolUse hook - auto-formats files after Edit tool invocation.

Priority: biome > prettier. Exit code: always 0 (never blocks).
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
    dry_run = os.environ.get("DRY_RUN") == "1"

    # Biome (highest priority)
    if Path(project_root, "biome.json").exists() or Path(project_root, "biome.jsonc").exists():
        if dry_run:
            print(f"[DRY_RUN] Would run: biome format --write {file_path}")
        else:
            try:
                subprocess.run(["biome", "format", "--write", file_path], capture_output=True)
            except FileNotFoundError:
                pass
        sys.exit(0)

    # Prettier
    prettierrc_exists = any(Path(project_root).glob(".prettierrc*"))
    prettier_in_package = False
    package_json = Path(project_root, "package.json")
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            prettier_in_package = "prettier" in pkg
        except Exception:
            pass

    if prettierrc_exists or prettier_in_package:
        if dry_run:
            print(f"[DRY_RUN] Would run: prettier --write {file_path}")
        else:
            try:
                subprocess.run(["prettier", "--write", file_path], capture_output=True)
            except FileNotFoundError:
                pass
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
