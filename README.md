# Vorbit

TDD-first product development workflows for Claude Code, Codex CLI, and Gemini CLI.

Vorbit packages three layers:
- **Commands** (`commands/`) — slash command entry points, thin dispatchers
- **Skills** (`skills/`, `codex/skills/`, `gemini/skills/`) — workflow logic per agent
- **Hooks** — formatting, validation, and push warnings

## Installation

### Prerequisites
- Python >= 3.9 (required for hook scripts)

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

This syncs Vorbit skills into `~/.codex/skills/`.

### Gemini CLI

```bash
cd /path/to/vorbit
bash scripts/sync-gemini-skills.sh
```

This syncs Vorbit skills into `~/.gemini/skills/`.

## Recommended Workflow

1. **Explore** — shape the problem with 10+ questions (`/vorbit:design:explore`)
2. **PRD** — write concrete user stories with acceptance criteria (`/vorbit:design:prd`)
3. **Journey** — visualize user flows in FigJam (`/vorbit:design:journey`)
4. **Design mockups** — build library-bound screens in Pencil or Figma. The Figma path checks linked libraries first and binds writes to real component keys / variable IDs, not invented primitives (`/vorbit:design:pencil`, `/vorbit:design:figma`)
5. **Epic** — convert PRD stories into Linear issues with dependency tree (`/vorbit:implement:epic`)
6. **Implement** — TDD-first coding (tests before code) (`/vorbit:implement:implement`)
7. **Verify** — validate against acceptance criteria (`/vorbit:implement:verify`)
8. **Review** — 3-layer code review before merge (`/vorbit:implement:code-review`)
9. **Cleanup mocks** — generate API contracts for backend handover (`/vorbit:implement:cleanup-mocks`)

*For a full list of commands and their parameters, run `/help` in Claude Code after installation, or explore the `commands/` directory.*

## Core Features

- **Automated Hooks**: Vorbit uses Python scripts to auto-format (Biome/Prettier), validate (tsc, go build, mypy), warn before push, and manage loop modes during execution.
- **Multi-Agent**: Claude Code, Codex CLI, and Gemini CLI share the same skill set. Each agent has its own skills and rule projections under `codex/` and `gemini/`.
- **Prototypes & Design**: Bootstrap prototypes, FigJam journeys, and library-bound design mockups with the design commands (`pencil`, `figma`, `journey`, `prototype`, `webflow`). The `figma` skill loads the Figma MCP's MANDATORY companion skills (`figma-use`, `figma-generate-design`) and discovers linked libraries before drawing, so generated frames are real component instances — not orphan rectangles.

## Repository Layout
```text
vorbit/
├── skills/                            # Claude Code skills
│   └── _shared/
│       ├── mcp-tool-routing.md        # Shared MCP routing reference
│       └── design-knowledge/          # Adapted design references (see Credits)
│           ├── references/            # Aesthetic, visual, UX strategy guides
│           ├── LICENSE
│           └── ATTRIBUTIONS.md
├── commands/                          # Claude Code slash commands
├── hooks/                             # Claude Code hooks (scripts + tests)
├── codex/
│   └── skills/                        # Codex CLI skills
├── gemini/
│   └── skills/                        # Gemini CLI skills
├── scripts/
│   ├── sync-codex-skills.sh           # Install Codex skills
│   └── sync-gemini-skills.sh          # Install Gemini skills
├── CLAUDE.md                          # Claude Code plugin development guide
├── AGENTS.md                          # Codex CLI instructions
├── dev-setup.sh                       # Claude Code plugin install
└── README.md
```

## Requirements

- Python >= 3.9
- At least one supported agent CLI: Claude Code, Codex CLI, or Gemini CLI
- **MCP integrations used by workflows:**
  - **Linear** (epic, implement, verify, prd)
  - **Notion or Anytype** (explore)
  - **Figma** (figma, journey, prototype, webflow)
  - **Pencil** (pencil)
  - **Webflow** (webflow)
  - **Mobbin** (optional — figma and pencil pull real-world UI references when connected)

## Credits

Some design knowledge in `skills/_shared/design-knowledge/` is adapted from [design-expert-skill](https://github.com/Opikat/design-expert-skill) by Ekaterina Pykhova, used under the MIT License. See `skills/_shared/design-knowledge/LICENSE` and `ATTRIBUTIONS.md` for full terms.

## License

MIT
