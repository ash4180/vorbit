#!/usr/bin/env python3
"""Gemini CLI SessionEnd hook — captures corrections into Vorbit canonical store.

Install: add to ~/.gemini/settings.json or <repo>/.gemini/settings.json

Gemini passes JSON on stdin with session context.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vorbit_core.learn.runtime import capture_from_transcript  # noqa: E402


def _find_latest_gemini_transcript(project_name: str) -> Path | None:
    """Find the most recent Gemini session transcript for a project."""
    gemini_chats = Path.home() / ".gemini" / "tmp" / project_name / "chats"
    if not gemini_chats.exists():
        return None
    try:
        transcripts = sorted(
            gemini_chats.glob("session-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except Exception:
        return None
    return transcripts[0] if transcripts else None


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        hook_input = {}

    cwd = hook_input.get("cwd", str(Path.cwd()))
    project_name = Path(cwd).name

    # Gemini may pass transcript_path directly, or we find the latest
    transcript_path = hook_input.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        found = _find_latest_gemini_transcript(project_name)
        if found is None:
            sys.exit(0)
        transcript_path = str(found)

    rules_source = REPO_ROOT / "skills" / "learn" / "vorbit-learning-rules.md"
    if not rules_source.exists():
        sys.exit(0)

    capture_from_transcript(
        source_agent="gemini",
        runtime="gemini-cli",
        project_root=cwd,
        transcript_path=transcript_path,
        rules_source=rules_source,
        seen_state_name="gemini-seen.tsv",
        transcript_format="gemini",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
