<!-- GENERATED from skills/concept/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-concept` skill directory (a sibling of `vorbit-shared`).

# Concept Skill

Draw ideas as concept frames, so the user can look, compare and choose without reading.

Read and follow `../references/execution-contract.md` before starting.

## Step 1: List the frames

Name the row before you draw: the `today` frame first, then one frame per idea. Write next to each frame if it loops or stays still. A flow of more than four steps is several frames: one frame per part of 2 to 4 steps. A result that is not a choice (findings, references, a plan) is a row of `result` frames.

When the idea changes a screen that exists in the code, read `references/screen-source.md` (from this skill's installed directory) and write the screen source file before you draw. Every drawing must look like the real product: the same layout, components, colors, type and features. The check compares each drawing with that file.

## Step 2: Draw each frame

Read `references/frame-rules.md` (from this skill's installed directory) and follow it.

Decide for each frame if the idea happens over time: a flow, an interaction or a change of state. If it does, the frame is a looping demo the user can stop, with one clickable card per step: copy `examples/frame-motion.dc.html`. If not, copy `examples/frame.dc.html`. Both paths are from this skill's installed directory.

Keep the structure, sizes and frame colors of the example. Replace only the content of the `data-cf` slots.

## Step 3: Check

Run the check on the row, in reading order:

`python3 scripts/check_frames.py <frame file> [<frame file> ...]` (the script is in this skill's directory)

Fix every `FAIL` line and run it again. Publish nothing until it prints `OK`. Never fix a `FAIL` about the project by changing the screen source file to match your drawing. Change the drawing.

## Step 4: Publish

- With canvas tools in this session: publish the frames to one Claude canvas of the "Design" type, following that type's instructions. One frame is one artboard. A looping frame gets `"is_interactive": true` in its canvas entry, so its cards and its Play and Stop button work. Put the frames of a row side by side, in reading order. A row may have one short title above it. Add no sticky notes.
- Without canvas tools: save the frames as HTML files in one folder and give the user the folder path.

## Step 5: Report

Reply in one or two sentences: where the frames are, and which one is your pick. When a frame loops, add one sentence: press Play on that frame, then click a card to hold its step. Reasons and open questions go in this reply, never on a frame.
