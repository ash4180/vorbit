"""Heuristics for pending review proposals."""

from __future__ import annotations

import re
from pathlib import Path

from vorbit_core.learn.models import CaptureRecord, ReviewItem
from vorbit_core.learn.text import slugify, utc_now


UNIVERSAL_MARKERS = (
    "always",
    "never",
    "any project",
    "all projects",
    "globally",
    "every project",
)
PROJECT_MARKERS = (
    "this project",
    "in this project",
    "our repo",
    "this repo",
    "we use",
    "project uses",
)
AGENT_MARKERS = (
    "you ",
    "assistant",
    "codex",
    "claude",
    "gemini",
    "runtime",
    "hook",
)
LEADING_PREFIXES = (
    "wrong",
    "nope",
    "still not working",
    "not working",
    "broken",
    "remember this",
    "save this",
    "note this",
    "keep this",
    "learn this",
)


def _clean_user_text(raw: str) -> str:
    text = raw.strip()
    lowered = text.lower()
    for prefix in LEADING_PREFIXES:
        if lowered.startswith(prefix):
            text = text[len(prefix):].lstrip(" :,.-")
            lowered = text.lower()
    if not text:
        return "Review this learning."
    if not text.endswith("."):
        text = f"{text}."
    text = re.sub(r"\s+", " ", text)
    return text[:240]


def propose_scope(capture: CaptureRecord) -> str:
    corpus = " ".join(capture.user_messages).lower()
    if any(marker in corpus for marker in UNIVERSAL_MARKERS) and not any(
        marker in corpus for marker in PROJECT_MARKERS
    ):
        return "universal-shared"
    if any(marker in corpus for marker in PROJECT_MARKERS) or capture.capture_type == "voluntary":
        return "project-shared"
    if any(marker in corpus for marker in AGENT_MARKERS):
        return "agent-local"
    return "agent-local"


def proposed_destination(
    scope: str,
    *,
    source_agent: str,
    project_slug: str,
    review_id: str,
) -> str:
    filename = f"{review_id}.md"
    if scope == "universal-shared":
        return str(Path("rules") / "universal" / filename)
    if scope == "project-shared":
        return str(Path("rules") / "projects" / project_slug / filename)
    return str(Path("rules") / "agents" / source_agent / "projects" / project_slug / filename)


def build_review_item(capture: CaptureRecord) -> ReviewItem:
    created_at = utc_now()
    scope = propose_scope(capture)
    summary_source = capture.user_messages[0] if capture.user_messages else capture.context.problem
    summary = summary_source.strip().replace("\n", " ")
    summary = summary[:120] if summary else capture.capture_type
    review_id = slugify(f"{capture.source_agent}-{capture.capture_type}-{capture.id}") or capture.id
    review_id = review_id[:80]
    return ReviewItem(
        id=review_id,
        capture_id=capture.id,
        source_agent=capture.source_agent,
        runtime=capture.runtime,
        project_root=capture.project_root,
        project_slug=capture.project_slug,
        project_name=capture.project_name,
        capture_type=capture.capture_type,
        proposed_scope=scope,
        proposed_rule=_clean_user_text(summary_source),
        proposed_destination=proposed_destination(
            scope,
            source_agent=capture.source_agent,
            project_slug=capture.project_slug,
            review_id=review_id,
        ),
        source_summary=summary,
        status="pending",
        created_at=created_at,
        updated_at=created_at,
    )

