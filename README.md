# Vorbit

TDD-first product development workflows for Claude Code, Codex CLI, and Gemini CLI — with shared multi-agent learning.

Vorbit packages three layers:
- **Commands** (`commands/`) — slash command entry points, thin dispatchers
- **Skills** (`skills/`, `codex/skills/`, `gemini/skills/`) — workflow logic per agent
- **Hooks** — automatic correction capture and learning across all agents
- **Core** (`vorbit_core/`) — shared Python library for config, learning, and rule management

## Installation

### Prerequisites
- Python >= 3.9 (required for hook scripts and vorbit_core)

### Claude Code

```bash
git clone https://github.com/ash4180/vorbit.git
cd vorbit
bash dev-setup.sh
```

Restart your Claude Code session after running the setup script.

### Codex CLI

```bash
cd /path/to/vorbit
bash scripts/sync-codex-skills.sh
```

This syncs Vorbit skills into `~/.codex/skills/` and installs the stop hook for automatic correction capture.

### Gemini CLI

```bash
cd /path/to/vorbit
bash scripts/sync-gemini-skills.sh
```

This syncs Vorbit skills into `~/.gemini/skills/` and installs the session end hook for automatic correction capture.

### Obsidian Export (optional, all agents)

To write correction notes to your Obsidian vault, add to `~/.vorbit/config.toml`:

```toml
[exporters.obsidian]
enabled = true
vault_path = "/path/to/your/obsidian/vault"
```

Each agent writes to its own subfolder: `claude/`, `codex/`, `gemini/`.

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

## Core Features

- **Automated Hooks**: Vorbit uses Python scripts to auto-format (Biome/Prettier), validate (tsc, go build, mypy), warn before push, and manage loop modes during execution.
- **Learning System**: Vorbit captures session corrections ("wrong", "broken", "revert") via stop hooks and writes them to the canonical store. Use `python3 scripts/vorbit-learning.py pending` to review.
- **Canonical Multi-Agent Store**: Captures, pending review items, and durable rules live in a configurable store (`VORBIT_HOME`, then `~/.vorbit/config.toml`, then `~/.vorbit`). Agent-specific compatibility bridges (Claude `~/.claude/rules/`, Obsidian export) are generated from that store.
- **Multi-Agent**: Claude Code, Codex CLI, and Gemini CLI share the same learning store. Each agent has its own skills, hooks, and rule projections — but learnings flow across all agents after review.
- **Prototypes & Design**: Quickly bootstrap prototype interfaces, user journeys, and apply standard UI patterns with the design commands.

## Learning System

When you correct any agent ("wrong", "broken", "revert"), Vorbit captures the correction and creates a pending review item. No correction becomes a durable rule without human approval.

```bash
# List pending learnings
python3 scripts/vorbit-learning.py pending --project-root .

# Approve a learning
python3 scripts/vorbit-learning.py approve <review-id> --approved-by <name>

# Reject a learning
python3 scripts/vorbit-learning.py reject <review-id> --reason "<why>"

# View rules for a specific agent
python3 scripts/vorbit-learning.py rules --agent claude
python3 scripts/vorbit-learning.py rules --agent codex
python3 scripts/vorbit-learning.py rules --agent gemini
```

## Repository Layout
```text
vorbit/
├── vorbit_core/               # Shared Python library (config, learning, rules)
├── skills/                    # Claude Code skills
├── commands/                  # Claude Code slash commands
├── hooks/                     # Claude Code hooks
├── codex/
│   ├── skills/                # Codex CLI skills
│   └── hooks.json             # Codex hook config reference
├── gemini/
│   ├── skills/                # Gemini CLI skills
│   └── hooks-settings.json    # Gemini hook config reference
├── scripts/
│   ├── hooks/                 # Hook wrappers for Codex and Gemini
│   ├── sync-codex-skills.sh   # Install Codex skills + hooks
│   ├── sync-gemini-skills.sh  # Install Gemini skills
│   ├── vorbit-codex-cli.py    # Manual Codex transcript capture
│   ├── vorbit-gemini-cli.py   # Manual Gemini transcript capture
│   └── vorbit-learning.py     # Review CLI (approve/reject/list)
├── tests/                     # Tests for vorbit_core
├── CLAUDE.md                  # Claude Code plugin development guide
├── AGENTS.md                  # Codex CLI instructions
├── dev-setup.sh               # Claude Code plugin install
└── README.md
```

## Requirements

- Python >= 3.9
- At least one supported agent CLI: Claude Code, Codex CLI, or Gemini CLI
- **MCP integrations used by workflows:**
  - **Linear** (epic, implement, verify)
  - **Notion or Anytype** (explore, prd)
  - **Figma** (journey, prototype, webflow)
  - **Webflow** (webflow)

## Testing

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all tests
pytest
```

## License

MIT
