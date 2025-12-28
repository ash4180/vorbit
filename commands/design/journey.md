---
description: Create user journey diagrams in Excalidraw, update PRD in Notion with link
argument-hint: [feature or PRD reference]
allowed-tools: Read, AskUserQuestion, Notion, mcp__excalidraw__*
---

Create a user flow for: $ARGUMENTS

Use the **user-flow** skill for output format and validation rules.

## Prerequisites

**Canvas server must be running:**
```bash
cd ~/.claude/mcps/excalidraw-mcp && npm run canvas
```
View diagrams at: http://localhost:3000

## Step 1: Gather Context

1. IF Notion PRD URL provided, fetch the PRD
2. IF feature name provided, search Notion for existing PRD
3. Extract user stories and acceptance criteria if available

## Step 2: Confirm Flow Details

**RULE: If ANY requirement is unclear, use AskUserQuestion.**

Ask about:
1. **Entry point** - "Where does the user start?"
2. **Primary goal** - "What is the user trying to accomplish?"
3. **Key decisions** - "What choices will the user make?"
4. **Error scenarios** - "What can go wrong? How to handle?"
5. **Exit points** - "Where can the user complete or leave?"

## Step 3: Create User Flow in Excalidraw

**CRITICAL: Max 15 nodes total. Split complex flows.**

Use Excalidraw MCP to create visual flow:

### Option A: From Mermaid (Recommended)
Use `create_from_mermaid` tool with Mermaid syntax:
```
flowchart LR
    A(["Entry"]) --> B["Action"]
    B --> C{"Decision?"}
    C -->|"Yes"| D["Continue"]
    C -->|"No"| E["Error"]
    E --> F["Recovery"]
    F --> B
    D --> G(["Success"])
```

### Option B: Direct Elements
Use `batch_create_elements` for custom layouts with annotations.

### Adding Notes/Memos
After creating flow, use `create_element` with type "text" to add:
- Validation rules near input nodes
- Error messages near error states
- Business logic notes

## Step 4: Update PRD in Notion

If PRD exists from Step 1:
1. Fetch the PRD page
2. Add flow reference: "User Flow: View in Excalidraw (local canvas)"
3. Include the Mermaid source code as backup

## Step 5: Export (Optional)

Tell user: "Flow created! View at http://localhost:3000"

Options for sharing:
- Screenshot the canvas and upload to Notion
- Export .excalidraw file from browser
- Copy Mermaid source to Notion as text backup

## Report

- Excalidraw flow created: Yes (view at localhost:3000)
- PRD updated: Yes/No (with URL)
- Node count: X nodes, Y decisions, Z error paths
- Next: `/vorbit:design:prototype` or `/vorbit:implement:epic`
