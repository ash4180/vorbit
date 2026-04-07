#!/usr/bin/env python3
"""Manage Vorbit learning reviews, projections, and legacy imports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vorbit_core.config import resolve_config  # noqa: E402
from vorbit_core.learn.importers import import_legacy_state  # noqa: E402
from vorbit_core.learn.rules import (  # noqa: E402
    load_rules_for_agent,
    publish_review_item,
    reject_review_item,
    render_rule_bundle,
    write_agent_projections,
    write_claude_bridge,
)
from vorbit_core.learn.storage import LearnStore  # noqa: E402


def _store(project_root: str | None, *, legacy_claude_bridge: bool = False) -> LearnStore:
    config = resolve_config(project_root, legacy_claude_bridge=legacy_claude_bridge)
    return LearnStore(config)


def _refresh_all_projections(store: LearnStore, project_root: str | None) -> None:
    config = resolve_config(project_root, legacy_claude_bridge=True)
    for agent in ("claude", "codex", "gemini"):
        write_agent_projections(store, config, agent=agent)
    write_claude_bridge(store, config)


def _cmd_pending(args: argparse.Namespace) -> int:
    store = _store(args.project_root)
    items = store.all_review_items() if args.all else store.list_pending()
    if args.json:
        print(json.dumps([item.to_dict() for item in items], indent=2))
        return 0
    for item in items:
        print(f"{item.id}\t{item.status}\t{item.source_agent}\t{item.proposed_scope}\t{item.source_summary}")
    return 0


def _cmd_approve(args: argparse.Namespace) -> int:
    store = _store(args.project_root)
    item = store.load_review_item(args.review_id)
    publish_review_item(
        store,
        item,
        approved_by=args.approved_by,
        scope=args.scope,
        rule_text=args.rule_text,
        destination=args.destination,
    )
    _refresh_all_projections(store, item.project_root)
    print(item.id)
    return 0


def _cmd_reject(args: argparse.Namespace) -> int:
    store = _store(args.project_root)
    item = store.load_review_item(args.review_id)
    reject_review_item(store, item, reason=args.reason)
    print(item.id)
    return 0


def _cmd_rules(args: argparse.Namespace) -> int:
    config = resolve_config(args.project_root)
    store = LearnStore(config)
    rules = load_rules_for_agent(store, agent=args.agent, project_slug=config.project_slug)
    print(render_rule_bundle(rules, title=f"Vorbit {args.agent} rules").rstrip())
    return 0


def _cmd_import_legacy(args: argparse.Namespace) -> int:
    counts = import_legacy_state(project_root=args.project_root, home=args.home)
    print(json.dumps(counts, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=str(Path.cwd()), help="Project root for project-scoped rules")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pending = subparsers.add_parser("pending", help="List pending learnings")
    pending.add_argument("--all", action="store_true", help="Include approved/rejected review items")
    pending.add_argument("--json", action="store_true", help="Emit JSON")
    pending.set_defaults(func=_cmd_pending)

    approve = subparsers.add_parser("approve", help="Approve and publish a review item")
    approve.add_argument("review_id")
    approve.add_argument("--approved-by", required=True)
    approve.add_argument("--scope", choices=["agent-local", "project-shared", "universal-shared"])
    approve.add_argument("--rule-text")
    approve.add_argument("--destination")
    approve.set_defaults(func=_cmd_approve)

    reject = subparsers.add_parser("reject", help="Reject a review item")
    reject.add_argument("review_id")
    reject.add_argument("--reason", default="")
    reject.set_defaults(func=_cmd_reject)

    rules = subparsers.add_parser("rules", help="Render applicable rules for an agent")
    rules.add_argument("--agent", required=True, choices=["claude", "codex", "gemini"])
    rules.set_defaults(func=_cmd_rules)

    importer = subparsers.add_parser("import-legacy", help="Import the legacy Claude/Obsidian state")
    importer.add_argument("--home", help="Override HOME for legacy import")
    importer.set_defaults(func=_cmd_import_legacy)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
