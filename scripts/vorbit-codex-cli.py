#!/usr/bin/env python3
"""Capture Codex CLI session transcripts into the Vorbit canonical store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vorbit_core.learn.runtime import capture_from_transcript  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=str(Path.cwd()))
    parser.add_argument("--transcript", required=True, help="JSONL transcript produced by the wrapper or CLI")
    parser.add_argument(
        "--rules-source",
        default=str(PROJECT_ROOT / "skills" / "learn" / "vorbit-learning-rules.md"),
        help="Rules file used for correction and voluntary keyword detection",
    )
    args = parser.parse_args()

    capture_from_transcript(
        source_agent="codex",
        runtime="codex-cli",
        project_root=args.project_root,
        transcript_path=args.transcript,
        rules_source=args.rules_source,
        seen_state_name="codex-seen.tsv",
        transcript_format="codex",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
