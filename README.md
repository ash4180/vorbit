# Vorbit

TDD-first product development workflows for Claude Code, Codex CLI, and Gemini CLI.

Vorbit packages four layers:
- **Commands** (`commands/`): slash command entry points, thin dispatchers
- **Skills** (`skills/`, `codex/skills/`, `gemini/skills/`): `skills/` is the single authored source. Codex and Gemini workflow files are generated from it (see "Editing Skills" below)
- **Hooks** (`hooks/`): formatting, type checks, push warnings, ADHD output mode, and loop mode
- **Core** (`vorbit_core/`): shared configuration, rule resolution, skill projection, and safe agent-asset sync

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
bash scripts/setup-codex.sh
```

This installs Vorbit skills, the deterministic rule resolver, and GitHub MCP.
GitHub MCP reads each repository's `origin` owner and uses the matching account
already saved by `gh auth login`. No GitHub token is stored by Vorbit.

To sync only skills and managed helper links, run:

```bash
bash scripts/sync-codex-skills.sh
```

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

### Shared rules for Codex and Gemini

`rules/universal/` holds versioned copies of the rules Codex and Gemini read from
`~/.vorbit/rules/` at run time (plain-language output, writing rules). Install or
update them on a machine:

```bash
mkdir -p ~/.vorbit/rules/universal
cp rules/universal/*.md ~/.vorbit/rules/universal/
```

Claude Code reads `.claude/rules/` in each project instead.

## Recommended Workflow

Every step reads and writes the `.vorbit/` folder of the repo you work in (see "Spec Files" below).

**Design**
1. **Explore**: research real apps first (Mobbin and web search), then ask the open questions. Saves a dated research file and a visual solution page (`/vorbit:design:explore`)
2. **PRD**: write user stories with acceptance criteria to `.vorbit/prd.md` (`/vorbit:design:prd`)
3. **Journey**: draw the user flows in FigJam (`/vorbit:design:journey`)
4. **Figma**: sync the design system, or build Figma screens from the PRD (`/vorbit:design:figma`)

**Build**
5. **Epic**: turn the PRD into an ordered task plan in `.vorbit/epic.md` (`/vorbit:implement:epic`)
6. **Ticket**: post one short summary ticket per story to Linear (`/vorbit:ticket`)
7. **Implement**: TDD-first coding, one task or story at a time. Add `--loop` to work through the whole queue (`/vorbit:implement:implement`)
8. **Review**: read-only code review with severity-ranked findings. Bugs the branch did not cause become follow-ups (`/vorbit:implement:code-review`)
9. **Cleanup mocks**: approve the API contract, integrate the real backend, then remove the mocks (`/vorbit:implement:cleanup-mocks`)

**Test and ship**
10. **QA plan**: write a human-runnable test plan to `.vorbit/qa-plan.md` (`/vorbit:implement:qa-plan`)
11. **QA report**: run the checks, save a screenshot per check, write a dated `.vorbit/qa-report.md` with a ready or not-ready verdict (`/vorbit:implement:qa-report`)
12. **Prepare PR**: rebase, run the CI checks locally, push, open the PR, update Linear (`/vorbit:implement:prepare-pr`)
13. **Tutorial**: write the user-facing how-to for the feature (`/vorbit:implement:tutorial`)

**Helpers at any point**
- `/vorbit:design:prototype`: a working front-end prototype with mock data
- `/vorbit:design:ui-patterns`: constraints for accessible, fast interfaces
- `/vorbit:design:webflow`: Webflow pages, templates, CMS structure, and components
- `/vorbit:teach`: turn the last technical answer into plain language, or teach one word
- Skills with no command, loaded by intent: `adhd` (plain-language output mode), `ux` (deep UX questioning), `react-best-practices`, `implement-loop`

The slash-command forms above are Claude Code entry points. In Codex or Gemini, invoke the corresponding `$vorbit-*` skill or describe the same intent. For a full command list, run `/help` in Claude Code or inspect `commands/`.

## Spec Files

Skills write their documents into `<repo>/.vorbit/`, inside the worktree you work in. The folder is gitignored. Vorbit adds the `.vorbit/` line to your `.gitignore` when it is missing and leaves that change uncommitted.

| Path | Written by | Holds |
|------|------------|-------|
| `prd.md` | prd | user stories, acceptance criteria, flows, constraints, success criteria |
| `epic.md` | epic | one section per story, ordered tasks with IDs and status |
| `qa-plan.md` | qa-plan | human-runnable checklist. The tester ticks each check |
| `qa-report.md` | qa-report | dated run history, newest first, with a verdict |
| `qa-screenshots/<date>/` | qa-report | one picture per check it ran |
| `explore/<date>-<topic>.md` and `.html` | explore | dated research, its visual solution page, and a `-refs/` folder of reference pictures |

Rules:
- The spec files are the source of truth. Linear holds only the short summaries posted by the ticket skill.
- Every file records its branch in a `Branch:` line. A mismatch stops the skill instead of mixing branches.
- Files stay in the worktree where they were written. Run the whole chain in one worktree.
- Deleting the worktree deletes its specs. The Linear summaries are the only durable copy.

## Core Features

- **Hooks (Claude Code)**: Python scripts run after each edit (auto-format with Biome or Prettier; advisory type checks with tsc, mypy, pyright, or go build that report errors but never block an edit), before a push (warning), and on session start (ADHD output mode when `~/.claude/.vorbit-adhd-always` exists). A Stop hook drives implement loop mode from a state file.
- **Multi-agent**: Claude Code, Codex CLI, and Gemini CLI share workflow contracts, stable requirement IDs, and deterministic rule precedence. Agent-specific projections adapt connector and runtime details.
- **Plain-language output**: the `adhd` skill reshapes every reply for a short attention span. `/vorbit:teach` explains the last answer in simple words. The writing rules in `rules/universal/` apply to tickets, PRs, and chat messages too.
- **Design**: prototypes, FigJam journeys, Figma screens, Webflow pages, and UI patterns from one set of commands.

## Repository Layout
```text
vorbit/
├── .claude-plugin/plugin.json # Claude Code plugin manifest
├── vorbit_core/               # Config, rule resolution, skill projection, GitHub MCP, safe sync
├── skills/                    # Canonical skills (single authored source)
│   └── _shared/               # Contracts and knowledge every skill reads
├── commands/                  # Claude Code slash commands (design/, implement/, teach, ticket)
├── hooks/                     # Claude Code hooks (hooks.json + scripts/)
├── rules/                     # Versioned copies of shared rules for ~/.vorbit/rules/ (Codex, Gemini)
├── codex/skills/              # Codex CLI skills (workflows GENERATED from skills/)
├── gemini/skills/             # Gemini CLI skills (workflows GENERATED from skills/)
├── ClaudeApp/                 # Hand-maintained upload copies for the Claude desktop app
├── scripts/
│   ├── setup-codex.sh         # Install Codex skills and GitHub MCP
│   ├── sync-codex-skills.sh   # Install Codex skills
│   ├── sync-gemini-skills.sh  # Install Gemini skills
│   ├── sync-agent-assets.py   # Safe managed-link sync used by the two sync scripts
│   ├── vorbit-github-mcp      # Account-aware GitHub MCP launcher
│   └── vorbit-resolve-rules   # Resolve enabled rules + precedence metadata
├── tests/                     # Runtime and cross-agent skill-contract tests
├── pyproject.toml             # Python package and dev dependencies
├── AGENTS.md                  # Codex CLI instructions
├── dev-setup.sh               # Claude Code plugin install
└── README.md
```

## Requirements

- Python >= 3.9
- At least one supported agent CLI: Claude Code, Codex CLI, or Gemini CLI
- **External capabilities used by workflows:**
  - **Mobbin MCP and web search**: explore research. Explore stops and asks when Mobbin is not connected
  - **Linear**: optional summary tickets (ticket), task status for implement and loops, PR status updates, follow-up checks in review and qa-report. Spec files stay canonical
  - **Figma/FigJam**: Figma design work and journey diagrams. Journey must load the connector's current `figma-generate-diagram` prerequisite
  - **Webflow**: Webflow page, template, and component mutation
  - **GitHub CLI or equivalent authenticated GitHub tooling**: prepare-pr
  - **Playwright or a browser-automation MCP**: qa-report runs the automated checks and clicks through manual ones
  - **Slack**: optional. qa-report searches prior discussion before it suggests a follow-up ticket
  - **Notion or Anytype**: optional copies of exploration docs, QA reports, and tutorials. They are not canonical PRD providers

Every mutating workflow preflights its required capability and current schema before external writes. Missing optional storage degrades to a chat/local artifact; missing required mutation capability returns a blocked status before destructive work.

## Editing Skills

`skills/<name>/SKILL.md` is the single source of truth. After editing a canonical
skill, regenerate the Codex/Gemini projections. Never edit the generated files
under `<agent>/skills/vorbit-shared/workflows/` or the mirrored asset directories:

```bash
python3 -m vorbit_core.project_skills --write   # regenerate
python3 -m vorbit_core.project_skills --check   # exit 1 if anything is stale
```

Two things are synced by hand:
- The `description` line in `codex/skills/vorbit-<name>/SKILL.md` and `gemini/skills/vorbit-<name>/SKILL.md`. `pytest` (`test_agent_skill_sets_and_descriptions_stay_in_sync`) fails when they drift.
- The `ClaudeApp/` upload copies.

`pytest` fails (`test_projected_outputs_are_fresh`) when a canonical edit lands
without regeneration. The only hand-written agent workflow is `implement-loop.md`.
Its Claude implementation depends on a Stop hook other runtimes do not have.

## Testing

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all tests
pytest
```

## License

MIT
