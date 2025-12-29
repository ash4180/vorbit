# Vorbit

Product development workflows for AI coding agents. Notion-first, Linear-integrated.

**Works with:** Claude Code, Google Antigravity (Gemini)

**Jump in at any step.** No strict prerequisites.

## Installation

```bash
git clone https://github.com/ash4180/vorbit.git
```

### Claude Code
Use as plugin directory or copy to `.claude/`.

### Google Antigravity
Copy `.agent/` folder to your project root:
```bash
cp -r vorbit/.agent your-project/
```

Or symlink for updates:
```bash
ln -s /path/to/vorbit/.agent your-project/.agent
```

## Architecture

### Claude Code
```
commands/
├── design/           # explore, prd, journey, prototype
└── implement/        # epic, implement, verify, review

skills/               # Pure schemas (no process instructions)
├── explore/          # Exploration document schema
├── prd/              # PRD schema with validation rules
├── journey/          # User flow diagram schema (max 15 nodes)
├── epic/             # Linear issue schema (branch-friendly titles)
└── prototype/        # Page/feature prototype patterns

hooks/
└── hooks.json        # Auto-validation before Notion/Linear saves
```

### Antigravity (Gemini)
```
.agent/
└──workflows/        # On-demand commands (triggered via /)
    ├── explore.md
    ├── prd.md
    ├── journey.md
    ├── prototype.md
    ├── epic.md
    ├── implement.md
    ├── verify.md
    └── review.md
```

**Notion** = Source of truth (PRDs, explorations, flows)
**Linear** = Issue tracking (epics + sub-issues)
**Code** = Prototypes and implementation

## Commands

| Purpose | Claude Code | Antigravity |
|---------|-------------|-------------|
| Explore ideas | `/vorbit:design:explore [topic]` | `/explore [topic]` |
| Create PRD | `/vorbit:design:prd [feature]` | `/prd [feature]` |
| User flow diagram | `/vorbit:design:journey [feature]` | `/journey [feature]` |
| UI prototype | `/vorbit:design:prototype [feature]` | `/prototype [feature]` |
| Create issues | `/vorbit:implement:epic [feature]` | `/epic [feature]` |
| Implement | `/vorbit:implement:implement [issue]` | `/implement [issue]` |
| Verify | `/vorbit:implement:verify [issue]` | `/verify [issue]` |
| Code review | `/vorbit:implement:review [file]` | `/review [file]` |

## Flexible Workflow

Enter at any point:

```
┌─────────────────────────────────────────────────────────┐
│                    ANY ENTRY POINT                      │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Explore │   │   PRD   │   │  Epic   │   │Prototype│
    │ (Notion)│   │ (Notion)│   │ (Linear)│   │ (Code)  │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                                │
                                ▼
                        ┌─────────────┐
                        │  Implement  │
                        └──────┬──────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   Verify    │
                        └─────────────┘
```

## Auto-Validation

Hooks automatically validate before saving:

- **Notion saves**: PRD, Exploration, User Flow validated against schemas
- **Linear creates**: Issue title (kebab-case, branch-friendly) and description validated

If validation fails, you'll be asked: "Found issues: [list]. Save anyway?"

## Skills

| Skill | Purpose | Key Rules |
|-------|---------|-----------|
| **explore** | Exploration structure | 10+ questions before options |
| **prd** | PRD structure | 3-8 word name, numbers in success criteria |
| **user-flow** | User flow diagrams | Max 15 nodes, split if needed |
| **epic** | Linear issue structure | Title from user story → kebab-case |
| **prototype** | Page/feature patterns | Mocks under feature folder |

## Requirements

### Claude Code
- Claude Code CLI
- Notion MCP
- Linear MCP
- Figma MCP

### Google Antigravity
- Google Antigravity IDE
- Notion integration 
- Linear integration 
- Figma MCP

## License

MIT
