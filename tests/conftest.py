"""Shared fixtures for Vorbit core tests."""

from __future__ import annotations

import subprocess

import pytest


@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def temp_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=project, check=True)
    return project.resolve()
