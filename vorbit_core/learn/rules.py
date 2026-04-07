"""Rule loading, review, and projection helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from vorbit_core.config import VorbitConfig
from vorbit_core.learn.models import PublishedRule, ReviewItem
from vorbit_core.learn.storage import LearnStore
from vorbit_core.learn.text import utc_now


def render_rule_bundle(rules: Iterable[PublishedRule], *, title: str) -> str:
    lines = [f"# {title}", ""]
    for rule in rules:
        lines.append(f"## {rule.id}")
        lines.append(rule.rule_text.strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_rules_for_agent(
    store: LearnStore,
    *,
    agent: str,
    project_slug: str | None,
) -> list[PublishedRule]:
    rules: list[PublishedRule] = []
    candidates: list[Path] = []
    candidates.extend(sorted((store.rules_dir / "universal").glob("*.md")))
    if project_slug:
        candidates.extend(sorted((store.rules_dir / "projects" / project_slug).glob("*.md")))
        candidates.extend(sorted((store.rules_dir / "agents" / agent / "projects" / project_slug).glob("*.md")))
    candidates.extend(sorted((store.rules_dir / "agents" / agent / "universal").glob("*.md")))

    for path in candidates:
        try:
            content = path.read_text()
        except OSError:
            continue
        if not content.startswith("---"):
            continue
        _, frontmatter, body = content.split("---", 2)
        metadata: dict[str, str] = {}
        for line in frontmatter.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
        rule = PublishedRule(
            id=json.loads(metadata["id"]),
            scope=json.loads(metadata["scope"]),
            source_agent=json.loads(metadata["source_agent"]),
            source_runtime=json.loads(metadata["source_runtime"]),
            project_root=json.loads(metadata["project_root"]),
            project_slug=json.loads(metadata["project_slug"]),
            project_name=json.loads(metadata["project_name"]),
            destination=str(path.relative_to(store.root)),
            rule_text=body.strip(),
            capture_ids=json.loads(metadata["capture_ids"]),
            approved_by=json.loads(metadata["approved_by"]),
            approved_at=json.loads(metadata["approved_at"]),
        )
        rules.append(rule)
    return rules


def _claude_global_rules_dir() -> Path:
    return Path.home() / ".claude" / "rules"


def _claude_project_rules_dir(project_root: str) -> Path:
    return Path(project_root) / ".claude" / "rules"


def project_projection_path(store: LearnStore, *, agent: str, project_slug: str) -> Path:
    return store.exports_dir / agent / "projects" / project_slug / "rules.md"


def global_projection_path(store: LearnStore, *, agent: str) -> Path:
    return store.exports_dir / agent / "global" / "rules.md"


def write_agent_projections(store: LearnStore, config: VorbitConfig, *, agent: str) -> None:
    project_slug = config.project_slug
    rules = load_rules_for_agent(store, agent=agent, project_slug=project_slug)
    universal_only = [rule for rule in rules if rule.scope != "project-shared" or not project_slug or rule.project_slug != project_slug]
    global_path = global_projection_path(store, agent=agent)
    global_path.parent.mkdir(parents=True, exist_ok=True)
    global_path.write_text(render_rule_bundle(universal_only, title=f"Vorbit {agent} global rules"))

    if project_slug:
        project_path = project_projection_path(store, agent=agent, project_slug=project_slug)
        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_rules = [rule for rule in rules if rule.project_slug == project_slug or rule.scope != "project-shared"]
        project_path.write_text(render_rule_bundle(project_rules, title=f"Vorbit {agent} project rules"))


def write_claude_bridge(store: LearnStore, config: VorbitConfig) -> None:
    project_slug = config.project_slug
    rules = load_rules_for_agent(store, agent="claude", project_slug=project_slug)
    global_rules = [rule for rule in rules if rule.scope != "project-shared"]

    global_dir = _claude_global_rules_dir()
    global_dir.mkdir(parents=True, exist_ok=True)
    (global_dir / "vorbit-universal.md").write_text(
        render_rule_bundle(global_rules, title="Vorbit Claude universal rules")
    )

    if config.project_root is None or project_slug is None:
        return
    project_dir = _claude_project_rules_dir(str(config.project_root))
    project_dir.mkdir(parents=True, exist_ok=True)
    project_rules = [rule for rule in rules if rule.project_slug == project_slug]
    (project_dir / "vorbit-project-rules.md").write_text(
        render_rule_bundle(project_rules, title=f"Vorbit Claude rules for {config.project_name or project_slug}")
    )


def publish_review_item(
    store: LearnStore,
    review_item: ReviewItem,
    *,
    approved_by: str,
    scope: str | None = None,
    rule_text: str | None = None,
    destination: str | None = None,
) -> PublishedRule:
    scope_value = scope or review_item.proposed_scope
    text_value = (rule_text or review_item.proposed_rule).strip()
    destination_value = destination or review_item.proposed_destination
    published = PublishedRule(
        id=review_item.id,
        scope=scope_value,
        source_agent=review_item.source_agent,
        source_runtime=review_item.runtime,
        project_root=review_item.project_root,
        project_slug=review_item.project_slug,
        project_name=review_item.project_name,
        destination=destination_value,
        rule_text=text_value,
        capture_ids=[review_item.capture_id],
        approved_by=approved_by,
        approved_at=utc_now(),
    )
    store.write_published_rule(published)
    review_item.status = "approved"
    review_item.updated_at = utc_now()
    review_item.proposed_scope = scope_value
    review_item.proposed_rule = text_value
    review_item.proposed_destination = destination_value
    store.update_review_item(review_item)
    capture = store.load_capture(review_item.capture_id)
    capture.status = "approved"
    store.update_capture(capture)
    return published


def reject_review_item(store: LearnStore, review_item: ReviewItem, *, reason: str = "") -> ReviewItem:
    review_item.status = "rejected"
    review_item.updated_at = utc_now()
    if reason:
        review_item.metadata["rejection_reason"] = reason
    store.update_review_item(review_item)
    capture = store.load_capture(review_item.capture_id)
    capture.status = "rejected"
    store.update_capture(capture)
    return review_item
