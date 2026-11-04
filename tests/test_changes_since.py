"""The shared changes_since script: a PR's own new commits since a checked commit, on real repos."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/_shared/scripts/changes_since.py"


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return done.stdout.strip()


def commit(repo: Path, name: str, text: str = "one\n") -> str:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", name)
    return git(repo, "rev-parse", "HEAD")


def run(repo: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *arguments], cwd=repo, capture_output=True, text=True,
    )


def changes(repo: Path, *arguments: str) -> dict:
    done = run(repo, *arguments)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout)


@pytest.fixture
def pr(temp_project):
    """main has base.txt; the PR branch has one commit that was already checked."""
    commit(temp_project, "base.txt")
    git(temp_project, "branch", "-M", "main")
    git(temp_project, "checkout", "-q", "-b", "feature")
    checked = commit(temp_project, "app.txt", "a\nb\nc\n")
    return temp_project, checked


def merge_main_with_someone_elses_work(repo: Path) -> None:
    git(repo, "checkout", "-q", "main")
    commit(repo, "other-team.txt", "x\ny\n")
    git(repo, "checkout", "-q", "feature")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge main into feature", "main")


def test_counts_each_new_commit_and_sums_its_lines(pr):
    repo, checked = pr
    commit(repo, "app.txt", "a\nB\nc\n")
    commit(repo, "src/new.ts", "1\n2\n")

    result = changes(repo, checked)

    assert result["status"] == "ok"
    assert result["scope"] == f"Changes since {checked[:7]}: 2 files, +3/-1"
    assert [c["subject"] for c in result["commits"]] == ["app.txt", "src/new.ts"]
    assert result["files"] == [
        {"path": "app.txt", "added": 1, "removed": 1},
        {"path": "src/new.ts", "added": 2, "removed": 0},
    ]
    assert result["totals"] == {"commits": 2, "files": 2, "added": 3, "removed": 1}


@pytest.mark.parametrize("base", [None, "main"])
def test_a_merge_from_the_base_branch_never_counts(pr, base):
    repo, checked = pr
    merge_main_with_someone_elses_work(repo)
    commit(repo, "app.txt", "a\nb\nc\nd\n")
    extra = ["--base", base] if base else []

    result = changes(repo, checked, *extra)
    patches = run(repo, checked, "--diff", *extra).stdout

    assert [c["subject"] for c in result["commits"]] == ["app.txt"]
    assert [f["path"] for f in result["files"]] == ["app.txt"]
    assert result["scope"] == f"Changes since {checked[:7]}: 1 file, +1/-0 (1 merge commit skipped)"
    assert "b/app.txt" in patches and "+d" in patches
    assert "other-team.txt" not in patches and "Merge main" not in patches


def test_with_the_base_a_commit_merged_in_from_the_prs_own_remote_counts(pr):
    """A GitHub suggestion commit, then `git pull` merges it with a local commit."""
    repo, checked = pr
    git(repo, "checkout", "-q", "-b", "remote-feature")
    commit(repo, "suggestion.txt")
    git(repo, "checkout", "-q", "feature")
    commit(repo, "local.txt")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge remote feature", "remote-feature")

    with_base = changes(repo, checked, "--base", "main")
    first_parent_only = changes(repo, checked)

    assert {c["subject"] for c in with_base["commits"]} == {"local.txt", "suggestion.txt"}
    assert [c["subject"] for c in first_parent_only["commits"]] == ["local.txt"]


def test_a_force_push_is_reported_and_gives_no_diff(pr):
    repo, checked = pr
    git(repo, "reset", "-q", "--hard", "main")
    head = commit(repo, "rewritten.txt")

    result = changes(repo, checked)
    diff = run(repo, checked, "--diff")

    assert result["status"] == "not_ancestor"
    assert result["scope"] == f"{checked[:7]} is not in the history of {head[:7]} (force-push or rebase)"
    assert "commits" not in result and "files" not in result
    assert diff.returncode == 3 and diff.stdout == ""
    assert "force-push or rebase" in diff.stderr


def test_a_commit_this_repository_does_not_have_is_reported(pr):
    repo, _ = pr
    result = changes(repo, "1" * 40)
    assert result["status"] == "unknown_commit"
    assert result["scope"] == f"Commit {'1' * 40} is not in this repository"


def test_nothing_new_since_the_checked_commit(pr):
    repo, checked = pr
    assert changes(repo, checked)["scope"] == f"No new commits since {checked[:7]}"

    merge_main_with_someone_elses_work(repo)
    only_a_merge = changes(repo, checked, "--base", "main")

    assert only_a_merge["status"] == "no_new_commits"
    assert only_a_merge["merges_skipped"] == 1
    assert only_a_merge["scope"] == f"No new commits since {checked[:7]} (1 merge commit skipped)"


def test_a_renamed_file_is_one_file_and_a_binary_file_adds_no_lines(pr):
    repo, checked = pr
    git(repo, "mv", "app.txt", "renamed.txt")
    (repo / "renamed.txt").write_text("a\nb\nC\n")
    (repo / "logo.png").write_bytes(b"\x00\x01\x02")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "rename")

    result = changes(repo, checked)

    assert result["files"] == [
        {"path": "logo.png", "added": 0, "removed": 0, "binary": True},
        {"path": "renamed.txt", "added": 1, "removed": 1, "renamed_from": "app.txt"},
    ]
    assert result["scope"] == f"Changes since {checked[:7]}: 2 files, +1/-1"


def test_a_head_older_than_the_checked_commit_is_not_new_work(pr):
    repo, checked = pr
    newer = commit(repo, "later.txt")
    result = changes(repo, newer, "--head", checked)
    assert result["status"] == "not_ancestor"


def test_a_base_that_does_not_resolve_is_an_error(pr):
    repo, checked = pr
    done = run(repo, checked, "--base", "origin/missing")
    assert done.returncode == 1
    assert json.loads(done.stdout) == {"error": "--base origin/missing is not a commit in this repository"}


@pytest.mark.parametrize("skill", ["review", "qa-plan"])
def test_both_skills_call_the_script_by_a_path_that_exists(skill):
    canonical = ROOT / "skills" / skill / "SKILL.md"
    projected = [ROOT / agent / "skills/vorbit-shared/workflows" / f"{skill}.md" for agent in ("codex", "gemini")]
    for document in (canonical, *projected):
        paths = re.findall(r"python3 (\.\./\S+/changes_since\.py)", document.read_text())
        assert paths, f"{document} does not call changes_since.py"
        for path in paths:
            assert (document.parent / path).resolve().is_file(), (document, path)
