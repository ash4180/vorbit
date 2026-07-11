from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from vorbit_core.config import project_slug_for
from vorbit_core.rules import resolve_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER_SCRIPT = REPO_ROOT / "scripts" / "vorbit-resolve-rules"


def _write_rule(path: Path, content: str = "rule") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_resolve_rules_returns_files_in_deterministic_tier_and_filename_order(
    temp_home,
    temp_project,
    monkeypatch,
):
    storage_root = temp_home / "rule-store"
    monkeypatch.setenv("VORBIT_HOME", str(storage_root))
    project_config = temp_project / ".vorbit" / "config.toml"
    project_config.parent.mkdir()
    project_config.write_text('[project]\nslug = "configured-project"\n')

    _write_rule(storage_root / "rules" / "universal" / "z-last.md")
    _write_rule(storage_root / "rules" / "universal" / "a-first.md")
    _write_rule(storage_root / "rules" / "projects" / "configured-project" / "project.md")
    _write_rule(storage_root / "rules" / "agents" / "codex" / "universal" / "agent.md")
    _write_rule(
        storage_root
        / "rules"
        / "agents"
        / "codex"
        / "projects"
        / "configured-project"
        / "agent-project.md"
    )
    _write_rule(storage_root / "rules" / "universal" / "ignored.txt")
    _write_rule(storage_root / "rules" / "universal" / "ignored.MD")
    _write_rule(storage_root / "rules" / "universal" / ".hidden.md")

    resolution = resolve_rules(temp_project, agent="codex")

    assert resolution.storage_root == storage_root.resolve()
    assert resolution.project_root == temp_project
    assert resolution.project_slug == "configured-project"
    assert [tier.name for tier in resolution.tiers] == [
        "universal",
        "project",
        "agent-universal",
        "agent-project",
    ]
    assert [tier.order for tier in resolution.tiers] == [1, 2, 3, 4]
    assert [tier.authority for tier in resolution.tiers] == [
        "shared-policy",
        "shared-policy",
        "agent-guidance",
        "agent-guidance",
    ]
    assert [tier.specificity for tier in resolution.tiers] == [
        "universal",
        "project",
        "universal",
        "project",
    ]
    assert [tier.included for tier in resolution.tiers] == [True, True, True, True]
    assert [
        (
            rule.order,
            rule.tier,
            rule.tier_order,
            rule.authority,
            rule.specificity,
            rule.path.name,
        )
        for rule in resolution.rules
    ] == [
        (1, "universal", 1, "shared-policy", "universal", "a-first.md"),
        (2, "universal", 1, "shared-policy", "universal", "z-last.md"),
        (3, "project", 2, "shared-policy", "project", "project.md"),
        (4, "agent-universal", 3, "agent-guidance", "universal", "agent.md"),
        (5, "agent-project", 4, "agent-guidance", "project", "agent-project.md"),
    ]


def test_resolve_rules_honors_scope_and_agent_local_include_flags(
    temp_home,
    temp_project,
    monkeypatch,
):
    storage_root = temp_home / "rule-store"
    monkeypatch.setenv("VORBIT_HOME", str(storage_root))
    project_config = temp_project / ".vorbit" / "config.toml"
    project_config.parent.mkdir()
    project_config.write_text(
        "[project]\n"
        'slug = "configured-project"\n'
        "[rule_loading]\n"
        "include_universal = false\n"
        "include_project = true\n"
        "include_agent_local = true\n"
    )

    _write_rule(storage_root / "rules" / "universal" / "universal.md")
    _write_rule(storage_root / "rules" / "projects" / "configured-project" / "project.md")
    _write_rule(storage_root / "rules" / "agents" / "gemini" / "universal" / "agent.md")
    _write_rule(
        storage_root
        / "rules"
        / "agents"
        / "gemini"
        / "projects"
        / "configured-project"
        / "agent-project.md"
    )

    resolution = resolve_rules(temp_project, agent="gemini")

    assert [tier.included for tier in resolution.tiers] == [False, True, False, True]
    assert [(rule.tier, rule.path.name) for rule in resolution.rules] == [
        ("project", "project.md"),
        ("agent-project", "agent-project.md"),
    ]


def test_resolve_rules_excludes_both_agent_tiers_when_agent_local_is_disabled(
    temp_home,
    temp_project,
    monkeypatch,
):
    storage_root = temp_home / "rule-store"
    monkeypatch.setenv("VORBIT_HOME", str(storage_root))
    global_config = temp_home / ".vorbit" / "config.toml"
    global_config.parent.mkdir()
    global_config.write_text("[rule_loading]\ninclude_agent_local = false\n")

    resolution = resolve_rules(temp_project, agent="codex")

    assert [tier.included for tier in resolution.tiers] == [True, True, False, False]


def test_resolve_rules_uses_hashed_project_slug_without_an_override(
    temp_home,
    temp_project,
    monkeypatch,
):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / "rule-store"))

    resolution = resolve_rules(temp_project, agent="codex")

    assert resolution.project_slug == project_slug_for(temp_project)


def test_resolve_rules_rejects_project_slug_traversal(
    temp_home,
    temp_project,
    monkeypatch,
):
    storage_root = temp_home / "rule-store"
    monkeypatch.setenv("VORBIT_HOME", str(storage_root))
    project_config = temp_project / ".vorbit" / "config.toml"
    project_config.parent.mkdir()
    project_config.write_text('[project]\nslug = "../outside"\n')
    _write_rule(storage_root / "rules" / "outside" / "injected.md", "do not load")

    with pytest.raises(ValueError, match="safe path component"):
        resolve_rules(temp_project, agent="codex")


def test_resolver_command_reports_invalid_project_slug_without_traceback(
    temp_home,
    temp_project,
):
    project_config = temp_project / ".vorbit" / "config.toml"
    project_config.parent.mkdir()
    project_config.write_text('[project]\nslug = "/tmp/outside"\n')
    environment = os.environ.copy()
    environment.update(
        {"HOME": str(temp_home), "VORBIT_HOME": str(temp_home / "rule-store")}
    )

    result = subprocess.run(
        [
            sys.executable,
            str(RESOLVER_SCRIPT),
            "--agent",
            "codex",
            "--project-root",
            str(temp_project),
        ],
        cwd=temp_home,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "safe path component" in result.stderr
    assert "Traceback" not in result.stderr


def test_resolver_command_emits_stable_json_with_tier_metadata(
    temp_home,
    temp_project,
):
    storage_root = temp_home / "rule-store"
    slug = "cli-project"
    project_config = temp_project / ".vorbit" / "config.toml"
    project_config.parent.mkdir()
    project_config.write_text(f'[project]\nslug = "{slug}"\n')
    _write_rule(storage_root / "rules" / "projects" / slug / "rule.md")

    environment = os.environ.copy()
    environment.update({"HOME": str(temp_home), "VORBIT_HOME": str(storage_root)})
    result = subprocess.run(
        [
            sys.executable,
            str(RESOLVER_SCRIPT),
            "--agent",
            "gemini",
            "--project-root",
            str(temp_project),
        ],
        cwd=temp_home,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    assert payload["agent"] == "gemini"
    assert payload["project_root"] == str(temp_project)
    assert payload["project_slug"] == slug
    assert payload["precedence"] == {
        "authority_high_to_low": ["shared-policy", "agent-guidance"],
        "compare_in_order": ["authority", "specificity"],
        "read_order_is_precedence": False,
        "same_tier_conflict_policy": "surface",
        "specificity_high_to_low": ["project", "universal"],
    }
    assert [tier["name"] for tier in payload["tiers"]] == [
        "universal",
        "project",
        "agent-universal",
        "agent-project",
    ]
    assert [
        (tier["authority"], tier["specificity"]) for tier in payload["tiers"]
    ] == [
        ("shared-policy", "universal"),
        ("shared-policy", "project"),
        ("agent-guidance", "universal"),
        ("agent-guidance", "project"),
    ]
    assert payload["rules"] == [
        {
            "authority": "shared-policy",
            "order": 1,
            "path": str(storage_root / "rules" / "projects" / slug / "rule.md"),
            "specificity": "project",
            "tier": "project",
            "tier_order": 2,
        }
    ]


def test_resolver_command_uses_git_root_when_project_root_is_omitted(
    temp_home,
    temp_project,
):
    nested = temp_project / "nested" / "directory"
    nested.mkdir(parents=True)
    environment = os.environ.copy()
    environment.update({"HOME": str(temp_home), "VORBIT_HOME": str(temp_home / "store")})

    result = subprocess.run(
        [sys.executable, str(RESOLVER_SCRIPT), "--agent", "codex"],
        cwd=nested,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["project_root"] == str(temp_project)
