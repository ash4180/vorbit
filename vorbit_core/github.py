"""Select the GitHub login that matches a repository owner."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import urlsplit


class GitHubAccountError(RuntimeError):
    """Raised when Vorbit cannot choose a safe GitHub login."""


def remote_owner(remote: str) -> str:
    value = remote.strip()
    if "://" in value:
        parsed = urlsplit(value)
        if parsed.hostname is None or parsed.hostname.casefold() != "github.com":
            raise GitHubAccountError(f"unsupported GitHub remote: {remote}")
        path = parsed.path
    else:
        prefix, separator, path = value.partition(":")
        host = prefix.rsplit("@", 1)[-1]
        if not separator or host.casefold() != "github.com":
            raise GitHubAccountError(f"unsupported GitHub remote: {remote}")

    owner = path.strip("/").partition("/")[0]
    if not owner:
        raise GitHubAccountError(f"unsupported GitHub remote: {remote}")
    return owner


def select_account(owner: str, accounts: Sequence[str]) -> str:
    matches = [account for account in accounts if account.casefold() == owner.casefold()]
    if len(matches) != 1:
        raise GitHubAccountError(
            f"no saved GitHub login matches repository owner {owner!r}"
        )
    return matches[0]


def _required_command(name: str) -> str:
    command = shutil.which(name)
    if command is None:
        raise GitHubAccountError(f"required command is not installed: {name}")
    return command


def _run(command: Sequence[str], cwd: Optional[Path] = None) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise GitHubAccountError(message)
    return result.stdout.strip()


def saved_accounts(gh: str) -> list[str]:
    raw_status = _run([gh, "auth", "status", "--json", "hosts"])
    try:
        hosts = json.loads(raw_status)["hosts"]
        entries = hosts["github.com"]
        accounts = [entry["login"] for entry in entries if entry.get("login")]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise GitHubAccountError("GitHub CLI returned invalid account data") from error
    if not accounts:
        raise GitHubAccountError("GitHub CLI has no saved github.com login")
    return accounts


def account_for_project(project_root: Path) -> tuple[str, str]:
    git = _required_command("git")
    gh = _required_command("gh")
    remote = _run([git, "remote", "get-url", "origin"], cwd=project_root)
    account = select_account(remote_owner(remote), saved_accounts(gh))
    return account, gh


def run_mcp_server(project_root: Path) -> int:
    account, gh = account_for_project(project_root)
    server = _required_command("github-mcp-server")
    token = _run([gh, "auth", "token", "--user", account])
    environment = os.environ.copy()
    environment["GITHUB_PERSONAL_ACCESS_TOKEN"] = token
    os.execvpe(server, [server, "stdio"], environment)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Start GitHub MCP with the login matching this repository owner."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--print-account", action="store_true")
    arguments = parser.parse_args(argv)

    try:
        if arguments.print_account:
            account, _ = account_for_project(arguments.project_root)
            print(account)
            return 0
        return run_mcp_server(arguments.project_root)
    except (OSError, GitHubAccountError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised through the script
    raise SystemExit(main())
