#!/usr/bin/env python3
"""Block use_figma calls that compose instances without importing components."""
import json
import os
import sys
from typing import Any


CREATE_INSTANCE = ".createInstance("
IMPORT_COMPONENT = "importComponentByKeyAsync("


def load_tool_input() -> dict[str, Any]:
    stdin_raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if stdin_raw:
        try:
            payload: dict[str, Any] = json.loads(stdin_raw)
            nested = payload.get("tool_input")
            if isinstance(nested, dict):
                return nested
        except json.JSONDecodeError:
            pass

    env_raw = os.environ.get("TOOL_INPUT", "")
    if env_raw:
        try:
            env_payload: dict[str, Any] = json.loads(env_raw)
            return env_payload
        except json.JSONDecodeError:
            pass

    return {}


def main() -> None:
    tool_input = load_tool_input()
    js = tool_input.get("code", "")
    if not isinstance(js, str) or not js:
        sys.exit(0)

    if CREATE_INSTANCE in js and IMPORT_COMPONENT not in js:
        sys.stderr.write(
            "BLOCKED by figma skill hook: use_figma JS contains "
            ".createInstance() but no importComponentByKeyAsync().\n"
            "This pattern produces orphan <frame> nodes instead of real "
            "library instances.\n"
            "Fix: for every Phase 3 component key, call "
            "`await figma.importComponentByKeyAsync(\"<key>\")` BEFORE "
            "any .createInstance() call. Bind variables via "
            "`figma.variables.getVariableByIdAsync(\"<var-id>\")`.\n"
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
