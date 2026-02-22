"""Tests for post_edit_validate.py hook — migrated from test-post-edit-validate.sh."""

import json
import shutil

import pytest

from hooks.tests.conftest import SCRIPTS


def test_detects_tsconfig(tmp_path, run_hook):
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {"strict": true}}')
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x: number = 42;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code == 0
    assert "tsc" in stdout.lower()


def test_detects_pyproject_mypy(tmp_path, run_hook):
    (tmp_path / "pyproject.toml").write_text("[tool.mypy]\n")
    test_file = tmp_path / "test.py"
    test_file.write_text("x: int = 1\n")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code == 0
    assert "mypy" in stdout.lower() or "pyright" in stdout.lower()


def test_detects_gomod(tmp_path, run_hook):
    (tmp_path / "go.mod").write_text("module test\n")
    test_file = tmp_path / "test.go"
    test_file.write_text("package main\n")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code == 0
    assert "go" in stdout.lower()


def test_no_validator_silent_skip(tmp_path, run_hook):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello\n")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, stderr = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code == 0
    assert "error" not in stdout.lower()
    assert "warning" not in stdout.lower()
    assert stdout.strip() == ""


@pytest.mark.skipif(shutil.which("tsc") is None, reason="tsc not installed")
def test_validation_failure_blocks(tmp_path, run_hook):
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {"strict": true}}')
    test_file = tmp_path / "test.ts"
    test_file.write_text('const x: number = "string";')  # intentional type error

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)})}
    exit_code, _, _ = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code != 0


@pytest.mark.skipif(shutil.which("tsc") is None, reason="tsc not installed")
def test_validation_success_passes(tmp_path, run_hook):
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {"strict": true}}')
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x: number = 42;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)})}
    exit_code, _, _ = run_hook(SCRIPTS["post_edit_validate"], env_overrides=env)

    assert exit_code == 0
