---
description: Execute tasks from the branch epic plan or Linear, or implement from description
argument-hint: [spec task/story ID, Linear issue ID, ticket branch name, or feature description] [--worktree] [--loop] [--cancel]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, Agent, SendMessage, mcp__plugin_linear_linear__*, Skill, ToolSearch
---

Use the **implement** skill.

Delegate each selected task to **vorbit:implement-worker** using the skill's prepare/resume handoff. The parent owns review, task status, and loop progress. One worker writes at a time.

**Input:** $ARGUMENTS
