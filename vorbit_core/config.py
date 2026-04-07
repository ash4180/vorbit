"""Vorbit configuration resolution."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - exercised on 3.9/3.10
    tomllib = None


def _parse_toml_value(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _parse_toml_fallback(text: str) -> dict[str, Any]:
    """Parse a small TOML subset used by Vorbit config files."""
    data: dict[str, Any] = {}
    cursor = data
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = [part.strip() for part in line[1:-1].split(".") if part.strip()]
            cursor = data
            for part in section:
                cursor = cursor.setdefault(part, {})
            continue
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        cursor[key.strip()] = _parse_toml_value(raw_value)
    return data


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        content = path.read_bytes()
    except OSError:
        return {}
    if tomllib is not None:
        try:
            return tomllib.loads(content.decode("utf-8"))
        except Exception:
            return {}
    try:
        return _parse_toml_fallback(content.decode("utf-8"))
    except Exception:
        return {}


def _nested_get(data: dict[str, Any], *parts: str) -> Any:
    current: Any = data
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def default_legacy_obsidian_vault(home: Path | None = None) -> Path:
    base = (home or Path.home()).expanduser()
    return base / "Projects" / "Thinking-Labs"


@dataclass
class ObsidianConfig:
    enabled: bool = False
    vault_path: Path | None = None


@dataclass
class LearnConfig:
    enabled: bool = True
    review_required: bool = True


@dataclass
class RuleLoadingConfig:
    include_universal: bool = True
    include_project: bool = True
    include_agent_local: bool = True


@dataclass
class VorbitConfig:
    storage_root: Path
    project_root: Path | None = None
    project_slug: str | None = None
    project_name: str | None = None
    learn: LearnConfig = field(default_factory=LearnConfig)
    obsidian: ObsidianConfig = field(default_factory=ObsidianConfig)
    rule_loading: RuleLoadingConfig = field(default_factory=RuleLoadingConfig)
    legacy_claude_bridge: bool = False


def project_slug_for(project_root: Path, override: str | None = None) -> str:
    if override:
        return override
    resolved = project_root.resolve()
    name = _slugify(resolved.name) or "project"
    digest = hashlib.sha1(str(resolved).encode("utf-8")).hexdigest()[:8]
    return f"{name}-{digest}"


def _resolve_storage_root(
    home: Path,
    global_config: dict[str, Any],
) -> Path:
    env_root = os.environ.get("VORBIT_HOME", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    config_root = _nested_get(global_config, "storage", "root")
    if isinstance(config_root, str) and config_root.strip():
        return Path(config_root).expanduser().resolve()
    return (home / ".vorbit").resolve()


def resolve_config(
    project_root: str | Path | None = None,
    *,
    force_obsidian: bool = False,
    legacy_claude_bridge: bool = False,
) -> VorbitConfig:
    home = Path.home().expanduser()
    global_config = _load_toml(home / ".vorbit" / "config.toml")

    project_path: Path | None = None
    project_config: dict[str, Any] = {}
    if project_root is not None:
        project_path = Path(project_root).expanduser().resolve()
        project_config = _load_toml(project_path / ".vorbit" / "config.toml")

    storage_root = _resolve_storage_root(home, global_config)
    storage_root.mkdir(parents=True, exist_ok=True)

    global_obsidian_enabled = _nested_get(global_config, "exporters", "obsidian", "enabled")
    project_obsidian_enabled = _nested_get(project_config, "exporters", "obsidian", "enabled")
    obsidian_enabled = bool(
        project_obsidian_enabled
        if project_obsidian_enabled is not None
        else global_obsidian_enabled
        if global_obsidian_enabled is not None
        else False
    )

    global_vault = _nested_get(global_config, "exporters", "obsidian", "vault_path")
    project_vault = _nested_get(project_config, "exporters", "obsidian", "vault_path")
    vault_value = project_vault if isinstance(project_vault, str) else global_vault
    vault_path = Path(vault_value).expanduser().resolve() if isinstance(vault_value, str) and vault_value else None

    # legacy_claude_bridge and force_obsidian enable Obsidian if not already
    # configured, but never override user-configured vault_path
    if legacy_claude_bridge or force_obsidian:
        obsidian_enabled = True
        if vault_path is None:
            vault_path = default_legacy_obsidian_vault(home).resolve()

    learn_enabled = _nested_get(project_config, "learn", "enabled")
    if learn_enabled is None:
        learn_enabled = _nested_get(global_config, "learn", "enabled")
    review_required = _nested_get(project_config, "learn", "review_required")
    if review_required is None:
        review_required = _nested_get(global_config, "learn", "review_required")

    project_slug = None
    project_name = None
    if project_path is not None:
        project_name = project_path.resolve().name
        override_slug = _nested_get(project_config, "project", "slug")
        if not isinstance(override_slug, str):
            override_slug = None
        project_slug = project_slug_for(project_path, override=override_slug)

    return VorbitConfig(
        storage_root=storage_root,
        project_root=project_path,
        project_slug=project_slug,
        project_name=project_name,
        learn=LearnConfig(
            enabled=True if learn_enabled is None else bool(learn_enabled),
            review_required=True if review_required is None else bool(review_required),
        ),
        obsidian=ObsidianConfig(enabled=obsidian_enabled, vault_path=vault_path),
        rule_loading=RuleLoadingConfig(
            include_universal=bool(
                _nested_get(project_config, "rule_loading", "include_universal")
                if _nested_get(project_config, "rule_loading", "include_universal") is not None
                else _nested_get(global_config, "rule_loading", "include_universal")
                if _nested_get(global_config, "rule_loading", "include_universal") is not None
                else True
            ),
            include_project=bool(
                _nested_get(project_config, "rule_loading", "include_project")
                if _nested_get(project_config, "rule_loading", "include_project") is not None
                else _nested_get(global_config, "rule_loading", "include_project")
                if _nested_get(global_config, "rule_loading", "include_project") is not None
                else True
            ),
            include_agent_local=bool(
                _nested_get(project_config, "rule_loading", "include_agent_local")
                if _nested_get(project_config, "rule_loading", "include_agent_local") is not None
                else _nested_get(global_config, "rule_loading", "include_agent_local")
                if _nested_get(global_config, "rule_loading", "include_agent_local") is not None
                else True
            ),
        ),
        legacy_claude_bridge=legacy_claude_bridge,
    )

