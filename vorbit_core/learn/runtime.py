"""Runtime adapter helpers for transcript-driven capture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vorbit_core.config import resolve_config
from vorbit_core.learn.heuristics import build_review_item
from vorbit_core.learn.legacy import setup_claude_rules_symlink, sync_obsidian_export
from vorbit_core.learn.models import CaptureContext, CaptureRecord, ReviewItem
from vorbit_core.learn.storage import LearnStore
from vorbit_core.learn.text import build_context, load_transcript, msg_role, msg_text, read_comment, slugify, utc_now


@dataclass
class AdapterResult:
    captures: list[CaptureRecord]
    reviews: list[ReviewItem]


def scan_keywords(
    messages: list[dict[str, Any]],
    pattern: str,
) -> list[int]:
    import re

    matching: list[int] = []
    for idx, msg in enumerate(messages):
        if msg_role(msg) != "user":
            continue
        text = msg_text(msg)
        if not text or len(text) > 500:
            continue
        if "<teammate-message" in text:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            matching.append(idx)
    return matching


def load_seen_indices(path: Path, session_id: str, flow: str) -> set[int]:
    seen: set[int] = set()
    if not path.exists():
        return seen
    for line in path.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or parts[0] != session_id or parts[1] != flow:
            continue
        try:
            seen.add(int(parts[2]))
        except ValueError:
            continue
    return seen


def append_seen_indices(path: Path, session_id: str, flow: str, indices: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as handle:
        for idx in indices:
            handle.write(f"{session_id}\t{flow}\t{idx}\n")


def _build_capture_record(
    *,
    source_agent: str,
    runtime: str,
    project_root: Path,
    project_slug: str,
    project_name: str,
    session_id: str,
    capture_type: str,
    flow: str,
    indices: list[int],
    keywords: list[str],
    transcript_path: Path,
    messages: list[dict[str, Any]],
) -> CaptureRecord:
    context_dict = build_context(messages, indices)
    capture_id = slugify(f"{source_agent}-{session_id}-{flow}-{indices[0] if indices else 0}") or session_id
    return CaptureRecord(
        id=capture_id,
        source_agent=source_agent,
        runtime=runtime,
        project_root=str(project_root),
        project_slug=project_slug,
        project_name=project_name,
        session_id=session_id,
        capture_type=capture_type,
        flow=flow,
        message_indices=indices,
        keywords=keywords,
        user_messages=[msg_text(messages[idx]) for idx in indices],
        context=CaptureContext.from_dict(context_dict),
        transcript_path=str(transcript_path),
        created_at=utc_now(),
    )


def _compile_pattern(csv_text: str) -> tuple[str, list[str]]:
    import re

    keywords = [item.strip() for item in csv_text.split(",") if item.strip()]
    if not keywords:
        return "", []
    pattern = r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"
    return pattern, keywords


def capture_from_transcript(
    *,
    source_agent: str,
    runtime: str,
    project_root: str | Path,
    transcript_path: str | Path,
    rules_source: str | Path,
    seen_state_name: str,
    transcript_format: str = "claude",
    compatibility_seen_path: str | Path | None = None,
    legacy_claude_bridge: bool = False,
    obsidian_export: bool = True,
) -> AdapterResult:
    project_path = Path(project_root).expanduser().resolve()
    config = resolve_config(
        project_path,
        legacy_claude_bridge=legacy_claude_bridge,
        force_obsidian=obsidian_export,
    )
    store = LearnStore(config)

    if legacy_claude_bridge:
        setup_claude_rules_symlink(Path(rules_source))

    messages = load_transcript(Path(transcript_path), fmt=transcript_format)
    if not messages or not config.learn.enabled or config.project_slug is None or config.project_name is None:
        return AdapterResult(captures=[], reviews=[])

    try:
        rules_text = Path(rules_source).read_text()
    except OSError:
        return AdapterResult(captures=[], reviews=[])

    session_id = Path(transcript_path).stem
    state_path = store.state_dir / seen_state_name
    compatibility_seen = Path(compatibility_seen_path) if compatibility_seen_path else None

    captures: list[CaptureRecord] = []
    reviews: list[ReviewItem] = []

    for flow, capture_type, comment_name in (
        ("f1", "correction", "correction-keywords"),
        ("fv", "voluntary", "voluntary-keywords"),
    ):
        pattern, keywords = _compile_pattern(read_comment(rules_text, comment_name))
        if not pattern:
            continue
        matches = scan_keywords(messages, pattern)
        seen = load_seen_indices(state_path, session_id, flow)
        if compatibility_seen is not None:
            seen |= load_seen_indices(compatibility_seen, session_id, flow)
        new_indices = [idx for idx in matches if idx not in seen]
        if not new_indices:
            continue

        capture = _build_capture_record(
            source_agent=source_agent,
            runtime=runtime,
            project_root=project_path,
            project_slug=config.project_slug,
            project_name=config.project_name,
            session_id=session_id,
            capture_type=capture_type,
            flow=flow,
            indices=new_indices,
            keywords=keywords,
            transcript_path=Path(transcript_path),
            messages=messages,
        )
        review_item = build_review_item(capture)
        capture.metadata["review_id"] = review_item.id
        capture.metadata["proposed_scope"] = review_item.proposed_scope
        capture.metadata["proposed_destination"] = review_item.proposed_destination

        legacy_export = sync_obsidian_export(store, config, capture, review_item)
        if legacy_export is not None:
            capture.legacy_export_path = legacy_export

        store.write_capture(capture)
        store.write_review_item(review_item)
        append_seen_indices(state_path, session_id, flow, new_indices)
        if compatibility_seen is not None:
            append_seen_indices(compatibility_seen, session_id, flow, new_indices)
        captures.append(capture)
        reviews.append(review_item)

    return AdapterResult(captures=captures, reviews=reviews)
