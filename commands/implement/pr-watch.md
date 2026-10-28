---
description: Review, QA, and watch a teammate's PR. Comment with screenshots, then approve and save a Slack draft.
argument-hint: <PR URL or number> [--slack <message link>] [--auto-comment] [--auto-approve]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill, ToolSearch, AskUserQuestion, Agent, SendMessage, ScheduleWakeup, mcp__plugin_playwright_playwright__*, mcp__plugin_linear_linear__*, mcp__claude_ai_Slack__slack_read_thread, mcp__claude_ai_Slack__slack_send_message_draft, mcp__claude_ai_Slack__slack_search_public_and_private
---

Use the **pr-watch** skill.

For browser testing, qa-report delegates to the **vorbit:qa-runner** subagent. Do not run browser flows in the parent.

**Input:** $ARGUMENTS
