#!/usr/bin/env python3
"""Stop hook - detect corrections and write canonical Vorbit captures.

Exit codes: always 0.
Compatibility behavior preserved:
- creates ~/.claude/rules/vorbit-learning.md symlink
- keeps ~/.claude/rules/pending-capture.md bridge
- keeps legacy Obsidian-style export for Claude users
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _runtime_plugin_root() -> Path:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    if plugin_root:
        return Path(plugin_root).expanduser().resolve()
    return Path(__file__).resolve().parent.parent.parent.parent


MODULE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RUNTIME_PLUGIN_ROOT = _runtime_plugin_root()
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from vorbit_core.learn.runtime import capture_from_transcript  # noqa: E402


def _project_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except Exception:
        pass
    return Path.cwd().resolve()


def _sessions_dir(project_root: Path) -> Path:
    project_slug = str(project_root).replace("/", "-")
    return Path.home() / ".claude" / "projects" / project_slug


def _latest_transcript(project_root: Path) -> Path | None:
    sessions_dir = _sessions_dir(project_root)
    try:
        transcripts = sorted(
            sessions_dir.glob("*.jsonl"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    except Exception:
        return None
    return transcripts[0] if transcripts else None


def _loop_active(project_root: Path) -> bool:
    loop_state_path = project_root / ".claude" / ".loop-state.json"
    if not loop_state_path.exists():
        return False
    try:
        loop_state = json.loads(loop_state_path.read_text())
    except Exception:
        return False
    return loop_state.get("active") is True


def main() -> None:
    sys.stdin.read()

    rules_source = RUNTIME_PLUGIN_ROOT / "skills" / "learn" / "vorbit-learning-rules.md"
    if not rules_source.exists():
        sys.exit(0)

    project_root = _project_root()
    if _loop_active(project_root):
        sys.exit(0)

    transcript_path = _latest_transcript(project_root)
    if transcript_path is None:
        sys.exit(0)

    capture_from_transcript(
        source_agent="claude",
        runtime="claude-code",
        project_root=project_root,
        transcript_path=transcript_path,
        rules_source=rules_source,
        seen_state_name="claude-seen.tsv",
        transcript_format="claude",
        compatibility_seen_path=Path.home() / ".claude" / "rules" / ".seen-correction-sessions",
        legacy_claude_bridge=True,
    )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
