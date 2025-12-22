# Vorbit

Claude Code extension for structured, opinionated development workflows. No fluff.

## Installation

```bash
git clone https://github.com/ash4180/vorbit.git
```

## Onboarding

Make the installer executable first:
```bash
chmod +x tools/install.sh
```

### For Claude Code
```bash
# Project-local
bash tools/install.sh claude
# → .claude/commands/vorbit/ + ./CLAUDE.md

# Global (all projects)
bash tools/install.sh --global claude
# → ~/.claude/commands/vorbit/ + ~/.claude/CLAUDE.md
```
Use `--force` to overwrite existing installation.

### For Cursor
```bash
bash tools/install.sh cursor
```
Adds Vorbit rules to `.cursorrules` in your project root.

### For Gemini CLI / Antigravity IDE
```bash
# Project-local
bash tools/install.sh gemini

# Global (all projects)
bash tools/install.sh --global gemini
```
Updates `GEMINI.md` with Vorbit rules.

### Manual Installation
If you prefer manual setup:
1. Copy commands: `cp -r commands/ .claude/commands/vorbit/` (project) or `~/.claude/commands/vorbit/` (global)
2. Append `AGENT.md` to `./CLAUDE.md` (project) or `~/.claude/CLAUDE.md` (global)

### Dry Run
Preview changes without modifying anything:
```bash
bash tools/install.sh --dry-run claude
bash tools/install.sh --dry-run cursor
bash tools/install.sh --dry-run gemini
```

Try `/vorbit:init:explore {idea}` to start.


## Commands

Vorbit organizes commands into focused categories with workflow enforcement:

**Key Benefits:**
- Feature isolation: Each feature gets its own `.vorbit/features/<slug>/` directory
- Workflow enforcement: Commands check prerequisites before running
- State tracking: Progress persists in feature directories
- TDD enforcement: Tasks generated as test/implementation pairs
- Parallel execution: Tasks marked `[P]` can run simultaneously

### Init Commands - Project Initialization
Core workflow for any project:
- `/vorbit:init:explore {idea}` - Explore solutions, creates feature slug
- `/vorbit:init:prd {slug}` - Create PRD for feature
- `/vorbit:init:epic {slug}` - Create implementation plan from PRD

### Manage Commands - Project Management
Works with epic-based workflow:
- `/vorbit:manage:task {slug}` - Break epic into test/impl task pairs
- `/vorbit:manage:implement {slug}` - Execute tasks from tasks.md
- `/vorbit:manage:review {file}` - Linus-style code review
- `/vorbit:manage:validate {slug}` - Validate implementation against epic

### Learning Commands
No workflow enforcement needed:
- `/vorbit:learn:learn {topic}` - Programming lessons

## Feature Workflow

### New Feature (Full Workflow)
You can use the following commands to create a new feature with the flow, if you're working on a new feature and you don't have the tech details. rely the flow to finish the feature.

```bash
# 1. Explore (Perform as product manager or designer) 
/vorbit:init:explore {example feature}

# 2. PRD (Perform as product manager or designer) 
/vorbit:init:prd {example feature}

# 3. Epic (Perform as Tech Architect) 
/vorbit:init:epic {example feature}

# 4. Generate tasks and implement (Perform as Developer)
/vorbit:manage:task {example feature}

# 5. Implement (Ensure tasks can be one by one to implement and pass acceptance criteria)
/vorbit:manage:implement {example feature}    

# 6. Validate against acceptance criteria (QA Engineer)
/vorbit:manage:validate {example feature}
```

### Quick Feature (Skip Explore and PRD Focus on Tech Implementation)
You can use the following commands to create a new feature with the flow, if you have the tech details very well. 

```bash
# 1. Create implementation plan directly
/vorbit:init:epic improve-login-flow

# 2. Generate tasks and implement
/vorbit:manage:task improve-login-flow

# 3. Implement the task one by one.
/vorbit:manage:implement improve-login-flow T001 

# 4. Validate
/vorbit:manage:validate improve-login-flow
```

## File Structure

```
.vorbit/                         # Auto-created, gitignored
├── features/
│   ├── user-auth/               # Feature directory
│   │   ├── explore.md           # Optional exploration
│   │   ├── prd.md               # Product requirements
│   │   ├── epic.md              # Implementation plan
│   │   └── tasks.md             # Generated tasks
│   └── payment-flow/            # Another feature
└── logs/                        # Task context files
```

## Task Management

Tasks are generated in pairs (TDD style):
- `T001a`: Write tests for feature
- `T001b`: Implement feature (depends on T001a)

Tasks marked with `[P]` can run in parallel when they don't depend on each other.

### Commands

```bash
# List all features and their states
/vorbit:manage:implement features

# List all tasks across all features
/vorbit:manage:implement list

# Task progress tracking
/vorbit:manage:implement start my-feature T001
/vorbit:manage:implement complete my-feature T001
/vorbit:manage:implement fail my-feature T001

# Task context (for resuming interrupted work)
/vorbit:manage:implement save T001
/vorbit:manage:implement restore T001
/vorbit:manage:implement resumable

# Environment validation
/vorbit:manage:implement setup
```

### Data Flow Example

1. User runs: `/vorbit:manage:implement my-feature`
- Command (implement.md) tells Claude:
- Source common.sh Run task.sh setup
- Find tasks for `my-feature`
- Execute `task.sh start` / `task.sh complete`
2. Script (task.sh) executes:
- Updates tasks.md with status emoji (✅🔄❌)
- Saves context to .vorbit/logs/
- Recalculates progress percentages
3. Log stores context so if interrupted:
- `task.sh resumable` lists saved contexts
- Command `/vorbit:manage:implement my-feature restore T001` and task.sh restore T001` recovers working state

### The Workflow Chain

```
explore → prd → epic → tasks → implement → validate
   │        │      │       │         │          │
   └────────┴──────┴───────┴─────────┴──────────┘
      All write to: .vorbit/features/<slug>/
```
## Important 
DO NOT believe agents' output, they are not reliable. check the documentation all the time by yourself. ensure the feature is align your requirements.


## Requirements

Claude Code


## License

MIT
