from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from vorbit_core.sync import build_sync_plan


REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER_SCRIPT = REPO_ROOT / "scripts" / "vorbit-resolve-rules"


def _run_sync(
    agent: str,
    agent_home: Path,
    temp_home: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["HOME"] = str(temp_home)
    environment[f"{agent.upper()}_HOME"] = str(agent_home)
    return subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / f"sync-{agent}-skills.sh"), *arguments],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("agent", ["codex", "gemini"])
def test_sync_installs_every_current_skill_and_rule_resolver_resource(
    agent,
    temp_home,
):
    agent_home = temp_home / f".{agent}"

    result = _run_sync(agent, agent_home, temp_home)

    assert result.returncode == 0, result.stderr
    source_skills = REPO_ROOT / agent / "skills"
    for source in sorted(source_skills.iterdir()):
        installed = agent_home / "skills" / source.name
        assert installed.is_symlink()
        assert installed.resolve() == source.resolve()
    installed_resolver = agent_home / "bin" / "vorbit-resolve-rules"
    assert installed_resolver.is_symlink()
    assert installed_resolver.resolve() == RESOLVER_SCRIPT.resolve()
    resolver_environment = os.environ.copy()
    resolver_environment.update(
        {"HOME": str(temp_home), "VORBIT_HOME": str(temp_home / "rule-store")}
    )
    resolver_result = subprocess.run(
        [
            str(installed_resolver),
            "--agent",
            agent,
            "--project-root",
            str(temp_home),
        ],
        env=resolver_environment,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(resolver_result.stdout)["agent"] == agent

    manifest = json.loads((agent_home / ".vorbit-managed-links.json").read_text())
    assert manifest["schema_version"] == 1
    assert manifest["agent"] == agent
    assert manifest["links"]["bin/vorbit-resolve-rules"] == str(RESOLVER_SCRIPT.resolve())
    assert set(manifest["links"]) == {
        "bin/vorbit-resolve-rules",
        *(f"skills/{source.name}" for source in source_skills.iterdir()),
    }


def test_sync_prunes_only_manifest_owned_and_legacy_repo_owned_stale_links(
    temp_home,
):
    agent = "codex"
    agent_home = temp_home / ".codex"
    skills_dir = agent_home / "skills"
    skills_dir.mkdir(parents=True)
    foreign_source = temp_home / "foreign-skill"
    foreign_source.mkdir()
    user_link = skills_dir / "vorbit-user-owned"
    user_link.symlink_to(foreign_source)
    legacy_stale = skills_dir / "vorbit-legacy-stale"
    legacy_stale.symlink_to(REPO_ROOT / "codex" / "skills" / "vorbit-legacy-stale")

    first_result = _run_sync(agent, agent_home, temp_home)

    assert first_result.returncode == 0, first_result.stderr
    assert user_link.is_symlink()
    assert user_link.resolve() == foreign_source
    assert not os.path.lexists(legacy_stale)

    manifest_path = agent_home / ".vorbit-managed-links.json"
    manifest = json.loads(manifest_path.read_text())
    manifest_owned = skills_dir / "vorbit-manifest-stale"
    manifest_owned.symlink_to(foreign_source)
    manifest["links"]["skills/vorbit-manifest-stale"] = str(foreign_source)
    manifest_path.write_text(json.dumps(manifest))

    second_result = _run_sync(agent, agent_home, temp_home)

    assert second_result.returncode == 0, second_result.stderr
    assert not os.path.lexists(manifest_owned)
    assert user_link.is_symlink()


def test_sync_refuses_to_replace_an_unowned_colliding_link(temp_home):
    agent_home = temp_home / ".gemini"
    skills_dir = agent_home / "skills"
    skills_dir.mkdir(parents=True)
    source_name = next(iter(sorted((REPO_ROOT / "gemini" / "skills").iterdir()))).name
    foreign_source = temp_home / "foreign-skill"
    foreign_source.mkdir()
    collision = skills_dir / source_name
    collision.symlink_to(foreign_source)

    result = _run_sync("gemini", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to replace unowned symlink" in result.stderr
    assert collision.is_symlink()
    assert collision.resolve() == foreign_source
    assert not (agent_home / ".vorbit-managed-links.json").exists()


def test_sync_refuses_to_replace_a_managed_link_retargeted_by_the_user(temp_home):
    agent_home = temp_home / ".codex"
    initial_result = _run_sync("codex", agent_home, temp_home)
    assert initial_result.returncode == 0, initial_result.stderr

    source_name = next(iter(sorted((REPO_ROOT / "codex" / "skills").iterdir()))).name
    managed_link = agent_home / "skills" / source_name
    foreign_source = temp_home / "foreign-skill"
    foreign_source.mkdir()
    managed_link.unlink()
    managed_link.symlink_to(foreign_source)

    result = _run_sync("codex", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to replace unowned symlink" in result.stderr
    assert managed_link.is_symlink()
    assert managed_link.resolve() == foreign_source


def test_sync_refuses_to_prune_a_retargeted_managed_link(temp_home):
    agent_home = temp_home / ".gemini"
    initial_result = _run_sync("gemini", agent_home, temp_home)
    assert initial_result.returncode == 0, initial_result.stderr

    stale = agent_home / "skills" / "vorbit-stale"
    recorded_source = temp_home / "old-source"
    recorded_source.mkdir()
    stale.symlink_to(recorded_source)
    manifest_path = agent_home / ".vorbit-managed-links.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["links"]["skills/vorbit-stale"] = str(recorded_source)
    manifest_path.write_text(json.dumps(manifest))

    foreign_source = temp_home / "foreign-skill"
    foreign_source.mkdir()
    stale.unlink()
    stale.symlink_to(foreign_source)

    result = _run_sync("gemini", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to prune retargeted managed symlink" in result.stderr
    assert stale.is_symlink()
    assert stale.resolve() == foreign_source


def test_sync_refuses_to_replace_a_regular_directory_at_a_skill_path(temp_home):
    agent_home = temp_home / ".codex"
    skills_dir = agent_home / "skills"
    skills_dir.mkdir(parents=True)
    source_name = next(iter(sorted((REPO_ROOT / "codex" / "skills").iterdir()))).name
    collision = skills_dir / source_name
    collision.mkdir()
    marker = collision / "user-data.txt"
    marker.write_text("keep me")

    result = _run_sync("codex", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to replace non-symlink path" in result.stderr
    assert marker.read_text() == "keep me"
    assert not (agent_home / ".vorbit-managed-links.json").exists()


def test_sync_refuses_to_prune_a_manifest_path_that_is_no_longer_a_link(temp_home):
    agent_home = temp_home / ".gemini"
    initial_result = _run_sync("gemini", agent_home, temp_home)
    assert initial_result.returncode == 0, initial_result.stderr

    stale = agent_home / "skills" / "vorbit-stale"
    stale.mkdir()
    marker = stale / "user-data.txt"
    marker.write_text("keep me")
    manifest_path = agent_home / ".vorbit-managed-links.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["links"]["skills/vorbit-stale"] = str(temp_home / "old-source")
    manifest_path.write_text(json.dumps(manifest))

    result = _run_sync("gemini", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to prune managed path that is not a symlink" in result.stderr
    assert marker.read_text() == "keep me"


def test_sync_refuses_a_non_directory_install_root_without_partial_changes(temp_home):
    agent_home = temp_home / ".codex"
    agent_home.mkdir()
    skills_path = agent_home / "skills"
    skills_path.write_text("user data")

    result = _run_sync("codex", agent_home, temp_home)

    assert result.returncode != 0
    assert "refusing to use non-directory install root" in result.stderr
    assert skills_path.read_text() == "user data"
    assert not (agent_home / "bin").exists()
    assert not (agent_home / ".vorbit-managed-links.json").exists()


def test_legacy_link_under_a_symlinked_repo_spelling_is_not_a_false_conflict(tmp_path):
    # Reproduce the first-run-over-legacy-links case: the repo is addressed
    # through a symlink (a different spelling than the link's resolved target),
    # and no manifest exists yet. The link is genuinely Vorbit-owned and must
    # be adopted, not misclassified as an unowned collision.
    linked_repo = tmp_path / "linked-vorbit"
    linked_repo.symlink_to(REPO_ROOT)
    agent_home = tmp_path / ".codex"
    (agent_home / "skills").mkdir(parents=True)
    skill_name = next(iter(sorted((REPO_ROOT / "codex" / "skills").iterdir()))).name
    legacy_link = agent_home / "skills" / skill_name
    legacy_link.symlink_to((REPO_ROOT / "codex" / "skills" / skill_name).resolve())

    plan = build_sync_plan(linked_repo, agent_home, "codex")

    assert plan.conflicts == ()
    replaced = {action.relative_path for action in plan.actions if action.kind == "replace"}
    assert f"skills/{skill_name}" not in replaced


def test_sync_check_and_dry_run_report_drift_without_writing(temp_home):
    agent_home = temp_home / ".codex"

    check_before = _run_sync("codex", agent_home, temp_home, "--check")
    dry_run = _run_sync("codex", agent_home, temp_home, "--dry-run")

    assert check_before.returncode == 1
    assert "sync required" in check_before.stdout
    assert dry_run.returncode == 0
    assert "would link" in dry_run.stdout
    assert not agent_home.exists()

    sync_result = _run_sync("codex", agent_home, temp_home)
    check_after = _run_sync("codex", agent_home, temp_home, "--check")

    assert sync_result.returncode == 0, sync_result.stderr
    assert check_after.returncode == 0, check_after.stderr
    assert "up to date" in check_after.stdout
