# Concept Frame Rules

A concept frame shows one idea as a picture. The reader is a designer and works by looking.

## The frame

Every frame is 1280 by 760 px and has the same parts. Start from `examples/frame.dc.html` and keep its sizes, colors and font. Change only what is inside the slots.

| Slot (`data-cf`) | What goes in | Limit |
|---|---|---|
| `chip` | "Today", "My pick", or a short name such as "A" | 3 words |
| `title` | What this frame shows | 8 words |
| `subtitle` | One line that says the main point | 16 words |
| `drawing` | The design, 800 by 600 px, in its real place | exactly one |
| `tile` | One state or one detail, with a small picture. In a looping demo: one card per step | 0 to 4 tiles |
| `tile-picture` | The small picture, 150 by 112 px | never empty |
| `tile-title` | The name of the state | 2 to 4 words |
| `tile-line` | One line about it | 14 words |
| `step` | One caption per step of a looping demo | 2 to 4 captions, 8 words each |
| `loop-badge` | The Play and Stop button, at the top right of the frame | one, only in a looping demo |

Your own words on one frame (chip, title, subtitle, tile titles and tile lines): 60 at most. Words inside the drawn design and step captions do not count.

Set `data-cf-source` on the frame: the path of the screen source file, or `none` for a fresh idea with no code yet. See `screen-source.md`.

Set `data-cf-kind` on the frame:

- `today`: the real current state. The chip says "Today".
- `idea`: one idea. The chip is a letter, a number or a short name.
- `pick`: the idea you would choose. The chip says "My pick".
- `result`: anything that is not a choice, such as a finding, a reference or one step of a plan.

## The drawing

- Draw the design exactly as it would really look, in the place where the user meets it. Not a cut-out piece, not a wireframe, not a screenshot.
- Inside the drawing, the design uses the product's own layout, components, colors and type, taken from the screen source file. The frame around it stays as in the example.
- Nothing of yours goes on the design: no labels, badges, chips, callouts, arrows, numbered dots or extra outlines.
- To show the part that differs, give it a tile with a close-up. Never mark it on the design.
- Never write a paragraph, a long list or a text table in a frame. A frame full of sentences is a memo.

## Motion

Every drawing says if it moves: `data-cf-motion="loop"` or `data-cf-motion="none"`.

It must be `loop` when the idea happens over time:

- a flow of two or more steps
- an interaction: a click, a drag, a hover, typing, opening or closing
- a change of state: loading, saving, an item that appears, moves or goes away

A still picture of such an idea is wrong, even when it is drawn well. Use `none` only for an idea that is one still state, such as a layout or a visual style.

Build a `loop` drawing like `examples/frame-motion.dc.html`:

- The design itself moves. Animate the real parts with CSS `@keyframes`.
- Every animation uses the same length and `linear infinite`, so all parts stay in step. 6 to 12 seconds for one loop.
- Each step holds still long enough to read, then moves. The loop ends where it starts.
- One `step` caption per step, as a pill at the bottom of the drawing. Start each with its number: "2 · You check it". Each caption shows only during its step.
- One `loop-badge` at the top right of the frame, at the end of the title line. Never inside the drawing. It is a `<button>`: it stops the loop, and plays it again.
- One card per step, in step order. Each card is a `<button data-cf="tile">` with `data-cf-at`: the second of the loop where its step holds still. A click jumps the demo to that second and stops it there.
- Each card has an outline that shows only during its step. Give it the same keyframes as the caption of that step.
- Keep the script of the example as it is. Change only the `data-cf-at` times.
- Add `@media (prefers-reduced-motion: reduce)` with `animation: none`.
- The picture on each card shows its step as a still close-up, so nothing is lost when the motion is off.

## The row

- One idea is one frame.
- A row of ideas starts with a `today` frame. Then comes one frame per idea, in reading order.
- Mark your pick with the `pick` kind. Never explain the pick in a paragraph.
- A finding is the real screen, drawn clean. One problem per frame, or one problem per tile.
- A reference from research is a `result` frame. Its drawing is the saved picture of that product. A reference with no picture stays out of the row.
- A flow of 2 to 4 steps is one looping frame, not one frame per step.
- A longer flow is cut into parts of 2 to 4 steps. One part is one looping frame. Put the parts side by side, in order, with the same chip. Start each title with its part: "Part 2 of 3". The step numbers go on from the part before.
- A plan is one `result` frame per step. Each drawing shows what that step makes.
- Open questions and reasons do not go on the canvas. They go in the chat reply or the document.

## The check

Run the check before you publish, with the files of one row in reading order:

`python3 scripts/check_frames.py <frame file> [<frame file> ...]`

A frame that fails is not published. Fix every `FAIL` line and run the check again. Never remove a `data-cf` slot to make the check pass.

The check cannot see everything. It cannot click: on the canvas, press Play on a looping frame and click each card and the badge yourself. It compares colors, fonts, components and features with the screen source, but it cannot measure layout, and it cannot see a mark drawn on the design. Those two rules are yours to keep.
