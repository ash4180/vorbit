"""Safe synchronization of Vorbit-managed agent links."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


SUPPORTED_AGENTS = ("codex", "gemini")
MANIFEST_NAME = ".vorbit-managed-links.json"
MANIFEST_SCHEMA_VERSION = 1
RESOURCE_NAME = "vorbit-resolve-rules"


class SyncError(RuntimeError):
    """Raised when sync cannot proceed without risking user-owned data."""


@dataclass(frozen=True)
class LinkAction:
    kind: str
    relative_path: str
    source: Path | None = None


@dataclass(frozen=True)
class SyncPlan:
    agent: str
    agent_home: Path
    expected_links: dict[str, Path]
    actions: tuple[LinkAction, ...]
    manifest_changed: bool
    conflicts: tuple[str, ...]

    @property
    def changed(self) -> bool:
        return bool(self.actions) or self.manifest_changed


def _normalized_absolute(path: Path) -> Path:
    # Resolve symlinks, not just `..`: ownership checks compare a link's on-disk
    # target against the repo source, and those can be spelled differently (macOS
    # /tmp vs /private/tmp, a symlinked checkout, the plugin cache). abspath would
    # leave the spellings divergent and misclassify a Vorbit-owned link as unowned.
    return Path(os.path.realpath(path.expanduser()))


def _safe_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or len(path.parts) != 2:
        raise SyncError(f"unsafe managed path in manifest: {value!r}")
    if path.parts[0] not in {"bin", "skills"}:
        raise SyncError(f"unsupported managed path in manifest: {value!r}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SyncError(f"unsafe managed path in manifest: {value!r}")
    return path.as_posix()


def _load_manifest(path: Path, agent: str) -> dict[str, Path]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SyncError(f"cannot read managed-link manifest {path}: {error}") from error

    if not isinstance(payload, dict):
        raise SyncError(f"invalid managed-link manifest {path}: expected an object")
    if payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise SyncError(f"unsupported managed-link manifest version in {path}")
    if payload.get("agent") != agent:
        raise SyncError(f"managed-link manifest agent does not match {agent}: {path}")
    raw_links = payload.get("links")
    if not isinstance(raw_links, dict):
        raise SyncError(f"invalid managed-link manifest {path}: links must be an object")

    links: dict[str, Path] = {}
    for raw_relative, raw_source in raw_links.items():
        if not isinstance(raw_relative, str) or not isinstance(raw_source, str):
            raise SyncError(f"invalid managed-link entry in {path}")
        relative = _safe_relative_path(raw_relative)
        links[relative] = _normalized_absolute(Path(raw_source))
    return links


def _manifest_payload(agent: str, links: dict[str, Path]) -> dict[str, object]:
    return {
        "agent": agent,
        "links": {relative: str(source) for relative, source in sorted(links.items())},
        "schema_version": MANIFEST_SCHEMA_VERSION,
    }


def _symlink_destination(path: Path) -> Path:
    destination = Path(os.readlink(path))
    if not destination.is_absolute():
        destination = path.parent / destination
    return _normalized_absolute(destination)


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _target_path(agent_home: Path, relative_path: str) -> Path:
    safe_relative = _safe_relative_path(relative_path)
    return agent_home.joinpath(*PurePosixPath(safe_relative).parts)


def _expected_links(repo_root: Path, agent: str) -> tuple[dict[str, Path], Path]:
    source_skills = repo_root / agent / "skills"
    if not source_skills.is_dir():
        raise SyncError(f"missing {agent} skills directory: {source_skills}")

    links: dict[str, Path] = {}
    for source in sorted(source_skills.iterdir(), key=lambda path: path.name):
        if source.name.startswith(".") or not source.exists():
            continue
        links[f"skills/{source.name}"] = _normalized_absolute(source)

    resolver = repo_root / "scripts" / RESOURCE_NAME
    if not resolver.is_file():
        raise SyncError(f"missing rule resolver resource: {resolver}")
    links[f"bin/{RESOURCE_NAME}"] = _normalized_absolute(resolver)
    return links, _normalized_absolute(source_skills)


def build_sync_plan(repo_root: Path, agent_home: Path, agent: str) -> SyncPlan:
    normalized_agent = agent.strip().lower()
    if normalized_agent not in SUPPORTED_AGENTS:
        supported = ", ".join(SUPPORTED_AGENTS)
        raise SyncError(f"unsupported agent {agent!r}; expected one of: {supported}")

    normalized_repo = _normalized_absolute(repo_root)
    normalized_home = _normalized_absolute(agent_home)
    if os.path.lexists(normalized_home) and not normalized_home.is_dir():
        raise SyncError(f"agent home is not a directory: {normalized_home}")
    expected, source_skills = _expected_links(normalized_repo, normalized_agent)
    manifest_path = normalized_home / MANIFEST_NAME
    managed = _load_manifest(manifest_path, normalized_agent)

    actions: list[LinkAction] = []
    conflicts: list[str] = []
    for directory_name in ("bin", "skills"):
        directory = normalized_home / directory_name
        if os.path.lexists(directory) and not directory.is_dir():
            conflicts.append(f"refusing to use non-directory install root: {directory}")

    for relative, source in sorted(expected.items()):
        target = _target_path(normalized_home, relative)
        if not os.path.lexists(target):
            actions.append(LinkAction("link", relative, source))
            continue
        if not target.is_symlink():
            conflicts.append(f"refusing to replace non-symlink path: {target}")
            continue
        destination = _symlink_destination(target)
        if destination == source:
            continue
        recorded_source = managed.get(relative)
        is_recorded_link = recorded_source is not None and destination == recorded_source
        if is_recorded_link or _is_within(destination, source_skills):
            actions.append(LinkAction("replace", relative, source))
            continue
        conflicts.append(f"refusing to replace unowned symlink: {target}")

    for relative in sorted(set(managed) - set(expected)):
        target = _target_path(normalized_home, relative)
        if not os.path.lexists(target):
            continue
        if target.is_symlink():
            if _symlink_destination(target) == managed[relative]:
                actions.append(LinkAction("unlink", relative))
            else:
                conflicts.append(f"refusing to prune retargeted managed symlink: {target}")
            continue
        conflicts.append(f"refusing to prune managed path that is not a symlink: {target}")

    skills_target = normalized_home / "skills"
    if skills_target.is_dir():
        for target in sorted(skills_target.iterdir(), key=lambda path: path.name):
            relative = f"skills/{target.name}"
            if relative in expected or relative in managed or not target.is_symlink():
                continue
            if _is_within(_symlink_destination(target), source_skills):
                actions.append(LinkAction("unlink", relative))

    current_payload = _manifest_payload(normalized_agent, managed)
    expected_payload = _manifest_payload(normalized_agent, expected)
    manifest_changed = current_payload != expected_payload or not manifest_path.exists()
    return SyncPlan(
        agent=normalized_agent,
        agent_home=normalized_home,
        expected_links=expected,
        actions=tuple(actions),
        manifest_changed=manifest_changed,
        conflicts=tuple(conflicts),
    )


def _write_manifest(plan: SyncPlan) -> None:
    plan.agent_home.mkdir(parents=True, exist_ok=True)
    manifest_path = plan.agent_home / MANIFEST_NAME
    payload = _manifest_payload(plan.agent, plan.expected_links)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            dir=plan.agent_home,
            prefix=f".{MANIFEST_NAME}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, manifest_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def apply_sync_plan(plan: SyncPlan) -> None:
    if plan.conflicts:
        raise SyncError("sync plan contains conflicts")
    for action in plan.actions:
        target = _target_path(plan.agent_home, action.relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if action.kind in {"replace", "unlink"}:
            if not target.is_symlink():
                raise SyncError(f"managed link changed during sync: {target}")
            target.unlink()
        if action.kind in {"link", "replace"}:
            if action.source is None:
                raise SyncError(f"missing source for link action: {target}")
            target.symlink_to(action.source, target_is_directory=action.source.is_dir())
    if plan.manifest_changed:
        _write_manifest(plan)


def _print_actions(plan: SyncPlan, prefix: str) -> None:
    for action in plan.actions:
        target = _target_path(plan.agent_home, action.relative_path)
        if action.kind == "unlink":
            print(f"{prefix} remove stale link {target}")
        else:
            print(f"{prefix} link {target} -> {action.source}")
    if plan.manifest_changed:
        print(f"{prefix} update {plan.agent_home / MANIFEST_NAME}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Safely sync Vorbit skills and resources.")
    parser.add_argument("--agent", choices=SUPPORTED_AGENTS, required=True)
    parser.add_argument("--agent-home", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Exit 1 when sync is required.")
    mode.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    arguments = parser.parse_args(argv)

    try:
        plan = build_sync_plan(arguments.repo_root, arguments.agent_home, arguments.agent)
    except (OSError, SyncError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if plan.conflicts:
        for conflict in plan.conflicts:
            print(f"error: {conflict}", file=sys.stderr)
        return 2

    if arguments.check:
        if plan.changed:
            _print_actions(plan, "would")
            print(f"sync required for {plan.agent}")
            return 1
        print(f"{plan.agent} skills and resources are up to date")
        return 0

    if arguments.dry_run:
        _print_actions(plan, "would")
        if plan.changed:
            print(f"dry run complete; sync required for {plan.agent}")
        else:
            print(f"dry run complete; {plan.agent} is up to date")
        return 0

    try:
        apply_sync_plan(plan)
    except (OSError, SyncError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    _print_actions(plan, "did")
    print(f"{plan.agent} skills and resources synced into {plan.agent_home}")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through shell entry points
    raise SystemExit(main())
