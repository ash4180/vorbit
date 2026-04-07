"""Import helpers for legacy Claude + Obsidian layouts."""

from __future__ import annotations

import re
from pathlib import Path

from vorbit_core.config import project_slug_for, resolve_config
from vorbit_core.learn.heuristics import build_review_item, proposed_destination
from vorbit_core.learn.models import CaptureContext, CaptureRecord, PublishedRule, ReviewItem
from vorbit_core.learn.storage import LearnStore
from vorbit_core.learn.text import slugify, utc_now


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        return {}, text
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body.strip()


def _capture_from_legacy_note(note_path: Path, *, source_agent: str = "claude") -> tuple[CaptureRecord, ReviewItem]:
    text = note_path.read_text()
    metadata, body = _parse_frontmatter(text)
    project_root = Path(metadata.get("project_path", note_path.parent.name)).expanduser()
    project_name = metadata.get("project", project_root.name or "project")
    project_slug = project_slug_for(project_root if project_root.is_absolute() else Path.cwd(), override=None)
    capture_type = metadata.get("capture_type", "correction")
    capture_id = slugify(f"legacy-{note_path.stem}") or note_path.stem

    def section(name: str) -> str:
        pattern = rf"## {re.escape(name)}\n(.*?)(?:\n## |\Z)"
        match = re.search(pattern, text, re.S)
        return match.group(1).strip() if match else ""

    context = CaptureContext(
        before=section("Conversation Context"),
        problem=section("Conversation Context"),
        diagnosis=section("Root Cause Analysis"),
        resolution=section("Suggested Rule"),
        full_context=section("Raw Transcript"),
    )
    created_at = metadata.get("date", utc_now().split("T", 1)[0]) + "T00:00:00Z"
    capture = CaptureRecord(
        id=capture_id,
        source_agent=source_agent,
        runtime="claude-code",
        project_root=str(project_root),
        project_slug=project_slug,
        project_name=project_name,
        session_id=note_path.stem,
        capture_type=capture_type,
        flow="legacy",
        message_indices=[],
        keywords=[],
        user_messages=[section("Conversation Context") or note_path.stem],
        context=context,
        transcript_path=str(note_path),
        created_at=created_at,
        status=metadata.get("status", "captured"),
        legacy_export_path=str(note_path),
    )
    review = build_review_item(capture)
    review.status = "pending" if metadata.get("status", "pending") == "pending" else metadata.get("status", "pending")
    review.proposed_rule = metadata.get("rule", "") or review.proposed_rule
    review.proposed_destination = metadata.get("routed_to", "") or review.proposed_destination
    return capture, review


def _import_rule_file(
    store: LearnStore,
    rule_path: Path,
    *,
    scope: str,
    source_agent: str,
    project_root: Path | None = None,
) -> PublishedRule:
    rule_text = rule_path.read_text().strip()
    project_slug = project_slug_for(project_root) if project_root is not None else ""
    project_name = project_root.name if project_root is not None else ""
    rule_id = slugify(f"legacy-{rule_path.stem}-{scope}") or rule_path.stem
    destination = proposed_destination(
        scope,
        source_agent=source_agent,
        project_slug=project_slug or "global",
        review_id=rule_id,
    )
    published = PublishedRule(
        id=rule_id,
        scope=scope,
        source_agent=source_agent,
        project_root=str(project_root.resolve()) if project_root is not None else "",
        project_slug=project_slug,
        project_name=project_name,
        destination=destination,
        rule_text=rule_text,
        capture_ids=[],
        approved_by="legacy-import",
        approved_at=utc_now(),
        source_runtime="claude-code",
        metadata={"imported_from": str(rule_path)},
    )
    store.write_published_rule(published)
    return published


def import_legacy_state(
    *,
    project_root: str | Path | None = None,
    home: str | Path | None = None,
) -> dict[str, int]:
    """Import legacy pending notes and durable Claude rules into the canonical store."""
    home_path = Path(home).expanduser().resolve() if home is not None else Path.home().resolve()
    project_path = Path(project_root).expanduser().resolve() if project_root is not None else None
    config = resolve_config(project_path)
    store = LearnStore(config)

    counts = {"captures": 0, "pending": 0, "rules": 0}
    legacy_vault = home_path / "Projects" / "Thinking-Labs" / "claude"
    pending_source = legacy_vault / "pending-capture.md"

    pending_notes: list[Path] = []
    if pending_source.exists():
        for line in pending_source.read_text().splitlines():
            if "Read the note at " not in line:
                continue
            note_path = Path(line.split("Read the note at ", 1)[1].strip())
            if note_path.exists():
                pending_notes.append(note_path)

    for note_path in pending_notes:
        capture, review = _capture_from_legacy_note(note_path)
        if not store.capture_path(capture.id).exists():
            store.write_capture(capture)
            counts["captures"] += 1
        if not store.review_path(review.id).exists():
            store.write_review_item(review)
            counts["pending"] += 1

    global_rules_dir = home_path / ".claude" / "rules"
    for rule_path in sorted(global_rules_dir.glob("*.md")):
        if rule_path.name in {"pending-capture.md", "vorbit-learning.md"} or rule_path.name.startswith(".seen"):
            continue
        _import_rule_file(store, rule_path, scope="universal-shared", source_agent="claude")
        counts["rules"] += 1

    if project_path is not None:
        project_rules_dir = project_path / ".claude" / "rules"
        for rule_path in sorted(project_rules_dir.glob("*.md")):
            _import_rule_file(
                store,
                rule_path,
                scope="project-shared",
                source_agent="claude",
                project_root=project_path,
            )
            counts["rules"] += 1

    return counts
