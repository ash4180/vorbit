---
name: vorbit-prototype
description: Use when the user asks for a clickable prototype, an interactive mockup, or to try or present a flow with real clicks. It reads the real screen's code first and writes a screen source file, builds the flow as an interactive artboard on a Claude canvas with sample data, runs a check that refuses dead buttons and designs that do not match the project, and publishes it. It changes no project file and writes no app code. Do not use for still or looping idea frames (the concept skill), Figma artifacts (the figma skill), or production code with mock data (the implement skill).
---

# Vorbit Prototype

Before prototyping:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/prototype.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the prototype workflow: name the flow, read the real screen, build the clickable artboard, check it, publish, walk the flow.
