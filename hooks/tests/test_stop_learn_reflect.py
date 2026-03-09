"""Tests for stop_learn_reflect.py hook — migrated from test-stop-learn-reflect.sh.

All tests run in isolated tmp_home + test_project fixtures so ~/.claude/rules/
is never touched. HOME override in subprocess env routes all file I/O to tmp dirs.
Obsidian notes are written to tmp_home/Projects/Thinking-Labs/claude/.
"""

import json
from pathlib import Path

from hooks.tests.conftest import PLUGIN_ROOT, SCRIPTS

HOOK = SCRIPTS["stop_learn_reflect"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_slr(run_hook, project, plugin_root=None):
    """Run stop_learn_reflect.py with isolated HOME and CLAUDE_PLUGIN_ROOT."""
    env = {
        "HOME": str(project["home"]),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root or PLUGIN_ROOT),
    }
    return run_hook(HOOK, stdin="", env_overrides=env, cwd=project["path"])


def _rules_dir(project):
    return project["home"] / ".claude" / "rules"


def _pending_file(project):
    """Pending file symlink in rules dir (follows symlink to Obsidian source)."""
    return _rules_dir(project) / "pending-capture.md"


def _pending_source(project):
    """Pending file source in Obsidian vault."""
    return _obsidian_dir(project) / "pending-capture.md"


def _seen_file(project):
    return _rules_dir(project) / ".seen-correction-sessions"


def _rules_file(project):
    return _rules_dir(project) / "vorbit-learning.md"


def _obsidian_dir(project):
    return project["home"] / "Projects" / "Thinking-Labs" / "claude"


def _obsidian_project_dir(project):
    project_name = project["path"].resolve().name
    return _obsidian_dir(project) / "projects" / project_name


def _read_latest_obsidian_note(project):
    """Read the most recently created Obsidian note for this project."""
    notes = sorted(_obsidian_project_dir(project).glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not notes:
        return ""
    return notes[0].read_text()


def _obsidian_index(project):
    return _obsidian_dir(project) / "_corrections-index.md"


def _write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _user(text, sid, ts):
    return {"type": "user", "message": {"role": "user", "content": text}, "sessionId": sid, "timestamp": ts}


def _asst(text, sid, ts):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}, "sessionId": sid, "timestamp": ts}


def _make_custom_rules(base_path, keyword=None):
    """Create skills/learn/vorbit-learning-rules.md under base_path."""
    rules_dir = base_path / "skills" / "learn"
    rules_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Test Rules"]
    if keyword:
        lines.append(f"<!-- correction-keywords: {keyword} -->")
    lines.append("<!-- vorbit-learning-rules -->")
    (rules_dir / "vorbit-learning-rules.md").write_text("\n".join(lines) + "\n")


# ============================================================================
# Section 0: Exit Code Safety
# ============================================================================

def test_corrupt_transcript_exits_0(test_project, run_hook):
    """0a: Corrupt transcript (invalid JSON) → exits 0."""
    (test_project["sessions_dir"] / "corrupt.jsonl").write_text("NOT VALID JSON{{{")
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_missing_rules_exits_0(test_project, run_hook, correction_transcript):
    """0b: Nonexistent CLAUDE_PLUGIN_ROOT → exits 0."""
    correction_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=Path("/nonexistent/path"))
    assert exit_code == 0


def test_empty_transcript_exits_0(test_project, run_hook):
    """0c: Empty transcript → exits 0."""
    (test_project["sessions_dir"] / "empty.jsonl").write_text("")
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_only_exits_0(test_project, run_hook, correction_transcript, clean_transcript):
    """0d: Script ALWAYS exits 0 — never any other code including 2."""
    # No transcript
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0

    # With corrections — still exits 0 (writes pending file instead)
    correction_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0

    # Clean session — different session id to avoid dedup
    for f in test_project["sessions_dir"].glob("*.jsonl"):
        f.unlink()
    clean_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


# ============================================================================
# Section 1: Correction Keyword Detection
# ============================================================================

def test_correction_keyword_wrong(test_project, run_hook, correction_transcript):
    """1a: 'Wrong' keyword → exits 0, pointer in pending file, context in Obsidian note."""
    correction_transcript(test_project["sessions_dir"])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    pending = _pending_file(test_project)
    assert pending.exists()
    content = pending.read_text()
    assert "VORBIT:CORRECTION-CAPTURE" in content
    assert "Obsidian" in content

    # Actual correction context lives in the Obsidian note
    note = _read_latest_obsidian_note(test_project)
    assert "Wrong, this project uses SQLite" in note
    assert "psycopg2" in note  # preceding assistant context
    assert "sqlite3" in note  # following assistant context


def test_clean_session_exits_0(test_project, run_hook, clean_transcript):
    """1b: Clean session → exits 0, no pending file."""
    clean_transcript(test_project["sessions_dir"])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    assert not _pending_file(test_project).exists()


def test_no_user_messages_exits_0(test_project, run_hook):
    """1c: Transcript with only assistant messages → exits 0."""
    sid = "test-session-nouser"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Starting task.", sid, "2026-02-15T10:00:00Z"),
        _asst("Task complete.", sid, "2026-02-15T10:01:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_nope_keyword(test_project, run_hook):
    """1d: 'Nope' keyword → exits 0, context in Obsidian note."""
    sid = "test-session-nope"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("I added the feature to line 42.", sid, "2026-02-15T10:00:00Z"),
        _user("Nope, line 12", sid, "2026-02-15T10:01:00Z"),
        _asst("Fixed, moved to line 12.", sid, "2026-02-15T10:02:00Z"),
    ])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    pending = _pending_file(test_project)
    assert pending.exists()
    assert "VORBIT:CORRECTION-CAPTURE" in pending.read_text()

    note = _read_latest_obsidian_note(test_project)
    assert "Nope, line 12" in note


def test_multiple_corrections(test_project, run_hook):
    """1e: Three correction keywords → exits 0, all three captured in Obsidian note."""
    sid = "test-session-multi789"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("I'll use MySQL for the database.", sid, "2026-02-15T10:00:00Z"),
        _user("Wrong, we use PostgreSQL.", sid, "2026-02-15T10:01:00Z"),
        _asst("OK switching to PostgreSQL.", sid, "2026-02-15T10:02:00Z"),
        _user("Still not working, check the port.", sid, "2026-02-15T10:03:00Z"),
        _asst("Fixed the port to 5432.", sid, "2026-02-15T10:04:00Z"),
        _user("Nope, the issue is in the cookie parser.", sid, "2026-02-15T10:05:00Z"),
        _asst("Found and fixed the cookie parser issue.", sid, "2026-02-15T10:06:00Z"),
    ])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""

    note = _read_latest_obsidian_note(test_project)
    assert "Wrong, we use PostgreSQL" in note
    assert "Still not working" in note
    assert "Nope, the issue is in the cookie parser" in note


# ============================================================================
# Section 2: False Positive Filtering
# ============================================================================

def test_long_message_filtered(test_project, run_hook, long_message_transcript):
    """2a: Message >500 chars with correction keywords → exits 0 (filtered)."""
    long_message_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_teammate_message_filtered(test_project, run_hook, teammate_transcript):
    """2b: <teammate-message> tag with correction keywords → exits 0 (filtered)."""
    teammate_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_real_short_correction_passes(test_project, run_hook):
    """2c: Short 'wrong' correction → exits 0, pending file written (not filtered)."""
    sid = "test-session-short"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Using var for variable declarations.", sid, "2026-02-15T10:00:00Z"),
        _user("wrong, use const", sid, "2026-02-15T10:01:00Z"),
        _asst("Fixed, using const instead.", sid, "2026-02-15T10:02:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert _pending_file(test_project).exists()


def test_word_boundary_not_triggered(test_project, run_hook):
    """2d: 'not'/'know'/'cannot' (containing 'no') must NOT trigger → exits 0."""
    sid = "test-session-nosub"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Setting up the config.", sid, "2026-02-15T10:00:00Z"),
        _user("the script is not ready yet", sid, "2026-02-15T10:01:00Z"),
        _user("I know there is another approach", sid, "2026-02-15T10:02:00Z"),
        _user("we cannot use that library", sid, "2026-02-15T10:03:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert not _seen_file(test_project).exists()


# ============================================================================
# Section 3: Keyword Source (reads from rules file, not hardcoded)
# ============================================================================

def test_custom_keyword_from_rules(test_project, run_hook):
    """3a: Custom keyword 'oops' in rules file → exits 0, pending file written."""
    _make_custom_rules(test_project["path"], keyword="oops")

    sid = "test-session-custom"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Deployed to staging.", sid, "2026-02-15T10:00:00Z"),
        _user("oops, that was the wrong branch", sid, "2026-02-15T10:01:00Z"),
        _asst("Rolling back.", sid, "2026-02-15T10:02:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=test_project["path"])
    assert exit_code == 0
    assert _pending_file(test_project).exists()


def test_keyword_swap_no_longer_matches(test_project, run_hook):
    """3a (swap): Keyword changed to 'broken', 'oops' transcript no longer matches → exits 0, no pending file."""
    _make_custom_rules(test_project["path"], keyword="broken")

    sid = "test-session-custom2"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Deployed to staging.", sid, "2026-02-15T10:00:00Z"),
        _user("oops, that was the wrong branch", sid, "2026-02-15T10:01:00Z"),
        _asst("Rolling back.", sid, "2026-02-15T10:02:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=test_project["path"])
    assert exit_code == 0
    assert not _pending_file(test_project).exists()


def test_missing_keywords_comment_exits_0(test_project, run_hook, correction_transcript):
    """3b: Rules file without correction-keywords comment → exits 0 (no crash)."""
    _make_custom_rules(test_project["path"], keyword=None)
    correction_transcript(test_project["sessions_dir"])

    exit_code, _, _ = _run_slr(run_hook, test_project, plugin_root=test_project["path"])
    assert exit_code == 0


# ============================================================================
# Section 4: Loop & Dedup Guards
# ============================================================================

def test_skips_during_active_loop(test_project, run_hook, correction_transcript):
    """4a: Loop active (loop-state.json active: true) → exits 0."""
    loop_state = test_project["path"] / ".claude" / ".loop-state.json"
    loop_state.parent.mkdir(parents=True, exist_ok=True)
    loop_state.write_text('{"active":true,"command":"test","iteration":1}')

    correction_transcript(test_project["sessions_dir"])

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


def test_per_learning_dedup_correction(test_project, run_hook, correction_transcript):
    """4b: Correction index in seen file → exits 0 (per-learning dedup), no pending file."""
    correction_transcript(test_project["sessions_dir"])

    # "Wrong, this project uses SQLite" is at index 2 in the correction_transcript
    seen = _seen_file(test_project)
    seen.parent.mkdir(parents=True, exist_ok=True)
    seen.write_text("test-session-abc123\tf1\t2\n")

    exit_code, _, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert not _pending_file(test_project).exists()


def test_correction_retrigger_dedup(test_project, run_hook, correction_transcript):
    """4c: First run exits 0 + writes pending file; second run exits 0 (same correction deduped)."""
    correction_transcript(test_project["sessions_dir"])

    # First run: keyword found → exits 0, pending file written, seen file written
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert _seen_file(test_project).exists()
    assert _pending_file(test_project).exists()

    # Second run: same session, index already in seen file → exits 0, no new pending write
    content_before = _pending_file(test_project).read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert _pending_file(test_project).read_text() == content_before


def test_multi_capture_new_index(test_project, run_hook):
    """4d: New correction at new index captured on second run, third run is clean."""
    sid = "test-session-multi-idx"
    transcript = test_project["sessions_dir"] / f"{sid}.jsonl"

    # Initial transcript: correction at index 2
    _write_jsonl(transcript, [
        _user("Write the function.", sid, "2026-02-22T10:00:00Z"),
        _asst("Using var for variables.", sid, "2026-02-22T10:01:00Z"),
        _user("Wrong, use const.", sid, "2026-02-22T10:02:00Z"),
        _asst("Fixed, using const.", sid, "2026-02-22T10:03:00Z"),
    ])

    # First run: correction at index 2 → exits 0, pending file written
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    seen = _seen_file(test_project)
    assert seen.exists()
    assert f"{sid}\tf1\t2" in seen.read_text()
    pending = _pending_file(test_project)
    assert pending.exists()

    note1 = _read_latest_obsidian_note(test_project)
    assert "Wrong, use const" in note1

    # Append new correction at index 4
    with transcript.open("a") as f:
        f.write(json.dumps(_user("Nope, still broken.", sid, "2026-02-22T10:04:00Z")) + "\n")
        f.write(json.dumps(_asst("Fixing now.", sid, "2026-02-22T10:05:00Z")) + "\n")

    # Second run: index 2 deduped, index 4 is new → exits 0, new Obsidian note
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    note2 = _read_latest_obsidian_note(test_project)
    assert "Nope, still broken" in note2

    # Third run: both corrections seen → exits 0, pending file unchanged
    content_after_second = pending.read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert pending.read_text() == content_after_second


# ============================================================================
# Section 5: Obsidian Note Content & Index
# ============================================================================

def test_obsidian_note_has_yaml_frontmatter(test_project, run_hook, correction_transcript):
    """5a: Obsidian note has YAML frontmatter with expected fields."""
    correction_transcript(test_project["sessions_dir"])
    _run_slr(run_hook, test_project)

    note = _read_latest_obsidian_note(test_project)
    assert "status: pending" in note
    assert "capture_type: correction" in note
    assert "root_cause:" in note
    assert "project:" in note


def test_obsidian_index_created(test_project, run_hook, correction_transcript):
    """5b: Dataview-based corrections index is created."""
    correction_transcript(test_project["sessions_dir"])
    _run_slr(run_hook, test_project)

    index = _obsidian_index(test_project)
    assert index.exists()
    content = index.read_text()
    assert "dataview" in content
    assert "capture_type" in content


def test_obsidian_note_has_rich_context(test_project, run_hook):
    """5c: Obsidian note captures multiple assistant messages (up to 3 before/after)."""
    sid = "test-session-richctx"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Step 1: Setting up the database.", sid, "2026-02-15T10:00:00Z"),
        _asst("Step 2: Adding migrations.", sid, "2026-02-15T10:01:00Z"),
        _asst("Step 3: Connecting to PostgreSQL.", sid, "2026-02-15T10:02:00Z"),
        _user("Wrong, we use SQLite.", sid, "2026-02-15T10:03:00Z"),
        _asst("Fix 1: Switching driver.", sid, "2026-02-15T10:04:00Z"),
        _asst("Fix 2: Updating config.", sid, "2026-02-15T10:05:00Z"),
        _asst("Fix 3: Done.", sid, "2026-02-15T10:06:00Z"),
    ])

    _run_slr(run_hook, test_project)

    note = _read_latest_obsidian_note(test_project)
    # Should have multiple assistant messages before the correction
    assert "Setting up the database" in note
    assert "Adding migrations" in note
    assert "Connecting to PostgreSQL" in note
    # And after
    assert "Switching driver" in note
    assert "Updating config" in note
    assert "Done" in note


# ============================================================================
# Section 6: Symlink & Setup
# ============================================================================

def test_symlink_setup(test_project, run_hook, clean_transcript):
    """6a: Fresh install → creates symlink at tmp_home/.claude/rules/vorbit-learning.md."""
    rules_file = _rules_file(test_project)
    if rules_file.exists() or rules_file.is_symlink():
        rules_file.unlink()

    clean_transcript(test_project["sessions_dir"])
    _run_slr(run_hook, test_project)

    assert rules_file.is_symlink()
    assert "vorbit-learning-rules" in rules_file.read_text()


def test_idempotent_setup(test_project, run_hook, clean_transcript):
    """6b: Existing file with marker → not replaced with symlink."""
    rules_file = _rules_file(test_project)
    rules_file.parent.mkdir(parents=True, exist_ok=True)
    rules_file.write_text("existing content\n<!-- vorbit-learning-rules -->\n")

    clean_transcript(test_project["sessions_dir"])
    _run_slr(run_hook, test_project)

    assert not rules_file.is_symlink()
    assert "existing content" in rules_file.read_text()


def test_exits_without_transcript(test_project, run_hook):
    """6c: Empty sessions dir → exits 0."""
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0


# ============================================================================
# Section 7: Output Format Verification
# ============================================================================

def test_output_format_pointer(test_project, run_hook, correction_transcript):
    """7a: Pending file has Obsidian pointer; Obsidian note has full context; stdout empty."""
    correction_transcript(test_project["sessions_dir"])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    content = _pending_file(test_project).read_text()
    assert "[VORBIT:CORRECTION-CAPTURE]" in content
    assert "Obsidian" in content

    note = _read_latest_obsidian_note(test_project)
    assert "psycopg2" in note
    assert "sqlite3" in note


# ============================================================================
# Section 8: Voluntary Keyword Detection
# ============================================================================

def test_voluntary_keyword_exits_0(test_project, run_hook):
    """8a: 'remember this' → exits 0, VOLUNTARY-CAPTURE in pending, context in Obsidian."""
    sid = "test-session-vol123"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("I've refactored the auth module to use JWT tokens.", sid, "2026-02-15T10:00:00Z"),
        _user("remember this: always use RS256 for JWT signing, not HS256", sid, "2026-02-15T10:01:00Z"),
        _asst("Noted, RS256 is the correct algorithm for asymmetric JWT signing.", sid, "2026-02-15T10:02:00Z"),
    ])

    exit_code, stdout, _ = _run_slr(run_hook, test_project)

    assert exit_code == 0
    assert stdout.strip() == ""
    pending = _pending_file(test_project)
    assert pending.exists()
    content = pending.read_text()
    assert "VORBIT:VOLUNTARY-CAPTURE" in content

    note = _read_latest_obsidian_note(test_project)
    assert "RS256" in note
    assert "capture_type: voluntary" in note


def test_no_voluntary_keywords_exits_0(test_project, run_hook, clean_transcript):
    """8b: No voluntary keywords → exits 0, no pending file."""
    clean_transcript(test_project["sessions_dir"])
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert not _pending_file(test_project).exists()


def test_voluntary_keyword_dedup(test_project, run_hook):
    """8c: Second run on same voluntary transcript → exits 0, pending file unchanged (fv dedup)."""
    sid = "test-session-vol-dedup"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _user("We always use sqlite3. Remember this.", sid, "2026-02-15T10:00:00Z"),
        _asst("Noted, sqlite3 it is.", sid, "2026-02-15T10:01:00Z"),
    ])

    # First run: voluntary keyword found → exits 0, seen file written with fv entry
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    seen = _seen_file(test_project)
    assert seen.exists()
    assert "fv" in seen.read_text()
    pending = _pending_file(test_project)
    assert pending.exists()

    # Second run: same session, same index already in seen file → exits 0, pending unchanged
    content_before = pending.read_text()
    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0
    assert pending.read_text() == content_before


# ============================================================================
# Section 9: Both flows run independently (no early exit)
# ============================================================================

def test_both_correction_and_voluntary_captured(test_project, run_hook):
    """9a: Session with both correction and voluntary keywords → both flows fire."""
    sid = "test-session-both"
    _write_jsonl(test_project["sessions_dir"] / f"{sid}.jsonl", [
        _asst("Using MySQL.", sid, "2026-02-15T10:00:00Z"),
        _user("Wrong, we use PostgreSQL.", sid, "2026-02-15T10:01:00Z"),
        _asst("Switching to PostgreSQL.", sid, "2026-02-15T10:02:00Z"),
        _user("Also, remember this: always use connection pooling.", sid, "2026-02-15T10:03:00Z"),
        _asst("Noted, connection pooling.", sid, "2026-02-15T10:04:00Z"),
    ])

    exit_code, _, _ = _run_slr(run_hook, test_project)
    assert exit_code == 0

    content = _pending_file(test_project).read_text()
    assert "VORBIT:CORRECTION-CAPTURE" in content
    assert "VORBIT:VOLUNTARY-CAPTURE" in content

    # Both should have Obsidian notes
    notes = sorted(_obsidian_project_dir(test_project).glob("*.md"))
    assert len(notes) == 2
