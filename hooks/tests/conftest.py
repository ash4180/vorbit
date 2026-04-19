#!/usr/bin/env python3
"""Shared pytest fixtures for vorbit hook script tests."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Python version guard
if sys.version_info < (3, 9):
    raise RuntimeError(f"Python 3.9+ required, got {sys.version_info.major}.{sys.version_info.minor}")

# Plugin root: conftest.py → tests/ → hooks/ → project root
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent

# Hook script paths relative to plugin root
SCRIPTS = {
    "pre_push_warning": PLUGIN_ROOT / "hooks" / "scripts" / "pre_push_warning.py",
    "post_edit_format": PLUGIN_ROOT / "hooks" / "scripts" / "post_edit_format.py",
    "post_edit_validate": PLUGIN_ROOT / "hooks" / "scripts" / "post_edit_validate.py",
    "loop_controller": PLUGIN_ROOT / "skills" / "implement-loop" / "hooks" / "loop_controller.py",
}


@pytest.fixture
def plugin_root():
    """Path to the plugin root directory."""
    return PLUGIN_ROOT


@pytest.fixture
def tmp_home(tmp_path):
    """Temporary HOME directory for test isolation.

    Hook scripts that call Path.home() will resolve to this directory
    when HOME is overridden in the subprocess environment.
    """
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def test_project(tmp_path, tmp_home):
    """Temporary git repo with project slug directory in tmp_home.

    Returns a dict with:
      path        - Path to the git repo
      resolved    - Resolved absolute path (macOS /tmp → /private/tmp)
      slug        - Project slug (path with / replaced by -)
      sessions_dir - tmp_home/.claude/projects/<slug>/
      home        - tmp_home path
    """
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=project, check=True)
    # Resolve to handle macOS /tmp → /private/tmp symlink
    resolved = project.resolve()
    slug = str(resolved).replace("/", "-")
    sessions_dir = tmp_home / ".claude" / "projects" / slug
    sessions_dir.mkdir(parents=True)
    return {
        "path": project,
        "resolved": resolved,
        "slug": slug,
        "sessions_dir": sessions_dir,
        "home": tmp_home,
    }


@pytest.fixture
def run_hook():
    """Run a hook script in a subprocess.

    Usage:
        exit_code, stdout, stderr = run_hook(
            script_path,
            stdin="",
            env_overrides={"HOME": str(tmp_home)},
            cwd=project_path,
        )

    Returns (exit_code: int, stdout: str, stderr: str).
    """
    def _run(script_path, stdin="", env_overrides=None, cwd=None):
        env = os.environ.copy()
        if env_overrides:
            env.update({k: str(v) for k, v in env_overrides.items()})
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(cwd) if cwd else None,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


