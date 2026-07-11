"""Tests for the implement-loop stop hook.

The hook is a Claude Code Stop hook. In production it receives a JSON control
payload on stdin (never raw chat text) and it must ALWAYS exit 0 — it continues
a loop by printing a ``block`` decision on stdout, not by exiting non-zero.
Fixtures below mirror that real payload shape so the tests exercise the same
input the hook sees at runtime.
"""

import json
import os

from hooks.tests.conftest import SCRIPTS

HOOK = SCRIPTS["loop_controller"]
COMMAND = "/vorbit:implement:implement VIB-100 --loop"


def _running_state(**overrides) -> dict:
    state = {
        "version": 2,
        "active": True,
        "status": "running",
        "command": COMMAND,
        "maxIterations": 50,
        "iteration": 1,
    }
    state.update(overrides)
    return state


def _write_state(project_path, state: dict):
    state_file = project_path / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state))
    return state_file


def _stop_payload(message: str = "") -> str:
    """A production-shaped Stop hook stdin payload."""
    return json.dumps(
        {
            "session_id": "session-123",
            "transcript_path": "/tmp/transcript.jsonl",
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": message,
        }
    )


def test_no_state_file(test_project, run_hook):
    """No state file exits cleanly after draining stdin."""
    state_file = test_project["path"] / ".claude" / ".loop-state.json"

    exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert not state_file.exists()


def test_running_loop_blocks_and_reinjects_command(test_project, run_hook):
    """A running loop increments atomically and continues via a block decision."""
    state_file = _write_state(test_project["path"], _running_state(iteration=3))

    exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    decision = json.loads(stdout)
    assert decision["decision"] == "block"
    assert COMMAND in decision["reason"]
    assert json.loads(state_file.read_text())["iteration"] == 4


def test_completed_status_deletes_state(test_project, run_hook):
    """status: completed removes the state file and lets the session stop."""
    state_file = _write_state(
        test_project["path"], _running_state(active=False, status="completed")
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert not state_file.exists()


def test_non_running_status_preserves_state_and_allows_stop(test_project, run_hook):
    """Terminal statuses wait for the user: no continuation, state untouched."""
    for status in ("blocked", "needs_input", "failed", "canceled"):
        state_file = _write_state(
            test_project["path"], _running_state(active=False, status=status)
        )

        exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

        assert exit_code == 0, status
        assert stdout == "", status
        assert state_file.exists(), status


def test_completion_marker_in_message_does_not_stop_a_running_loop(test_project, run_hook):
    """Chat text can never end the loop; only status does."""
    state_file = _write_state(test_project["path"], _running_state())

    exit_code, stdout, _ = run_hook(
        HOOK,
        stdin=_stop_payload("All done <!-- VORBIT_LOOP_COMPLETE -->"),
        cwd=test_project["path"],
    )

    assert exit_code == 0
    assert json.loads(stdout)["decision"] == "block"
    assert state_file.exists()


def test_unreadable_state_is_quarantined_not_blocking(test_project, run_hook):
    """Malformed state is moved aside and the session is allowed to stop."""
    state_file = test_project["path"] / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("{not-json")

    exit_code, stdout, stderr = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert not state_file.exists()
    aside = state_file.with_suffix(".invalid")
    assert aside.read_text() == "{not-json"
    assert "Moved aside" in stderr


def test_non_object_state_is_quarantined(test_project, run_hook):
    """Valid JSON that is not an object (e.g. a list) is treated as unusable."""
    state_file = test_project["path"] / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("[]")

    exit_code, _, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert not state_file.exists()
    assert state_file.with_suffix(".invalid").exists()


def test_legacy_version_is_quarantined_with_visible_reason(test_project, run_hook):
    """An old-schema state (no version) is retired visibly, not silently."""
    state_file = _write_state(
        test_project["path"],
        {
            "active": True,
            "status": "running",
            "command": COMMAND,
            "completionSignal": "✅ All acceptance criteria met",
            "iteration": 1,
            "maxIterations": 50,
        },
    )

    exit_code, stdout, stderr = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert not state_file.exists()
    assert "unsupported" in stderr
    assert state_file.with_suffix(".invalid").exists()


def test_command_without_loop_flag_retires_failed(test_project, run_hook):
    state_file = _write_state(
        test_project["path"], _running_state(command="/vorbit:implement:implement VIB-100")
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["status"] == "failed"
    assert state["active"] is False
    assert "--loop" in state["blockReason"]


def test_lookalike_loop_flag_retires_failed(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _running_state(command="/vorbit:implement:implement VIB-100 --loophole"),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["status"] == "failed"


def test_max_iterations_retires_blocked(test_project, run_hook):
    state_file = _write_state(
        test_project["path"], _running_state(iteration=10, maxIterations=10)
    )

    exit_code, stdout, stderr = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["status"] == "blocked"
    assert state["active"] is False
    assert "maxIterations (10)" in state["blockReason"]
    assert "blocked" in stderr


def test_invalid_iteration_retires_failed(test_project, run_hook):
    state_file = _write_state(test_project["path"], _running_state(iteration="three"))

    exit_code, _, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert state["status"] == "failed"


def test_nonpositive_iteration_retires_failed(test_project, run_hook):
    state_file = _write_state(test_project["path"], _running_state(iteration=0))

    exit_code, _, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert json.loads(state_file.read_text())["status"] == "failed"


def test_boolean_iteration_retires_failed(test_project, run_hook):
    """iteration: true is a bool, not a valid int, even though bool subclasses int."""
    state_file = _write_state(test_project["path"], _running_state(iteration=True))

    exit_code, _, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])

    assert exit_code == 0
    assert json.loads(state_file.read_text())["status"] == "failed"


def test_running_loop_survives_readonly_dir_without_blocking(test_project, run_hook):
    """A write failure fails open (exit 0), never traps the session."""
    state_file = _write_state(test_project["path"], _running_state())
    claude_dir = state_file.parent
    os.chmod(claude_dir, 0o500)
    try:
        exit_code, stdout, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=test_project["path"])
    finally:
        os.chmod(claude_dir, 0o700)

    assert exit_code == 0
    assert stdout == ""


def test_exit_code_is_always_zero_or_two(test_project, run_hook):
    """Mandated invariant: the stop hook exits 0 or 2 only — never any other code."""
    project = test_project["path"]
    state_file = project / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    scenarios = [
        lambda: state_file.unlink(missing_ok=True),
        lambda: state_file.write_text(json.dumps(_running_state())),
        lambda: state_file.write_text(json.dumps(_running_state(active=False, status="completed"))),
        lambda: state_file.write_text(json.dumps(_running_state(active=False, status="blocked"))),
        lambda: state_file.write_text(json.dumps(_running_state(iteration=50, maxIterations=50))),
        lambda: state_file.write_text(json.dumps(_running_state(command="no-loop-here"))),
        lambda: state_file.write_text(json.dumps(_running_state(iteration="bad"))),
        lambda: state_file.write_text("{not-json"),
        lambda: state_file.write_text("[]"),
        lambda: state_file.write_text(json.dumps({"status": "running", "command": COMMAND})),
    ]

    for prepare in scenarios:
        prepare()
        exit_code, _, _ = run_hook(HOOK, stdin=_stop_payload(), cwd=project)
        assert exit_code in (0, 2), exit_code
        # Restore a quarantined file so the next scenario starts clean.
        state_file.with_suffix(".invalid").unlink(missing_ok=True)
