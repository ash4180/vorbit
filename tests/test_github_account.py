from __future__ import annotations

import pytest

from vorbit_core.github import GitHubAccountError, remote_owner, select_account


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("https://github.com/ash4180/vorbit.git", "ash4180"),
        ("https://ash4180@github.com/ash4180/vorbit.git", "ash4180"),
        ("git@github.com:Vibe-Ash/client.git", "Vibe-Ash"),
        ("ssh://git@github.com/Vibe-Ash/client.git", "Vibe-Ash"),
    ],
)
def test_remote_owner_reads_common_github_urls(remote, expected):
    assert remote_owner(remote) == expected


def test_remote_owner_rejects_non_github_urls():
    with pytest.raises(GitHubAccountError, match="unsupported GitHub remote"):
        remote_owner("https://gitlab.com/ash4180/vorbit.git")


def test_select_account_matches_owner_without_case_sensitivity():
    assert select_account("vibe-ash", ["ash4180", "Vibe-Ash"]) == "Vibe-Ash"


def test_select_account_rejects_an_owner_without_a_matching_login():
    with pytest.raises(GitHubAccountError, match="no saved GitHub login matches"):
        select_account("another-org", ["ash4180", "Vibe-Ash"])
