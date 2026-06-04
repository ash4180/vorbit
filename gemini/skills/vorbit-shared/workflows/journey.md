# Vorbit Journey Workflow

Use for creating user journey diagrams in Excalidraw.

> **MCP namespace**: This workflow uses `mcp__claude_ai_Excalidraw__create_view` (inline preview) and `mcp__claude_ai_Excalidraw__export_to_excalidraw` (publish to shareable URL). See `vorbit-shared/references/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

1. Load Vorbit durable rules before doing anything else.
2. Gather context: fetch PRD if available, extract user stories and acceptance criteria.
3. Confirm flow details: ask about entry point, primary goal, key decisions, error scenarios, exit points.
4. Draft flow as text outline in chat. Get user confirmation before creating diagram.
5. Load element format once via `mcp__claude_ai_Excalidraw__read_me`, then build the element array and call `create_view` to render inline preview with animation. Max 15 nodes. Use labeled shapes (`label: { text: "..." }`), `startBinding`/`endBinding` for arrows, `cameraUpdate` first.
6. After user confirms the preview, call `export_to_excalidraw` with the same JSON to get a shareable excalidraw.com URL. If user says "skip preview", go straight here.
7. Color palette (Excalidraw light fills): start/end and action `#a5d8ff`, decision diamond `#fff3bf`, positive `#b2f2bb`, negative `#ffc9c9`.
8. Update PRD with the excalidraw.com URL if PRD exists.
9. Report: Excalidraw URL, PRD updated status, node count, next steps.
