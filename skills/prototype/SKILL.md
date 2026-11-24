---
name: prototype
description: Use when the user asks for a clickable prototype, an interactive mockup, or to try or present a flow with real clicks. It reads the real screen's code first and writes a screen source file, builds the flow as an interactive artboard on a Claude canvas with sample data, runs a check that refuses dead buttons and designs that do not match the project, and publishes it. It changes no project file and writes no app code. Do not use for still or looping idea frames (the concept skill), Figma artifacts (the figma skill), or production code with mock data (the implement skill).
---

# Prototype Skill

Build a prototype the user can really click, on a Claude canvas. It is for trying a flow and for presenting it. It changes no project file and is never app code.

Read and follow `../_shared/execution-contract.md` before starting.

## Step 1: Name the flow

Write down, in one line each: the screen where the flow starts, each click the user makes, and the end result.

- The branch `.vorbit/prd.md` (see `../_shared/spec-files.md`) is the source for behavior when it exists. Use the steps and acceptance criteria of the story as the flow.
- With no PRD, take the flow from the request, or from the concept frame the user picked.
- Ask the user only when the start or the end result is unclear. Never add steps, screens or features that nobody asked for.

## Step 2: Read the real screen

Read `../concept/references/screen-source.md` and follow it. When the screen exists in the code, write its `screen-source.json` before you draw anything. The prototype must look and behave like the real product: the same layout, components, colors, type and features.

Only a flow for a product with no code yet uses `data-cf-source="none"`.

## Step 3: Build

Read `../concept/references/prototype-rules.md` and follow it. Copy `../concept/examples/prototype.dc.html` and replace its screen with the real one.

Save the files in `.vorbit/prototype/<topic>/` in the worktree (folder rules in `../_shared/spec-files.md`). Write nothing outside that folder.

## Step 4: Check

`python3 ../concept/scripts/check_frames.py <prototype file> [...]`

Fix every `FAIL` line and run it again. Publish nothing until it prints `OK`.

## Step 5: Publish

- With canvas tools in this session: publish to one Claude canvas of the "Design" type, following that type's instructions. Each prototype artboard gets `"is_interactive": true`. When the idea came from a concept row, add the prototype to that same canvas, after the row.
- Without canvas tools: stop and say that a clickable prototype needs a Claude canvas. Offer looping concept frames in its place. Do not build the flow as app code.

## Step 6: Walk the flow

The check cannot click. Open the canvas, press Play, and make every click of the flow from Step 1. Use a browser tool when the session has one. When it has none, say plainly that the clicks are not tested, and ask the user to walk the flow.

Fix what does not work, run the check, and publish again.

## Step 7: Report

- The canvas link, and the flow in one line.
- What was tested by clicking, and what was not.
- Each control marked `data-cf-idle`, so the user knows what does nothing.
- Next: `/vorbit:implement:epic` to plan the real feature. Give it the canvas link as the behavior reference.
