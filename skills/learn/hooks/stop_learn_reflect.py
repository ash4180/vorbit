#!/usr/bin/env python3
"""Stop hook - detects correction/voluntary keywords and extracts self-discovered learnings.

Exit codes: 0 = end session normally (always).
Reads all config from vorbit-learning-rules.md — nothing hardcoded.
Per-learning dedup: SEEN_FILE stores session_id TAB flow TAB msg_index.
Flows 1 and 1b write context to pending-capture.md for the next session to process.
Flow 2 writes classified learnings directly to unprocessed-corrections.md.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def extract_text(content):
    """Extract plain text from message content (string or array of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if block.get("type") == "text"
        )
    return ""


def read_comment(rules_source_text, comment_name):
    """Read value from <!-- name: value --> comment in file text."""
    match = re.search(rf"<!--\s*{re.escape(comment_name)}:\s*(.*?)\s*-->", rules_source_text)
    return match.group(1) if match else ""


def load_transcript(transcript_path) -> list[dict[str, Any]]:
    """Load JSONL transcript, skip invalid lines."""
    messages: list[dict[str, Any]] = []
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
        pass
    return messages


def load_seen(seen_file, session_id, flow):
    """Return set of message indices already captured for this session+flow."""
    seen = set()
    try:
        with open(seen_file) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 3 and parts[0] == session_id and parts[1] == flow:
                    try:
                        seen.add(int(parts[2]))
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return seen


def mark_seen(seen_file, session_id, flow, indices):
    """Append new seen entries."""
    Path(seen_file).parent.mkdir(parents=True, exist_ok=True)
    with open(seen_file, "a") as f:
        for idx in indices:
            f.write(f"{session_id}\t{flow}\t{idx}\n")


def build_context(messages, indices):
    """Build context block: preceding assistant + user message + following assistant."""
    lines = []
    for idx in indices:
        if idx > 0 and messages[idx - 1].get("message", {}).get("role") == "assistant":
            text = extract_text(messages[idx - 1].get("message", {}).get("content", ""))[:200]
            lines.append(f"A: [{text}]")
        text = extract_text(messages[idx].get("message", {}).get("content", ""))
        lines.append(f"USER: {text}")
        if idx + 1 < len(messages) and messages[idx + 1].get("message", {}).get("role") == "assistant":
            text = extract_text(messages[idx + 1].get("message", {}).get("content", ""))[:200]
            lines.append(f"A: [{text}]")
        lines.append("")
    return "\n".join(lines)


def write_pending(pending_file, project_root, directive_tag, directive_msg, context):
    """Append a capture block to pending-capture.md for the next session to process."""
    p = Path(pending_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%d %b %Y")
    block = (
        f"## [{directive_tag}] | Project: {project_root} | {timestamp}\n"
        f"{directive_msg}\n\n"
        f"{context}\n"
        "---\n\n"
    )
    if not p.exists():
        p.write_text(
            "# Pending Captures\n\n"
            "**Action required:** The stop hook wrote unprocessed captures below.\n"
            "Run the appropriate learn skill flow for each block, then delete this file.\n\n"
            "---\n\n"
        )
    with open(p, "a") as f:
        f.write(block)


def main():
    # Consume stdin (stop hook protocol)
    sys.stdin.read()

    rules_dir = Path.home() / ".claude" / "rules"
    rules_file = rules_dir / "vorbit-learning.md"
    rules_marker = "vorbit-learning-rules"

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        # 4 levels up: stop_learn_reflect.py → hooks/ → learn/ → skills/ → plugin root
        plugin_root = str(Path(__file__).resolve().parent.parent.parent.parent)

    rules_source = Path(plugin_root) / "skills" / "learn" / "vorbit-learning-rules.md"
    pending_file = rules_dir / "pending-capture.md"
    seen_file = rules_dir / ".seen-correction-sessions"

    if not rules_source.exists():
        sys.exit(0)

    # Read rules source text once
    try:
        rules_text = rules_source.read_text()
    except Exception:
        sys.exit(0)

    # --- One-Time Setup: symlink rules file into ~/.claude/rules/ ---
    try:
        content = rules_file.read_text() if rules_file.exists() else ""
        if rules_marker not in content:
            rules_dir.mkdir(parents=True, exist_ok=True)
            if rules_file.exists() or rules_file.is_symlink():
                rules_file.unlink()
            rules_file.symlink_to(rules_source)
    except Exception:
        pass

    # --- Get project root ---
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True
        )
        project_root = result.stdout.strip() if result.returncode == 0 else os.getcwd()
    except Exception:
        project_root = os.getcwd()

    # --- Skip during active loop ---
    loop_state_path = Path(project_root) / ".claude" / ".loop-state.json"
    try:
        if loop_state_path.exists():
            loop_state = json.loads(loop_state_path.read_text())
            if loop_state.get("active") is True:
                sys.exit(0)
    except Exception:
        pass

    # --- Locate transcript ---
    project_slug = project_root.replace("/", "-")
    sessions_dir = Path.home() / ".claude" / "projects" / project_slug

    try:
        transcripts = sorted(
            sessions_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
    except Exception:
        sys.exit(0)

    if not transcripts:
        sys.exit(0)

    transcript_path = transcripts[0]
    session_id = transcript_path.stem

    messages = load_transcript(transcript_path)
    if not messages:
        sys.exit(0)

    # --- FLOW 1: Correction keyword detection ---
    # Per-learning dedup: session_id TAB f1 TAB msg_index
    keywords_csv = read_comment(rules_text, "correction-keywords")
    if keywords_csv:
        keywords = [k.strip() for k in keywords_csv.split(",") if k.strip()]
        keyword_pattern = r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b"

        all_matching = []
        for idx, msg in enumerate(messages):
            if msg.get("type") != "user":
                continue
            text = extract_text(msg.get("message", {}).get("content", ""))
            if not text or len(text) > 500:
                continue
            if "<teammate-message" in text:
                continue
            if re.search(keyword_pattern, text, re.IGNORECASE):
                all_matching.append(idx)

        seen_f1 = load_seen(seen_file, session_id, "f1")
        new_indices = [i for i in all_matching if i not in seen_f1]

        if new_indices:
            context = build_context(messages, new_indices)
            write_pending(
                pending_file,
                project_root,
                "VORBIT:CORRECTION-CAPTURE",
                "Stop hook found correction keywords. "
                "Run the Stop-Hook Correction Flow from vorbit-learning-rules.md.",
                context,
            )
            mark_seen(seen_file, session_id, "f1", new_indices)
            sys.exit(0)

    # --- FLOW 1b: Voluntary keyword detection ---
    # Per-learning dedup: session_id TAB fv TAB msg_index
    voluntary_csv = read_comment(rules_text, "voluntary-keywords")
    if voluntary_csv:
        phrases = [p.strip() for p in voluntary_csv.split(",") if p.strip()]
        voluntary_pattern = "|".join(re.escape(p) for p in phrases)

        all_voluntary = []
        for idx, msg in enumerate(messages):
            if msg.get("type") != "user":
                continue
            text = extract_text(msg.get("message", {}).get("content", ""))
            if not text or len(text) > 500:
                continue
            if "<teammate-message" in text:
                continue
            if re.search(voluntary_pattern, text, re.IGNORECASE):
                all_voluntary.append(idx)

        seen_fv = load_seen(seen_file, session_id, "fv")
        new_voluntary = [i for i in all_voluntary if i not in seen_fv]

        if new_voluntary:
            context = build_context(messages, new_voluntary)
            write_pending(
                pending_file,
                project_root,
                "VORBIT:VOLUNTARY-CAPTURE",
                "Stop hook found voluntary capture keywords. "
                "Run the Stop-Hook Voluntary Capture Flow from vorbit-learning-rules.md.",
                context,
            )
            mark_seen(seen_file, session_id, "fv", new_voluntary)
            sys.exit(0)

    # --- FLOW 2: Self-discovered learning extraction ---
    # Per-learning dedup: session_id TAB f2 TAB msg_index
    fields_def = read_comment(rules_text, "learning-fields")
    if not fields_def:
        sys.exit(0)

    field_names = [f.strip() for f in fields_def.split(",")]
    if len(field_names) < 3:
        sys.exit(0)

    f1_label = field_names[0] + ": "
    f2_label = field_names[1] + ": "
    f3_label = field_names[2] + ": "

    seen_f2 = load_seen(seen_file, session_id, "f2")
    learnings = []

    for idx, msg in enumerate(messages):
        if msg.get("type") != "assistant":
            continue
        if idx in seen_f2:
            continue
        content = msg.get("message", {}).get("content", "")
        texts = []
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
        elif isinstance(content, str):
            texts = [content]

        for text in texts:
            if f1_label in text and f2_label in text and f3_label in text:
                root_cause = text.split(f1_label)[1].split("\n")[0].strip()
                rule = text.split(f2_label)[1].split("\n")[0].strip()
                dest = text.split(f3_label)[1].split("\n")[0].strip()
                learnings.append({"idx": idx, "root_cause": root_cause, "rule": rule, "dest": dest})
                break

    if not learnings:
        sys.exit(0)

    output_file = rules_dir / "unprocessed-corrections.md"
    mark_seen(seen_file, session_id, "f2", [entry["idx"] for entry in learnings])

    learning_blocks = []
    for entry in learnings:
        title = entry["root_cause"].split(".")[0][:80]
        block = (
            f"## {title} [msg:{entry['idx']}]\n"
            f"**Root cause:** {entry['root_cause']}\n"
            f"**Rule:** {entry['rule']}\n"
            f"**Destination:** {entry['dest']}"
        )
        learning_blocks.append(block)

    learnings_text = "\n\n".join(learning_blocks)
    timestamp = datetime.now().strftime("%d %b %Y")

    rules_dir.mkdir(parents=True, exist_ok=True)
    if not output_file.exists():
        output_file.write_text(
            "# Unprocessed Session Corrections\n\n"
            "**Action required:** Route each entry to its destination file.\n"
            "Check existing rules files before writing — append to matching topic\n"
            "files, never create duplicates. Use the absolute project path in each\n"
            "block header for routing. Delete this file after processing.\n\n"
            "---\n\n"
        )

    with open(output_file, "a") as f:
        f.write(
            f"## Session: {session_id} | Project: {project_root} | {timestamp}\n\n"
            f"{learnings_text}\n\n"
            "---\n\n"
        )

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
