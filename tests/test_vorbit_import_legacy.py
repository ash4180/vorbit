from __future__ import annotations

from pathlib import Path

from vorbit_core.config import resolve_config
from vorbit_core.learn.importers import import_legacy_state
from vorbit_core.learn.storage import LearnStore


def test_import_legacy_state_migrates_pending_and_rules(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))

    legacy_vault = temp_home / "Projects" / "Thinking-Labs" / "claude"
    project_dir = legacy_vault / "projects" / temp_project.name
    project_dir.mkdir(parents=True, exist_ok=True)
    note = project_dir / "2026-04-06-sqlite.md"
    note.write_text(
        "---\n"
        f"project: {temp_project.name}\n"
        f"project_path: {temp_project}\n"
        "capture_type: correction\n"
        "status: pending\n"
        "---\n\n"
        "# Wrong db\n\n"
        "## Conversation Context\n"
        "Wrong, we use SQLite.\n\n"
        "## Root Cause Analysis\n"
        "Project policy.\n\n"
        "## Suggested Rule\n"
        "Use SQLite.\n\n"
        "## Destination\n"
        "rules/projects/example/shared.md\n\n"
        "## Raw Transcript\n"
        "USER: Wrong, we use SQLite.\n"
    )
    (legacy_vault / "pending-capture.md").write_text(f"Read the note at {note}\n")

    global_rules = temp_home / ".claude" / "rules"
    global_rules.mkdir(parents=True, exist_ok=True)
    (global_rules / "user-preferences.md").write_text("Always run tests before commit.\n")

    project_rules = temp_project / ".claude" / "rules"
    project_rules.mkdir(parents=True, exist_ok=True)
    (project_rules / "database.md").write_text("Use SQLite for local development.\n")

    counts = import_legacy_state(project_root=temp_project, home=temp_home)

    assert counts == {"captures": 1, "pending": 1, "rules": 2}

    store = LearnStore(resolve_config(temp_project))
    assert len(store.list_pending()) == 1
    imported_rules = list((store.root / "rules").rglob("*.md"))
    assert len(imported_rules) >= 2
