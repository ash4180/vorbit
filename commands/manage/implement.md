---
description: Execute or resume tasks from tasks.md
---

## Setup

1. Read `./CLAUDE.md` and `~/.claude/CLAUDE.md` for project standards
2. Source `tools/scripts/common.sh`
3. Run `tools/scripts/task.sh setup` to validate environment

## Determine Mode

**Parse arguments** - formats: `<feature-slug>`, `<feature-slug> T001`, `<feature-slug> next`, `T001`, `next`, or no args

1. **IF `{ARGS}` is `<feature-slug>`**: Work on that feature's tasks
2. **IF `{ARGS}` is `<feature-slug> T001`**: Execute specific task from that feature
3. **IF `{ARGS}` is `<feature-slug> next`**: Execute next pending task for that feature
4. **IF `{ARGS}` is just `T001`**: Find which feature has this task, execute it
5. **IF no args or `next`**:
   - Run `tools/scripts/task.sh list` to find all tasks across features
   - If interrupted tasks found → show list, ask user which to resume
   - If pending tasks exist → show by feature, ask user which to execute
   - If nothing found → report "No tasks available"

## Execute Task

For each task (with resolved feature slug):

1. **Start**: `tools/scripts/task.sh start .vorbit/features/<slug>/tasks.md <TASK_ID>`
2. **Execute** the task step by step
3. **Complete**: `tools/scripts/task.sh complete .vorbit/features/<slug>/tasks.md <TASK_ID>`

## On Completion

- Report what was done
- Show feature context: `[<slug>]`
- **IF more tasks remain**: "Task X complete. Y tasks remaining. Run `/vorbit:manage:implement <slug> next` to continue."
- **IF all tasks complete**: "Run `/vorbit:manage:validate <slug>` to verify against acceptance criteria"

## Cross-Feature View

To see all tasks across features:
```
tools/scripts/task.sh list
```

Output shows tasks grouped by feature with progress.
