---
name: journey
version: 1.2.0
description: Use when user says "create user flow", "user journey", "flow diagram", "map user steps", "Excalidraw diagram", or wants to visualize user flows. Renders the flow inline in chat with animation, then publishes a shareable Excalidraw URL.
---

# Journey Skill

Create user journey diagrams in Excalidraw with an inline animated preview, then publish to excalidraw.com for a shareable URL.

> **MCP namespace**: This skill uses `mcp__claude_ai_Excalidraw__create_view` (inline preview) and `mcp__claude_ai_Excalidraw__export_to_excalidraw` (publish). See `_shared/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Gather Context

1. IF Notion PRD URL provided, use `notion-find` to fetch the PRD
2. IF Anytype PRD URL or object ID provided, use `API-get-object` to fetch the PRD
3. IF feature name provided, search the detected platform for existing PRD
4. Extract user stories and acceptance criteria if available

## Step 3: Confirm Flow Details

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Ask about:
1. **Entry point** - "Where does the user start?"
2. **Primary goal** - "What is the user trying to accomplish?"
3. **Key decisions** - "What choices will the user make?"
4. **Error scenarios** - "What can go wrong? How to handle?"
5. **Exit points** - "Where can the user complete or leave?"

## Step 4: Draft Flow in Chat

**Show the flow as a text outline for review:**

```
User Flow: [Feature Name]

1. [Entry] User lands on...
   ↓
2. [Action] User clicks...
   ↓
3. [Decision] Is valid?
   → Yes: Continue to step 4
   → No: Show error → End
   ↓
4. [Action] System processes...
   ↓
5. [Success] User sees confirmation → End
```

**After showing draft, ask:** "Does this flow look correct? Ready to draw?"

## Step 5: Render Flow in Excalidraw

**Only proceed after user confirms the draft.**

**CRITICAL: Max 15 nodes total. Split complex flows.**

### Step 5a: Inline Preview (`create_view`)

Before the first preview in a session, load the element format reference once: call `mcp__claude_ai_Excalidraw__read_me`. The response includes the color palette, element schema, camera/sizing rules, and full examples. Do not call `read_me` again in the same session — the response is the same.

Build an element array (see "Element Patterns" below), then call `mcp__claude_ai_Excalidraw__create_view` with the JSON-encoded array as the `elements` string. The diagram renders inline in chat with streaming draw-on animation.

After it renders, ask: "Does this look right, or should I adjust?"

If adjustments are needed, modify the element array and call `create_view` again. To avoid re-sending the whole diagram, start the new array with `{ "type": "restoreCheckpoint", "id": "<checkpointId from previous response>" }` and append only changed/new elements.

### Step 5b: Publish (`export_to_excalidraw`)

After user confirms the diagram, call `mcp__claude_ai_Excalidraw__export_to_excalidraw` with the same elements (serialized as the `json` string). The response is a shareable `https://excalidraw.com/...` URL.

### Skip-preview flag

If the user says "skip preview", "just give me the link", or similar, skip Step 5a and go straight to Step 5b. Default is always preview-then-publish.

## Step 6: Update PRD

If PRD exists from Step 2:

### If Notion PRD:
1. Use `notion-fetch` to get the PRD page
2. Add the Excalidraw URL under "User Flow" section

### If Anytype PRD:
1. Use `API-get-object` to fetch the PRD
2. Use `API-update-object` to add the Excalidraw URL under "User Flow" section

**IMPORTANT**: After `export_to_excalidraw`, show the returned URL as a markdown link so the user can view and edit.

## Step 7: Report

- Excalidraw flow created: Yes (with URL)
- PRD updated: Yes/No (with URL)
- Node count: X nodes, Y decisions, Z error paths
- Next: `/vorbit:implement:prototype` or `/vorbit:implement:epic`

---

# Element Patterns

## Element Format

Excalidraw uses a JSON array of element objects. Use labeled shapes (`label: { text: "..." }`) instead of separate text elements — auto-centers and saves tokens.

Always start the array with a `cameraUpdate` so the viewport frames the diagram. Use camera L (`width: 800, height: 600`) for standard flows. Emit elements in z-order: background → shape → label → arrow → next shape.

## Node Types

| Type | Shape | Fill | Use For |
|------|-------|------|---------|
| Start / End | rectangle (`roundness: { type: 3 }`) | `#a5d8ff` (light blue) | Entry / exit points |
| Action | rectangle (`roundness: { type: 3 }`) | `#a5d8ff` (light blue) | User does something |
| Decision | diamond | `#fff3bf` (light yellow) | Branch point — Yes/No |
| Positive | rectangle (`roundness: { type: 3 }`) | `#b2f2bb` (light green) | Success state |
| Negative | rectangle (`roundness: { type: 3 }`) | `#ffc9c9` (light red) | Error state |

For multi-section flows, wrap each section in a background zone rectangle (`opacity: 30`, light fill from the read_me palette).

## Arrows

Bind arrows to nodes with `startBinding` and `endBinding` so they stay attached if nodes move. `fixedPoint`: top `[0.5,0]`, bottom `[0.5,1]`, left `[0,0.5]`, right `[1,0.5]`.

Add `label: { text: "Yes" }` on the arrow for decision-branch labels.

## Validation Rules

- Exactly one entry point
- At least one exit point with success state
- All decision branches labeled (`label` on the arrow)
- Error states are terminal — no back-loops; user retries implicitly
- **MAX 15 nodes total** — split into multiple diagrams if more needed
- Minimum shape size 120×60, minimum fontSize 16 (20 for titles), 20–30px gaps between elements

## Common Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| Back-loop arrow from error to retry | Error as terminal node | Implicit retry; cleaner layout |
| 20+ node diagram | Split into sub-flows | Max 15 nodes per diagram |
| Separate `text` element on top of `rectangle` | `label: { text: "..." }` on the rectangle | Auto-centers, saves tokens |
| Manual arrow positioning | `startBinding` + `endBinding` to node ids | Arrows stay attached when nodes move |
| Skipping `cameraUpdate` | Always emit a `cameraUpdate` first | Without it the viewport may not frame the diagram |
| `fontSize` below 16 | Minimum 16 for body, 20 for titles | Smaller is unreadable at display scale |

## Template (Skeleton)

```json
[
  { "type": "cameraUpdate", "width": 800, "height": 600, "x": 0, "y": 100 },
  { "type": "rectangle", "id": "start", "x": 50, "y": 200, "width": 140, "height": 70, "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "label": { "text": "User opens feature", "fontSize": 18 } },
  { "type": "arrow", "id": "a1", "x": 190, "y": 235, "width": 80, "height": 0, "points": [[0,0],[80,0]], "endArrowhead": "arrow", "startBinding": { "elementId": "start", "fixedPoint": [1, 0.5] }, "endBinding": { "elementId": "decide", "fixedPoint": [0, 0.5] } },
  { "type": "diamond", "id": "decide", "x": 270, "y": 175, "width": 160, "height": 120, "backgroundColor": "#fff3bf", "fillStyle": "solid", "label": { "text": "Valid?", "fontSize": 18 } },
  { "type": "arrow", "id": "a2", "x": 430, "y": 235, "width": 80, "height": 0, "points": [[0,0],[80,0]], "endArrowhead": "arrow", "label": { "text": "Yes" }, "startBinding": { "elementId": "decide", "fixedPoint": [1, 0.5] }, "endBinding": { "elementId": "ok", "fixedPoint": [0, 0.5] } },
  { "type": "rectangle", "id": "ok", "x": 510, "y": 200, "width": 140, "height": 70, "roundness": { "type": 3 }, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "label": { "text": "Success", "fontSize": 18 } },
  { "type": "arrow", "id": "a3", "x": 350, "y": 295, "width": 0, "height": 80, "points": [[0,0],[0,80]], "endArrowhead": "arrow", "label": { "text": "No" }, "startBinding": { "elementId": "decide", "fixedPoint": [0.5, 1] }, "endBinding": { "elementId": "err", "fixedPoint": [0.5, 0] } },
  { "type": "rectangle", "id": "err", "x": 280, "y": 375, "width": 140, "height": 70, "roundness": { "type": 3 }, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "label": { "text": "Error shown", "fontSize": 18 } }
]
```
