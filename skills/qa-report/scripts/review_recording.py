#!/usr/bin/env python3
"""Join a QA run's clips into one recording a person can watch in one go.

Usage: review_recording.py MANIFEST.json --out review.mp4

The pr-watch skill writes the manifest from the final QA report:
  {"title": "Billing page, PR #7", "commit": "abc1234", "ticket": "VIB-1", "verdict": "Ready" or "Not ready",
   "flows": [{"id": "QA1", "name": "...", "result": "Passed" or "Failed" or "Not done",
              "reason": "...", "clip": "QA1-x.webm" or null, "commit": "optional, if tested earlier",
              "kind": "optional: 'command' (automated test run) or 'person' (checked by a person), both without video"}]}

A clip path is absolute, or relative to the manifest. The video starts with a summary card.
Each flow then gets a result card, followed by its clip when it has one.
Nothing is invented: a flow without a clip gets a card only. A Passed flow must have a clip, unless it is a command or a person's check.
The original clips stay the evidence. This file is for watching.

Exit: 0 ok, 2 bad manifest, 4 ffmpeg or Pillow missing, 6 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_MANIFEST, EXIT_NO_TOOL, EXIT_FFMPEG = 2, 4, 6

WIDTH, HEIGHT, FPS = 1280, 720, 25
OPENING_SECONDS, CARD_SECONDS = 4, 3
RESULTS = ("Passed", "Failed", "Not done")
COLORS = {"Passed": (74, 222, 128), "Failed": (248, 113, 113), "Not done": (156, 163, 175)}
BACKGROUND, WHITE, GRAY = (17, 24, 39), (243, 244, 246), (156, 163, 175)
NO_CLIP_NOTES = {"command": "Automated check, no video.", "person": "Checked by a person. No video."}
SEGMENT_FLAGS = ["-c:v", "libx264", "-crf", "28", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), "-video_track_timescale", "12800", "-an"]


class Fail(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def load_manifest(path: Path) -> dict:
    try:
        manifest = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise Fail(EXIT_MANIFEST, f"cannot read manifest {path}: {error}")
    for key in ("title", "commit", "verdict"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise Fail(EXIT_MANIFEST, f"manifest needs a text value for '{key}'")
    flows = manifest.get("flows")
    if not isinstance(flows, list) or not flows:
        raise Fail(EXIT_MANIFEST, "manifest needs at least one flow")
    seen = set()
    for flow in flows:
        name = flow.get("id", "?")
        if name in seen:
            raise Fail(EXIT_MANIFEST, f"flow {name} appears twice")
        seen.add(name)
        if flow.get("result") not in RESULTS:
            raise Fail(EXIT_MANIFEST, f"flow {name}: result must be one of {', '.join(RESULTS)}")
        if not flow.get("name"):
            raise Fail(EXIT_MANIFEST, f"flow {name}: needs a name")
        if flow["result"] == "Not done" and not flow.get("reason"):
            raise Fail(EXIT_MANIFEST, f"flow {name}: Not done needs a reason")
        if flow.get("kind") not in (None, *NO_CLIP_NOTES):
            raise Fail(EXIT_MANIFEST, f"flow {name}: kind must be 'command' or 'person'")
        if flow["result"] == "Passed" and not flow.get("clip") and flow.get("kind") not in NO_CLIP_NOTES:
            raise Fail(EXIT_MANIFEST, f"flow {name}: Passed without a clip. A pass needs a recording.")
        if flow.get("clip"):
            clip = path.parent / flow["clip"]
            if not clip.is_file() or clip.stat().st_size == 0:
                raise Fail(EXIT_MANIFEST, f"flow {name}: clip is missing or empty: {clip}")
    return manifest


def counts(manifest: dict) -> dict[str, int]:
    return {result: sum(flow["result"] == result for flow in manifest["flows"]) for result in RESULTS}


def card_lines(manifest: dict, index: int | None) -> list[tuple[str, int, tuple]]:
    """Text for one card as (text, font size, color). index None is the opening card."""
    if index is None:
        total = counts(manifest)
        facts = f"Commit {manifest['commit']}" + (f", ticket {manifest['ticket']}" if manifest.get("ticket") else "")
        verdict_color = COLORS["Passed"] if manifest["verdict"] == "Ready" else COLORS["Failed"]
        return [
            ("Review recording", 30, GRAY), (manifest["title"], 52, WHITE), (facts, 30, GRAY),
            (manifest["verdict"], 84, verdict_color),
            (f"{total['Passed']} passed, {total['Failed']} failed, {total['Not done']} not done", 36, WHITE),
        ]
    flow = manifest["flows"][index]
    lines = [
        (f"Flow {index + 1} of {len(manifest['flows'])}  ({flow['id']})", 30, GRAY),
        (flow["name"], 52, WHITE), (flow["result"], 96, COLORS[flow["result"]]),
    ]
    if flow.get("reason"):
        lines.append((flow["reason"], 34, WHITE))
    if flow.get("commit") and flow["commit"] != manifest["commit"]:
        lines.append((f"Tested earlier, on commit {flow['commit']}", 28, GRAY))
    if not flow.get("clip"):
        lines.append((NO_CLIP_NOTES.get(flow.get("kind"), "No recording for this flow."), 28, GRAY))
    return lines


def draw_card(lines: list[tuple[str, int, tuple]], path: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
        ImageFont.load_default(size=20)
    except (ImportError, TypeError):
        raise Fail(EXIT_NO_TOOL, "Pillow 10.1 or newer is needed for the title cards. Run: pip install pillow")
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    margin = 90
    rows = []
    for text, size, color in lines:
        font = ImageFont.load_default(size=size)
        words, current = text.split(), ""
        for word in words:
            attempt = f"{current} {word}".strip()
            if current and draw.textlength(attempt, font=font) > WIDTH - 2 * margin:
                rows.append((current, font, size, color))
                current = word
            else:
                current = attempt
        rows.append((current, font, size, color))
    height = sum(int(size * 1.35) for _, _, size, _ in rows)
    y = max(40, (HEIGHT - height) // 2)
    for text, font, size, color in rows:
        draw.text((margin, y), text, font=font, fill=color)
        y += int(size * 1.35)
    image.save(path)


def ffmpeg(*args: str) -> None:
    done = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Fail(EXIT_FFMPEG, f"ffmpeg failed: {done.stderr.strip()[:300]}")


def seconds_of(path: Path) -> float:
    done = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(done.stdout.strip())
    except ValueError:
        raise Fail(EXIT_FFMPEG, f"cannot read the length of {path.name}")


def card_segment(lines, seconds: int, folder: Path, name: str) -> Path:
    png, out = folder / f"{name}.png", folder / f"{name}.mp4"
    draw_card(lines, png)
    ffmpeg("-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i", str(png), *SEGMENT_FLAGS, str(out))
    return out


def clip_segment(clip: Path, folder: Path, name: str) -> Path:
    out = folder / f"{name}.mp4"
    fit = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}"
    ffmpeg("-i", str(clip), "-vf", fit, *SEGMENT_FLAGS, str(out))
    return out


def build(manifest: dict, manifest_dir: Path, out: Path) -> dict:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise Fail(EXIT_NO_TOOL, f"{tool} not found. Install ffmpeg, then run again.")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        folder = Path(scratch)
        segments = [card_segment(card_lines(manifest, None), OPENING_SECONDS, folder, "open")]
        for index, flow in enumerate(manifest["flows"]):
            segments.append(card_segment(card_lines(manifest, index), CARD_SECONDS, folder, f"card{index}"))
            if flow.get("clip"):
                segments.append(clip_segment(manifest_dir / flow["clip"], folder, f"clip{index}"))
        expected = sum(seconds_of(segment) for segment in segments)
        listing = folder / "list.txt"
        listing.write_text("".join(f"file '{segment}'\n" for segment in segments))
        partial = out.with_name(f".{out.name}.partial.mp4")
        try:
            ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(partial))
            length = seconds_of(partial)
            if abs(length - expected) > 1.0:
                raise Fail(EXIT_FFMPEG, f"joined video is {length:.1f}s but its parts add up to {expected:.1f}s")
            os.replace(partial, out)
        finally:
            partial.unlink(missing_ok=True)
    return {"out": str(out), "seconds": round(length, 1), "megabytes": round(out.stat().st_size / 1e6, 2), **{k.lower().replace(" ", "_"): v for k, v in counts(manifest).items()}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manifest")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    try:
        manifest = load_manifest(manifest_path)
        result = build(manifest, manifest_path.parent, Path(args.out).resolve())
    except Fail as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return error.code
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
