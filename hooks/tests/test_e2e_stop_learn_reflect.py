"""E2E tests for stop_learn_reflect.py — full lifecycle with real git repos.

Each test exercises the hook with JSONL transcripts and verifies:
- Pending-capture.md has Obsidian pointers (not inline context)
- Obsidian notes contain rich context with YAML frontmatter
- Corrections index is updated
- Exit codes, dedup, filtering all work correctly

HOME is overridden via env to tmp_home, so all ~/.claude/ and ~/Projects/ I/O is isolated.
"""

import json

from hooks.tests.conftest import PLUGIN_ROOT, SCRIPTS

HOOK = SCRIPTS["stop_learn_reflect"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_slr(run_hook, project, plugin_root=None):
    env = {
        "HOME": str(project["home"]),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root or PLUGIN_ROOT),
    }
    return run_hook(HOOK, stdin="", env_overrides=env, cwd=project["path"])


def _pending_file(project):
    return project["home"] / ".claude" / "rules" / "pending-capture.md"


def _seen_file(project):
    return project["home"] / ".claude" / "rules" / ".seen-correction-sessions"


def _obsidian_dir(project):
    return project["home"] / "Projects" / "Thinking-Labs" / "claude"


def _obsidian_project_dir(project):
    project_name = project["path"].resolve().name
    return _obsidian_dir(project) / "projects" / project_name


def _read_latest_obsidian_note(project):
    notes = sorted(_obsidian_project_dir(project).glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not notes:
        return ""
    return notes[0].read_text()


def _obsidian_index(project):
    return _obsidian_dir(project) / "_corrections-index.md"


def _write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _user(text, sid, ts):
    return {
        "type": "user",
        "message": {"role": "user", "content": text},
        "sessionId": sid,
        "timestamp": ts,
    }


def _asst(text, sid, ts):
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
        "sessionId": sid,
        "timestamp": ts,
    }


# ---------------------------------------------------------------------------
# E2E-1: Wrong tech assumption → exit 0, Obsidian note with context
# ---------------------------------------------------------------------------


def test_e2e_wrong_tech_assumption(test_project, run_hook):
    """Correction keyword writes pointer to pending and rich context to Obsidian note."""
    sid = "e2e1-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Add a PostgreSQL connection to config.py", sid, "2026-02-21T10:00:00Z"),
            _asst("I'll add psycopg2 for PostgreSQL connectivity.", sid, "2026-02-21T10:01:00Z"),
            _user("Wrong, this project uses SQLite not PostgreSQL", sid, "2026-02-21T10:02:00Z"),
            _asst("Fixed, switching to sqlite3 module instead.", sid, "2026-02-21T10:03:00Z"),
        ],
    )

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""

    pending = _pending_file(test_project)
    assert pending.exists()
    content = pending.read_text()
    assert "[VORBIT:CORRECTION-CAPTURE]" in content
    assert "Obsidian" in content

    note = _read_latest_obsidian_note(test_project)
    assert "Wrong, this project uses SQLite not PostgreSQL" in note
    assert "psycopg2" in note  # preceding assistant context
    assert "sqlite3" in note  # following assistant context
    # First unrelated message should NOT be in the note's Problem section directly
    # but may appear in context if within the 3-message window


# ---------------------------------------------------------------------------
# E2E-2: Nope keyword → exit 0, Obsidian note
# ---------------------------------------------------------------------------


def test_e2e_nope_keyword(test_project, run_hook):
    """'Nope' triggers correction capture with Obsidian note."""
    sid = "e2e2-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _asst("I added the feature to line 42.", sid, "2026-02-21T10:00:00Z"),
            _user("Nope, line 12", sid, "2026-02-21T10:01:00Z"),
            _asst("Fixed, moved to line 12.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    pending = _pending_file(test_project)
    assert pending.exists()
    assert "[VORBIT:CORRECTION-CAPTURE]" in pending.read_text()

    note = _read_latest_obsidian_note(test_project)
    assert "Nope, line 12" in note


# ---------------------------------------------------------------------------
# E2E-3: Multiple corrections → all captured in Obsidian
# ---------------------------------------------------------------------------


def test_e2e_multiple_corrections(test_project, run_hook):
    """Three correction keywords in one session: all in Obsidian note."""
    sid = "e2e3-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _asst("I'll use MySQL for the database.", sid, "2026-02-21T10:00:00Z"),
            _user("Wrong, we use PostgreSQL.", sid, "2026-02-21T10:01:00Z"),
            _asst("Switching to PostgreSQL.", sid, "2026-02-21T10:02:00Z"),
            _user("Still not working, check the port.", sid, "2026-02-21T10:03:00Z"),
            _asst("Fixed the port to 5432.", sid, "2026-02-21T10:04:00Z"),
            _user("Nope, the issue is in the cookie parser.", sid, "2026-02-21T10:05:00Z"),
            _asst("Found and fixed the cookie parser.", sid, "2026-02-21T10:06:00Z"),
        ],
    )

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""

    note = _read_latest_obsidian_note(test_project)
    assert "Wrong, we use PostgreSQL" in note
    assert "Still not working" in note
    assert "Nope, the issue is in the cookie parser" in note


# ---------------------------------------------------------------------------
# E2E-4: Clean session → exit 0, no stdout, no pending file
# ---------------------------------------------------------------------------


def test_e2e_clean_session(test_project, run_hook):
    """Session with no correction or voluntary keywords: exits 0, no pending file."""
    sid = "e2e4-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Please fix the login page styling.", sid, "2026-02-21T10:00:00Z"),
            _asst("I'll fix the login page styling now.", sid, "2026-02-21T10:01:00Z"),
            _user("Great, looks good.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    assert not _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-5: Continuation summary (>500 chars) → filtered, exit 0
# ---------------------------------------------------------------------------


def test_e2e_long_message_filtered(test_project, run_hook):
    """User message >500 chars with correction keywords is filtered."""
    sid = "e2e5-session"
    long_text = (
        "This session is being continued from a previous conversation. Previously the user said wrong "
        "and broken and we fixed it. The user also mentioned not working several times. This summary "
        "is very long and contains many correction keywords but should be excluded because it is a "
        "continuation summary that quotes past corrections rather than being a real correction itself. "
        "It goes on and on with more filler text to push it well past the five hundred character limit "
        "used to filter out these false positives."
    )
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user(long_text, sid, "2026-02-21T10:00:00Z"),
            _asst("Continuing from before.", sid, "2026-02-21T10:01:00Z"),
            _user("Please continue.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert not _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-6: Teammate message with keywords → filtered, exit 0
# ---------------------------------------------------------------------------


def test_e2e_teammate_message_filtered(test_project, run_hook):
    """<teammate-message> tags with correction words are filtered."""
    sid = "e2e6-session"
    tag = (
        '<teammate-message teammate_id="auditor">## Audit Complete\n'
        "✓ No issues found. wrong broken error not working.</teammate-message>"
    )
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user(tag, sid, "2026-02-21T10:00:00Z"),
            _asst("Got the audit results.", sid, "2026-02-21T10:01:00Z"),
            _user("Looks good, thanks.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert not _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-7a: Custom keyword 'oops' matches
# ---------------------------------------------------------------------------


def test_e2e_custom_keyword_matches(test_project, tmp_path, run_hook):
    """Custom rules file with 'oops' keyword triggers correction capture."""
    custom_root = tmp_path / "custom_plugin"
    rules_dir = custom_root / "skills" / "learn"
    rules_dir.mkdir(parents=True)
    (rules_dir / "vorbit-learning-rules.md").write_text(
        "# Test Rules\n"
        "<!-- correction-keywords: oops -->\n"
        "<!-- vorbit-learning-rules -->\n"
    )

    sid = "e2e7a-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _asst("Deployed to production.", sid, "2026-02-21T10:00:00Z"),
            _user("oops, that was the wrong branch", sid, "2026-02-21T10:01:00Z"),
            _asst("Rolling back.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=custom_root)

    assert exit_code == 0
    assert _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-7b: Custom keyword swapped — 'oops' no longer triggers
# ---------------------------------------------------------------------------


def test_e2e_custom_keyword_swap(test_project, tmp_path, run_hook):
    """After swapping keyword to 'broken', 'oops' no longer matches."""
    custom_root = tmp_path / "custom_plugin"
    rules_dir = custom_root / "skills" / "learn"
    rules_dir.mkdir(parents=True)
    (rules_dir / "vorbit-learning-rules.md").write_text(
        "# Test Rules\n"
        "<!-- correction-keywords: broken -->\n"
        "<!-- vorbit-learning-rules -->\n"
    )

    sid = "e2e7b-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _asst("Deployed to production.", sid, "2026-02-21T10:00:00Z"),
            _user("oops, that was the wrong branch", sid, "2026-02-21T10:01:00Z"),
            _asst("Rolling back.", sid, "2026-02-21T10:02:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=custom_root)

    assert exit_code == 0
    assert not _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-8: Loop mode active → exit 0 (skips correction capture)
# ---------------------------------------------------------------------------


def test_e2e_loop_active_skips(test_project, run_hook):
    """Active loop state file causes hook to skip entirely."""
    (test_project["path"] / ".claude").mkdir(exist_ok=True)
    (test_project["path"] / ".claude" / ".loop-state.json").write_text(
        '{"active":true,"command":"implement","iteration":2}'
    )

    sid = "e2e8-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use const not var.", sid, "2026-02-21T10:00:00Z"),
            _asst("Fixed.", sid, "2026-02-21T10:01:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert not _pending_file(test_project).exists()


# ---------------------------------------------------------------------------
# E2E-9: Per-learning dedup — second run skips via seen file
# ---------------------------------------------------------------------------


def test_e2e_session_dedup(test_project, run_hook):
    """First run captures correction; second run skips via seen file."""
    sid = "e2e9-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use SQLite not PostgreSQL.", sid, "2026-02-21T10:00:00Z"),
            _asst("Switching to SQLite.", sid, "2026-02-21T10:01:00Z"),
        ],
    )

    # First run → exits 0, pending file written
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    pending = _pending_file(test_project)
    assert pending.exists()

    # Second run — correction already in seen file → exits 0, pending unchanged
    content_before = pending.read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert pending.read_text() == content_before


# ---------------------------------------------------------------------------
# E2E-10: Multi-capture — new correction after first already captured
# ---------------------------------------------------------------------------


def test_e2e_multi_capture(test_project, run_hook):
    """Second correction at new index creates a new Obsidian note."""
    sid = "e2e10-session"
    transcript = test_project["sessions_dir"] / f"{sid}.jsonl"
    _write_jsonl(
        transcript,
        [
            _user("Set up the database.", sid, "2026-02-22T10:00:00Z"),
            _asst("Using MySQL.", sid, "2026-02-22T10:01:00Z"),
            _user("Wrong, we use PostgreSQL.", sid, "2026-02-22T10:02:00Z"),
            _asst("Switching to PostgreSQL.", sid, "2026-02-22T10:03:00Z"),
        ],
    )

    # First run: correction at idx 2
    exit_code, stdout, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert stdout.strip() == ""

    note1 = _read_latest_obsidian_note(test_project)
    assert "Wrong, we use PostgreSQL" in note1

    # Append new correction at idx 4
    with transcript.open("a") as f:
        f.write(json.dumps(_user("Nope, check the connection string.", sid, "2026-02-22T10:04:00Z")) + "\n")
        f.write(json.dumps(_asst("Fixed the connection string.", sid, "2026-02-22T10:05:00Z")) + "\n")

    # Second run: idx 2 already captured, idx 4 is new
    exit_code, stdout, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert stdout.strip() == ""

    note2 = _read_latest_obsidian_note(test_project)
    assert "Nope, check the connection string" in note2

    # Third run: all corrections captured → pending unchanged
    content_before = _pending_file(test_project).read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert _pending_file(test_project).read_text() == content_before


# ---------------------------------------------------------------------------
# E2E-11: Seen file tab-separated format verification
# ---------------------------------------------------------------------------


def test_e2e_seen_file_format(test_project, run_hook):
    """Seen file uses tab-separated format: session_id TAB flow TAB idx."""
    sid = "e2e11-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use const not var.", sid, "2026-02-22T10:00:00Z"),
            _asst("Fixed.", sid, "2026-02-22T10:01:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert _pending_file(test_project).exists()

    seen = _seen_file(test_project)
    assert seen.exists()
    first_line = seen.read_text().splitlines()[0]
    assert first_line == f"{sid}\tf1\t0"


# ---------------------------------------------------------------------------
# E2E-12: Both flows run independently (no early exit)
# ---------------------------------------------------------------------------


def test_e2e_both_flows_fire(test_project, run_hook):
    """Session with correction AND voluntary keywords → both captured."""
    sid = "e2e12-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _asst("Using JWT tokens.", sid, "2026-02-22T10:00:00Z"),
            _user("Wrong, we use sessions not JWT.", sid, "2026-02-22T10:01:00Z"),
            _asst("Switching to session-based auth.", sid, "2026-02-22T10:02:00Z"),
            _user("Remember this: sessions expire after 24h in this project.", sid, "2026-02-22T10:03:00Z"),
            _asst("Noted, 24h session expiry.", sid, "2026-02-22T10:04:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0

    content = _pending_file(test_project).read_text()
    assert "VORBIT:CORRECTION-CAPTURE" in content
    assert "VORBIT:VOLUNTARY-CAPTURE" in content

    # Both should have Obsidian notes
    notes = sorted(_obsidian_project_dir(test_project).glob("*.md"))
    assert len(notes) == 2


# ---------------------------------------------------------------------------
# E2E-13: Obsidian index grows with each capture
# ---------------------------------------------------------------------------


def test_e2e_index_tracks_captures(test_project, run_hook):
    """Dataview index is created with live query."""
    sid = "e2e13-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use SQLite.", sid, "2026-02-22T10:00:00Z"),
            _asst("Fixed.", sid, "2026-02-22T10:01:00Z"),
        ],
    )

    _run_slr(run_hook, test_project)

    index = _obsidian_index(test_project)
    assert index.exists()
    content = index.read_text()
    assert "dataview" in content
    assert "capture_type" in content
    # Obsidian note has the actual correction data
    note = _read_latest_obsidian_note(test_project)
    assert "status: pending" in note
