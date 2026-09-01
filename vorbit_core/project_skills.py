"""Project canonical Claude Code skills into Codex/Gemini workflow files.

One source of truth: `skills/<name>/SKILL.md` is authored once; this module
generates `{codex,gemini}/skills/vorbit-shared/workflows/<name>.md` from it by
applying a deterministic, per-agent substitution table (tool idioms, storage
paths, slash-command syntax). It also mirrors skill-local asset directories
(`references/`, `examples/`) into the agent skill folders and ships the
agent-neutral execution contract.

`implement-loop` is intentionally NOT projected: its Claude implementation is
driven by a Stop hook that other runtimes don't have, so its agent workflows
stay hand-written.

Usage:
    python3 -m vorbit_core.project_skills --write   # regenerate all outputs
    python3 -m vorbit_core.project_skills --check   # exit 1 if outputs are stale
"""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS = REPO_ROOT / "skills"

# canonical skill dir -> workflow filename stem (agent skill dir differs for two)
PROJECTED_SKILLS: dict[str, str] = {
    "adhd": "adhd",
    "explore": "explore",
    "prd": "prd",
    "journey": "journey",
    "epic": "epic",
    "linear-sync": "linear-sync",
    "qa-plan": "qa-plan",
    "qa-report": "qa-report",
    "tutorial": "tutorial",
    "teach": "teach",
    "figma": "figma",
    "pencil": "pencil",
    "prototype": "prototype",
    "webflow": "webflow",
    "implement": "implement",
    "verify": "verify",
    "review": "review",
    "implement-cleanup-mocks": "cleanup-mocks",
    "prepare-pr": "prepare-pr",
    "ux": "ux",
    "ui-patterns": "ui-patterns",
    "react-best-practices": "react-best-practices",
}

AGENT_DIR_NAME: dict[str, str] = {
    "review": "vorbit-code-review",
    "implement-cleanup-mocks": "vorbit-cleanup-mocks",
}

ASSET_DIRS = ("references", "examples")

AGENTS: dict[str, dict[str, str]] = {
    "codex": {
        "label": "Codex",
        "slug": "codex",
        "repo_doc": "AGENTS.md",
    },
    "gemini": {
        "label": "Gemini CLI",
        "slug": "gemini",
        "repo_doc": "GEMINI.md",
    },
}

# Appended verbatim to specific projected workflows for one agent.
AGENT_NOTES: dict[tuple[str, str], str] = {
    ("codex", "linear-sync"): (
        "\n> Codex note: the current Linear creation operation is `create_issue` — "
        "after inspecting its schema, call `create_issue` with the composed summary "
        "title, description, team, and project. Never use `save_issue` as a guessed "
        "alias.\n"
    ),
}

# Tokens that must never survive projection. Checked per generated file.
FORBIDDEN_OUTPUT_TOKENS = (
    "mcp__",
    ".claude/",
    "/vorbit:",
    "AskUserQuestion",
    "ToolSearch",
    "TaskCreate",
    "TaskUpdate",
    "_shared/",
    "at most 15 nodes",
    "no back-loops",
    "call `save_issue`",
)


def _routing_repl(agent: dict[str, str]) -> Callable[[re.Match[str]], str]:
    def repl(match: re.Match[str]) -> str:
        verb = "Preflight" if match.group(0)[0].isupper() else "preflight"
        return (
            f"{verb} required connectors: confirm each needed connector is "
            f"configured in {agent['label']} and inspect its current "
            "operation/parameter schemas; never guess tool names"
        )

    return repl


def _rules(agent: dict[str, str]) -> list[tuple[re.Pattern[str], object]]:
    label = agent["label"]
    repo_doc = agent["repo_doc"]
    slug = agent["slug"]

    def lit(pattern: str, replacement: str) -> tuple[re.Pattern[str], object]:
        return (re.compile(re.escape(pattern)), replacement.replace("\\", "\\\\"))

    return [
        # -- markdown links wrapping slash commands, then slash commands ------
        (re.compile(r"\[`(/vorbit:[^`]+)`\]\([^)]*\)"), r"`\1`"),
        (re.compile(r"/vorbit:(?:design|implement):([a-z-]+)"), r"$vorbit-\1"),
        # /vorbit:ticket is the top-level Claude Code command for the
        # linear-sync skill; agent skill dirs keep the linear-sync stem.
        (re.compile(r"/vorbit:ticket\b"), "$vorbit-linear-sync"),
        # -- shared file pointers --------------------------------------------
        # Generated workflows live in vorbit-shared/workflows/, so the shared
        # contract is one level up in ../references/, not ../vorbit-shared/.
        lit(
            "../_shared/execution-contract.md",
            "../references/execution-contract.md",
        ),
        lit(
            "../_shared/mock-registry.md",
            "../references/mock-registry.md",
        ),
        lit(
            "../_shared/spec-files.md",
            "../references/spec-files.md",
        ),
        lit(
            "../_shared/glossary.md",
            "../references/glossary.md",
        ),
        lit(
            "../_shared/design-knowledge/",
            "../references/design-knowledge/",
        ),
        lit(
            'save using the "Save Content" section in `_shared/mcp-tool-routing.md` and pass',
            "save via the connected platform's current content-creation tools "
            "(inspect schemas first) and pass",
        ),
        lit("per `_shared/mcp-tool-routing.md`", "per your connector preflight"),
        (
            re.compile(
                r"[Rr]ead(?: and follow)? `_shared/mcp-tool-routing\.md`"
                r"(?: \(glob for `[^`]+`\))?"
            ),
            _routing_repl(agent),
        ),
        # -- Claude-only tools -> plain equivalents ---------------------------
        (re.compile(r"`?AskUserQuestion`?"), "plain-text chat questions"),
        lit("Run `ToolSearch` for", "Check your configured connectors for"),
        (re.compile(r"`?ToolSearch`?"), "connector discovery"),
        lit("Use TaskCreate/TaskUpdate", "Keep a markdown progress checklist"),
        (re.compile(r"`?TaskCreate(?:/TaskUpdate)?`?"), "the progress checklist"),
        (re.compile(r"`?TaskUpdate`?"), "the progress checklist"),
        lit("(Glob for it)", "(check with a shell listing)"),
        lit(
            "Glob for `**/skills/review/references/` to resolve the path.",
            "They ship inside this skill's installed directory (see the asset note above).",
        ),
        lit(
            "(glob for `**/skills/review/references/pr-pipeline.md`)",
            "(in this skill's `references/` directory)",
        ),
        # -- Claude Code session commands -------------------------------------
        lit(
            "Run `/mcp` to connect, then retry.",
            f"Configure the connector in {label}, then retry.",
        ),
        lit(
            "Run `/mcp` to reconnect, then retry.",
            f"Reconnect the connector in {label}, then retry.",
        ),
        lit(
            "run `/mcp` to reconnect and stop",
            f"reconnect the Linear connector in {label} and stop",
        ),
        lit("`/mcp`", "your connector settings"),
        # -- storage/rules paths ----------------------------------------------
        (
            re.compile(r"`?\.claude/rules/pencil\.md`?"),
            "`<rules-root>/projects/<project-slug>/pencil.md` "
            "(resolve the root via `vorbit-resolve-rules`)",
        ),
        (
            re.compile(r"`?\.claude/review-rules\.md`?"),
            "`<rules-root>/projects/<project-slug>/review-rules.md` "
            "(resolve the root via `vorbit-resolve-rules`)",
        ),
        lit(
            "`./CLAUDE.md` and `~/.claude/CLAUDE.md`",
            f"`./{repo_doc}` and other repository instruction files",
        ),
        lit(
            "`.claude/.loop-state.json` contains an active loop",
            f"the {slug} implement-loop state file (see the implement-loop workflow) "
            "shows an active loop",
        ),
        lit(
            "Never hardcode `.claude/`, `.codex/`, or `.gemini/` storage.",
            "Never hardcode agent-runtime storage paths.",
        ),
        lit(
            "Writes to `.claude/rules/` and Pencil canvas only.",
            "Writes to the resolved Vorbit rules root and Pencil canvas only.",
        ),
        # -- Linear verbs ------------------------------------------------------
        lit(
            "then `save_issue` to add or replace",
            "then the connector's issue-update operation to add or replace",
        ),
        lit(
            "(`save_issue` in the vorbit Claude plugin)",
            "(inspect the connector schema for the current issue-update verb)",
        ),
        # -- misc ---------------------------------------------------------------
        lit("relative to this skill", "from this skill's installed directory"),
        lit("discovered through routing", "resolved during connector preflight"),
    ]


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    parts = text.split("---", 2)
    return parts[2].lstrip("\n") if len(parts) == 3 else text


def _agent_dir(canonical_name: str) -> str:
    return AGENT_DIR_NAME.get(canonical_name, f"vorbit-{canonical_name}")


def _has_assets(canonical_name: str) -> bool:
    skill_dir = CANONICAL_SKILLS / canonical_name
    return any((skill_dir / asset).is_dir() for asset in ASSET_DIRS)


def project_workflow(canonical_name: str, agent_key: str) -> str:
    agent = AGENTS[agent_key]
    source = CANONICAL_SKILLS / canonical_name / "SKILL.md"
    body = _strip_frontmatter(source.read_text())

    for pattern, replacement in _rules(agent):
        body = pattern.sub(replacement, body)  # type: ignore[arg-type]

    note = AGENT_NOTES.get((agent_key, PROJECTED_SKILLS[canonical_name]), "")
    header = (
        f"<!-- GENERATED from skills/{canonical_name}/SKILL.md — edit the canonical "
        "file, then run: python3 -m vorbit_core.project_skills --write -->\n\n"
    )
    if _has_assets(canonical_name):
        header += (
            "> Skill assets: paths like `references/...` in this workflow resolve "
            f"inside the installed `{_agent_dir(canonical_name)}` skill directory "
            "(a sibling of `vorbit-shared`).\n\n"
        )

    output = header + body.rstrip() + "\n" + note

    for token in FORBIDDEN_OUTPUT_TOKENS:
        if token == "_shared/" and "vorbit-shared/" in output:
            cleaned = output.replace("vorbit-shared/", "")
            assert token not in cleaned, (canonical_name, agent_key, token)
            continue
        assert token not in output, (canonical_name, agent_key, token)
    return output


def _workflow_path(agent_key: str, canonical_name: str) -> Path:
    return (
        REPO_ROOT
        / agent_key
        / "skills"
        / "vorbit-shared"
        / "workflows"
        / f"{PROJECTED_SKILLS[canonical_name]}.md"
    )


MIRRORED_SHARED: tuple[str, ...] = (
    "execution-contract.md",
    "glossary.md",
    "mock-registry.md",
    "spec-files.md",
)

# Whole directories under skills/_shared/ mirrored into each agent's
# vorbit-shared/references/ (vendored design reference content).
MIRRORED_SHARED_DIRS: tuple[str, ...] = ("design-knowledge",)


def _shared_target(agent_key: str, filename: str) -> Path:
    return (
        REPO_ROOT
        / agent_key
        / "skills"
        / "vorbit-shared"
        / "references"
        / filename
    )


def _iter_asset_pairs(agent_key: str):
    for canonical_name in PROJECTED_SKILLS:
        for asset in ASSET_DIRS:
            source = CANONICAL_SKILLS / canonical_name / asset
            if source.is_dir():
                yield source, (
                    REPO_ROOT
                    / agent_key
                    / "skills"
                    / _agent_dir(canonical_name)
                    / asset
                )


def _dirs_equal(a: Path, b: Path) -> bool:
    if not b.is_dir():
        return False
    comparison = filecmp.dircmp(a, b)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        return False
    return all(
        _dirs_equal(a / sub, b / sub) for sub in comparison.common_dirs
    )


def write_all() -> None:
    for agent_key in AGENTS:
        for canonical_name in PROJECTED_SKILLS:
            path = _workflow_path(agent_key, canonical_name)
            path.write_text(project_workflow(canonical_name, agent_key))
        for filename in MIRRORED_SHARED:
            source = CANONICAL_SKILLS / "_shared" / filename
            _shared_target(agent_key, filename).write_text(source.read_text())
        for dirname in MIRRORED_SHARED_DIRS:
            source = CANONICAL_SKILLS / "_shared" / dirname
            target = _shared_target(agent_key, dirname)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        for source, target in _iter_asset_pairs(agent_key):
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)


def check_all() -> list[str]:
    stale: list[str] = []
    for agent_key in AGENTS:
        for canonical_name in PROJECTED_SKILLS:
            path = _workflow_path(agent_key, canonical_name)
            expected = project_workflow(canonical_name, agent_key)
            if not path.is_file() or path.read_text() != expected:
                stale.append(str(path.relative_to(REPO_ROOT)))
        for filename in MIRRORED_SHARED:
            source = CANONICAL_SKILLS / "_shared" / filename
            target = _shared_target(agent_key, filename)
            if not target.is_file() or target.read_text() != source.read_text():
                stale.append(str(target.relative_to(REPO_ROOT)))
        for dirname in MIRRORED_SHARED_DIRS:
            source = CANONICAL_SKILLS / "_shared" / dirname
            dir_target = _shared_target(agent_key, dirname)
            if not _dirs_equal(source, dir_target):
                stale.append(str(dir_target.relative_to(REPO_ROOT)))
        for source, asset_target in _iter_asset_pairs(agent_key):
            if not _dirs_equal(source, asset_target):
                stale.append(str(asset_target.relative_to(REPO_ROOT)))
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="regenerate all outputs")
    group.add_argument("--check", action="store_true", help="exit 1 if outputs are stale")
    args = parser.parse_args(argv)

    if args.write:
        write_all()
        print("projected workflows regenerated")
        return 0

    stale = check_all()
    if stale:
        print("stale projected outputs (run --write):")
        for path in stale:
            print(f"  {path}")
        return 1
    print("projected outputs are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
