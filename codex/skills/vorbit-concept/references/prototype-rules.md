# Canvas Prototype Rules

A canvas prototype is a screen the user can really click, on a Claude canvas. It is for trying an idea and for presenting it. It is never app code, and it changes no file in the project.

## The file

Start from `examples/prototype.dc.html`. A prototype is the screen alone: no chip, no title, no tiles.

- The root has `data-cf="prototype"` and `data-cf-source` (see `screen-source.md`).
- The canvas entry of the artboard has `"is_interactive": true`. The canvas then shows a Play button.
- A web or desktop screen is a page: a fluid root with no fixed width, and `"expand": "fill"` on its canvas entry. A phone screen is 390 by 844 px.

## What must work

- Every step of the flow you were asked to show works with real clicks, from the first screen to the end result.
- The data on screen changes: a new item appears, a checked item moves, a count goes up. Keep the data in `state`.
- Every button and link reacts. A control outside the flow gets `data-cf-idle`, so the choice is on purpose.
- Empty, loading and error states are shown when the flow reaches them.

## How to build it

- One flow that shares data is one artboard: handlers set `state`, and each screen sits in its own `<sc-if>`.
- Screens that share no data can be separate artboards, joined by links: `<a href="Next.dc.html">`. Style the link as the button. Never put a `<button>` inside a link.
- Events are whole attributes: `onClick="{{ addTask }}"`. The name must be returned from `renderVals()`.
- A `{{ }}` hole holds a plain name only, such as `{{ task.title }}`. Work out every value in `renderVals()`.
- Each item in a list carries its own handler: `onClick="{{ task.toggle }}"` inside `<sc-for>`.
- `<sc-if>` needs `hint-placeholder-val`. `<sc-for>` needs `hint-placeholder-count`.
- Sample data is real-looking and short. No "Lorem ipsum", no invented numbers that look like facts.

## The check

`python3 scripts/check_frames.py <prototype file> [...]`

It refuses a prototype where nothing reacts, a button does nothing, a handler is missing from the script, or the design does not match the screen source. It cannot click. Open the canvas, press Play, and walk the flow yourself before you say it works.
