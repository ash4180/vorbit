"""Tests for post_edit_format.py hook — migrated from test-post-edit-format.sh."""

import json
from hooks.tests.conftest import SCRIPTS


def test_detects_biome_json(tmp_path, run_hook):
    (tmp_path / "biome.json").write_text('{"formatter": {"enabled": true}}')
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x = 1;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
    assert "biome" in stdout.lower()


def test_detects_prettierrc(tmp_path, run_hook):
    (tmp_path / ".prettierrc").write_text("{}")
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x = 1;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
    assert "prettier" in stdout.lower()


def test_detects_prettier_in_package_json(tmp_path, run_hook):
    (tmp_path / "package.json").write_text('{"prettier": {"semi": true}}')
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x = 1;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
    assert "prettier" in stdout.lower()


def test_priority_biome_over_prettier(tmp_path, run_hook):
    (tmp_path / "biome.json").write_text("{}")
    (tmp_path / ".prettierrc").write_text("{}")
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x = 1;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
    assert "biome" in stdout.lower()
    assert "prettier" not in stdout.lower()


def test_no_formatter_silent_skip(tmp_path, run_hook):
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x = 1;")

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)}), "DRY_RUN": "1"}
    exit_code, stdout, stderr = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
    assert "error" not in stdout.lower()
    assert "warning" not in stdout.lower()
    assert stdout.strip() == ""


def test_formatter_failure_exits_zero(tmp_path, run_hook):
    # biome not installed → FileNotFoundError caught → exits 0 silently
    (tmp_path / "biome.json").write_text("{}")
    test_file = tmp_path / "test.ts"
    test_file.write_text("const x =")  # invalid syntax

    env = {"TOOL_INPUT": json.dumps({"file_path": str(test_file)})}
    exit_code, stdout, _ = run_hook(SCRIPTS["post_edit_format"], env_overrides=env)

    assert exit_code == 0
