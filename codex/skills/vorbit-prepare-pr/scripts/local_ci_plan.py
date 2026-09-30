#!/usr/bin/env python3
"""List the commands the repository's pull-request CI runs, so they can run locally first.

Reads every GitHub Actions workflow under .github/workflows/ that triggers on
pull_request (or pull_request_target) for the given base branch, and prints each
`run:` step in job order. Steps are classified so the caller runs the real checks
and skips what only makes sense on a CI machine.

Usage: python3 local_ci_plan.py [--repo <path>] [--base <branch>] [--head <branch>]

Prints JSON: {"workflows": [...], "steps": [...], "tool_versions": [...]}. Each step has:
  workflow, job, step   where the step lives
  kind                  check | setup | gate | skip
                          check: run it locally
                          setup: dependency install; run only when the tools are missing
                          gate:  a summary job reading other jobs' results; nothing to run
                          skip:  prints only, or needs CI secrets or services
  command               the command to run locally (shard flags removed, branch names filled in)
  working_directory     run it from here (relative to the repo root)
  notes                 why a step was skipped or changed
tool_versions lists the runtime versions CI pins (node, python, ...), so the
caller can warn when the local version differs.
Exit codes: 0 when the workflows were read (the list may be empty), 1 on a read error,
2 when PyYAML is missing (read the workflow files directly instead).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - depends on the machine
    print(json.dumps({"error": "PyYAML is not installed. Read .github/workflows/*.yml directly."}))
    sys.exit(2)

PR_EVENTS = ("pull_request", "pull_request_target")
# Bare `yarn` installs, but `yarn lint` runs a script, so yarn only matches with flags.
INSTALL = re.compile(
    r"^(yarn(\s+install)?(\s+--\S+)*"
    r"|(npm (ci|install)|pnpm i(nstall)?|bun install|pip3? install|python3? -m pip install|poetry install"
    r"|uv sync|bundle install|go mod download|npx playwright install(-deps)?)(\s.*)?)$"
)
# A shard value can hold expressions with spaces: --shard=${{ matrix.shard }}/${{ strategy.job-total }}
SHARD_FLAG = re.compile(r"\s*--shard[= ](?=\S*\$\{\{)(\$\{\{[^}]*\}\}|[^\s$])+")
CI_PLUMBING = re.compile(r"\$\{?(GITHUB_OUTPUT|GITHUB_ENV|GITHUB_PATH|GITHUB_STEP_SUMMARY)\b")
EXPRESSION = re.compile(r"\$\{\{\s*([^}]*?)\s*\}\}")
ENV_REF = re.compile(r"^env\.(\w+)$")


def triggers(workflow: dict[Any, Any]) -> Any:
    # PyYAML reads the bare key `on` as boolean True.
    return workflow.get("on", workflow.get(True))


def runs_on_pull_request(workflow: dict[Any, Any], base: str | None) -> bool:
    on = triggers(workflow)
    if isinstance(on, str):
        return on in PR_EVENTS
    if isinstance(on, list):
        return any(event in PR_EVENTS for event in on)
    if not isinstance(on, dict):
        return False
    for event in PR_EVENTS:
        if event not in on:
            continue
        config = on[event] or {}
        branches = config.get("branches") if isinstance(config, dict) else None
        if not base or not branches:
            return True
        if any(fnmatch(base, pattern) for pattern in branches):
            return True
    return False


def is_print_only(command: str) -> bool:
    lines = [line.strip() for line in command.splitlines() if line.strip() and not line.strip().startswith("#")]
    return bool(lines) and all(line.startswith(("echo ", "echo\t", "printf ")) or line == "exit 0" for line in lines)


def resolve_env(value: Any, env: dict[str, Any]) -> str:
    text = str(value)
    match = EXPRESSION.fullmatch(text.strip())
    if match:
        ref = ENV_REF.match(match.group(1))
        if ref and ref.group(1) in env:
            return str(env[ref.group(1)])
    return text


def fill_branches(command: str, branches: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        return branches.get(match.group(1), match.group(0))

    return EXPRESSION.sub(replace, command)


def classify(step: dict[str, Any], job: dict[str, Any], branches: dict[str, str]) -> tuple[str, str, list[str]]:
    command = fill_branches(str(step["run"]).strip(), branches)
    notes: list[str] = []
    condition = str(step.get("if", ""))
    if "needs." in condition or (job.get("needs") and command in ("exit 1", "exit 0")):
        return "gate", command, ["reads other jobs' results; nothing to run locally"]
    if is_print_only(command):
        return "skip", command, ["prints a message only"]
    if "secrets." in command or "secrets." in json.dumps(step.get("env", {}), default=str):
        return "skip", command, ["needs CI secrets"]
    if CI_PLUMBING.search(command) and not any(
        line.strip() and not line.strip().startswith("#") and not CI_PLUMBING.search(line) and "=$(" not in line
        for line in command.splitlines()
    ):
        return "skip", command, ["only passes values between CI steps"]
    if job.get("services"):
        notes.append("CI starts service containers for this job; start them locally or expect a failure")
    if "\n" not in command and INSTALL.match(command):
        return "setup", command, notes
    if SHARD_FLAG.search(command):
        command = SHARD_FLAG.sub("", command)
        notes.append("CI splits this into shards; run it once, whole")
    leftover = EXPRESSION.findall(command)
    if leftover:
        notes.append("contains CI expressions (" + ", ".join(sorted(set(leftover))) + "); replace them before running")
    return "check", command, notes


def tool_versions(step: dict[str, Any], env: dict[str, Any]) -> list[dict[str, str]]:
    uses = str(step.get("uses", ""))
    found = re.match(r"actions/setup-(\w+)@", uses)
    if not found:
        return []
    tool = found.group(1)
    with_block = step.get("with") or {}
    versions = []
    for key, value in with_block.items():
        if key.endswith("-version"):
            versions.append({"tool": tool, "version": resolve_env(value, env)})
    return versions


def plan(repo: Path, base: str | None, head: str | None) -> dict[str, Any]:
    branches = {key: value for key, value in (("github.base_ref", base), ("github.head_ref", head)) if value}
    folder = repo / ".github" / "workflows"
    files = sorted(list(folder.glob("*.yml")) + list(folder.glob("*.yaml"))) if folder.is_dir() else []
    result: dict[str, Any] = {"workflows": [], "steps": [], "tool_versions": []}
    seen_versions: set[tuple[str, str]] = set()
    for path in files:
        workflow = yaml.safe_load(path.read_text()) or {}
        if not isinstance(workflow, dict) or not runs_on_pull_request(workflow, base):
            continue
        name = str(workflow.get("name") or path.name)
        result["workflows"].append({"name": name, "file": str(path.relative_to(repo))})
        env = workflow.get("env") or {}
        defaults = ((workflow.get("defaults") or {}).get("run") or {}).get("working-directory", ".")
        for job_id, job in (workflow.get("jobs") or {}).items():
            job = job or {}
            job_name = str(job.get("name") or job_id)
            job_dir = ((job.get("defaults") or {}).get("run") or {}).get("working-directory", defaults)
            for step in job.get("steps") or []:
                for version in tool_versions(step, {**env, **(job.get("env") or {})}):
                    key = (version["tool"], version["version"])
                    if key not in seen_versions:
                        seen_versions.add(key)
                        result["tool_versions"].append(version)
                if "run" not in step:
                    continue
                kind, command, notes = classify(step, job, branches)
                result["steps"].append({
                    "workflow": name,
                    "job": job_name,
                    "step": str(step.get("name") or command.splitlines()[0]),
                    "kind": kind,
                    "command": command,
                    "working_directory": str(step.get("working-directory", job_dir)),
                    "notes": notes,
                })
    return result


def current_branch(repo: Path) -> str | None:
    result = subprocess.run(["git", "-C", str(repo), "branch", "--show-current"], capture_output=True, text=True)
    return result.stdout.strip() or None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--base", default=None, help="the PR's base branch; filters workflows by their branch list")
    parser.add_argument("--head", default=None, help="the PR's branch; defaults to the checked-out branch")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    head = args.head or current_branch(repo)
    try:
        output = plan(repo, args.base, head)
    except (OSError, yaml.YAMLError) as error:
        print(json.dumps({"error": f"could not read the workflows: {error}"}))
        sys.exit(1)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
