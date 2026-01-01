---
description: Create user journey diagrams in FigJam, update PRD in Notion with link
argument-hint: [feature or PRD reference]
allowed-tools: Read, Skill, AskUserQuestion, mcp__plugin_Notion_notion__*, mcp__plugin_figma_figma__generate_diagram
---

Create a user flow for: $ARGUMENTS

Use the **journey** skill for output format and validation rules.

## Step 0: Verify Notion Connection (if Notion needed)

**IF user provides a Notion URL OR wants to update PRD in Notion:**
1. Run a lightweight test: use `notion-find` to search for "test"
2. **IF the call fails (auth error, token expired, connection refused):**
   - Tell the user: "Notion connection has expired. Please run `/mcp` and reconnect the Notion server, then run this command again."
   - **STOP HERE** - do not proceed with the rest of the command
3. **IF the call succeeds:** proceed to Step 1

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

## Step 3: Create User Flow in FigJam

**CRITICAL: Max 15 nodes total. Split complex flows.**

Use `mcp__plugin_figma_figma__generate_diagram` with:
- `name`: Descriptive title (e.g., "User Login Flow")
- `mermaidSyntax`: Flowchart using LR direction, all text in quotes
- `userIntent`: Brief description of what user is accomplishing

### Mermaid Syntax Rules for FigJam

```mermaid
flowchart LR
    A(["Entry"]):::startend --> B["Action"]:::action
    B --> C{"Decision?"}:::decision
    C -->|"Yes"| D["Continue"]:::action
    C -->|"No"| E["Error"]:::negative
    D --> F(["Success"]):::positive

    classDef startend fill:#CBD5E1,color:#334155,stroke:#94A3B8
    classDef action fill:#BAE6FD,color:#0c4a6e,stroke:#7DD3FC
    classDef condition fill:#C4B5FD,color:#4c1d95,stroke:#A78BFA
    classDef decision fill:#FED7AA,color:#7c2d12,stroke:#FDBA74
    classDef positive fill:#A7F3D0,color:#14532d,stroke:#6EE7B7
    classDef negative fill:#FECDD3,color:#881337,stroke:#FB7185
```

Note: Error state `E` is terminal. User sees the error and retries implicitly - no back-loop needed.

### Color Palette (Required)

| Node Type | Fill | Stroke | Use For |
|-----------|------|--------|---------|
| Start & End | `#CBD5E1` | `#94A3B8` | Entry/exit points |
| Action | `#BAE6FD` | `#7DD3FC` | User actions |
| Condition | `#C4B5FD` | `#A78BFA` | Filter/settings nodes |
| Decision | `#FED7AA` | `#FDBA74` | Branch points |
| Positive | `#A7F3D0` | `#6EE7B7` | Success states |
| Negative | `#FECDD3` | `#FB7185` | Error states |

**IMPORTANT**:
- Use `LR` direction (left-to-right)
- Put ALL text in quotes (`["text"]`, `{"text?"}`, `-->|"label"|`)
- Apply color classes to ALL nodes using `:::className` syntax
- No emojis in Mermaid code
- No `\n` for newlines

## Step 4: Update PRD in Notion

If PRD exists from Step 1:
1. Fetch the PRD page
2. Add FigJam URL under "User Flow" section
3. Include the Mermaid source code as backup

**IMPORTANT**: After calling generate_diagram, show the returned URL as a markdown link so user can view and edit.

## Report

- FigJam flow created: Yes (with URL)
- PRD updated: Yes/No (with URL)
- Node count: X nodes, Y decisions, Z error paths
- Next: `/vorbit:design:prototype` or `/vorbit:implement:epic`
