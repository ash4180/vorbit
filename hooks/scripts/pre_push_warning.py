#!/usr/bin/env python3
"""PreToolUse hook - warns before git push commands. Never blocks (always exits 0)."""

import json
import os
import re
import sys


def main():
    tool_input_str = os.environ.get("TOOL_INPUT", "")
    try:
        tool_input = json.loads(tool_input_str) if tool_input_str else {}
    except json.JSONDecodeError:
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    if re.match(r"^git\s+push", command):
        print("⚠️  About to push to remote repository")
        print(f"   Command: {command}")
        print("   Make sure you've reviewed your changes!")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
