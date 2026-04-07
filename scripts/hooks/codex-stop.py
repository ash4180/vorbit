#!/usr/bin/env python3
"""Codex CLI Stop hook — captures corrections into Vorbit canonical store.

Install: add to ~/.codex/hooks.json or <repo>/.codex/hooks.json
Requires: [features] codex_hooks = true in ~/.codex/config.toml

Codex passes JSON on stdin with session_id, transcript_path, cwd.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vorbit_core.learn.runtime import capture_from_transcript  # noqa: E402


def main() -> None:
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", "")

    if not transcript_path or not Path(transcript_path).exists():
        sys.exit(0)

    rules_source = REPO_ROOT / "skills" / "learn" / "vorbit-learning-rules.md"
    if not rules_source.exists():
        sys.exit(0)

    capture_from_transcript(
        source_agent="codex",
        runtime="codex-cli",
        project_root=cwd or Path.cwd(),
        transcript_path=transcript_path,
        rules_source=rules_source,
        seen_state_name="codex-seen.tsv",
        transcript_format="codex",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
