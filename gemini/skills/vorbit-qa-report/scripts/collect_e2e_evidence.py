#!/usr/bin/env python3
"""Copy every test's proof out of a Playwright JSON report, before the next run wipes it.

Playwright's JSON report names each test, its result, and the exact path of every
file attached to it (videos, screenshots, traces). This script copies those files
into the QA run's picture folder and prints one manifest entry per test, so the
report never guesses which video belongs to which test.

Usage: python3 collect_e2e_evidence.py --report <playwright.json> --dest <run picture folder> --check QP1

Prints JSON: {"check", "summary", "tests": [...]}. Each test entry has:
  id            QP1-1, QP1-2, ... in report order (setup steps are not numbered)
  title         the test name; path is file › group › test
  status        passed | failed | timedOut | skipped | interrupted
  flaky         true when it passed only on a retry
  setup         true for setup steps (a "setup" project or a *.setup.* file); not a check
  evidence      copied files: {"kind": video | screenshot | trace | other, "file": relative path}
  proof         video | screenshot | pass line | none
  note          why a proof is missing (no page, video lost), or the first error line
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--check", required=True, help="the plan's QP# for this command")
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

    for suite in report.get("suites", []):
        for titles, spec, test in walk(suite, [suite.get("title", "")]):
            results = test.get("results") or [{}]
            last = results[-1]
            project = test.get("projectName", "")
            file = spec.get("file", "")
            setup = project == "setup" or bool(SETUP_FILE.search(file))
            if not setup:
                number += 1
            test_id = f"{args.check}-{number}" if not setup else f"{args.check}-setup"
            status = last.get("status", "skipped")

            evidence = []
            for index, attachment in enumerate(last.get("attachments", [])):
                source = attachment.get("path")
                if not source or not Path(source).is_file():
                    continue
                kind = kind_of(attachment)
                suffix = Path(source).suffix or ".bin"
                extra = f"-{index}" if index else ""
                name = f"{test_id.lower()}-{slug(titles[-1])}{extra}{suffix}"
                shutil.copy2(source, dest / name)
                evidence.append({"kind": kind, "file": str(dest / name)})

            kinds = {e["kind"] for e in evidence}
            note = ""
            if "video" in kinds:
                proof = "video"
            elif "screenshot" in kinds:
                proof = "screenshot"
            elif status == "passed":
                proof = "pass line"
                lost = [a for a in test.get("annotations", []) + last.get("annotations", []) if a.get("type") == "qa-video-missing"]
                note = "video lost: " + lost[0].get("description", "")[:200] if lost else "no video: the test opened no page"
            else:
                proof = "none"
            if status not in ("passed", "skipped"):
                errors = last.get("errors") or [last.get("error") or {}]
                message = (errors[0].get("message") or "") if errors else ""
                note = re.sub(r"\x1b\[[0-9;]*m", "", message).strip().splitlines()[0][:300] if message.strip() else note

            tests.append({
                "id": test_id,
                "title": titles[-1],
                "path": " › ".join(t for t in titles if t),
                "file": file,
                "line": spec.get("line"),
                "project": project,
                "status": status,
                "flaky": status == "passed" and len(results) > 1,
                "setup": setup,
                "evidence": evidence,
                "proof": proof,
                "note": note,
            })

    checks = [t for t in tests if not t["setup"]]
    summary = {
        "tests": len(checks),
        "passed": sum(t["status"] == "passed" for t in checks),
        "failed": sum(t["status"] not in ("passed", "skipped") for t in checks),
        "skipped": sum(t["status"] == "skipped" for t in checks),
        "flaky": sum(t["flaky"] for t in checks),
        "with_video": sum(t["proof"] == "video" for t in checks),
        "without_proof": sum(t["proof"] == "none" for t in checks),
    }
    manifest = {"check": args.check, "summary": summary, "tests": tests}
    (dest / f"{args.check.lower()}-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
