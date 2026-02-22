"""Tests for loop_controller.py hook — migrated from test-loop-controller.sh."""

import json

from hooks.tests.conftest import SCRIPTS

HOOK = SCRIPTS["loop_controller"]


def _write_state(project_path, state: dict):
    state_file = project_path / ".claude" / ".loop-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state))
    return state_file


def test_no_state_file(test_project, run_hook):
    """No state file → exits 0, does nothing."""
    state_file = test_project["path"] / ".claude" / ".loop-state.json"
    assert not state_file.exists()

    exit_code, stdout, _ = run_hook(HOOK, stdin="some claude output", cwd=test_project["path"])

    assert exit_code == 0
    assert not state_file.exists()


def test_inactive_loop(test_project, run_hook):
    """active: false → exits 0, state file left in place."""
    state_file = _write_state(
        test_project["path"],
        {"active": False, "iteration": 1, "maxIterations": 50},
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="some claude output", cwd=test_project["path"])

    assert exit_code == 0
    assert state_file.exists()


def test_increments_iteration(test_project, run_hook):
    """Active loop, no completion signal → increments iteration, exits 2, echoes command."""
    cmd = "test-command-12345"
    state_file = _write_state(
        test_project["path"],
        {
            "active": True,
            "command": cmd,
            "completionSignal": "LOOP_DONE",
            "maxIterations": 50,
            "iteration": 3,
        },
    )

    exit_code, stdout, _ = run_hook(
        HOOK,
        stdin="some output without the signal",
        cwd=test_project["path"],
    )

    updated_state = json.loads(state_file.read_text())
    assert exit_code == 2
    assert updated_state["iteration"] == 4
    assert stdout.strip() == cmd
    assert state_file.exists()


def test_completion_signal_stops_loop(test_project, run_hook):
    """Completion signal in Claude's output → deletes state file, exits 0."""
    state_file = _write_state(
        test_project["path"],
        {
            "active": True,
            "completionSignal": "ALL_DONE",
            "maxIterations": 50,
            "iteration": 2,
        },
    )

    exit_code, stdout, _ = run_hook(
        HOOK,
        stdin="Work complete. ALL_DONE",
        cwd=test_project["path"],
    )

    assert exit_code == 0
    assert not state_file.exists()


def test_max_iterations_stops_loop(test_project, run_hook):
    """iteration >= maxIterations → deletes state file, exits 0."""
    state_file = _write_state(
        test_project["path"],
        {
            "active": True,
            "completionSignal": "DONE",
            "maxIterations": 10,
            "iteration": 10,
        },
    )

    exit_code, stdout, _ = run_hook(HOOK, stdin="still going", cwd=test_project["path"])

    assert exit_code == 0
    assert not state_file.exists()


def test_no_signal_continues_loop(test_project, run_hook):
    """No signal in output → exits 2, echoes command, state file kept."""
    cmd = "test-command-67890"
    state_file = _write_state(
        test_project["path"],
        {
            "active": True,
            "command": cmd,
            "completionSignal": "LOOP_COMPLETE",
            "maxIterations": 50,
            "iteration": 1,
        },
    )

    exit_code, stdout, _ = run_hook(
        HOOK,
        stdin="output with no signal here",
        cwd=test_project["path"],
    )

    assert exit_code == 2
    assert stdout.strip() == cmd
    assert state_file.exists()
