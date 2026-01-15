# Vorbit

Universal product development workflows for AI coding agents. TDD-first, Linear-integrated.

**Works with:** Claude Code, Google Antigravity, GPT Codex

**Jump in at any step.** No strict prerequisites.

## Installation

### Claude Code (Marketplace)
```
/install-plugin vorbit
```

### Google Antigravity
Skills auto-discovered from `.agent/skills/` when you open the project.

### GPT Codex (GitHub Copilot)
```
$skill-installer vorbit
```

### Manual Installation
```bash
git clone https://github.com/ash4180/vorbit.git
claude --plugin-dir /path/to/vorbit
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
└── skills/          # Full process instructions (auto-discovered)
    ├── explore.md
    ├── prd.md
    ├── journey.md
    ├── prototype.md
    ├── epic.md
    ├── implement.md
    ├── verify.md
    └── review.md
```

### GPT Codex
```
.codex/
└── skills/          # Symlink to .agent/skills/ (shares same content)
```

**Notion** = Source of truth (PRDs, explorations, flows)
**Linear** = Issue tracking (epics + sub-issues)
**Code** = Prototypes and implementation

## Commands

| Purpose | Claude Code | Antigravity | GPT Codex |
|---------|-------------|-------------|-----------|
| Explore ideas | `/vorbit:design:explore [topic]` | Auto | `$explore` |
| Create PRD | `/vorbit:design:prd [feature]` | Auto | `$prd` |
| User flow diagram | `/vorbit:design:journey [feature]` | Auto | `$journey` |
| UI prototype | `/vorbit:design:prototype [feature]` | Auto | `$prototype` |
| Webflow development | `/vorbit:design:webflow [figma-url]` | - | - |
| Create issues | `/vorbit:implement:epic [feature]` | Auto | `$epic` |
| Implement | `/vorbit:implement:implement [issue]` | Auto | `$implement` |
| Verify | `/vorbit:implement:verify [issue]` | Auto | `$verify` |
| Code review | `/vorbit:implement:review [file]` | Auto | `$review` |

**Antigravity "Auto"**: Skills trigger automatically when your task matches the description.

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

### GPT Codex
- GitHub Copilot with Codex
- Notion MCP
- Linear MCP
- Figma MCP

## Platform Support

| Platform | Skills | Commands | Hooks | Install |
|----------|--------|----------|-------|---------|
| Claude Code | ✅ | ✅ | ✅ | `/install-plugin vorbit` |
| Antigravity | ✅ | Auto | ❌ | Auto-discovered |
| GPT Codex | ✅ | `$skill` | ❌ | `$skill-installer vorbit` |

## License

MIT
