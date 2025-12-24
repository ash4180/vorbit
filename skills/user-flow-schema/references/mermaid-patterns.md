# Mermaid Diagram Patterns

## Step Types

| Type | Mermaid Shape | Use Case |
|------|---------------|----------|
| `start` | `([text])` | User's starting point |
| `action` | `[text]` | User performs action |
| `decision` | `{text?}` | User/system makes choice |
| `success` | `[text]` | Positive outcome |
| `error` | `[text]` | Error state |
| `end` | `([text])` | User leaves flow |

## Base Template

```mermaid
flowchart LR
    %% Entry
    START([Start]) --> A[First Action]

    %% Main flow
    A --> B{Decision?}
    B -->|Yes| C[Action C]
    B -->|No| D[Action D]

    %% Success path
    C --> SUCCESS[Success State]
    D --> SUCCESS

    %% Error handling
    A -->|Error| ERR[Error State]
    ERR -->|Retry| A

    %% Exit
    SUCCESS --> END([End])
```

## Direction Options

- `LR` - Left to Right (default, recommended)
- `TD` - Top Down (for vertical flows)

## Styling

```mermaid
flowchart LR
    %% Style definitions
    classDef success fill:#90EE90
    classDef error fill:#FFB6C1
    classDef decision fill:#FFE4B5

    A[Action] --> B{Decision}
    B -->|Yes| C[Success]:::success
    B -->|No| D[Error]:::error

    class B decision
```

## Subgraphs for Complex Flows

```mermaid
flowchart LR
    subgraph Login
        A[Enter email] --> B[Enter password]
        B --> C[Click Login]
    end

    subgraph Dashboard
        D[View stats] --> E[Navigate]
    end

    C --> D
```

## Edge Labels

Always label decision branches:
```mermaid
B{Valid?} -->|Yes| C
B -->|No| D
```

Never use unlabeled branches from decisions.

## Max Complexity

| Flow Size | Steps | Recommendation |
|-----------|-------|----------------|
| Simple | 1-5 | Single diagram |
| Medium | 6-10 | Single diagram with sections |
| Complex | 11-15 | Consider subgraphs |
| Too Large | 16+ | MUST split into sub-flows |
