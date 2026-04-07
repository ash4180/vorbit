"""Text and transcript helpers for Vorbit learning.

Vorbit normalized message format:
    {"role": "user"|"assistant", "text": "plain text content"}

All agent transcripts normalize to this shape before entering the pipeline.
Every agent (Claude, Codex, Gemini) goes through its own loader — none is the default.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_comment(text: str, comment_name: str) -> str:
    match = re.search(rf"<!--\s*{re.escape(comment_name)}:\s*(.*?)\s*-->", text)
    return match.group(1) if match else ""


def slugify(text: str, max_len: int = 64) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_len].rstrip("-")


# ---------------------------------------------------------------------------
# Normalized message helpers
# ---------------------------------------------------------------------------


def msg_text(msg: dict[str, Any]) -> str:
    """Extract plain text from a Vorbit normalized message."""
    return str(msg.get("text", ""))


def msg_role(msg: dict[str, Any]) -> str:
    """Extract role from a Vorbit normalized message."""
    return str(msg.get("role", ""))


# ---------------------------------------------------------------------------
# Transcript loaders — each normalizes to Vorbit format
# ---------------------------------------------------------------------------


def load_transcript(transcript_path: Path, *, fmt: str = "claude") -> list[dict[str, Any]]:
    """Load a transcript and normalize to Vorbit's internal message format.

    Supported formats: "claude", "codex", "gemini".
    """
    if fmt == "codex":
        return _load_codex_transcript(transcript_path)
    if fmt == "gemini":
        return _load_gemini_transcript(transcript_path)
    return _load_claude_transcript(transcript_path)


def _extract_claude_text(content: Any) -> str:
    """Extract plain text from Claude's content field (string or block array)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def _load_claude_transcript(transcript_path: Path) -> list[dict[str, Any]]:
    """Load Claude Code JSONL and normalize to Vorbit format.

    Claude stores: {"type": "user"|"assistant", "message": {"content": "..." | [{"type": "text", "text": "..."}]}}
    """
    messages: list[dict[str, Any]] = []
    try:
        with open(transcript_path) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                entry_type = entry.get("type", "")
                if entry_type not in ("user", "assistant"):
                    continue
                role = "user" if entry_type == "user" else "assistant"
                text = _extract_claude_text(entry.get("message", {}).get("content", ""))
                messages.append({"role": role, "text": text})
    except Exception:
        return []
    return messages


def _load_codex_transcript(transcript_path: Path) -> list[dict[str, Any]]:
    """Load Codex CLI JSONL and normalize to Vorbit format.

    Codex stores: {"type": "response_item", "payload": {"type": "message", "role": "user"|"assistant", "content": [{"type": "input_text"|"output_text", "text": "..."}]}}
    """
    messages: list[dict[str, Any]] = []
    try:
        with open(transcript_path) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "response_item":
                    continue
                payload = entry.get("payload", {})
                if payload.get("type") != "message":
                    continue
                role = payload.get("role", "")
                if role not in ("user", "assistant"):
                    continue
                content_blocks = payload.get("content", [])
                parts: list[str] = []
                if isinstance(content_blocks, list):
                    for block in content_blocks:
                        if not isinstance(block, dict):
                            continue
                        text = block.get("text", "") or block.get("input_text", "") or block.get("output_text", "")
                        if text:
                            parts.append(str(text))
                messages.append({"role": role, "text": "\n".join(parts)})
    except Exception:
        return []
    return messages


def _load_gemini_transcript(transcript_path: Path) -> list[dict[str, Any]]:
    """Load Gemini CLI JSON and normalize to Vorbit format.

    Gemini stores a single JSON: {"messages": [{"type": "user", "content": [{"text": "..."}]}, {"type": "gemini", "content": "plain string"}]}
    """
    messages: list[dict[str, Any]] = []
    try:
        data = json.loads(transcript_path.read_text())
    except Exception:
        return []
    raw_messages = data.get("messages", [])
    if not isinstance(raw_messages, list):
        return []
    for msg in raw_messages:
        if not isinstance(msg, dict):
            continue
        msg_type = msg.get("type", "")
        if msg_type == "user":
            role = "user"
        elif msg_type == "gemini":
            role = "assistant"
        else:
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = "\n".join(
                str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("text")
            )
        else:
            text = ""
        messages.append({"role": role, "text": text})
    return messages


# ---------------------------------------------------------------------------
# Context building — works on Vorbit normalized messages
# ---------------------------------------------------------------------------


def build_context(messages: list[dict[str, Any]], indices: list[int]) -> dict[str, str]:
    max_chars = 500
    max_surrounding = 3

    all_before: list[str] = []
    all_problem: list[str] = []
    all_after: list[str] = []
    full_lines: list[str] = []

    for idx in indices:
        found_before: list[str] = []
        for cursor in range(idx - 1, -1, -1):
            entry = messages[cursor]
            if msg_role(entry) != "assistant":
                continue
            full = msg_text(entry)
            if not full.strip():
                continue
            found_before.append(full[:max_chars])
            if len(found_before) >= max_surrounding:
                break

        for text in reversed(found_before):
            all_before.append(text)
            full_lines.append(f"A: [{text}]")

        user_text = msg_text(messages[idx])
        all_problem.append(user_text)
        full_lines.append(f"USER: {user_text}")

        found_after_texts: list[str] = []
        for cursor in range(idx + 1, len(messages)):
            entry = messages[cursor]
            if msg_role(entry) != "assistant":
                continue
            full = msg_text(entry)
            if not full.strip():
                continue
            found_after_texts.append(full[:max_chars])
            full_lines.append(f"A: [{full[:max_chars]}]")
            if len(found_after_texts) >= max_surrounding:
                break
        all_after.extend(found_after_texts)
        full_lines.append("")

    return {
        "before": "\n".join(all_before),
        "problem": "\n".join(all_problem),
        "diagnosis": all_after[0] if all_after else "",
        "resolution": all_after[-1] if all_after else "",
        "full_context": "\n".join(full_lines),
    }
