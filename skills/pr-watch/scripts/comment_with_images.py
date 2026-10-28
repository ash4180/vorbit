#!/usr/bin/env python3
"""Post a PR comment with screenshots. The GitHub CLI cannot upload images, so the Orca browser does it.

Usage:
  comment_with_images.py --pr N --images a.png b.png --body-file comment.md
                         [--repo OWNER/REPO] [--expect-head SHA] [--dry-run]

The body file holds {{image:1}}, {{image:2}} ... in the order of --images.
--dry-run only checks inputs, tools and the PR. It uploads and posts nothing.
Prints one TAG line per uploaded image, then a last line that starts with PASS or FAIL.

Exit: 0 pass, 2 bad input, 3 sign in to GitHub in the Orca browser then run again,
4 tool missing, 5 PR head moved, 6 upload failed, 7 comment posted but an image is broken.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXIT_INPUT, EXIT_SIGN_IN, EXIT_NO_TOOL, EXIT_MOVED, EXIT_UPLOAD, EXIT_BROKEN = 2, 3, 4, 5, 6, 7

UPLOAD_LABEL = "pr-watch-upload"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
TAG = re.compile(
    r'<img\b[^>]*\bsrc="https://github\.com/user-attachments/[^"]+"[^>]*>'
    r"|!\[[^\]]*\]\(https://github\.com/user-attachments/[^)]+\)"
)
PLACEHOLDER = re.compile(r"\{\{image:(\d+)\}\}")

UNHIDE_JS = """(() => {
  const box = document.getElementById('new_comment_field');
  if (!box) return 'no-box';
  const input = box.closest('form').querySelector('input[type=file]');
  if (!input) return 'no-input';
  Object.assign(input.style, {display: 'block', position: 'fixed', top: '0', left: '0', opacity: '1'});
  input.setAttribute('aria-label', '%s');
  return 'ok';
})()""" % UPLOAD_LABEL
BOX_TEXT_JS = "(document.getElementById('new_comment_field') || {value: null}).value"
CLEAR_BOX_JS = """(() => {
  const box = document.getElementById('new_comment_field');
  if (!box) return null;
  box.value = '';
  box.dispatchEvent(new Event('input', {bubbles: true}));
  return box.value;
})()"""
IMAGES_JS = """(id => {
  const root = document.getElementById(id);
  if (!root) return 'null';
  root.scrollIntoView();
  const body = root.querySelector('.comment-body') || root;
  return JSON.stringify([...body.querySelectorAll('img')].filter(i => !i.classList.contains('emoji')).map(i => {
    i.loading = 'eager';
    return {ok: i.complete && i.naturalWidth > 0, width: i.naturalWidth};
  }));
})(%s)"""


class Fail(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def extract_tags(text: str) -> list[str]:
    return TAG.findall(text)


def fill_placeholders(body: str, tags: list[str]) -> str:
    wrong = [n for n in map(int, PLACEHOLDER.findall(body)) if not 1 <= n <= len(tags)]
    if wrong:
        raise Fail(EXIT_INPUT, f"body has {{{{image:{wrong[0]}}}}} but only {len(tags)} images")
    return PLACEHOLDER.sub(lambda match: tags[int(match.group(1)) - 1], body)


def check_inputs(images: list[str], body: str) -> None:
    for image in images:
        path = Path(image)
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            raise Fail(EXIT_INPUT, f"not an image file: {image}")
        if "," in image:
            raise Fail(EXIT_INPUT, f"a comma in the file name breaks the upload: {image}")
    used = {int(n) for n in PLACEHOLDER.findall(body)}
    missing = set(range(1, len(images) + 1)) - used
    if missing:
        raise Fail(EXIT_INPUT, f"body never uses {{{{image:{min(missing)}}}}}")
    fill_placeholders(body, [""] * len(images))


def run(command: list[str], code: int) -> str:
    done = subprocess.run(command, capture_output=True, text=True)
    if done.returncode != 0:
        raise Fail(code, f"{' '.join(command[:4])} failed: {(done.stderr or done.stdout).strip()[:300]}")
    return done.stdout


def pr_facts(pr: str, repo: str | None) -> dict:
    command = ["gh", "pr", "view", pr, "--json", "url,headRefOid,state"] + (["--repo", repo] if repo else [])
    return json.loads(run(command, EXIT_INPUT))


def wait_until(read, done, timeout: float, step: float = 1.0):
    end = time.monotonic() + timeout
    while True:
        value = read()
        if done(value) or time.monotonic() > end:
            return value
        time.sleep(step)


class Browser:
    """One Orca browser tab. Every call goes to that tab by page id."""

    def __init__(self, url: str):
        created = self.orca("tab", "create", "--url", url, page=False)
        self.page = created["browserPageId"]

    def orca(self, *args: str, page: bool = True, code: int = EXIT_UPLOAD) -> dict:
        command = ["orca", *args] + (["--page", self.page] if page else []) + ["--json"]
        done = subprocess.run(command, capture_output=True, text=True)
        try:
            out = json.loads(done.stdout)
        except ValueError:
            raise Fail(code, f"orca {args[0]} gave no JSON: {(done.stderr or done.stdout).strip()[:300]}")
        if done.returncode != 0 or not out.get("ok"):
            raise Fail(code, f"orca {args[0]} failed: {json.dumps(out.get('error', out))[:300]}")
        return out["result"]

    def js(self, expression: str):
        return self.orca("eval", "--expression", expression)["result"]

    def js_json(self, expression: str):
        value = self.js(expression)
        return json.loads(value) if isinstance(value, str) else value

    def close(self) -> None:
        self.orca("tab", "close", code=EXIT_UPLOAD)

    def box_ready(self) -> bool:
        def read():
            try:
                return self.js(BOX_TEXT_JS)
            except Fail:
                return None

        return wait_until(read, lambda text: text is not None, 20) is not None

    def upload(self, images: list[str], count: int) -> list[str]:
        if self.js(UNHIDE_JS) != "ok":
            raise Fail(EXIT_UPLOAD, "could not find the hidden file input next to the comment box")
        refs = self.orca("snapshot")["refs"]
        ref = next((key for key, item in refs.items() if item.get("name") == UPLOAD_LABEL), None)
        if ref is None:
            raise Fail(EXIT_UPLOAD, "the file input has no ref in the snapshot")
        self.orca("upload", "--element", f"@{ref}", "--files", ",".join(str(Path(i).resolve()) for i in images))
        text = wait_until(
            lambda: self.js(BOX_TEXT_JS) or "",
            lambda value: len(extract_tags(value)) >= count and "Uploading" not in value,
            90,
        )
        tags = extract_tags(text)
        if len(tags) != count or "Uploading" in text:
            raise Fail(EXIT_UPLOAD, f"expected {count} image tags, found {len(tags)}")
        return tags

    def clear_box(self) -> None:
        if self.js(CLEAR_BOX_JS) not in ("", None):
            raise Fail(EXIT_UPLOAD, "could not clear the comment box")

    def broken_images(self, comment_url: str, count: int, timeout: float = 30) -> list[int]:
        found_id = re.search(r"#(issuecomment-\d+)", comment_url)
        if not found_id:
            raise Fail(EXIT_BROKEN, f"comment is posted but gh gave no comment id: {comment_url}")
        comment_id = found_id.group(1)
        self.orca("goto", "--url", comment_url)
        expression = IMAGES_JS % json.dumps(comment_id)
        found = wait_until(
            lambda: self.js_json(expression),
            lambda items: bool(items) and len(items) == count and all(item["ok"] for item in items),
            timeout,
        )
        if not found or len(found) != count:
            return list(range(1, count + 1))
        return [number for number, item in enumerate(found, 1) if not item["ok"]]


def post(args: argparse.Namespace, facts: dict, body: str) -> str:
    browser = Browser(facts["url"])
    try:
        if not browser.box_ready():
            raise Fail(EXIT_SIGN_IN, f"no comment box on {facts['url']}. Sign in to GitHub in the Orca browser tab, then run again.")
        try:
            tags = browser.upload(args.images, len(args.images))
        finally:
            browser.clear_box()
        for tag in tags:
            print(f"TAG {tag}")
        if args.expect_head and pr_facts(args.pr, args.repo)["headRefOid"] != args.expect_head:
            raise Fail(EXIT_MOVED, "the PR head moved while uploading. Nothing was posted. Re-test the new commit.")
        with tempfile.TemporaryDirectory() as folder:
            resolved = Path(folder) / "comment.md"
            resolved.write_text(fill_placeholders(body, tags))
            posted = run(["gh", "pr", "comment", args.pr, "--body-file", str(resolved)] + (["--repo", args.repo] if args.repo else []), EXIT_UPLOAD)
        comment_url = posted.strip().splitlines()[-1]
        broken = browser.broken_images(comment_url, len(tags))
        if broken:
            raise Fail(EXIT_BROKEN, f"comment is posted ({comment_url}) but image {broken} did not load")
        browser.close()
        return comment_url
    except Fail as error:
        if error.code != EXIT_SIGN_IN:
            print(f"Browser tab {browser.page} left open to inspect.", file=sys.stderr)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--images", nargs="+", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--repo")
    parser.add_argument("--expect-head")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        for tool in ("gh", "orca"):
            if not shutil.which(tool):
                raise Fail(EXIT_NO_TOOL, f"{tool} not found. Install it, then run again.")
        body_path = Path(args.body_file)
        if not body_path.is_file():
            raise Fail(EXIT_INPUT, f"body file not found: {args.body_file}")
        body = body_path.read_text()
        check_inputs(args.images, body)
        facts = pr_facts(args.pr, args.repo)
        if facts["state"] != "OPEN":
            raise Fail(EXIT_INPUT, f"PR is {facts['state']}, not OPEN")
        if args.expect_head and facts["headRefOid"] != args.expect_head:
            raise Fail(EXIT_MOVED, f"PR head is {facts['headRefOid'][:9]}, expected {args.expect_head[:9]}. Re-test first.")
        if args.dry_run:
            print(f"PASS dry run: {len(args.images)} images, PR open, head {facts['headRefOid'][:9]}. Nothing uploaded or posted.")
            return 0
        url = post(args, facts, body)
    except Fail as error:
        print(f"FAIL {error}")
        return error.code
    print(f"PASS comment={url} images={len(args.images)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
