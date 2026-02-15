# Vorbit

TDD-first product development workflows for Claude Code, with strong PRD -> Epic -> Implement traceability.

Vorbit packages three layers:
- Slash commands (`commands/`) for task entry points
- Skills (`skills/*/SKILL.md`) for workflow logic
- Hooks (`hooks/hooks.json`) for automatic formatting, validation, loop control, and learning capture

## Installation

### Marketplace
```bash
/install-plugin vorbit
```

### Local Development
```bash
git clone https://github.com/ash4180/vorbit.git
claude --plugin-dir /path/to/vorbit
```

Use `--plugin-dir` for local development so command/skill/hook changes are picked up live.

## Command Reference

### Design
| Purpose | Command | Input |
|---|---|---|
| Explore ideas | `/vorbit:design:explore [topic]` | Problem/topic |
| Create PRD | `/vorbit:design:prd [feature]` | Feature description or URL |
| Create user journey diagram | `/vorbit:design:journey [feature or PRD]` | Feature name or PRD reference |
| Build UI prototype | `/vorbit:design:prototype [feature or URL]` | Feature, PRD URL, or Figma URL |
| Apply UI constraints | `/vorbit:design:ui-patterns [component]` | Component/feature |
| Develop in Webflow | `/vorbit:design:webflow [figma-url or description]` | Figma URL or requirements |

### Implement
| Purpose | Command | Input |
|---|---|---|
| Create Linear epic + sub-issues | `/vorbit:implement:epic [feature or PRD]` | Feature or PRD reference |
| Implement from issue/description | `/vorbit:implement:implement [issue] [--loop] [--cancel]` | Linear issue ID/URL or description |
| Verify implementation | `/vorbit:implement:verify [issue or feature]` | Linear issue ID/URL or feature |
| Review code or PR | `/vorbit:implement:code-review [files or --pr base-branch]` | Paths or PR base |
| Cleanup mocks for backend handover | `/vorbit:implement:cleanup-mocks [feature or all]` | Feature name / `all` |

### Learn
| Purpose | Command | Input |
|---|---|---|
| Review pending learnings | `/vorbit:learn:checkmemory [optional options]` | Optional approval args |
| Backfill learnings from past sessions | `/vorbit:learn:backfill [N]` | Number of sessions |

## Recommended Workflow

1. Explore and shape the problem (`explore`)
2. Write PRD with concrete user stories and acceptance criteria (`prd`)
3. Create journey/flow visualization (`journey`)
4. Convert PRD stories into actionable Linear work (`epic`)
5. Implement with TDD (`implement`)
6. Validate against acceptance criteria (`verify`)
7. Run review before merge (`code-review`)
8. Cleanup mocks and generate API handover contract when needed (`cleanup-mocks`)

## Current Skill Set

| Skill | Version | Purpose |
|---|---|---|
| explore | 1.1.0 | Lightweight exploration before PRD |
| prd | 1.1.0 | Structured PRD creation and saving |
| journey | 1.1.0 | User journey diagrams in FigJam |
| prototype | 1.1.0 | UI prototypes with mock data |
| webflow | 1.1.0 | Webflow page/template/component development |
| ui-patterns | 1.0.0 | UI constraints from ui-skills.com |
| epic | 1.3.0 | PRD -> Linear epic/sub-issue planning |
| implement | 1.3.0 | TDD implementation workflow |
| implement-loop | 1.0.0 | Loop-mode autonomous iteration |
| implement-cleanup-mocks | 1.0.0 | Mock cleanup + API contract generation |
| verify | 1.1.0 | Acceptance verification + quality checks |
| review | 2.0.0 | File-mode and PR-mode code review |
| learn | 7.0.0 | Correction capture and digest processing |
| ux | 1.0.0 | UX clarification and requirement precision |
| react-best-practices | 1.0.0 | React/Next.js performance guidance |

## Hook Automation

Configured in `hooks/hooks.json`:

| Hook Event | Script | Behavior |
|---|---|---|
| `PostToolUse` (`Edit`) | `hooks/scripts/post-edit-format.sh` | Auto-format edited files (Biome > Prettier) |
| `PostToolUse` (`Edit`) | `hooks/scripts/post-edit-validate.sh` | Language-aware validation (`tsc`, `mypy/pyright`, `go build`) |
| `PreToolUse` (`Bash`) | `hooks/scripts/pre-push-warning.sh` | Warn on `git push` commands |
| `Stop` | `hooks/scripts/loop-controller.sh` | Loop-mode state and iteration control |
| `Stop` | `hooks/scripts/stop-learn-reflect.sh` | Learning reflection bootstrap |
| `Stop` | `hooks/scripts/stop-console-log-audit.sh` | Debug statement audit |

## Mock Cleanup and API Handover

`implement-cleanup-mocks` supports frontend -> backend transition:
- Finds and removes mock data usage
- Generates API contract documentation
- Writes contract output to knowledge platform
- Leaves implementation handover notes

Mock runtime state:
- `.claude/mock-registry.json`

## Repository Layout

```text
.claude-plugin/plugin.json      # Plugin manifest
commands/                       # Slash command entry points
  design/
  implement/
  learn/
skills/                         # Skill logic (SKILL.md)
  _shared/                      # Shared platform detection blocks
  explore/
  prd/
  journey/
  prototype/
  webflow/
  ui-patterns/
  epic/
  implement/
  implement-loop/
  implement-cleanup-mocks/
  verify/
  review/
  learn/
  ux/
  react-best-practices/
hooks/
  hooks.json                    # Hook wiring
  scripts/                      # Hook scripts
  tests/                        # Hook script tests
CLAUDE.md                       # Project usage notes
AGENT.md                        # Output and engineering guidelines
```

## Requirements

- Claude Code plugin support
- MCP integrations used by workflows:
  - Linear MCP
  - Notion MCP or Anytype MCP
  - Figma MCP (for journey/prototype/webflow flows)
  - Webflow MCP (for webflow command)
- Shell tooling used by hooks/scripts (`bash`, `jq`, git tooling)

## Testing Hook Scripts

```bash
bash hooks/tests/test-post-edit-format.sh
bash hooks/tests/test-post-edit-validate.sh
bash hooks/tests/test-pre-push-warning.sh
bash hooks/tests/test-stop-console-log-audit.sh
bash hooks/tests/test-stop-learn-reflect.sh
```

## License

MIT
