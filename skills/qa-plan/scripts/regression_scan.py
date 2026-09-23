#!/usr/bin/env python3
"""Collect regression inputs for the qa-plan skill when epic.md is missing.

Read-only. Prints one JSON object with:
- the base branch the diff was taken against, and how it was chosen
- every file this branch modified (created files are skipped), each with the
  other files that import it, grouped by folder so the plan can name features
- the project's automated E2E suite command, when one exists

Usage: python3 regression_scan.py [--base <ref>]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".py"}
JS_INDEX_NAMES = {"index"}
MAX_CONSUMERS_LISTED = 25
E2E_RUNNER = re.compile(r"\b(playwright\s+test|cypress\s+run|wdio|testcafe|nightwatch)\b")
E2E_NAME = re.compile(r"(^|:)(e2e|playwright|cypress)(:|$)")
# Script variants that open a UI, seed data, show a report, or aim at a remote env.
E2E_EXCLUDE = re.compile(r"(--ui\b|--headed\b|show-report|\bopen\b|seed|:ui$|:report$|:seed)")
JS_SPECIFIER = re.compile(
    r"""(?:from\s+|import\s*\(\s*|require\s*\(\s*|import\s+)['"]([^'"]+)['"]"""
)
# Test and story files import shared code too, but they are not features.
NOT_A_FEATURE = re.compile(r"(__tests__/|__mocks__/|(^|/)(e2e|tests?)/|\.(test|spec|stories)\.)")
PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def ref_exists(ref: str) -> bool:
    return bool(git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"))


def resolve_base(explicit: str | None) -> tuple[str, str]:
    if explicit:
        return explicit, "given by the caller"
    try:
        pr = subprocess.run(
            ["gh", "pr", "view", "--json", "baseRefName", "-q", ".baseRefName"],
            capture_output=True, text=True, timeout=20,
        )
        name = pr.stdout.strip()
        if pr.returncode == 0 and name:
            for ref in (f"origin/{name}", name):
                if ref_exists(ref):
                    return ref, "base branch of the open pull request"
    except (OSError, subprocess.TimeoutExpired):
        pass
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if head and ref_exists(head):
        return head, "default branch of the remote"
    for ref in ("origin/main", "origin/master", "main", "master"):
        if ref_exists(ref):
            return ref, "fallback: first of main/master found"
    return "", "no base branch found"


def changed_files(base: str) -> tuple[list[str], list[str], list[str]]:
    merge_base = git("merge-base", base, "HEAD") or base
    modified: list[str] = []
    created: list[str] = []
    deleted: list[str] = []
    for line in git("diff", "--name-status", "-M", merge_base, "HEAD").splitlines():
        parts = line.split("\t")
        status = parts[0][:1]
        if status == "A":
            created.append(parts[-1])
        elif status == "D":
            deleted.append(parts[-1])
        elif status in {"M", "R", "T"}:
            modified.append(parts[-1])
    return modified, created, deleted


def module_key(path: str) -> PurePosixPath:
    """The path an import would name: no code suffix, and no trailing /index."""
    pure = PurePosixPath(path)
    if pure.suffix in CODE_SUFFIXES:
        pure = pure.with_suffix("")
    return pure.parent if pure.name in JS_INDEX_NAMES else pure


def resolve_js(importer: str, specifier: str, targets: dict[PurePosixPath, str]) -> list[str]:
    spec = specifier.split("?")[0]
    if spec.startswith("."):
        joined = PurePosixPath(importer).parent / spec
        parts: list[str] = []
        for part in joined.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        key = module_key("/".join(parts)) if parts else None
        return [targets[key]] if key in targets else []
    # Path aliases such as "@/components/Button" or "~/lib/api": match by tail.
    tail = PurePosixPath(re.sub(r"^[@~#][^/]*/", "", spec))
    tail_key = module_key(str(tail))
    return [
        path for key, path in targets.items()
        if len(tail_key.parts) >= 2 and key.parts[-len(tail_key.parts):] == tail_key.parts
    ]


def resolve_py(module: str, targets: dict[PurePosixPath, str]) -> list[str]:
    dotted = PurePosixPath(*module.split("."))
    return [
        path for key, path in targets.items()
        if path.endswith(".py") and key.parts[-len(dotted.parts):] == dotted.parts
    ]


def find_consumers(modified: list[str]) -> dict[str, list[str]]:
    targets = {module_key(p): p for p in modified if Path(p).suffix in CODE_SUFFIXES}
    consumers: dict[str, set[str]] = {p: set() for p in targets.values()}
    if not targets:
        return {}
    for importer in git("ls-files").splitlines():
        if Path(importer).suffix not in CODE_SUFFIXES or "node_modules/" in importer:
            continue
        if NOT_A_FEATURE.search(importer):
            continue
        try:
            text = Path(importer).read_text(errors="ignore")
        except OSError:
            continue
        hits: list[str] = []
        if importer.endswith(".py"):
            for match in PY_IMPORT.finditer(text):
                hits += resolve_py(match.group(1) or match.group(2), targets)
        else:
            for match in JS_SPECIFIER.finditer(text):
                hits += resolve_js(importer, match.group(1), targets)
        for hit in hits:
            if hit != importer:
                consumers[hit].add(importer)
    return {path: sorted(users) for path, users in consumers.items()}


def shared_entry(path: str, users: list[str]) -> dict[str, Any]:
    own_dir = str(PurePosixPath(path).parent)
    by_folder: dict[str, list[str]] = {}
    for user in users:
        by_folder.setdefault(str(PurePosixPath(user).parent), []).append(user)
    return {
        "file": path,
        "consumer_count": len(users),
        "consumers": users[:MAX_CONSUMERS_LISTED],
        "consumer_folders": sorted(by_folder),
        "used_outside_own_folder": any(folder != own_dir for folder in by_folder),
    }


def package_runner(package_dir: Path) -> str:
    for lockfile, runner in (("yarn.lock", "yarn"), ("pnpm-lock.yaml", "pnpm"), ("bun.lockb", "bun")):
        for folder in (package_dir, Path(".")):
            if (folder / lockfile).exists():
                return runner
    return "npm run"


def run_command(runner: str, package_dir: str, script: str) -> str:
    if package_dir in ("", "."):
        return f"{runner} {script}"
    if runner == "yarn":
        return f"yarn --cwd {package_dir} {script}"
    if runner == "pnpm":
        return f"pnpm --dir {package_dir} {script}"
    if runner == "bun":
        return f"bun --cwd {package_dir} run {script}"
    return f"npm --prefix {package_dir} run {script}"


def find_e2e_suites() -> list[dict[str, Any]]:
    suites: list[dict[str, Any]] = []
    for manifest in git("ls-files", "package.json", "*/package.json", "*/*/package.json").splitlines():
        if "node_modules/" in manifest:
            continue
        try:
            scripts = json.loads(Path(manifest).read_text()).get("scripts", {})
        except (OSError, ValueError, AttributeError):
            continue
        package_dir = str(PurePosixPath(manifest).parent)
        runner = package_runner(Path(package_dir))
        for name, command in scripts.items():
            if not isinstance(command, str):
                continue
            if not (E2E_RUNNER.search(command) or E2E_NAME.search(name)):
                continue
            if E2E_EXCLUDE.search(name) or E2E_EXCLUDE.search(command):
                continue
            suites.append({
                "package": package_dir,
                "script": name,
                "script_body": command,
                "command": run_command(runner, package_dir, name),
                # The plain name ("e2e", "test:e2e") is the default full suite;
                # variants such as "e2e:staging" point at another environment.
                "primary": name in {"e2e", "test:e2e", "playwright", "cypress"},
            })
    suites.sort(key=lambda s: (not s["primary"], s["package"] != ".", s["script"]))
    return suites


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="base branch or ref to diff against")
    args = parser.parse_args()

    top = git("rev-parse", "--show-toplevel")
    if not top:
        print(json.dumps({"error": "not inside a git repository"}))
        return 1
    os.chdir(top)

    base, base_source = resolve_base(args.base)
    modified, created, deleted = changed_files(base) if base else ([], [], [])
    consumers = find_consumers(modified)
    shared = [shared_entry(p, u) for p, u in consumers.items() if u]
    shared.sort(key=lambda e: (not e["used_outside_own_folder"], -e["consumer_count"]))

    print(json.dumps({
        "base": base,
        "base_source": base_source,
        "head": git("rev-parse", "--abbrev-ref", "HEAD"),
        "shared_modified_files": shared,
        "modified_without_importers": sorted(p for p in modified if not consumers.get(p)),
        "created_files_skipped": created,
        "deleted_files": deleted,
        "e2e_suites": find_e2e_suites(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
