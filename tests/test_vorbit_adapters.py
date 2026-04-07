from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tests.conftest import (
    codex_assistant_msg,
    codex_user_msg,
    gemini_assistant_msg,
    gemini_session,
    gemini_user_msg,
    write_json,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parent.parent
CODEX_SCRIPT = ROOT / "scripts" / "vorbit-codex-cli.py"
GEMINI_SCRIPT = ROOT / "scripts" / "vorbit-gemini-cli.py"


def _run(script: Path, *, project_root: Path, transcript: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(project_root),
            "--transcript",
            str(transcript),
        ],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def test_codex_cli_capture_creates_pending_item(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))
    transcript = write_jsonl(
        temp_project / "codex-session.jsonl",
        [
            codex_assistant_msg("I'll wire PostgreSQL."),
            codex_user_msg("Wrong, this project uses SQLite."),
            codex_assistant_msg("Fixed, switching to sqlite3."),
        ],
    )

    env = os.environ.copy()
    result = _run(CODEX_SCRIPT, project_root=temp_project, transcript=transcript, env=env)

    assert result.returncode == 0
    pending_dir = Path(env["VORBIT_HOME"]) / "pending"
    pending_items = list(pending_dir.glob("*.json"))
    assert len(pending_items) == 1
    payload = json.loads(pending_items[0].read_text())
    assert payload["source_agent"] == "codex"
    assert payload["status"] == "pending"


def test_gemini_cli_capture_creates_pending_item(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))
    transcript = write_json(
        temp_project / "gemini-session.json",
        gemini_session([
            gemini_assistant_msg("I'll keep HS256."),
            gemini_user_msg("remember this: in this project we always use RS256"),
            gemini_assistant_msg("Noted."),
        ]),
    )

    env = os.environ.copy()
    result = _run(GEMINI_SCRIPT, project_root=temp_project, transcript=transcript, env=env)

    assert result.returncode == 0
    pending_dir = Path(env["VORBIT_HOME"]) / "pending"
    pending_items = list(pending_dir.glob("*.json"))
    assert len(pending_items) == 1
    payload = json.loads(pending_items[0].read_text())
    assert payload["source_agent"] == "gemini"
    assert payload["proposed_scope"] == "project-shared"
