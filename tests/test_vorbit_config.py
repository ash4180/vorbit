from __future__ import annotations

from pathlib import Path

from vorbit_core.config import project_slug_for, resolve_config


def test_vorbit_home_env_overrides_global_config(temp_home, temp_project, monkeypatch):
    config_dir = temp_home / ".vorbit"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text('[storage]\nroot = "/tmp/should-not-win"\n')

    override_root = temp_home / "custom-store"
    monkeypatch.setenv("VORBIT_HOME", str(override_root))

    config = resolve_config(temp_project)

    assert config.storage_root == override_root.resolve()


def test_global_config_storage_root_used_when_env_missing(temp_home, temp_project, monkeypatch):
    monkeypatch.delenv("VORBIT_HOME", raising=False)
    config_dir = temp_home / ".vorbit"
    config_dir.mkdir()
    configured = temp_home / "configured-store"
    (config_dir / "config.toml").write_text(f'[storage]\nroot = "{configured}"\n')

    config = resolve_config(temp_project)

    assert config.storage_root == configured.resolve()


def test_project_slug_is_stable_and_hashed(temp_project):
    slug = project_slug_for(temp_project)
    assert slug.startswith("project-")
    assert len(slug.split("-")[-1]) == 8
