---
name: vorbit-concept
description: Use when the user asks to draw, show or sketch an idea, a concept, design options, a before and after, a flow, findings or a plan as pictures on a canvas, or when another skill must present ideas visually. It draws each idea as one concept frame from a fixed template (a big drawing of the design in its real place, up to four small state tiles, very few words), starts a row with the current state, marks the pick, reads the real screen first so the drawing matches the project, runs a check script that refuses frames that are mostly text or that do not match the project, and publishes the row to a Claude canvas or saves it as HTML files. Do not use for a production screen, a clickable prototype (the prototype skill), a written document, or a chart of data.
---

# Vorbit Concept

Before drawing:

1. Read `../vorbit-shared/references/load-rules.md`.
2. Read `../vorbit-shared/workflows/concept.md`.
3. Load the applicable durable Vorbit rules for the current project and Gemini agent scope.
4. Then follow the concept workflow: list the frames, read the real screen, draw each frame from an example, run the check, then publish or save.
