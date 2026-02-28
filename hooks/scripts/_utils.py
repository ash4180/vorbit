"""Shared utilities for hook scripts."""

import json
import os
import subprocess
import sys
from pathlib import Path


def find_project_root(file_path: str) -> str:
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


def parse_tool_input() -> dict:
    """Parse TOOL_INPUT from environment. Returns empty dict on failure."""
    tool_input_str = os.environ.get("TOOL_INPUT", "")
    try:
        return json.loads(tool_input_str) if tool_input_str else {}
    except json.JSONDecodeError:
        return {}


def get_file_path_or_exit(tool_input: dict) -> str:
    """Extract file_path from tool input. Exits 0 if missing or invalid."""
    file_path = tool_input.get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        sys.exit(0)
    return file_path
