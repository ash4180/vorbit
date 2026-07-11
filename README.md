# Vorbit

TDD-first product development workflows for Claude Code, Codex CLI, and Gemini CLI.

Vorbit packages four layers:
- **Commands** (`commands/`) — slash command entry points, thin dispatchers
- **Skills** (`skills/`, `codex/skills/`, `gemini/skills/`) — workflow logic per agent
- **Hooks** — formatting, validation, and push warnings
- **Core** (`vorbit_core/`) — shared configuration, rule resolution, and safe agent-asset sync

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

This syncs Vorbit skills into `~/.codex/skills/` and installs the deterministic
rule resolver at `~/.codex/bin/vorbit-resolve-rules`.

### Gemini CLI

```bash
cd /path/to/vorbit
bash scripts/sync-gemini-skills.sh
```

This syncs Vorbit skills into `~/.gemini/skills/` and installs the deterministic
rule resolver at `~/.gemini/bin/vorbit-resolve-rules`.

Both sync commands preserve user-owned entries. They only replace or prune links
recorded in Vorbit's managed-link manifest (plus legacy links into the current
Vorbit checkout). Preview or validate an installation without changing it:

```bash
bash scripts/sync-codex-skills.sh --dry-run
bash scripts/sync-codex-skills.sh --check
```

Resolve the exact ordered rule set for a project as JSON:

```bash
~/.codex/bin/vorbit-resolve-rules --agent codex --project-root /path/to/project
~/.gemini/bin/vorbit-resolve-rules --agent gemini --project-root /path/to/project
```

The output labels each rule's tier, authority, and specificity. File read order
is deterministic, but it does not let agent guidance override shared policy.

## Recommended Workflow

1. **Explore** — shape the problem until the PRD-blocking unknowns are resolved (`/vorbit:design:explore`)
2. **PRD** — write concrete user stories with acceptance criteria (`/vorbit:design:prd`)
3. **Journey** — visualize user flows in FigJam (`/vorbit:design:journey`)
4. **Epic** — convert PRD stories into Linear issues with dependency tree (`/vorbit:implement:epic`)
5. **Implement** — TDD-first coding (tests before code) (`/vorbit:implement:implement`)
6. **Verify** — validate against acceptance criteria (`/vorbit:implement:verify`)
7. **Review** — 3-layer code review before merge (`/vorbit:implement:code-review`)
8. **Cleanup mocks** — approve the API contract, integrate the real backend, then remove mocks atomically (`/vorbit:implement:cleanup-mocks`)
9. **Prepare PR** — verify, preview branch mutations, and publish the approved PR (`/vorbit:implement:prepare-pr`)

The slash-command forms above are Claude Code entry points. In Codex or Gemini, invoke the corresponding `$vorbit-*` skill or describe the same intent. For a full command list, run `/help` in Claude Code or inspect `commands/`.

## Core Features

- **Automated Hooks**: Vorbit uses Python scripts to auto-format (Biome/Prettier), validate (tsc, go build, mypy), warn before push, and manage loop modes during execution.
- **Multi-Agent**: Claude Code, Codex CLI, and Gemini CLI share workflow contracts, stable requirement IDs, and deterministic rule precedence. Agent-specific projections adapt connector and runtime details.
- **Prototypes & Design**: Quickly bootstrap prototype interfaces, user journeys, and apply standard UI patterns with the design commands.

## Repository Layout
```text
vorbit/
├── vorbit_core/               # Config, rule resolution, and safe sync
├── skills/                    # Claude Code skills
├── commands/                  # Claude Code slash commands
├── hooks/                     # Claude Code hooks
├── codex/
│   └── skills/                # Codex CLI skills
├── gemini/
│   └── skills/                # Gemini CLI skills
├── scripts/
│   ├── sync-codex-skills.sh   # Install Codex skills
│   ├── sync-gemini-skills.sh  # Install Gemini skills
│   └── vorbit-resolve-rules   # Resolve enabled rules + precedence metadata
├── tests/                     # Runtime and cross-agent skill-contract tests
├── CLAUDE.md                  # Claude Code plugin development guide
├── AGENTS.md                  # Codex CLI instructions
├── dev-setup.sh               # Claude Code plugin install
└── README.md
```

## Requirements

- Python >= 3.9
- At least one supported agent CLI: Claude Code, Codex CLI, or Gemini CLI
- **External capabilities used by workflows:**
  - **Linear** — canonical PRDs, epic trees, tracked implementation/loops, optional verification/PR updates
  - **Figma/FigJam** — Figma design work and journey diagrams; journey must load the connector's current `figma-generate-diagram` prerequisite
  - **Pencil** — token/component synchronization; optional input for prototypes and Webflow
  - **Webflow** — Webflow page, template, and component mutation
  - **GitHub CLI or equivalent authenticated GitHub tooling** — prepare-pr
  - **Notion or Anytype** — optional storage for exploration drafts only; they are not canonical PRD providers

Every mutating workflow preflights its required capability and current schema before external writes. Missing optional storage degrades to a chat/local artifact; missing required mutation capability returns a blocked status before destructive work.

## Testing

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all tests
pytest
```

## License

MIT
