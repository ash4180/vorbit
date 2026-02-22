"""Tests for mark_voluntary_seen.py — mid-session dedup helper for Voluntary Capture."""

import json
from pathlib import Path

from hooks.tests.conftest import PLUGIN_ROOT, SCRIPTS

HOOK = SCRIPTS["mark_voluntary_seen"]


# ---------------------------------------------------------------------------
# Helpers (same pattern as test_stop_learn_reflect.py)
# ---------------------------------------------------------------------------

def _run_mvs(run_hook, project, plugin_root=None):
    """Run mark_voluntary_seen.py with isolated HOME and CLAUDE_PLUGIN_ROOT."""
    env = {
        "HOME": str(project["home"]),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root or PLUGIN_ROOT),
    }
    return run_hook(HOOK, stdin="", env_overrides=env, cwd=project["path"])


def _seen_file(project):
    return project["home"] / ".claude" / "rules" / ".seen-correction-sessions"


def _write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _user(text, sid, ts):
    return {"type": "user", "message": {"role": "user", "content": text}, "sessionId": sid, "timestamp": ts}


def _asst(text, sid, ts):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}, "sessionId": sid, "timestamp": ts}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_marks_voluntary_message_as_seen(test_project, run_hook):
    """Happy path: 'remember this' in transcript → seen file written with fv entry."""
    sid = "test-mvs-happy"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user("We always use sqlite3. Remember this.", sid, "2026-02-22T10:00:00Z"),
        _asst("Noted, sqlite3 it is.", sid, "2026-02-22T10:01:00Z"),
    ])

    exit_code, _, _ = _run_mvs(run_hook, test_project)

    assert exit_code == 0
    seen = _seen_file(test_project)
    assert seen.exists()
    content = seen.read_text()
    assert f"{sid}\tfv\t0" in content


def test_no_transcript_exits_0(test_project, run_hook):
    """No transcript in sessions dir → exits 0, no seen file created."""
    exit_code, _, _ = _run_mvs(run_hook, test_project)

    assert exit_code == 0
    assert not _seen_file(test_project).exists()


def test_no_voluntary_keywords_exits_0(test_project, run_hook):
    """Transcript with no voluntary keywords → exits 0, no seen file written."""
    sid = "test-mvs-clean"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user("Fix the login page.", sid, "2026-02-22T10:00:00Z"),
        _asst("Fixed.", sid, "2026-02-22T10:01:00Z"),
    ])

    exit_code, _, _ = _run_mvs(run_hook, test_project)

    assert exit_code == 0
    assert not _seen_file(test_project).exists()


def test_already_seen_not_duplicated(test_project, run_hook):
    """Index already in seen file → not written again."""
    sid = "test-mvs-dedup"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user("Save this: always use RS256 for JWT.", sid, "2026-02-22T10:00:00Z"),
        _asst("Noted.", sid, "2026-02-22T10:01:00Z"),
    ])

    seen = _seen_file(test_project)
    seen.parent.mkdir(parents=True, exist_ok=True)
    seen.write_text(f"{sid}\tfv\t0\n")

    exit_code, _, _ = _run_mvs(run_hook, test_project)

    assert exit_code == 0
    # Still only one entry — no duplicate written
    lines = [ln for ln in seen.read_text().splitlines() if ln.strip()]
    assert len(lines) == 1


def test_invalid_plugin_root_exits_0(test_project, run_hook):
    """Missing CLAUDE_PLUGIN_ROOT → exits 0 silently."""
    sid = "test-mvs-noroot"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user("Remember this.", sid, "2026-02-22T10:00:00Z"),
    ])

    exit_code, _, _ = _run_mvs(run_hook, test_project, plugin_root=Path("/nonexistent/path"))

    assert exit_code == 0


def test_teammate_message_not_marked(test_project, run_hook):
    """Message with <teammate-message> containing voluntary keywords → not marked."""
    sid = "test-mvs-teammate"
    tag = '<teammate-message teammate_id="x">remember this pattern: always log errors</teammate-message>'
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user(tag, sid, "2026-02-22T10:00:00Z"),
        _asst("Got it.", sid, "2026-02-22T10:01:00Z"),
    ])

    exit_code, _, _ = _run_mvs(run_hook, test_project)

    assert exit_code == 0
    assert not _seen_file(test_project).exists()
