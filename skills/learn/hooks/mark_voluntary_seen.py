#!/usr/bin/env python3
"""Mark all voluntary-keyword messages in current session as seen.

Called by SKILL.md Voluntary Capture after writing a learning mid-session.
Prevents the stop hook from writing an unnecessary pending-capture.md entry
at session end for capture that was already handled during the session.

Exit codes: 0 always (non-blocking helper).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if block.get("type") == "text"
        )
    return ""


def main():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        # 4 levels up: mark_voluntary_seen.py → hooks/ → learn/ → skills/ → plugin root
        plugin_root = str(Path(__file__).resolve().parent.parent.parent.parent)

    rules_source = Path(plugin_root) / "skills" / "learn" / "vorbit-learning-rules.md"
    if not rules_source.exists():
        sys.exit(0)

    try:
        rules_text = rules_source.read_text()
    except Exception:
        sys.exit(0)

    # Read voluntary keywords from HTML comment
    match = re.search(r"<!--\s*voluntary-keywords:\s*(.*?)\s*-->", rules_text)
    if not match:
        sys.exit(0)

    phrases = [p.strip() for p in match.group(1).split(",") if p.strip()]
    if not phrases:
        sys.exit(0)

    voluntary_pattern = "|".join(re.escape(p) for p in phrases)

    # Get project root
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        project_root = result.stdout.strip() if result.returncode == 0 else os.getcwd()
    except Exception:
        project_root = os.getcwd()

    # Find the current session transcript
    project_slug = project_root.replace("/", "-")
    sessions_dir = Path.home() / ".claude" / "projects" / project_slug

    try:
        transcripts = sorted(
            sessions_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except Exception:
        sys.exit(0)

    if not transcripts:
        sys.exit(0)

    transcript_path = transcripts[0]
    session_id = transcript_path.stem
    seen_file = Path.home() / ".claude" / "rules" / ".seen-correction-sessions"

    # Load transcript
    messages = []
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        sys.exit(0)

    # Find all voluntary-keyword user messages
    matching_indices = []
    for idx, msg in enumerate(messages):
        if msg.get("type") != "user":
            continue
        text = extract_text(msg.get("message", {}).get("content", ""))
        if not text or len(text) > 500:
            continue
        if "<teammate-message" in text:
            continue
        if re.search(voluntary_pattern, text, re.IGNORECASE):
            matching_indices.append(idx)

    if not matching_indices:
        sys.exit(0)

    # Load already-seen fv entries for this session
    seen = set()
    try:
        with open(seen_file) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 3 and parts[0] == session_id and parts[1] == "fv":
                    try:
                        seen.add(int(parts[2]))
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass

    # Mark unseen voluntary messages as seen
    new_indices = [i for i in matching_indices if i not in seen]
    if new_indices:
        seen_file.parent.mkdir(parents=True, exist_ok=True)
        with open(seen_file, "a") as f:
            for idx in new_indices:
                f.write(f"{session_id}\tfv\t{idx}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
