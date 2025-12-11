# Vorbit

Claude Code extension for structured, opinionated development workflows. No fluff.

## Installation

```bash
git clone https://github.com/ash4180/vorbit.git
cp -r vorbit/commands/* ~/.claude/commands/
```

## Onboarding

1. Copy commands to Claude's command directory:
   ```bash
   cp -r vorbit/commands/* ~/.claude/commands/
   ```

2. Copy `tools/` folder to your project root.

3. **(Optional)** Use Vorbit's coding standards globally:
   ```bash
   cp vorbit/AGENT.md ~/.claude/CLAUDE.md
   ```
   Copy the agent.md content to your claud.md file. This applies Vorbit's opinionated guidelines to ALL your Claude Code sessions.

4. Try `/vorbit:init:explore {idea}` to start.


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
/vorbit:init:epic "improve login flow"

# 2. Generate tasks and implement
/vorbit:manage:task improve-login-flow
And implement the task one by one.
/vorbit:manage:implement improve-login-flow T001 

# 3. Validate
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

### Script Commands
```bash
# List all features
tools/scripts/task.sh features

# List all tasks
tools/scripts/task.sh list

# Task progress
tools/scripts/task.sh start .vorbit/features/<slug>/tasks.md T001a
tools/scripts/task.sh complete .vorbit/features/<slug>/tasks.md T001a
```

## Important Note: DO NOT believe agents' output, they are not reliable. check the documentation all the time by yourself. ensure the feature is align your requirements.


## Requirements

- Claude Code

## License

MIT
