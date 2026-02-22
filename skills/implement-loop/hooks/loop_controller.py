#!/usr/bin/env python3
"""Stop hook - manages implement loop iteration.

Exit codes: 0 = end session, 2 = inject stdout and continue loop.
Reads loop state from .claude/.loop-state.json at project root.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True
        )
        project_root = result.stdout.strip() if result.returncode == 0 else os.getcwd()
    except Exception:
        project_root = os.getcwd()

    state_file = Path(project_root) / ".claude" / ".loop-state.json"

    if not state_file.exists():
        sys.stdin.read()
        sys.exit(0)

    try:
        state = json.loads(state_file.read_text())
    except Exception:
        sys.stdin.read()
        sys.exit(0)

    if not state.get("active"):
        sys.stdin.read()
        sys.exit(0)

    completion_signal = state.get("completionSignal", "")
    max_iterations = state.get("maxIterations", 50)
    current_iteration = state.get("iteration", 1)
    command = state.get("command", "")

    # Read Claude's last output (only after confirming loop is active)
    claude_output = sys.stdin.read()

    # Check for completion signal
    if completion_signal and completion_signal in claude_output:
        state_file.unlink(missing_ok=True)
        sys.exit(0)

    # Check max iterations
    if current_iteration >= max_iterations:
        state_file.unlink(missing_ok=True)
        sys.exit(0)

    # Increment and re-inject command to continue loop
    state["iteration"] = current_iteration + 1
    state_file.write_text(json.dumps(state))

    print(command)
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
