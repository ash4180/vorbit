#!/usr/bin/env python3
"""Copy every test's proof out of a Playwright JSON report, before the next run wipes it.

Playwright's JSON report names each test, its result, and the exact path of every
file attached to it (videos, screenshots, traces). This script copies those files
into the QA run's evidence folder and prints one manifest entry per test, so the
report never guesses which video belongs to which test.

Usage: python3 collect_e2e_evidence.py --report <playwright.json> --dest <run evidence folder> --check QP1
Use --api-only QP1-2 only after inspecting that test and its fixtures to confirm
it never opens a page. Repeat the flag for other confirmed API-only tests.

Prints JSON: {"check", "summary", "tests": [...]}. Each test entry has:
  id            QP1-1, QP1-2, ... in report order (setup steps are not numbered)
  title         the test name; path is file › group › test
  status        passed | failed | timedOut | skipped | interrupted
  qa_status     passed | failed | flaky | not_tested | needs_evidence
  flaky         true when it passed only on a retry
  setup         true for setup steps (a "setup" project or a *.setup.* file); not a check
  evidence      copied files from every attempt: kind, file, attempt (1-based), status
  proof         video | screenshot | pass line | none; final attempt only
  note          missing recording, confirmed API-only check, or first error line
Summary passed counts verified, non-flaky passes, not raw runner passes.
Exit codes: 0 when the report was read, 1 when it could not be read.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterator

SETUP_FILE = re.compile(r"\.setup\.[cm]?[jt]sx?$")


def kind_of(attachment: dict[str, Any]) -> str:
    content_type = attachment.get("contentType", "")
    if content_type.startswith("video/"):
        return "video"
    if content_type.startswith("image/"):
        return "screenshot"
    if content_type == "application/zip" or attachment.get("name") == "trace":
        return "trace"
    return "other"


def walk(suite: dict[str, Any], titles: list[str]) -> Iterator[tuple[list[str], dict[str, Any], dict[str, Any]]]:
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            yield titles + [spec.get("title", "")], spec, test
    for child in suite.get("suites", []):
        yield from walk(child, titles + [child.get("title", "")])


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "test"


def copy_evidence(results: list[dict[str, Any]], dest: Path, label: str) -> list[dict[str, Any]]:
    evidence = []
    for attempt, result in enumerate(results, start=1):
        for index, attachment in enumerate(result.get("attachments", [])):
            source = Path(attachment["path"]) if attachment.get("path") else None
            if source is None or not source.is_file() or source.stat().st_size == 0:
                continue
            name = f"{label}-attempt-{attempt}-{index}{source.suffix or '.bin'}"
            shutil.copy2(source, dest / name)
            evidence.append({
                "kind": kind_of(attachment), "file": str(dest / name),
                "attempt": attempt, "status": result.get("status", "skipped"),
            })
    return evidence


def assess_result(test: dict[str, Any], evidence: list[dict[str, Any]], api_only: bool) -> tuple[str, str, str]:
    """Separate what the runner reported from what this QA run can prove."""
    results = test.get("results") or [{}]
    last = results[-1]
    status = last.get("status", "skipped")
    final_evidence = [item for item in evidence if item["attempt"] == len(results)]
    kinds = {item["kind"] for item in final_evidence}
    proof = "none"
    if "screenshot" in kinds:
        proof = "screenshot"
    if "video" in kinds:
        proof = "video"
    annotations = test.get("annotations", []) + last.get("annotations", [])
    lost = [a for a in annotations if a.get("type") == "qa-video-missing"]
    attachment_kinds = [kind_of(a) for a in last.get("attachments", [])]
    visual_attachments = any(kind in {"video", "screenshot"} for kind in attachment_kinds)
    missing_video = attachment_kinds.count("video") > sum(item["kind"] == "video" for item in final_evidence)
    confirmed_api = api_only and not lost and not visual_attachments
    note = ""
    if proof != "video":
        note = "recording missing: final attempt has no saved video; API-only not confirmed"
    if missing_video:
        note = "recording missing: one or more attached videos are missing or empty"
    if lost:
        note = "video lost: " + lost[0].get("description", "")[:200]
    if status == "passed" and confirmed_api:
        proof, note = "pass line", "API-only confirmed by caller after inspecting test and fixtures"
    if status == "skipped":
        return "not_tested", proof, "test was skipped or did not run"
    if status != "passed" or test.get("expectedStatus", "passed") != "passed":
        errors = last.get("errors") or [last.get("error") or {}]
        message = re.sub(r"\x1b\[[0-9;]*m", "", errors[0].get("message") or "").strip()
        return "failed", proof, message.splitlines()[0][:300] if message else f"runner result: {status}"
    if len(results) > 1 or test.get("status") == "flaky":
        return "flaky", proof, "passed only on a retry" + (f"; {note}" if note else "")
    if lost or missing_video or proof not in {"video", "pass line"}:
        return "needs_evidence", proof, note
    return "passed", proof, note


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--check", required=True, help="the plan's QP# for this command")
    parser.add_argument("--api-only", action="append", default=[], metavar="TEST_ID",
                        help="collector test ID confirmed by source inspection to open no page (repeatable)")
    args = parser.parse_args()

    try:
        report = json.loads(Path(args.report).read_text())
    except (OSError, ValueError) as error:
        print(json.dumps({"error": f"cannot read report: {error}"}))
        return 1

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    tests: list[dict[str, Any]] = []
    number = 0

    for titles, spec, test in walk(report, []):
        results = test.get("results") or [{}]
        project = test.get("projectName", "")
        file = spec.get("file", "")
        setup = project == "setup" or bool(SETUP_FILE.search(file))
        if not setup:
            number += 1
        test_id = f"{args.check}-{number}" if not setup else f"{args.check}-setup"
        label = f"{test_id.lower()}-{slug(titles[-1])}"
        if setup:
            label += f"-{len(tests)}"
        evidence = copy_evidence(results, dest, label)
        qa_status, proof, note = assess_result(test, evidence, test_id in args.api_only)
        tests.append({
            "id": test_id,
            "title": titles[-1],
            "path": " › ".join(t for t in titles if t),
            "file": file,
            "line": spec.get("line"),
            "project": project,
            "status": results[-1].get("status", "skipped"),
            "qa_status": qa_status,
            "flaky": qa_status == "flaky",
            "setup": setup,
            "evidence": evidence,
            "proof": proof,
            "note": note,
        })

    checks = [t for t in tests if not t["setup"]]
    summary = {
        "tests": len(checks),
        "passed": sum(t["qa_status"] == "passed" for t in checks),
        "failed": sum(t["qa_status"] == "failed" for t in checks),
        "skipped": sum(t["qa_status"] == "not_tested" for t in checks),
        "flaky": sum(t["flaky"] for t in checks),
        "needs_evidence": sum(t["qa_status"] == "needs_evidence" for t in checks),
        "with_video": sum(t["proof"] == "video" for t in checks),
        "without_proof": sum(t["proof"] == "none" for t in checks),
    }
    manifest = {"check": args.check, "summary": summary, "tests": tests}
    (dest / f"{args.check.lower()}-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
