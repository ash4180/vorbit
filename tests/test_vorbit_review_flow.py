from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from vorbit_core.config import resolve_config
from vorbit_core.learn.heuristics import build_review_item
from vorbit_core.learn.models import CaptureContext, CaptureRecord
from vorbit_core.learn.rules import load_rules_for_agent
from vorbit_core.learn.storage import LearnStore
from vorbit_core.learn.text import utc_now


ROOT = Path(__file__).resolve().parent.parent
LEARN_SCRIPT = ROOT / "scripts" / "vorbit-learning.py"


def _store(project_root: Path) -> LearnStore:
    config = resolve_config(project_root)
    return LearnStore(config)


def _make_capture(*, source_agent: str, project_root: Path, capture_type: str, problem: str) -> CaptureRecord:
    config = resolve_config(project_root)
    assert config.project_slug is not None
    assert config.project_name is not None
    return CaptureRecord(
        id=f"{source_agent}-{capture_type}",
        source_agent=source_agent,
        runtime=f"{source_agent}-cli",
        project_root=str(project_root),
        project_slug=config.project_slug,
        project_name=config.project_name,
        session_id=f"{source_agent}-session",
        capture_type=capture_type,
        flow="test",
        message_indices=[0],
        keywords=[],
        user_messages=[problem],
        context=CaptureContext(before="", problem=problem, diagnosis="", resolution="", full_context=problem),
        transcript_path=str(project_root / f"{source_agent}.jsonl"),
        created_at=utc_now(),
    )


def test_agent_local_rule_stays_local(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))
    store = _store(temp_project)
    capture = _make_capture(source_agent="codex", project_root=temp_project, capture_type="correction", problem="Wrong, use const.")
    review = build_review_item(capture)
    store.write_capture(capture)
    store.write_review_item(review)

    subprocess.run(
        [
            sys.executable,
            str(LEARN_SCRIPT),
            "--project-root",
            str(temp_project),
            "approve",
            review.id,
            "--approved-by",
            "tester",
        ],
        check=True,
    )

    config = resolve_config(temp_project)
    codex_rules = load_rules_for_agent(store, agent="codex", project_slug=config.project_slug)
    claude_rules = load_rules_for_agent(store, agent="claude", project_slug=config.project_slug)
    gemini_rules = load_rules_for_agent(store, agent="gemini", project_slug=config.project_slug)

    assert any(rule.rule_text == review.proposed_rule for rule in codex_rules)
    assert all(rule.rule_text != review.proposed_rule for rule in claude_rules)
    assert all(rule.rule_text != review.proposed_rule for rule in gemini_rules)


def test_project_shared_rule_loads_for_all_agents(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))
    store = _store(temp_project)
    capture = _make_capture(
        source_agent="gemini",
        project_root=temp_project,
        capture_type="voluntary",
        problem="remember this: in this project we always use sqlite3",
    )
    review = build_review_item(capture)
    store.write_capture(capture)
    store.write_review_item(review)

    subprocess.run(
        [
            sys.executable,
            str(LEARN_SCRIPT),
            "--project-root",
            str(temp_project),
            "approve",
            review.id,
            "--approved-by",
            "tester",
        ],
        check=True,
    )

    config = resolve_config(temp_project)
    for agent in ("claude", "codex", "gemini"):
        rules = load_rules_for_agent(store, agent=agent, project_slug=config.project_slug)
        assert any(rule.rule_text == review.proposed_rule for rule in rules)


def test_rejected_review_does_not_publish_rule(temp_home, temp_project, monkeypatch):
    monkeypatch.setenv("VORBIT_HOME", str(temp_home / ".vorbit-store"))
    store = _store(temp_project)
    capture = _make_capture(source_agent="codex", project_root=temp_project, capture_type="correction", problem="Wrong, use pytest.")
    review = build_review_item(capture)
    store.write_capture(capture)
    store.write_review_item(review)

    subprocess.run(
        [
            sys.executable,
            str(LEARN_SCRIPT),
            "--project-root",
            str(temp_project),
            "reject",
            review.id,
            "--reason",
            "not useful",
        ],
        check=True,
    )

    assert not list((Path(os.environ["VORBIT_HOME"]) / "rules").rglob(f"{review.id}.md"))
