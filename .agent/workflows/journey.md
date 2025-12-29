# Journey

Create user journey diagrams, update PRD with link.

Use the **user-flow-schema** rule for output format and validation.

## Step 1: Gather Context

1. IF Notion PRD URL provided, fetch the PRD
2. IF feature name provided, search Notion for existing PRD
3. Extract user stories and acceptance criteria if available

## Step 2: Confirm Flow Details

**RULE: If ANY requirement is unclear, ask questions.**

Ask about:
1. **Entry point** - "Where does the user start?"
2. **Primary goal** - "What is the user trying to accomplish?"
3. **Key decisions** - "What choices will the user make?"
4. **Error scenarios** - "What can go wrong? How to handle?"
5. **Exit points** - "Where can the user complete or leave?"

## Step 3: Create User Flow

**CRITICAL: Max 15 nodes total. Split complex flows.**

Create visual flow using Mermaid syntax with color styling:
```mermaid
flowchart LR
    A(["Entry"]):::startend --> B["Action"]:::action
    B --> C{"Decision?"}:::decision
    C -->|"Yes"| D["Continue"]:::action
    C -->|"No"| E["Error"]:::negative
    E --> F["Recovery"]:::action
    F --> B
    D --> G(["Success"]):::positive

    classDef startend fill:#CBD5E1,color:#334155,stroke:#94A3B8
    classDef action fill:#BAE6FD,color:#0c4a6e,stroke:#7DD3FC
    classDef condition fill:#C4B5FD,color:#4c1d95,stroke:#A78BFA
    classDef decision fill:#FED7AA,color:#7c2d12,stroke:#FDBA74
    classDef positive fill:#A7F3D0,color:#14532d,stroke:#6EE7B7
    classDef negative fill:#FECDD3,color:#881337,stroke:#FB7185
```

### Color Palette

| Node Type | Fill | Stroke | Use For |
|-----------|------|--------|---------|
| Start & End | `#CBD5E1` | `#94A3B8` | Entry/exit points |
| Action | `#BAE6FD` | `#7DD3FC` | User actions |
| Condition | `#C4B5FD` | `#A78BFA` | Filter/settings nodes |
| Decision | `#FED7AA` | `#FDBA74` | Branch points |
| Positive | `#A7F3D0` | `#6EE7B7` | Success states |
| Negative | `#FECDD3` | `#FB7185` | Error states |

For complex flows, split into:
* Main flow (15 nodes max)
* Sub-flows referenced by name

## Step 4: Update PRD (if exists)

If PRD exists from Step 1:
1. Fetch the PRD page
2. Add flow reference with diagram
3. Include the Mermaid source code

## Report

* Flow created: Yes
* PRD updated: Yes/No (with URL)
* Node count: X nodes, Y decisions, Z error paths
* Next: `/prototype` or `/epic`
