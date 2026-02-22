#!/usr/bin/env python3
"""Shared pytest fixtures for vorbit hook script tests."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Python version guard
if sys.version_info < (3, 9):
    raise RuntimeError(f"Python 3.9+ required, got {sys.version_info.major}.{sys.version_info.minor}")

# Plugin root: conftest.py → tests/ → hooks/ → project root
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent

# Hook script paths relative to plugin root
SCRIPTS = {
    "pre_push_warning": PLUGIN_ROOT / "hooks" / "scripts" / "pre_push_warning.py",
    "post_edit_format": PLUGIN_ROOT / "hooks" / "scripts" / "post_edit_format.py",
    "post_edit_validate": PLUGIN_ROOT / "hooks" / "scripts" / "post_edit_validate.py",
    "loop_controller": PLUGIN_ROOT / "skills" / "implement-loop" / "hooks" / "loop_controller.py",
    "stop_learn_reflect": PLUGIN_ROOT / "skills" / "learn" / "hooks" / "stop_learn_reflect.py",
}


@pytest.fixture
def plugin_root():
    """Path to the plugin root directory."""
    return PLUGIN_ROOT


@pytest.fixture
def tmp_home(tmp_path):
    """Temporary HOME directory for test isolation.

    Hook scripts that call Path.home() will resolve to this directory
    when HOME is overridden in the subprocess environment.
    """
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def test_project(tmp_path, tmp_home):
    """Temporary git repo with project slug directory in tmp_home.

    Returns a dict with:
      path        - Path to the git repo
      resolved    - Resolved absolute path (macOS /tmp → /private/tmp)
      slug        - Project slug (path with / replaced by -)
      sessions_dir - tmp_home/.claude/projects/<slug>/
      home        - tmp_home path
    """
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=project, check=True)
    # Resolve to handle macOS /tmp → /private/tmp symlink
    resolved = project.resolve()
    slug = str(resolved).replace("/", "-")
    sessions_dir = tmp_home / ".claude" / "projects" / slug
    sessions_dir.mkdir(parents=True)
    return {
        "path": project,
        "resolved": resolved,
        "slug": slug,
        "sessions_dir": sessions_dir,
        "home": tmp_home,
    }


@pytest.fixture
def run_hook():
    """Run a hook script in a subprocess.

    Usage:
        exit_code, stdout, stderr = run_hook(
            script_path,
            stdin="",
            env_overrides={"HOME": str(tmp_home)},
            cwd=project_path,
        )

    Returns (exit_code: int, stdout: str, stderr: str).
    """
    def _run(script_path, stdin="", env_overrides=None, cwd=None):
        env = os.environ.copy()
        if env_overrides:
            env.update({k: str(v) for k, v in env_overrides.items()})
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(cwd) if cwd else None,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


# ---------------------------------------------------------------------------
# Transcript builders
# ---------------------------------------------------------------------------

def _user_msg(text, session_id, ts):
    """User message — content is a plain string (real Claude transcript format)."""
    return json.dumps({
        "type": "user",
        "message": {"role": "user", "content": text},
        "sessionId": session_id,
        "timestamp": ts,
    })


def _assistant_msg(text, session_id, ts):
    """Assistant message — content is array of text blocks (real Claude transcript format)."""
    return json.dumps({
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
        "sessionId": session_id,
        "timestamp": ts,
    })


def _write_transcript(path, lines):
    path.write_text("\n".join(lines) + "\n")
    return path


@pytest.fixture
def correction_transcript():
    """Transcript with a correction keyword ('Wrong') in a user message."""
    def _make(sessions_dir, session_id="test-session-abc123"):
        sid = session_id
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg("Add a PostgreSQL connection to config.py", sid, "2026-02-15T10:00:00Z"),
                _assistant_msg("I'll add psycopg2 for PostgreSQL connectivity.", sid, "2026-02-15T10:01:00Z"),
                _user_msg("Wrong, this project uses SQLite not PostgreSQL", sid, "2026-02-15T10:02:00Z"),
                _assistant_msg("Fixed, switching to sqlite3 module instead.", sid, "2026-02-15T10:03:00Z"),
                _user_msg("Looks good, thanks.", sid, "2026-02-15T10:04:00Z"),
            ],
        )
    return _make


@pytest.fixture
def clean_transcript():
    """Transcript with no correction or voluntary keywords."""
    def _make(sessions_dir, session_id="test-session-def456"):
        sid = session_id
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg("Please fix the login page styling.", sid, "2026-02-15T10:00:00Z"),
                _assistant_msg("I'll fix the login page styling now.", sid, "2026-02-15T10:01:00Z"),
                _user_msg("Great, looks good.", sid, "2026-02-15T10:02:00Z"),
            ],
        )
    return _make


@pytest.fixture
def teammate_transcript():
    """Transcript with <teammate-message> tags containing correction-like words.

    The keyword filter must NOT trigger on these — teammate audit messages
    contain words like 'wrong', 'broken', 'error' as analysis text.
    """
    def _make(sessions_dir, session_id="test-session-team123"):
        sid = session_id
        tag = (
            '<teammate-message teammate_id="auditor">## Audit Complete\n'
            '✓ No issues found. wrong broken error not working.</teammate-message>'
        )
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg(tag, sid, "2026-02-15T10:00:00Z"),
                _assistant_msg("Got the audit results.", sid, "2026-02-15T10:01:00Z"),
                _user_msg("Thanks, looks good.", sid, "2026-02-15T10:02:00Z"),
            ],
        )
    return _make


@pytest.fixture
def long_message_transcript():
    """Transcript with a long session-continuation summary containing correction keywords.

    Messages over ~500 chars must NOT trigger the keyword filter — they are
    typically session continuation summaries quoting past corrections.
    """
    def _make(sessions_dir, session_id="test-session-long456"):
        sid = session_id
        long_text = (
            "This session is being continued from a previous conversation. Previously the user said wrong "
            "and broken and we fixed it. The user also mentioned not working several times. This summary "
            "is very long and contains many correction keywords but should be excluded because it is a "
            "continuation summary that quotes past corrections rather than being a real correction itself. "
            "It goes on and on with more filler text to push it well past the five hundred character limit "
            "that we use to filter out these false positives from real corrections."
        )
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg(long_text, sid, "2026-02-15T10:00:00Z"),
                _assistant_msg("Understood, continuing from before.", sid, "2026-02-15T10:01:00Z"),
                _user_msg("Please continue with the task.", sid, "2026-02-15T10:02:00Z"),
            ],
        )
    return _make


@pytest.fixture
def voluntary_transcript():
    """Transcript with a voluntary capture keyword ('remember this')."""
    def _make(sessions_dir, session_id="test-session-vol123"):
        sid = session_id
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg(
                    "We always use sqlite3 for this project, never psycopg2. Remember this.",
                    sid, "2026-02-15T10:00:00Z",
                ),
                _assistant_msg("Noted! I'll remember that this project uses sqlite3.", sid, "2026-02-15T10:01:00Z"),
            ],
        )
    return _make


@pytest.fixture
def self_discovery_transcript():
    """Transcript with self-discovered learning fields in an assistant message.

    The stop hook's Flow 2 reads ROOT_CAUSE/RULE/DESTINATION from assistant
    messages and writes to unprocessed-corrections.md.
    """
    def _make(sessions_dir, session_id="test-session-self123"):
        sid = session_id
        learning_text = (
            "ROOT_CAUSE: The script assumed PostgreSQL but the project uses SQLite.\n"
            "RULE: Always check pyproject.toml for the database driver before adding DB code.\n"
            "DESTINATION: /Users/ash/Projects/vorbit/.claude/rules/architecture.md"
        )
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg("Fix the database connection.", sid, "2026-02-15T10:00:00Z"),
                _assistant_msg(learning_text, sid, "2026-02-15T10:01:00Z"),
            ],
        )
    return _make


@pytest.fixture
def multiple_corrections_transcript():
    """Transcript with two separate correction keywords across different user messages."""
    def _make(sessions_dir, session_id="test-session-multi789"):
        sid = session_id
        return _write_transcript(
            sessions_dir / f"{sid}.jsonl",
            [
                _user_msg("Add PostgreSQL support.", sid, "2026-02-15T10:00:00Z"),
                _assistant_msg("Adding psycopg2...", sid, "2026-02-15T10:01:00Z"),
                _user_msg("Wrong, we use SQLite.", sid, "2026-02-15T10:02:00Z"),
                _assistant_msg("OK, switching to sqlite3.", sid, "2026-02-15T10:03:00Z"),
                _user_msg("Also add Redis caching.", sid, "2026-02-15T10:04:00Z"),
                _assistant_msg("Adding redis...", sid, "2026-02-15T10:05:00Z"),
                _user_msg("Nope, we don't use Redis. Use in-memory cache.", sid, "2026-02-15T10:06:00Z"),
                _assistant_msg("Switching to functools.lru_cache.", sid, "2026-02-15T10:07:00Z"),
            ],
        )
    return _make
