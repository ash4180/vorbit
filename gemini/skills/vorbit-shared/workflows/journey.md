# Vorbit Journey Workflow

Use for creating user journey diagrams.

1. Load Vorbit durable rules before doing anything else.
2. Gather context: fetch PRD if available, extract user stories and acceptance criteria.
3. Confirm flow details: ask about entry point, primary goal, key decisions, error scenarios, exit points.
4. Draft flow as text outline in chat. Get user confirmation before creating diagram.
5. Create in FigJam using Mermaid syntax: max 15 nodes, LR direction, all text in quotes, no back-loops. Error states are terminal (implicit retry).
6. Color palette: startend (#CBD5E1), action (#BAE6FD), condition (#C4B5FD), decision (#FED7AA), positive (#A7F3D0), negative (#FECDD3).
7. Update PRD with FigJam URL and Mermaid source if PRD exists.
8. Report: FigJam URL, PRD updated status, node count, next steps.
