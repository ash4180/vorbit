"""Tests for the implement-loop stop hook."""

import json

from hooks.tests.conftest import SCRIPTS

HOOK = SCRIPTS["loop_controller"]
COMMAND = "/vorbit:implement:implement VIB-100 --loop"
SIGNAL = "<!-- VORBIT_LOOP_COMPLETE -->"


def _write_state(project_path, state: dict):
    state_file = project_path / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state))
    return state_file


def _active_state(**overrides):
    state = {
        "version": 2,
        "active": True,
        "status": "running",
        "command": COMMAND,
        "completionSignal": SIGNAL,
        "maxIterations": 50,
        "iteration": 1,
    }
    state.update(overrides)
    return state


def test_no_state_file(test_project, run_hook):
    """No state file exits cleanly after draining stdin."""
    state_file = test_project["path"] / ".claude" / ".loop-state.json"

    exit_code, stdout, _ = run_hook(HOOK, stdin="some output", cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert not state_file.exists()


def test_inactive_loop_leaves_state_for_inspection(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(active=False, status="blocked"),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="some output", cwd=test_project["path"])

    assert exit_code == 0
    assert stdout == ""
    assert state_file.exists()


def test_unreadable_state_blocks_and_is_preserved(test_project, run_hook):
    state_file = test_project["path"] / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("{not-json")

    exit_code, stdout, stderr = run_hook(
        HOOK,
        stdin="some output",
        cwd=test_project["path"],
    )

    assert exit_code == 2
    assert stdout == ""
    assert "state is unreadable" in stderr
    assert state_file.read_text() == "{not-json"


def test_active_loop_increments_atomically_and_reinjects_loop_command(test_project, run_hook):
    state_file = _write_state(test_project["path"], _active_state(iteration=3))

    exit_code, stdout, _ = run_hook(HOOK, stdin="work remains", cwd=test_project["path"])

    updated_state = json.loads(state_file.read_text())
    assert exit_code == 2
    assert updated_state["iteration"] == 4
    assert stdout.strip() == COMMAND


def test_completed_status_and_exact_signal_delete_state(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(active=False, status="completed"),
    )

    exit_code, _, _ = run_hook(
        HOOK,
        stdin=f"Queue verified. {SIGNAL}",
        cwd=test_project["path"],
    )

    assert exit_code == 0
    assert not state_file.exists()


def test_completed_state_without_signal_is_preserved(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(active=False, status="completed"),
    )

    exit_code, stdout, _ = run_hook(
        HOOK,
        stdin="Queue verified, but marker omitted.",
        cwd=test_project["path"],
    )

    assert exit_code == 0
    assert stdout == ""
    assert state_file.exists()


def test_signal_alone_cannot_stop_running_loop(test_project, run_hook):
    state_file = _write_state(test_project["path"], _active_state(status="running"))

    exit_code, stdout, _ = run_hook(HOOK, stdin=SIGNAL, cwd=test_project["path"])

    assert exit_code == 2
    assert stdout.strip() == COMMAND
    assert state_file.exists()


def test_max_iterations_blocks_and_preserves_state(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(iteration=10, maxIterations=10),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="still going", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert "blocked after 10 iterations" in stdout
    assert state["active"] is False
    assert state["status"] == "blocked"
    assert state["blockReason"] == "Reached maxIterations (10)"


def test_command_without_loop_flag_fails_closed(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(command="/vorbit:implement:implement VIB-100"),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="continue", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["active"] is False
    assert state["status"] == "failed"
    assert "--loop" in state["blockReason"]


def test_lookalike_loop_flag_fails_closed(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(command="/vorbit:implement:implement VIB-100 --loophole"),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="continue", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["active"] is False
    assert state["status"] == "failed"


def test_noncanonical_completion_signal_fails_closed(test_project, run_hook):
    state_file = _write_state(
        test_project["path"],
        _active_state(status="completed", completionSignal="DONE"),
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="DONE", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert stdout == ""
    assert state["active"] is False
    assert state["status"] == "failed"
    assert "completion signal" in state["blockReason"]


def test_invalid_iteration_values_fail_closed(test_project, run_hook):
    state_file = _write_state(test_project["path"], _active_state(iteration="three"))

    exit_code, _, _ = run_hook(HOOK, stdin="continue", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert state["active"] is False
    assert state["status"] == "failed"


def test_nonpositive_iteration_values_fail_closed(test_project, run_hook):
    state_file = _write_state(test_project["path"], _active_state(iteration=0))

    exit_code, _, _ = run_hook(HOOK, stdin="continue", cwd=test_project["path"])

    state = json.loads(state_file.read_text())
    assert exit_code == 0
    assert state["active"] is False
    assert state["status"] == "failed"
