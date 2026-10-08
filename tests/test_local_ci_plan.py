"""prepare-pr's local CI plan: which pull-request CI commands run locally, and how."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "skills/prepare-pr/scripts/local_ci_plan.py"

# Same shapes as a real Node repo's pr-check.yml: bare `on`, env-pinned node,
# cache-guarded install, sharded matrix tests, CI-output plumbing, summary gate.
PR_WORKFLOW = """
name: PR Check
on:
  pull_request:
    branches: [ main, dev ]
env:
  NODE_VERSION: '22.13.0'
jobs:
  branch:
    runs-on: ubuntu-latest
    steps:
      - name: Check branch name
        run: |
          BRANCH_NAME="${{ github.head_ref }}"
          [[ "$BRANCH_NAME" =~ ^feature/ ]]
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
      - name: Install dependencies
        if: steps.node-modules.outputs.cache-hit != 'true'
        run: yarn install --frozen-lockfile
      - name: Lint
        run: yarn lint
      - name: Resolve version
        run: |
          version=$(node -p "1")
          echo "version=$version" >> "$GITHUB_OUTPUT"
      - name: Deploy preview
        run: ./deploy.sh
        env:
          TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2]
    steps:
      - name: Run tests
        run: yarn test:run --shard=${{ matrix.shard }}/${{ strategy.job-total }} --maxWorkers=2
  checks:
    needs: [quality, test]
    if: always()
    steps:
      - name: Fail when a job failed
        if: contains(needs.*.result, 'failure')
        run: exit 1
      - name: All passed
        run: echo "All checks passed"
"""

NIGHTLY = """
name: Nightly
on:
  schedule:
    - cron: '0 6 * * *'
jobs:
  e2e:
    steps:
      - run: yarn e2e
"""


def run_plan(repo: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(PLAN), "--repo", str(repo), "--head", "feature/x-1", *args],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def repo_with(tmp_path: Path, **workflows: str) -> Path:
    folder = tmp_path / ".github" / "workflows"
    folder.mkdir(parents=True)
    for name, text in workflows.items():
        (folder / f"{name}.yml").write_text(text)
    return tmp_path


def by_step(plan: dict) -> dict:
    return {step["step"]: step for step in plan["steps"]}


def test_only_pull_request_workflows_are_listed(tmp_path: Path) -> None:
    plan = run_plan(repo_with(tmp_path, pr=PR_WORKFLOW, nightly=NIGHTLY), "--base", "dev")
    assert [w["name"] for w in plan["workflows"]] == ["PR Check"]
    assert "yarn e2e" not in [s["command"] for s in plan["steps"]]


def test_branch_filter_excludes_other_bases(tmp_path: Path) -> None:
    plan = run_plan(repo_with(tmp_path, pr=PR_WORKFLOW), "--base", "release")
    assert plan["workflows"] == []


def test_steps_are_classified(tmp_path: Path) -> None:
    steps = by_step(run_plan(repo_with(tmp_path, pr=PR_WORKFLOW), "--base", "dev"))
    assert steps["Install dependencies"]["kind"] == "setup"
    # `yarn lint` must not be mistaken for the bare `yarn` install.
    assert steps["Lint"]["kind"] == "check"
    assert steps["Resolve version"]["kind"] == "skip"
    assert steps["Deploy preview"]["kind"] == "skip"
    assert steps["Fail when a job failed"]["kind"] == "gate"
    assert steps["All passed"]["kind"] == "skip"


def test_shards_are_removed_and_branch_names_filled(tmp_path: Path) -> None:
    steps = by_step(run_plan(repo_with(tmp_path, pr=PR_WORKFLOW), "--base", "dev"))
    assert steps["Run tests"]["command"] == "yarn test:run --maxWorkers=2"
    assert steps["Run tests"]["notes"]
    assert 'BRANCH_NAME="feature/x-1"' in steps["Check branch name"]["command"]
    assert steps["Check branch name"]["notes"] == []


def test_pinned_tool_versions_resolve_env(tmp_path: Path) -> None:
    plan = run_plan(repo_with(tmp_path, pr=PR_WORKFLOW), "--base", "dev")
    assert plan["tool_versions"] == [{"tool": "node", "version": "22.13.0"}]


def test_no_workflows_folder_gives_empty_plan(tmp_path: Path) -> None:
    plan = run_plan(tmp_path, "--base", "dev")
    assert plan == {"workflows": [], "steps": [], "tool_versions": []}
