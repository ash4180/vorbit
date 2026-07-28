"""Tests for adhd_always_on.sh SessionStart hook (always-on ADHD mode)."""

import os
import subprocess

from hooks.tests.conftest import SCRIPTS

FLAG_NAME = ".vorbit-adhd-always"


def run_sh(script_path, env_overrides=None):
    env = os.environ.copy()
    if env_overrides:
        env.update({k: str(v) for k, v in env_overrides.items()})
    result = subprocess.run(
        ["sh", str(script_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def test_silent_without_flag(tmp_path):
    exit_code, stdout, _ = run_sh(
        SCRIPTS["adhd_always_on"], env_overrides={"CLAUDE_CONFIG_DIR": tmp_path}
    )
    assert exit_code == 0
    assert stdout == ""


def test_silent_when_config_dir_missing(tmp_path):
    exit_code, stdout, _ = run_sh(
        SCRIPTS["adhd_always_on"],
        env_overrides={"CLAUDE_CONFIG_DIR": tmp_path / "does-not-exist"},
    )
    assert exit_code == 0
    assert stdout == ""


def test_injects_ruleset_with_flag(tmp_path):
    (tmp_path / FLAG_NAME).touch()
    exit_code, stdout, _ = run_sh(
        SCRIPTS["adhd_always_on"], env_overrides={"CLAUDE_CONFIG_DIR": tmp_path}
    )
    assert exit_code == 0
    assert "ADHD MODE ACTIVE (always-on)" in stdout
    assert "Lead with the next action" in stdout


def test_strips_frontmatter(tmp_path):
    (tmp_path / FLAG_NAME).touch()
    _, stdout, _ = run_sh(
        SCRIPTS["adhd_always_on"], env_overrides={"CLAUDE_CONFIG_DIR": tmp_path}
    )
    assert "license: MIT" not in stdout
    assert "metadata:" not in stdout
    assert not stdout.split("\n\n", 1)[1].startswith("---")


def test_tells_user_how_to_disable(tmp_path):
    (tmp_path / FLAG_NAME).touch()
    _, stdout, _ = run_sh(
        SCRIPTS["adhd_always_on"], env_overrides={"CLAUDE_CONFIG_DIR": tmp_path}
    )
    assert str(tmp_path / FLAG_NAME) in stdout
    assert "stop adhd mode" in stdout
