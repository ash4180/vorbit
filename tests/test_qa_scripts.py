"""The QA skills' helper scripts: E2E proof collection and the QA-mode suite choice."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

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


def run_collect(tmp_path: Path, report: dict, *arguments: str) -> dict:
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))
    output = subprocess.run(
        [sys.executable, str(COLLECT), "--report", str(report_path), "--dest", str(tmp_path / "shots"), "--check", "QP1", *arguments],
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

    manifest = run_collect(tmp_path, report, "--api-only", "QP1-2")
    by_id = {t["id"]: t for t in manifest["tests"]}

    assert manifest["summary"] == {"tests": 4, "passed": 2, "failed": 1, "skipped": 0, "flaky": 1, "needs_evidence": 0, "with_video": 1, "without_proof": 1}
    assert by_id["QP1-setup"]["setup"] is True
    assert by_id["QP1-1"]["proof"] == "video"
    assert Path(by_id["QP1-1"]["evidence"][0]["file"]).is_file()
    assert by_id["QP1-1"]["path"] == "smoke.spec.ts › Smoke › page loads"
    assert by_id["QP1-2"]["proof"] == "pass line"
    assert "API-only confirmed" in by_id["QP1-2"]["note"]
    assert by_id["QP1-2"]["qa_status"] == "passed"
    assert by_id["QP1-3"]["proof"] == "screenshot"
    assert by_id["QP1-3"]["note"] == "Expected 200, got 500"
    assert by_id["QP1-4"]["flaky"] is True
    assert "video lost: page closed" in by_id["QP1-4"]["note"]
    assert (tmp_path / "shots" / "qp1-manifest.json").is_file()


def test_collect_reports_an_unreadable_report(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(COLLECT), "--report", str(tmp_path / "missing.json"), "--dest", str(tmp_path), "--check", "QP1"],
        capture_output=True, text=True,
    )
    assert completed.returncode == 1
    assert "cannot read report" in completed.stdout


def test_collect_does_not_invent_api_only_proof_for_a_pass_without_video(tmp_path):
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("save a profile", "ui.spec.ts", "chromium", [result("passed", [])]),
    ]}]}

    manifest = run_collect(tmp_path, report)
    check = manifest["tests"][0]

    assert check["status"] == "passed", "Keep the runner result separate from QA verification"
    assert check["proof"] == "none", "Missing video does not prove the test opened no page"
    assert check["qa_status"] == "needs_evidence"
    assert manifest["summary"]["passed"] == 0
    assert manifest["summary"]["needs_evidence"] == 1


@pytest.mark.parametrize("evidence_kind", ["screenshot", "missing_video", "empty_video", "lost_video"])
def test_collect_keeps_recording_gaps_unverified(tmp_path, evidence_kind):
    attachments = []
    annotations = []
    if evidence_kind == "screenshot":
        attachments = [attachment(tmp_path / "screen.png", "screenshot", "image/png")]
    if evidence_kind in {"missing_video", "empty_video"}:
        path = tmp_path / "video.webm"
        attachments = [{"name": "video", "contentType": "video/webm", "path": str(path)}]
        if evidence_kind == "empty_video":
            path.touch()
    if evidence_kind == "lost_video":
        annotations = [{"type": "qa-video-missing", "description": "recording failed"}]
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("save", "ui.spec.ts", "chromium", [result("passed", attachments, annotations=annotations)]),
    ]}]}

    # A claimed API-only exception cannot hide explicit evidence of a browser test.
    manifest = run_collect(tmp_path, report, "--api-only", "QP1-1")

    assert manifest["tests"][0]["qa_status"] == "needs_evidence"
    assert manifest["summary"]["passed"] == 0
    assert manifest["summary"]["needs_evidence"] == 1


def test_collect_preserves_recordings_from_failed_attempts_and_retries(tmp_path):
    first = attachment(tmp_path / "failed.webm", "video", "video/webm")
    last = attachment(tmp_path / "passed.webm", "video", "video/webm")
    Path(first["path"]).write_bytes(b"failed attempt")
    Path(last["path"]).write_bytes(b"successful retry")
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("save", "ui.spec.ts", "chromium", [result("failed", [first]), result("passed", [last])]),
    ]}]}

    manifest = run_collect(tmp_path, report)
    check = manifest["tests"][0]

    assert check["qa_status"] == "flaky"
    assert manifest["summary"]["passed"] == 0
    assert manifest["summary"]["flaky"] == 1
    assert [item["attempt"] for item in check["evidence"]] == [1, 2]
    assert [Path(item["file"]).read_bytes() for item in check["evidence"]] == [b"failed attempt", b"successful retry"]
    assert [item["status"] for item in check["evidence"]] == ["failed", "passed"]


def test_collect_does_not_use_an_earlier_recording_as_final_attempt_proof(tmp_path):
    video = attachment(tmp_path / "failed.webm", "video", "video/webm")
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("save", "ui.spec.ts", "chromium", [result("failed", [video]), result("passed", [])]),
    ]}]}

    check = run_collect(tmp_path, report)["tests"][0]

    assert check["qa_status"] == "flaky"
    assert check["proof"] == "none"
    assert "recording missing" in check["note"]
    assert len(check["evidence"]) == 1


@pytest.mark.parametrize("gap", ["missing_attachment", "lost_annotation"])
def test_collect_does_not_pass_a_test_with_only_some_page_recordings(tmp_path, gap):
    attachments = [attachment(tmp_path / "main.webm", "video", "video/webm")]
    annotations = []
    if gap == "missing_attachment":
        attachments.append({"name": "video", "contentType": "video/webm", "path": str(tmp_path / "popup.webm")})
    else:
        annotations = [{"type": "qa-video-missing", "description": "popup recording lost"}]
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("pay in popup", "ui.spec.ts", "chromium", [result("passed", attachments, annotations=annotations)]),
    ]}]}

    manifest = run_collect(tmp_path, report)

    assert manifest["tests"][0]["qa_status"] == "needs_evidence"
    assert len(manifest["tests"][0]["evidence"]) == 1, "Retain the recording that was saved"
    assert manifest["summary"]["passed"] == 0


@pytest.mark.parametrize("status, qa_status", [
    ("failed", "failed"), ("timedOut", "failed"), ("interrupted", "failed"), ("skipped", "not_tested"),
])
def test_collect_preserves_nonpassing_results_even_with_video(tmp_path, status, qa_status):
    video = attachment(tmp_path / "video.webm", "video", "video/webm")
    report = {"suites": [{"title": "ui.spec.ts", "specs": [
        spec("save", "ui.spec.ts", "chromium", [result(status, [video])]),
    ]}]}

    manifest = run_collect(tmp_path, report)

    assert manifest["tests"][0]["qa_status"] == qa_status
    assert manifest["summary"]["passed"] == 0


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
