#!/usr/bin/env python3
"""Check concept frames and canvas prototypes before they are published.

Use: check_frames.py <file> [<file> ...]

Give the files of one row in reading order. Prints one line per problem and
exits 1 when any file breaks a rule. The rules are in references/frame-rules.md,
references/prototype-rules.md and references/screen-source.md.
Standard library only, so the scripts folder can be copied.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from screen_source import Design, check_design, check_sheet, load_sheet  # noqa: E402

FRAME_WIDTH = 1280
FRAME_HEIGHT = 760
ROOTS = ("frame", "prototype")
KINDS = ("today", "idea", "pick", "result")
FIXED_CHIP = {"today": "Today", "pick": "My pick"}
SLOTS = (
    "chip",
    "title",
    "subtitle",
    "drawing",
    "tile",
    "tile-picture",
    "tile-title",
    "tile-line",
    "step",
    "loop-badge",
)
TEXT_SLOTS = ("chip", "title", "subtitle", "tile-title", "tile-line")
PICTURE_SLOTS = ("drawing", "tile-picture")
DEMO_SLOTS = ("step", "loop-badge")
MOTIONS = ("loop", "none")
NO_SOURCE = "none"

MAX_CHIP_WORDS = 3
MAX_TITLE_WORDS = 8
MAX_SUBTITLE_WORDS = 16
MAX_TILES = 4
TILE_TITLE_WORDS = (2, 4)
MAX_TILE_LINE_WORDS = 14
MAX_OWN_WORDS = 60
MIN_DRAWING_ELEMENTS = 8
MAX_DRAWING_TEXT_WORDS = 25
SENTENCE_WORDS = 9
MAX_DRAWING_SENTENCES = 4
STEP_COUNT = (2, 4)
MAX_STEP_WORDS = 8

VOID_TAGS = frozenset(
    "area base br col embed hr img input link meta source track wbr".split()
)
SILENT_TAGS = frozenset(("script", "style", "head", "title"))
PICTURE_TAGS = frozenset(("img", "svg", "canvas", "video"))
HOLE = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
PLAIN_HOLE = re.compile(r"\s*[\w$]+(?:\.[\w$]+)*\s*")
ARTBOARD_LINK = re.compile(r"\.dc\.html(?:[#?].*)?$")


def count_words(text: str) -> int:
    return sum(1 for token in text.split() if re.search(r"\w", token))


def _events(values: dict[str, str]) -> list[str]:
    return [value for name, value in values.items() if name.startswith("on") and HOLE.search(value)]


@dataclass
class Tile:
    tag: str = ""
    at: str | None = None
    reacts: bool = False
    picture_elements: int = 0
    has_picture: bool = False
    title: str = ""
    line: str = ""


@dataclass
class Control:
    tag: str
    reacts: bool
    idle: bool
    label: str = ""


@dataclass
class Frame:
    roots: list[str] = field(default_factory=list)
    kind: str = ""
    style: str = ""
    source: str | None = None
    text: dict[str, list[str]] = field(default_factory=lambda: {s: [] for s in TEXT_SLOTS})
    drawings: int = 0
    drawing_elements: int = 0
    drawing_has_picture: bool = False
    drawing_motion: str = ""
    drawing_texts: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    loop_badges: int = 0
    badge_buttons: int = 0
    demo_slots_misplaced: int = 0
    badges_on_design: int = 0
    tiles: list[Tile] = field(default_factory=list)
    stray_words: int = 0
    marks_on_design: int = 0
    unknown_slots: list[str] = field(default_factory=list)
    slots_used: int = 0
    broken_tags: int = 0
    design: Design = field(default_factory=Design)
    controls: list[Control] = field(default_factory=list)
    handlers: list[str] = field(default_factory=list)
    artboard_links: int = 0
    buttons_in_links: int = 0
    bad_holes: list[str] = field(default_factory=list)
    hintless: list[str] = field(default_factory=list)
    script: str = ""

    @property
    def root(self) -> str:
        return self.roots[0] if len(self.roots) == 1 else ""


class FrameReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.frame = Frame()
        self.stack: list[tuple[str, str]] = []

    def _inside(self, *slots: str) -> bool:
        return any(slot in slots for _, slot in self.stack)

    def _in_tag(self, *tags: str) -> bool:
        return any(tag in tags for tag, _ in self.stack)

    def _on_design(self) -> bool:
        if self._inside(*DEMO_SLOTS):
            return False
        return self._inside("prototype", *PICTURE_SLOTS)

    def _note_holes(self, text: str) -> None:
        for hole in HOLE.findall(text):
            if not PLAIN_HOLE.fullmatch(hole):
                self.frame.bad_holes.append(hole.strip())

    def _open(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        values = {name: value or "" for name, value in attrs}
        slot = values.get("data-cf", "")
        frame = self.frame
        on_design = self._inside(*PICTURE_SLOTS)

        if self._inside("drawing"):
            frame.drawing_elements += 1
            frame.drawing_has_picture |= tag in PICTURE_TAGS
        if self._inside("tile-picture") and frame.tiles:
            frame.tiles[-1].picture_elements += 1
        for value in values.values():
            self._note_holes(value)
        frame.slots_used += slot in SLOTS

        if slot in ROOTS:
            frame.roots.append(slot)
            frame.kind = values.get("data-cf-kind", "")
            frame.style = values.get("style", "")
            frame.source = values.get("data-cf-source")
        elif slot and slot not in SLOTS:
            frame.unknown_slots.append(slot)
        elif slot == "step":
            if self._inside("drawing") and not self._inside("tile-picture", *DEMO_SLOTS):
                frame.steps.append("")
            else:
                frame.demo_slots_misplaced += 1
        elif slot == "loop-badge":
            if on_design or self._inside("tile", *DEMO_SLOTS):
                frame.badges_on_design += 1
            else:
                frame.loop_badges += 1
                frame.badge_buttons += tag == "button" and bool(_events(values))
        elif slot and on_design:
            frame.marks_on_design += 1
        elif slot == "drawing":
            frame.drawings += 1
            frame.drawing_motion = values.get("data-cf-motion", "")
        elif slot == "tile":
            frame.tiles.append(Tile(tag, values.get("data-cf-at"), bool(_events(values))))
        elif slot == "tile-picture" and frame.tiles:
            frame.tiles[-1].has_picture = True

        if slot == "prototype" or (slot not in SLOTS and self._on_design()):
            frame.design.add_element(values)
        self._note_control(tag, values)
        if push:
            self.stack.append((tag, slot))

    def _note_control(self, tag: str, values: dict[str, str]) -> None:
        frame = self.frame
        events = _events(values)
        frame.handlers += [hole.strip() for value in events for hole in HOLE.findall(value)]
        href = values.get("href", "")
        if tag == "a" and ARTBOARD_LINK.search(href):
            frame.artboard_links += 1
        if tag == "button" and self._in_tag("a"):
            frame.buttons_in_links += 1
        if tag in ("button", "a"):
            reacts = bool(events) or (tag == "a" and bool(href)) or self._in_tag("a")
            idle = "disabled" in values or "data-cf-idle" in values
            frame.controls.append(Control(tag, reacts, idle, values.get("aria-label", "")))
        if tag == "sc-if" and "hint-placeholder-val" not in values:
            frame.hintless.append("sc-if needs hint-placeholder-val")
        if tag == "sc-for" and "hint-placeholder-count" not in values:
            frame.hintless.append("sc-for needs hint-placeholder-count")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, push=tag not in VOID_TAGS)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, push=False)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.frame.broken_tags += len(self.stack) - 1 - index
                del self.stack[index:]
                return
        if tag not in VOID_TAGS:
            self.frame.broken_tags += 1

    def handle_data(self, data: str) -> None:
        frame = self.frame
        if self._in_tag("script"):
            frame.script += data
            return
        if not data.strip() or self._in_tag(*SILENT_TAGS):
            return
        self._note_holes(data)
        if self._in_tag("button", "a") and frame.controls and not frame.controls[-1].label:
            frame.controls[-1].label = " ".join(data.split())
        if self._inside(*DEMO_SLOTS):
            if self._inside("step") and frame.steps:
                frame.steps[-1] += " " + data
            return
        if self._on_design():
            frame.design.texts.append(data)
        if self._inside("drawing"):
            frame.drawing_texts.append(data)
            return
        if self._inside("tile-picture", "prototype"):
            return
        for _, slot in reversed(self.stack):
            if slot in ("tile-title", "tile-line") and frame.tiles:
                tile = frame.tiles[-1]
                if slot == "tile-title":
                    tile.title += " " + data
                else:
                    tile.line += " " + data
                frame.text[slot].append(data)
                return
            if slot in TEXT_SLOTS:
                frame.text[slot].append(data)
                return
        frame.stray_words += count_words(data)


def _style_px(style: str, name: str) -> int | None:
    match = re.search(rf"(?:^|;)\s*{name}\s*:\s*(\d+)px", style)
    return int(match.group(1)) if match else None


def read_frame(source: str) -> Frame:
    reader = FrameReader()
    reader.feed(source)
    reader.close()
    reader.frame.broken_tags += len(reader.stack)
    return reader.frame


def _check_source(frame: Frame, folder: Path | None, must_keep_features: bool) -> list[str]:
    if frame.source is None or not frame.source.strip():
        return [
            "the root must say data-cf-source: the path of the screen source file, "
            f'or "{NO_SOURCE}" for a fresh idea with no code yet.'
        ]
    if frame.source == NO_SOURCE:
        return []
    sheet, problems = load_sheet((folder or Path.cwd()) / frame.source)
    if sheet is None:
        return problems
    return check_sheet(sheet) + check_design(sheet, frame.design, must_keep_features)


def _check_motion(frame: Frame, lowered: str) -> list[str]:
    if frame.drawing_motion not in MOTIONS:
        return [
            'the drawing must say data-cf-motion="loop" or data-cf-motion="none". '
            "A flow, an interaction or a change of state must loop."
        ]
    if frame.drawing_motion == "none":
        if frame.steps or frame.loop_badges:
            return ['step captions and the loop badge need data-cf-motion="loop".']
        if any(tile.at is not None for tile in frame.tiles):
            return ['a card with data-cf-at needs data-cf-motion="loop". A still frame has no steps to show.']
        return []
    problems: list[str] = []
    if "@keyframes" not in lowered or "infinite" not in lowered:
        problems.append("a loop drawing needs a demo that loops (@keyframes, and animation ... infinite).")
    if "prefers-reduced-motion" not in lowered:
        problems.append("a loop drawing needs a prefers-reduced-motion rule that stops the motion.")
    low, high = STEP_COUNT
    if not low <= len(frame.steps) <= high:
        problems.append(f"a loop drawing has {len(frame.steps)} step captions. It needs {low} to {high}.")
    for number, step in enumerate(frame.steps, start=1):
        if not 1 <= count_words(step) <= MAX_STEP_WORDS:
            problems.append(f"step {number} has {count_words(step)} words. It needs 1 to {MAX_STEP_WORDS}.")
    if frame.loop_badges != 1:
        problems.append("a loop frame needs exactly one loop badge at its top right, so the viewer knows it moves.")
    elif not frame.badge_buttons:
        problems.append(
            "the loop badge must be a <button> with a handler, so the viewer can stop and play the loop."
        )
    return problems + _check_step_cards(frame)


def _check_step_cards(frame: Frame) -> list[str]:
    if len(frame.tiles) != len(frame.steps):
        return [
            f"a loop frame has {len(frame.steps)} steps and {len(frame.tiles)} cards. "
            "Each step needs its own card, in the same order."
        ]
    problems: list[str] = []
    times: list[float] = []
    for number, tile in enumerate(frame.tiles, start=1):
        if tile.tag != "button" or not tile.reacts:
            problems.append(
                f"card {number} must be a <button> with a handler, so a click shows step {number}."
            )
        try:
            times.append(float(tile.at or ""))
        except ValueError:
            problems.append(
                f"card {number} needs data-cf-at: the second of the loop where step {number} holds still."
            )
    if not problems and (times[0] < 0 or any(late <= early for early, late in zip(times, times[1:]))):
        problems.append("the data-cf-at times of the cards must go up, from the first step to the last.")
    return problems + _check_handlers(frame)


def _check_handlers(frame: Frame) -> list[str]:
    problems: list[str] = []
    if "class Component extends DCLogic" not in frame.script:
        problems.append("the script must hold `class Component extends DCLogic`.")
    for handler in dict.fromkeys(frame.handlers):
        name = handler.split(".")[-1]
        if not re.search(rf"\b{re.escape(name)}\b", frame.script):
            problems.append(f'the handler "{handler}" is not in the script. The click would do nothing.')
    return problems


def _check_concept(frame: Frame, source: str) -> list[str]:
    problems: list[str] = []
    if frame.kind not in KINDS:
        problems.append(f'data-cf-kind must be one of {", ".join(KINDS)}, found "{frame.kind}".')
    size = (_style_px(frame.style, "width"), _style_px(frame.style, "height"))
    if size != (FRAME_WIDTH, FRAME_HEIGHT):
        problems.append(f"the frame must be {FRAME_WIDTH} x {FRAME_HEIGHT} px.")
    problems += [f'unknown slot data-cf="{slot}".' for slot in frame.unknown_slots]

    chip = " ".join(frame.text["chip"]).strip()
    title_words = count_words(" ".join(frame.text["title"]))
    subtitle_words = count_words(" ".join(frame.text["subtitle"]))
    fixed = FIXED_CHIP.get(frame.kind)
    if fixed and chip != fixed:
        problems.append(f'a {frame.kind} frame needs the chip "{fixed}", found "{chip}".')
    if count_words(chip) > MAX_CHIP_WORDS:
        problems.append(f"the chip has {count_words(chip)} words. The limit is {MAX_CHIP_WORDS}.")
    if not 1 <= title_words <= MAX_TITLE_WORDS:
        problems.append(f"the title has {title_words} words. It needs 1 to {MAX_TITLE_WORDS}.")
    if not 1 <= subtitle_words <= MAX_SUBTITLE_WORDS:
        problems.append(f"the subtitle has {subtitle_words} words. It needs 1 to {MAX_SUBTITLE_WORDS}.")

    if frame.drawings != 1:
        problems.append(f"needs exactly one drawing, found {frame.drawings}.")
    elif not frame.drawing_has_picture and frame.drawing_elements < MIN_DRAWING_ELEMENTS:
        problems.append(
            f"the drawing is almost empty ({frame.drawing_elements} parts). Draw the real design."
        )
    longest = max((count_words(text) for text in frame.drawing_texts), default=0)
    sentences = sum(1 for text in frame.drawing_texts if count_words(text) >= SENTENCE_WORDS)
    if longest > MAX_DRAWING_TEXT_WORDS:
        problems.append(f"the drawing holds a paragraph of {longest} words. Draw it, do not write it.")
    if sentences > MAX_DRAWING_SENTENCES:
        problems.append(f"the drawing holds {sentences} sentences. It reads as a memo, not a design.")
    if frame.marks_on_design:
        problems.append("a chip, title or tile sits inside a drawing. Your own words go around the design.")
    if frame.demo_slots_misplaced:
        problems.append("a step caption sits outside the drawing. It belongs at the bottom of a loop drawing.")
    if frame.badges_on_design:
        problems.append("the loop badge sits on the design. It belongs at the top right of the frame, in the title line.")
    if frame.drawings == 1:
        problems += _check_motion(frame, source.lower())

    if len(frame.tiles) > MAX_TILES:
        problems.append(f"{len(frame.tiles)} tiles. The limit is {MAX_TILES}.")
    low, high = TILE_TITLE_WORDS
    for number, tile in enumerate(frame.tiles, start=1):
        if not tile.has_picture or tile.picture_elements == 0:
            problems.append(f"tile {number} has no picture.")
        if not low <= count_words(tile.title) <= high:
            problems.append(f"tile {number} title has {count_words(tile.title)} words. It needs {low} to {high}.")
        if not 1 <= count_words(tile.line) <= MAX_TILE_LINE_WORDS:
            problems.append(
                f"tile {number} line has {count_words(tile.line)} words. It needs 1 to {MAX_TILE_LINE_WORDS}."
            )

    if frame.stray_words:
        problems.append(f"{frame.stray_words} words sit outside every slot. Move them into a slot or delete them.")
    own = sum(count_words(" ".join(texts)) for texts in frame.text.values())
    if own > MAX_OWN_WORDS:
        problems.append(f"{own} of your own words. The limit is {MAX_OWN_WORDS}. Cut, or draw it.")
    return problems


def _check_prototype(frame: Frame) -> list[str]:
    problems: list[str] = []
    if frame.unknown_slots or frame.slots_used:
        problems.append("a prototype is the screen alone. It has no chip, title, drawing slot or tiles.")
    if not frame.handlers and not frame.artboard_links:
        problems.append("nothing reacts to a click. A prototype needs at least one handler or artboard link.")
    problems += _check_handlers(frame)
    for control in frame.controls:
        if not control.reacts and not control.idle:
            label = control.label or "no label"
            problems.append(
                f'the {control.tag} "{label}" does nothing. Give it a handler, or mark it data-cf-idle '
                "when it is outside this flow."
            )
    if frame.buttons_in_links:
        problems.append("a button sits inside a link and swallows the click. Style the link as the button.")
    problems += [f"{hint}, or it shows nothing while loading." for hint in dict.fromkeys(frame.hintless)]
    return problems


def check_frame(source: str, folder: Path | None = None) -> list[str]:
    frame = read_frame(source)
    if not frame.root:
        return [
            f"needs exactly one data-cf root (frame or prototype), found {len(frame.roots)}. "
            "Start from an example file."
        ]
    problems = _check_concept(frame, source) if frame.root == "frame" else _check_prototype(frame)
    problems += [
        f'"{{{{ {hole} }}}}" is not a plain name. Work it out in renderVals() and use its name.'
        for hole in dict.fromkeys(frame.bad_holes)
    ]
    if frame.broken_tags:
        problems.append(
            f"{frame.broken_tags} tags are not closed, or are closed twice. The layout will break."
        )
    must_keep = frame.root == "frame" and frame.kind == "today"
    return problems + _check_source(frame, folder, must_keep)


def check_row(frames: list[Frame]) -> list[str]:
    kinds = [frame.kind for frame in frames if frame.root == "frame"]
    if any(kind in ("idea", "pick") for kind in kinds) and kinds[0] != "today":
        return ['a row of ideas starts with a "today" frame.']
    return []


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    failed = False
    frames: list[Frame] = []
    for name in argv:
        try:
            source = Path(name).read_text(encoding="utf-8")
        except OSError as error:
            print(f"FAIL {name}: cannot read the file ({error.strerror}).")
            failed = True
            continue
        problems = check_frame(source, Path(name).resolve().parent)
        frames.append(read_frame(source))
        for problem in problems:
            print(f"FAIL {name}: {problem}")
        failed |= bool(problems)
    for problem in check_row(frames):
        print(f"FAIL row: {problem}")
        failed = True
    if failed:
        return 1
    concept = [frame for frame in frames if frame.root == "frame"]
    loops = sum(frame.drawing_motion == "loop" for frame in concept)
    prototypes = len(frames) - len(concept)
    print(f"OK {len(concept)} frame(s), {loops} with a looping demo, {prototypes} prototype(s)")
    if concept and not loops:
        print("NOTE no frame loops. A flow, an interaction or a change of state needs a looping demo.")
    if any(frame.source == NO_SOURCE for frame in frames):
        print('NOTE a file says data-cf-source="none". That is right only when no code for this screen exists.')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
