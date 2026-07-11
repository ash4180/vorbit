"""Deterministic durable-rule resolution for Vorbit agents."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from vorbit_core.config import resolve_config


SUPPORTED_AGENTS = ("codex", "gemini")


@dataclass(frozen=True)
class RuleTier:
    """One ordered rule directory and whether config includes it."""

    order: int
    name: str
    authority: str
    specificity: str
    directory: Path
    included: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "authority": self.authority,
            "directory": str(self.directory),
            "included": self.included,
            "name": self.name,
            "order": self.order,
            "specificity": self.specificity,
        }


@dataclass(frozen=True)
class ResolvedRule:
    """One rule file in its final loading order."""

    order: int
    tier: str
    tier_order: int
    authority: str
    specificity: str
    path: Path

    def as_dict(self) -> dict[str, object]:
        return {
            "authority": self.authority,
            "order": self.order,
            "path": str(self.path),
            "tier": self.tier,
            "tier_order": self.tier_order,
            "specificity": self.specificity,
        }


@dataclass(frozen=True)
class RuleResolution:
    """Resolved config and ordered rules for one project and agent."""

    agent: str
    storage_root: Path
    project_root: Path
    project_slug: str
    tiers: tuple[RuleTier, ...]
    rules: tuple[ResolvedRule, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "agent": self.agent,
            "project_root": str(self.project_root),
            "project_slug": self.project_slug,
            "precedence": {
                "authority_high_to_low": ["shared-policy", "agent-guidance"],
                "compare_in_order": ["authority", "specificity"],
                "read_order_is_precedence": False,
                "same_tier_conflict_policy": "surface",
                "specificity_high_to_low": ["project", "universal"],
            },
            "rules": [rule.as_dict() for rule in self.rules],
            "schema_version": 1,
            "storage_root": str(self.storage_root),
            "tiers": [tier.as_dict() for tier in self.tiers],
        }


def find_project_root(start: str | Path | None = None) -> Path:
    """Return the enclosing Git root, falling back to the starting directory."""
    directory = Path(start or Path.cwd()).expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return directory
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).expanduser().resolve()
    return directory


def resolve_rules(project_root: str | Path, *, agent: str) -> RuleResolution:
    """Resolve all applicable Markdown rule files in documented tier order."""
    normalized_agent = agent.strip().lower()
    if normalized_agent not in SUPPORTED_AGENTS:
        supported = ", ".join(SUPPORTED_AGENTS)
        raise ValueError(f"unsupported agent {agent!r}; expected one of: {supported}")

    config = resolve_config(project_root)
    if config.project_root is None or config.project_slug is None:
        raise ValueError("project_root is required to resolve project rules")

    rules_root = config.storage_root / "rules"
    include_universal = config.rule_loading.include_universal
    include_project = config.rule_loading.include_project
    include_agent = config.rule_loading.include_agent_local
    tiers = (
        RuleTier(
            1,
            "universal",
            "shared-policy",
            "universal",
            rules_root / "universal",
            include_universal,
        ),
        RuleTier(
            2,
            "project",
            "shared-policy",
            "project",
            rules_root / "projects" / config.project_slug,
            include_project,
        ),
        RuleTier(
            3,
            "agent-universal",
            "agent-guidance",
            "universal",
            rules_root / "agents" / normalized_agent / "universal",
            include_agent and include_universal,
        ),
        RuleTier(
            4,
            "agent-project",
            "agent-guidance",
            "project",
            rules_root
            / "agents"
            / normalized_agent
            / "projects"
            / config.project_slug,
            include_agent and include_project,
        ),
    )

    resolved_rules: list[ResolvedRule] = []
    for tier in tiers:
        if not tier.included or not tier.directory.is_dir():
            continue
        paths = sorted(
            (
                path
                for path in tier.directory.iterdir()
                if path.is_file()
                and not path.name.startswith(".")
                and path.suffix == ".md"
            ),
            key=lambda path: path.name,
        )
        for path in paths:
            resolved_rules.append(
                ResolvedRule(
                    order=len(resolved_rules) + 1,
                    tier=tier.name,
                    tier_order=tier.order,
                    authority=tier.authority,
                    specificity=tier.specificity,
                    path=path,
                )
            )

    return RuleResolution(
        agent=normalized_agent,
        storage_root=config.storage_root,
        project_root=config.project_root,
        project_slug=config.project_slug,
        tiers=tiers,
        rules=tuple(resolved_rules),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve Vorbit durable rules in deterministic loading order."
    )
    parser.add_argument("--agent", choices=SUPPORTED_AGENTS, required=True)
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root. Defaults to the enclosing Git root, then the current directory.",
    )
    arguments = parser.parse_args(argv)

    project_root = (
        arguments.project_root.expanduser().resolve()
        if arguments.project_root is not None
        else find_project_root()
    )
    try:
        resolution = resolve_rules(project_root, agent=arguments.agent)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(resolution.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the installed command
    raise SystemExit(main())
