"""E2E tests for stop_learn_reflect.py — migrated from test-e2e-stop-learn-reflect.sh.

Each test exercises the full hook lifecycle with a real git repo and JSONL transcripts.
Tests verify observable output (files written, exit codes, stdout content) rather than
just exit codes alone.

HOME is overridden via env to tmp_home, so all ~/.claude/ I/O is isolated.
"""

import json

from hooks.tests.conftest import PLUGIN_ROOT, SCRIPTS

HOOK = SCRIPTS["stop_learn_reflect"]

DIRECTIVE = (
    "[VORBIT:CORRECTION-CAPTURE] Stop hook found correction keywords. "
    "Run the Stop-Hook Correction Flow from vorbit-learning-rules.md."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_slr(run_hook, project, plugin_root=None):
    env = {
        "HOME": str(project["home"]),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root or PLUGIN_ROOT),
    }
    return run_hook(HOOK, stdin="", env_overrides=env, cwd=project["path"])


def _output_file(project):
    return project["home"] / ".claude" / "rules" / "unprocessed-corrections.md"


def _seen_file(project):
    return project["home"] / ".claude" / "rules" / ".seen-correction-sessions"


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
# E2E-1: Wrong tech assumption → exit 2, directive + context in stdout
# ---------------------------------------------------------------------------


def test_e2e_wrong_tech_assumption(test_project, run_hook):
    """Correction keyword triggers exit 2 with directive, context windows around correction."""
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

    assert exit_code == 2
    assert stdout.splitlines()[0] == DIRECTIVE
    assert "Wrong, this project uses SQLite not PostgreSQL" in stdout
    assert "psycopg2" in stdout  # preceding assistant context
    assert "sqlite3" in stdout  # following assistant context
    assert "Add a PostgreSQL connection" not in stdout  # unrelated first message excluded

    # Flow 1 must NOT write to unprocessed-corrections.md
    content = _output_file(test_project).read_text() if _output_file(test_project).exists() else ""
    assert "Session:" not in content


# ---------------------------------------------------------------------------
# E2E-2: Nope keyword → exit 2, directive present
# ---------------------------------------------------------------------------


def test_e2e_nope_keyword(test_project, run_hook):
    """'Nope' triggers correction capture, exits 2 with directive as first line."""
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

    assert exit_code == 2
    assert stdout.splitlines()[0] == DIRECTIVE


# ---------------------------------------------------------------------------
# E2E-3: Multiple corrections → all captured in stdout
# ---------------------------------------------------------------------------


def test_e2e_multiple_corrections(test_project, run_hook):
    """Three correction keywords in one session: all appear in stdout, output file stays clean."""
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

    assert exit_code == 2
    assert "Wrong, we use PostgreSQL" in stdout
    assert "Still not working" in stdout
    assert "Nope, the issue is in the cookie parser" in stdout

    content = _output_file(test_project).read_text() if _output_file(test_project).exists() else ""
    assert "Session:" not in content


# ---------------------------------------------------------------------------
# E2E-4: Clean session → exit 0, no stdout
# ---------------------------------------------------------------------------


def test_e2e_clean_session(test_project, run_hook):
    """Session with no correction or voluntary keywords: exits 0 with empty stdout."""
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


# ---------------------------------------------------------------------------
# E2E-5: Continuation summary (>500 chars) → filtered, exit 0
# ---------------------------------------------------------------------------


def test_e2e_long_message_filtered(test_project, run_hook):
    """User message >500 chars with correction keywords is filtered as a continuation summary."""
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


# ---------------------------------------------------------------------------
# E2E-6: Teammate message with keywords → filtered, exit 0
# ---------------------------------------------------------------------------


def test_e2e_teammate_message_filtered(test_project, run_hook):
    """<teammate-message> tags with correction words are filtered; hook exits 0."""
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
        "<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->\n"
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

    assert exit_code == 2


# ---------------------------------------------------------------------------
# E2E-7b: Custom keyword swapped — 'oops' no longer triggers
# ---------------------------------------------------------------------------


def test_e2e_custom_keyword_swap(test_project, tmp_path, run_hook):
    """After swapping keyword to 'broken', 'oops' in transcript no longer matches."""
    custom_root = tmp_path / "custom_plugin"
    rules_dir = custom_root / "skills" / "learn"
    rules_dir.mkdir(parents=True)
    # Only "broken" — "oops" must not match
    (rules_dir / "vorbit-learning-rules.md").write_text(
        "# Test Rules\n"
        "<!-- correction-keywords: broken -->\n"
        "<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->\n"
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


# ---------------------------------------------------------------------------
# E2E-8: Loop mode active → exit 0 (skips correction capture)
# ---------------------------------------------------------------------------


def test_e2e_loop_active_skips(test_project, run_hook):
    """Active loop state file causes hook to skip correction capture entirely."""
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


# ---------------------------------------------------------------------------
# E2E-9: Per-learning dedup — second run on same correction exits 0
# ---------------------------------------------------------------------------


def test_e2e_session_dedup(test_project, run_hook):
    """First run captures correction (exits 2); second run skips via seen file (exits 0)."""
    sid = "e2e9-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use SQLite not PostgreSQL.", sid, "2026-02-21T10:00:00Z"),
            _asst("Switching to SQLite.", sid, "2026-02-21T10:01:00Z"),
        ],
    )

    # First run → exits 2, output file NOT written
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 2
    content = _output_file(test_project).read_text() if _output_file(test_project).exists() else ""
    assert "Session:" not in content

    # Second run — correction already in seen file → exits 0
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


# ---------------------------------------------------------------------------
# E2E-10: Multi-capture — new correction after first already captured
# ---------------------------------------------------------------------------


def test_e2e_multi_capture(test_project, run_hook):
    """Per-learning dedup: second correction at new index is captured after first is seen."""
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

    # First run: correction at idx 2 → exits 2
    exit_code, stdout, _ = _run_slr(run_hook, test_project)
    assert exit_code == 2
    assert "Wrong, we use PostgreSQL" in stdout

    # Append new correction at idx 4 (simulates continued session)
    with transcript.open("a") as f:
        f.write(json.dumps(_user("Nope, check the connection string.", sid, "2026-02-22T10:04:00Z")) + "\n")
        f.write(json.dumps(_asst("Fixed the connection string.", sid, "2026-02-22T10:05:00Z")) + "\n")

    # Second run: idx 2 already captured, idx 4 is new → exits 2 for idx 4 only
    exit_code, stdout, _ = _run_slr(run_hook, test_project)
    assert exit_code == 2
    assert "Nope, check the connection string" in stdout
    assert "Wrong, we use PostgreSQL" not in stdout  # not re-captured

    # Third run: all corrections captured → exits 0
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


# ---------------------------------------------------------------------------
# E2E-11: Seen file tab-separated format verification
# ---------------------------------------------------------------------------


def test_e2e_seen_file_format(test_project, run_hook):
    """After capturing a correction, seen file uses tab-separated format: session_id TAB flow TAB idx."""
    sid = "e2e11-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Wrong, use const not var.", sid, "2026-02-22T10:00:00Z"),
            _asst("Fixed.", sid, "2026-02-22T10:01:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 2

    seen = _seen_file(test_project)
    assert seen.exists()
    first_line = seen.read_text().splitlines()[0]
    assert first_line == f"{sid}\tf1\t0"


# ---------------------------------------------------------------------------
# E2E-12: Self-learning flows independently after correction capture
# ---------------------------------------------------------------------------


def test_e2e_self_learning_after_correction(test_project, run_hook):
    """Flow 2 captures self-learning on the second run after Flow 1's correction is deduped."""
    sid = "e2e12-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Set up auth.", sid, "2026-02-22T10:00:00Z"),
            _asst("Using JWT tokens.", sid, "2026-02-22T10:01:00Z"),
            _user("Wrong, we use sessions not JWT.", sid, "2026-02-22T10:02:00Z"),
            _asst("Switching to session-based auth.", sid, "2026-02-22T10:03:00Z"),
            _user("Looks good.", sid, "2026-02-22T10:04:00Z"),
            _asst(
                "ROOT_CAUSE: Assumed JWT when project uses sessions.\n"
                "RULE: Always check existing auth strategy before implementing.\n"
                "DESTINATION: /Users/ash/Projects/vorbit/.claude/rules/bash-scripts.md",
                sid,
                "2026-02-22T10:05:00Z",
            ),
        ],
    )

    # First run: correction at idx 2 → exits 2
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 2

    # Second run: correction already seen (idx 2), self-learning at idx 5 is new
    # Flow 2 captures it → writes to output file → exits 0
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    out = _output_file(test_project)
    assert out.exists()
    content = out.read_text()
    assert "Always check existing auth strategy" in content
    assert "msg:5" in content

    # Third run: both flows fully captured → exits 0, output file unchanged
    content_before = out.read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert out.read_text() == content_before


# ---------------------------------------------------------------------------
# E2E-13: [msg:N] traceability in unprocessed-corrections.md
# ---------------------------------------------------------------------------


def test_e2e_msg_index_traceability(test_project, run_hook):
    """Self-discovered learning written to output file includes [msg:N] header for traceability."""
    sid = "e2e13-session"
    _write_jsonl(
        test_project["sessions_dir"] / f"{sid}.jsonl",
        [
            _user("Fix the login page.", sid, "2026-02-22T10:00:00Z"),
            _asst(
                "ROOT_CAUSE: Session tokens expire too fast due to hardcoded TTL.\n"
                "RULE: Always read TTL from config, never hardcode.\n"
                "DESTINATION: .claude/rules/auth.md",
                sid,
                "2026-02-22T10:01:00Z",
            ),
            _user("Thanks.", sid, "2026-02-22T10:02:00Z"),
        ],
    )

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    out = _output_file(test_project)
    assert out.exists()
    content = out.read_text()
    assert "Session:" in content
    assert "[msg:1]" in content
    assert "hardcoded TTL" in content
