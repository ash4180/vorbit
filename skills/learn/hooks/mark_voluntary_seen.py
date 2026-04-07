#!/usr/bin/env python3
"""Mark voluntary Claude messages as seen in both canonical and legacy state."""

from __future__ import annotations

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

from vorbit_core.config import resolve_config  # noqa: E402
from vorbit_core.learn.runtime import append_seen_indices, load_seen_indices, scan_keywords  # noqa: E402
from vorbit_core.learn.storage import LearnStore  # noqa: E402
from vorbit_core.learn.text import load_transcript, read_comment  # noqa: E402


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


def _latest_transcript(project_root: Path) -> Path | None:
    sessions_dir = Path.home() / ".claude" / "projects" / str(project_root).replace("/", "-")
    try:
        transcripts = sorted(
            sessions_dir.glob("*.jsonl"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    except Exception:
        return None
    return transcripts[0] if transcripts else None


def main() -> None:
    project_root = _project_root()
    transcript_path = _latest_transcript(project_root)
    if transcript_path is None:
        sys.exit(0)

    rules_source = RUNTIME_PLUGIN_ROOT / "skills" / "learn" / "vorbit-learning-rules.md"
    if not rules_source.exists():
        sys.exit(0)

    try:
        rules_text = rules_source.read_text()
    except Exception:
        sys.exit(0)

    voluntary_csv = read_comment(rules_text, "voluntary-keywords")
    if not voluntary_csv:
        sys.exit(0)

    import re

    keywords = [item.strip() for item in voluntary_csv.split(",") if item.strip()]
    if not keywords:
        sys.exit(0)
    pattern = r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"
    messages = load_transcript(transcript_path, fmt="claude")
    if not messages:
        sys.exit(0)

    session_id = transcript_path.stem
    config = resolve_config(project_root, legacy_claude_bridge=True)
    store = LearnStore(config)
    state_path = store.state_dir / "claude-seen.tsv"
    legacy_path = Path.home() / ".claude" / "rules" / ".seen-correction-sessions"

    matches = scan_keywords(messages, pattern)
    if not matches:
        sys.exit(0)

    seen = load_seen_indices(state_path, session_id, "fv") | load_seen_indices(legacy_path, session_id, "fv")
    new_indices = [idx for idx in matches if idx not in seen]
    if not new_indices:
        sys.exit(0)

    append_seen_indices(state_path, session_id, "fv", new_indices)
    append_seen_indices(legacy_path, session_id, "fv", new_indices)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
