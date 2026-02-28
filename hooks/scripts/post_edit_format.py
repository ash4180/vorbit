#!/usr/bin/env python3
"""PostToolUse hook - auto-formats files after Edit tool invocation.

Priority: biome > prettier. Exit code: always 0 (never blocks).
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
