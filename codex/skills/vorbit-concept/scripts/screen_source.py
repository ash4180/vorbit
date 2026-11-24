"""Read a screen source file and compare a drawing with it.

A screen source file lists what the real screen is made of: its code files,
components, colors, fonts and features. Every entry carries evidence, a piece
of text that must be found in the listed code files. So an agent cannot list a
component, a color or a feature that the project does not have.

The format is in references/screen-source.md. Standard library only.
"""

from __future__ import annotations

import colorsys
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

MIN_EVIDENCE_CHARS = 3
GENERIC_FONTS = frozenset(
    "serif sans-serif monospace cursive fantasy system-ui ui-sans-serif ui-serif "
    "ui-monospace ui-rounded inherit initial unset -apple-system blinkmacsystemfont".split()
)
COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|hsl)a?\([^)]*\)")
FONT_PATTERN = re.compile(r"font-family\s*:\s*([^;]+)")


@dataclass(frozen=True)
class Color:
    rgb: str
    see_through: bool


def _numbers(text: str) -> list[float]:
    return [float(part) for part in re.findall(r"-?\d*\.?\d+", text)]


def parse_color(text: str) -> Color | None:
    text = text.strip().lower()
    if text.startswith("#"):
        digits = text[1:]
        if len(digits) in (3, 4):
            digits = "".join(char * 2 for char in digits)
        if len(digits) not in (6, 8):
            return None
        return Color("#" + digits[:6], len(digits) == 8 and digits[6:] != "ff")
    numbers = _numbers(text)
    if len(numbers) < 3:
        return None
    if text.startswith("hsl"):
        red, green, blue = colorsys.hls_to_rgb(numbers[0] / 360, numbers[2] / 100, numbers[1] / 100)
        channels = [round(red * 255), round(green * 255), round(blue * 255)]
    else:
        channels = [round(number) for number in numbers[:3]]
    if any(not 0 <= channel <= 255 for channel in channels):
        return None
    alpha = numbers[3] if len(numbers) > 3 else 1.0
    if "%" in text.split(",")[-1] and len(numbers) > 3 and not text.startswith("hsl"):
        alpha /= 100
    return Color("#" + "".join(f"{channel:02x}" for channel in channels), alpha < 1)


def colors_in(text: str) -> list[Color]:
    found = (parse_color(match) for match in COLOR_PATTERN.findall(text))
    return [color for color in found if color]


def fonts_in(style: str) -> list[str]:
    fonts: list[str] = []
    for families in FONT_PATTERN.findall(style):
        first = families.split(",")[0].strip().strip("\"'")
        if first and first.lower() not in GENERIC_FONTS:
            fonts.append(first)
    return fonts


@dataclass
class Design:
    """What a drawing uses. Collected while the frame file is read."""

    colors: list[Color] = field(default_factory=list)
    fonts: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    texts: list[str] = field(default_factory=list)

    def add_element(self, attrs: dict[str, str]) -> None:
        style = attrs.get("style", "")
        self.colors += colors_in(" ".join((style, attrs.get("fill", ""), attrs.get("stroke", ""))))
        self.fonts += fonts_in(style)
        if attrs.get("data-src"):
            self.sources.append(attrs["data-src"])
        self.texts += [attrs[name] for name in ("aria-label", "placeholder", "alt", "value") if attrs.get(name)]


@dataclass
class Sheet:
    path: Path
    repo: Path
    data: dict

    def entries(self, key: str) -> list[dict]:
        value = self.data.get(key, [])
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    def files(self) -> list[str]:
        screen = self.data.get("screen")
        named = [screen.get("file", "")] if isinstance(screen, dict) else []
        named += [item.get("file", "") for item in self.entries("components")]
        extra = self.data.get("files", [])
        named += [name for name in extra if isinstance(name, str)] if isinstance(extra, list) else []
        return [name for name in dict.fromkeys(named) if name]


def _find_repo(start: Path) -> Path:
    for folder in (start, *start.parents):
        if (folder / ".git").exists():
            return folder
    return start


def load_sheet(path: Path) -> tuple[Sheet | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return None, [f"the screen source file {path} cannot be read."]
    except json.JSONDecodeError as error:
        return None, [f"the screen source file is not valid JSON ({error.msg}, line {error.lineno})."]
    if not isinstance(data, dict):
        return None, ["the screen source file must hold one JSON object."]
    folder = path.resolve().parent
    repo = (folder / data["repo"]).resolve() if isinstance(data.get("repo"), str) else _find_repo(folder)
    return Sheet(path, repo, data), []


def check_sheet(sheet: Sheet) -> list[str]:
    """The sheet must be true to the code: files exist, evidence is found."""
    problems: list[str] = []
    screen = sheet.data.get("screen")
    if not isinstance(screen, dict) or not screen.get("name") or not screen.get("file"):
        problems.append('the screen source needs "screen" with a "name" and a "file".')

    corpus = ""
    for name in sheet.files():
        target = (sheet.repo / name).resolve()
        if not target.is_relative_to(sheet.repo) or not target.is_file():
            problems.append(f'"{name}" is not a file in the project. List only real files.')
            continue
        corpus += target.read_text(encoding="utf-8", errors="replace") + "\n"

    for key, label in (("colors", "value"), ("fonts", "value"), ("features", "label")):
        entries = sheet.entries(key)
        if not entries:
            problems.append(f'the screen source needs at least one entry in "{key}".')
        for entry in entries:
            name = str(entry.get(label, "")).strip()
            evidence = str(entry.get("evidence", "")).strip()
            if not name:
                problems.append(f'an entry in "{key}" has no "{label}".')
            elif len(evidence) < MIN_EVIDENCE_CHARS:
                problems.append(f'{key}: "{name}" needs "evidence", the text in the code that proves it.')
            elif evidence not in corpus:
                problems.append(
                    f'{key}: the evidence "{evidence}" for "{name}" is not in the listed files. '
                    "Read the real code again."
                )
    for entry in sheet.entries("colors"):
        if entry.get("value") and parse_color(str(entry["value"])) is None:
            problems.append(f'colors: "{entry["value"]}" is not a hex, rgb or hsl color.')
    for entry in sheet.entries("components"):
        if not entry.get("name") or not entry.get("file"):
            problems.append('every entry in "components" needs a "name" and a "file".')
    return problems


def _plain(text: str) -> str:
    return " ".join(text.lower().split())


def check_design(sheet: Sheet, design: Design, must_keep_features: bool) -> list[str]:
    """The drawing must use only what the sheet lists."""
    problems: list[str] = []
    allowed = {color.rgb for entry in sheet.entries("colors") if (color := parse_color(str(entry.get("value", ""))))}
    strange = sorted(
        {
            color.rgb
            for color in design.colors
            if color.rgb not in allowed and not (color.see_through and color.rgb in ("#000000", "#ffffff"))
        }
    )
    if strange:
        problems.append(
            f"the design uses colors the project does not have: {', '.join(strange[:6])}. "
            "Use the colors from the screen source."
        )

    fonts = {str(entry.get("value", "")).lower() for entry in sheet.entries("fonts")}
    wrong_fonts = sorted({font for font in design.fonts if font.lower() not in fonts})
    if wrong_fonts:
        problems.append(f"the design uses fonts the project does not have: {', '.join(wrong_fonts)}.")

    components = {str(entry.get("file", "")) for entry in sheet.entries("components")}
    unknown = sorted({source for source in design.sources if source not in components})
    if unknown:
        problems.append(f'data-src names files that are not in "components": {", ".join(unknown[:6])}.')
    if components and not design.sources:
        problems.append(
            "no drawn part says which real component it is. Put data-src=\"<component file>\" on each one."
        )

    if must_keep_features:
        seen = _plain(" ".join(design.texts))
        missing = [
            str(entry.get("label", ""))
            for entry in sheet.entries("features")
            if _plain(str(entry.get("label", ""))) not in seen
        ]
        if missing:
            problems.append(
                f"the real screen has these, and the drawing does not: {', '.join(missing[:8])}. "
                "Draw the screen as it is."
            )
    return problems
