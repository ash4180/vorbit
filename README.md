# Vorbit

TDD-first product development workflows for Claude Code, with strong PRD → Epic → Implement traceability.

Vorbit packages three layers:
- **Commands** (`commands/`) — slash command entry points, thin dispatchers
- **Skills** (`skills/*/SKILL.md`) — workflow logic with multi-step decision trees
- **Hooks** (`hooks/hooks.json`) — automatic formatting, validation, loop control, and learning capture

## Installation

### Prerequisites
- Python >= 3.9 (required for hook scripts)

### Local Setup
```bash
git clone https://github.com/ash4180/vorbit.git
cd vorbit
bash dev-setup.sh
```

Restart your Claude Code session after running the setup script.

## Recommended Workflow

1. **Explore** — shape the problem with 10+ questions (`/vorbit:design:explore`)
2. **PRD** — write concrete user stories with acceptance criteria (`/vorbit:design:prd`)
3. **Journey** — visualize user flows in FigJam (`/vorbit:design:journey`)
4. **Epic** — convert PRD stories into Linear issues with dependency tree (`/vorbit:implement:epic`)
5. **Implement** — TDD-first coding (tests before code) (`/vorbit:implement:implement`)
6. **Verify** — validate against acceptance criteria (`/vorbit:implement:verify`)
7. **Review** — 3-layer code review before merge (`/vorbit:implement:code-review`)
8. **Cleanup mocks** — generate API contracts for backend handover (`/vorbit:implement:cleanup-mocks`)

*For a full list of commands and their parameters, run `/help` in Claude Code after installation, or explore the `commands/` directory.*

## Core Workflows & Features

- **Automated Hooks**: Vorbit uses Python scripts in `hooks/` to auto-format (Biome/Prettier), validate (tsc, go build, mypy), warn before push, and manage loop modes during execution.
- **Learning System**: Vorbit captures session corrections ("wrong", "broken", "revert") using stop hooks and syncs them to local rule files. Use `/vorbit:learn:checkmemory` to process pending learnings.
- **Multi-Platform**: Primary integration is via Claude Code (Terminal). Secondary/No-terminal usage is supported via Claude Desktop app using the included `ClaudeApp/` skills.
- **Prototypes & Design**: Quickly bootstrap prototype interfaces, user journeys, and apply standard UI patterns with the design commands.

*See `CLAUDE.md` for full plugin development guidelines and deeper details on skill and hook structures.*

## Repository Layout
```text
vorbit/
├── .claude-plugin/        # Plugin manifest
├── commands/              # Slash commands (auto-discovered)
├── skills/                # Workflow logic (auto-discovered via SKILL.md)
├── hooks/                 # Hook scripts (formatting, validation, learning)
├── ClaudeApp/             # Claude.ai skills (separate platform)
├── CLAUDE.md              # Plugin development guide
├── AGENT.md               # Output style and engineering guidelines
├── dev-setup.sh           # Plugin install + cache setup
└── README.md
```

## Requirements

- Claude Code with plugin support
- Python >= 3.9 (for hook scripts)
- **MCP integrations used by workflows:**
  - **Linear** (epic, implement, verify)
  - **Notion or Anytype** (explore, prd)
  - **Figma** (journey, prototype, webflow)
  - **Webflow** (webflow)

## Testing

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all hook tests
pytest
```

## License

MIT
