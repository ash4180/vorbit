#!/usr/bin/env python3
"""Stop hook - detects correction/voluntary keywords in session transcripts.

Exit codes: 0 = end session normally (always).
Reads all config from vorbit-learning-rules.md — nothing hardcoded.
Per-learning dedup: SEEN_FILE stores session_id TAB flow TAB msg_index.
Writes structured Obsidian notes with rich context and lightweight pointers
to pending-capture.md for the next session to process.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

OBSIDIAN_VAULT = Path.home() / "Projects" / "Thinking-Labs"
OBSIDIAN_CLAUDE_DIR = OBSIDIAN_VAULT / "claude"


def extract_text(content: Any) -> str:
    """Extract plain text from message content (string or array of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if block.get("type") == "text"
        )
    return ""


def read_comment(rules_source_text: str, comment_name: str) -> str:
    """Read value from <!-- name: value --> comment in file text."""
    match = re.search(rf"<!--\s*{re.escape(comment_name)}:\s*(.*?)\s*-->", rules_source_text)
    return match.group(1) if match else ""


def load_transcript(transcript_path: Path) -> list[dict[str, Any]]:
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


def load_seen(seen_file: Path, session_id: str, flow: str) -> set[int]:
    """Return set of message indices already captured for this session+flow."""
    seen: set[int] = set()
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


def mark_seen(seen_file: Path, session_id: str, flow: str, indices: list[int]) -> None:
    """Append new seen entries."""
    Path(seen_file).parent.mkdir(parents=True, exist_ok=True)
    with open(seen_file, "a") as f:
        for idx in indices:
            f.write(f"{session_id}\t{flow}\t{idx}\n")


def slugify(text: str, max_len: int = 50) -> str:
    """Convert text to a URL-safe slug for filenames."""
    slug: str = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_len].rstrip("-")


def build_context(messages: list[dict[str, Any]], indices: list[int]) -> dict[str, str]:
    """Build structured context: what agent was doing, what user corrected, how agent fixed it.

    Returns dict with keys: before, problem, diagnosis, resolution, full_context.
    - before: assistant messages before the correction (what went wrong)
    - problem: the user's correction message(s)
    - diagnosis: first assistant message after correction (identifies the issue)
    - resolution: last assistant message after correction (confirms the fix)
    - full_context: full chronological context for the Obsidian note
    """
    max_chars: int = 500
    max_surrounding: int = 3

    all_before: list[str] = []
    all_problem: list[str] = []
    all_after: list[str] = []
    full_lines: list[str] = []

    for idx in indices:
        # Search backward for up to max_surrounding assistant messages
        found_before: list[str] = []
        for i in range(idx - 1, -1, -1):
            entry: dict[str, Any] = messages[i]
            if entry.get("type") == "assistant":
                full: str = extract_text(entry.get("message", {}).get("content", ""))
                if full.strip():
                    found_before.append(full[:max_chars])
                    if len(found_before) >= max_surrounding:
                        break

        # Add in chronological order
        for text in reversed(found_before):
            all_before.append(text)
            full_lines.append(f"A: [{text}]")

        user_entry: dict[str, Any] = messages[idx]
        user_text: str = extract_text(user_entry.get("message", {}).get("content", ""))
        all_problem.append(user_text)
        full_lines.append(f"USER: {user_text}")

        # Search forward for up to max_surrounding assistant messages
        found_after_texts: list[str] = []
        for i in range(idx + 1, len(messages)):
            entry = messages[i]
            if entry.get("type") == "assistant":
                full = extract_text(entry.get("message", {}).get("content", ""))
                if full.strip():
                    found_after_texts.append(full[:max_chars])
                    full_lines.append(f"A: [{full[:max_chars]}]")
                    if len(found_after_texts) >= max_surrounding:
                        break
        all_after.extend(found_after_texts)
        full_lines.append("")

    # Diagnosis = first assistant response after correction (usually identifies the issue)
    # Resolution = last assistant response after correction (usually confirms the fix)
    diagnosis: str = all_after[0] if all_after else ""
    resolution: str = all_after[-1] if all_after else ""

    return {
        "before": "\n".join(all_before),
        "problem": "\n".join(all_problem),
        "diagnosis": diagnosis,
        "resolution": resolution,
        "full_context": "\n".join(full_lines),
    }


def get_project_name(project_root: str) -> str:
    """Extract project name from absolute path."""
    return Path(project_root).name


def write_obsidian_note(
    project_root: str,
    capture_type: str,
    user_messages: list[str],
    context: dict[str, str],
) -> str:
    """Write a structured correction note to Obsidian vault. Returns relative path within vault.

    context dict has keys: before, problem, diagnosis, resolution, full_context.
    """
    project_name: str = get_project_name(project_root)
    date_str: str = datetime.now().strftime("%Y-%m-%d")

    # Use first user message for slug and title
    first_msg: str = user_messages[0] if user_messages else "correction"
    slug: str = slugify(first_msg)
    if not slug:
        slug = "correction"
    filename: str = f"{date_str}-{slug}.md"

    note_dir: Path = OBSIDIAN_CLAUDE_DIR / "projects" / project_name
    note_dir.mkdir(parents=True, exist_ok=True)

    note_path: Path = note_dir / filename
    # Handle duplicate filenames
    counter: int = 1
    while note_path.exists():
        filename = f"{date_str}-{slug}-{counter}.md"
        note_path = note_dir / filename
        counter += 1

    relative_path: str = f"claude/projects/{project_name}/{filename}"

    # Title: clean first message, capped
    title: str = first_msg[:100].strip()

    # Extract structured sections from context
    problem: str = context.get("problem", chr(10).join(user_messages))
    diagnosis: str = context.get("diagnosis", "")
    resolution: str = context.get("resolution", "")
    before: str = context.get("before", "")
    full_context: str = context.get("full_context", "")

    # Build context sections
    what_agent_did: str = before if before else "_No preceding context._"
    agent_diagnosis: str = diagnosis if diagnosis else "_No diagnosis captured._"
    agent_fix: str = resolution if resolution else "_No fix captured._"

    note_content: str = f"""---
date: {date_str}
project: {project_name}
project_path: {project_root}
capture_type: {capture_type}
root_cause: ""
status: pending
rule: ""
routed_to: ""
tags: [{project_name}]
---

# {title}

## Conversation Context

**User said:**
{problem}

**What agent did before correction:**
{what_agent_did}

**What agent found after correction:**
{agent_diagnosis}

**How agent fixed it:**
{agent_fix}

## Root Cause Analysis
_Agent: analyze the context above — why did this happen? Classify as tool-behavior / knowledge / claude-md / agent-mistake / user-preference / skill / script / general._

## Suggested Rule
_Agent: write a concise imperative rule (commit-message style) ready to add to the destination file._

## Destination
_Agent: which file should this go to? Project-specific (.claude/rules/) or universal (~/.claude/rules/)?_

## Raw Transcript
{full_context}
"""

    note_path.write_text(note_content)
    return relative_path


def ensure_dataview_index() -> None:
    """Ensure the Dataview-based corrections index exists."""
    index_path: Path = OBSIDIAN_CLAUDE_DIR / "_corrections-index.md"
    if index_path.exists():
        return
    index_path.parent.mkdir(parents=True, exist_ok=True)
    (OBSIDIAN_CLAUDE_DIR / "universal").mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "# Corrections Index\n\n"
        "Auto-generated by vorbit learn stop hook. Live query via Dataview.\n\n"
        "```dataview\n"
        "TABLE date, project, capture_type as Type, status, rule\n"
        'FROM "claude/projects" OR "claude/universal"\n'
        "WHERE capture_type\n"
        "SORT date DESC\n"
        "```\n"
    )


def write_pending(
    pending_file: Path,
    rules_dir: Path,
    project_root: str,
    directive_tag: str,
    obsidian_path: str,
) -> None:
    """Write a lightweight pointer to pending-capture.md in Obsidian vault.

    Also ensures a symlink exists in rules_dir so Claude Code auto-loads it.
    """
    p = Path(pending_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    timestamp: str = datetime.now().strftime("%d %b %Y")
    full_note_path: str = str(OBSIDIAN_VAULT / obsidian_path)
    block: str = (
        f"## [{directive_tag}] | Project: {project_root} | {timestamp}\n"
        f"Full context saved to Obsidian: {obsidian_path}\n"
        f"Read the note at {full_note_path} for rich context before classifying.\n\n"
        "---\n\n"
    )
    if not p.exists():
        p.write_text(
            "# Pending Captures\n\n"
            "**Action required:** Read the linked Obsidian notes for full context.\n"
            "Run the appropriate learn skill flow for each block, then delete this file.\n\n"
            "---\n\n"
        )
    with open(p, "a") as f:
        f.write(block)

    # Ensure symlink in rules dir for auto-loading
    pending_link: Path = rules_dir / "pending-capture.md"
    try:
        if not pending_link.exists() and not pending_link.is_symlink():
            pending_link.symlink_to(p)
    except Exception:
        pass


def setup_symlinks(rules_dir: Path, rules_source: Path, rules_marker: str) -> None:
    """One-time setup: symlink rules and index into ~/.claude/rules/."""
    rules_file: Path = rules_dir / "vorbit-learning.md"
    try:
        content: str = rules_file.read_text() if rules_file.exists() else ""
        if rules_marker not in content:
            rules_dir.mkdir(parents=True, exist_ok=True)
            if rules_file.exists() or rules_file.is_symlink():
                rules_file.unlink()
            rules_file.symlink_to(rules_source)
    except Exception:
        pass

    # Ensure Dataview index exists in Obsidian vault
    try:
        ensure_dataview_index()
    except Exception:
        pass

    # Symlink pending-capture.md from Obsidian into rules dir for auto-loading
    pending_source: Path = OBSIDIAN_CLAUDE_DIR / "pending-capture.md"
    pending_link: Path = rules_dir / "pending-capture.md"
    try:
        if pending_source.exists() and not pending_link.exists():
            pending_link.symlink_to(pending_source)
        elif pending_link.is_symlink() and not pending_source.exists():
            # Source was deleted (agent processed it), clean up stale symlink
            pending_link.unlink()
    except Exception:
        pass


def scan_keywords(
    messages: list[dict[str, Any]],
    pattern: str,
) -> list[int]:
    """Scan user messages for keyword matches. Returns matching message indices."""
    matching: list[int] = []
    for idx, msg in enumerate(messages):
        if msg.get("type") != "user":
            continue
        text: str = extract_text(msg.get("message", {}).get("content", ""))
        if not text or len(text) > 500:
            continue
        if "<teammate-message" in text:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            matching.append(idx)
    return matching


def main() -> None:
    # Consume stdin (stop hook protocol)
    sys.stdin.read()

    rules_dir: Path = Path.home() / ".claude" / "rules"
    rules_marker: str = "vorbit-learning-rules"

    plugin_root: str = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        # 4 levels up: stop_learn_reflect.py → hooks/ → learn/ → skills/ → plugin root
        plugin_root = str(Path(__file__).resolve().parent.parent.parent.parent)

    rules_source: Path = Path(plugin_root) / "skills" / "learn" / "vorbit-learning-rules.md"
    pending_file: Path = OBSIDIAN_CLAUDE_DIR / "pending-capture.md"
    seen_file: Path = rules_dir / ".seen-correction-sessions"

    if not rules_source.exists():
        sys.exit(0)

    # Read rules source text once
    try:
        rules_text: str = rules_source.read_text()
    except Exception:
        sys.exit(0)

    # --- One-Time Setup ---
    setup_symlinks(rules_dir, rules_source, rules_marker)

    # --- Get project root ---
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True
        )
        project_root: str = result.stdout.strip() if result.returncode == 0 else os.getcwd()
    except Exception:
        project_root = os.getcwd()

    # --- Skip during active loop ---
    loop_state_path: Path = Path(project_root) / ".claude" / ".loop-state.json"
    try:
        if loop_state_path.exists():
            loop_state: dict[str, Any] = json.loads(loop_state_path.read_text())
            if loop_state.get("active") is True:
                sys.exit(0)
    except Exception:
        pass

    # --- Locate transcript ---
    project_slug: str = project_root.replace("/", "-")
    sessions_dir: Path = Path.home() / ".claude" / "projects" / project_slug

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

    transcript_path: Path = transcripts[0]
    session_id: str = transcript_path.stem

    messages: list[dict[str, Any]] = load_transcript(transcript_path)
    if not messages:
        sys.exit(0)

    project_name: str = get_project_name(project_root)

    # --- FLOW 1: Correction keyword detection ---
    keywords_csv: str = read_comment(rules_text, "correction-keywords")
    if keywords_csv:
        keywords: list[str] = [k.strip() for k in keywords_csv.split(",") if k.strip()]
        keyword_pattern: str = r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b"

        all_matching: list[int] = scan_keywords(messages, keyword_pattern)
        seen_f1: set[int] = load_seen(seen_file, session_id, "f1")
        new_indices: list[int] = [i for i in all_matching if i not in seen_f1]

        if new_indices:
            context: dict[str, str] = build_context(messages, new_indices)
            user_texts: list[str] = []
            for i in new_indices:
                entry: dict[str, Any] = messages[i]
                text: str = extract_text(entry.get("message", {}).get("content", ""))
                user_texts.append(text)

            obsidian_path: str = write_obsidian_note(
                project_root, "correction", user_texts, context,
            )
            write_pending(
                pending_file, rules_dir, project_root,
                "VORBIT:CORRECTION-CAPTURE", obsidian_path,
            )
            mark_seen(seen_file, session_id, "f1", new_indices)

    # --- FLOW 1b: Voluntary keyword detection ---
    # No early exit — both flows run independently
    voluntary_csv: str = read_comment(rules_text, "voluntary-keywords")
    if voluntary_csv:
        phrases: list[str] = [p.strip() for p in voluntary_csv.split(",") if p.strip()]
        voluntary_pattern: str = r"\b(" + "|".join(re.escape(p) for p in phrases) + r")\b"

        all_voluntary: list[int] = scan_keywords(messages, voluntary_pattern)
        seen_fv: set[int] = load_seen(seen_file, session_id, "fv")
        new_voluntary: list[int] = [i for i in all_voluntary if i not in seen_fv]

        if new_voluntary:
            context = build_context(messages, new_voluntary)
            user_texts = []
            for i in new_voluntary:
                entry = messages[i]
                text = extract_text(entry.get("message", {}).get("content", ""))
                user_texts.append(text)

            obsidian_path = write_obsidian_note(
                project_root, "voluntary", user_texts, context,
            )
            write_pending(
                pending_file, rules_dir, project_root,
                "VORBIT:VOLUNTARY-CAPTURE", obsidian_path,
            )
            mark_seen(seen_file, session_id, "fv", new_voluntary)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
