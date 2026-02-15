---
description: Process unprocessed corrections and route learnings to project knowledge files
argument-hint: "[optional: approve all | item numbers]"
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

Use the **learn** skill in digest processing mode.

1. Read `~/.claude/rules/unprocessed-corrections.md`
2. If the file does not exist → output "Nothing to process." and stop
3. Follow the skill's Digest Processing steps to classify, present, route, and clean up

**Input:** $ARGUMENTS
