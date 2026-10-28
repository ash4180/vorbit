"""The QA skills' helper scripts: E2E proof collection and the QA-mode suite choice."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Importing a script writes __pycache__ beside it, and the mirror check treats that as drift.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / "skills/qa-report/scripts/collect_e2e_evidence.py"
SCAN = ROOT / "skills/qa-plan/scripts/regression_scan.py"
REVIEW = ROOT / "skills/qa-report/scripts/review_recording.py"

_spec = importlib.util.spec_from_file_location("review_recording", REVIEW)
review_recording = importlib.util.module_from_spec(_spec)
sys.modules["review_recording"] = review_recording
_spec.loader.exec_module(review_recording)


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


# --- review_recording: one video joined from the run's clips -----------------------------

needs_video_tools = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None or importlib.util.find_spec("PIL") is None,
    reason="ffmpeg and Pillow are needed",
)


def flow(**fields):
    return {"id": "QA1", "name": "Search a word", "result": "Passed", "reason": "ok", "clip": None, **fields}


def write_manifest(folder: Path, flows: list, **top) -> Path:
    path = folder / "review-manifest.json"
    path.write_text(json.dumps({"title": "Search, PR #7", "commit": "abc1234", "ticket": "VIB-1", "verdict": "Not ready", "flows": flows, **top}))
    return path


def bad_manifest(tmp_path, flows, match):
    with pytest.raises(review_recording.Fail) as error:
        review_recording.load_manifest(write_manifest(tmp_path, flows))
    assert error.value.code == review_recording.EXIT_MANIFEST
    assert match in str(error.value)


def test_a_passed_browser_flow_without_a_clip_is_refused(tmp_path):
    bad_manifest(tmp_path, [flow()], "A pass needs a recording")


@pytest.mark.parametrize("kind", ["command", "person"])
def test_a_passed_command_or_person_check_may_have_no_clip(tmp_path, kind):
    review_recording.load_manifest(write_manifest(tmp_path, [flow(id="QP1", kind=kind)]))


def test_an_unknown_kind_is_refused(tmp_path):
    bad_manifest(tmp_path, [flow(kind="robot")], "kind must be")


def test_manifest_rules_for_reason_result_clip_and_ids(tmp_path):
    bad_manifest(tmp_path, [flow(result="Not done", reason="")], "needs a reason")
    bad_manifest(tmp_path, [flow(result="Flaky")], "result must be one of")
    bad_manifest(tmp_path, [flow(result="Failed", clip="gone.webm")], "missing or empty")
    bad_manifest(tmp_path, [flow(result="Not done", reason="x"), flow(result="Not done", reason="y")], "appears twice")
    bad_manifest(tmp_path, [], "at least one flow")
    (tmp_path / "empty.webm").write_bytes(b"")
    bad_manifest(tmp_path, [flow(result="Failed", clip="empty.webm")], "missing or empty")


def test_cards_show_counts_and_say_when_a_pass_is_from_an_earlier_commit_or_a_person():
    manifest = {"title": "T", "commit": "abc1234", "ticket": "VIB-1", "verdict": "Ready", "flows": [
        flow(), flow(id="QA2", result="Failed", commit="old9999"),
        flow(id="QA3", result="Not done", reason="no data"), flow(id="QA4", kind="person")]}
    opening = [text for text, _, _ in review_recording.card_lines(manifest, None)]
    assert "2 passed, 1 failed, 1 not done" in opening
    earlier = [text for text, _, _ in review_recording.card_lines(manifest, 1)]
    assert "Tested earlier, on commit old9999" in earlier
    assert not any("Tested earlier" in text for text, _, _ in review_recording.card_lines(manifest, 0))
    person = [text for text, _, _ in review_recording.card_lines(manifest, 3)]
    assert "Checked by a person. No video." in person


def make_clip(path: Path, seconds: int, size: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=duration={seconds}:size={size}:rate=25", "-c:v", "libvpx", str(path)],
        check=True,
    )


def frame_at(video: Path, seconds: float, out: Path):
    from PIL import Image
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(seconds), "-i", str(video), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


@needs_video_tools
def test_recording_joins_cards_and_clips_in_order_with_real_footage(tmp_path):
    make_clip(tmp_path / "a.webm", 2, "320x240")
    make_clip(tmp_path / "b.webm", 1, "640x360")
    flows = [
        flow(id="QA1", name="First", clip="a.webm"),
        flow(id="QA2", name="Second", result="Failed", reason="Saw the wrong thing", clip="b.webm"),
        flow(id="QA3", name="Third", result="Not done", reason="need data"),
        flow(id="QP1", name="Tests", kind="command", reason="3 of 3"),
    ]
    out = tmp_path / "out" / "review.mp4"
    done = subprocess.run([sys.executable, "-B", str(REVIEW), str(write_manifest(tmp_path, flows)), "--out", str(out)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert (result["passed"], result["failed"], result["not_done"]) == (2, 1, 1)
    assert abs(result["seconds"] - (4 + 4 * 3 + 2 + 1)) < 1.0
    assert not list(out.parent.glob(".*partial*"))

    opening = frame_at(out, 1, tmp_path / "f1.png")
    assert opening.getextrema()[0][1] > 200, "the opening card has bright text"
    footage = frame_at(out, 4 + 3 + 0.5, tmp_path / "f2.png")
    assert len(footage.getcolors(maxcolors=100000)) > 50, "the clip frame is real picture content, not a flat card"
    no_clip_card = frame_at(out, 4 + 3 + 2 + 3 + 1 + 1.5, tmp_path / "f3.png")
    assert no_clip_card.getextrema()[0][1] > 120, "the Not done card has text"


@needs_video_tools
def test_a_bad_manifest_makes_no_video(tmp_path):
    out = tmp_path / "review.mp4"
    done = subprocess.run([sys.executable, "-B", str(REVIEW), str(write_manifest(tmp_path, [flow()])), "--out", str(out)], capture_output=True, text=True)
    assert done.returncode == review_recording.EXIT_MANIFEST
    assert "A pass needs a recording" in done.stderr
    assert not out.exists()
