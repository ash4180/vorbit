from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "concept"
SCRIPT = SKILL / "scripts" / "check_frames.py"
EXAMPLE = SKILL / "examples" / "frame.dc.html"
MOTION_EXAMPLE = SKILL / "examples" / "frame-motion.dc.html"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_frames", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_frames"] = module
    spec.loader.exec_module(module)
    return module


check_frames = _load()

SCREEN = "".join(f'<div class="row"><span>Task {n}</span></div>' for n in range(5))


def tile(title: str = "Open task", line: str = "An empty box.", picture: str = "<i></i>") -> str:
    return (
        f'<div data-cf="tile"><div data-cf="tile-picture">{picture}</div>'
        f'<div data-cf="tile-title">{title}</div><div data-cf="tile-line">{line}</div></div>'
    )


def frame(
    kind: str = "today",
    chip: str = "Today",
    title: str = "The task list now",
    subtitle: str = "One long list.",
    drawing: str = SCREEN,
    tiles: str = "",
    extra: str = "",
    drawing_attrs: str = ' data-cf-motion="none"',
    size: str = "width: 1280px; height: 760px",
    head: str = "",
    source: str = ' data-cf-source="none"',
    badge: str | None = None,
    script: str = "class Component extends DCLogic { renderVals() { return { toggle: 0, showStep: 0 }; } }",
) -> str:
    if badge is None:
        badge = BADGE if "loop" in drawing_attrs else ""
    return (
        f"<html><head><title>Ignored words in the page title</title>{head}</head><body>"
        f'<div data-cf="frame" data-cf-kind="{kind}"{source} style="{size}; padding: 40px">'
        f'<div data-cf="chip">{chip}</div><div data-cf="title">{title}</div>'
        f'<div data-cf="subtitle">{subtitle}</div>{badge}'
        f'<div data-cf="drawing"{drawing_attrs}>{drawing}</div>{tiles}{extra}</div>'
        f"<script>{script}</script></body></html>"
    )


@pytest.mark.parametrize("example", [EXAMPLE, MOTION_EXAMPLE], ids=["still", "loop"])
def test_example_frames_pass(example: Path):
    assert check_frames.check_frame(example.read_text()) == []


def test_minimal_frame_passes():
    assert check_frames.check_frame(frame()) == []


@pytest.mark.parametrize(
    "source",
    [
        frame(drawing=SCREEN + "<p>Payments are slow for some users right now, since 9:06 this morning.</p>"),
        frame(drawing='<img src="/_blob/abc">'),
        frame(tiles=tile() * 4),
        frame(kind="idea", chip="A"),
        frame(kind="result", chip=""),
    ],
    ids=["one-real-sentence-in-the-design", "picture-only", "four-tiles", "idea", "result-no-chip"],
)
def test_frames_that_look_risky_but_are_fine(source: str):
    assert check_frames.check_frame(source) == []


LOOP = ' data-cf-motion="loop"'
LOOP_STYLE = (
    "<style>@keyframes slide{to{opacity:1}} .row{animation: slide 8s linear infinite}"
    "@media (prefers-reduced-motion: reduce){*{animation:none}}</style>"
)
STEP = '<div data-cf="step">1 · A task waits in the list</div>'
BADGE = '<button data-cf="loop-badge" onClick="{{ toggle }}">Stop the loop</button>'
STEPS = STEP * 2


def card(at: str | None = "1", tag: str = "button", click: str = ' onClick="{{ showStep }}"') -> str:
    time = "" if at is None else f' data-cf-at="{at}"'
    return (
        f'<{tag} data-cf="tile"{time}{click}><span data-cf="tile-picture"><i></i></span>'
        f'<span data-cf="tile-title">Open task</span><span data-cf="tile-line">An empty box.</span></{tag}>'
    )


CARDS = card("1") + card("3")


def loop(drawing: str = SCREEN + STEPS, tiles: str = CARDS, head: str = LOOP_STYLE, **changes: str) -> str:
    return frame(drawing_attrs=LOOP, drawing=drawing, tiles=tiles, head=head, **changes)

SENTENCE = "<p>This option moves the done tasks into a second list below.</p>"

BAD = {
    "memo-of-sentences": (frame(drawing=SCREEN + SENTENCE * 5), "memo"),
    "paragraph": (frame(drawing=SCREEN + "<p>" + "word " * 26 + "</p>"), "paragraph"),
    "empty-drawing": (frame(drawing="<div></div>"), "almost empty"),
    "five-tiles": (frame(tiles=tile() * 5), "5 tiles"),
    "long-title": (frame(title="one two three four five six seven eight nine"), "title has 9"),
    "no-subtitle": (frame(subtitle=""), "subtitle has 0"),
    "tile-title-one-word": (frame(tiles=tile(title="Open")), "tile 1 title"),
    "tile-without-picture": (frame(tiles=tile(picture="")), "tile 1 has no picture"),
    "words-outside-slots": (frame(extra="<p>Why I like this option best.</p>"), "outside every slot"),
    "chip-on-the-design": (frame(drawing=SCREEN + '<span data-cf="chip">New</span>'), "inside a drawing"),
    "today-with-wrong-chip": (frame(chip="Now"), 'needs the chip "Today"'),
    "pick-with-wrong-chip": (frame(kind="pick", chip="Recommended"), 'needs the chip "My pick"'),
    "unknown-kind": (frame(kind="option"), "data-cf-kind"),
    "wrong-size": (frame(size="width: 1280px; height: 620px"), "1280 x 760"),
    "too-many-own-words": (
        frame(subtitle="word " * 16, tiles=tile(line="word " * 14) * 4),
        "of your own words",
    ),
    "motion-not-declared": (frame(drawing_attrs=""), "must loop"),
    "motion-unknown-word": (frame(drawing_attrs=' data-cf-motion="yes"'), "must loop"),
    "loop-without-animation": (loop(head=""), "demo that loops"),
    "loop-without-reduced-motion": (
        loop(head="<style>@keyframes a{to{opacity:1}} i{animation:a 8s infinite}</style>"),
        "prefers-reduced-motion",
    ),
    "loop-without-steps": (loop(drawing=SCREEN), "0 step captions"),
    "loop-without-badge": (loop(badge=""), "loop badge"),
    "loop-badge-on-the-design": (loop(drawing=SCREEN + STEPS + BADGE, badge=""), "sits on the design"),
    "loop-badge-on-a-still-frame": (frame(badge=BADGE), 'need data-cf-motion="loop"'),
    "loop-step-too-long": (
        loop(drawing=SCREEN + STEPS + '<div data-cf="step">' + "word " * 9 + "</div>", tiles=CARDS + card("5")),
        "step 3 has 9 words",
    ),
    "loop-with-five-steps": (loop(drawing=SCREEN + STEP * 5, tiles=CARDS + card("5") + card("6")), "5 step captions"),
    "loop-step-without-a-card": (loop(drawing=SCREEN + STEP * 3), "3 steps and 2 cards"),
    "loop-without-cards": (loop(tiles=""), "2 steps and 0 cards"),
    "loop-card-is-not-a-button": (loop(tiles=card("1") + card("3", tag="div")), "card 2 must be a <button>"),
    "loop-card-without-a-handler": (loop(tiles=card("1", click="") + card("3")), "card 1 must be a <button>"),
    "loop-card-without-a-time": (loop(tiles=card("1") + card(None)), "card 2 needs data-cf-at"),
    "loop-card-time-is-a-word": (loop(tiles=card("1") + card("soon")), "card 2 needs data-cf-at"),
    "loop-card-times-go-down": (loop(tiles=card("3") + card("1")), "must go up"),
    "loop-card-times-repeat": (loop(tiles=card("3") + card("3")), "must go up"),
    "loop-badge-is-not-a-button": (loop(badge='<div data-cf="loop-badge">Live demo, it loops</div>'), "badge must be a <button>"),
    "loop-badge-without-a-handler": (loop(badge='<button data-cf="loop-badge">Stop the loop</button>'), "badge must be a <button>"),
    "loop-handler-not-in-script": (loop(script="class Component extends DCLogic { renderVals() { return { toggle: 0 }; } }"), '"showStep" is not in the script'),
    "loop-without-logic-class": (loop(script="const toggle = 0, showStep = 0;"), "class Component extends DCLogic"),
    "card-time-on-a-still-frame": (frame(tiles=card("1")), 'needs data-cf-motion="loop"'),
    "steps-on-a-still-frame": (frame(drawing=SCREEN + STEPS), 'need data-cf-motion="loop"'),
    "step-outside-the-drawing": (frame(extra=STEP), "sits outside the drawing"),
    "extra-closing-tag": (frame(drawing=SCREEN + "</div>"), "The layout will break"),
    "unclosed-tag": (frame(drawing=SCREEN + "<div><span>Open</span>"), "The layout will break"),
    "source-not-declared": (frame(source=""), "data-cf-source"),
    "hole-with-an-expression": (frame(drawing=SCREEN + "<b>{{ count + 1 }}</b>"), "not a plain name"),
    "no-frame-root": ("<div><p>Just a note about the idea.</p></div>", "exactly one"),
}


@pytest.mark.parametrize("case", BAD, ids=list(BAD))
def test_bad_frames_are_refused(case: str):
    source, expected = BAD[case]
    problems = check_frames.check_frame(source)
    assert any(expected in problem for problem in problems), problems


def test_loop_frame_with_steps_and_badge_passes():
    assert check_frames.check_frame(loop()) == []


def test_loop_card_times_may_be_parts_of_a_second():
    assert check_frames.check_frame(loop(tiles=card("0") + card("2.5"))) == []


def test_step_captions_do_not_count_as_a_memo_or_own_words():
    long_steps = '<div data-cf="step">one two three four five six seven eight</div>' * 4
    source = loop(drawing=SCREEN + long_steps, tiles=CARDS + card("5") + card("7"))
    assert check_frames.check_frame(source) == []


def test_still_row_gets_a_note_about_motion(tmp_path: Path):
    result = _run(tmp_path, frame())
    assert result.returncode == 0
    assert "NOTE no frame loops" in result.stdout


def _run(tmp_path: Path, *sources: str) -> subprocess.CompletedProcess[str]:
    paths = []
    for index, source in enumerate(sources):
        path = tmp_path / f"{index}.dc.html"
        path.write_text(source)
        paths.append(str(path))
    return subprocess.run([sys.executable, str(SCRIPT), *paths], capture_output=True, text=True)


def test_row_of_ideas_must_start_with_today(tmp_path: Path):
    result = _run(tmp_path, frame(kind="idea", chip="A"), frame(kind="pick", chip="My pick"))
    assert result.returncode == 1
    assert 'starts with a "today" frame' in result.stdout


def test_good_row_exits_zero(tmp_path: Path):
    result = _run(tmp_path, frame(), frame(kind="idea", chip="A"), frame(kind="pick", chip="My pick"))
    assert result.returncode == 0, result.stdout
    assert result.stdout.startswith("OK 3 frame(s), 0 with a looping demo, 0 prototype(s)")


def test_result_row_needs_no_today_frame(tmp_path: Path):
    assert _run(tmp_path, frame(kind="result", chip="Step 1")).returncode == 0


def test_missing_file_fails(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "none.dc.html")], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "cannot read the file" in result.stdout


# ---- screen source: the drawing must match the real project ----

REAL_SCREEN = (
    '<div data-src="src/Button.tsx" style="background: #112233; font-family: Inter, sans-serif">'
    "<span>New task</span><span>Projects</span></div>"
    + "".join(f'<div style="color: rgb(17, 34, 51)"><span>Task {n}</span></div>' for n in range(4))
)


def _project(tmp_path: Path, **changes: object) -> str:
    """A tiny project plus its screen source file. Returns the frame's source attribute."""
    (tmp_path / ".git").mkdir(exist_ok=True)
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "Tasks.tsx").write_text('<Button>New task</Button><Nav label="Projects" />')
    (src / "Button.tsx").write_text('export const Button = () => <button className="bg-brand" />')
    (src / "theme.css").write_text(":root { --brand: #112233; font-family: Inter; }")
    sheet: dict[str, object] = {
        "screen": {"name": "Tasks", "file": "src/Tasks.tsx"},
        "components": [{"name": "Button", "file": "src/Button.tsx"}],
        "files": ["src/theme.css"],
        "colors": [{"value": "#112233", "evidence": "--brand: #112233"}],
        "fonts": [{"value": "Inter", "evidence": "font-family: Inter"}],
        "features": [
            {"label": "New task", "evidence": "New task"},
            {"label": "Projects", "evidence": 'label="Projects"'},
        ],
    }
    sheet.update(changes)
    (tmp_path / "screen-source.json").write_text(json.dumps(sheet))
    return ' data-cf-source="screen-source.json"'


def test_drawing_that_matches_the_project_passes(tmp_path: Path):
    source = frame(drawing=REAL_SCREEN, source=_project(tmp_path))
    assert check_frames.check_frame(source, tmp_path) == []


def test_see_through_black_and_white_are_always_allowed(tmp_path: Path):
    shadow = '<div style="box-shadow: 0 2px 8px rgba(0,0,0,0.4); border: 1px solid #ffffff22"></div>'
    source = frame(drawing=REAL_SCREEN + shadow, source=_project(tmp_path))
    assert check_frames.check_frame(source, tmp_path) == []


def test_idea_frame_may_drop_a_feature(tmp_path: Path):
    drawing = REAL_SCREEN.replace("<span>Projects</span>", "")
    source = frame(kind="idea", chip="A", drawing=drawing, source=_project(tmp_path))
    assert check_frames.check_frame(source, tmp_path) == []


SOURCE_BAD = {
    "color-not-in-project": (REAL_SCREEN + '<i style="color: #ff0000"></i>', {}, "colors the project does not have: #ff0000"),
    "svg-fill-not-in-project": (REAL_SCREEN + '<svg><path fill="#00ff00"></path></svg>', {}, "#00ff00"),
    "font-not-in-project": (REAL_SCREEN + '<i style="font-family: Roboto, sans-serif"></i>', {}, "fonts the project does not have: Roboto"),
    "today-drops-a-feature": (REAL_SCREEN.replace("<span>Projects</span>", ""), {}, "the drawing does not: Projects"),
    "no-part-names-its-component": (REAL_SCREEN.replace(' data-src="src/Button.tsx"', ""), {}, "which real component"),
    "data-src-outside-the-list": (REAL_SCREEN + '<i data-src="src/Card.tsx"></i>', {}, "not in \"components\": src/Card.tsx"),
    "invented-component-file": (
        REAL_SCREEN,
        {"components": [{"name": "Button", "file": "src/Button.tsx"}, {"name": "Card", "file": "src/Card.tsx"}]},
        '"src/Card.tsx" is not a file in the project',
    ),
    "file-outside-the-project": (REAL_SCREEN, {"files": ["../secret.txt"]}, "is not a file in the project"),
    "invented-color-evidence": (
        REAL_SCREEN,
        {"colors": [{"value": "#112233", "evidence": "--primary: #112233"}]},
        'evidence "--primary: #112233"',
    ),
    "feature-without-evidence": (
        REAL_SCREEN,
        {"features": [{"label": "New task", "evidence": "New task"}, {"label": "Projects"}]},
        '"Projects" needs "evidence"',
    ),
    "invented-feature": (
        REAL_SCREEN + "<span>Export</span>",
        {"features": [{"label": "New task", "evidence": "New task"}, {"label": "Projects", "evidence": "Projects"}, {"label": "Export", "evidence": "Export CSV"}]},
        'evidence "Export CSV"',
    ),
    "no-features-listed": (REAL_SCREEN, {"features": []}, 'at least one entry in "features"'),
}


@pytest.mark.parametrize("case", SOURCE_BAD, ids=list(SOURCE_BAD))
def test_drawing_that_does_not_match_the_project_is_refused(case: str, tmp_path: Path):
    drawing, changes, expected = SOURCE_BAD[case]
    source = frame(drawing=drawing, source=_project(tmp_path, **changes))
    problems = check_frames.check_frame(source, tmp_path)
    assert any(expected in problem for problem in problems), problems


def test_missing_screen_source_file_is_refused(tmp_path: Path):
    problems = check_frames.check_frame(frame(source=' data-cf-source="nowhere.json"'), tmp_path)
    assert any("cannot be read" in problem for problem in problems), problems


# ---- canvas prototypes ----

PROTOTYPE_EXAMPLE = SKILL / "examples" / "prototype.dc.html"
SCRIPT_OK = "<script>class Component extends DCLogic { renderVals() { return { add: () => {}, open: [] }; } }</script>"


def prototype(body: str = '<button onClick="{{ add }}">New task</button>', script: str = SCRIPT_OK) -> str:
    return f'<div data-cf="prototype" data-cf-source="none">{body}</div>{script}'


def test_prototype_example_passes():
    assert check_frames.check_frame(PROTOTYPE_EXAMPLE.read_text()) == []


@pytest.mark.parametrize(
    "body",
    [
        '<button onClick="{{ add }}">New task</button>',
        '<a href="Cart.dc.html">View cart</a>',
        '<button onClick="{{ add }}">Add</button><button data-cf-idle>Team</button><button disabled>Save</button>',
        '<sc-for list="{{ open }}" as="t" hint-placeholder-count="2"><button onClick="{{ t.add }}">{{ t.title }}</button></sc-for>',
    ],
    ids=["handler", "artboard-link", "idle-and-disabled", "list-handlers"],
)
def test_working_prototypes_pass(body: str):
    assert check_frames.check_frame(prototype(body)) == []


PROTOTYPE_BAD = {
    "nothing-reacts": (prototype("<p>Tasks</p>"), "nothing reacts"),
    "dead-button": (prototype('<button onClick="{{ add }}">Add</button><button>Export</button>'), 'button "Export" does nothing'),
    "dead-link": (prototype('<button onClick="{{ add }}">Add</button><a>Help</a>'), 'a "Help" does nothing'),
    "handler-not-in-script": (prototype('<button onClick="{{ remove }}">Delete</button>'), '"remove" is not in the script'),
    "button-inside-link": (prototype('<a href="Next.dc.html"><button>Next</button></a>'), "swallows the click"),
    "no-logic-class": (prototype(script="<script>const x = 1;</script>"), "class Component extends DCLogic"),
    "expression-in-hole": (prototype('<button onClick="{{ add }}">{{ open.length + 1 }}</button>'), "not a plain name"),
    "sc-for-without-hint": (prototype('<button onClick="{{ add }}">Add</button><sc-for list="{{ open }}" as="t"><i></i></sc-for>'), "hint-placeholder-count"),
    "frame-parts-in-a-prototype": (prototype('<button onClick="{{ add }}">Add</button><div data-cf="title">Tasks</div>'), "the screen alone"),
    "source-not-declared": ('<div data-cf="prototype"><button onClick="{{ add }}">Add</button></div>' + SCRIPT_OK, "data-cf-source"),
}


@pytest.mark.parametrize("case", PROTOTYPE_BAD, ids=list(PROTOTYPE_BAD))
def test_broken_prototypes_are_refused(case: str):
    source, expected = PROTOTYPE_BAD[case]
    problems = check_frames.check_frame(source)
    assert any(expected in problem for problem in problems), problems


def test_prototype_must_match_the_project_too(tmp_path: Path):
    attr = _project(tmp_path)
    body = '<button data-src="src/Button.tsx" onClick="{{ add }}" style="background: #ff0000">New task</button>'
    source = f'<div data-cf="prototype"{attr}>{body}</div>{SCRIPT_OK}'
    problems = check_frames.check_frame(source, tmp_path)
    assert any("#ff0000" in problem for problem in problems), problems


def test_prototype_alone_needs_no_today_frame(tmp_path: Path):
    result = _run(tmp_path, prototype())
    assert result.returncode == 0, result.stdout
    assert "1 prototype(s)" in result.stdout
