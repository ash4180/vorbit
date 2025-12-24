# Vorbit

Claude Code plugin for structured development workflows. Notion-first, Linear-integrated.

## Installation

```bash
# Clone and install as plugin
git clone https://github.com/ash4180/vorbit.git
cd vorbit

# Option 1: Use as plugin (recommended)
# Copy .claude-plugin/ to make it a valid plugin

# Option 2: Copy commands to Claude's command directory
mkdir -p ~/.claude/commands/vorbit && cp -r commands/* ~/.claude/commands/vorbit/
```

## Architecture

**Notion** = Source of truth for documentation (PRDs, user flows, explorations)
**Linear** = Issue tracking (parent + sub-issues)
**Code** = Prototypes and implementation

## Commands

Jump in at any step. No strict prerequisites.

### Design Commands

| Command | Purpose |
|---------|---------|
| `/vorbit:design:explore [topic]` | Explore ideas, save to Notion |
| `/vorbit:design:prd [feature]` | Create PRD in Notion |
| `/vorbit:design:journey [feature]` | Create user flow diagram in Notion |
| `/vorbit:design:prototype [feature]` | Generate UI prototype fast |

### Implement Commands

| Command | Purpose |
|---------|---------|
| `/vorbit:implement:epic [feature]` | Create parent issue + sub-issues in Linear |
| `/vorbit:implement:implement [issue]` | Implement from Linear issue (supports parallel execution) |
| `/vorbit:implement:verify [issue]` | Verify tests pass and acceptance criteria met |
| `/vorbit:implement:review [file]` | Linus-style code review |


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

## Skills

Vorbit includes skills for consistent agent output:

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| **explore-schema** | Exploration structure | Context questions, options analysis, recommendations |
| **prd-schema** | PRD structure for Notion | RICE prioritization, JSON schema, Notion mapping |
| **user-flow-schema** | User flow diagrams | Mermaid patterns, step types, validation rules |
| **epic-schema** | Linear issue structure | Parent + sub-issues, PRD mapping, priority |
| **prototype-patterns** | Fast UI prototypes | Framework detection, mock data strategies |

Each skill follows Claude Code patterns:
```
skills/skill-name/
├── SKILL.md          # Core definition (lean)
├── references/       # Detailed guides
├── examples/         # Valid/invalid examples
└── scripts/          # Helper scripts (optional)
```

## Agents

- **output-validator** - Validates output before saving to Notion/Linear

## Notion Integration

Commands ask where to save (database name, page URL, or skip):
- PRDs, explorations, and flows saved to user-specified location
- If database has `Type` property, sets appropriate type (PRD, Flow Research, Document)

## Linear Integration

- Detects team's existing setup (labels, states, projects)
- Creates parent issue + sub-issues (using `parentId`)
- `[P]` marked sub-issues can run in parallel
- Adapts to team's conventions, doesn't impose new patterns

## Requirements

- Claude Code
- Notion MCP (for Notion integration)
- Linear MCP (for Linear integration)

## License

MIT
