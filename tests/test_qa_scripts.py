"""The QA skills' helper scripts: E2E proof collection and the QA-mode suite choice."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / "skills/qa-report/scripts/collect_e2e_evidence.py"
SCAN = ROOT / "skills/qa-plan/scripts/regression_scan.py"


def attachment(path: Path, name: str, content_type: str) -> dict:
    path.write_bytes(b"x")
    return {"name": name, "contentType": content_type, "path": str(path)}


def result(status: str, attachments: list, errors: list | None = None, annotations: list | None = None) -> dict:
    # Same fields a real Playwright 1.60 JSON report carries per result.
    return {"status": status, "retry": 0, "attachments": attachments, "errors": errors or [], "annotations": annotations or []}


def spec(title: str, file: str, project: str, results: list) -> dict:
    return {"title": title, "file": file, "line": 1, "tests": [{"projectName": project, "results": results, "annotations": []}]}


def run_collect(tmp_path: Path, report: dict) -> dict:
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))
    output = subprocess.run(
        [sys.executable, str(COLLECT), "--report", str(report_path), "--dest", str(tmp_path / "shots"), "--check", "QP1"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(output)


def test_collect_copies_each_tests_proof_and_explains_gaps(tmp_path):
    src = tmp_path / "test-results"
    src.mkdir()
    report = {"suites": [
        {"title": "auth.setup.ts", "specs": [spec("log in", "auth.setup.ts", "setup", [
            result("passed", [attachment(src / "setup.webm", "qa-video", "video/webm")])])]},
        {"title": "smoke.spec.ts", "specs": [], "suites": [{"title": "Smoke", "specs": [
            spec("page loads", "smoke.spec.ts", "chromium", [
                result("passed", [attachment(src / "a.webm", "qa-video", "video/webm")])]),
            spec("health API", "smoke.spec.ts", "chromium", [result("passed", [])]),
            spec("save fails", "smoke.spec.ts", "chromium", [
                result("failed", [attachment(src / "b.png", "screenshot", "image/png")],
                       errors=[{"message": "\x1b[31mExpected 200\x1b[0m, got 500\nstack"}])]),
            spec("retried", "smoke.spec.ts", "chromium", [
                result("failed", []),
                result("passed", [], annotations=[{"type": "qa-video-missing", "description": "page closed"}])]),
        ]}]},
    ]}

    manifest = run_collect(tmp_path, report)
    by_id = {t["id"]: t for t in manifest["tests"]}

    assert manifest["summary"] == {"tests": 4, "passed": 3, "failed": 1, "skipped": 0, "flaky": 1, "with_video": 1, "without_proof": 0}
    assert by_id["QP1-setup"]["setup"] is True
    assert by_id["QP1-1"]["proof"] == "video"
    assert Path(by_id["QP1-1"]["evidence"][0]["file"]).is_file()
    assert by_id["QP1-1"]["path"] == "smoke.spec.ts › Smoke › page loads"
    assert by_id["QP1-2"]["proof"] == "pass line"
    assert by_id["QP1-2"]["note"] == "no video: the test opened no page"
    assert by_id["QP1-3"]["proof"] == "screenshot"
    assert by_id["QP1-3"]["note"] == "Expected 200, got 500"
    assert by_id["QP1-4"]["flaky"] is True
    assert by_id["QP1-4"]["note"] == "video lost: page closed"
    assert (tmp_path / "shots" / "qp1-manifest.json").is_file()


def test_collect_reports_an_unreadable_report(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(COLLECT), "--report", str(tmp_path / "missing.json"), "--dest", str(tmp_path), "--check", "QP1"],
        capture_output=True, text=True,
    )
    assert completed.returncode == 1
    assert "cannot read report" in completed.stdout


def scan_suites(project: Path, scripts: dict) -> list:
    (project / "package.json").write_text(json.dumps({"scripts": scripts}))
    subprocess.run(["git", "add", "-A"], cwd=project, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"], cwd=project, check=True)
    output = subprocess.run([sys.executable, str(SCAN), "--base", "HEAD"], cwd=project, capture_output=True, text=True, check=True).stdout
    return json.loads(output)["e2e_suites"]


def test_scan_prefers_the_qa_mode_suite(temp_project):
    suites = scan_suites(temp_project, {
        "e2e": "playwright test",
        "e2e:qa": "E2E_QA_MODE=1 playwright test",
        "e2e:staging": "E2E_TARGET_ENV=staging playwright test",
    })
    primary = [s["script"] for s in suites if s["primary"]]
    assert primary == ["e2e:qa"]


def test_scan_keeps_the_plain_suite_without_a_qa_mode(temp_project):
    suites = scan_suites(temp_project, {"e2e": "playwright test", "e2e:ui": "playwright test --ui"})
    assert [s["script"] for s in suites if s["primary"]] == ["e2e"]
    assert all(not s["qa_mode"] for s in suites)
