"""Canonical records for Vorbit learning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CaptureContext:
    before: str
    problem: str
    diagnosis: str
    resolution: str
    full_context: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaptureContext":
        return cls(
            before=str(data.get("before", "")),
            problem=str(data.get("problem", "")),
            diagnosis=str(data.get("diagnosis", "")),
            resolution=str(data.get("resolution", "")),
            full_context=str(data.get("full_context", "")),
        )


@dataclass
class CaptureRecord:
    id: str
    source_agent: str
    runtime: str
    project_root: str
    project_slug: str
    project_name: str
    session_id: str
    capture_type: str
    flow: str
    message_indices: list[int]
    keywords: list[str]
    user_messages: list[str]
    context: CaptureContext
    transcript_path: str
    created_at: str
    status: str = "captured"
    legacy_export_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["context"] = self.context.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaptureRecord":
        return cls(
            id=str(data["id"]),
            source_agent=str(data["source_agent"]),
            runtime=str(data["runtime"]),
            project_root=str(data["project_root"]),
            project_slug=str(data["project_slug"]),
            project_name=str(data.get("project_name", data["project_slug"])),
            session_id=str(data["session_id"]),
            capture_type=str(data["capture_type"]),
            flow=str(data["flow"]),
            message_indices=[int(idx) for idx in data.get("message_indices", [])],
            keywords=[str(value) for value in data.get("keywords", [])],
            user_messages=[str(value) for value in data.get("user_messages", [])],
            context=CaptureContext.from_dict(data.get("context", {})),
            transcript_path=str(data.get("transcript_path", "")),
            created_at=str(data["created_at"]),
            status=str(data.get("status", "captured")),
            legacy_export_path=(
                str(data["legacy_export_path"])
                if data.get("legacy_export_path") is not None
                else None
            ),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ReviewItem:
    id: str
    capture_id: str
    source_agent: str
    runtime: str
    project_root: str
    project_slug: str
    project_name: str
    capture_type: str
    proposed_scope: str
    proposed_rule: str
    proposed_destination: str
    source_summary: str
    status: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewItem":
        return cls(
            id=str(data["id"]),
            capture_id=str(data["capture_id"]),
            source_agent=str(data["source_agent"]),
            runtime=str(data["runtime"]),
            project_root=str(data["project_root"]),
            project_slug=str(data["project_slug"]),
            project_name=str(data.get("project_name", data["project_slug"])),
            capture_type=str(data["capture_type"]),
            proposed_scope=str(data["proposed_scope"]),
            proposed_rule=str(data["proposed_rule"]),
            proposed_destination=str(data["proposed_destination"]),
            source_summary=str(data.get("source_summary", "")),
            status=str(data.get("status", "pending")),
            created_at=str(data["created_at"]),
            updated_at=str(data.get("updated_at", data["created_at"])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class PublishedRule:
    id: str
    scope: str
    source_agent: str
    project_root: str
    project_slug: str
    project_name: str
    destination: str
    rule_text: str
    capture_ids: list[str]
    approved_by: str
    approved_at: str
    source_runtime: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PublishedRule":
        return cls(
            id=str(data["id"]),
            scope=str(data["scope"]),
            source_agent=str(data["source_agent"]),
            project_root=str(data.get("project_root", "")),
            project_slug=str(data.get("project_slug", "")),
            project_name=str(data.get("project_name", data.get("project_slug", ""))),
            destination=str(data["destination"]),
            rule_text=str(data["rule_text"]),
            capture_ids=[str(value) for value in data.get("capture_ids", [])],
            approved_by=str(data["approved_by"]),
            approved_at=str(data["approved_at"]),
            source_runtime=str(data.get("source_runtime", "")),
            metadata=dict(data.get("metadata", {})),
        )
