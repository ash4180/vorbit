"""Tests for pre_push_warning.py hook — migrated from test-pre-push-warning.sh."""

import json
from hooks.tests.conftest import SCRIPTS


def test_detects_git_push(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": "git push"})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0
    assert "push" in stdout.lower()


def test_detects_git_push_origin_main(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": "git push origin main"})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0
    assert "push" in stdout.lower()


def test_ignores_git_status(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": "git status"})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0
    assert "warning" not in stdout.lower()


def test_ignores_git_commit(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": 'git commit -m "test"'})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0
    assert "warning" not in stdout.lower()


def test_always_exits_zero(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": "git push --force origin main"})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0


def test_ignores_non_git_commands(run_hook):
    env = {"TOOL_INPUT": json.dumps({"command": "npm install"})}
    exit_code, stdout, stderr = run_hook(SCRIPTS["pre_push_warning"], env_overrides=env)
    assert exit_code == 0
    assert "push" not in stdout.lower()
