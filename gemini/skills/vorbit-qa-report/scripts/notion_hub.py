#!/usr/bin/env python3
"""Print the Notion QA report hub saved for this repository.

The hub list lives in ~/.vorbit/qa-report-hubs.json. It is keyed by the
owner/repo of the origin remote, so every worktree and clone finds the same hub:

    {"vibraniumlabs/client": "https://app.notion.com/p/<hub database id>"}

Usage: python3 notion_hub.py [--repo-dir <path>]

Prints JSON: {"repo", "hub", "settings"}, plus "error" on exit 1. hub is null
when this repository has no saved hub.
Exit codes: 0 when the lookup ran, 1 when the hub list cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def repo_key(remote_url: str) -> str | None:
    path = remote_url.strip().rstrip("/").removesuffix(".git")
    parts = [part for part in re.split(r"[/:]", path) if part]
    return "/".join(parts[-2:]).lower() if len(parts) >= 2 else None


def origin_url(repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", type=Path, default=Path.cwd())
    args = parser.parse_args()

    settings = Path.home() / ".vorbit" / "qa-report-hubs.json"
    output = {"repo": repo_key(origin_url(args.repo_dir)), "hub": None, "settings": str(settings)}
    try:
        hubs = json.loads(settings.read_text()) if settings.is_file() else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(json.dumps({**output, "error": f"cannot read the hub list: {error}"}))
        return 1
    if not isinstance(hubs, dict) or not all(isinstance(url, str) for url in hubs.values()):
        print(json.dumps({**output, "error": 'the hub list must look like {"owner/repo": "hub URL"}'}))
        return 1

    output["hub"] = next((url for key, url in hubs.items() if key.lower() == output["repo"]), None)
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
