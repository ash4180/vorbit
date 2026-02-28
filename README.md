# Vorbit

TDD-first product development workflows for Claude Code, with strong PRD → Epic → Implement traceability.

Vorbit packages three layers:
- **Commands** (`commands/`) — slash command entry points, thin dispatchers
- **Skills** (`skills/*/SKILL.md`) — workflow logic with multi-step decision trees
- **Hooks** (`hooks/hooks.json`) — automatic formatting, validation, loop control, and learning capture

## Installation

### Marketplace
```bash
/install-plugin vorbit
```

### Local Development
```bash
git clone https://github.com/ash4180/vorbit.git
cd vorbit && bash dev-setup.sh
```

`dev-setup.sh` creates a local marketplace, installs the plugin, and sets up the cache directory with symlinked contents for live editing. Restart Claude Code after running.

## Command Reference

### Design
| Purpose | Command | Input |
|---|---|---|
| Explore ideas | `/vorbit:design:explore [topic]` | Problem or topic |
| Create PRD | `/vorbit:design:prd [feature]` | Feature description or URL |
| Create user journey diagram | `/vorbit:design:journey [feature or PRD]` | Feature name or PRD reference |
| Build UI prototype | `/vorbit:design:prototype [feature or URL]` | Feature, PRD URL, or Figma URL |
| Apply UI constraints | `/vorbit:design:ui-patterns [component]` | Component or feature |
| Develop in Webflow | `/vorbit:design:webflow [figma-url or description]` | Figma URL or requirements |

### Implement
| Purpose | Command | Input |
|---|---|---|
| Create Linear epic + sub-issues | `/vorbit:implement:epic [feature or PRD]` | Feature or PRD reference |
| Implement from issue/description | `/vorbit:implement:implement [issue] [--loop] [--cancel]` | Linear issue ID/URL or description |
| Verify implementation | `/vorbit:implement:verify [issue or feature]` | Linear issue ID/URL or feature |
| Review code or PR | `/vorbit:implement:code-review [files or --pr base-branch]` | Paths or PR base |
| Cleanup mocks for backend handover | `/vorbit:implement:cleanup-mocks [feature or all]` | Feature name or `all` |

### Learn
| Purpose | Command | Input |
|---|---|---|
| Review pending learnings | `/vorbit:learn:checkmemory` | None |

## Recommended Workflow

1. **Explore** — shape the problem with 10+ questions
2. **PRD** — write concrete user stories with acceptance criteria (AC-* IDs)
3. **Journey** — visualize user flows in FigJam
4. **Epic** — convert PRD stories into Linear issues with dependency tree
5. **Implement** — TDD-first coding (tests before code)
6. **Verify** — validate against acceptance criteria
7. **Review** — 3-layer code review before merge
8. **Cleanup mocks** — generate API contracts for backend handover

## Skills

| Skill | Version | Purpose |
|---|---|---|
| explore | 1.1.0 | Lightweight exploration before PRD |
| prd | 1.2.2 | Structured PRD creation and saving |
| journey | 1.1.0 | User journey diagrams in FigJam |
| prototype | 1.1.0 | UI prototypes with mock data |
| webflow | 1.1.0 | Webflow page/template/component development |
| ui-patterns | 1.0.0 | UI constraints from ui-skills.com |
| epic | 1.4.2 | PRD → Linear epic/sub-issue planning |
| implement | 1.3.0 | TDD implementation workflow |
| implement-loop | 1.0.0 | Loop-mode autonomous iteration |
| implement-cleanup-mocks | 1.0.0 | Mock cleanup + API contract generation |
| verify | 1.1.0 | Acceptance verification + quality checks |
| review | 2.0.0 | File-mode and PR-mode code review |
| learn | 7.0.0 | Correction capture and digest processing |
| ux | 1.0.0 | UX clarification and requirement precision |
| react-best-practices | 1.0.0 | React/Next.js performance guidance (reference skill, no command) |

## Hook Automation

All hooks are Python scripts, configured in `hooks/hooks.json`:

| Hook Event | Script | Behavior |
|---|---|---|
| `PostToolUse` (Edit) | `hooks/scripts/post_edit_format.py` | Auto-format edited files (biome > prettier) |
| `PostToolUse` (Edit) | `hooks/scripts/post_edit_validate.py` | Language-aware validation (tsc, mypy/pyright, go build) |
| `PreToolUse` (Bash) | `hooks/scripts/pre_push_warning.py` | Warn on `git push` commands |
| `Stop` | `skills/implement-loop/hooks/loop_controller.py` | Loop-mode state and iteration control |
| `Stop` | `skills/learn/hooks/stop_learn_reflect.py` | Correction and voluntary keyword capture |

Stop hooks co-locate with their parent skill. General-purpose hooks live in `hooks/scripts/`.

## Learning System

Vorbit captures mistakes and learnings across sessions:

1. **Stop hook** (`stop_learn_reflect.py`) scans each session transcript for correction keywords ("wrong", "broken", "revert") and voluntary keywords ("remember this", "save this")
2. Detected keywords are written to `~/.claude/rules/pending-capture.md`
3. Next session, `/vorbit:learn:checkmemory` classifies each capture (root cause type + destination) and routes it to permanent rules files after user confirmation

Root cause types: `claude-md`, `knowledge`, `skill`, `script`, `agent-mistake`, `user-preference`, `tool-behavior`, `general`

## Multi-Platform

| Platform | Location | Status | Use when |
|---|---|---|---|
| Claude Code | `commands/`, `skills/`, `hooks/` | Primary | Terminal or via `claude remote-control` from Desktop/mobile |
| Claude.ai / Desktop | `ClaudeApp/` | Secondary | Using Claude Desktop app directly (no terminal session) |
| Google Antigravity | `.agent/workflows/` | Planned | Gemini workflows |

Each platform has independent implementations — no shared execution layer.

### Claude Code (Terminal)

The full plugin: 12 commands, 15 skills, 5 hooks, MCP integrations. Also accessible from Claude Desktop or mobile via [`claude remote-control`](https://code.claude.com/docs/en/desktop).

### Claude.ai / Desktop (No Terminal)

For users who open Claude Desktop directly without a terminal session. `ClaudeApp/` provides 4 skills (explore, epic, prd, writing) as Claude.ai project skills. These are simplified versions — no hook automation, no MCP routing, no loop mode. Configure them as project knowledge in your Claude.ai project.

## Repository Layout

```text
vorbit/
├── .claude-plugin/
│   └── plugin.json                         # Plugin manifest
├── commands/                               # Slash commands (auto-discovered)
│   ├── design/                             # explore, journey, prd, prototype, ui-patterns, webflow
│   ├── implement/                          # cleanup-mocks, code-review, epic, implement, verify
│   └── learn/                              # checkmemory
├── skills/                                 # Workflow logic (auto-discovered via SKILL.md)
│   ├── _shared/
│   │   └── mcp-tool-routing.md             # MCP platform detection rules
│   ├── epic/
│   ├── explore/
│   ├── implement/
│   ├── implement-cleanup-mocks/
│   ├── implement-loop/
│   │   └── hooks/
│   │       └── loop_controller.py          # Stop hook: loop state management
│   ├── journey/
│   ├── learn/
│   │   ├── hooks/
│   │   │   ├── stop_learn_reflect.py       # Stop hook: keyword capture
│   │   │   └── mark_voluntary_seen.py      # Dedup helper
│   │   ├── references/                     # format.md, routing.md, consolidation.md
│   │   └── vorbit-learning-rules.md        # Symlinked → ~/.claude/rules/
│   ├── prd/
│   ├── prototype/
│   ├── react-best-practices/
│   │   └── references/rules/               # 40+ categorized rule files
│   ├── review/
│   │   └── references/pr-pipeline.md
│   ├── ui-patterns/
│   ├── ux/
│   │   └── references/                     # question-matrix, edge-case-catalog, ux-philosophy
│   ├── verify/
│   └── webflow/
│       ├── examples/
│       └── references/                     # component-mapping, mcp-tools, templates
├── hooks/
│   ├── hooks.json                          # Hook event wiring
│   ├── scripts/                            # Python hook scripts
│   │   ├── _utils.py                       # Shared utilities (project root, input parsing)
│   │   ├── post_edit_format.py
│   │   ├── post_edit_validate.py
│   │   └── pre_push_warning.py
│   └── tests/                              # pytest test harnesses
│       ├── conftest.py
│       ├── test_post_edit_format.py
│       ├── test_post_edit_validate.py
│       ├── test_pre_push_warning.py
│       ├── test_loop_controller.py
│       ├── test_stop_learn_reflect.py
│       └── test_e2e_stop_learn_reflect.py
├── ClaudeApp/                              # Claude.ai skills (separate platform)
│   ├── epic/
│   ├── explore/
│   ├── prd/
│   └── writing/
├── CLAUDE.md                               # Plugin development guide
├── AGENT.md                                # Output style and engineering guidelines
├── dev-setup.sh                            # Plugin install + cache setup
├── pyproject.toml                          # pytest config
└── README.md
```

## Requirements

- Claude Code with plugin support
- Python >= 3.9 (for hook scripts)
- MCP integrations used by workflows:
  - **Linear** — epic, implement, verify
  - **Notion or Anytype** — explore, prd
  - **Figma** — journey, prototype, webflow
  - **Webflow** — webflow

## Testing

```bash
# Run all hook tests
pytest

# Run a specific test
pytest hooks/tests/test_post_edit_format.py

# Install dev dependencies first
pip install -e ".[dev]"
```

## License

MIT
