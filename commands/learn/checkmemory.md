---
description: Scan Obsidian corrections index and process pending items
argument-hint: "[optional: project name | approve all]"
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

Use the **learn** skill to scan and process corrections.

1. Check `~/Projects/Thinking-Labs/claude/pending-capture.md` for pending blocks
2. If no pending items → scan `~/Projects/Thinking-Labs/claude/projects/` for notes with `status: pending` in frontmatter
3. If nothing found → output "Nothing to process." and stop
4. For each pending item: read the Obsidian note, classify using the decision tree, present for approval, route
5. Update processed Obsidian notes (status: done or cancelled)

**Input:** $ARGUMENTS
