# Vorbit

Product development workflows for AI coding agents. Notion-first, Linear-integrated.

**Works with:** Claude Code, Google Antigravity (Gemini)

**Jump in at any step.** No strict prerequisites.

## Installation

```bash
git clone https://github.com/ash4180/vorbit.git
```

### Claude Code
Run with plugin directory flag:
```bash
claude --plugin-dir /path/to/vorbit
```

Or add to your shell config for permanent use:
```bash
alias claude='claude --plugin-dir /path/to/vorbit'
```

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
├── design/           # explore, prd, journey, prototype, webflow
└── implement/        # epic, implement, verify, review

skills/               # Pure schemas (no process instructions)
├── explore/          # Exploration document schema
├── prd/              # PRD schema with validation rules
├── journey/          # User flow diagram schema (max 15 nodes)
├── epic/             # Linear issue schema (branch-friendly titles)
├── prototype/        # Page/feature prototype patterns
└── webflow/          # Webflow development from Figma designs
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
| Webflow development | `/vorbit:design:webflow [figma-url or description]` | - |
| Create issues | `/vorbit:implement:epic [feature]` | `/epic [feature]` |
| Implement | `/vorbit:implement:implement [issue]` | `/implement [issue]` |
| Verify | `/vorbit:implement:verify [issue]` | `/verify [issue]` |
| Code review | `/vorbit:implement:review [file]` | `/review [file]` |

## Loop Mode (Ralph Wiggum Pattern)

**Automatically iterate until task complete:**

```bash
/vorbit:implement:implement ABC-123 --loop
```

**How it works:**
1. Fetches Linear issue acceptance criteria
2. Runs implementation (TDD workflow)
3. On completion attempt, checks if all criteria met
4. If not done → automatically starts next iteration
5. If done → outputs completion signal and exits

**Customize completion signal:**
```bash
/vorbit:implement:implement ABC-123 --loop --completion-signal "🎉 DONE"
```

**Cancel active loop:**
```bash
/vorbit:implement:implement ABC-123 --cancel
```

**Default limits:**
- Max iterations: 50
- Completion signal: "✅ All acceptance criteria met"

**Best for:**
- Complex features requiring multiple refinement passes
- TDD workflows where tests guide development
- Autonomous implementation when requirements are clear

## Skills

| Skill | Purpose | Key Rules |
|-------|---------|-----------|
| **explore** | Exploration structure | 10+ questions before options |
| **prd** | PRD structure | 3-8 word name, numbers in success criteria |
| **journey** | User flow diagrams | Max 15 nodes, split if needed |
| **epic** | Linear issue structure | Title from user story → kebab-case |
| **prototype** | Page/feature patterns | Mocks under feature folder |
| **webflow** | Webflow development | Figma optional, templates with page slots |

## Requirements

### Claude Code
- Claude Code CLI
- Notion MCP
- Linear MCP
- Figma MCP
- Webflow MCP (for `/vorbit:design:webflow`)

### Google Antigravity
- Google Antigravity IDE
- Notion MCP
- Linear MCP
- Figma MCP

## License

MIT
