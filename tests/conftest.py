"""Shared fixtures for Vorbit core tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def temp_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=project, check=True)
    return project.resolve()


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    return path


def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


# ---------------------------------------------------------------------------
# Claude transcript fixtures (JSONL)
# ---------------------------------------------------------------------------


def claude_user_msg(text: str) -> dict:
    return {
        "type": "user",
        "message": {"role": "user", "content": text},
    }


def claude_assistant_msg(text: str) -> dict:
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


# ---------------------------------------------------------------------------
# Codex transcript fixtures (JSONL with response_item envelope)
# ---------------------------------------------------------------------------


def codex_user_msg(text: str) -> dict:
    return {
        "type": "response_item",
        "timestamp": "2026-04-06T10:00:00Z",
        "payload": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        },
    }


def codex_assistant_msg(text: str) -> dict:
    return {
        "type": "response_item",
        "timestamp": "2026-04-06T10:00:01Z",
        "payload": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": text}],
        },
    }


# ---------------------------------------------------------------------------
# Gemini transcript fixtures (single JSON with messages array)
# ---------------------------------------------------------------------------


def gemini_user_msg(text: str) -> dict:
    return {
        "type": "user",
        "content": [{"text": text}],
    }


def gemini_assistant_msg(text: str) -> dict:
    return {
        "type": "gemini",
        "content": text,
    }


def gemini_session(messages: list[dict]) -> dict:
    return {
        "sessionId": "test-session",
        "projectHash": "abc123",
        "startTime": "2026-04-06T10:00:00Z",
        "lastUpdated": "2026-04-06T10:05:00Z",
        "messages": messages,
    }
