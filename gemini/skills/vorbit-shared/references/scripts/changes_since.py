#!/usr/bin/env python3
"""The new changes of a pull request since a commit that was checked before.

Read-only git. Run it inside the repository.

Usage: python3 changes_since.py <commit> [--head <ref>] [--base <ref>] [--diff]

The new changes are the commits after <commit> up to the head, without merge
commits and without the work a merge brings in. With --base, a commit counts
only when the base branch does not have it, so the list matches the pull
request's own commits. Without --base, only commits on the branch's own line
(each merge's first parent) count.

Prints one JSON object: status (ok, no_new_commits, not_ancestor,
unknown_commit) and a one-line scope sentence. For ok it also lists the
commits, each changed file with its added and removed line counts (summed over
the commits), and totals. --diff prints the patches of those commits instead,
oldest first, and exits 3 when the status is not ok.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any, Iterator

EXIT_ERROR, EXIT_NO_DIFF = 1, 3


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "--no-optional-locks", *args], capture_output=True, text=True, errors="replace",
    )


def commit_sha(ref: str) -> str | None:
    done = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return done.stdout.strip() if done.returncode == 0 else None


def plural(count: int, word: str) -> str:
    return f"{count} {word}" + ("" if count == 1 else "s")


def own_commits(since: str, head: str, base: str | None) -> list[str]:
    """Revision arguments that select this pull request's own commits after `since`."""
    return [f"{since}..{head}", f"^{base}"] if base else ["--first-parent", f"{since}..{head}"]


def numstat(shas: list[str]) -> Iterator[tuple[str, str, str, str | None]]:
    """(path, added, removed, renamed_from) for each file each commit changed."""
    for sha in shas:
        tokens = iter(git("diff-tree", "-r", "-M", "--numstat", "-z", "--no-commit-id", sha).stdout.split("\0"))
        for token in tokens:
            if not token:
                continue
            added, removed, path = token.split("\t", 2)
            renamed_from = None
            if not path:
                renamed_from, path = next(tokens), next(tokens)
            yield path, added, removed, renamed_from


def changed_files(shas: list[str]) -> list[dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for path, added, removed, renamed_from in numstat(shas):
        entry = files.setdefault(path, {"path": path, "added": 0, "removed": 0})
        if renamed_from:
            entry.setdefault("renamed_from", renamed_from)
        if added == "-":
            entry["binary"] = True
            continue
        entry["added"] += int(added)
        entry["removed"] += int(removed)
    return [files[path] for path in sorted(files)]


def new_changes(commit: str, head: str, base: str | None) -> dict[str, Any]:
    since = commit_sha(commit)
    facts: dict[str, Any] = {"since": since or commit, "head": head, "base": base}
    if not since:
        return {"status": "unknown_commit", "scope": f"Commit {commit} is not in this repository", **facts}
    label = since[:7]
    if git("merge-base", "--is-ancestor", since, head).returncode != 0:
        scope = f"{label} is not in the history of {head[:7]} (force-push or rebase)"
        return {"status": "not_ancestor", "scope": scope, **facts}

    selection = own_commits(since, head, base)
    log = git("log", "--no-merges", "--reverse", "--format=%H%x1f%s", *selection).stdout
    commits = [dict(zip(("sha", "subject"), line.split("\x1f", 1))) for line in log.splitlines()]
    merges = int(git("rev-list", "--count", "--merges", *selection).stdout.strip() or 0)
    skipped = f" ({plural(merges, 'merge commit')} skipped)" if merges else ""
    if not commits:
        scope = f"No new commits since {label}{skipped}"
        return {"status": "no_new_commits", "scope": scope, "merges_skipped": merges, **facts}

    files = changed_files([c["sha"] for c in commits])
    added = sum(f["added"] for f in files)
    removed = sum(f["removed"] for f in files)
    return {
        "status": "ok",
        "scope": f"Changes since {label}: {plural(len(files), 'file')}, +{added}/-{removed}{skipped}",
        **facts,
        "commits": commits,
        "merges_skipped": merges,
        "files": files,
        "totals": {"commits": len(commits), "files": len(files), "added": added, "removed": removed},
    }


def fail(message: str) -> int:
    print(json.dumps({"error": message}))
    return EXIT_ERROR


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("commit", help="the head that was checked before")
    parser.add_argument("--head", default="HEAD", help="the newest commit to include (default: HEAD)")
    parser.add_argument("--base", help="the base branch; commits it has never count")
    parser.add_argument("--diff", action="store_true", help="print the patches of the new commits instead of JSON")
    args = parser.parse_args()

    if git("rev-parse", "--git-dir").returncode != 0:
        return fail("not inside a git repository")
    head = commit_sha(args.head)
    if not head:
        return fail(f"--head {args.head} is not a commit in this repository")
    if args.base and not commit_sha(args.base):
        return fail(f"--base {args.base} is not a commit in this repository")

    result = new_changes(args.commit, head, args.base)
    if not args.diff:
        print(json.dumps(result, indent=2))
        return 0
    if result["status"] != "ok":
        print(result["scope"], file=sys.stderr)
        return EXIT_NO_DIFF
    patches = git(
        "log", "-p", "-M", "--no-merges", "--reverse", "--pretty=medium", "--no-color", "--no-ext-diff",
        *own_commits(result["since"], head, args.base),
    )
    sys.stdout.write(patches.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
