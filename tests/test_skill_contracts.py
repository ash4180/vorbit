from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS = REPO_ROOT / "skills"
CODEX_SKILLS = REPO_ROOT / "codex" / "skills"
GEMINI_SKILLS = REPO_ROOT / "gemini" / "skills"

CANONICAL_NAME_BY_AGENT_NAME = {
    "cleanup-mocks": "implement-cleanup-mocks",
    "code-review": "review",
}
EXPLICIT_ONLY = {
    "vorbit-cleanup-mocks",
    "vorbit-implement-loop",
    "vorbit-prepare-pr",
    "vorbit-ux",
}
AGENT_OVERLAY_WORKFLOWS = {
    "figma.md",
    "implement-loop.md",
    "implement.md",
    "pencil.md",
    "prd.md",
}
PORTABLE_FRONTMATTER_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
TERMINAL_STATUSES = {
    "blocked",
    "blocked_missing_capability",
    "blocked_missing_runtime",
    "blocked_rule_conflict",
    "canceled",
    "completed",
    "failed",
    "needs_backend",
    "needs_input",
}


def _skill_directories(root: Path) -> list[Path]:
    return sorted(
        path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    assert text.startswith("---\n"), f"missing frontmatter: {path}"
    try:
        raw = text.split("---", 2)[1]
    except IndexError as error:  # pragma: no cover - assertion message is the useful output
        raise AssertionError(f"unterminated frontmatter: {path}") from error

    values: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def test_agent_skill_sets_and_descriptions_stay_in_sync():
    codex = _skill_directories(CODEX_SKILLS)
    gemini = _skill_directories(GEMINI_SKILLS)

    assert [path.name for path in codex] == [path.name for path in gemini]
    assert len(codex) == 17

    for codex_dir, gemini_dir in zip(codex, gemini):
        codex_meta = _frontmatter(codex_dir / "SKILL.md")
        gemini_meta = _frontmatter(gemini_dir / "SKILL.md")
        assert codex_meta == gemini_meta
        assert codex_meta["name"] == codex_dir.name

        short_name = codex_dir.name.removeprefix("vorbit-")
        canonical_name = CANONICAL_NAME_BY_AGENT_NAME.get(short_name, short_name)
        canonical_meta = _frontmatter(CANONICAL_SKILLS / canonical_name / "SKILL.md")
        assert canonical_meta["description"] == codex_meta["description"]


@pytest.mark.parametrize("root", [CANONICAL_SKILLS, CODEX_SKILLS, GEMINI_SKILLS])
def test_skill_frontmatter_uses_portable_schema(root: Path):
    for skill_dir in _skill_directories(root):
        frontmatter = (skill_dir / "SKILL.md").read_text().split("---", 2)[1]
        top_level_keys = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line and not line[0].isspace() and ":" in line
        }
        assert top_level_keys <= PORTABLE_FRONTMATTER_KEYS, skill_dir


def test_codex_skills_have_safe_ui_metadata():
    for skill_dir in _skill_directories(CODEX_SKILLS):
        metadata_path = skill_dir / "agents" / "openai.yaml"
        content = metadata_path.read_text()
        default_prompt = re.search(r'^  default_prompt: "([^"]+)"$', content, re.MULTILINE)
        short_description = re.search(
            r'^  short_description: "([^"]+)"$', content, re.MULTILINE
        )
        implicit = re.search(
            r"^  allow_implicit_invocation: (true|false)$", content, re.MULTILINE
        )

        assert default_prompt, metadata_path
        assert f"${skill_dir.name}" in default_prompt.group(1)
        assert short_description, metadata_path
        assert 25 <= len(short_description.group(1)) <= 64
        assert implicit, metadata_path
        assert (implicit.group(1) == "false") == (skill_dir.name in EXPLICIT_ONLY)


@pytest.mark.parametrize("root", [CODEX_SKILLS, GEMINI_SKILLS])
def test_every_wrapper_reference_resolves(root: Path):
    for skill_dir in _skill_directories(root):
        wrapper = skill_dir / "SKILL.md"
        references = re.findall(r"`(\.\./vorbit-shared/[^`]+\.md)`", wrapper.read_text())
        assert len(references) == 2, wrapper
        for reference in references:
            assert (skill_dir / reference).resolve().is_file(), (wrapper, reference)


@pytest.mark.parametrize("root", [CODEX_SKILLS, GEMINI_SKILLS])
def test_projected_workflow_references_resolve(root: Path):
    workflows = root / "vorbit-shared" / "workflows"
    for workflow in workflows.glob("*.md"):
        references = re.findall(r"`(\.\./references/[^`\s]+\.md)`", workflow.read_text())
        for reference in references:
            assert (workflow.parent / reference).resolve().is_file(), (workflow, reference)


def test_agent_neutral_workflows_do_not_drift():
    codex_workflows = CODEX_SKILLS / "vorbit-shared" / "workflows"
    gemini_workflows = GEMINI_SKILLS / "vorbit-shared" / "workflows"
    assert {path.name for path in codex_workflows.glob("*.md")} == {
        path.name for path in gemini_workflows.glob("*.md")
    }

    for codex_path in codex_workflows.glob("*.md"):
        if codex_path.name in AGENT_OVERLAY_WORKFLOWS:
            continue
        assert codex_path.read_text() == (gemini_workflows / codex_path.name).read_text()


def test_agent_neutral_references_do_not_drift():
    codex_references = CODEX_SKILLS / "vorbit-shared" / "references"
    gemini_references = GEMINI_SKILLS / "vorbit-shared" / "references"
    assert {path.name for path in codex_references.glob("*.md")} == {
        path.name for path in gemini_references.glob("*.md")
    }
    for codex_path in codex_references.glob("*.md"):
        if codex_path.name == "load-rules.md":
            continue
        assert codex_path.read_text() == (gemini_references / codex_path.name).read_text()


@pytest.mark.parametrize("root", [CODEX_SKILLS, GEMINI_SKILLS])
def test_projected_workflows_have_no_legacy_agent_or_handoff_syntax(root: Path):
    shared_text = "\n".join(
        path.read_text() for path in sorted((root / "vorbit-shared").rglob("*.md"))
    )
    forbidden = {
        ".claude/": "Claude-specific runtime path",
        "/vorbit:": "Claude-only slash command handoff",
        "at most 15 nodes": "stale journey limit",
        "no back-loops": "requirement-dropping journey rule",
    }
    for pattern, reason in forbidden.items():
        assert pattern not in shared_text, reason

    if root == CODEX_SKILLS:
        assert "call `save_issue`" not in shared_text, "stale Codex Linear create alias"
        assert "call `create_issue`" in shared_text, "current Codex Linear create operation"


def test_canonical_skills_load_the_execution_contract():
    skill_dirs = _skill_directories(CANONICAL_SKILLS)
    assert len(skill_dirs) == 17
    contract = CANONICAL_SKILLS / "_shared" / "execution-contract.md"
    assert contract.is_file()
    for skill_dir in skill_dirs:
        assert "../_shared/execution-contract.md" in (skill_dir / "SKILL.md").read_text()


def test_static_canonical_skill_references_resolve():
    for skill_dir in _skill_directories(CANONICAL_SKILLS):
        references = re.findall(
            r"`((?:\.\./)?(?:_shared|references)/[^`\s]+\.md)`",
            (skill_dir / "SKILL.md").read_text(),
        )
        for reference in references:
            if any(marker in reference for marker in ("*", "{", "}")):
                continue
            candidates = (skill_dir / reference, CANONICAL_SKILLS / reference)
            assert any(candidate.resolve().is_file() for candidate in candidates), (
                skill_dir,
                reference,
            )


def test_canonical_skill_entrypoints_stay_compact():
    for skill_dir in _skill_directories(CANONICAL_SKILLS):
        line_count = len((skill_dir / "SKILL.md").read_text().splitlines())
        assert line_count <= 500, (skill_dir, line_count)


def test_execution_contract_and_projected_loaders_share_terminal_statuses():
    contracts = [
        CANONICAL_SKILLS / "_shared" / "execution-contract.md",
        CODEX_SKILLS / "vorbit-shared" / "references" / "load-rules.md",
        GEMINI_SKILLS / "vorbit-shared" / "references" / "load-rules.md",
    ]
    for contract in contracts:
        content = contract.read_text()
        assert all(f"`{status}`" in content for status in TERMINAL_STATUSES), contract


def test_projected_rule_loaders_match_the_resolver_schema():
    loaders = [
        CODEX_SKILLS / "vorbit-shared" / "references" / "load-rules.md",
        GEMINI_SKILLS / "vorbit-shared" / "references" / "load-rules.md",
    ]
    for loader in loaders:
        content = loader.read_text()
        assert "`rules` array" in content, loader
        assert "ascending `order`" in content, loader
        assert "read_order" not in content, loader


def test_prd_workflows_forbid_invented_requirements():
    prd_contracts = [
        CANONICAL_SKILLS / "prd" / "SKILL.md",
        CODEX_SKILLS / "vorbit-shared" / "workflows" / "prd.md",
        GEMINI_SKILLS / "vorbit-shared" / "workflows" / "prd.md",
    ]
    for contract in prd_contracts:
        content = contract.read_text()
        assert "Do not invent" in content or "Never invent" in content, contract
        assert "confirmed, sourced numbers" in content, contract

    for projected in prd_contracts[1:]:
        assert "Do not require an existing Linear ticket to draft" in projected.read_text()


def test_loop_workflows_define_inactive_human_input_state():
    loop_contracts = [
        CANONICAL_SKILLS / "implement-loop" / "SKILL.md",
        CODEX_SKILLS / "vorbit-shared" / "workflows" / "implement-loop.md",
        GEMINI_SKILLS / "vorbit-shared" / "workflows" / "implement-loop.md",
    ]
    for contract in loop_contracts:
        content = contract.read_text()
        assert "active: false" in content, contract
        assert "status: needs_input" in content or 'status: "needs_input"' in content, contract
        assert "status: running" in content or 'status: "running"' in content, contract


def test_mock_registry_guidance_labels_unapproved_endpoints():
    registry_skills = [
        CANONICAL_SKILLS / "implement" / "SKILL.md",
        CANONICAL_SKILLS / "prototype" / "SKILL.md",
        CANONICAL_SKILLS / "implement-cleanup-mocks" / "SKILL.md",
    ]
    for skill in registry_skills:
        content = skill.read_text()
        assert "proposed:" in content, skill
        assert '"version": "1.1"' in content, skill
        assert '"version": "1.0"' not in content, skill
