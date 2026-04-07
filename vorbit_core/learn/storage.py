"""Canonical filesystem-backed learning store."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from vorbit_core.config import VorbitConfig
from vorbit_core.learn.models import CaptureRecord, PublishedRule, ReviewItem
from vorbit_core.learn.text import utc_now


def _json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


class LearnStore:
    """Canonical store plus compatibility helpers."""

    def __init__(self, config: VorbitConfig):
        self.config = config
        self.root = config.storage_root
        self.ensure_layout()

    @property
    def captures_dir(self) -> Path:
        return self.root / "captures"

    @property
    def pending_dir(self) -> Path:
        return self.root / "pending"

    @property
    def rules_dir(self) -> Path:
        return self.root / "rules"

    @property
    def state_dir(self) -> Path:
        return self.root / "state"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def index_path(self) -> Path:
        return self.root / "index.jsonl"

    def ensure_layout(self) -> None:
        for directory in (
            self.root,
            self.root / "captures",
            self.root / "pending",
            self.root / "rules" / "universal",
            self.root / "rules" / "projects",
            self.root / "rules" / "agents",
            self.root / "state",
            self.root / "exports",
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def append_index(self, event: str, payload: dict[str, Any]) -> None:
        row = {"event": event, "timestamp": utc_now(), "payload": payload}
        with open(self.index_path, "a") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    def capture_path(self, capture_id: str) -> Path:
        return self.captures_dir / f"{capture_id}.json"

    def review_path(self, review_id: str) -> Path:
        return self.pending_dir / f"{review_id}.json"

    def write_capture(self, capture: CaptureRecord) -> Path:
        path = self.capture_path(capture.id)
        _json_dump(path, capture.to_dict())
        self.append_index("capture-created", {"id": capture.id, "source_agent": capture.source_agent})
        return path

    def update_capture(self, capture: CaptureRecord) -> Path:
        path = self.capture_path(capture.id)
        _json_dump(path, capture.to_dict())
        self.append_index("capture-updated", {"id": capture.id, "status": capture.status})
        return path

    def load_capture(self, capture_id: str) -> CaptureRecord:
        return CaptureRecord.from_dict(_json_load(self.capture_path(capture_id)))

    def write_review_item(self, review_item: ReviewItem) -> Path:
        path = self.review_path(review_item.id)
        _json_dump(path, review_item.to_dict())
        self.append_index(
            "review-created",
            {"id": review_item.id, "capture_id": review_item.capture_id, "scope": review_item.proposed_scope},
        )
        return path

    def update_review_item(self, review_item: ReviewItem) -> Path:
        path = self.review_path(review_item.id)
        _json_dump(path, review_item.to_dict())
        self.append_index("review-updated", {"id": review_item.id, "status": review_item.status})
        return path

    def load_review_item(self, review_id: str) -> ReviewItem:
        return ReviewItem.from_dict(_json_load(self.review_path(review_id)))

    def list_pending(self) -> list[ReviewItem]:
        items: list[ReviewItem] = []
        for path in sorted(self.pending_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                item = ReviewItem.from_dict(_json_load(path))
            except Exception:
                continue
            if item.status == "pending":
                items.append(item)
        return items

    def all_review_items(self) -> list[ReviewItem]:
        items: list[ReviewItem] = []
        for path in sorted(self.pending_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                items.append(ReviewItem.from_dict(_json_load(path)))
            except Exception:
                continue
        return items

    def rule_path_for(self, rule: PublishedRule) -> Path:
        relative = Path(rule.destination)
        return self.root / relative

    def write_published_rule(self, rule: PublishedRule) -> Path:
        path = self.rule_path_for(rule)
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "id": rule.id,
            "scope": rule.scope,
            "source_agent": rule.source_agent,
            "source_runtime": rule.source_runtime,
            "project_slug": rule.project_slug,
            "project_name": rule.project_name,
            "project_root": rule.project_root,
            "capture_ids": rule.capture_ids,
            "approved_by": rule.approved_by,
            "approved_at": rule.approved_at,
        }
        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, list):
                frontmatter_lines.append(f"{key}: [{', '.join(json.dumps(item) for item in value)}]")
            else:
                frontmatter_lines.append(f"{key}: {json.dumps(value)}")
        frontmatter_lines.append("---")
        body = "\n".join(frontmatter_lines) + "\n\n" + rule.rule_text.strip() + "\n"
        path.write_text(body)
        self.append_index("rule-published", {"id": rule.id, "destination": rule.destination})
        return path

    def write_state_lines(self, state_name: str, lines: list[str]) -> Path:
        path = self.state_dir / state_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(lines))
        return path

    def append_state_line(self, state_name: str, line: str) -> Path:
        path = self.state_dir / state_name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as handle:
            handle.write(line)
        return path

    def read_state_lines(self, state_name: str) -> list[str]:
        path = self.state_dir / state_name
        if not path.exists():
            return []
        return [line.rstrip("\n") for line in path.read_text().splitlines()]
